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
:mod:`brcddb.report.chassis` - Creates a chassis page to be added to an Excel Workbook

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
import brcdapi.log as brcdapi_log
import brcddb.util.util as brcddb_util
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.report.utils as report_utils
import brcddb.report.fonts as report_fonts
import brcddb.report.switch as report_switch
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util

sheet = None
row = 1

hdr = collections.OrderedDict()
# Key is the column header and value is the width
hdr['Comment'] = 30
hdr['Parameter'] = 22
hdr['Setting'] = 22
hdr['col_only_3'] = 20
hdr['col_only_4'] = 10
hdr['col_only_5'] = 10
hdr['col_only_6'] = 10
hdr['col_only_7'] = 10
hdr['col_only_8'] = 10
hdr['col_only_9'] = 10

_fru = {}
_fru_hdr = {
    'brocade-fru/blade': {'h': 'Blades', 's': 'slot-number'},
    'brocade-fru/fan': {'h': 'Fans', 's': 'unit-number'},
    'brocade-fru/power-supply': {'h': 'Power Supplies', 's': 'unit-number'},
}

switch_hdr = collections.OrderedDict()
# Key is the column header and value is key used in the reference to the brcddb.report.switch_key_case table
switch_hdr['Name'] = '_SWITCH_NAME'
switch_hdr['WWN'] = '_SWITCH_WWN'
switch_hdr['Fabric ID'] = 'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id'
switch_hdr['Domain ID'] = 'brocade-fabric/fabric-switch/domain-id'


def _setup_worksheet(wb, tc, sheet_name, sheet_i, sheet_title, chassis_obj):
    """Creates a chassis detail worksheet for the Excel report.

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
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :rtype: None
    """
    global row, sheet, hdr

    # Create the worksheet and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    row = 1
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

    # Add the headers and set the column widths
    col = 1
    row += 2
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_2')
    sheet[cell] = brcddb_chassis.best_chassis_name(chassis_obj)
    row += 1
    for k, v in hdr.items():
        sheet.column_dimensions[xl.get_column_letter(col)].width = v
        if 'col_only' not in k:
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].border = report_fonts.border_type('thin')
            sheet[cell].font = report_fonts.font_type('bold')
            sheet[cell] = k
        col += 1


def _maps_dashboard(chassis_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :rtype: None
    """
    global row, sheet

    merge_len = 4  # NUmber of columns to be merged for the MAPS dashboard
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
    for alert_obj in chassis_obj.r_alert_objects():
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


##################################################################
#
# Case statements for _chassis_detail()
#
###################################################################


def cfru_blade_id_case(v):
    return brcddb_chassis.blade_name(v) + ' (' + str(v) + ')'


chassis_key_case = {}  # This is consistent with all  other reports. I just don't have anything chassis custom


chassis_fru_key_case = {
    'blade-id': cfru_blade_id_case,
}

_bladed_chassis_only = (
    'brocade-chassis/ha-status/ha-enabled',
    'brocade-chassis/ha-status/heartbeat-up',
    'brocade-chassis/ha-status/ha-synchronized',
    'brocade-chassis/ha-status/active-cp',
    'brocade-chassis/ha-status/active-slot',
    'brocade-chassis/ha-status/recovery-type',
    'brocade-chassis/ha-status/standby-cp',
    'brocade-chassis/ha-status/standby-health',
    'brocade-chassis/ha-status/standby-slot',
)


def _chassis_detail(chassis_obj, display):
    """Adds the chassis detail to the worksheet.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    global row, sheet, _bladed_chassis_only, _fru

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    for k in display:
        if k in ('brocade-fru/blade', 'brocade-fru/fan', 'brocade-fru/power-supply'):
            _fru.update({k: brcddb_util.convert_to_list(chassis_obj.r_get(k))})
        else:
            font = report_utils.font_type_for_key(chassis_obj, k)
            col = 1
            row += 1
            # Comments
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].border = border
            sheet[cell].alignment = alignment
            sheet[cell] = report_utils.comments_for_alerts(chassis_obj, k)
            # Key description
            col += 1
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].border = border
            sheet[cell].alignment = alignment
            sheet[cell] = display[k]
            # Value
            col += 1
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].border = border
            sheet[cell].alignment = alignment
            if k in chassis_key_case:
                sheet[cell] = chassis_key_case[k](chassis_obj, k)
            else:
                if not chassis_obj.r_is_bladded() and k in _bladed_chassis_only:
                    sheet[cell] = 'n/a'
                else:
                    v = chassis_obj.r_get(k)
                    if isinstance(v, bool):
                        sheet[cell] = '\u221A' if v else ''
                    else:
                        sheet[cell] = v if isinstance(v, (str, int, float)) else '' if v is None else str(v)


def _chassis_frus(chassis_obj, display):
    """Adds the chassis FRUs to the worksheet

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    global row, sheet, _fru, _fru_hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    for fk in _fru:
        row += 2
        col = 1
        # Add the headers
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('bold')
        sheet[cell].alignment = report_fonts.align_type('wrap')
        sheet[cell] = _fru_hdr[fk]['h']
        row += 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('std')
        sheet[cell].alignment = report_fonts.align_type('wrap')
        sheet[cell] = 'Comments'
        disp = display[fk]
        for k, v in disp.items():
            col += 1
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = report_fonts.font_type('std')
            sheet[cell].border = border
            sheet[cell].alignment = alignment
            sheet[cell] = disp[k]
        # Add the values
        for d in brcddb_util.sort_obj_num(_fru[fk], _fru_hdr[fk]['s'], r=False):
            row += 1
            col = 2
            for k in disp:
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].font = report_fonts.font_type('std')
                sheet[cell].border = border
                sheet[cell].alignment = alignment
                sheet[cell] = chassis_fru_key_case[k](d[k]) if k in chassis_fru_key_case and k in d \
                    else d[k] if k in d else ''
                if disp[k] == 'State':
                    # Add the comments
                    cell = xl.get_column_letter(1) + str(row)
                    sheet[cell].border = border
                    sheet[cell].alignment = alignment
                    if 'ault' in d[k]:
                        sheet[cell].font = report_fonts.font_type('error')
                        sheet[cell] = 'Fault'
                    else:
                        sheet[cell].font = report_fonts.font_type('std')
                        sheet[cell] = ''
                col += 1


def _logical_switches(chassis_obj, display):
    """Creates a chassis detail worksheet for the Excel report.

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    global row, sheet, switch_hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('bold')
    row += 2
    col = 1
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 4)
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = font
    sheet[cell].alignment = alignment
    sheet[cell] = 'Logical Switches'
    row += 1
    # The column headers
    for k in switch_hdr:
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell] = k
        col += 1
    # The values
    for switchObj in chassis_obj.r_switch_objects():
        row += 1
        col = 1
        font = report_fonts.font_type('std')
        for k in switch_hdr:
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].alignment = alignment
            k0 = switch_hdr[k]
            if k0 in report_switch.switch_key_case:
                sheet[cell] = report_switch.switch_key_case[k0](switchObj, k0)
            else:  # It can only be the domain ID
                sheet[cell] = switchObj.r_get(k0)
            col += 1


def chassis_page(wb, tc, sheet_name, sheet_i, sheet_title, chassis_obj, display):
    """Creates a chassis detail worksheet for the Excel report.

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
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param display: List of keys to display. Similar to switch_page()
    :type display: dict
    :rtype: None
    """
    # Validate the user input
    err_msg = []
    if chassis_obj is None:
        err_msg.append('chassis_obj was not defined.')
    elif brcddb_class_util.get_simple_class_type(chassis_obj) != 'ChassisObj':
        err_msg.append('Wrong object type, ' + str(type(chassis_obj)) + 'Must be brcddb.classes.chassis.ChassisObj.')
    if display is None:
        err_msg.append('display not defined.')
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Create the worksheet and add the chassis information
    _setup_worksheet(wb, tc, sheet_name, sheet_i, sheet_title, chassis_obj)
    _chassis_detail(chassis_obj, display)
    _maps_dashboard(chassis_obj)
    _chassis_frus(chassis_obj, display)
    _logical_switches(chassis_obj, display)
