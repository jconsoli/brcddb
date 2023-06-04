# Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli.  All rights reserved.
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

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | switch_page           | Creates a switch detail worksheet for the Excel report.                               |
    +-----------------------+---------------------------------------------------------------------------------------+

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
    | 3.0.2     | 01 Nov 2020   | Removed deprecated KPIs                                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 17 Jul 2021   | Get switch type from brcddb_chassis instead of brcddb_switch                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 14 Nov 2021   | No functional changes. Added defaults for display tables and sheet indicies.      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 31 Dec 2021   | Corrected descriptions for "param in_display" and "type in_display" in            |
    |           |               | switch_page() header. No functional changes.                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 28 Apr 2022   | Added references for report_app, allowed single switch in switch_page()           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 14 Oct 2022   | Added zone and port statistics summary                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 04 Jun 2023   | Use URI references in brcdapi.util                                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '04 Jun 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.9'

import collections
import openpyxl.utils.cell as xl
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util
import brcdapi.excel_util as excel_util
import brcdapi.excel_fonts as excel_fonts
import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.brcddb_switch as brcddb_switch
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.app_data.alert_tables as al
import brcddb.app_data.report_tables as rt
import brcddb.util.search as brcddb_search
import brcddb.report.utils as report_utils

_hdr = collections.OrderedDict()
# Key is the column header and value is the width
_hdr['Comment'] = 30
_hdr['Parameter'] = 29
_hdr['Setting'] = 29
_sw_quick_d = collections.OrderedDict()  # Used to set up links to port pages
_sw_quick_d['Port Configurations'] = 'report_app/hyperlink/pc'
_sw_quick_d['Port Statistics'] = 'report_app/hyperlink/ps'
_sw_quick_d['Ports by Zone and Login'] = 'report_app/hyperlink/pz'
_sw_quick_d['SFP report'] = 'report_app/hyperlink/sfp'
# Below is for effeciency
_std_font = excel_fonts.font_type('std')
_bold_font = excel_fonts.font_type('bold')
_link_font = excel_fonts.font_type('link')
_hdr2_font = excel_fonts.font_type('hdr_2')
_hdr1_font = excel_fonts.font_type('hdr_1')
_align_wrap = excel_fonts.align_type('wrap')
_align_wrap_vc = excel_fonts.align_type('wrap_vert_center')
_align_wrap_c = excel_fonts.align_type('wrap_center')
_border_thin = excel_fonts.border_type('thin')


##################################################################
#
#        Switch case statements in switch_page()
#
###################################################################

def _s_switch_name_case(switch_obj, k=None):
    return brcddb_switch.best_switch_name(switch_obj, wwn=False, did=False)


def _s_switch_name_and_wwn_case(switch_obj, k=None):
    return brcddb_switch.best_switch_name(switch_obj, wwn=True, did=False)


def _s_switch_wwn_case(switch_obj, k=None):
    return switch_obj.r_obj_key()


def _s_switch_did_case(switch_obj, k):
    did = switch_obj.r_get(brcdapi_util.bfs_did)
    return '0x00' if did is None else '0x' + f'{did:X}' + ' (' + str(did) + ')'


def _s_switch_list_case(switch_obj, k):
    sl = switch_obj.r_get(k)
    return None if sl is None else '\n'.join(sl)


def _s_switch_trunk_case(switch_obj, k):  # Not used yet
    rl = list()
    for obj in brcddb_util.convert_to_list(switch_obj.r_get(k)):
        port_obj = switch_obj.r_port_object_for_index(obj.get('source-port'))
        ps_name = 'Index: ' + obj.get('source-port') if port_obj is None else port_obj.r_obj_key()
        d_switch_obj = switch_obj.r_project_obj().r_switch_obj(obj.get('neighbor-wwn'))
        port_obj = None if d_switch_obj is None else d_switch_obj.r_port_object_for_index(obj.get('destination-port'))
        pd_name = 'Index: ' + str(obj.get('destination-port')) if port_obj is None else port_obj.r_obj_key()
        rl.append('From ' + ps_name + ' to ' + obj.get('neighbor-switch-name') + ' ' + pd_name)
    return '\n'.join(rl)


def _s_switch_area_mode_case(switch_obj, k):
    x = switch_obj.r_get(k)
    return str(x) + ' (' + brcddb_switch.area_mode[x] + ')' if x in brcddb_switch.area_mode else str(x) + '(Unknown)'


def _s_switch_model_case(switch_obj, k):
    # Custom OEM index not yet available as of 9.0.1b
    return brcddb_chassis.chassis_type(switch_obj.r_chassis_obj(), type_num=True, in_oem='brcd')


def _s_switch_up_time_case(switch_obj, k):
    x = switch_obj.r_get(k)
    return int(x / 86400 + 0.5) if isinstance(x, int) else 'Unknown'


def _s_maps_active_policy_name(switch_obj, k):
    try:
        return switch_obj.r_active_maps_policy().get('name')
    except AttributeError:
        return ''


switch_key_case = {
    # Custom
    '_FABRIC_NAME': report_utils.fabric_name_case,
    '_FABRIC_NAME_AND_WWN': report_utils.fabric_name_or_wwn_case,
    '_FABRIC_WWN': report_utils.fabric_wwn_case,
    '_SWITCH_NAME': _s_switch_name_case,
    '_SWITCH_NAME_AND_WWN': _s_switch_name_and_wwn_case,
    '_SWITCH_WWN': _s_switch_wwn_case,
    '_SWITCH_ACTIVE_MAPS_POLICY_NAME': _s_maps_active_policy_name,
    # Root level API
    brcdapi_util.bfs_did: _s_switch_did_case,
    'brocade-fibrechannel-switch/fibrechannel-switch/ip-static-gateway-list/ip-static-gateway': _s_switch_list_case,
    brcdapi_util.bfs_model: _s_switch_model_case,
    brcdapi_util.bfc_area_mode: _s_switch_area_mode_case,
    brcdapi_util.bfc_up_time: _s_switch_up_time_case,
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
    :param sheet_i: Sheet index where page is to be placed. Default s 0
    :type sheet_i: int, None
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :return sheet: Worksheet object
    :rtype openpyxl.Worksheet
    :return row: Next row
    :rtype: int
    """
    global _hdr

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    row = col = 1
    for k, v in _hdr.items():
        sheet.column_dimensions[xl.get_column_letter(col)].width = v
        col += 1
    col = 1
    if isinstance(tc, str):
        excel_util.cell_update(sheet, row, col, 'Contents', font=_link_font, link=tc)
        col += 1
    excel_util.cell_update(sheet, row, col, sheet_title, font=_hdr1_font)
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(_hdr))
    sheet.freeze_panes = sheet['A2']

    return sheet, row + 1


def _maps_dashboard(sheet, row, switch_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param sheet: Workbook sheet
    :type sheet: openpyxl.Worksheet
    :param row: Starting row
    :type row: int
    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Next row
    :rtype: int
    """
    global _border_thin, _align_wrap, _bold_font, _std_font

    col, merge_len = 1, 2  # merge_len is the number of columns to be merged for the MAPS dashboard
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
    excel_util.cell_update(sheet, row, col, 'MAPS Dashboard Alerts', font=_bold_font, align=_align_wrap)
    i = 0
    for alert_obj in switch_obj.r_alert_objects():
        if alert_obj.alert_num() in al.AlertTable.maps_alerts:
            row += 1
            sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
            for col in range(1, merge_len+2):
                excel_util.cell_update(sheet, row, col, None, border=_border_thin)
            col = 1
            excel_util.cell_update(sheet, row, col, alert_obj.fmt_msg(), font=_std_font, align=_align_wrap)
            i += 1
    if i == 0:
        row += 1
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + merge_len)
        for col in range(1, merge_len+2):
            excel_util.cell_update(sheet, row, col, None, border=_border_thin)
        col = 1
        excel_util.cell_update(sheet, row, col, 'None', font=_std_font, align=_align_wrap, border=_border_thin)

    return row


def _switch_statistics(sheet, row, switch_obj):
    """Adds switch detail to the worksheet.

    :param sheet: Workbook sheet
    :type sheet: openpyxl.Worksheet
    :param row: Starting row
    :type row: int
    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Next row
    :rtype: int
    """
    global _border_thin, _align_wrap, _hdr2_font, _bold_font
    
    # Figure out what to put in the statistics summary section
    switch_stats_d = collections.OrderedDict()
    port_obj_l = switch_obj.r_port_objects()
    switch_stats_d['Physical Ports'] = len(port_obj_l)
    switch_stats_d['ICL-Ports'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.icl_ports))
    switch_stats_d['ISL (E-Ports)'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.e_ports))
    switch_stats_d['FC-Lag Ports'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.fc_lag_ports))
    port_obj_l = brcddb_search.match_test(port_obj_l, brcddb_search.f_ports)
    sum_logins = 0
    for port_obj in port_obj_l:
        sum_logins += len(port_obj.r_login_keys())
    switch_stats_d['Name Server Logins'] = sum_logins
    switch_stats_d['Port Logins at 1G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_1G))
    switch_stats_d['Port Logins at 2G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_2G))
    switch_stats_d['Port Logins at 4G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_4G))
    switch_stats_d['Port Logins at 8G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_8G))
    switch_stats_d['Port Logins at 16G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_16G))
    switch_stats_d['Port Logins at 32G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_32G))
    switch_stats_d['Port Logins at 64G'] = len(brcddb_search.match_test(port_obj_l, brcddb_search.login_64G))

    # Add the statistics summary items to the sheet
    for k, v in switch_stats_d.items():
        excel_util.cell_update(sheet, row, 1, None, border=_border_thin)
        excel_util.cell_update(sheet, row, 2, k, font=_std_font, align=_align_wrap, border=_border_thin)
        excel_util.cell_update(sheet, row, 3, v, font=_std_font, border=_border_thin)
        row += 1

    return row


def _add_switch(sheet, row, switch_obj, display, sheet_name, switch_name):
    """Adds switch detail to the worksheet.

    :param sheet: Workbook sheet
    :type sheet: openpyxl.Worksheet
    :param row: Starting row
    :type row: int
    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param display: List of keys to display. Find next instance of switch_key_case. Much less complex than port_page()
    :type display: dict
    :param switch_name: When True, adds a seperate line for the switch name.
    :type switch_name: bool
    :return: Next row
    :rtype: int
    """
    global _hdr, switch_key_case, _border_thin, _align_wrap, _hdr2_font, _bold_font

    row += 1

    # Add switch information from the API
    fab_obj = switch_obj.r_fabric_obj()
    if fab_obj is not None:
        link = fab_obj.r_get('report_app/hyperlink/sw')
        if link is not None:
            tl = link.split('!')
            brcddb_util.add_to_obj(switch_obj, 'report_app/hyperlink/sw', tl[0] + '!A' + str(row))

    # Add the switchname
    if switch_name:
        col = 1
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(_hdr))
        excel_util.cell_update(sheet, row, col, brcddb_switch.best_switch_name(switch_obj, wwn=True, did=True),
                                 font=_hdr2_font)
        row += 2

    # Add the MAPS dashboard
    row = _maps_dashboard(sheet, row, switch_obj) + 2

    # Add the switch details header
    col = 1
    for k in _hdr.keys():
        excel_util.cell_update(sheet, row, col, k, font=_bold_font)
        col += 1

    row += 1
    for k in display:
        font = report_utils.font_type_for_key(switch_obj, k)
        row, col = row+1, 1

        v = switch_obj.r_get(k)
        if k in switch_key_case:
            val = switch_key_case[k](switch_obj, k)
        elif k in brcddb_common.switch_conversion_tbl:
            val = '' if v is None else brcddb_common.switch_conversion_tbl[k][v]
        else:
            if isinstance(v, bool):
                val = 'Yes' if v else 'No'
            else:
                val = v if isinstance(v, (str, int, float)) else '' if v is None else str(v)
        # cell_fill_l is what goes in Comment, Parameter, and Setting cells
        cell_fill_l = [report_utils.comments_for_alerts(switch_obj, k), display[k] if k in display else k, val]

        for buf in cell_fill_l:
            excel_util.cell_update(sheet, row, col, buf, font=font, align=_align_wrap, border=_border_thin)
            col += 1

    return row


def switch_page(wb, tc, sheet_name, sheet_i, sheet_title, s_list_in, in_display=None, switch_name=True):
    """Creates a switch detail worksheet for the Excel report.
    
    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed. Default is 0
    :type sheet_i: int, None
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :param s_list_in: List of switch objects (SwitchObj) to display
    :type s_list_in: list, tuple, None, brcddb.classes.switch.SwitchObj
    :param in_display: Display table for switch parameters
    :type in_display: dict, None
    :param switch_name: When True, adds a seperate line for the switch name.
    :type switch_name: bool
    :rtype: None
    """
    global _sw_quick_d, _border_thin, _align_wrap, _std_font

    # Scrub user input
    s_list = brcddb_util.convert_to_list(s_list_in)
    display = rt.Switch.switch_display_tbl if in_display is None else in_display

    # Set up the worksheet and add each switch
    sheet, row = _setup_worksheet(wb, tc, sheet_name, 0 if sheet_i is None else sheet_i, sheet_title)
    for switch_obj in s_list:

        # Add the worksheet
        row = _add_switch(sheet, row, switch_obj, display, sheet_name, switch_name)
        row = _switch_statistics(sheet, row, switch_obj)

        # Add the links to the port sheets
        col = 2
        for k, v in _sw_quick_d.items():
            link = switch_obj.r_get(v)
            if link is not None:
                sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+1)
                excel_util.cell_update(sheet, row, col, k, font=_link_font, align=_align_wrap, link=link)
                row += 1

    return
