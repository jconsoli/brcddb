# Copyright 2020, 2021, 2022, 2023 Jack Consoli.  All rights reserved.
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

:mod:`report.utils` - Common methods used for reading and generating Excel reports.

Public Methods & Data::

    +-------------------------------+-------------------------------------------------------------------------------+
    | Method                        | Description                                                                   |
    +===============================+===============================================================================+
    | fabric_name_case              | Return the fabric name. Typically used in case statments for page reports in  |
    |                               | brcddb.report.                                                                |
    +-------------------------------+-------------------------------------------------------------------------------+
    | fabric_name_or_wwn_case       | Return the fabric name with (wwn). Typically used in case statments for page  |
    |                               | reports in brcddb.report.*"                                                   |
    +-------------------------------+-------------------------------------------------------------------------------+
    | fabric_wwn_case               | Return the fabric WWN. Typically used in case statments for page reports in   |
    |                               | brcddb.report.                                                                |
    +-------------------------------+-------------------------------------------------------------------------------+
    | font_type                     | Determines the display font based on alerts.                                  |
    +-------------------------------+-------------------------------------------------------------------------------+
    | font_type_for_key             | Determines the display font based on alerts associated with an object.        |
    +-------------------------------+-------------------------------------------------------------------------------+
    | comments_for_alerts           | Converts alerts associated with an object to a human readable string.         |
    |                               | Multiple comments separated with /n                                           |
    +-------------------------------+-------------------------------------------------------------------------------+
    | combined_login_alert_objects  | Combines login alert objects with FDMI HBA and FDMI port alerts objects       |
    +-------------------------------+-------------------------------------------------------------------------------+
    | combined_login_alerts         | Converts alerts associated with a login object and the login and FDMI objects |
    |                               | for lwwn to a human readable string                                           |
    +-------------------------------+-------------------------------------------------------------------------------+
    | combined_alert_objects        | Combines alerts associated with a port object and the login and FDMI objects  |
    |                               | for wwn.                                                                      |
    +-------------------------------+-------------------------------------------------------------------------------+
    | combined_alerts               | Converts alerts associated with a port object and the login and FDMI objects  |
    |                               | for lwwn to a human readable string.                                          |
    +-------------------------------+-------------------------------------------------------------------------------+
    | title_page                    | Creates a title page for the Excel report.                                    |
    +-------------------------------+-------------------------------------------------------------------------------+
    | get_next_switch_d             | Finds the first match in an sl list returned from excel_util.read_sheet() and |
    |                               | returns the next entry                                                        |
    +-------------------------------+-------------------------------------------------------------------------------+
    | parse_sfp_file                | Parses Excel file with the new SFP rules. See sfp_rules_rx.xlsx               |
    +-------------------------------+-------------------------------------------------------------------------------+
    | parse_switch_file             | Parses Excel switch configuration Workbook.                                   |
    +-------------------------------+-------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-8   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 14 May 2021   | Added parse_parameters(), replaced wb.get_sheet_by_name() with wb[sheet_name]     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 14 Nov 2021   | No functional changes. Defaulted sheet index to 0                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 31 Dec 2021   | Fixed error message when file not found in parse_switch_file()                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 28 Apr 2022   | Moved generic Excel utilities to brcdapi.excel_util                               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.3     | 22 Jun 2022   | Added _parse_chassis_sheet(), additional parameters from the switch configuration |
    |           |               | workbook, fixed font reference in title_page().                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.4     | 01 Jan 2023   | Added the port index, routing poilcy, and CUP enable. Modified                    |
    |           |               | parse_switch_file() to return an error list rather than print the errors to the   |
    |           |               | log.                                                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.5     | 11 Feb 2023   | Added ability to handle 'open -n' and 'ficon -n' for port names. Added check for  |
    |           |               | FICON ports with addresses > 0xFD                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '11 Feb 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.5'

import openpyxl as xl
import openpyxl.utils.cell as xl_util
import fnmatch
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.excel_util as excel_util
import brcdapi.excel_fonts as excel_fonts
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.util.search as brcddb_search

_MAX_FICON_PORT_NAME = 24
_conv_routing_policy_d = dict(EBR='exchange-based', DBR='device-based')

#######################################################################
#
# Common case statements in port_page(), switch_page(), chassis_page()
#
#######################################################################


def fabric_name_case(obj, k=None, wwn=None):
    """Return the fabric name. Typically used in case statments for page reports in brcddb.report.*

    :param obj: brcddb object that contains a fabric object
    :type obj: brcddb.classes.fabric.FabricObj, brcddb.classes.fabric.SwitchObj, brcddb.classes.fabric.PortObj,
               brcddb.classes.fabric.LoginObj
    :param k: Not used
    :type k: str
    :param wwn: Not used
    :type wwn: str
    """
    return brcddb_fabric.best_fab_name(obj.r_fabric_obj(), False)


def fabric_name_or_wwn_case(obj, k=None, wwn=None):
    """Return the fabric name with (wwn). Typically used in case statments for page reports in brcddb.report.*

    See fabric_name_case() for parameter definitions"""
    return brcddb_fabric.best_fab_name(obj.r_fabric_obj(), True)


def fabric_wwn_case(obj, k=None, wwn=None):
    """Return the fabric WWN. Typically used in case statments for page reports in brcddb.report.*

    See fabric_name_case() for parameter definitions"""
    return obj.r_fabric_key()


def font_type(obj_list):
    """Determines the display font based on alerts.

    :param obj_list: List of brcddb.classes.alert.AlertObj
    :param obj_list: list
    """
    font = excel_fonts.font_type('std')
    for alert_obj in obj_list:
        if alert_obj.is_error():
            return excel_fonts.font_type('error')
        elif alert_obj.is_warn():
            font = excel_fonts.font_type('warn')

    return font


def font_type_for_key(obj, k=None):
    """Determines the display font based on alerts associated with an object.

    :param obj: Any brcddb object
    :param obj: ChassisObj, FabricObj, SwitchObj, PortObj, ZoneObj, ZoneCfgObj, AliasObj
    :param k: Key to associate the alert with
    :type k: str
    """
    font = excel_fonts.font_type('std')
    a_list = obj.r_alert_objects() if k is None else [a_obj for a_obj in obj.r_alert_objects() if a_obj.key() == k]
    for a_obj in a_list:
        if a_obj.is_error():
            return excel_fonts.font_type('error')
        elif a_obj.is_warn():
            font = excel_fonts.font_type('warn')

    return font


def comments_for_alerts(gobj, k=None, wwn=None):
    """Converts alerts associated with an object to a human readable string. Multiple comments separated with /n

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
    a_list = obj.r_alert_objects() if k is None else [a_obj for a_obj in obj.r_alert_objects() if a_obj.key() == k]
    return '\n'.join([a_obja_obj.fmt_msg() for a_obja_obj in a_list])


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


def title_page(wb, tc, sheet_name, sheet_i, sheet_title, content, col_width):
    """Creates a title page for the Excel report.

    content is as defined as noted below. Any unspecified item is ignored which means the default is whatever default is
    configured in Excel.
        content_item = {
            'new_row':  False           # Default is True. Setting this to False is useful when using different cell
                                        # attributes for different columns. Otherwise, all cell attributes are applied
                                        # to all cells.
            'font': 'hdr_1',            # Predefined font type in font_tbl
            'fill': 'light_blue'        # Predefined cell fill type in fill_tbl
            'border': 'thin'            # Predefined border type in border_tbl
            'align': 'wrap'             # Predefined align type in align_tbl
            'merge': 2,                 # Number of columns to merge, starting from current column
            'disp': ('col_1', 'col_2', 'etc')   # Str, list or tuple. Content to add to the worksheet
        }
        Example:
        content = (
            {'font': 'hdr_1', 'merge': 3, 'align': 'wrap_center', 'disp': 'Title Page'},
            {}, # Skip a row
            {'font': 'std', 'align': 'wrap', 'disp': ('col_1', 'col_2', 'col_3') },
        )

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1.
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed. Typically 0. Default is 0
    :type sheet_i: int, None
    :param sheet_title: Title to be displayed in large font, hdr_1, with light blue fill at the top of the sheet
    :type sheet_title: str
    :param content: Caller defined content. List or tuple of dictionaries to add to the title page. See comments above
    :type content: list, tuple
    :param col_width: Column widths of list of column widths to set on sheet
    :type col_width: int, list, tuple
    :rtype: None
    """

    # Set up the sheet
    col = 1
    sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i,
                            title=excel_util.valid_sheet_name.sub('_', sheet_name))
    for i in gen_util.convert_to_list(col_width):
        sheet.column_dimensions[xl_util.get_column_letter(col)].width = i
        col += 1
    max_col = col-1
    row = col = 1
    if isinstance(tc, str):
        excel_util.cell_update(sheet, row, col, 'Contents', link='#' + tc + '!A1', font=excel_fonts.font_type('link'))
        col += 1
    sheet.merge_cells(start_row=row, start_column=col, end_row=row, end_column=max_col)
    excel_util.cell_update(sheet, row, col, sheet_title, font=excel_fonts.font_type('hdr_1'),
                           fill=excel_fonts.fill_type('lightblue'))
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
                                              str(row), echo=True)
                for buf in display:
                    excel_util.cell_update(sheet, row, col, buf,
                                           link=obj.get('hyper'),
                                           font=excel_fonts.font_type(obj.get('font')),
                                           align=excel_fonts.align_type(obj.get('align')),
                                           border=excel_fonts.border_type(obj.get('border')),
                                           fill=excel_fonts.fill_type(obj.get('fill')))
                    if 'merge' in obj:
                        if isinstance(obj.get('merge'), int):
                            if obj.get('merge') > 1:
                                sheet.merge_cells(start_row=row, start_column=col, end_row=row,
                                                  end_column=(col + obj.get('merge') - 1))
                                col += obj.get('merge')
                        else:
                            brcdapi_log.exception('Merge must be an integer. Type: ' + str(type(obj.get('merge'))),
                                                  echo=True)
                            col += 1
                    else:
                        col += 1
                if 'new_row' not in obj or ('new_row' in obj and obj.get('new_row')):
                    row, col = row+1, 1
            else:
                brcdapi_log.exception('Invalid type in content list, ' + str(type(obj)) + ', at row ' + str(row),
                                      echo=True)
    else:
        brcdapi_log.exception('Invalid content type: ' + str(type(content)), echo=True)


def get_next_switch_d(switch_list, val, test_type, ignore_case=False):
    """Finds the first match in an sl list returned from excel_util.read_sheet() and returns the next entry

    :param switch_list: A list of dictionaries as returned from excel_util.read_sheet()
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


def parse_sfp_file(file):
    """Parses Excel file with the new SFP rules. See sfp_rules_rx.xlsx

    :param file: Path and name of Excel Workbook with new SFP rules
    :type file: str
    :return: List of dictionaries. The key for each dictionary is the column header and the value is the cell value
    :rtype: list
    """
    if file is None:
        return list()

    # Load the workbook & contents
    try:
        parsed_sfp_sheet = excel_util.parse_parameters(sheet_name='new_SFP_rules', hdr_row=0, wb_name=file)['content']
    except FileNotFoundError:
        brcdapi_log.log('SFP rules workbook: ' + str(file) + ' not found.', echo=True)
        return list()

    # Get rid of everything past '__END__'
    for i in range(0, len(parsed_sfp_sheet)):
        if parsed_sfp_sheet[i]['Group'] == '__END__':
            break
    return parsed_sfp_sheet[0: i]


def find_headers(hdr_row_l, hdr_l=None, warn=False):
    """Moved to brcdapi.excel_util.find_headers()"""
    return excel_util.find_headers(hdr_row_l, hdr_l=hdr_l, warn=warn)


def _parse_chassis_sheet(sheet_d):
    """Parses the "Chassis" worksheet from a switch configuration workbook into a dictionary. The key is the KPI. The
    value is the content.

    :param sheet_d: Output from excel_util.read_workbook() for the Chassis worksheet
    :type sheet_d: list
    :return error_l: List of error messages. Empty if no error encountered
    :rtype error_l: list
    :return: Dictionary for chassis.
    :rtype: dict
    """
    error_l, rd = list(), dict()
    al = sheet_d['al']
    if len(al) < 2:
        return error_l, rd

    # Find the 'Area' and 'Parameter' columns
    col_d = excel_util.find_headers(al[0], ('Area', 'Parameter'))
    for k, v in col_d.items():
        if v is None:
            error_l.append('Sheet ' + sheet_d['switch_info']['sheet_name'] + ' missing column ' + k)
    if len(error_l) > 0:
        return error_l, None

    # Add all the data to the return dictionary
    area_i, content_d, working_key = col_d['Area'], None, None
    for row in range(1, len(al)):
        new_key, row_l = False, al[row]
        for k in ('running', 'operations'):
            if len(row_l[area_i]) > len(k) and row_l[area_i][0:len(k)] == k:
                new_key, working_key, content_d = True, row_l[area_i], rd.get(working_key)
                if content_d is None:
                    content_d = dict()
                    rd.update({working_key: content_d})
                break
        if new_key:
            continue
        if content_d is None:
            error_l.append('Chassis sheet: Content found before a KPI was defined in row ' + str(row+1))
            continue
        val = row_l[col_d['Parameter']]
        if val is None:
            continue
        content_d.update({row_l[area_i]: val})

    return error_l, rd


# Case methods for _switch_d
def _conv_add(error_l, obj_d, switch_d, val):
    """Used in _switch_d to add a key/value pair to obj_d

    :param error_l: List of error messages to append error messges to
    :type error_l: list
    :param obj_d: Object to update with Rest API key and values
    :type obj_d: dict
    :param switch_d: Dictionary in _switch_d
    :type switch_d: dict
    :param val: Value from the configuration workbook to add to key
    :type val: int, float, str, None
    :rtype: None
    """
    add_val = switch_d['d'] if val is None else val
    if add_val is not None:
        gen_util.add_to_obj(obj_d, switch_d['k'], add_val)


def _conv_port_name(error_l, obj_d, switch_d, val):
    """Used in _switch_d to convert hex to decimal int. See _conv_add for parameter definitions"""
    gen_util.add_to_obj(obj_d, 'switch_info/port_name', val)
    port_name_mode = switch_d['d'] if not isinstance(val, str) else 'off' if val in ('open -n, ficon -n') else val
    try:
        _conv_add(error_l, obj_d, switch_d, port_name_mode)
    except (ValueError, TypeError):
        error_l.append('Value for ' + switch_d['k'] + ', ' + str(val) + ', is not a valid hex number.')


def _conv_hex(error_l, obj_d, switch_d, val):
    """Used in _switch_d to convert hex to decimal int. See _conv_add for parameter definitions"""
    try:
        _conv_add(error_l, obj_d, switch_d, int(val.replace('0x', ''), 16))
    except (ValueError, TypeError):
        error_l.append('Value for ' + switch_d['k'] + ', ' + str(val) + ', is not a valid hex number.')


def _conv_yn_bool(error_l, obj_d, switch_d, val):
    """Used in _switch_d to convert "yes" or "no" to a bool. See _conv_add for parameter definitions"""
    add_val = switch_d['d'] if val is None else val
    if isinstance(add_val, str):
        add_val = True if add_val.lower() == 'yes' else False
    try:
        _conv_add(error_l, obj_d, switch_d, add_val)
    except AttributeError:
        error_l.append('Expected type bool or str for ' + switch_d['k'] + '. Received type ' + str(type(val)))


def _conv_req_int(error_l, obj_d, switch_d, val):
    """Used in _switch_d. An int type val is required. See _conv_add for parameter definitions"""
    add_val = switch_d['d'] if val is None else val
    if isinstance(add_val, int):
        _conv_add(error_l, obj_d, switch_d, add_val)
    else:
        error_l.append('Expected type int for ' + switch_d['k'] + '. Received type ' + str(type(val)))


def _conv_cup(error_l, obj_d, switch_d, val):
    """Enable CUP. See _conv_add for parameter definitions"""
    val_bool = True if isinstance(val, str) and val.lower() == 'yes' else False
    if obj_d['switch_info']['switch_type'] == 'ficon':
        _conv_add(error_l, obj_d, switch_d, val_bool)
        if val_bool:
            gen_util.add_to_obj(obj_d, 'running/brocade-ficon/cup/active-equal-saved-mode', True)
            # At the time this was written, modifying mihpto was not supported in the API. It was GET only.
            # gen_util.add_to_obj(obj_d, 'running/brocade-ficon/cup/mihpto', 180)
    elif val_bool:
        error_l.append('Enable CUP is only supported on "ficon" switch types. Sheet: ' + '')


def _conv_routing_policy(error_l, obj_d, switch_d, val):
    """Used in _switch_d. To enable CUP. See _conv_add for parameter definitions"""
    global _conv_routing_policy_d

    add_val = switch_d['d'] if not isinstance(val, str) else None if val=='default' else _conv_routing_policy_d[val]
    if isinstance(add_val, str):
        _conv_add(error_l, obj_d, switch_d, add_val)


""" _switch_d is used in _parse_switch_sheet() to determine what should be parsed out of the spreadsheet and how it
should be interpreted. The key is the value in the cell in the "Area" column. The value is a dict as follows:
    +-------+-------------------------------------------------------------------------------------------------------+
    | key   | Description                                                                                           |
    +=======+=======================================================================================================+
    | k     | Rest API branch corresponding to "Area" in the switch configuration workbooks. At the time this was   |
    |       | written, only running branches were included. This is because "operations" branches require special   |
    |       | handling. There is also a special key "switch_info". Most of the information in switch_info is what   |
    |       | is passed to the brcdapi.switch.py module which handles "operations" branch and other switch actions  |
    |       | that require special handling.                                                                        | 
    +-------+-------------------------------------------------------------------------------------------------------+
    | d     | The default value to assign in the event the parameter is missing from the spreadsheet                |
    +-------+-------------------------------------------------------------------------------------------------------+
    | c     | Pointer to value conversion action.                                                                   |
    +-------+-------------------------------------------------------------------------------------------------------+
"""
_fc_switch = 'running/brocade-fibrechannel-switch/'
_fc_config = 'running/brocade-fibrechannel-configuration/'
_switch_d = {  # See above for definitions. This table is used in _parse_switch_sheet()
    'Fabric ID (FID)': dict(k='switch_info/fid', d=None, c=_conv_req_int),
    'Fabric Name': dict(k=_fc_switch+'fibrechannel-switch/fabric-user-friendly-name', d=None, c=_conv_add),
    'Switch Name': dict(k=_fc_switch+'fibrechannel-switch/user-friendly-name', d=None, c=_conv_add),
    'Domain ID (DID)': dict(k=_fc_switch+'fibrechannel-switch/domain-id', d=None, c=_conv_hex),
    'Insistent DID': dict(k=_fc_config+'fabric/insistent-domain-id-enabled', d=True, c=_conv_yn_bool),
    'Fabric Principal Enable': dict(k=_fc_config+'fabric/principal-selection-enabled', d=False, c=_conv_yn_bool),
    'Fabric Principal Priority': dict(k=_fc_config+'fabric/principal-priority', d=None, c=_conv_add),
    'Allow XISL': dict(k=_fc_config+'switch-configuration/xisl-enabled', d=False, c=_conv_yn_bool),
    'Enable Switch': dict(k='switch_info/enable_switch', d=False, c=_conv_yn_bool),
    'Enable Ports': dict(k='switch_info/enable_ports', d=False, c=_conv_yn_bool),
    'Login Banner': dict(k=_fc_switch+'fibrechannel-switch/banner', d=None, c=_conv_add),
    'Switch Type': dict(k='switch_info/switch_type', d=None, c=_conv_add),
    'Duplicate WWN': dict(k=_fc_config+'f-port-login-settings/enforce-login', d=0, c=_conv_req_int),
    'Bind': dict(k='switch_info/bind', d=False, c=_conv_yn_bool),
    'Routing Policy': dict(k=_fc_switch+'fibrechannel-switch/advanced-performance-tuning-policy', d=None,
                           c=_conv_routing_policy),
    'Port Name': dict(k=_fc_config+'port-configuration/portname-mode', d=None, c=_conv_port_name),
    'Port Name Format': dict(k=_fc_config+'port-configuration/dynamic-portname-format', d='S.T.I.A', c=_conv_add),
    'Enable CUP': dict(k='running/brocade-ficon/cup/fmsmode-enabled', d=False, c=_conv_cup),
}


def _parse_switch_sheet(sheet_d):
    """Parses a "Switch_x" worksheet from one of the witch configuration worksheets and returns a dictionary of Rest API
    branch and leaf names. The values are what to send to the switch. Also contains a dictionary whose key is

    +---------------+-------+-------------------------------------------------------------------------------+
    | Key           | type  | Value Description                                                             |
    +===============+=======+===============================================================================+
    | switch_info   | dict  | See switch_info below                                                         |
    +---------------+-------+-------------------------------------------------------------------------------+
    | err_msgs      | list  | Although no longer used by this module, the list is created and left empty    |
    |               |       | because other modules may use it and expect this key to be present.           |
    +---------------+-------+-------------------------------------------------------------------------------+
    | port_d        | dict  | Key is port in s/p notation. Value is a dict as read from the Slot x sheets   |
    +---------------+-------+-------------------------------------------------------------------------------+
    | running       | dict  | Branch and leaves in Rest API format for the running branch                   |
    +---------------+-------+-------------------------------------------------------------------------------+
    | operations    | dict  | Branch and leaves in Rest API format for the operations branch. As of         |
    |               |       | 29 Dec 2022 there was nothing to put in here so the branch was not present.   |
    +---------------+-------+-------------------------------------------------------------------------------+

    "switch_info" defined as follows:

    +---------------+-----------+-----------------------------------------------------------------------------------+
    | key           | type      | Description                                                                       |
    +===============+===========+===================================================================================+
    | bind          | bool      | If True, bind the port addresses.                                                 |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_ports  | bool      | If True, enable the ports when done.                                              |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_switch | bool      | If True, enable the switch when done.                                             |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | fid           | int       | Fabric ID                                                                         |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | sheet_name    | str       | Sheet name from switch configuration workbook                                     |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_type   | str       | base, ficon, or open                                                              |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | port_name     | str       | Port Name from switch configuration workbook                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+

    :param sheet_d: Output from excel_util.read_workbook() for the Chassis worksheet
    :type sheet_d: list
    :return error_l: List of error messages. Empty if no error encountered
    :rtype error_l: list
    :return: Dictionary for switch. None if an error was encountered.
    :rtype: dict, None
    """
    global _switch_d

    # Find the 'Area' and 'Parameter' columns
    error_l, rd, al = list(), dict(switch_info=dict(), port_d=dict(), err_msgs=list()), sheet_d['al']
    col_d = excel_util.find_headers(al[0], ('Area', 'Parameter'))
    for k, v in col_d.items():
        if v is None:
            error_l.append('Sheet ' + sheet_d['switch_info']['sheet_name'] + ' missing column ' + k)
    if len(error_l) > 0:
        brcdapi_log.log(error_l, echo=True)
        return None

    # Add and validate all the data from the worksheet and add it to the return dictionary, rd
    for row_l in al[1:]:
        switch_d = _switch_d.get(row_l[col_d['Area']])
        if isinstance(switch_d, dict):  # error_l, k, val, def_val
            switch_d['c'](error_l, rd, switch_d, row_l[col_d['Parameter']])
        else:
            error_l.append('Invalid key "' + row_l[col_d['Area']] + '" sheet: ' + sheet_d['switch_info']['sheet_name'])

    # If it's a ficon switch, in order delivery and DLS needs to be set
    if rd['switch_info']['switch_type'] == 'ficon':
        gen_util.add_to_obj(rd, _fc_switch+'dynamic-load-sharing', 'two-hop-lossless-dls')

    return error_l, rd


"""
+-------+-----------------------------------------------------------------------------------------------+
| k     | Key used in the dictionaries returned from _parse_slot_sheet(). IDK why I didn't just use the |
|       | same key as is used in the API. That would have saved the trouble of needing a look up table, |
|       | _switch_d_to_api, in switch_config.py but I'm not changing working code.                      |
+-------+-----------------------------------------------------------------------------------------------+
| h     | If True, treat the cell value as a hex number and convert to a decimal int                    |
+-------+-----------------------------------------------------------------------------------------------+
| i     | If True, convert the cell value to an int.                                                    |
+-------+-----------------------------------------------------------------------------------------------+
| s     | If True, convert the cell value to a str                                                      |
+-------+-----------------------------------------------------------------------------------------------+
| slot  | If True, prepend the slot number + '/' to the value. Used to convert ports to s/p notation    |
+-------+-----------------------------------------------------------------------------------------------+
| p     | When the length of the cell value is less than that specified by p, 0s are prepended to make  |
|       | the value this length. Used for creating FC addresses.                                        | 
+-------+-----------------------------------------------------------------------------------------------+
| pn    | When True, check the port naming convention and adjust the port name accordingly.             |
+-------+-----------------------------------------------------------------------------------------------+
"""
_slot_d_find = {  # See table above
    'Port': dict(k='port', h=False, i=False, s=True, slot=True, p=0, pn=False),
    'DID (Hex)': dict(k='did', h=True, i=False, s=True, slot=False, p=0, pn=False),
    'Port Addr (Hex)': dict(k='port_addr', h=False, i=False, s=True, slot=False, p=2, pn=False),
    'Index': dict(k='index', h=False, i=True, s=True, slot=False, p=0, pn=False),
    'Link Addr': dict(k='link_addr', h=False, i=False, s=True, slot=False, p=4, pn=False),
    'FID': dict(k='fid', h=False, i=False, s=False, slot=False, p=0, pn=False),
    'Attached Device': dict(k='desc', h=False, i=False, s=False, slot=False, p=0, pn=False),
    'ICL Description': dict(k='desc', h=False, i=False, s=False, slot=False, p=0, pn=False),
    'Port Name': dict(k='port_name', h=False, i=False, s=False, slot=False, p=0, pn=True),
    'Low Qos VC': dict(k='low_vc', h=False, i=False, s=False, slot=False, p=0, pn=False),
    'Med Qos VC': dict(k='med_vc', h=False, i=False, s=False, slot=False, p=0, pn=False),
    'High Qos VC': dict(k='high_vc', h=False, i=False, s=False, slot=False, p=0, pn=False),
}


def _parse_slot_sheet(sheet_d, port_name_d):
    """Parses a "Slot x" worksheet from a configuration workbook into a dictionary. The key is the port number in s/p
    notation. The value for each port dictionary is as follows:

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
    | index         | int       | Port index                                                                        |
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

    :param sheet_d: Output from excel_util.read_workbook() for the Chassis worksheet
    :type sheet_d: list
    :param port_name_d: Key is the FID as an int. Value is the port naming convention
    :type port_name_d: dict()
    :return error_l: List of error messages. Empty if no error encountered
    :rtype error_l: list
    :return: Dictionary for switch. None if an error was encountered.
    :rtype: dict, None
    """
    global _slot_d_find, _MAX_FICON_PORT_NAME

    error_l, rd, al = list(), dict(), sheet_d['al']

    # Find the slot number
    for buf in al[0]:
        if buf is not None and 'slot' in buf.lower():
            slot = buf.split(' ')[1] + '/'
            break

    # Find the column headers
    i, hdr_l, col_d_l = 0, al[1], [dict(), dict()]
    for col in range(0, len(hdr_l)):
        try:
            r_key = _slot_d_find[hdr_l[col]]['k']
            if r_key in col_d_l[i]:
                i += 1  # A repeat means we're starting the second column of ports
                if i > len(col_d_l):
                    error_l.append('Invalid column header, "' + buf + '", on sheet ' + sheet_d['name'])
                    break
            col_d_l[i].update({r_key: col})
        except KeyError:
            pass  # Other columns for documentation purposes may be present so just skip them

    # Add the data from the worksheet
    for row in range(3, len(al)):

        if al[row][col_d_l[0]['port']] is None:
            break  # If the port is None, we reached the end of the workbook

        for i in range(0, 2):  # Director class products have 2 columns, each with the same headers
            if len(col_d_l[i]) == 0:
                break

            # Build the port dict and add to the return dict
            pd = dict()
            for k, d in _slot_d_find.items():
                r_key = _slot_d_find[k]['k']
                if r_key in col_d_l[i]:
                    v = str(al[row][col_d_l[i][r_key]]) if d['s'] else al[row][col_d_l[i][r_key]]
                    if d['h']:
                        try:
                            v = int(v, 16)
                        except ValueError:
                            error_l.append('Value for ' + k + ', ' + str(v) + ', is not a valid hex number.')
                    if d['i']:
                        try:
                            v = int(v)
                        except ValueError:
                            error_l.append('Value for ' + k + ', ' + str(v) + ', is not a number in ' +
                                           sheet_d['switch_info']['sheet_name'])
                    if d['pn']:
                        try:
                            port_name = port_name_d[pd['fid']]
                            if port_name in ('open -n', 'ficon -n'):
                                if isinstance(v, str):
                                    if port_name == 'ficon -n' and len(v) > _MAX_FICON_PORT_NAME:
                                        buf = 'The port name, ' + v + ', for port ' + str(pd.get('port')) + ' is ' + \
                                              str(len(v)) + '. The maximum supported FICON Port name length is ' + \
                                              str(_MAX_FICON_PORT_NAME)
                                        error_l.append(buf)
                                        v = v[0: _MAX_FICON_PORT_NAME]
                                else:
                                    v = ''
                        except KeyError:
                            pass  # We're not configuring this FID

                    if isinstance(v, str):
                        while len(v) < d['p']:
                            v = '0' + v
                    v = slot + v if d['slot'] else v
                    pd.update({r_key: v})
            rd.update({pd['port']: pd})

    # Return the slot dict or None if there was an error
    return error_l, rd


def parse_switch_file(file):
    """Parses Excel switch configuration Workbook.

    :param file: Path and name of Excel Workbook with switch configuration definitions
    :type file: str
    :return error_l: List of errors. Empty list if no errors found
    :rtype error_l: list
    :return chassis_d: Dictionary of chassis parameters. None if error reding workbook
    :rtype chassis_d: dict, None
    :return switch_l: List of logical switch dictionaries as described below.
    :rtype switch_l: list

    Note: This started as as something very different. If I had to do it over again, I would have used the FOS API
    mnemonics for these values.

    +---------------+-----------+-----------------------------------------------------------------------------------+
    | key           | type      | Description                                                                       |
    +===============+===========+===================================================================================+
    | banner        | None, str | Login banner. Not set if None.                                                    |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | bind          | bool      | If True, bind the addresses to the ports.                                         |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | did           | int       | Although read from the workbook as a str in Hex, it is returned as a decimal int  |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | dup_wwn       | int       | 0 - First login takes precedence.                                                 |
    |               |           | 1 - Second FLOGI and FDISC takes precedence.                                      |
    |               |           | 2 - First FLOGI takes precedence. Second FDISC takes precedence                   |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_ports  | bool      | If True, enable the ports after configuration is complete.                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | enable_switch | bool      | If True, enable the switch after configuration is complete.                       |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | fab_name      | None, str | Fabric name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | port_name     | None, str | User friendly port name                                                           |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | ports         | dict      | Key is the port number and value is a dictionary as follows:                      |
    |               |           |  Key          Type    Value                                                       |
    |               |           |  did          int     The hexadecimal DID converted to decimal.                   |
    |               |           |  port_addr    str     The hexadecimal port address (middle byte of the FC address)|
    |               |           |  index        int     The port index                                              |
    |               |           |  link_addr    str     FICON link address in hex                                   |
    |               |           |  fid          int     Fabric ID                                                   |
    |               |           |  ad           str,None    Attached device description. None if left blank.        |
    |               |           |  low_vc       int     VC for QOSL zone                                            |
    |               |           |  med_vc       int     VC for QOSM zone                                            |
    |               |           |  high_vc      int     VC for QOSH zone                                            |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | sheet_name    | str       | Name of sheet in Workbook.                                                        |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | switch_name   | None, str | Switch name. Not set if None                                                      |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    | xisl          | bool      | If True, base switch usage is allowed.                                            |
    +---------------+-----------+-----------------------------------------------------------------------------------+
    """
    chassis_d, port_d, error_l, port_name_d, rd = None, dict(), list(), None, dict()

    # Load the workbook
    skip_l = ('About', 'Summary', 'Sheet', 'Instructions', 'CLI_Bind', 'lists', 'VC')
    try:
        sheet_l = excel_util.read_workbook(file, dm=3, skip_sheets=skip_l)
    except FileNotFoundError:
        error_l.append('Workbook ' + str(file) + ' not found')
        return error_l, chassis_d, list()

    # Parse the "Chassis", "Sheet_x", and "Slot x" worksheets
    for sheet_d in sheet_l:
        title = sheet_d['sheet']
        if fnmatch.fnmatch(title, 'Chassis*'):
            ml, chassis_d = _parse_chassis_sheet(sheet_d)
            error_l.extend(ml)
        elif fnmatch.fnmatch(title, 'Switch*'):
            ml, d = _parse_switch_sheet(sheet_d)
            error_l.extend(ml)
            gen_util.add_to_obj(d, 'switch_info/sheet_name', title)
            fid = d['switch_info']['fid']
            if fid in rd:
                error_l.append('Duplicate FID, ' + str(fid) + '. Appears in ' + title + ' and ' +
                               rd[fid]['switch_info']['sheet_name'])
            else:
                rd.update({fid: d})
        elif fnmatch.fnmatch(title, 'Slot ?*'):
            if not isinstance(port_name_d, dict):
                # This could have been more elegant. I forgot that some port naming modes want all ports not explicitly
                # named to be set to an empty string. Furthermore, ficon port names need to be truncated to a maximum of
                # 24 characters so I jammed this in and made a hack in _parse_slot_sheet() to set the names correctly.
                port_name_d = dict()
                for fid, temp_switch_d in rd.items():
                    port_name_d.update({fid: temp_switch_d['switch_info']['port_name']})
            # if not isinstance(port_name_d, port_name_d):
            ml, d = _parse_slot_sheet(sheet_d, port_name_d)
            error_l.extend(ml)
            port_d.update(d)

    # Add all the ports to the the switch in the return dictionary, rd. I did it this way in case someone rearranged the
    # sheets such that a "Slot x" worksheet came before the corresponding "Switch x" worksheet.
    for k, d in port_d.items():
        switch_d = rd.get(d['fid'])
        if isinstance(switch_d, dict):
            if switch_d['switch_info']['switch_type'] == 'ficon' and int(d['port_addr'], 16) > 253:
                ml = ['Skipping ' + 'FID: ' + str(d['fid']) + ', Port: ' + d['port'] + ' Address: ' + d['port_addr'],
                      'Addresses greater than 0xFD are not supported in a ficon switch.']
                brcdapi_log.log(ml, echo=True)
                continue
            switch_d['port_d'].update({k: d})

    return error_l, chassis_d, [switch_d for switch_d in rd.values()]

###################################################################
#
#                    Depracated
#
###################################################################

def parse_parameters(in_wb=None, sheet_name='parameters', hdr_row=0, wb_name=None):
    return excel_util.parse_parameters(in_wb, sheet_name, hdr_row, wb_name)


def new_report():
    return excel_util.new_report()


def save_report(wb, file_name='Report.xlsx'):
    return excel_util.save_report(wb, file_name)


def col_to_num(cell):
    return excel_util.col_to_num(cell)


def cell_match_val(sheet, val, col=None, row=None, num=1):
    return excel_util.cell_match_val(sheet, val, col, row, num)


def datetime(v, granularity):
    return excel_util.datetime(v, granularity)


def read_sheet(sheet, order='col', granularity=2):
    return excel_util.read_sheet(sheet, order, granularity)


def cell_update(sheet, row, col, buf, font=None, align=None, fill=None, link=None, border=None):
    return excel_util.cell_update(sheet, row, col, buf, font, align, fill, link, border)
