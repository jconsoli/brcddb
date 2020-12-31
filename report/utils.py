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

:mod:`report.utils` - Create and save workbooks, title page, and miscellaneous common methods.

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
    | 3.0.2     | 29 Sep 2020   | Set type for col_width to list or tuple in title_page(), added valid_sheet_name.  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 01 Nov 2020   | Fix bug if row was a list in cell_match_val(). Added read_sheet() and             |
    |           |               | get_next_switch_d()                                                               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2020   | Made parse_sfp_file() more effecient and added protection against a malformed file|
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2020   | Fixed exception case when a bad merge type was passed or merge was 0              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '31 Dec 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

import openpyxl as xl
import openpyxl.utils.cell as xl_util
import re
import brcdapi.log as brcdapi_log
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.util.util as brcddb_util
import brcddb.report.fonts as report_fonts
import brcddb.util.search as brcddb_search

# Use this to create a sheet name that is not only valid for Excel but can have a link. Note when creating a link to a
# sheet in Excel, there are additional restrictions on the sheet name. For example, it cannot contain a space. Sample
# use: good_sheet_name = valid_sheet_name.sub('_', bad_sheet_name)
valid_sheet_name = re.compile(r'[^\d\w_]')

#######################################################################
#
# Common case statements in port_page(), switch_page(), chassis_page()
#
#######################################################################


def fabric_name_case(obj, k=None, wwn=None):
    return brcddb_fabric.best_fab_name(obj.r_fabric_obj(), False)


def fabric_name_or_wwn_case(obj, k=None, wwn=None):
    return brcddb_fabric.best_fab_name(obj.r_fabric_obj(), True)


def fabric_wwn_case(obj, k=None, wwn=None):
    return obj.r_fabric_key()


def font_type(obj_list):
    """Determines the display font based on alerts.

    :param obj_list: List of brcddb.classes.alert.AlertObj
    :param obj_list: list
    """
    font = report_fonts.font_type('std')
    for alert_obj in obj_list:
        if alert_obj.is_error():
            return report_fonts.font_type('error')
        elif alert_obj.is_warn():
            font = report_fonts.font_type('warn')
    return font


def font_type_for_key(obj, k=None):
    """Determines the display font based on alerts associated with an object.

    :param obj: Any brcddb object
    :param obj: ChassisObj, FabricObj, SwitchObj, PortObj, ZoneObj, ZoneCfgObj, AliasObj
    :param k: Key to associate the alert with
    :type k: str
    """
    font = report_fonts.font_type('std')
    a_list = obj.r_alert_objects() if k is None else [alertObj for alertObj in obj.r_alert_objects() if alertObj.key() == k]
    for alertObj in a_list:
        if alertObj.is_error():
            return report_fonts.font_type('error')
        elif alertObj.is_warn():
            font = report_fonts.font_type('warn')
    return font


def comments_for_alerts(gobj, k=None, wwn=None):
    """Converts alerts associated with an object to a human readable string. Multiple comments seprated with /n

    :param gobj: Any brcddb object
    :type gobj: ChassisObj, FabricObj, SwitchObj, PortObj, ZoneObj, ZoneCfgObj, AliasObj
    :param k: Key to associate the alert with
    :type k: str
    :param wwn: If nont None, the object is assumed to be a portObj and the comments returned are for the login
    :type wwn: None, str
    :return: /n seperated list of alert message(s) associated with obj
    :rtype: str
    """
    obj = gobj if wwn is None else gobj.r_fabric_obj().r_login_obj(wwn)
    if obj is None:
        return ''
    a_list = obj.r_alert_objects() if k is None else [alertObj for alertObj in obj.r_alert_objects() if
                                                      alertObj.key() == k]
    return '\n'.join([alertObj.fmt_msg() for alertObj in a_list])


def combined_login_alert_objects(login_obj):
    """Combines login alert objects with FDMI HBA and FDMI port alerts objects

    :param login_obj: Login object
    :type : brcddb.classes.login.LoginObj
    :return: List of AlertObj
    :rtype: list
    """
    a_list = list()
    if login_obj is not None:
        a_list.extend(login_obj.r_alert_objects())  # Alerts tied to the login
        wwn = login_obj.r_obj_key()
        fab_obj = login_obj.r_fabric_obj()
        if fab_obj is not None:
            obj = fab_obj.r_fdmi_node_obj(wwn)  # FDMI HBA (node) alerts
            if obj is not None:
                a_list.extend(obj.r_alert_objects())
            obj = fab_obj.r_fdmi_port_obj(wwn)  # FDMI port alerts
            if obj is not None:
                a_list.extend(obj.r_alert_objects())
    return a_list


def combined_login_alerts(login_obj, wwn):
    """Converts alerts associated with a login object and the login and FDMI objects for lwwn to a human readable string
combined_login_alerts
    :param login_obj: Port object
    :type login_obj: brcddb.classes.port.PortObj
    :param wwn: Login wwn
    :type wwn: str
    :return: CSV list of alert message(s) associated with obj
    :rtype: str
    """
    a_list = combined_login_alert_objects(login_obj)
    return '\n'.join([obj.fmt_msg() for obj in a_list]) if a_list is not None and len(a_list) > 0 else ''


def combined_alert_objects(port_obj, wwn):
    """Combines alerts associated with a port object and the login and FDMI objects for wwn.

    :param port_obj: Port object
    :type port_obj: brcddb.classes.port.PortObj
    :param wwn: Login wwn
    :type wwn: str
    :return: List of AlertObj
    :rtype: list
    """
    a_list = [obj for obj in port_obj.r_alert_objects()]  # All port alerts
    fab_obj = port_obj.r_fabric_obj()
    if fab_obj is not None and wwn is not None:
        obj = fab_obj.r_login_obj(wwn)
        if obj is not None:
            a_list.extend(obj.r_alert_objects())
        obj = fab_obj.r_fdmi_node_obj(wwn)
        if obj is not None:
            a_list.extend(obj.r_alert_objects())
        obj = fab_obj.r_fdmi_port_obj(wwn)
        if obj is not None:
            a_list.extend(obj.r_alert_objects())
    return a_list


def combined_alerts(port_obj, wwn):
    """Converts alerts associated with a port object and the login and FDMI objects for lwwn to a human readable string.

    :param port_obj: Port object
    :type port_obj: brcddb.classes.port.PortObj
    :param wwn: Login wwn
    :type wwn: str
    :return: CSV list of alert message(s) associated with obj
    :rtype: str
    """
    a_list = combined_alert_objects(port_obj, wwn)
    return '\n'.join([obj.fmt_msg() for obj in a_list]) if a_list is not None and len(a_list) > 0 else ''


def new_report():
    """Creates a workbook object for the Excel report.

    :return: wb
    :rtype: Workbook object
    """
    return xl.Workbook()


def save_report(wb, file_name='Report.xlsx'):
    """Saves a workbook object as an Excel file.

    :param wb: Workbook object
    :type wb: class
    :param file_name: Report name
    :type file_name: str
    """
    wb.save(file_name)


def title_page(wb, tc, sheet_name, sheet_i, sheet_title, content, col_width):
    """Creates a title page for the Excel report.

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1.
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed. Typically 0
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, with light blue fill at the top of the sheet
    :type sheet_title: str
    :param content: Caller defined content. List or tuple of dictionaries to add to the title page. See comments below
    :type content: list, tuple
    :param col_width: List of column widths to set on sheet
    :type col_width: list, tuple
    :rtype: None
    """
    # dict defined as noted below. Any unspecified item is ignored which means the default is whatever default is
    # configured in Excel.
#        content_item = {
#            'new_row':  False           # Default is True. Setting this to False is useful when using different cell
#                                        # attributes for different columns. Otherwise, all cell attributes are applied
#                                        # to all cells.
#            'font': 'hdr_1',            # Predefined font type in font_tbl
#            'fill': 'light_blue'        # Predefined cell fill type in fill_tbl
#            'border': 'thin'            # Predefined border type in border_tbl
#            'align': 'wrap'             # Predefined align type in align_tbl
#            'merge': 2,                 # Number of columns to merge, starting from current column
#            'disp': ('col_1', 'col_2', 'etc')   # Str, list or tuple. Content to add to the worksheet
#        }
#        Example:
#        content = (
#            {'font': 'hdr_1', 'merge': 3, 'align': 'wrap_center', 'disp': 'Title Page'},
#            {}, # Skip a row
#            {'font': 'std', 'align': 'wrap', 'disp': ('col_1', 'col_2', 'col_3') },
#        )

    # Set up the sheet
    col = 1
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    for i in col_width:
        sheet.column_dimensions[xl_util.get_column_letter(col)].width = i
        col += 1
    max_col = col - 1
    row = 1
    col = 1
    if isinstance(tc, str):
        cell = xl_util.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl_util.get_column_letter(col) + str(row)
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=max_col)
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell].fill = report_fonts.fill_type('lightblue')
    sheet[cell] = sheet_title
    row += 2
    # Add the content
    # Intended for general users so lots of error checking.
    col = 1
    if isinstance(content, (list, tuple)):
        for obj in content:
            if isinstance(obj, dict):
                display = list()
                if 'disp' in obj:
                    if isinstance(obj.get('disp'), (str, int, float)):
                        display.append(obj.get('disp'))
                    elif isinstance(obj.get('disp'), (list, tuple)):
                        display = obj.get('disp')
                    elif obj.get('disp') is None:
                        pass
                    else:
                        brcdapi_log.exception('Unknown disp type, ' + str(type((obj.get('disp')))) + ', at row ' +
                                              str(row), True)
                for buf in display:
                    cell = xl_util.get_column_letter(col) + str(row)
                    if 'hyper' in obj:
                        sheet[cell].hyperlink = obj.get('hyper')
                        sheet[cell] = buf
                    else:
                        sheet[cell] = buf
                    if 'font' in obj:
                        sheet[cell].font = report_fonts.font_type(obj.get('font'))
                    if 'align' in obj:
                        sheet[cell].alignment = report_fonts.align_type(obj.get('align'))
                    if 'border' in obj:
                        sheet[cell].border = report_fonts.border_type(obj.get('border'))
                    if 'fill' in obj:
                        sheet[cell].fill = report_fonts.fill_type(obj.get('fill'))
                    if 'merge' in obj:
                        if isinstance(obj.get('merge'), int):
                            if obj.get('merge') > 1:
                                sheet.merge_cells(start_row=row, start_column=col, end_row=row,
                                                  end_column=(col + obj.get('merge') - 1))
                                col += obj.get('merge')
                        else:
                            brcdapi_log.exception('Merge must be an integer. Type: ' + str(type(obj.get('merge'))),
                                                  True)
                            col += 1
                    else:
                        col += 1
                    if 'hyper' in obj:
                        sheet[cell].hyperlink = (obj.get('hyper') + '.')[:-1]
                if 'new_row' not in obj or ('new_row' in obj and obj.get('new_row')):
                    row += 1
                    col = 1
            else:
                brcdapi_log.exception('Invalid type in content list, ' + str(type(obj)) + ', at row ' + str(row), True)
    else:
        brcdapi_log.exception('Invalid content type: ' + str(type(content)), True)


def col_to_num(cell):
    """Converts a cell reference to a column number. This is a little more effecient than the openpyxl method

    :param cell: Excel spreadsheet cell reference. Example: 'AR20' or just 'AR'
    :type cell: str
    :return: Column number. 0 if column not found
    :rtype: int
    """
    r = 0
    for i in range(0, len(cell)):
        x = ord(cell[i].upper()) - 64
        if x < 1 or x > 26:
            break
        r = (r * 26) + x
    return r


def cell_match_val(sheet, val, col=None, row=None, num=1):
    """Finds the cell matching a value

    :param sheet: Sheet structure returned from wb.create_sheet()
    :type sheet: class
    :param val: Cell contents we're looking for
    :type val: int, float, str
    :param col: List of columns letters to look in. If None, checks all columns on sheet.
    :type col: list, str, None
    :param row: Row number or list of row numbers to look in. If None, checks all rows on sheet.
    :type row: int, list, None
    :param num: Number of instances to find
    :type num: int
    :return: List of cell references where value found. If num == 1: just one str is returned. None if not found
    :rtype: str, list, None
    """
    col_list = [xl_util.get_column_letter(i) for i in range(1, sheet.max_column)] if col is None \
        else brcddb_util.convert_to_list(col)
    row_list = [i for i in range(1, sheet.max_row)] if row is None else brcddb_util.convert_to_list(row)

    class Found(Exception):
        pass
    ret = list()
    try:
        for c in col_list:
            for r in row_list:
                cell = c + str(r)
                rv = sheet[cell].value
                if (isinstance(val, (int, float)) and isinstance(rv, (int, float))) or \
                        (isinstance(val, str) and isinstance(rv, str)):
                    if val == rv:
                        ret.append(cell)
                        if num >= len(ret):
                            raise Found
    except Found:
        pass

    if num == 1:
        if len(ret) > 0:
            return ret[0]
        else:
            return None
    else:
        return ret


def read_sheet(sheet, order='col'):
    """Reads the contents (values) of a worksheet into a list of dict of:

    sl Detail:
    +---------------+---------------------------------------------------------------------------------------+
    | key           | Value description                                                                     |
    +===============+=======================================================================================+
    | cell          | Cell reference.                                                                       |
    +---------------+---------------------------------------------------------------------------------------+
    | val           | Value read from cell.                                                                 |
    +---------------+---------------------------------------------------------------------------------------+

    Intended to be used by methods that will feed this list to brcddb.utils.search.match_test()

    :param sheet: Sheet structure returned from wb.create_sheet()
    :type sheet: class
    :param order: Order in which to read. 'row' means read by row, then each individual column. 'col' for column 1st
    :type order: str
    :return sl: List of dict as noted above
    :rtype sl: list
    :return al: List of lists. Contents of the worksheet referenced by al[col-1][row-1] if order is 'col' or
                al[row-1][col-1] if order is 'row'
    :rtype al: list
    """
     # Read in all the cell values
    sl = list()
    al = list()
    if order.lower() == 'col':
        for col in range(1, sheet.max_column):
            col_ref = xl_util.get_column_letter(col)
            rl = list()
            for row in range(1, sheet.max_row):
                cell = col_ref + str(row)
                v = sheet[cell].value
                rl.append(v)
                if v is not None and col not in hidden_columns and row not in hidden_rows:
                    sl.append(dict(cell=cell, val=v))
            al.append(rl)
    else:
        for row in range(1, sheet.max_row+1):
            cl = list()
            for col in range(1, sheet.max_column):
                cell = xl_util.get_column_letter(col) + str(row)
                v = sheet[cell].value
                cl.append(v)
                if v is not None:
                    sl.append(dict(cell=cell, val=v))
            al.append(cl)

    return sl, al


def get_next_switch_d(switch_list, val, test_type, ignore_case=False):
    """Finds the first match in an sl list returned from read_sheet() and returns the next entry in switch_list

    :param switch_list: A list of dictionaries as returned from brcddb.report.utils.read_sheet()
    :type switch_list: list, tuple
    :param val: The value to look for
    :type val: str, int, float
    :param test_type: The type of test to perform. See brcddb.util.search.match_test
    :type test_type: str
    :param ignore_case: If True, performs a case insensitive search
    :return: Entry in switch_list. None if not found or if the match was the last entry in switch_list
    :rtype: dict, None
    """
    ml = brcddb_search.match_test(switch_list, dict(k='val', v=val, t=test_type, i=ignore_case))
    if len(ml) > 0:
        cell = ml[0]['cell']  # Find this cell
        for i in range(0, len(switch_list)):
            if switch_list[i]['cell'] == cell:
                return None if i + 1 >= len(switch_list) else switch_list[i+1]
    return None


# Rather than rely on the user to not move columns or worksheets around, we use the tables below to figure out where
# everything is. The first key is a common name for each rule which is only used internally in _parse_sfp_file() to sort
# out all the rules. The keys in 'mem' are used to match the column headers in the Excel workbook.
_convert_action = {  # Key is the CLI action and value is the API action
    'decom': 'decomission',  # Yes, decommission is spelled incorrectly in FOS
    'email': 'e-mail',
    'fence': 'port-fence',
    'toggle': 'port-toggle',
    'sfp_marginal': 'sfp-marginal',
    'snmp': 'snmp-trap',
    'sw_critical': 'sw-critical',
    'sw_marginal': 'sw-marginal',
    'unquar': 'un-quarantine',
    'uninstall_vtap': 'vtap-uninstall',
}


def _action_value(group, val):
    return {'action': [_convert_action[buf] if buf in _convert_action else buf for buf in val.split(';')]}


def _name_value(group, val):
    return val + group


def _gen_value(group, val):
    return val


def _int_str_value(group, val):
    return str(val)


_rules = {
    'current_h': {
        'monitoring-system': 'CURRENT',
        'logical-operator': 'ge',
        'mem': {
            'Current High (mA)': {'api': 'threshold-value', 'val': _int_str_value},
            'Current High Name Prefix': {'api':  'name', 'val': _name_value},
            'Current High Sev': {'api':  'event-severity', 'val': _gen_value},
            'Current High QT': {'api':  'quiet-time', 'val': _gen_value},
            'Current High Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'current_l': {
        'monitoring-system': 'CURRENT',
        'logical-operator': 'le',
        'mem': {
            'Current Low (mA)': {'api':  'threshold-value', 'val': _int_str_value},
            'Current Low Name Prefix': {'api':  'name', 'val': _name_value},
            'Current Low Sev': {'api':  'event-severity', 'val': _gen_value},
            'Current Low QT': {'api':  'quiet-time', 'val': _gen_value},
            'Current Low Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'voltage_h': {
        'monitoring-system': 'VOLTAGE',
        'logical-operator': 'ge',
        'mem': {
            'Voltage High (mV)': {'api':  'threshold-value', 'val': _int_str_value},
            'Voltage High Name Prefix': {'api':  'name', 'val': _name_value},
            'Voltage High Sev': {'api':  'event-severity', 'val': _gen_value},
            'Voltage High QT': {'api':  'quiet-time', 'val': _gen_value},
            'Voltage High Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'voltage_l': {
        'monitoring-system': 'VOLTAGE',
        'logical-operator': 'le',
        'mem': {
            'Voltage Low (mV)': {'api':  'threshold-value', 'val': _int_str_value},
            'Voltage Low Name Prefix': {'api':  'name', 'val': _name_value},
            'Voltage Low Sev': {'api':  'event-severity', 'val': _gen_value},
            'Voltage Low QT': {'api':  'quiet-time', 'val': _gen_value},
            'Voltage Low Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'temp_h': {
        'monitoring-system': 'SFP_TEMP',
        'logical-operator': 'ge',
        'mem': {
            'Temp High (C)': {'api':  'threshold-value', 'val': _int_str_value},
            'Temp High Name Prefix': {'api':  'name', 'val': _name_value},
            'Temp High Sev': {'api':  'event-severity', 'val': _gen_value},
            'Temp High QT': {'api':  'quiet-time', 'val': _gen_value},
            'Temp High Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'temp_l': {
        'monitoring-system': 'SFP_TEMP',
        'logical-operator': 'le',
        'mem': {
            'Temp Low (C)': {'api':  'threshold-value', 'val': _int_str_value},
            'Temp Low Name Prefix': {'api':  'name', 'val': _name_value},
            'Temp Low Sev': {'api':  'event-severity', 'val': _gen_value},
            'Temp Low QT': {'api':  'quiet-time', 'val': _gen_value},
            'Temp Low Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'tx_h': {
        'monitoring-system': 'TXP',
        'logical-operator': 'ge',
        'mem': {
            'Tx High (uW)': {'api':  'threshold-value', 'val': _int_str_value},
            'Tx High Name Prefix': {'api':  'name', 'val': _name_value},
            'Tx High Sev': {'api':  'event-severity', 'val': _gen_value},
            'Tx High QT': {'api':  'quiet-time', 'val': _gen_value},
            'Tx High Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'tx_l': {
        'monitoring-system': 'TXP',
        'logical-operator': 'le',
        'mem': {
            'Tx Low (uW)': {'api':  'threshold-value', 'val': _int_str_value},
            'Tx Low Name Prefix': {'api':  'name', 'val': _name_value},
            'Tx Low Sev': {'api':  'event-severity', 'val': _gen_value},
            'Tx Low QT': {'api':  'quiet-time', 'val': _gen_value},
            'Tx Low Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'rx_h': {
        'monitoring-system': 'RXP',
        'logical-operator': 'ge',
        'mem': {
            'Rx High (uW)': {'api':  'threshold-value', 'val': _int_str_value},
            'Rx High Name Prefix': {'api':  'name', 'val': _name_value},
            'Rx High Sev': {'api':  'event-severity', 'val': _gen_value},
            'Rx High QT': {'api':  'quiet-time', 'val': _gen_value},
            'Rx High Action': {'api':  'actions', 'val': _action_value},
        }
    },
    'rx_l': {
        'monitoring-system': 'RXP',
        'logical-operator': 'le',
        'mem': {
            'Rx Low (uW)': {'api':  'threshold-value', 'val': _int_str_value},
            'Rx Low Name Prefix': {'api':  'name', 'val': _name_value},
            'Rx Low Sev': {'api':  'event-severity', 'val': _gen_value},
            'Rx Low QT': {'api':  'quiet-time', 'val': _gen_value},
            'Rx Low Action': {'api':  'actions', 'val': _action_value},
        },
    },
}


def parse_sfp_file_for_rules(file, groups):
    """Parses Excel file with the new SFP rules Formatted to be sent to the API. See sfp_rules_rx.xlsx

    :param file: Path and name of Excel Workbook with new SFP rules
    :type file: str
    :param groups: List of groups defined on this switch - returned from 'brocade-maps/group'
    :type groups: list
    :return: List of SFP rule dictionaries. None if an error was encountered
    :rtype: list, None
    """
    new_sfp_rules = list()  # The list of rule dictionaries that will be returned

    # Load the workbook
    try:
        wb = xl.load_workbook(file, data_only=True)
    except:
        return None

    # Find where all the columns are
    sheet = wb['new_SFP_rules']
    cell = cell_match_val(sheet, 'Group', None, 1)
    if cell is None:
        brcdapi_log.log('Could not find column with \'Group\'', True)
        return None
    group_col = xl_util.get_column_letter(col_to_num(cell))
    for k0, v0 in _rules.items():
        for k1, v1 in v0.get('mem').items():
            cell = cell_match_val(sheet, k1, None, 1)
            if cell is not None:
                v1.update({'col': xl_util.get_column_letter(col_to_num(cell))})

    # Build the list of rules to send to the switch.
    row = 2
    group = sheet[group_col + str(row)].value
    while group != '__END__':
        if group in groups:
            for k0, v0 in _rules.items():
                d = {'is-rule-on-rule': False, 'time-base': 'NONE', 'group-name': group}
                for k1, v1 in v0.items():
                    if k1 != 'mem':
                        d.update({k1: v1})
                for k1, v1 in v0.get('mem').items():
                    d.update({v1.get('api'): v1.get('val')(group, sheet[v1.get('col') + str(row)].value)})
                new_sfp_rules.append(d)
        row += 1
        group = sheet[group_col + str(row)].value

    return new_sfp_rules


def parse_sfp_file(file):
    """Parses Excel file with the new SFP rules. See sfp_rules_rx.xlsx

    :param file: Path and name of Excel Workbook with new SFP rules
    :type file: str
    :return: List of dictionaries. The key for each dictionary is the column header and the value is the cell value
    :rtype: list
    """
    parsed_sfp_sheet = list()  # The list of rule dictionaries that will be returned

    # Load the workbook
    try:
        wb = xl.load_workbook(file, data_only=True)
        sheet = wb['new_SFP_rules']
    except:
        brcdapi_log.log('Error opening workbook: ' + 'None' if file is None else file, True)
        return parsed_sfp_sheet

    sl, al = read_sheet(sheet, 'row')

    # We must have at least the 'Group' column
    hdr = al[0]
    for group_col in range(0, len(hdr)):
        if hdr[group_col] == 'Group':
            break
    if hdr[group_col] != 'Group':
        brcdapi_log.log('Could not find column with \'Group\'', True)
        return parsed_sfp_sheet
    max_columns = len(hdr)

    # Parse all the rows
    for row in range(1, len(al)):
        row_data = al[row]
        if row_data[group_col] == '__END__':
            break
        d = dict()
        for i in range(0, max_columns):
            d.update({hdr[i]: row_data[i]})
        parsed_sfp_sheet.append(d)

    return parsed_sfp_sheet


""" _switch_find_d is used in _parse_switch_sheet() to determine what should be parsed out of the spreadsheet and how it
should be interpreted. The key is the value in the cell in the "Area" column. The value is a dict as follows:
    +-------+-------------------------------------------------------------------------------------------------------+
    | key   | Description                                                                                           |
    +=======+=======================================================================================================+
    | k     | The key used in the data structure returned from _parse_switch_sheet()                                |
    +-------+-------------------------------------------------------------------------------------------------------+
    | d     | The default value to assign in the event the parameter is missing from the spreadsheet                |
    +-------+-------------------------------------------------------------------------------------------------------+
    | r     | If True, a value for the paramter is required                                                         |
    +-------+-------------------------------------------------------------------------------------------------------+
    | h     | If True, treat the value from the spreasheet as a hex number and convert to a decimal int.            |
    +-------+-------------------------------------------------------------------------------------------------------+
    | i     | Convert the value from the spreadsheet to an int                                                      |
    +-------+-------------------------------------------------------------------------------------------------------+
    | yn    | Convert "Yes" to True and "No" to False                                                               |
    +-------+-------------------------------------------------------------------------------------------------------+
"""
_switch_find_d = {  # Key is the 'Area' column. Value dict is: k=Key for return data structure, d=default value,
    # r=required, h=True if value is hex and should be conerted to the decimal int equivalent, yn=Convert Yes/No to
    # True/False. This table is used in _parse_switch_sheet()
    'Fabric ID (FID)': dict(k='fid', d=None, r=True, h=False, yn=False),
    'Fabric Name': dict(k='fab_name', d=None, r=False, i=False, h=False, yn=False),
    'Switch Name': dict(k='switch_name', d=None, r=False, i=False, h=False, yn=False),
    'Domain ID (DID)': dict(k='did', d=None, r=True, h=True, yn=False),
    'Insistent DID': dict(k='idid', d=True, r=False, h=False, yn=True),
    'Allow XISL': dict(k='xisl', d=False, r=False, i=False, h=False, yn=True),
    'Enable Switch': dict(k='enable_switch', d=False, r=False, i=False, h=False, yn=True),
    'Enable Ports': dict(k='enable_ports', d=False, r=False, i=False, h=False, yn=True),
    'Login Banner': dict(k='banner', d=None, r=False, i=False, h=False, yn=False),
    'Switch Type': dict(k='switch_type', d=None, r=False, i=False, h=False, yn=False),
    'Duplicate WWN': dict(k='dup_wwn', d='First', r=False, i=True, h=False, yn=False),
    'Bind': dict(k='bind', d=None, r=False, i=False, h=False, yn=True),
}


def _parse_switch_sheet(sheet):
    """Parses a "Switch_x" workhseet from X6_X7-8_Slot_48_FICON_Link_Address_Planning.xlsx as this dictionary:

    +---------------+-----------+-----------------------------------------------------------------------------------+
    | key           | type      | Description                                                                       |
    +===============+===========+===================================================================================+
    | banner        | None, str | Login banner. Not set if None.                                                    |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | bind          | bool      | If set, find the addresses                                                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | fab_name      | None, str | Fabric name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | fid           | int       | Fabric ID as a decimal.                                                           |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | did           | int       | Domain ID. Although read from the workbook as a str in Hex, it is returned as a   |
    |               |           | decimal int                                                                       |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | dup_wwn       | str       | Duplicate WWN handling: 'First', 'Second', 'Second FDISC'                         |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_ports  | bool      | If True, enable the ports after configuration is complete.                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_swtich | bool      | If True, enable the switch after configuruation is complete.                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | ports         | dict      | Key is the port number and value is the link address                              |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_flag   | bool      | When True, a corresponding switch sheet was not found. This happens when a FID on |
    |               |           | on a "Slot x" sheet without a sheet  to match.                                    |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_name   | None, str | Switch name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_type   | str       | default', 'ficon', 'base', or 'open'                                              |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | xisl          | bool      | If True, base switch usage is allowed.                                            |
    +---------------+-----------+-----------------------------------------------------------------------------------+

    :param sheet: openpyxl worksheet
    :type sheet: str
    :return: Dictionary for switch. None if an error was encountered.
    :rtype: dict, None
    """
    global _switch_find_d

    sl, al = read_sheet(sheet, 'row')

    # Find the 'Area' and 'Parameter' columns
    find_l = ('Area', 'Parameter')
    col_d = dict()
    hdr = al[0]
    for buf in find_l:
        found = False
        for col in range(0, len(hdr)):
            if hdr[col] == buf:
                col_d.update({buf: col})
                found = True
                break
        if not found:
            brcdapi_log.log('Sheet ' + sheet.title + ' missing column ' + buf, True)
            return None

    # Add and validate all the data from the worksheet to return dictionary
    rd = dict(switch_flag=True, ports=dict())
    ml = list()
    for k, d in _switch_find_d.items():
        found = False
        for row in range(1, len(al)):
            if k == al[row][col_d['Area']]:
                v = d['d'] if al[row][col_d['Parameter']] is None else al[row][col_d['Parameter']]
                if v is None and d['r']:
                    ml.append('Missing required value for ' + k)
                else:
                    if d['h']:
                        try:
                            v = int(v, 16)
                        except:
                            ml.append('Value for ' + k + ', ' + str(v) + ', is not a valid hex number.')
                    if d['yn']:
                        v = True if v.lower() == 'yes' else False
                    found = True
                break
        if not found:
            v = d['d']
        if d['r'] and v is None:
            ml.append('Missing required value for ' + k)
        rd.update({d['k']: v})

    # Return the switch dict or None if there was an error
    if len(ml) > 0:
        brcdapi_log.log(ml, True)
        return None
    return rd


"""
+-------+-----------------------------------------------------------------------------------------------+
| k     | Key used in the dictionaries returned from _parse_slot_sheet()                                |
+-------+-----------------------------------------------------------------------------------------------+
| h     | If True, treat the cell value as a hex number and convert to a decimal int                    |
+-------+-----------------------------------------------------------------------------------------------+
| s     | If True, convert the cell value to a str                                                      |
+-------+-----------------------------------------------------------------------------------------------+
| slot  | If True, prepend the slot number an '/' to the value. Used to convert ports to s/p notation   |
+-------+-----------------------------------------------------------------------------------------------+
| p     | When the length of the cell value is less than that specified by p, 0s are prepended to make  |
|       | the value this length. Used for creating FC addresses.                                        | 
+-------+-----------------------------------------------------------------------------------------------+
"""
_slot_d_find = {  # See table above
    'Port': dict(k='port', h=False, s=True, slot=True, p=0),
    'DID (Hex)': dict(k='did', h=True, s=True, slot=False, p=0),
    'Port Addr (Hex)': dict(k='port_addr', h=False, s=True, slot=False, p=2),
    'Link Addr': dict(k='link_addr', h=False, s=True, slot=False, p=4),
    'FID': dict(k='fid', h=False, s=False, slot=False, p=0),
    'Attached Device': dict(k='desc', h=False, s=True, slot=False, p=0),
    'ICL Description': dict(k='desc', h=False, s=True, slot=False, p=0),
    'Low Qos VC': dict(k='low_vc', h=False, s=False, slot=False, p=0),
    'Med Qos VC': dict(k='med_vc', h=False, s=False, slot=False, p=0),
    'High Qos VC': dict(k='high_vc', h=False, s=False, slot=False, p=0),
}


def _parse_slot_sheet(sheet):
    """Parses a "Slot x" workhseet from X6_X7-8_Slot_48_FICON_Link_Address_Planning.xlsx as a dictionary. The key is the
    port number in s/p notation. The value for each port dictionary is as follows:

    +---------------+-----------+-----------------------------------------------------------------------------------+
    | key           | type      | Description                                                                       |
    +===============+===========+===================================================================================+
    | fid           | int       | Fabric ID as a decimal.                                                           |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | did           | int       | Domain ID. Although read from the workbook as a str in Hex, it is returned as a   |
    |               |           | decimal int                                                                       |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | port_addr     | str       | Port address in hex as read from the sheet (no leading 0x). Padded to 2 places.   |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | link_addr     | str       | Link address in hex as read from the sheet (no leading 0x)                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | desc          | str       | Attached Device or ICL Description                                                |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | low_vc        | int       | Low Qos VC                                                                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | med_vc        | int       | Medium Qos VC                                                                     |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | high_vc       | int       | High Qos VC                                                                       |
    +---------------+-----------+-----------------------------------------------------------------------------------+

    :param sheet: openpyxl worksheet
    :type sheet: str
    :return: Dictionary for switch. None if an error was encountered.
    :rtype: dict, None
    """
    global _slot_d_find

    rd = dict()  # The return dictionary
    sl, al = read_sheet(sheet, 'row')

    # Find the slot number
    for buf in al[0]:
        if buf is not None and 'slot' in buf.lower():
            slot = buf.split(' ')[1] + '/'
            break

    # Find the column headers
    col_d = [dict(), dict()]
    col_start = [0, 0]
    hdr = al[1]
    port_found = False
    max_col = 0
    for i in range(0, 2):
        col_start[i] = max_col
        for k in _slot_d_find.keys():
            for col in range(col_start[i], len(hdr)):
                if hdr[col] == k:
                    col_d[i].update({_slot_d_find[k]['k']: col})
                    max_col = max(max_col, col+1)
                    break

    # Add the data from the worksheet
    rl = list()
    ml = list()
    for row in range(3, len(al)):
        if al[row][col_d[0]['port']] is None:
            break
        for i in range(0, 2):
            if len(col_d[i]) == 0:
                break

            # Build the port dict and add to the return dict
            pd = dict()
            for k, d in _slot_d_find.items():
                r_key = _slot_d_find[k]['k']
                if r_key in col_d[i]:
                    v = str(al[row][col_d[i][r_key]]) if d['s'] else al[row][col_d[i][r_key]]
                    if d['h']:
                        try:
                            v = int(v, 16)
                        except:
                            ml.append('Value for ' + k + ', ' + str(v) + ', is not a valid hex number.')
                    if isinstance(v, str):
                        while len(v) < d['p']:
                            v = '0' + v
                    v = slot + v if d['slot'] else v
                    pd.update({r_key: v})
            rd.update({pd['port']: pd})

    # Return the slot dict or None if there was an error
    if len(ml) > 0:
        brcdapi_log.log(ml, True)
        return None
    return rd


def parse_switch_file(file):
    """Parses Excel switch configuration Workbook. See X6_X7-8_Slot_48_FICON_Link_Address_Planning.xlsx

    :param file: Path and name of Excel Workbook with switch configuration definitions
    :type file: str
    :return: Dictionary of logical switches (dict as described below). Key is the FID as an int.
    :rtype: dict

    +---------------+-----------+-----------------------------------------------------------------------------------+
    | key           | type      | Description                                                                       |
    +===============+===========+===================================================================================+
    | switch_flag   | bool      | When True, a corresponding switch sheet was found. When False, the FID was found  |
    |               |           | on a "Slot x" sheet without a matchin sheet for the switch.                       |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | fab_name      | None, str | Fabric name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_name   | None, str | Switch name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | Domain ID     | int       | Although read from the workbook as a str in Hex, it is returned as a decimal int  |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | xisl          | bool      | If True, base switch usage is allowed.                                            |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_swtich | bool      | If True, enable the switch after configuruation is complete.                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_ports  | bool      | If True, enable the ports after configuration is complete.                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | banner        | None, str | Login banner. Not set if None.                                                    |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | ports         | dict      | Key is the port number and value is a dictionary as follows:                      |
    |               |           |  Key          Type    Value                                                       |
    |               |           |  did          int     The hexidecimal DID converted to decimal.                   |
    |               |           |  port_addr    str     The hexidecimal port address (middle byte of the FC address)|
    |               |           |  link_addr    str     FICON link address in hex                                   |
    |               |           |  fid          int     Fabric ID                                                   |
    |               |           |  ad           str,None    Attached device description. None if left blank.        |
    |               |           |  low_vc       int     VC for QOSL zone                                            |
    |               |           |  med_vc       int     VC for QOSM zone                                            |
    |               |           |  high_vc      int     VC for QOSH zone                                            |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | sheet_name    | str       | Name of sheet in Workbook.                                                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    """
    rd = dict()  # Return dict

    # Load the workbook
    try:
        wb = xl.load_workbook(file, data_only=True)
    except:
        brcdapi_log.log('Error opening workbook: ' + 'None' if file is None else file, True)
        return rd

    # Sort out the "Sheet_x" and "Slot x" worksheets
    switch_d = dict()
    port_d = dict()
    for sheet in wb.worksheets:
        title = sheet.title
        if len(title) >= len('Switch') and title[0:len('Switch')] == 'Switch':
            d = _parse_switch_sheet(sheet)
            d.update(dict(sheet_name=title))
            fid = d.get('fid')
            if fid is not None:
                if fid in rd:
                    buf = 'Duplicate FID, ' + str(fid) + '. Appears in ' + title + ' and ' + rd[fid]['sheet_name']
                    brcdapi_log.log(buf, True)
                else:
                    rd.update({d['fid']: d})
        elif len(title) >= len('Slot x') and title[0:len('Slot ')] == 'Slot ':
            port_d.update(_parse_slot_sheet(sheet))

    # Build the return dictionary
    for k, port in port_d.items():
        fid = port.get('fid')
        switch_d = dict(switch_flag=False, fid=fid, ports=dict()) if rd.get(fid) is None else rd.get(fid)
        switch_d['ports'].update({k: port})

    return rd
