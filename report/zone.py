# Copyright 2019, 2020, 2021 Jack Consoli.  All rights reserved.
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
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 22 Aug 2020   | Fixed orientation of check marks.                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 29 Sep 2020   | Added alerts associated with the port for the zone member                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 13 Mar 2021   | Added login speed to the zone report.                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '13 Mar 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import collections
import openpyxl.utils.cell as xl
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.brcddb_login as brcddb_login
import brcddb.report.utils as report_utils

##################################################################
#
#              Case methods for hdr in zone_page()
#
##################################################################


def _zone_comment_case(obj):
    return '\n'.join([a.fmt_msg() for a in obj.r_alert_objects() if not a.is_flag()])


def _zone_zone_case(obj):
    return obj.r_obj_key()


def _zone_effective_case(obj):
    return '\u221A' if obj.r_is_effective() else ''


def _zone_peer_case(obj):
    return '\u221A' if obj.r_is_peer() else ''


def _zone_target_case(obj):
    return '\u221A' if obj.r_is_target_driven() else ''


def _zone_cfg_case(obj):
    return '\n'.join(obj.r_zone_configurations())


def _zone_member_case(obj):
    return len(obj.r_members()) + len(obj.r_pmembers())


def _zone_null_case(obj):
    return ''


def _zone_member_wwn_case(obj):
    members = list(obj.r_members())
    members.extend(list(obj.r_pmembers()))
    fab_obj = obj.r_fabric_obj()
    i = 0
    for mem in members:
        i += 1 if fab_obj.r_alias_obj(mem) is None else len(fab_obj.r_alias_obj(mem).r_members())
    return i


def _mem_null_case(obj, mem, wwn, port_obj):
    return ''


def _mem_member_case(obj, mem, wwn, port_obj):
    return mem


def _mem_comment_case(obj, mem, wwn, port_obj):
    # Get any comments for this WWN in the zone object
    al = [a.fmt_msg() for a in obj.r_alert_objects() if a.is_flag() and a.p0() == wwn]
    # If there is a login, add any comments associated with the login that are zoning specific
    if obj.r_fabric_obj() is not None and obj.r_fabric_obj().r_login_obj(wwn) is not None:
        al.extend('\n'.join([a.fmt_msg() for a in obj.r_fabric_obj().r_login_obj(wwn).r_alert_objects()
                             if a.is_flag() and a.p0() == mem]))
    if port_obj is not None:  # Add the alerts associated with the port for this member
        al.extend([a.fmt_msg() for a in port_obj.r_alert_objects() if a.is_error() or a.is_warn()])
    return '\n'.join(al)


def _mem_principal_case(obj, mem, wwn, port_obj):
    return '\u221A' if mem in obj.r_pmembers() else ''


def _mem_member_wwn_case(obj, mem, wwn, port_obj):
    return '' if wwn is None else '' if ',' in wwn else wwn


def _mem_switch_case(obj, mem, wwn, port_obj):
    return '' if port_obj is None else brcddb_switch.best_switch_name(port_obj.r_switch_obj())


def _mem_port_case(obj, mem, wwn, port_obj):
    return '' if port_obj is None else port_obj.r_obj_key()


def _mem_speed_case(obj, mem, wwn, port_obj):
    speed = None if port_obj is None else port_obj.r_get('fibrechannel/speed')
    return '' if speed is None else speed/1000000000


def _mem_desc_case(obj, mem, wwn, port_obj):
    try:
        t_wwn = port_obj.r_get('fibrechannel/neighbor')[0] if ',' in wwn else wwn
        return brcddb_login.login_best_port_desc(obj.r_fabric_obj().r_login_obj(t_wwn))
    except:
        return ''


_zone_hdr = {
    # Key is the column header. Value is a dict as follows:
    #   'c' Column width
    #   'z' Case method to fill in the cell for basic zone information
    #   'm' Case method to fill the cell for member information
    #   'v' True - display centered in column. Headers vertical, Otherwise, use default wrap alignment
    'Comments': {'c': 30, 'z': _zone_comment_case, 'm': _mem_comment_case},
    'Zone': {'c': 22, 'z': _zone_zone_case, 'm': _mem_null_case},
    'Effectve': {'c': 5, 'v': True, 'z': _zone_effective_case, 'm': _mem_null_case},
    'Peer': {'c': 5, 'v': True, 'z': _zone_peer_case, 'm': _mem_null_case},
    'Target Driven': {'c': 5, 'v': True, 'z': _zone_target_case, 'm': _mem_null_case},
    'Principal': {'c': 5, 'v': True, 'z': _zone_null_case, 'm': _mem_principal_case},
    'Configurations': {'c': 22, 'z': _zone_cfg_case, 'm': _mem_null_case},
    'Member': {'c': 22, 'z': _zone_member_case, 'm': _mem_member_case},
    'Member WWN': {'c':  22, 'z': _zone_member_wwn_case, 'm': _mem_member_wwn_case},
    'Switch': {'c': 22, 'z': _zone_null_case, 'm': _mem_switch_case},
    'Port': {'c': 7, 'z': _zone_null_case, 'm': _mem_port_case},
    'Speed Gbps': {'c': 7, 'z': _zone_null_case, 'm': _mem_speed_case},
    'Description': {'c': 50, 'z': _zone_null_case, 'm': _mem_desc_case},
}


def zone_page(fab_obj, tc, wb, sheet_name, sheet_i, sheet_title):
    """Creates a zone detail worksheet for the Excel report.

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: class
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global _zone_hdr

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
    for k in _zone_hdr:
        sheet.column_dimensions[xl.get_column_letter(col)].width = _zone_hdr[k]['c']
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        if 'v' in _zone_hdr[k] and _zone_hdr[k]['v']:
            sheet[cell].alignment = report_fonts.align_type('wrap_vert_center')
        else:
            sheet[cell].alignment = report_fonts.align_type('wrap')
        sheet[cell] = k
        col += 1

    # Fill out all the zoning information
    row += 1
    col = 1
    for zone_obj in fab_obj.r_zone_objects():
        # The zone information
        fill = report_fonts.fill_type('lightblue')
        for k in _zone_hdr:
            cell = xl.get_column_letter(col) + str(row)
            if k == 'Comments':
                sheet[cell].font = report_utils.font_type(zone_obj.r_alert_objects())
            else:
                sheet[cell].font = report_fonts.font_type('bold')
            sheet[cell].border = border
            if 'v' in _zone_hdr[k] and _zone_hdr[k]['v']:
                sheet[cell].alignment = report_fonts.align_type('wrap_center')
            else:
                sheet[cell].alignment = report_fonts.align_type('wrap')
            sheet[cell].fill = fill
            sheet[cell] = _zone_hdr[k]['z'](zone_obj)
            col += 1
        col = 1
        row += 1

        # The member information
        mem_list = list(zone_obj.r_pmembers())
        mem_list.extend(list(zone_obj.r_members()))
        for mem in mem_list:
            wwn_list = list()  # WWNs or d,i
            if fab_obj.r_alias_obj(mem) is None:
                wwn_list.append(mem)
            else:
                wwn_list.extend(fab_obj.r_alias_obj(mem).r_members())
            for wwn in wwn_list:
                if ',' in wwn:  # It's a d,i zone
                    port_obj = fab_obj.r_port_object_for_di(wwn)
                else:
                    port_obj = fab_obj.r_port_obj(wwn)
                if port_obj is None:
                    # Since brcddb_fabric.zone_analysis() already checked to see it's in another fabric, it would be
                    # much faster to check for the associated alert, but this was easier to code and time is not of the
                    # essence here.
                    for fobj in fab_obj.r_project_obj().r_fabric_objects():
                        if fab_obj.r_obj_key() != fobj.r_obj_key():
                            port_obj = fobj.r_port_obj(wwn)
                            if port_obj is not None:
                                break
                for k in _zone_hdr:
                    cell = xl.get_column_letter(col) + str(row)
                    # Display font based on alerts associated with the zone only, not members, for a zone object
                    if k == 'Comments':
                        alerts = [a for a in zone_obj.r_alert_objects() if a.is_flag() and a.p0() == wwn]
                        sheet[cell].font = report_utils.font_type(alerts)
                    else:
                        sheet[cell].font = report_fonts.font_type('std')
                    sheet[cell].border = border
                    if 'v' in _zone_hdr[k] and _zone_hdr[k]['v']:
                        sheet[cell].alignment = report_fonts.align_type('wrap_center')
                    else:
                        sheet[cell].alignment = report_fonts.align_type('wrap')
                    sheet[cell] = _zone_hdr[k]['m'](zone_obj, mem, wwn, port_obj)
                    col += 1
                col = 1
                row += 1


def alias_comment_case(obj, mem):
    return '\n'.join([a.fmt_msg() for a in obj.r_alert_objects() if not a.is_flag()])


def _alais_name_case(obj, mem):
    return obj.r_obj_key()


def _alias_node_desc_case(obj, mem):
    try:
        return brcddb_login.login_best_node_desc(obj.r_fabric_obj().r_login_obj(mem))
    except:
        return ''


def _alias_mem_member_case(obj, mem):
    return mem


def alias_mem_null_case(obj, mem):
    return ''


def _alias_mem_switch_case(obj, mem):
    try:
        return brcddb_switch.best_switch_name(obj.r_fabric_obj().r_login_obj(mem).r_switch_obj(), False)
    except:
        return ''


def _alias_mem_port_case(obj, mem):
    try:
        return obj.r_fabric_obj().r_login_obj(mem).r_port_obj().r_obj_key()
    except:
        return ''


def _alias_mem_desc_case(obj, mem):
    try:
        return brcddb_login.login_best_port_desc(obj.r_fabric_obj().r_login_obj(mem))
    except:
        return ''


def _alias_used_in_zone_case(obj, mem):
    return ', '.join([zobj.r_obj_key() for zobj in obj.r_zone_objects()])


def _alias_member_case(obj, mem):
    return obj.r_members()[0] if len(obj.r_members()) > 0 else ''


def _alias_null_case(obj, mem):
    return ''


# Key is the column header. Value is a dict as follows:
#   'c' Column width
#   'v' Case method to fill in the cell for alias and first member
#   'm' Case method to fill the cell for remaining member information
alias_hdr = collections.OrderedDict()
alias_hdr['Comments'] = {'c': 40, 'v': alias_comment_case, 'm': _alias_null_case}
alias_hdr['Alias'] = {'c': 32, 'v': _alais_name_case, 'm': _alias_null_case}
alias_hdr['Used in Zone'] = {'c': 32, 'v': _alias_used_in_zone_case, 'm': _alias_null_case}
alias_hdr['Member'] = {'c': 32, 'v': _alias_member_case, 'm': _alias_mem_member_case}
alias_hdr['Switch'] = {'c': 22, 'v': _alias_mem_switch_case, 'm': _alias_mem_switch_case}
alias_hdr['Port'] = {'c': 7, 'v': _alias_mem_port_case, 'm': _alias_mem_port_case}
alias_hdr['Description'] = {'c': 50, 'v': _alias_node_desc_case, 'm': _alias_mem_desc_case}


def alias_page(fab_obj, tc, wb, sheet_name, sheet_i, sheet_title):
    """Creates a port detail worksheet for the Excel report.

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: class
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
            if k == 'Comments':
                sheet[cell].font = report_utils.font_type(alias_obj.r_alert_objects())
            else:
                sheet[cell].font = report_fonts.font_type('std')
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
