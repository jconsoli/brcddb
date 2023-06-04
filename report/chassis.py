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
:mod:`brcddb.report.chassis` - Creates a chassis page to be added to an Excel Workbook

Public Methods::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | chassis_page          | Creates a chassis detail worksheet for the Excel report.                              |
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
    | 3.0.2     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2021   | No functional changes. Prepended "_" for private methods and defaulted index to 0 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2021   | No functional changes. Removed unused code and updated comments and doc strings.  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 28 Apr 2022   | Added report links                                                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 22 Jun 2022   | Added switch links in logical switch summary.                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 21 May 2023   | Documentation updates.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 04 Jun 2023   | Used URI references in brcdapi.util                                               |
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
import brcdapi.gen_util as gen_util
import brcdapi.util as brcdapi_util
import brcdapi.excel_fonts as excel_fonts
import brcdapi.excel_util as excel_util
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.report.utils as report_utils
import brcddb.report.switch as report_switch
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util
import brcddb.app_data.report_tables as rt

_sheet = None
_row = 1
_std_font = excel_fonts.font_type('std')
_bold_font = excel_fonts.font_type('bold')
_link_font = excel_fonts.font_type('link')
_hdr2_font = excel_fonts.font_type('hdr_2')
_hdr1_font = excel_fonts.font_type('hdr_1')
_align_wrap = excel_fonts.align_type('wrap')
_align_wrap_vc = excel_fonts.align_type('wrap_vert_center')
_align_wrap_c = excel_fonts.align_type('wrap_center')
_border_thin = excel_fonts.border_type('thin')

_hdr = collections.OrderedDict()
# Key is the column header and value is the width
_hdr['Comment'] = 30
_hdr['Parameter'] = 22
_hdr['Setting'] = 22
_hdr['col_only_3'] = 20
_hdr['col_only_4'] = 10
_hdr['col_only_5'] = 10
_hdr['col_only_6'] = 10
_hdr['col_only_7'] = 10
_hdr['col_only_8'] = 10
_hdr['col_only_9'] = 10

_fru = dict()
_fru_hdr = {
    'brocade-fru/blade': {'h': 'Blades', 's': 'slot-number'},
    'brocade-fru/fan': {'h': 'Fans', 's': 'unit-number'},
    'brocade-fru/power-supply': {'h': 'Power Supplies', 's': 'unit-number'},
}

_switch_hdr = collections.OrderedDict()
# Key is the column header and value is a dictionary as follows:
# k: key used in the reference to the brcddb.report.switch_key_case table
# l: Link. If true, adds the switch link
_switch_hdr['Name'] = dict(k='_SWITCH_NAME', l=True)
_switch_hdr['WWN'] = dict(k='_SWITCH_WWN', l=True)
_switch_hdr['Fabric ID'] = dict(k=brcdapi_util.bfls_fid, l=False)
_switch_hdr['Domain ID'] = dict(k=brcdapi_util.bfs_did, l=False)


def _setup_worksheet(wb, tc, sheet_name, sheet_i, sheet_title, chassis_obj):
    """Creates a chassis detail worksheet for the Excel report.

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
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :rtype: None
    """
    global _row, _sheet, _hdr, _bold_font, _border_thin, _hdr2_font, _hdr1_font, _link_font

    # Create the worksheet, set up the column widths, and add the report link
    _sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i, title=sheet_name)
    _sheet.page_setup.paperSize = _sheet.PAPERSIZE_LETTER
    _sheet.page_setup.orientation = _sheet.ORIENTATION_LANDSCAPE

    # Add the contents
    _row = col = 1
    if isinstance(tc, str):
        excel_util.cell_update(_sheet, _row, col, 'Contents', font=_link_font, link=tc)
        col += 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    excel_util.cell_update(_sheet, _row, col, sheet_title, font=_hdr1_font)
    _sheet.freeze_panes = _sheet['A2']

    # Add the headers and set the column widths
    _row, col = _row + 2, 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    excel_util.cell_update(_sheet, _row, col, brcddb_chassis.best_chassis_name(chassis_obj), font=_hdr2_font)
    _row += 1
    for k, v in _hdr.items():
        _sheet.column_dimensions[xl.get_column_letter(col)].width = v
        if 'col_only' not in k:
            excel_util.cell_update(_sheet, _row, col, k, font=_bold_font, border=_border_thin)
        col += 1


def _maps_dashboard(chassis_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :rtype: None
    """
    global _row, _sheet, _std_font, _border_thin, _align_wrap, _bold_font

    merge_len = 4  # NUmber of columns to be merged for the MAPS dashboard
    _row, col = _row+2, 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col + merge_len)
    excel_util.cell_update(_sheet, _row, col, 'MAPS Dashboard Alerts', font=_bold_font, align=_align_wrap,
                           border=_border_thin)

    i = 0
    for alert_obj in chassis_obj.r_alert_objects():
        if alert_obj.alert_num() in al.AlertTable.maps_alerts:
            _row += 1
            _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col + merge_len)
            for col in range(1, merge_len + 2):
                excel_util.cell_update(_sheet, _row, col, None, border=_border_thin)
            col, i = 1, i + 1
            excel_util.cell_update(_sheet, _row, col, alert_obj.fmt_msg(), font=_std_font, align=_align_wrap)
    if i == 0:
        _row += 1
        _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col + merge_len)
        for col in range(1, merge_len + 2):
            excel_util.cell_update(_sheet, _row, col, None, border=_border_thin)
        excel_util.cell_update(_sheet, _row, 1, 'None', font=_std_font, align=_align_wrap)


##################################################################
#
# Case statements for _chassis_detail()
#
###################################################################


def _cfru_blade_id_case(v):
    return brcddb_chassis.blade_name(v) + ' (' + str(v) + ')'


_chassis_key_case = dict()  # This is consistent with all  other reports. I just don't have anything chassis custom


chassis_fru_key_case = {
    'blade-id': _cfru_blade_id_case,
}

_bladed_chassis_only = (
    brcdapi_util.bc_ha,
    brcdapi_util.bc_heartbeat,
    brcdapi_util.bc_sync,
    brcdapi_util.bc_active_cp,
    brcdapi_util.bc_active_slot,
    brcdapi_util.bc_ha_recovery,
    brcdapi_util.bc_ha_standby_cp,
    brcdapi_util.bc_ha_standby_health,
    brcdapi_util.bc_ha_standby_slot,
)


def _chassis_detail(chassis_obj, display):
    """Adds the chassis detail to the worksheet.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    global _row, _sheet, _bladed_chassis_only, _fru, _border_thin

    for k in display:
        if 'brocade-fru' in k:
            _fru.update({k: gen_util.convert_to_list(chassis_obj.r_get(k))})
        else:
            font = report_utils.font_type_for_key(chassis_obj, k)
            _row, col = _row+1, 1
            if k in _chassis_key_case:
                val = _chassis_key_case[k](chassis_obj, k)
            else:
                if not chassis_obj.r_is_bladded() and k in _bladed_chassis_only:
                    val = 'n/a'
                else:
                    v = chassis_obj.r_get(k)
                    if isinstance(v, bool):
                        val = '\u221A' if v else ''
                    else:
                        val = v if isinstance(v, (str, int, float)) else '' if v is None else str(v)

            for buf in [report_utils.comments_for_alerts(chassis_obj, k),  # Comments
                        display[k],  # Key description
                        val]:  # Value
                excel_util.cell_update(_sheet, _row, col, buf, font=font, align=_align_wrap, border=_border_thin)
                col += 1


def _chassis_frus(display):
    """Adds the chassis FRUs to the worksheet

    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    global _row, _sheet, _fru, _fru_hdr, _border_thin, _align_wrap, _bold_font, _std_font

    for fk in _fru:
        _row, col = _row+2, 1
        # Add the headers
        excel_util.cell_update(_sheet, _row, col, _fru_hdr[fk]['h'], font=_bold_font, align=_align_wrap)
        _row += 1
        excel_util.cell_update(_sheet, _row, col, 'Comments', font=_std_font, align=_align_wrap)
        disp = display[fk]
        for k, v in disp.items():
            col += 1
            excel_util.cell_update(_sheet, _row, col, disp[k], font=_std_font, align=_align_wrap, border=_border_thin)
        # Add the values
        for d in gen_util.sort_obj_num(_fru[fk], _fru_hdr[fk]['s'], r=False):
            _row, col = _row+1, 2
            for k in disp:
                buf = chassis_fru_key_case[k](d[k]) if k in chassis_fru_key_case and k in d else d[k] if k in d else ''
                excel_util.cell_update(_sheet, _row, col, buf, font=_std_font, align=_align_wrap, border=_border_thin)
                if disp[k] == 'State':  # Add the comments
                    if 'ault' in d[k]:  # A simple way to match "Fault" or "fault"
                        buf, font = 'Fault', excel_fonts.font_type('error')
                    else:
                        buf, font = '', _std_font
                    excel_util.cell_update(_sheet, _row, col, buf, font=font, align=_align_wrap, border=_border_thin)
                col += 1


def _logical_switches(chassis_obj):
    """Add the logical switch summary.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :rtype: None
    """
    global _row, _sheet, _switch_hdr, _bold_font, _std_font, _align_wrap, _link_font

    _row, col = _row+2, 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col + 4)
    excel_util.cell_update(_sheet, _row, col, 'Logical Switches', font=_bold_font, align=_align_wrap)
    _row += 1

    # The column headers
    for k in _switch_hdr.keys():
        excel_util.cell_update(_sheet, _row, col, k, font=_bold_font)
        col += 1

    # The values
    for switch_obj in chassis_obj.r_switch_objects():
        _row, col = _row + 1, 1
        for k, d in _switch_hdr.items():
            buf = report_switch.switch_key_case[d['k']](switch_obj, d['k']) if d['k'] in report_switch.switch_key_case \
                else switch_obj.r_get(d['k'])  # It can only be the domain ID
            link = switch_obj.r_get('report_app/hyperlink/sw') if d['l'] else None
            font = _std_font if link is None else _link_font
            excel_util.cell_update(_sheet, _row, col, buf, font=font, align=_align_wrap, link=link)
            col += 1


def chassis_page(wb, tc, sheet_name, sheet_i, sheet_title, chassis_obj, in_display):
    """Creates a chassis detail worksheet for the Excel report.

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
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param in_display: List of keys to display. Default is brcddb.app_data.report_tables.chassis_display_tbl
    :type in_display: dict, None
    :rtype: None
    """
    # Validate the user input
    err_msg = list()
    if chassis_obj is None:
        err_msg.append('chassis_obj was not defined.')
    elif brcddb_class_util.get_simple_class_type(chassis_obj) != 'ChassisObj':
        err_msg.append('Wrong object type, ' + str(type(chassis_obj)) + 'Must be brcddb.classes.chassis.ChassisObj.')
    display = rt.Chassis.chassis_display_tbl if in_display is None else in_display
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Create the worksheet and add the chassis information
    _setup_worksheet(wb, tc, sheet_name, 0 if sheet_i is None else sheet_i, sheet_title, chassis_obj)
    _chassis_detail(chassis_obj, display)
    _maps_dashboard(chassis_obj)
    _chassis_frus(display)
    _logical_switches(chassis_obj)
