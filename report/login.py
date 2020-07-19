#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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

:mod:`brcddb.report.login` - Includes methods to create login page

Version Control::

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

import time
import openpyxl.utils.cell as xl
import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log
import brcddb.util.util as brcddb_util
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.utils as report_utils
import brcddb.report.fonts as report_fonts


##################################################################
#
#        Case statements in login_page()
#
###################################################################

# Custom
def l_switch_name_case(login_obj):
    return brcddb_switch.best_switch_name(login_obj.r_switch_obj(), False)

def l_switch_name_and_wwn_case(login_obj):
    return brcddb_switch.best_switch_name(login_obj.r_switch_obj(), True)

def l_switch_wwn_case(login_obj):
    switch_obj = login_obj.r_switch_obj()
    return '' if switch_obj is None else switch_obj.r_obj_key()

def l_port_number_case(login_obj):
    port_obj = login_obj.r_port_obj()
    return '' if port_obj is None else port_obj.r_obj_key()

def l_alias_case(login_obj):
    return '\n'.join(login_obj.r_fabric_obj().r_alias_for_wwn(login_obj.r_obj_key()))

def l_zones_def_case(login_obj):
    # You can have an alias that includes a WWN + the same WWN as a WWN in the zone in which case this would return
    # the same zone twice. As a practical matter, I've never seen it done and nothing breaks in the code so this is
    # good enough
    return '\n'.join(login_obj.r_fabric_obj().r_zones_for_wwn(login_obj.r_obj_key()))

def l_zones_eff_case(login_obj):
    return '\n'.join(login_obj.r_fabric_obj().r_eff_zones_for_wwn(login_obj.r_obj_key()))

def l_fdmi_node_case(login_obj, k):
    # Remember, it's the base WWN we want for the node (hba), not the login WWN
    try:
        wwn = login_obj.r_port_obj().r_get('fibrechannel/neighbor/wwn')[0]
        buf = login_obj.r_fabric_obj().r_fdmi_node_obj(wwn).r_get(k)
        return '' if buf is None else buf
    except:
        return ''

def l_fdmi_port_case(login_obj, k):
    try:
        buf = login_obj.r_fabric_obj().r_fdmi_port_obj(login_obj.r_obj_key()).r_get(k)
        if isinstance(buf, str):
            tl = k.split('/')
            try:
                return brcddb_common.fdmi_port_conversion_tbl[tl[1]][buf]
            except:
                return buf
        return '' if buf is None else buf
    except:
        return ''

def l_port_name_case(login_obj):
    port_name = login_obj.r_get('port-name')  # There isn't anything in here if it's AMP
    return login_obj.r_obj_key() if port_name is None else login_obj.r_get('port-name')

def l_comment_case(login_obj):
    a_list = report_utils.combined_login_alert_objects(login_obj)
    return '\n'.join([obj.fmt_msg() for obj in a_list]) if len(a_list) > 0 else ''


login_case = {
    '_FABRIC_NAME': report_utils.fabric_name_case,
    '_FABRIC_NAME_AND_WWN': report_utils.fabric_name_or_wwn_case,
    '_FABRIC_WWN': report_utils.fabric_wwn_case,
    '_LOGIN_COMMENTS': l_comment_case,
    '_PORT_NUMBER': l_port_number_case,
    '_SWITCH_NAME': l_switch_name_case,
    '_SWITCH_NAME_AND_WWN': l_switch_name_and_wwn_case,
    '_SWITCH_WWN': l_switch_wwn_case,
    '_ALIAS': l_alias_case,
    '_ZONES_DEF': l_zones_def_case,
    '_ZONES_EFF': l_zones_eff_case,
    'port-name': l_port_name_case,
}

fdmi_case = {
    '_FDMI_NODE': l_fdmi_node_case,
    '_FDMI_PORT': l_fdmi_port_case,
}

def login_page(wb, tc, sheet_name, sheet_i, sheet_title, l_list, display, login_display_tbl, s=True):
    """Creates a login detail worksheet for the Excel report.

    :param wb: Workbook object
    :type wb: dict
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :param l_list: List of login objects (LoginObj) to display
    :type l_list: list, tuple
    :param display: List of parameters to display.
    :type display: list, tuple
    :param login_display_tbl: Display control table. See brcddb.report.report_tables.login_display_tbl
    :type login_display_tbl: dict
    :param s: If True, sorts the logins by port-id (port address where the login was found)
    :rtype: None
    """
    global login_case, fdmi_case

    # Validate the user input
    err_msg = []
    if l_list is None:
        err_msg.append('l_list was not defined.')
    elif not isinstance(l_list, (list, tuple)):
        err_msg.append('l_list was type ' + str(type(l_list)) + '. Must be a list or tuple.')
    if display is None:
        err_msg.append('display not defined.')
    if len(err_msg) > 0:
        err_msg.append('Failed to create login_page().')
        buf = ', '.join(err_msg)
        brcdapi_log.exception(buf, True)
        proj_obj = None
        if isinstance(l_list, (list, tuple)):
            for login_obj in l_list:
                proj_obj = login_obj.r_project_obj()
                if proj_obj is not None:
                    proj_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_USER_ERROR, None, buf, None)
                    proj_obj.s_user_error_flag()
                    break
        return

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
    sheet.freeze_panes = sheet['A3']
    col = 1
    row += 1
    for k in display:
        if k in login_display_tbl and 'dc' in login_display_tbl[k] and login_display_tbl[k]['dc'] is True:
            continue
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('bold')
        sheet[cell].border = report_fonts.border_type('thin')
        if k in login_display_tbl:
            if 'c' in login_display_tbl[k]:
                sheet.column_dimensions[xl.get_column_letter(col)].width = login_display_tbl[k]['c']
            try:
                if login_display_tbl[k]['v']:
                    sheet[cell].alignment = report_fonts.align_type('wrap_vert_center')
                else:
                    sheet[cell].alignment = report_fonts.align_type('wrap')
            except:
                sheet[cell].alignment = report_fonts.align_type('wrap')
            if 'd' in login_display_tbl[k]:
                sheet[cell] = login_display_tbl[k]['d']
            else:
                sheet[cell] = k
        else:
            sheet[cell] = k  # This happens when a new key is introduced before updating the display table
        col += 1

    # Add a row for each login
    row += 1
    if s:
        wl = brcddb_util.sort_obj_num(l_list, 'port-id', r=False, h=True)  # Filters out anything not found
        wl.extend(list(set(l_list) - set(wl)))
    else:
        wl = l_list
    for login_obj in wl:
        if login_obj is None:
            row += 1
            continue
        col = 1
        border = report_fonts.border_type('thin')
        alignment = report_fonts.align_type('wrap')
        center_alignment = report_fonts.align_type('wrap_center')
        font = report_utils.font_type(report_utils.combined_login_alert_objects(login_obj))
        for k in display:
            if k in login_display_tbl and 'dc' in login_display_tbl[k] and login_display_tbl[k]['dc'] is True:
                continue
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].border = border
            if k in login_display_tbl and 'm' in login_display_tbl[k] and login_display_tbl[k]['m'] is True:
                sheet[cell].alignment = center_alignment
            else:
                sheet[cell].alignment = alignment
            sheet[cell].font = font
            k_list = k.split('.')
            if len(k_list) > 1:
                try:
                    sheet[cell] = fdmi_case[k_list[0]](login_obj, k_list[1])
                except:
                    sheet[cell] = ''
                    brcdapi_log.exception('Unknown key: ' + k_list[0])
            elif k in login_case:
                sheet[cell] = login_case[k](login_obj)
            elif k in login_display_tbl:
                v = login_obj.r_get(k)
                if v is None:
                    v1 = ''
                else:
                    try:
                        v1 = brcddb_common.login_conversion_tbl[k][v]
                        if v1 is None:
                            raise
                    except:
                        v1 = v
                if isinstance(v1, bool):
                    sheet[cell] = '\u221A' if v1 else ''
                else:
                    sheet[cell] = v1
            else:
                sheet[cell].font = report_fonts.font_type('std')
                sheet[cell] = '' if login_obj.r_get(k) is None else str(login_obj.r_get(k))
            col += 1
        row += 1
        col = 1
