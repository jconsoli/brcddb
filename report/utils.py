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
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '29 Sep 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.2'

import openpyxl as xl
import openpyxl.utils.cell as xl_util
import re
import brcdapi.log as brcdapi_log
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.util.util as brcddb_util
import brcddb.report.fonts as report_fonts


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
    a_list = []
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
                display = []
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
                        if isinstance(obj.get('merge'), int) and obj.get('merge') > 1:
                            sheet.merge_cells(start_row=row, start_column=col, end_row=row,
                                              end_column=(col + obj.get('merge') - 1))
                            col += obj.get('merge')
                        else:
                            brcdapi_log.exception('Merge must be an integer > 1. Type: ' + str(len(obj.get('merge'))),
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
    """Converts a cell reference to a column number.

    :param cell: Excel spreadsheet cell reference. Example: 'AR20' or just 'AR'
    :type cell: str
    :return: Column number
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
    if col is None:
        col_list = []
        for i in range(1, sheet.max_column):
            col_list.append(xl_util.get_column_letter(i))
    else:
        col_list = brcddb_util.convert_to_list(col)

    class Found(Exception):
        pass
    ret = []
    try:
        for c in col_list:
            for r in brcddb_util.convert_to_list(row):
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
    new_sfp_rules = []  # The list of rule dictionaries that will be returned

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
    parsed_sfp_sheet = []  # The list of rule dictionaries that will be returned

    # Load the workbook
    try:
        wb = xl.load_workbook(file, data_only=True)
        sheet = wb['new_SFP_rules']
    except:
        brcdapi_log.log('Error opening workbook: ' + 'None' if file is None else file, True)
        return parsed_sfp_sheet

    # We must have at least the 'Group' column
    cell = cell_match_val(sheet, 'Group', None, 1)
    if cell is None:
        brcdapi_log.log('Could not find column with \'Group\'', True)
        return parsed_sfp_sheet
    group_col = xl_util.get_column_letter(col_to_num(cell))

    # Find all the columns
    sheet = wb['new_SFP_rules']
    max_columns = sheet.max_column
    col_hdr = [None]
    col_letter = [None]
    for i in range(1, max_columns):
        col_letter.append(xl_util.get_column_letter(i))
        col_hdr.append(sheet[col_letter[i] + str(1)].value)

    # Now parse all the rows
    row = 2
    group = sheet[group_col + str(row)].value
    while group != '__END__':
        d = {}
        for i in range(1, max_columns):
            d.update({col_hdr[i]: sheet[col_letter[i] + str(row)].value})
        parsed_sfp_sheet.append(d)
        row += 1
        group = sheet[group_col + str(row)].value

    return parsed_sfp_sheet
