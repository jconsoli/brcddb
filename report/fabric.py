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
:mod:`brcddb.report.fabric` - Creates a fabric page to be added to an Excel Workbook

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 15 Jul 2020   | Initial Launch                                                                    |
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
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util

sheet = None
row = 1
hdr = collections.OrderedDict()
# Key is the column header and value is the width
hdr['Name'] = 22
hdr['WWN'] = 22
hdr['DID'] = 22
hdr['Firmware'] = 22
zone_key_conv = {
    'cfg-action': 'Configuration actions',
    'cfg-name': 'Effective Configuration',
    'checksum': 'Checksum',
    'db-avail': 'Available zone database size (bytes)',
    'db-committed': 'Size of commited defined zone database (bytes)',
    'db-max': 'Maximum permitted zone database size (bytes)',
    'db-transaction': 'Size (bytes) to commit the pending transaction',
    'transaction-token': 'Transaction token',
    'default-zone-access': 'All Access',
}


def _setup_worksheet(wb, tc, sheet_i, sheet_name, sheet_title):
    """Creates a fabric detail worksheet for the Excel report.

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

    # Set the column width
    col = 1
    for k, v in hdr.items():
        sheet.column_dimensions[xl.get_column_letter(col)].width = v
        col += 1


def _fabric_summary(fabric_obj):
    """Adds a fabric summary to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global row, sheet, hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('bold')

    # Add the headers
    row += 2
    col = 1
    for k in hdr.keys():
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].border = border
        sheet[cell].font = font
        sheet[cell] = k
        col += 1

    # Add the switches
    font = report_fonts.font_type('std')
    for switch_obj in fabric_obj.r_switch_objects():
        col = 1
        row += 1
        # Switch name
        buf = brcddb_switch.best_switch_name(switch_obj, False)
        if switch_obj.r_is_principal():
            buf = '*' + buf
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].border = border
        sheet[cell].font = font
        sheet[cell] = buf
        col += 1
        # Switch WWN
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].border = border
        sheet[cell].font = font
        sheet[cell] = switch_obj.r_obj_key()
        col += 1
        # Switch DID
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].border = border
        sheet[cell].font = font
        buf = switch_obj.r_get('brocade-fabric/fabric-switch/domain-id')
        if buf is None:
            buf = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/domain-id')
        sheet[cell] = '' if buf is None else buf
        col += 1
        # Switch Firmware
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].border = border
        sheet[cell].font = font
        buf = switch_obj.r_get('brocade-fabric/fabric-switch/firmware-version')
        if buf is None:
            buf = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/firmware-version')
        sheet[cell] = '' if buf is None else buf

    # Pincipal switch footnote
    row += 1
    col = 1
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = font
    sheet[cell] = '* indicates principal switch'


def _maps_dashboard(fabric_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global row, sheet, hdr

    col = 1
    row += 2
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('bold')
    sheet[cell].alignment = alignment
    sheet[cell] = 'MAPS Dashboard Alerts'
    font = report_fonts.font_type('std')
    i = 0
    for alert_obj in fabric_obj.r_alert_objects():
        if alert_obj.alert_num() in al.AlertTable.maps_alerts:
            row += 1
            sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
            for col in range(1, len(hdr)):
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
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
        for col in range(1, len(hdr) + 1):
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].border = border
        col = 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].alignment = alignment
        sheet[cell] = 'None'


def _zone_configuration(fabric_obj):
    """Adds the zone configuration summary to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global row, sheet, hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('std')
    obj = fabric_obj.r_eff_zone_cfg_obj()

    # Add the Defined Configurations
    row += 2
    col = 1
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr)+1)
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].alignment = alignment
    sheet[cell].border = border
    sheet[cell].font = report_fonts.font_type('bold')
    sheet[cell] = 'Defined Configurations'
    for obj in fabric_obj.r_zonecfg_objects():
        buf = obj.r_obj_key()
        if buf == '_effective_zone_cfg':
            continue
        row += 1
        if obj.r_is_effective():
            buf = '*' + buf
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
        for col in range(1, len(hdr)+1):
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].border = border
        col = 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].alignment = alignment
        sheet[cell].font = font
        sheet[cell] = buf

    # Effective zone footnote
    row += 1
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
    col = 1
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = font
    sheet[cell] = '* indicates effective zone configuration'

    # Effective zone configuration summary
    if obj is not None:
        row += 2
        col = 1
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('bold')
        sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=len(hdr))
        sheet[cell] = 'Effective Zone Configuration Summary'
        ec_obj = fabric_obj.r_get('brocade-zone/effective-configuration')
        if isinstance(ec_obj, dict):
            for k in ec_obj:
                row += 1
                col = 1
                sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+1)
                for i in range(col, col+2):
                    cell = xl.get_column_letter(i) + str(row)
                    sheet[cell].border = border
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].font = font
                sheet[cell].alignment = alignment
                sheet[cell] = zone_key_conv[k] if k in zone_key_conv else k
                col += 2
                sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+1)
                for i in range(col, col+2):
                    cell = xl.get_column_letter(i) + str(row)
                    sheet[cell].border = border
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].font = font
                sheet[cell].alignment = alignment
                v = ec_obj.get(k)
                try:
                    sheet[cell] = brcddb_common.zonecfg_conversion_tbl[k][v]
                except:
                    sheet[cell] = v
        else:
            row += 1
            col = 1
            sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 1)
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = font
            sheet[cell].alignment = alignment
            sheet[cell] = 'No effective configuration'


def fabric_page(wb, tc, sheet_i, sheet_name, sheet_title, fabric_obj):
    """Creates the fabric summary page

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_i: Relative location for this worksheet
    :type sheet_i: int
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_title: Title for sheet
    :type sheet_title: str
    :param fabric_obj: Fabric object
    :type fabric_obj: FabricObj
    :rtype: None
    """
    # Validate the user input
    err_msg = []
    if fabric_obj is None:
        err_msg.append('FabricObj was not defined.')
    elif brcddb_class_util.get_simple_class_type(fabric_obj) != 'FabricObj':
        err_msg.append('Wrong object type, ' + str(type(fabric_obj)) + 'Must be brcddb.classes.fabric.FabricObj.')
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Set up the worksheet and add the fabric
    _setup_worksheet(wb, tc, sheet_i, sheet_name, sheet_title)
    _fabric_summary(fabric_obj)
    _maps_dashboard(fabric_obj)
    _zone_configuration(fabric_obj)
    return
