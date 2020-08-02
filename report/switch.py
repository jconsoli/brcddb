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
:mod:`brcddb.report.switch` - Creates a switch page to be added to an Excel Workbook

Version Control::

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
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '02 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

import collections
import openpyxl.utils.cell as xl
import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log
import brcddb.util.util as brcddb_util
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.utils as report_utils
import brcddb.report.fonts as report_fonts
import brcddb.app_data.alert_tables as al

sheet = None
row = 1
hdr = collections.OrderedDict()
# Key is the column header and value is the width
hdr['Comment'] = 30
hdr['Parameter'] = 29
hdr['Setting'] = 29


##################################################################
#
#        Switch case statements in switch_page()
#
###################################################################

def s_switch_name_case(switch_obj, k=None):
    return brcddb_switch.best_switch_name(switch_obj, False)


def s_switch_name_and_wwn_case(switch_obj, k=None):
    return brcddb_switch.best_switch_name(switch_obj, True)


def s_switch_wwn_case(switch_obj, k=None):
    return switch_obj.r_obj_key()


def s_switch_did_case(switch_obj, k):
    did = switch_obj.r_get('brocade-fabric/fabric-switch/domain-id')
    return '0x00' if did is None else '0x' + f'{did:X}' + ' (' + str(did) + ')'


def s_switch_list_case(switch_obj, k):
    sl = switch_obj.r_get(k)
    return None if sl is None else '\n'.join(sl)


def s_switch_trunk_case(switch_obj, k):  # Not used yet
    rl = []
    for obj in brcddb_util.convert_to_list(switch_obj.r_get(k)):
        port_obj = switch_obj.r_port_object_for_index(obj.get('source-port'))
        ps_name = 'Index: ' + obj.get('source-port') if port_obj is None else port_obj.r_obj_key()
        d_switch_obj = switch_obj.r_project_obj().r_switch_obj(obj.get('neighbor-wwn'))
        port_obj = None if d_switch_obj is None else d_switch_obj.r_port_object_for_index(obj.get('destination-port'))
        pd_name = 'Index: ' + str(obj.get('destination-port')) if port_obj is None else port_obj.r_obj_key()
        rl.append('From ' + ps_name + ' to ' + obj.get('neighbor-switch-name') + ' ' + pd_name)
    return '\n'.join(rl)


def s_switch_area_mode_case(switch_obj, k):
    x = switch_obj.r_get(k)
    return str(x) + ' (' + brcddb_switch.area_mode[x] + ')' if x in brcddb_switch.area_mode else str(x) + '(Unknown)'


def s_switch_model_case(switch_obj, k):
    oem = brcddb_switch.SWITCH_BRAND.Brocade  # Custom OEM index not yet available as of 8.2.1b
    x = switch_obj.c_switch_model()
    if oem == brcddb_switch.SWITCH_BRAND.Brocade:
        return str(x) + ' (' + brcddb_switch.model_broadcom(x) + ')'
    else:
        return str(x) + ' (' + brcddb_switch.model_oem(x, oem)  + ', ' + brcddb_switch.model_broadcom(x) + ')'


def s_switch_up_time_case(switch_obj, k):
    x = switch_obj.r_get(k)
    return int(x / 86400 + 0.5) if isinstance(x, int) else 'Unknown'


def s_operational_status_case(switch_obj, k):
    try:
        return brcddb_common.switch_conversion_tbl[k][switch_obj.r_get(k)]
    except:
        try:
            return brcddb_common.switch_conversion_tbl['enabled-state'][switch_obj.r_get('enabled-state')]
        except:
            return ''


def s_maps_active_policy_name(switch_obj, k):
    try:
        return switch_obj.r_active_maps_policy().get('name')
    except:
        return ''


switch_key_case = {
    # Custom
    '_FABRIC_NAME': report_utils.fabric_name_case,
    '_FABRIC_NAME_AND_WWN': report_utils.fabric_name_or_wwn_case,
    '_FABRIC_WWN': report_utils.fabric_wwn_case,
    '_SWITCH_NAME': s_switch_name_case,
    '_SWITCH_NAME_AND_WWN': s_switch_name_and_wwn_case,
    '_SWITCH_WWN': s_switch_wwn_case,
    '_SWITCH_ACTIVE_MAPS_POLICY_NAME': s_maps_active_policy_name,
    # Root level API
    'brocade-fabric/fabric-switch/domain-id': s_switch_did_case,
    'brocade-fibrechannel-switch/fibrechannel-switch/ip-static-gateway-list/ip-static-gateway': s_switch_list_case,
    'brocade-fibrechannel-switch/fibrechannel-switch/model': s_switch_model_case,
    'fibrechannel/operational-status': s_operational_status_case,
    'brocade-fibrechannel-configuration/switch-configuration/area-mode': s_switch_area_mode_case,
    'brocade-fibrechannel-switch/fibrechannel-switch/up-time': s_switch_up_time_case,
    # f-port-login-settings
    # 'zone-configuration': ?, This is a dict, but I don't know what the members are yet
}


def _setup_worksheet(wb, tc, sheet_name, sheet_i, sheet_title):
    """Creates a switch detail worksheet for the Excel report.

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global row, sheet, hdr

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    row = 1
    col = 1
    for k, v in hdr.items():
        sheet.column_dimensions[xl.get_column_letter(col)].width = v
        col += 1
    col = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell] = sheet_title
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    sheet.freeze_panes = sheet['A2']


def _maps_dashboard(switch_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :rtype: None
    """
    global row, sheet

    merge_len = 2  # NUmber of columns to be merged for the MAPS dashboard
    col = 1
    row += 2
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('bold')
    sheet[cell].alignment = alignment
    sheet[cell] = 'MAPS Dashboard Alerts'
    font = report_fonts.font_type('std')
    i = 0
    for alert_obj in switch_obj.r_alert_objects():
        if alert_obj.alert_num() in al.AlertTable.maps_alerts:
            row += 1
            sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
            for col in range(1, merge_len + 2):
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].border = border
            col = 1
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].alignment = alignment
            sheet[cell] = alert_obj.fmt_msg()
            i += 1
    if i == 0:
        row += 1
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
        for col in range(1, merge_len + 2):
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].border = border
        col = 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].alignment = alignment
        sheet[cell] = 'None'


def _add_switch(switch_obj, display):
    """Adds switch detail to the worksheet.

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param display: List of keys to display. Find next instance of switch_key_case. Much less complex than port_page()
    :type display: dict
    :rtype: None
    """
    global row, sheet, hdr, switch_key_case

    # Add the headers
    col = 1
    row += 2
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_2')
    sheet[cell] = brcddb_switch.best_switch_name(switch_obj, True)
    row += 1
    for k in hdr.keys():
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('bold')
        sheet[cell] = k
        col += 1

    # Add the MAPS dashboard
    _maps_dashboard(switch_obj)

    # Add the switch details
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    row += 1
    for k in display:
        font = report_utils.font_type_for_key(switch_obj, k)
        col = 1
        row += 1
        # Comments
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        sheet[cell].alignment = alignment
        sheet[cell] = report_utils.comments_for_alerts(switch_obj, k)
        # Key description
        col += 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        sheet[cell].alignment = alignment
        sheet[cell] = display[k] if k in display else k
        # Value
        col += 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        sheet[cell].alignment = alignment
        v = switch_obj.r_get(k)
        if k in switch_key_case:
            sheet[cell] = switch_key_case[k](switch_obj, k)
        elif k in brcddb_common.switch_conversion_tbl:
            sheet[cell] = '' if v is None else brcddb_common.switch_conversion_tbl[k][v]
        else:
            if isinstance(v, bool):
                sheet[cell] = 'Yes' if v else 'No'
            else:
                sheet[cell] = v if isinstance(v, (str, int, float)) else '' if v is None else str(v)


def switch_page(wb, tc, sheet_name, sheet_i, sheet_title, s_list, display):
    """Creates a switch detail worksheet for the Excel report.
    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :param s_list: List of switch objects (SwitchObj) to display
    :type s_list: list, tuple
    :param display: List of keys to display. Find next instance of switch_key_case. Much less complex than port_page()
    :type display: dict
    :rtype: None
    """
    # Validate the user input
    err_msg = []
    if s_list is None:
        err_msg.append('s_list was not defined.')
    elif not isinstance(s_list, (list, tuple)):
        err_msg.append('s_list was type ' + str(type(s_list)) + '. Must be a list or tuple.')
    if display is None:
        err_msg.append('display not defined.')
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Set up the worksheed and add each switch
    _setup_worksheet(wb, tc, sheet_name, sheet_i, sheet_title)
    for switch_obj in s_list:
        _add_switch(switch_obj, display)
