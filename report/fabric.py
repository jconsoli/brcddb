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
    | 3.0.2     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Added FID to fabric summary.                                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2021   | No funcitonal changes. Added defaults for display tables and sheet indicies.      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '14 Nov 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import collections
import openpyxl.utils.cell as xl
import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util

_sheet = None
_row = 1
_hdr = collections.OrderedDict()
# Key is the column header and value is the width
_hdr['Name'] = 30
_hdr['WWN'] = 22
_hdr['DID'] = 10
_hdr['Fabric ID'] = 10
_hdr['Firmware'] = 22
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
    :param sheet_i: Sheet index where page is to be placed. Default is 0
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global _row, _sheet, _hdr

    # Create the worksheet, add the headers, and set up the column widths
    _sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i, title=sheet_name)
    _sheet.page_setup.paperSize = _sheet.PAPERSIZE_LETTER
    _sheet.page_setup.orientation = _sheet.ORIENTATION_LANDSCAPE
    _row = 1
    col = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell].hyperlink = '#' + tc + '!A1'
        _sheet[cell].font = report_fonts.font_type('link')
        _sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(_row)
    _sheet[cell].font = report_fonts.font_type('hdr_1')
    _sheet[cell] = sheet_title
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    _sheet.freeze_panes = _sheet['A2']

    # Set the column width
    col = 1
    for k, v in _hdr.items():
        _sheet.column_dimensions[xl.get_column_letter(col)].width = v
        col += 1


def _fabric_summary(fabric_obj):
    """Adds a fabric summary to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global _row, _sheet, _hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('bold')

    # Add the headers
    _row += 2
    col = 1
    for k in _hdr.keys():
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell].alignment = alignment
        _sheet[cell].border = border
        _sheet[cell].font = font
        _sheet[cell] = k
        col += 1
    _row += 1

    # Setup the common cell attributes
    font = report_fonts.font_type('std')
    switch_obj_l = fabric_obj.r_switch_objects()
    row = _row
    for switch_obj in switch_obj_l:
        for col in range(1, len(_hdr)+1):
            cell = xl.get_column_letter(col) + str(row)
            _sheet[cell].alignment = alignment
            _sheet[cell].border = border
            _sheet[cell].font = font
        row += 1

    # Add the switch summary
    for switch_obj in switch_obj_l:
        col = 1
        # Switch name
        buf = brcddb_switch.best_switch_name(switch_obj, False)
        if switch_obj.r_is_principal():
            buf = '*' + buf
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell] = buf
        col += 1
        # Switch WWN
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell] = switch_obj.r_obj_key()
        col += 1
        # Switch DID
        cell = xl.get_column_letter(col) + str(_row)
        buf = switch_obj.r_get('brocade-fabric/fabric-switch/domain-id')
        _sheet[cell] = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/domain-id') if buf is None \
            else buf
        col += 1
        # Switch FID
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell] = brcddb_switch.switch_fid(switch_obj)
        col += 1
        # Firmware version
        cell = xl.get_column_letter(col) + str(_row)
        buf = switch_obj.r_get('brocade-fabric/fabric-switch/firmware-version')
        _sheet[cell] = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/firmware-version') if \
            buf is None else buf
        _row += 1

    # Pincipal switch footnote
    col = 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    cell = xl.get_column_letter(col) + str(_row)
    _sheet[cell].font = font
    _sheet[cell] = '* indicates principal switch'


def _maps_dashboard(fabric_obj):
    """Adds the MAPS dashboard to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global _row, _sheet, _hdr

    col = 1
    _row += 2
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    cell = xl.get_column_letter(col) + str(_row)
    _sheet[cell].font = report_fonts.font_type('bold')
    _sheet[cell].alignment = alignment
    _sheet[cell] = 'MAPS Dashboard Alerts'
    font = report_fonts.font_type('std')
    i = 0
    for alert_obj in fabric_obj.r_alert_objects():
        if alert_obj.alert_num() in al.AlertTable.maps_alerts:
            _row += 1
            _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
            for col in range(1, len(_hdr)):
                cell = xl.get_column_letter(col) + str(_row)
                _sheet[cell].border = border
            col = 1
            cell = xl.get_column_letter(col) + str(_row)
            _sheet[cell].font = font
            _sheet[cell].alignment = alignment
            _sheet[cell] = alert_obj.fmt_msg()
            i += 1
    if i == 0:
        _row += 1
        _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
        for col in range(1, len(_hdr) + 1):
            cell = xl.get_column_letter(col) + str(_row)
            _sheet[cell].border = border
        col = 1
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell].font = font
        _sheet[cell].alignment = alignment
        _sheet[cell] = 'None'


def _zone_configuration(fabric_obj):
    """Adds the zone configuration summary to the worksheet.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :rtype: None
    """
    global _row, _sheet, _hdr

    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('std')
    obj = fabric_obj.r_eff_zone_cfg_obj()

    # Add the Defined Configurations
    _row += 2
    col = 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr)+1)
    cell = xl.get_column_letter(col) + str(_row)
    _sheet[cell].alignment = alignment
    _sheet[cell].border = border
    _sheet[cell].font = report_fonts.font_type('bold')
    _sheet[cell] = 'Defined Configurations'
    for obj in fabric_obj.r_zonecfg_objects():
        buf = obj.r_obj_key()
        if buf == '_effective_zone_cfg':
            continue
        _row += 1
        if obj.r_is_effective():
            buf = '*' + buf
        _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
        for col in range(1, len(_hdr)+1):
            cell = xl.get_column_letter(col) + str(_row)
            _sheet[cell].border = border
        col = 1
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell].alignment = alignment
        _sheet[cell].font = font
        _sheet[cell] = buf

    # Effective zone footnote
    _row += 1
    _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
    col = 1
    cell = xl.get_column_letter(col) + str(_row)
    _sheet[cell].font = font
    _sheet[cell] = '* indicates effective zone configuration'

    # Effective zone configuration summary
    if obj is not None:
        _row += 2
        col = 1
        cell = xl.get_column_letter(col) + str(_row)
        _sheet[cell].font = report_fonts.font_type('bold')
        _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
        _sheet[cell] = 'Effective Zone Configuration Summary'
        ec_obj = fabric_obj.r_get('brocade-zone/effective-configuration')
        if isinstance(ec_obj, dict):
            for k in ec_obj:
                _row += 1
                col = 1
                _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col+1)
                cell = xl.get_column_letter(col) + str(_row)
                _sheet[cell].font = font
                _sheet[cell].alignment = alignment
                # _sheet[cell].border = border
                _sheet[cell] = zone_key_conv[k] if k in zone_key_conv else k
                col += 2
                _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=len(_hdr))
                cell = xl.get_column_letter(col) + str(_row)
                _sheet[cell].font = font
                _sheet[cell].alignment = alignment
                v = ec_obj.get(k)
                try:
                    _sheet[cell] = brcddb_common.zonecfg_conversion_tbl[k][v]
                except:
                    _sheet[cell] = v
                for i in range(1, len(_hdr)+1):
                    cell = xl.get_column_letter(i) + str(_row)
                    _sheet[cell].border = border
        else:
            _row += 1
            col = 1
            _sheet.merge_cells(start_row=_row, start_column=col, end_row=_row, end_column=col + 1)
            cell = xl.get_column_letter(col) + str(_row)
            _sheet[cell].font = font
            _sheet[cell].alignment = alignment
            _sheet[cell] = 'No effective configuration'


def fabric_page(wb, tc, sheet_i, sheet_name, sheet_title, fabric_obj):
    """Creates the fabric summary page

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param sheet_i: Relative location for this worksheet. Default is 0
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
    err_msg = list()
    if fabric_obj is None:
        err_msg.append('FabricObj was not defined.')
    elif brcddb_class_util.get_simple_class_type(fabric_obj) != 'FabricObj':
        err_msg.append('Wrong object type, ' + str(type(fabric_obj)) + 'Must be brcddb.classes.fabric.FabricObj.')
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Set up the worksheet and add the fabric
    _setup_worksheet(wb, tc, 0 if sheet_i is None else sheet_i, sheet_name, sheet_title)
    _fabric_summary(fabric_obj)
    _maps_dashboard(fabric_obj)
    _zone_configuration(fabric_obj)
    return
