"""
Copyright 2023, 2024, 2025, 2026 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Common functions used for reading and generating Excel reports.

**add_contents()**

add_contents() adds cell content and formatting to Excel sheets. The content list, contents_l, passed to add_contents()
is a list of rows with either:

    * A function pointer. This allows you to use a function to insert rows.
    * A list of dictionaries describing the cell content and formatting for each column. See "Column Dictionaries" and
      "Extended Column Dictionaries" below for details.

Column Dictionaries:

These key/value pairs are used by add_contents() to determine what and how to add cell contents.

+-----------+-----------------------+-------------------------------------------------------------------------------+
| Key       | Type                  | Description                                                                   |
+===========+=======================+===============================================================================+
| a         | Function pointer      | Allows you to insert column data from a function rather than a dictionary or  |
|           |                       | hard coded values.                                                            |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| align     | xl_styles.Alignment,  | One of the align types from brcdapi.excel_util. The default is _align_wrap.   |
|           | None                  | If explicitly set to None, the alignment for the cell is not set. In that     |
|           |                       | case, the alignment for the cell will be the default for the Excel workbook.  |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| border    | xl_styles.Border,     | One of the border types from brcdapi.excel_util. The default is _border_thin. |
|           | None                  | See notes with align regarding a None value.                                  |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| buf       | See description       | Determines what to print in the cell as follows:                              |
|           |                       |   Function pointer    The function is called. The returned value is used as   |
|           |                       |                       cell content.                                           |
|           |                       |   int, float, str     Unless converted to a string, see note at bottom, these |
|           |                       |                       values are used directly as cell content.               |
|           |                       |   dict                The key is used to retrieve the cell value from the     |
|           |                       |                       dictionary.                                             |
|           |                       |   Object type         In this module, the object type is a switch object. The |
|           |                       |                       key is used to retrieve the cell value from the object. |
|           |                       |   list                May be a list of the above. If the length of the list   |
|           |                       |                       is greater than 1, after all items are converted to     |
|           |                       |                       strings and concatenated. WARNING: Supporting a list    |
|           |                       |                       was planned, but never tested. I'm not sure if I even   |
|           |                       |                       finished coding it.                                     |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| comments  | str                   | Cell comments                                                                 |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| dv        | DataValidation        | Data validation object from openpyxl.worksheet.datavalidation.DataValidation  |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| fill      | xl_styles.PatternFill | One of the fill types from brcdapi.excel_util.                                |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| font      | xl_styles.Font,       | One of the font types from brcdapi.excel_util. The default is _std_font       |
|           | None                  | See notes with align regarding a None value.                                  |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| key       | str, key              | Key to use when the buf item is a dictionary or a brcddb class object. It is  |
|           |                       | also passed to functions when buf is a function pointer.                      |
+-----------+-----------------------+-------------------------------------------------------------------------------+
| span      | int, list, tuple      | Number of columns to span (merge). If 0, fill in with the maximum column.     |
|           |                       | Using a list or tuple only makes sense when the function in 'a' knows what to |
|           |                       | do with it. At the time this was written, brcddb.report.utils.cell_content()  |
|           |                       | was the only function that worked with a list of tuple.                       |
+-----------+-----------------------+-------------------------------------------------------------------------------+

Extended Column Dictionaries:

These key/value pairs are ignored by add_contents(). They are used to customize pre-determined content. At the time this
was written, using this data was limited to the port map created when the chassis page is created. The switch page
displays this same port map except ports not in the logical switch are greyed out, the highlighting links are for the
switch instead of the chassis, and highlighting operations cannot be applied to ports not in that logical switch. Some
data was also added for fabrics with future plans to add port highlighting to the fabric port list.

+-------------------+-----------+-----------------------------------------------------------------------------------+
| Key               | Type      | Description                                                                       |
+===================+===========+===================================================================================+
| ch_cond_link      | str       | The reference to the "Chassis Highlight Total" cell.                              |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| sw_cond_link      | str       | The reference to the "Switch Highlight Total" cell.                               |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| fab_cond_link     | str       | The reference to the "Fabric Highlight Total" cell.                               |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| port_obj          | PortObj   | Port object for the port.                                                         |
+-------------------+-----------+-----------------------------------------------------------------------------------+

**Public Functions**

+-------------------------------+-----------------------------------------------------------------------------------+
| Method                        | Description                                                                       |
+===============================+===================================================================================+
| aboug_page                    | Inserts a standard "About" page in a workbook.                                    |
+-------------------------------+-----------------------------------------------------------------------------------+
| add_content_defaults          | Adds the default values for font, align, and border to a list of contents for     |
|                               | add_contents().                                                                   |
+-------------------------------+-----------------------------------------------------------------------------------+
| add_contents                  | Adds contents to the worksheet                                                    |
+-------------------------------+-----------------------------------------------------------------------------------+
| alert_eval                    | Determines if there are alerts associated with an object.                         |
+-------------------------------+-----------------------------------------------------------------------------------+
| cell_content                  | Builds a list of column dictionaries for rows that are Comment, Parameter, Value  |
+-------------------------------+-----------------------------------------------------------------------------------+
| combined_alerts               | Converts alerts associated with a port object and the login and FDMI objects      |
|                               | for lwwn to a human-readable string.                                              |
+-------------------------------+-----------------------------------------------------------------------------------+
| combined_alert_objects        | Combines alerts associated with a port object and the login and FDMI objects      |
|                               | for wwn.                                                                          |
+-------------------------------+-----------------------------------------------------------------------------------+
| comments_for_alerts           | Converts alerts associated with an object to a human-readable string.             |
|                               | Multiple comments separated with /n                                               |
+-------------------------------+-----------------------------------------------------------------------------------+
| combined_login_alerts         | Converts alerts associated with a login object and the login and FDMI objects     |
|                               | for lwwn to a human-readable string                                               |
+-------------------------------+-----------------------------------------------------------------------------------+
| combined_login_alert_objects  | Combines login alert objects with FDMI HBA and FDMI port alerts objects           |
+-------------------------------+-----------------------------------------------------------------------------------+
| conditional_highlight         | Adds the port highlighting filters for a worksheet.                               |
+-------------------------------+-----------------------------------------------------------------------------------+
| fabric_name_case              | Return the fabric name. Typically used in case statements for page reports in     |
|                               | brcddb.report.                                                                    |
+-------------------------------+-----------------------------------------------------------------------------------+
| fabric_name_or_wwn_case       | Return the fabric name with (wwn). Typically used in case statements for page     |
|                               | reports in brcddb.report.*                                                        |
+-------------------------------+-----------------------------------------------------------------------------------+
| fabric_wwn_case               | Return the fabric WWN. Typically used in case statements for page reports in      |
|                               | brcddb.report.                                                                    |
+-------------------------------+-----------------------------------------------------------------------------------+
| font_type                     | Determines the display font based on alerts.                                      |
+-------------------------------+-----------------------------------------------------------------------------------+
| font_type_for_key             | Determines the display font based on alerts associated with an object.            |
+-------------------------------+-----------------------------------------------------------------------------------+
| get_next_switch_d             | Finds the first match in sl list returned from excel_util.read_sheet() and        |
|                               | returns the next entry                                                            |
+-------------------------------+-----------------------------------------------------------------------------------+
| list_to_str                   | Converts a list to a \n seperated list. Returns the column list.                  |
+-------------------------------+-----------------------------------------------------------------------------------+
| alert_summary                 | Inserts MAPS dashboard rows.                                                      |
+-------------------------------+-----------------------------------------------------------------------------------+
| parse_sfp_file                | Parses Excel file with the new SFP rules. See sfp_rules_rx.xlsx                   |
+-------------------------------+-----------------------------------------------------------------------------------+
| parse_switch_file             | Parses Excel switch configuration Workbook used with switvch_config.py.           |
+-------------------------------+-----------------------------------------------------------------------------------+
| port_statistics               | Adds port statistics for the worksheet.                                           |
+-------------------------------+-----------------------------------------------------------------------------------+
| seconds_to_days               | Converts a value in seconds to days. Returns the comments, parameter, and value   |
|                               | in a list for column insertion.                                                   |
+-------------------------------+-----------------------------------------------------------------------------------+
| title_page                    | Creates a title page for the Excel report.                                        |
+-------------------------------+-----------------------------------------------------------------------------------+

**Public Data**

+-----------------------+-------+-----------------------------------------------------------------------------------+
| Data                  | Type  | Description                                                                       |
+=======================+=======+===================================================================================+
| default_stats         | int   | Default value for the highlighting section of port stats. This is also the        |
|                       |       | maximum allowable value in highlight_stats_dv.                                    |
+-----------------------+-------+-----------------------------------------------------------------------------------+
| highlight_stats_dv    | class | Data validation class: openpyxl.worksheet.datavalidation.DataValidation           |
+-----------------------+-------+-----------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Added functions to support the combined switch and chassis formats.                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Fixed bugs: FC address on ICL ports for FICON switches, allowing XISL on base switch, |
|           |               | and setting the default routing policy.                                               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 26 Dec 2024   | Fixed grammar mistake in help message.                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 04 Jan 2025   | Added Slot_x_Terms is list of sheets to skip reading.                                 |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 12 Apr 2025   | FOS 9.2 updates.                                                                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.7     | 25 Aug 2025   | Made _alert_font_d public (changed to alert_font_d).                                  |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.8     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.9     | 04 Dec 2025   | Added clearer language regarding port highlighting.                                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.0     | 20 Feb 2026   | Updated disclaimer in _about_sheet_l.                                                 |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.1     | 21 Feb 2026   | Removed debug code.                                                                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.2     | 10 Mar 2026   | Added more error checking and more user friendly error messages.                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.3     | 01 Aug 2026   | Added start/end and CLI commands for switch and chassis.                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.4     | 26 Oct 2026   | Added ability to process 'rh', row_height, in contents_l passed to add_contents()     |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.5     | 29 Oct 2026   | Somehow, import brcddb.util.iocp was removed. It's back.                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025, 2026 Jack Consoli'
__date__ = '29 Oct 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.1.5'

import collections
import copy
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting import Rule
from openpyxl.styles.differential import DifferentialStyle
import openpyxl.utils.cell as xl_util
import brcdapi.util as brcdapi_util
import fnmatch
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.excel_util as excel_util
import brcdapi.excel_fonts as excel_fonts
import brcdapi.port as brcdapi_port
import brcddb.util.obj_convert as brcddb_conv
import brcddb.brcddb_port as brcddb_port
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_login as brcddb_login
import brcddb.util.search as brcddb_search
import brcddb.util.iocp as brcddb_iocp
import brcddb.app_data.alert_tables as al_table
import brcddb.app_data.report_tables as rt
import brcddb.classes.alert as alert_class
import brcddb.classes.util as brcddb_class_util
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.zone as zone_report

default_stats = 999999999999999
highlight_stats_dv = DataValidation(type='whole',
                                    operator='between',
                                    formula1=0,
                                    formula2=default_stats,
                                    allow_blank=False)
highlight_stats_dv.errorTitle = 'Invalid Entry'
highlight_stats_dv.error = 'Value must be an integer between 0 and ' + str(default_stats)
highlight_stats_dv.showErrorMessage = True

_apt_policy_d = dict(EBR='exchange-based', DBR='device-based')

# Below is for efficiency
_std_font = excel_fonts.font_type('std')
_bold_font = excel_fonts.font_type('bold')
_warn_font = excel_fonts.font_type('warn')
_error_font = excel_fonts.font_type('error')
_gray_font = excel_fonts.font_type('gray')
_link_font = excel_fonts.font_type('link')
_hdr1_font = excel_fonts.font_type('hdr_1')
_align_wrap = excel_fonts.align_type('wrap')
_align_wrap_r = excel_fonts.align_type('wrap_right')
_align_wrap_vc = excel_fonts.align_type('wrap_vert_center')
_align_wrap_c = excel_fonts.align_type('wrap_center')
_border_thin = excel_fonts.border_type('thin')
_lightgreen_fill = excel_fonts.fill_type('lightgreen')
_lightgold_fill = excel_fonts.fill_type('lightgold')
_lightred_fill = excel_fonts.fill_type('lightred')
_lightblue_fill = excel_fonts.fill_type('lightblue')
_yellow_fill = excel_fonts.fill_type('yellow')

# _obj_type_to_key_d is used in add_contents() to determine what "xxx_Highlight Total" to use for the object.
_obj_type_to_key_d = dict(ChassisObj='ch_cond_link', SwitchObj='sw_cond_link', FabricObj='fab_cond_link')

# About worksheet - used in function: about
_about_sheet_l = (
    dict(f=_hdr1_font, t='Generated By'),
    None,
    dict(f=_std_font, t='Script:  ', s='script_name'),
    dict(f=_std_font, t='Version: ', s='version'),
    None,
    dict(f=_hdr1_font, t='Description'),
    None,
    dict(f=_std_font, t='', s='description'),
    None,
    dict(f=_hdr1_font, t='Automation & Scripting Tools'),
    None,
    dict(f=_std_font,
         t='The script used to generate this workbook and other scripts for use with the Brocade FOS RESTConf API can '
           'be found at:'),
    dict(f=_link_font, l='https://github.com/jconsoli', t='https://github.com/jconsoli'),
    None,
    dict(f=_std_font,
         t='YouTube videos to assist with getting started and using some of the sample scripts are available at:'),
    dict(f=_link_font,
         l='https://youtu.be/BWz7L0QOtYQ',
         t='Getting Started: Install Python and configure Brocade switches for use with the API'),
    dict(f=_link_font, l='https://youtu.be/n9-Eni_AFCg', t='Capture Data & Generate Reports'),
    dict(f=_link_font, l='https://youtu.be/x1OvuRZRdA8', t='FOS API Zoning'),
    dict(f=_link_font, l='https://youtu.be/WGxXZrvhG2E', t='Chassis, Switch, Fabric, and Port Configuration'),
    None,
    dict(f=_std_font, t='email: jack_consoli@yahoo.com'),
    None,
    dict(f=_hdr1_font, t='Disclaimer'),
    None,
    dict(f=_std_font,
         t='The script uses open source software covered by the GNU General Public License or other open source '
           'license agreements.'),
    None,
    dict(f=_std_font,
         t='The accuracy and completness of information contained herein are dependant of the FOS version, data '
           'collection method, and other factors. Consoli-Solutions and Jack Consoli do not assume any liability '
           'arising out of the application or use of this information, nor the application or use of any product or '
           'software described herein, neither does it convey any license under its patent rights nor the rights of '
           'others.'),
)

_enable_disable_d = {'Enable': 'enable', 'Disable': 'disable','Persistent Disable': 'persistent_disable'}
_yes_no_d = dict(Yes=True, No=False)
_reserve_d = dict(Reserve='reserve',Release='release')


def _cli_to_list(cli):
    """Converts CLI to a list.

    :param cli: CLI string from workbook
    :type cli: str, None
    :return: List of CLI commands
    :rtype: list
    """

    return [b for b in cli.replace('\r\n', '\n').split('\n') if len(b) > 0]

"""
Dictionary definitions for _conv_parameters(). Used in _parse_chassis_switch_sheet() and _parse_slot_sheet() to
determine how to process worksheet entries.

+-------+-----------------------------------------------------------------------------------------------+
| Key   | Description                                                                                   |
+=======+===============================================================================================+
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
| p     | Fixed value length. "0"s are prepended to make the value this length. Used for creating FC    |
|       | addresses and link addresses.                                                                 | 
+-------+-----------------------------------------------------------------------------------------------+
| conv  | Pointer to the dictionary to convert cell context to a True/False boolean.                    |
+-------+-----------------------------------------------------------------------------------------------+
"""
_conv_parameters_d = {  # See table above
    # Common to all worksheets
    'CLI': dict(k='cli', h=False, i=False, s=True, slot=False, p=0, conv=_cli_to_list),
    # Common to "Chassis" and "Switch_x" Worksheets
    'Enable/Disable': dict(k='enable', h=False, i=False, s=False, slot=False, p=0, conv=_enable_disable_d),
    # Common to "Switch_x" and "Slot x" worksheets
    'Port Name': dict(k='port_name', h=False, i=False, s=False, slot=False, p=0, conv=None),
    # "Chassis" Worksheet
    'Chassis Name': dict(k='chassis_name', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'FCR': dict(k='fcr', h=False, i=False, s=False, slot=False, p=0, conv=_enable_disable_d),
    'Message Of The Day': dict(k='msg_of_day', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Shell Timeout': dict(k='shell_to', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Session Timeout': dict(k='session_to', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'TCP Timeout Level': dict(k='tcp_to', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Max REST Sessions': dict(k='max_rest', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Web Tools': dict(k='web_tools', h=False, i=False, s=False, slot=False, p=0, conv=_enable_disable_d),
    'Configure Switches': dict(k='config_switches', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    # "Switch_x" Worksheets
    'Fabric ID (FID)': dict(k='fid', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Fabric Name': dict(k='fab_name', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Switch Name': dict(k='switch_name', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Domain ID (DID)': dict(k='did', h=True, i=False, s=False, slot=False, p=0, conv=None),
    'Insistent DID': dict(k='insistent_did', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    'Fabric Principal': dict(k='fab_principal', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    'Fabric Principal Priority': dict(k='fab_priority', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Allow XISL': dict(k='xisl', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    'Login Banner': dict(k='login_banner', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Switch Type': dict(k='switch_type', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Duplicate WWN': dict(k='dup_wwn', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Bind': dict(k='bind', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    'Routing Policy': dict(k='routing_policy', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Port Name Format': dict(k='port_name_format', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Configure Ports': dict(k='config_ports', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Enable CUP': dict(k='cup', h=False, i=False, s=False, slot=False, p=0, conv=_yes_no_d),
    'SCC': dict(k='scc', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'FICON Zone': dict(k='ficon_zone', h=False, i=False, s=False, slot=False, p=0, conv=None),
    # FICON Zone
    # Ports, "Slot x" worksheets
    'Port': dict(k='port', h=False, i=False, s=True, slot=True, p=0, conv=None),
    'DID (Hex)': dict(k='did', h=True, i=False, s=True, slot=False, p=0, conv=None),
    'Port Addr (Hex)': dict(k='port_addr', h=False, i=False, s=True, slot=False, p=2, conv=None),
    'Index': dict(k='index', h=False, i=True, s=True, slot=False, p=0, conv=None),
    'Link Addr': dict(k='link_addr', h=False, i=False, s=True, slot=False, p=4, conv=None),
    'FID': dict(k='fid', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Start Enable': dict(k='start_enable', h=False, i=False, s=False, slot=False, p=0, conv=_enable_disable_d),
    'End Enable': dict(k='end_enable', h=False, i=False, s=False, slot=False, p=0, conv=_enable_disable_d),
    'Reserve': dict(k='reserve', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Attached Device': dict(k='desc', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'ICL Description': dict(k='desc', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Low Qos VC': dict(k='low_vc', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'Med Qos VC': dict(k='med_vc', h=False, i=False, s=False, slot=False, p=0, conv=None),
    'High Qos VC': dict(k='high_vc', h=False, i=False, s=False, slot=False, p=0, conv=None),
}


class Found(Exception):
    pass


#########################################################################
#                                                                       #
# Common case statements in port_page(), switch_page(), chassis_page()  #
#                                                                       #
#########################################################################
def fabric_name_case(obj, k=None, wwn=None):
    """Return the fabric name. Typically used in case statements for page reports in brcddb.report.*

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
    """Return the fabric name with (wwn). Typically used in case statements for page reports in brcddb.report.*

    See fabric_name_case() for parameter definitions"""
    return brcddb_fabric.best_fab_name(obj.r_fabric_obj(), True)


def fabric_wwn_case(obj, k=None, wwn=None):
    """Return the fabric WWN. Typically used in case statements for page reports in brcddb.report.*

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
    """Converts alerts associated with an object to a human-readable string. Multiple comments separated with /n

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
    """Converts alerts associated with a login object and the login and FDMI objects for lwwn to a human-readable string

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
    """Converts alerts associated with a port object and the login and FDMI objects for lwwn to a human-readable string.

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
            'disp': ('col_1', 'col_2', 'etc.')   # Str, list or tuple. Content to add to the worksheet
        }
        Example:
        content = (
            {'font': 'hdr_1', 'merge': 3, 'align': 'wrap_center', 'disp': 'Title Page'},
            {}, # Skip a row
            {'font': 'std', 'align': 'wrap', 'disp': ('col_1', 'col_2', 'col_3') }
        )

    :param wb: Workbook object
    :type wb: class
    :param tc: Table of context page. A link to this page is place in cell A1.
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed. Typically, 0. Default is 0
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
    # Add the content. Intended for general use so lots of error checking.
    col = 1
    if isinstance(content, (list, tuple)):
        for obj in content:
            if isinstance(obj, dict):
                display_l = list()
                if 'disp' in obj:
                    if isinstance(obj.get('disp'), (str, int, float)):
                        display_l.append(obj.get('disp'))
                    elif isinstance(obj.get('disp'), (list, tuple)):
                        display_l = obj.get('disp')
                    elif obj.get('disp') is None:
                        pass
                    else:
                        brcdapi_log.exception('Unknown disp type, ' + str(type((obj.get('disp')))) + ', at row ' +
                                              str(row), echo=True)
                for buf in display_l:
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
    """Finds the first match in sl list returned from excel_util.read_sheet() and returns the next entry

    :param switch_list: A list of dictionaries as returned from excel_util.read_sheet()
    :type switch_list: list, tuple
    :param val: The value to look for
    :type val: str, int, float
    :param test_type: The type of test to perform. See brcddb.util.search.match_test
    :type test_type: str
    :param ignore_case: If True, performs a case-insensitive search
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
    rl = list()

    # Load the workbook & contents
    if file is not None:
        try:
            # Return everything up to '__END__'
            for d in excel_util.parse_parameters(sheet_name='new_SFP_rules', hdr_row=0, wb_name=file)['content']:
                if d['Group'] == '__END__':
                    break
                else:
                    rl.append(d)
        except FileNotFoundError:
            brcdapi_log.log('SFP rules workbook: ' + str(file) + ' not found.', echo=True)
            return list()
        except FileExistsError:
            brcdapi_log.log('Folder in ' + file + ' does not exist', echo=True)
            return list()

    return rl


def find_headers(hdr_row_l, hdr_l=None, warn=False):
    """Moved to brcdapi.excel_util.find_headers()"""
    return excel_util.find_headers(hdr_row_l, hdr_l=hdr_l, warn=warn)


def _convert_parameters(area, parameter):
    """Converts worksheet cell values to machine-readable values.
    
    :param area: Used as key into _conv_parameters
    :type area: str
    :param parameter: Parameter to convert
    :type parameter: None, str, int
    :return error_l: List of errors messages
    :rtype: list
    :return return_key: Machine readable key for the area
    :rtype return_key: str
    :return return_v: parameter converted to a machine-readable format.
    :rtype return_v: None, str, int, list
    """
    global _conv_parameters_d

    # Initialize return values and conversion table
    error_l = list()
    return_key = None
    return_v = None if isinstance(parameter, str) and len(parameter.replace(' ', '')) == 0 else parameter
    control_d = _conv_parameters_d.get(area) if isinstance(area, str) else None
    if not isinstance(control_d, dict):
        return error_l, return_key, return_v  # I'm assuming the user added stuff to the workbook for documentation
    return_key = control_d.get('k')
    if not isinstance(return_key, str):
        return error_l, return_key, return_v  # I'm assuming the user added stuff to the workbook for documentation
    if return_v is None:
        return error_l, return_key, return_v

    # Modify return value
    if control_d['s']:
        return_v = str(return_v)
    if control_d['h']:
        temp_v = '0x' + str(return_v) if isinstance(return_v, int) else return_v
        try:
            return_v = int(temp_v, 16)
        except ValueError:
            error_l.append('Value for ' + k + ', ' + str(return_v) + ', is not a valid hex number.')
    if control_d['i']:
        if return_v != 'None':
            try:
                return_v = int(return_v)
            except ValueError:
                error_l.append('Value for ' + k + ', ' + str(return_v) + ', is not valid in ' + sheet_d['sheet'])
    if callable (control_d['conv']):
        return_v = control_d['conv'](return_v)
    elif isinstance(control_d['conv'], dict):
        return_v = control_d['conv'].get(return_v, False)
    if control_d['p'] > 0:
        return_v = gen_util.pad_string(return_v, control_d['p'], '0')

    return error_l, return_key, return_v


def _parse_chassis_switch_sheet(sheet_d):
    """Parses the "Chassis" and "Switch_x" worksheets from a switch configuration workbook into a dictionary.

    Return dictionaries in return_l

    +-----------+-----------------------+---------------------------------------------------------------------------+
    | Key       | type                  | Description.                                                              |
    +===========+=======================+===========================================================================+
    | key       | str                   | Simplified machine-readable key                                           |
    +-----------+-----------------------+---------------------------------------------------------------------------+
    | user_key  | str                   | User friendly key (Area) from worksheet. Used for error reporting.        |
    +-----------+-----------------------+---------------------------------------------------------------------------+
    | parameter | str, bool, int, float | Conditioned user entered parameter. See _convert_parameters()             |
    +-----------+-----------------------+---------------------------------------------------------------------------+
    | row       | int                   | 0 relative worksheet row number. Used for error reporting.                |
    +-----------+-----------------------+---------------------------------------------------------------------------+

    :param sheet_d: Output from excel_util.read_workbook() for the Chassis worksheet
    :type sheet_d: dict
    :return error_l: Error messages. Empty if no error encountered
    :rtype error_l: list
    :return return_l: List of dictionaries. See function header for details.
    :rtype return_l: list
    :return fid: Fabric ID. Only relavant for switch sheets.
    :rtype fid: int, None
    :return fid_row: 0 relative row number for FID. Used for error reporting.
    :rtype fid_row: int
    :return did: Domain ID. Only relavant for switch sheets.
    :rtype did: int, None
    :return did_row: 0 relative row number for FID. Used for error reporting.
    :rtype did_row: int
    """
    error_l, return_l, fid, fid_row, did, did_row = list(), list(), None, 0, None, 0

    al = sheet_d['al']
    if len(al) < 2:  # The sheet is empty
        return error_l, return_l

    # Find the 'Area' and 'Parameter' columns and do some basic worksheet validation
    col_d = excel_util.find_headers(al[0], ('Area', 'Parameter'))
    for k, v in col_d.items():
        if v is None:
            error_l.append('Sheet ' + sheet_d['switch_info']['sheet_name'] + ' missing column ' + k)
    if len(error_l) > 0:
        return error_l, rd
    area_i, param_i = col_d['Area'], col_d['Parameter']

    # Add the dictionary to the return list
    for row in range(1, len(al)):

        # Get the Area and Parameter
        area, parameter = al[row][area_i], al[row][param_i]
        if not isinstance(area, str) or parameter is None:
            continue  # I'm assuming it's a blank row  of empty parameter cell
        if isinstance(area, str) and len(area) > 0 and area[0] == '#':
            continue

        # Add the data to the return list.
        ml, area_key, return_v = _convert_parameters(area, parameter)
        error_l.extend(ml)
        if return_v is not None:
            if area_key == 'fid':
                fid, fid_row = return_v, row
            elif area_key == 'did':
                did, did_row = return_v, row
            return_l.append(dict(key=area_key, user_key=area, parameter=return_v, row=row))

    return error_l, return_l, fid, fid_row, did, did_row


def _parse_slot_sheet(sheet_d, chassis_d):
    """Parses a "Slot x" worksheet from a configuration workbook into a dictionary. The key is the port number in s/p
    notation.

    :param sheet_d: Raw data read from the workbook. See _conv_parameters_d for details.
    :type sheet_d: dict
    :param chassis_d: See "chassis_d" in parse_switch_file() for details
    :type chassis_d: dict
    :return error_l: List of error messages. Empty if no error encountered
    :rtype error_l: list
    """
    global _conv_parameters_d

    error_l, al, buf, slot = list(), sheet_d['al'], '', ''

    # Find the slot number
    for buf in al[0]:
        if buf is not None and 'slot' in buf.lower():
            slot = buf.split(' ')[1] + '/'
            break

    # Find the column headers
    i, hdr_l, col_d_l = 0, al[1], [dict(), dict()]
    for col in range(0, len(hdr_l)):
        try:
            r_key = _conv_parameters_d[hdr_l[col]]['k']
            if r_key in col_d_l[i]:
                i += 1  # A repeat means we're starting the second column of ports
                if i > len(col_d_l):
                    error_l.append('Invalid column header, "' + buf + '", on sheet ' + sheet_d['sheet'])
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

            # Build the port map dict and add it to chassis_d
            port_d = dict(sheet=sheet_d['sheet'])
            for area, control_d in _conv_parameters_d.items():
                r_key = control_d['k']
                if r_key in col_d_l[i]:
                    ml, r_key, return_v = _convert_parameters(area, al[row][col_d_l[i][r_key]])
                    error_l.extend(ml)
                    if isinstance(return_v, list) and isinstance(port_d.get(r_key), list):
                        port_d[r_key].extend(return_v)
                    else:
                        port_d[r_key] = return_v
                    if r_key == 'port':
                        port_d['row'] = row
                        port_d['port_key'] = slot + return_v
            chassis_d['port_d'][port_d['port_key']] = port_d

    return error_l


def parse_switch_file(file):
    """Parses Excel switch configuration Workbook. The dictionary in the return lists is as follows:

    IMPORTANT NOTE: The "Type" column in the Sphinx documentation below refers to the value type from the "Parameter"
                    cell associated with the "Area". The value may also be type None if no parameter data was entered.

    chassis_d

    +---------------+-------+---------------------------------------------------------------------------------------+
    | Key           | Type  | Description                                                                           |
    +===============+=======+=======================================================================================+
    | port_d        | dict  | Key: Port number in s/p notation. Value: See "port_d" below.                          |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | data_l        | list  | List of dictionaries representing the "Chassis" worksheet. Each dictionary has the    |
    |               |       | following:                                                                            |
    |               |       | Key           Value                                                                   |
    |               |       | ___           _____                                                                   |
    |               |       | key           User key converted to a machine key. See _conv_parameters_d.            |
    |               |       | user_key      The user key as read from the "Area" column                             |
    |               |       | parameter     Parameter as read from the "Parameter" column.                          |
    |               |       | row           0 relative row number. Used for error eporting.                         |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | sheet         | str   | Sheet name                                                                            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | switch_d      | dict  | Key: FID as an integer. Value: See "sheet_d" below.                                   |
    +---------------+-------+---------------------------------------------------------------------------------------+

    switch_d

    +---------------+-------+---------------------------------------------------------------------------------------+
    | Key           | Type  | Description                                                                           |
    +===============+=======+=======================================================================================+
    | sheet         | str   | Sheet name                                                                            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | data_l        | list  | List of dictionaries representing the "Switch_x" worksheet. Each dictionary has the   |
    |               |       | following (same as chassis_d['data_l']:                                               |
    |               |       | Key           Value                                                                   |
    |               |       | ___           _____                                                                   |
    |               |       | key           User key converted to a machine key. See _conv_parameters_d.            |
    |               |       | user_key      The user key as read from the "Area" column                             |
    |               |       | parameter     Parameter as read from the "Parameter" column.                          |
    |               |       | row           0 relative row number. Used for error eporting.                         |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | did           | int   | Domain ID                                                                             |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | did_row       | int   | 0 relative sheet row number where "Domain ID (DID)" was found. Used for error         |
    |               |       | reporting.                                                                            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | fid           | int   | Fabric ID                                                                             |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | fid_row       | int   | 0 relative sheet row number where "Fabric ID (FID)" was found. Used for error         |
    |               |       | reporting.                                                                            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | ge_port_l     | list  | List of GE ports in s/p notation that belong to this switch.  See port_d.             |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | row           | int   | 0 relative sheet row number associated with dictionary. Used for error reporting.     |
    +---------------+-------+---------------------------------------------------------------------------------------+

    port_d - Filled in by _parse_slot_sheet().

    +---------------+-------+---------------------------------------------------------------------------------------+
    | Key           | Type  | Description                                                                           |
    +===============+=======+=======================================================================================+
    | cli           | list  | List of CLI commands from the parameter column associated with Area "CLI".            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | port_name     | str   | Parameter associated with Area "Port Name".                                           |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | fid           | int   | Parameter associated with Area "FID".                                                 |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | did           | int   | Parameter associated with Area "DID (Hex)".                                           |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | end_enable    | int   | Parameter associated with Area "End Enable".                                          |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | index         | int   | Parameter associated with Area "Index".                                               |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | link_addr     | int   | Parameter associated with Area "Link Addr".                                           |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | port          | int   | Parameter associated with Area "Port".                                                |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | port_addr     | str   | Parameter associated with Area "Port Addr (Hex)".                                     |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | port_key      | str   | Port number in s/p notation. Intended for looking up the port object in ChassisObj    |
    |               |       | and SwitchObj                                                                         |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | reserve       | str   | Parameter associated with Area "Reserve".                                             |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | row           | int   | 0 relative sheet row number associated with dictionary. Used for error reporting.     |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | sheet         | str   | Sheet name                                                                            |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | start_enable  | str   | Parameter associated with Area "Start Enable".                                        |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | low_vc        | int   | Parameter associated with Area "Low Qos VC".                                          |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | med_vc        | int   | Parameter associated with Area "Med Qos VC".                                          |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | high_vc       | int   | Parameter associated with Area "High Qos VC".                                         |
    +---------------+-------+---------------------------------------------------------------------------------------+

    :param file: Path and name of Excel Workbook with switch configuration definitions
    :type file: str
    :return error_l: List of errors. Empty list if no errors found
    :rtype error_l: list
    :return chassis_d: Dictionary as described above.
    :rtype chassis_d: dict
    """
    switch_d = dict()

    chassis_d = dict(switch_d=switch_d, data_l=list(), port_d=dict())

    # Load the workbook
    skip_l = ('About', 'Summary', 'Sheet', 'Instructions', 'Slot_x_Terms', 'CLI_Bind', 'lists', 'VC')
    error_l, sheet_l = excel_util.read_workbook(file, dm=3, skip_sheets=skip_l, hidden=False)
    if len(error_l) > 0:
        return error_l, chassis_d

    # Parse the "Chassis", "Sheet_x", and "Slot x" worksheets
    for sheet_d in sheet_l:
        buf = file + ' does not look like a valid switch configuration workbook. Use X7-8_Switch_Configuration.xlsx '
        buf += 'as an example.'

        try:
            title = sheet_d['sheet']
            if fnmatch.fnmatch(title, 'Chassis*'):
                chassis_d['sheet'] = title
                ml, data_l, fid, fid_row, did, did_row = _parse_chassis_switch_sheet(sheet_d)
                error_l.extend(ml)
                chassis_d['data_l'] = data_l

            elif fnmatch.fnmatch(title, 'Switch*'):
                ml, data_l, fid, fid_row, did, did_row = _parse_chassis_switch_sheet(sheet_d)

                # Is the FID valid?
                if not isinstance(fid, int) or fid < 1 or fid > 128:
                    buf = 'Invalid FID for sheet: ' + title + ', row: ' + str(fid_row+1) + '. FIDs must be an integer '
                    buf += 'in the range of 1-128.'
                    ml.append(buf)
                else:  # Is there a duplicate FID?
                    existing_sheet_d = switch_d.get(fid)
                    if existing_sheet_d is not None:
                        buf = 'Duplicate logical switches with the same FID, ' + str(fid) + '. Sheet: '
                        buf += existing_sheet_d['sheet'] + ', Row: ' + str(existing_sheet_d['fid_row']+1) + ' and '
                        buf += 'Sheet: ' + title + ' Row: ' + str(fid_row+1)
                        ml.append(buf)

                # Is the DID valid?
                if not isinstance(did, int) or did < 0 or did > 239:
                    buf = 'Invalid DID for sheet: ' + title + ', row: ' + str(did_row+1) + '. DIDs must be entered as '
                    buf += 'a hex number in the range of 0x01-0xEF.'
                    ml.append(buf)
                if len(ml) > 0:
                    error_l.extend(ml)
                else:
                    switch_d[fid] = dict(
                        sheet=title,
                        data_l=data_l,
                        port_l=list(),
                        ge_port_l=list(),
                        fid=fid,
                        fid_row=fid_row,
                        did=did,
                        did_row=did_row,
                    )

            elif fnmatch.fnmatch(title, 'Slot ?*'):
                error_l.extend(_parse_slot_sheet(sheet_d, chassis_d))

        except (TypeError, ValueError, IndexError):
            error_l.append(buf)
            break

    return error_l, chassis_d


def empty_port_d():
    """Used when a port is added after calling parse_switch_file().

    :return: See "port_d" in parse_switch_file()
    :rtype: dict
    """
    return dict(
        cli=None,
        port_name=None,
        fid=0,
        did=0,
        end_enable=None,
        index=None,
        link_addr='Unknown',
        port=-1,
        port_addr='Unknown',
        port_key='Unknown',
        row=0,
        sheet='Unknown',
        start_enable=None,
        low_vc=0,
        med_vc=0,
        high_vc=0,
    )


#####################################################################################
#                                                                                   #
#   New data and functions supporting the combined switch and chassis page formats  #
#                                                                                   #
#####################################################################################
def span_to_list(span):
    """Converts a span value into a list of length 3

    :param span: Value to convert to a list
    :type span: int, list, tuple
    :return: List of column span values
    :rtype: list
    """
    rl = gen_util.convert_to_list(span)
    x = rl[len(rl) - 1]
    while len(rl) < 3:
        rl.append(x)
    return rl


# _alert_d is a dictionary indexed by the URI. The value is a dictionary indexed by the alert numbers. By default, the
# alert dictionary is assumed to be empty if it's not in this table. The alerts in the switch object are searched for
# matching alert numbers in _alert_d. If found, that alert number is converted to a human-readable text message and
# inserted in the comments cell for the associated URI.
_alert_d = {
    brcdapi_util.bfc_idid: {al_table.ALERT_NUM.SWITCH_IDID: True},
    brcdapi_util.bfc_fport_enforce_login: {al_table.ALERT_NUM.HANDLE_DUP_WWN: True},
}
# alert_font_d is used to determine the font
alert_font_d = {
    # alert_class.ALERT_SEV.GENERAL: _std_font,
    alert_class.ALERT_SEV.WARN: _warn_font,
    alert_class.ALERT_SEV.ERROR: _error_font,
}

"""The sheet and cell location of the conditional highlighting parameters has to be stored in the switch or chassis
object. Rather than hard code it in _conditional_highlight_l, the list entries are determined in
conditional_highlight(). The key is the header. The value is a dictionary as follows:

+-----------+---------------------------------------------------+
| Key       | Value                                             |
+===========+===================================================+
| align     | One of the Excel align definitions.               |
+-----------+---------------------------------------------------+
| border    | One of the Excel border definitions.              |
+-----------+---------------------------------------------------+
| default   | The default (initial) value to fill in the cell   |
+-----------+---------------------------------------------------+
| dv        | Data validation                                   |
+-----------+---------------------------------------------------+
| font      | One of the Excel font definitions.                |
+-----------+---------------------------------------------------+

Formatting is always: font=_std_font, align=_align_wrap_r, border=_border_thin. The fill color is dynamically determined
based on the port type and if there are any errors."""
_default_stats = 999999999999
_conditional_test_0_d = collections.OrderedDict()
_conditional_test_0_d['Discarded Frames'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['BB Credit Starvation'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Bit Errors'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Warn Alerts'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Error Alerts'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Frame Errors'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Link Resets'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Link Failures'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_0_d['Loss Of Signal'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d = collections.OrderedDict()
_conditional_test_1_d['Loss Of Sync'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d['Too Many RDYs'] = dict(
    default=_default_stats,
    dv=highlight_stats_dv,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d['Zone EXACT'] = dict(
    default=None,
    dv=None,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d['Zone FIND'] = dict(
    default=None,
    dv=None,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d['Alias EXACT'] = dict(
    default=None,
    dv=None,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_test_1_d['Alias FIND'] = dict(
    default=None,
    dv=None,
    font=_std_font,
    align=_align_wrap_r,
    border=_border_thin)
_conditional_highlight_l = [
    [dict(buf='Port Highlighting', font=_bold_font, align=_align_wrap)],
    list(),
    [dict(buf='To highlight ports with zones and aliases using the EXACT or FIND functions in Excel, enter the zone '
            'object name in the box below. EXACT and FIND',
          font=_std_font,
          align=_align_wrap)],
    [dict(buf='are case sensitive. A FIND in Excel is equivalent to *zone_name*. For all other highlighting options, '
              'enter an integer in the range ',
          font=_std_font,
          align=_align_wrap)],
    [dict(buf='0 - 999,999,999. Numeric comparisons are greater than, ">". Highlighting is determined by a logical '
              'OR of all high lighting filters.',
        font=_std_font,
        align=_align_wrap)],
    list(),
]


def conditional_highlight(obj, span):
    """Returns a list of dictionaries for the "Port Highlighting" section. For use with add_contents().

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param span: Number of columns to span when displaying the conditional formatting
    :type span: int
    :return: List of lists containing dictionaries to insert while processing _contents
    :rtype: list
    """
    global _conditional_highlight_l, _std_font, _align_wrap_r, _border_thin

    rl, sheet_d = list(), obj.r_get('report_app/worksheet')
    sheet_ref = sheet_d['sheet'].title + '!'
    num_columns = sheet_d['num_columns']

    # Insert the section header
    rl = copy.deepcopy(_conditional_highlight_l)
    for col_l in rl:
        for col_d in [d for d in col_l if isinstance(d, dict)]:
            col_d['span'] = num_columns
    row = len(rl) + sheet_d['row']

    # Insert the cells for the "Port Highlighting" section.
    cond_format_d = sheet_d.get('cond_format_d')
    if isinstance(cond_format_d, dict):
        for conditional_d in (_conditional_test_0_d, _conditional_test_1_d):
            col, col_h_l, col_v_l = 1, list(), list()
            rl.extend([col_h_l, col_v_l])
            for buf, d in conditional_d.items():
                col_h_l.append(dict(
                    buf=buf,
                    dv=None,
                    font=_bold_font,
                    align=d['align'],
                    border=d['border'],
                    span=span))
                col_v_l.append(dict(
                    buf=d['default'],
                    dv=d['dv'],
                    font=d['font'],
                    align=d['align'],
                    border=d['border'],
                    span=span))
                cond_format_d[buf] = sheet_ref + xl_util.get_column_letter(col) + str(row+1)  # Entry is the next row
                col += span
            row += 2
    else:
        buf = 'Port highlighting is only available on the chassis page at this time. Port highlighting allows you to '
        buf += 'highlight ports with certain bit errors, with logins in certain zones or matching certain aliases, and '
        buf += 'more. Click on the chassis link at the top of the page.'
        rl = [
            [dict(buf='Port Highlighting', font=_bold_font, align=_align_wrap, span=num_columns)],
            [dict(buf='Port highlighting is only available on the chassis page at this time. Port highlighting allows '
                      'you to highlight ports with certain bit errors, with logins in certain zones or matching')],
            [dict(buf='certain aliases, and more. Click on the chassis link at the top of the page.')]
        ]
        add_content_defaults(rl, dict(font=_std_font, align=_align_wrap, span=num_columns))

    return rl


def port_statistics(obj, type_span, speed_span):
    """Returns a list of port statistics formatted for use with add_contents().

    :param obj: Project, fabric, chassis, or switch object
    :type obj: brcddb.classes.project.ProjectObj, brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj, \
        brcddb.classes.fabric.FabricObj
    :param type_span: Number of columns to span when displaying the number of ports by login type
    :type type_span: int
    :param speed_span: Number of columns to span when displaying the number of ports by login speed
    :type speed_span: int
    :return: List of lists containing dictionaries to insert while processing _contents
    :rtype: list
    """
    global _border_thin, _align_wrap, _bold_font, _align_wrap_r

    # Figure out what to put in the statistics summary section
    port_obj_l = brcddb_search.match_test(obj.r_port_objects(), brcddb_search.port_online)
    sum_logins = 0
    for port_obj in brcddb_search.match_test(port_obj_l, brcddb_search.f_ports):
        sum_logins += len(port_obj.r_login_keys())
    sheet_d = obj.r_get('report_app/worksheet')

    # Add the ports by login type
    return [
        [dict(buf='Ports by Login Type', font=_bold_font, align=_align_wrap, span=sheet_d['num_columns'])],
        [
            dict(buf='Physical Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='ICL-Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='ISL (E-Ports)', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='FC-Lag Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='Name Server Logins', font=_std_font, align=_align_wrap_r, border=_border_thin,
                 span=type_span),
        ],
        [
            dict(buf=len(obj.r_port_objects()),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.icl_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.e_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.fc_lag_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=sum_logins, font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
        ],
        [],

        # Add the ports by speed: Headers
        [dict(buf='Ports by Login Speed', font=_bold_font, align=_align_wrap, span=sheet_d['num_columns'])],
        [
            dict(buf='1G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='2G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='4G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='8G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='16G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='32G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='64G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='128G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
        ],
        [  # Add the ports by speed: The values
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_1g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_2g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_4g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_8g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_16g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_32g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_64g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_128g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
        ],
    ]


def enabled_no_login(obj, type_span, speed_span):
    """Returns a list of enabled ports with no logins formatted for use with add_contents().

    :param obj: Project, fabric, chassis, or switch object
    :type obj: brcddb.classes.project.ProjectObj, brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj, \
        brcddb.classes.fabric.FabricObj
    :param type_span: Number of columns to span when displaying the number of ports by login type
    :type type_span: int
    :param speed_span: Number of columns to span when displaying the number of ports by login speed
    :type speed_span: int
    :return: List of lists containing dictionaries to insert while processing _contents
    :rtype: list
    """
    global _border_thin, _align_wrap, _bold_font, _align_wrap_r

    # Figure out what to put in the statistics summary section
    port_obj_l = brcddb_search.match_test(obj.r_port_objects(), brcddb_search.port_online)
    sum_logins = 0
    for port_obj in brcddb_search.match_test(port_obj_l, brcddb_search.f_ports):
        sum_logins += len(port_obj.r_login_keys())
    sheet_d = obj.r_get('report_app/worksheet')

    # Add the ports by login type
    return [
        [dict(buf='Ports by Login Type', font=_bold_font, align=_align_wrap, span=sheet_d['num_columns'])],
        [
            dict(buf='Physical Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='ICL-Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='ISL (E-Ports)', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='FC-Lag Ports', font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf='Name Server Logins', font=_std_font, align=_align_wrap_r, border=_border_thin,
                 span=type_span),
        ],
        [
            dict(buf=len(obj.r_port_objects()),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.icl_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.e_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.fc_lag_ports)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
            dict(buf=sum_logins, font=_std_font, align=_align_wrap_r, border=_border_thin, span=type_span),
        ],
        [],

        # Add the ports by speed: Headers
        [dict(buf='Ports by Login Speed', font=_bold_font, align=_align_wrap, span=sheet_d['num_columns'])],
        [
            dict(buf='1G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='2G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='4G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='8G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='16G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='32G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='64G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf='128G', font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
        ],
        [  # Add the ports by speed: The values
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_1g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_2g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_4g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_8g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_16g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_32g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_64g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
            dict(buf=len(brcddb_search.match_test(port_obj_l, brcddb_search.login_128g)),
                 font=_std_font, align=_align_wrap_r, border=_border_thin, span=speed_span),
        ],
    ]


def add_content_defaults(contents_l, default_d):
    """Intended for adding default values for things such as font in a list of contents for add_contents()

    :param contents_l: Worksheet contents. This list will be modified.
    :type contents_l: list
    :param default_d: Contains keys and values (typically openpyxl.styles.fonts.Font)
    :type default_d: dict
    :return: Modified contents_l. WARNING: contents_l is returned as a convenience. contents_l is modified.
    :rtype: list
    """
    for content_l in [row_l for row_l in contents_l if isinstance(row_l, list)]:
        for d in [v0 for v0 in content_l if isinstance(v0, dict)]:
            for key, v1 in default_d.items():
                if key not in d:
                    d.update({key: v1})

    return contents_l


# _lookup_d is used in cell_content to determine which lookup table should be used to resolve descriptions.
_lookup_d = dict(
    ChassisObj=rt.Chassis.chassis_display_tbl,
    SwitchObj=rt.Switch.switch_display_tbl,
    FabricObj=rt.Fabric.fabric_display_tbl
)


def cell_content(obj, col_d, old_bool=False):
    """Builds a list of column dictionaries for rows that are Comment, Parameter, Value

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param col_d: Dictionary defining the column. Search for _contents: in brcddb.report.switch for details.
    :type col_d: dict
    :param old_bool: If True, treat the input as an old boolean style
    :type old_bool: bool
    :return: List of dictionaries with the comments, parameter, and setting values.
    :rtype: list
    """
    global _std_font, _align_wrap_r, _border_thin, _lookup_d

    comment_l, font = alert_eval(obj, col_d)
    span_l = span_to_list(col_d.get('span'))
    key = col_d['key']
    value = col_d.get('val', obj.r_get(key))

    # Determine the cell content
    if old_bool:  # I think this is obsolete by now.
        value = bool(value)
    elif isinstance(value, bool):
        value = str(value)
    elif isinstance(value, list):
        value = '\n'.join(value)

    try:
        parameter = _lookup_d[brcddb_class_util.get_simple_class_type(obj)].get(key)
    except TypeError:
        parameter = 'Invalid object: ' + str(type(obj))
        brcdapi_log.exception(parameter, echo=True)
    except KeyError:
        parameter = 'Invalid object type: ' + brcddb_class_util.get_simple_class_type(obj)
        brcdapi_log.exception(
            [parameter, ' Supported types are:', '\n'.join([str(k) for k in _lookup_d.keys()])],
            echo=True
        )

    return add_content_defaults(
        [
            [
                dict(buf=None if len(comment_l) == 0 else '\n'.join(comment_l), span=span_l[0]),
                dict(buf=parameter, span=span_l[1]),
                dict(buf=value, span=span_l[2]),
            ]
        ],
        dict(font=font, align=col_d.get('align'), border=col_d.get('border'))
    )[0]


def alert_summary(obj, col_d):
    """Inserts each alert as a row.

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param col_d: Dictionary defining the column. Search for _contents: in brcddb.report.switch for details.
    :type col_d: dict
    :return: List of lists containing dictionaries with MAPS alerts associated with the object.
    :rtype: list
    """
    rl, sheet_d = list(), obj.r_get('report_app/worksheet')
    if isinstance(sheet_d, dict):
        for alert_obj in obj.r_alert_objects():
            rl.append([dict(buf=alert_obj.fmt_msg())])
    if len(rl) == 0:
        rl.append([dict(buf='None')])

    return add_content_defaults(rl, dict(font=_std_font, align=_align_wrap, span=sheet_d['num_columns']))


def alert_eval(obj, col_d):
    """Determines if there are alerts associated with an object.

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param col_d: Dictionary in the sub-list of _contents
    :type col_d: dict
    :return comment_l: List of alerts for the comments field
    :rtype: list
    :return font: Font type for the cell
    :rtype: tuple
    """
    global _alert_d, alert_font_d

    comment_l, alert_level = list(), alert_class.ALERT_SEV.GENERAL
    for alert_obj in obj.r_alert_objects():
        if alert_obj.alert_num() in _alert_d.get(col_d['key'], list()):
            comment_l.append(alert_obj.fmt_msg())
            alert_level = max(alert_level, alert_obj.sev())

    return comment_l, alert_font_d.get(alert_level, col_d.get('font'))


def seconds_to_days(obj, col_d):
    """Converts a value in seconds to days. Returns the comments, parameter, and value in a list for column insertion

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param col_d: Dictionary in the sub-list of _contents
    :type col_d: dict
    :return: List of dictionaries with the comments, parameter, and setting values.
    :rtype: list
    """
    key, align, border, span_l = col_d['key'], col_d.get('align'), col_d.get('border'), span_to_list(col_d.get('span'))
    comment_l, font = alert_eval(obj, col_d)
    parameter = rt.Switch.switch_display_tbl.get(key)
    x = obj.r_get(key)
    value = int(x / 86400 + 0.5) if isinstance(x, int) else None
    return [
        dict(buf=None if len(comment_l) == 0 else '\n'.join(comment_l),
             font=font, align=align, border=border, span=span_l[0]),
        dict(buf=parameter, font=font, align=align, border=border, span=span_l[1]),
        dict(buf=value, font=font, align=align, border=border, span=span_l[2]),
    ]


def list_to_str(obj, col_d):
    """Converts a list to a \n seperated list. Returns the column list.

    :param obj: Switch or chassis object
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.chassis.ChassisObj
    :param col_d: Dictionary in the sub-list of _contents
    :type col_d: dict
    :return: List of dictionaries with the comments, parameter, and setting values.
    :rtype: list
    """
    global _align_wrap

    comment_l, font = alert_eval(obj, col_d)
    key, align, border, span_l = col_d['key'], col_d.get('align'), col_d.get('border'), span_to_list(col_d.get('span'))
    sl = obj.r_get(key)
    value = None if sl is None else '\n'.join(sl)
    return [
        dict(buf=None if len(comment_l) == 0 else '\n'.join(comment_l),
             font=font, align=align, border=border, span=span_l[0]),
        dict(buf=rt.Switch.switch_display_tbl.get(key), font=font, align=_align_wrap, border=border, span=span_l[1]),
        dict(buf=value, font=font, align=align, border=border, span=span_l[2]),
    ]


def add_contents(obj, contents_l):
    """Adds contents to the worksheet

    :param obj: brcddb object.
    :type obj: ProjectObj, FabricObj, SwitchObj, ChassisObj
    :param contents_l: List of dictionaries defining the cell contents (passed to brcdapi.excel_util.cell_update). The
                       dictionaries may also contain the key 'rh', whose value is the row height. If 'rh' is defined in
                       multiple dictionaries for the row, the maximum value is used for the row height.
    :type contents_l: list
    """
    global _yellow_fill

    col = 1
    sheet_d = obj.r_get('report_app/worksheet')
    if sheet_d is None:
        brcdapi_log.exception(str(type(obj)) + ' missing "report_app/worksheet"', echo=True)
        return
    sheet = sheet_d['sheet']

    # Add the contents
    for row_item in contents_l:
        for row_l in row_item(obj, None) if callable(row_item) else [row_item]:
            row_height_l = list()
            for col_item_d in row_l:
                action = col_item_d.get('a')
                col_l = action(obj, col_item_d) if callable(action) else [col_item_d]
                for col_d in col_l:
                    key, buf, buf_item = col_d.get('key', None), None, col_d.get('buf', None)
                    if isinstance(col_item_d.get('rh'), (int, float)):
                        row_height_l.append(col_item_d.get('rh'))
                    if callable(buf_item):
                        buf = buf_item(obj, col_d)
                    elif key is not None:
                        if isinstance(buf_item, dict):
                            buf = buf_item.get(key, None)
                        else:
                            buf = obj.r_get(key)
                    elif isinstance(buf_item, (str, int, float)):
                        buf = buf_item
                    elif buf_item is not None:
                        brcdapi_log.exception('Unexpected type, ' + str(type(buf_item)), echo=False)
                        try:
                            buf = str(type(buf_item))
                        except BaseException as e:
                            brcdapi_log.exception(['Could not convert buf_item to string.', e], echo=True)
                            buf = None  # IDK why it wouldn't be None. This is just to be certain.

                    # Is there any conditional formatting?
                    rule, rule_key = None, None
                    class_type = brcddb_class_util.get_simple_class_type(obj)
                    try:
                        rule_key = col_d.get(_obj_type_to_key_d[class_type])
                    except KeyError:
                        brcdapi_log.exception('Unexpected object type, ' + class_type, echo=True)
                    if isinstance(rule_key, str):
                        rule = Rule(type="expression",
                                    dxf=DifferentialStyle(fill=_yellow_fill, font=_bold_font),
                                    stopIfTrue=True)
                        rule.formula = [rule_key + '>0']

                    # Add the cell contents
                    excel_util.cell_update(
                        sheet,
                        sheet_d['row'],
                        col,
                        buf,
                        font=col_d.get('font'),
                        fill=col_d.get('fill'),
                        align=col_d.get('align'),
                        border=col_d.get('border'),
                        comments=col_d.get('comments'),
                        comment_height=len(col_d.get('comments', list())) + 20,
                        link=col_d.get('link'),
                        cf=rule,
                        dv=col_d.get('dv')
                    )

                    # Merge cells, if necessary
                    span = col_d.get('span', 1)
                    if span > 1:
                        sheet.merge_cells(
                            start_row=sheet_d['row'],
                            start_column=col,
                            end_row=sheet_d['row'],
                            end_column=col + span - 1)
                    col += span

            # Set the row height.
            if len(row_height_l) > 0:
                sheet.row_dimensions[sheet_d['row']].height = max(row_height_l)

            sheet_d['row'], col = sheet_d['row'] + 1, 1


def about_page(wb, sheet_i, sheet_name, file_name, version, description, tc=None):
    """Inserts a standard "About" page in a workbook

    :param wb: Workbook object
    :type wb: class
    :param sheet_i: Sheet index where page is to be placed. Typically, 0. Default is 0
    :type sheet_i: int, None
    :param sheet_name: Sheet (tab) name. If None, the name defaults to "About"
    :type sheet_name: None, str
    :param description: Workbook description. May be a string or list of strings
    :type description: str,list,tuple
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    """
    global _std_font

    # Add an "about" sheet
    sheet = wb.create_sheet(index=sheet_i, title='About' if sheet_name is None else sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.column_dimensions['A'].width = 80

    row = col = 1
    buf_xlate_d = dict(
        script_name=file_name,
        version=version,
        description=description,
        default='',
    )

    # Add link to Table of Contents
    if isinstance(tc, str):
        excel_util.cell_update(sheet, row, col, 'Contents', font=_link_font, link=tc)
        row += 1

    # First portion of the About page
    for d in _about_sheet_l:
        if d is not None:
            buf_l = gen_util.convert_to_list(buf_xlate_d.get(d.get('s', 'default')))
            for buf in buf_l:
                excel_util.cell_update(sheet, row, col, d['t'] + buf, font=d['f'], align=_align_wrap, link=d.get('l'))
                row += 1
        else:
            row += 1

#################################################
#                                               #
#       Methods for determining groups          #
#                                               #
#################################################

def _filter_wwn(proj_obj, filter_val, search):
    """Returns a list of port objects with logins that have WWNs matching the search criteria

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param filter_val: Value from the "Filter" column of the workbook
    :type filter_val: str, None
    :param search: The search type. Value from the "Operator" column of the workbook
    :type search: str, None
    """

    return brcddb_conv.obj_extract(
        brcddb_search.match_test(
            brcddb_conv.obj_extract(proj_obj, 'LoginObj'),
            dict(k='_obj_key', t=search, v=filter_val, i=True)),
        'PortObj')


def _filter_alias(proj_obj, filter_val, search):
    """Returns a list of port objects with logins that have aliases matching the search criteria. See _filter_wwn()"""
    return brcddb_conv.obj_extract(
        brcddb_search.match_test(brcddb_conv.obj_extract(proj_obj, 'AliasObj'),
                                 dict(k='_obj_key', t=search, v=filter_val, i=True)),
        'PortObj'
    )


def _filter_switch_port(proj_obj, filter_val, search):
    """Returns a list of port objects for the switch(es) and port(s) specified in filter_val. See _filter_wwn()"""
    switch_l, rl = list(), list()
    tl = filter_val.split(';') if isinstance(filter_val, str) else list()
    if len(tl) >= 2:
        for switch in tl[0].split(','):
            switch_l.extend([proj_obj.r_switch_obj(switch)] if gen_util.is_wwn(switch)
                            else brcddb_project.switch_obj_for_user_name(proj_obj, switch, match_type=search))
        port_l = brcdapi_port.port_range_to_list(tl[1])
        for switch_obj in switch_l:
            rl.extend([switch_obj.r_port_obj(p) for p in port_l if switch_obj.r_port_obj(p) is not None])
    else:
        brcdapi_log.exception('Invalid filter_val. Type: ' + str(type(filter_val)) + ', Val: ' + str(filter_val),
                              echo=True)

    return rl


def _filter_switch_port_name(proj_obj, filter_val, search):
    """Returns a list of port objects for the switch(es) and port(s) specified in filter_val. See _filter_wwn()"""
    switch_l, rl = list(), list()
    tl = filter_val.split(';') if isinstance(filter_val, str) else list()
    if len(tl) >= 2:
        for switch in tl[0].split(','):
            switch_obj = proj_obj.r_switch_obj(switch) if gen_util.is_wwn(switch) \
                else brcddb_project.switch_obj_for_user_name(proj_obj, switch)
            if switch_obj is None:
                brcdapi_log.log('**ERROR** Switch ' + switch + ' not found', echo=True)
            else:
                switch_l.append(switch_obj)
        for switch_obj in switch_l:
            for name in tl[1].split(','):
                rl.extend(brcddb_port.port_objects_for_name(switch_obj, name, search=search))
    else:
        brcdapi_log.log('**ERROR** Missing port in ' + str(filter_val), echo=True)

    return rl


def _filter_isl(proj_obj, filter_val, search):
    """Returns a dictionary whose key is the ISL group name (switch_x_to_switch_y). The value is a list of port objects
    associated with the ISLs for the pairs. See _filter_wwn()"""
    rd = dict()

    # Figure out all the E-Ports
    e_port_l = [obj for obj in proj_obj.r_port_objects() if obj.r_get(brcdapi_util.fc_port_type_str) == 'e-port']

    # The neighbor is going to be the WWN of the remote port, so build a table of remote ports and the associated switch
    port_to_switch_d = dict()
    for switch_obj in proj_obj.r_switch_objects():
        switch_wwn = switch_obj.r_obj_key()
        for port_wwn in [obj.r_get(brcdapi_util.fc_wwn) for obj in e_port_l]:
            port_to_switch_d[port_wwn] = switch_wwn

    # Figure out groups of ISLs between switches
    isl_group_d = dict()  # Key is switch_name_1_to_switch_name_2. This can break if someone uses duplicate switch names
    for switch_obj in proj_obj.r_switch_objects():
        switch_wwn = switch_obj.r_obj_key()
        for port_obj in e_port_l:
            for remote_port_wwn in port_obj.r_get(brcdapi_util.fc_neighbor_wwn, list()):  # Should always be a list of 1
                temp_l = [switch_wwn, port_to_switch_d[remote_port_wwn]]
                temp_l.sort()  # So that I'm looking at the same ISL pair from either direction.
                group_name = brcddb_switch.best_switch_name(proj_obj.r_switch_obj(temp_l[0])) + '_to_'
                group_name += brcddb_switch.best_switch_name(proj_obj.r_switch_obj(temp_l[1]))
                if group_name not in isl_group_d:
                    isl_group_d[group_name] = list()
                isl_d[group_name].append(port_obj)

    return rd


def _filter_zone(proj_obj, filter_val, search):
    """Returns a list of alias objects in proj_obj. See _filter_wwn()"""
    return brcddb_conv.obj_extract(
        brcddb_search.match_test(
            brcddb_conv.obj_extract(proj_obj, 'ZoneObj'),
            dict(k='_obj_key', t=search, v=filter_val, i=True)),
        'PortObj'
    )


# Valid group filters for processing the groups workbook.
_group_filter_d = {
    'WWN': _filter_wwn,
    'Alias': _filter_alias,
    'switch;port': _filter_switch_port,
    'switch;port_name': _filter_switch_port_name,
    'Zone': _filter_zone,
    'ISL': _filter_isl,
}

def groups(proj_obj, group_file):
    """Parses the group definition file

    The dictionary for each group is as follows:

    +---------------+-------+---------------------------------------------------------------------------------------+
    | Key           | Type  | Description                                                                           |
    +===============+=======+=======================================================================================+
    | group_wwn_d   | dict  | A dictionary of each login for each port in port_obj_l. The key is the login WWN. The |
    |               |       | value is True or False. It is intended to be used as a simple check to determine if a |
    |               |       | login is a member of the group.                                                       |
    +---------------+-------+---------------------------------------------------------------------------------------+
    | port_obj_l    | list  | List of port objects associated with the group.                                       |
    +---------------+-------+---------------------------------------------------------------------------------------+

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param group_file: File name of group definition file, -group.
    :type group_file: str
    :return group_d: Dictionary whose key is the group name and the value is as described in the method header
    :rtype group_d: dict
    :return el: List of str error messages
    :rtype el: list
    """
    global _group_filter_d

    el, group_l, ungrouped_initiator_l, ungrouped_target_l = list(), list(), list(), list()
    grouped_d, group_d = dict(), collections.OrderedDict()
    previous_group_name = None

    # Read the group definition file.
    if group_file is not None:  # Group group_file
        el, worksheet_data_l = excel_util.read_workbook(group_file, dm=3, sheets='parameters', hidden=False)
        if len(el) > 0:
            return group_d, el
        try:
            group_l = worksheet_data_l[0]['al']
            if len(group_l) < 2:
                el.append('No Filters defined in ' + group_file)
                return group_d, el
        except (IndexError, KeyError):
            el.append('"parameters" sheet not found in ' + group_file)
            return group_d, el

    # Determine what's in each group and start building the return dictionary
    if len(group_l) > 0:

        # Find the column headers
        col_d = excel_util.find_headers(group_l[0])
        for key in ('Group', 'Filter', 'Operand', 'Operator'):
            if key not in col_d:
                el.append(key + ' missing in ' + group_file)
        if len(el) > 0:
            return group_d, el
        isl_check_l = (col_d['Group'], col_d['Operand'], col_d['Operator'])
        non_isl_check_l = (col_d['Filter'], col_d['Operand'], col_d['Operator'])
        full_check_l = (col_d['Group'], col_d['Filter'], col_d['Operand'], col_d['Operator'])

        # Figure out what's in each group
        row = 1
        for row_l in group_l[1:]:
            row += 1

            # Validate the row data
            try:
                for i in full_check_l:
                    if row_l[i] is not None:
                        raise Found
                continue  # It's a blank line
            except Found:
                pass

            # If it's an ISL group, everything other than the Filter cell should be empty
            if isinstance(row_l[col_d['Filter']], str) and row_l[col_d['Filter']] == 'ISL':
                group_name = previous_group_name = None
                try:
                    for i in isl_check_l:
                        if row_l[i] is not None:
                            raise Found
                except Found:
                    el.append('Only the Filter cell should contain data when "ISL" is the filter at row ' + str(row))
                    continue

            # If it's not an ISL group, make sure everything is filled out.
            else:
                group_name = previous_group_name if row_l[col_d['Group']] is None else row_l[col_d['Group']].strip()
                previous_group_name = group_name
                if group_name is None:
                    el.append('Cannot determine the group name at row ' + str(row))
                    continue
                try:
                    for i in non_isl_check_l:
                        if not isinstance(row_l[i], str):
                            raise Found
                except Found:
                    el.append('The Filter, Operand, and Operator cells must contain valid data at row ' + str(row))
                    continue

            # The row data is valid if we got this far. Start processing each group
            g_filter = row_l[col_d['Filter']]
            if not isinstance(g_filter, str) or g_filter not in _group_filter_d:
                el.append('Unknown Filter, ' + str(g_filter) + ', at row ' + str(row))
                continue
            operand = row_l[col_d['Operand']]
            if isinstance(operand, str):
                operand = operand.strip()
            processed_row = _group_filter_d[g_filter](proj_obj, operand, row_l[col_d['Operator']])
            if isinstance(processed_row, list):
                sub_group_d = group_d.get(group_name)
                if sub_group_d is None:
                    sub_group_d = dict(group_wwn_d=dict(), port_obj_l=list())
                    group_d[group_name] = sub_group_d
                sub_group_d['port_obj_l'].extend(processed_row)
            else:  # Its an ISL group if we get here.
                for group_name, port_obj_l in processed_row.items():
                    group_d[group_name] = port_obj_l

        # Zone groups are typically used for storage enclosures. It's not uncommon to use standard zones with multiple
        # target WWNs in the same zone. Below probably could have been more efficient. I didn't think of this until
        # after the first test, so I just shoe horned it in. It adds a dictionary of login WWNs that are part of the
        # group. This dictionary is used in the report zone page to skip logins zoned to this group that are already
        # part of the group.
        for sub_group_d in group_d.values():
            for port_obj in sub_group_d['port_obj_l']:
                for wwn in port_obj.r_login_keys():
                    sub_group_d['group_wwn_d'].update({wwn: True})
                # Keep track of ports already grouped:
                grouped_d.update({port_obj.r_switch_key()+port_obj.r_obj_key(): True})

    # Another after thought: find all the logins that are not grouped and get all groups by RNID Sequence number
    # rnid_d: Key is the generic device type. Value is a dict whose key is the sequence number. Value is list of port
    # objects. Sorting by generic device type was done to display groups in order of the device type.
    rnid_d = dict()  # See comment above
    for port_obj in [obj for obj in proj_obj.r_port_objects() if obj.r_is_online()]:

        # Mainframe Groups
        port_rnid_d = port_obj.r_get('rnid')
        if isinstance(port_rnid_d, dict):
            generic_type = brcddb_iocp.generic_device_type(port_rnid_d.get('type-number'))
            port_rnid_seq = port_rnid_d.get('sequence-number', '000000000000')

            # Get the generic device type dictionary from rnid_d. If it hasn't been added yet, add it.
            generic_type_d = rnid_d.get(generic_type)
            if not isinstance(generic_type_d, dict):
                generic_type_d = dict()
                rnid_d.update({generic_type: generic_type_d})

            # Get the port object list for this sequence number
            port_obj_l = generic_type_d.get(port_rnid_seq)
            if not isinstance(port_obj_l, list):
                port_obj_l = list()
                generic_type_d.update({port_rnid_seq: port_obj_l})

            # Add the port object
            port_obj_l.append(port_obj)

        # Determine what hasn't been grouped. This is just for displaying helpful information in reports
        elif not bool(grouped_d.get(port_obj.r_switch_key()+port_obj.r_obj_key())):
            login_obj_l = port_obj.r_login_objects()
            if len(login_obj_l) > 0:
                fc4_features = login_obj_l[0].r_get(brcdapi_util.bns_fc4_features)
                if isinstance(fc4_features, str):
                    if 'initiator' in fc4_features.lower():
                        ungrouped_initiator_l.append(port_obj)
                    else:
                        ungrouped_target_l.append(port_obj)

    # Sort out the mainframe groups in order of storage followed by CHPID
    for key in ('DASD', 'Tape', 'CUP', 'CTC', 'Switch', 'IDG', 'Test', 'UNKN', 'CPU'):
        for sub_key, port_obj_l in rnid_d.get(key, dict()).items():
            if len(port_obj_l) > 0:
                group_d[key + '_' + sub_key] = dict(mf_group=key, port_obj_l=port_obj_l)

    # Are there any missing CPUs?
    missing_cpu_l, missing_cpu_d = list(), dict()
    for port_obj in proj_obj.r_port_objects():
        port_rnid_d = port_obj.r_get('rnid')
        if isinstance(port_rnid_d, dict):
            if brcddb_iocp.generic_device_type(port_rnid_d.get('type-number')) == 'CPU':
                sn = port_rnid_d.get('sequence-number', '').upper()
                if sn not in rnid_d.get('CPU', list()) and sn not in missing_cpu_d:
                    missing_cpu_d[sn] = True
                    missing_cpu_l.append(port_obj)

    group_d[zone_report.UNGROUPED_TARGET] = dict(port_obj_l=ungrouped_target_l)
    group_d[zone_report.UNGROUPED_INITIATOR] = dict(port_obj_l=ungrouped_initiator_l)
    group_d[zone_report.MISSING_CPU] = dict(port_obj_l=missing_cpu_l)

    return group_d, el
