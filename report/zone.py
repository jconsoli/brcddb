#!/usr/bin/python
# Copyright 2019 Jack Consoli.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`report.zone` - Creates a zoning page to be added to an Excel Workbook

VVersion Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '19 Jul 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import datetime
import time
import calendar
import collections
import openpyxl.utils.cell as xl
import brcddb.brcddb_common as brcddb_common
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_login as brcddb_login

# Common styles
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font

def zone_font_type(obj):
    """Determines the display font based on alerts associated with the zone only, no members, for a zone object.
    :param obj: The zone object
    :param obj: ZoneObj
    :param mem: Zone member. If none, only determine font based on alerts for the zone itself
    :type mem: str
    """
    font = report_fonts.font_type('std')
    # Get a list of the relevant comment objects
    for aObj in [a for a in obj.r_alert_objects() if not a.is_flag()]:
        if aObj.is_error():
            return report_fonts.font_type('error')
        elif aObj.is_warn():
            font = report_fonts.font_type('warn')
    return font


def mem_font_type(obj, mem):
    """Determines the display font based on alerts associated with the zone only, no members, for a zone object.
    :param obj: The zone object
    :param obj: ZoneObj
    :param mem: Zone member. If none, only determine font based on alerts for the zone itself
    :type mem: str
    """
    font = report_fonts.font_type('std')
    # Get a list of the relevant comment objects
    for aObj in [a for a in obj.r_alert_objects() if a.is_flag() and a.p0() == mem]:
        if aObj.is_error():
            return report_fonts.font_type('error')
        elif aObj.is_warn():
            font = report_fonts.font_type('warn')
    return font


##################################################################
#
#              Case methods for hdr in zone_page()
#
##################################################################

def zone_comment_case(obj):
    return '\n'.join([a.fmt_msg() for a in obj.r_alert_objects() if not a.is_flag()])

def zone_zone_case(obj):
    return obj.r_obj_key()

def zone_effective_case(obj):
    return '\u221A' if obj.r_is_effective() else ''

def zone_peer_case(obj):
    return '\u221A' if obj.r_is_peer() else ''

def zone_target_case(obj):
    return '\u221A' if obj.r_is_target_driven() else ''

def zone_cfg_case(obj):
    return '\n'.join(obj.r_zone_configurations())

def zone_member_case(obj):
    return len(obj.r_members()) + len(obj.r_pmembers())

def zone_null_case(obj=None, mem=None, wwn=None, port_map=None):
    return ''

def zone_member_wwn_case(obj):
    members = list(obj.r_members())
    members.extend(list(obj.r_pmembers()))
    fabObj = obj.r_fabric_obj()
    i = 0
    for mem in members:
        i += 1 if fabObj.r_alias_obj(mem) is None else len(fabObj.r_alias_obj(mem).r_members())
    return i

def mem_member_case(obj, mem, wwn, portObj):
    return mem

def mem_comment_case(obj, mem, wwn, portObj):
    # Get any comments for this WWN in the zone object
    al = [a.fmt_msg() for a in obj.r_alert_objects() if a.is_flag() and a.p0() == wwn]
    # If there is a login, add any comments associated with the login that are zoning specific
    if obj.r_fabric_obj() is not None and obj.r_fabric_obj().r_login_obj(wwn) is not None:
        al.extend('\n'.join([a.fmt_msg() for a in obj.r_fabric_obj().r_login_obj(wwn).r_alert_objects() \
                      if a.is_flag() and a.p0() == mem]))
    return '\n'.join(al)

def mem_principal_case(obj, mem, wwn, portObj):
    return '\u221A' if mem in obj.r_pmembers() else ''

def mem_member_wwn_case(obj, mem, wwn, portObj):
    return '' if wwn is None else '' if ',' in wwn else wwn

def mem_switch_case(obj, mem, wwn, portObj):
    return '' if portObj is None else brcddb_switch.best_switch_name(portObj.r_switch_obj())

def mem_port_case(obj, mem, wwn, portObj):
    return '' if portObj is None else portObj.r_obj_key()

def mem_desc_case(obj, mem, wwn, portObj):
    try:
        t_wwn = portObj.r_get('fibrechannel/neighbor')[0] if ',' in wwn else wwn
        return brcddb_login.login_best_port_desc(obj.r_fabric_obj().r_login_obj(t_wwn))
    except:
        return ''

zone_hdr = {
    # Key is the column header. Value is a dict as follows:
    #   'c' Column width
    #   'z' Case method to fill in the cell for basic zone information
    #   'm' Case method to fill the cell for member information
    #   'v' True - display centered in column. Headers vertical, Otherwise, use default wrap alignment
    'Comments': {'c': 30, 'z': zone_comment_case, 'm': mem_comment_case},
    'Zone': {'c': 22, 'z': zone_zone_case, 'm': zone_null_case},
    'Effectve': {'c': 5, 'v': True, 'z': zone_effective_case, 'm': zone_null_case},
    'Peer': {'c': 5, 'v': True, 'z': zone_peer_case, 'm': zone_null_case},
    'Target Driven': {'c': 5, 'v': True, 'z': zone_target_case, 'm': zone_null_case},
    'Principal': {'c': 5, 'v': True, 'z': zone_null_case, 'm': mem_principal_case},
    'Configurations': {'c': 22, 'z': zone_cfg_case, 'm': zone_null_case},
    'Member': {'c': 22, 'z': zone_member_case, 'm': mem_member_case},
    'Member WWN': {'c':  22, 'z': zone_member_wwn_case, 'm': mem_member_wwn_case},
    'Switch': {'c': 22, 'z': zone_null_case, 'm': mem_switch_case},
    'Port': {'c': 7, 'z': zone_null_case, 'm': mem_port_case},
    'Description': {'c': 50, 'z': zone_null_case, 'm': mem_desc_case},
}




def zone_page(fabObj, tc, wb, sheet_name, sheet_i, sheet_title):
    """Creates a zone detail worksheet for the Excel report.

    :param fabObj: Fabric object
    :type fabObj: brcddb.classes.fabric.FabricObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: dict
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global zone_hdr

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    col = 1
    row = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell] = sheet_title
    row += 2
    col = 1
    sheet.freeze_panes = sheet['A4']
    font = report_fonts.font_type('hdr_2')
    border = report_fonts.border_type('thin')
    for k in zone_hdr:
        sheet.column_dimensions[xl.get_column_letter(col)].width = zone_hdr[k]['c']
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        sheet[cell].alignment = report_fonts.align_type('wrap_vert_center') if 'v' in zone_hdr[k] and zone_hdr[k]['v'] \
            else report_fonts.align_type('wrap')
        sheet[cell] = k
        col += 1

    # Fill out all the zoning information
    row += 1
    col = 1
    for zoneObj in fabObj.r_zone_objects():
        # The zone information
        fill = report_fonts.fill_type('lightblue')
        for k in zone_hdr:
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = zone_font_type(zoneObj) if k == 'Comments' else report_fonts.font_type('bold')
            sheet[cell].border = border
            sheet[cell].alignment = report_fonts.align_type('wrap_center') if 'v' in zone_hdr[k] and zone_hdr[k]['v'] \
                else report_fonts.align_type('wrap')
            sheet[cell].fill = fill
            sheet[cell] = zone_hdr[k]['z'](zoneObj)
            col += 1
        col = 1
        row += 1

        # The member information
        mem_list = list(zoneObj.r_pmembers())
        mem_list.extend(list(zoneObj.r_members()))
        for mem in mem_list:
            wwn_list = []  # WWNs or d,i
            if fabObj.r_alias_obj(mem) is None:
                wwn_list.append(mem)
            else:
                wwn_list.extend(fabObj.r_alias_obj(mem).r_members())
            for wwn in wwn_list:
                if ',' in wwn:  # It's a d,i zone
                    portObj = fabObj.r_port_object_for_di(wwn)
                else:
                    portObj = fabObj.r_port_obj(wwn)
                if portObj is None:
                    # Since brcddb_fabric.zone_analysis() already checked to see it's in another fabric, it would be
                    # much faster to check for the associated alert, but this was easier to code and time is not of the
                    # essence here.
                    for fobj in fabObj.r_project_obj().r_fabric_objects():
                        if fabObj.r_obj_key() != fobj.r_obj_key():
                            portObj = fobj.r_port_obj(wwn)
                            if portObj is not None:
                                break
                for k in zone_hdr:
                    cell = xl.get_column_letter(col) + str(row)
                    sheet[cell].font = mem_font_type(zoneObj, wwn) if k is 'Comments'\
                        else report_fonts.font_type('std')
                    sheet[cell].border = border
                    sheet[cell].alignment = report_fonts.align_type('wrap_center') if 'v' in zone_hdr[k] and \
                                                    zone_hdr[k]['v'] else report_fonts.align_type('wrap')
                    sheet[cell] = zone_hdr[k]['m'](zoneObj, mem, wwn, portObj)
                    col += 1
                col = 1
                row += 1


def alias_comment_case(obj, mem):
    return '\n'.join([a.fmt_msg() for a in obj.r_alert_objects() if not a.is_flag()])

def alais_name_case(obj, mem):
    return obj.r_obj_key()

def alias_node_desc_case(obj, mem):
    try:
        return brcddb_login.login_best_node_desc(obj.r_fabric_obj().r_login_obj(mem))
    except:
        return ''

def alias_mem_member_case(obj, mem):
    return mem

def alias_mem_null_case(obj, mem):
    return ''

def alias_mem_switch_case(obj, mem):
    try:
        return brcddb_switch.best_switch_name(obj.r_fabric_obj().r_login_obj(mem).r_switch_obj(), False)
    except:
        return ''

def alias_mem_port_case(obj, mem):
    try:
        return obj.r_fabric_obj().r_login_obj(mem).r_port_obj().r_obj_key()
    except:
        return ''

def alias_mem_desc_case(obj, mem):
    try:
        return brcddb_login.login_best_port_desc(obj.r_fabric_obj().r_login_obj(mem))
    except:
        return ''

def alias_used_in_zone_case(obj, mem):
    return ', '.join([zobj.r_obj_key() for zobj in obj.r_zone_objects()])

def alias_member_case(obj, mem):
    return obj.r_members()[0] if len(obj.r_members()) > 0 else ''

def alias_null_case(obj, mem):
    return ''


# Key is the column header. Value is a dict as follows:
#   'c' Column width
#   'v' Case method to fill in the cell for alias and first member
#   'm' Case method to fill the cell for remaining member information
alias_hdr = collections.OrderedDict()
alias_hdr['Comments'] = {'c': 40, 'v': alias_comment_case, 'm': alias_null_case}
alias_hdr['Alias'] = {'c': 32, 'v': alais_name_case, 'm': alias_null_case}
alias_hdr['Used in Zone'] = {'c': 32, 'v': alias_used_in_zone_case, 'm': alias_null_case}
alias_hdr['Member'] = {'c': 32, 'v': alias_member_case, 'm': alias_mem_member_case}
alias_hdr['Switch'] = {'c': 22, 'v': alias_mem_switch_case, 'm': alias_mem_switch_case}
alias_hdr['Port'] = {'c': 7, 'v': alias_mem_port_case, 'm': alias_mem_port_case}
alias_hdr['Description'] = {'c': 50, 'v': alias_node_desc_case, 'm': alias_mem_desc_case}


def alias_page(fab_obj, tc, wb, sheet_name, sheet_i, sheet_title):
    """Creates a port detail worksheet for the Excel report.

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: dict
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global alias_hdr

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    col = 1
    row = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(row)
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    sheet[cell].border = border
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell] = sheet_title
    row += 2
    col = 1
    sheet.freeze_panes = sheet['A4']
    for k in alias_hdr:
        sheet.column_dimensions[xl.get_column_letter(col)].width = alias_hdr[k]['c']
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('hdr_2')
        sheet[cell].border = border
        sheet[cell].alignment = alignment
        sheet[cell] = k
        col += 1

    # Fill out the alias information
    std_font = report_fonts.font_type('std')
    for alias_obj in fab_obj.r_alias_objects():
        mem_list = alias_obj.r_members().copy()
        mem = mem_list.pop(0) if len(mem_list) > 0 else None
        row += 1
        col = 1
        for k in alias_hdr:
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = zone_font_type(alias_obj) if k == 'Comments' else report_fonts.font_type('std')
            sheet[cell].border = border
            sheet[cell].alignment = alignment
            sheet[cell] = alias_hdr[k]['v'](alias_obj, mem)
            col += 1

        # Usually just one member per alias, but just in case...
        while len(mem_list) > 1:
            mem = mem_list.pop(0)
            row += 1
            col = 1
            for k in alias_hdr:
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].font = std_font
                sheet[cell].border = border
                sheet[cell].alignment = alignment
                sheet[cell] = alias_hdr[k]['m'](alias_obj, mem)
                col += 1