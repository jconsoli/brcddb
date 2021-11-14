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
mod:`brcddb.report.bp` - Best practice violations

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
    | 3.0.3     | 14 May 2021   | Removed the shebang line                                                          |
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

import openpyxl.utils.cell as xl
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.classes.alert as al
import brcdapi.log as brcdapi_log
import brcddb.brcddb_port as brcddb_port


def _add_alerts(obj, type, sev, area_1, area_2):
    return [[type, al_obj.fmt_sev(), area_1, area_2, al_obj.fmt_msg()] for al_obj in obj.r_alert_objects() if \
            al_obj.sev() == sev]


##################################################################
#
#        Best practice case statements in bp_page()
#
###################################################################
def type_case(a_list):
    """Returns the type value

    :param a_list: List of alert parameters as returned from _add_alerts()
    :type a_list: list
    :return: Value for element 0 (Type)
    :rtype: str
    """
    return a_list[0]


def sev_case(a_list):
    """Returns the type value

    :param a_list: List of alert parameters as returned from _add_alerts()
    :type a_list: list
    :return: Value for element 1 (Sev)
    :rtype: str
    """
    return a_list[1]


def area_1_case(a_list):
    """Returns the type value

    :param a_list: List of alert parameters as returned from _add_alerts()
    :type a_list: list
    :return: Value for element 2 (Area_1)
    :rtype: str
    """
    return a_list[2]


def area_2_case(a_list):
    """Returns the type value

    :param a_list: List of alert parameters as returned from _add_alerts()
    :type a_list: list
    :return: Value for element 3 (Area_2)
    :rtype: str
    """
    return a_list[3]


def desc_case(a_list):
    """Returns the type value

    :param a_list: List of alert parameters as returned from _add_alerts()
    :type a_list: list
    :return: Value for element 4 (Type)
    :rtype: str
    """
    return a_list[4]


bp_case = {
    '_TYPE': type_case,
    '_SEV': sev_case,
    '_AREA_1': area_1_case,
    '_AREA_2': area_2_case,
    '_DESCRIPTION': desc_case,
}


def bp_page(wb, tc, sheet_name, sheet_i, sheet_title, obj, display, display_tbl):
    """Creates a best practice violation worksheet for the Excel report.

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
    :param obj: Project or fabric object.
    :type obj: brcddb.classes.project.ProjectObj, brcddb.classes.fabric.FabricObj
    :param display: List of parameters to display.
    :type display: list, tuple
    :param display_tbl: Display control table. See brcddb.report.report_tables.display_tbl
    :rtype: None
    """
    # Validate the user input
    err_msg = list()
    if obj is None:
        err_msg.append('obj was not defined.')
    elif not bool('ProjectObj' in str(type(obj)) or 'FabricObj' in str(type(obj))):
        err_msg.append('Invalid object type: ' + str(type(obj)) + '.')
    if display is None:
        err_msg.append('display not defined.')
    if len(err_msg) > 0:
        brcdapi_log.exception(err_msg, True)
        return

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    col = 1
    row = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell] = sheet_title
    sheet.freeze_panes = sheet['A3']
    col = 1
    row += 1
    for k in display:
        if k in display_tbl and 'dc' in display_tbl[k] and display_tbl[k]['dc'] is True:
            continue
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = report_fonts.font_type('bold')
        sheet[cell].border = report_fonts.border_type('thin')
        if k in display_tbl:
            if 'c' in display_tbl[k]:
                sheet.column_dimensions[xl.get_column_letter(col)].width = display_tbl[k]['c']
            try:
                if display_tbl[k]['v']:
                    sheet[cell].alignment = report_fonts.align_type('wrap_vert_center')
                else:
                    sheet[cell].alignment = report_fonts.align_type('wrap')
            except:
                sheet[cell].alignment = report_fonts.align_type('wrap')
            if 'd' in display_tbl[k]:
                sheet[cell] = display_tbl[k]['d']
            else:
                sheet[cell] = k  # This happens when a new key is introduced before the display tables have been updated
        else:
            sheet[cell] = k  # This happens when a new key is introduced before the display tables have been updated
        col += 1

    # Get a list of fabric objects and initialize alert_list
    if 'ProjectObj' in str(type(obj)):
        fab_list = obj.r_fabric_objects()
        chassis_list = obj.r_chassis_objects()
        switch_list = obj.r_switch_objects()
    else:
        fab_list = [obj]
        chassis_list = obj.r_project_obj().r_chassis_objects()
        switch_list = obj.r_project_obj().r_switch_objects()
    alert_list = list()

    # Get all the chassis alerts
    for tobj in chassis_list:
        tl = list()
        for sev in (al.ALERT_SEV.ERROR, al.ALERT_SEV.WARN):  # Display errors first
            tl.extend(_add_alerts(tobj, 'Chassis', sev, brcddb_chassis.best_chassis_name(tobj), ''))
        if len(tl) > 0:
            alert_list.append([''])
            alert_list.append(['Chassis: ' + brcddb_chassis.best_chassis_name(tobj)])
            alert_list.extend(tl)

    # Get all the fabric alerts
    for fab_obj in fab_list:
        tl = list()
        for sev in (al.ALERT_SEV.ERROR, al.ALERT_SEV.WARN):  # Display errors first
            tl.extend(_add_alerts(fab_obj, 'Fabric', sev, brcddb_fabric.best_fab_name(fab_obj), ''))
            for tobj in fab_obj.r_zonecfg_objects():
                tl.extend(_add_alerts(tobj, 'ZoneCfg', sev, tobj.r_obj_key(), ''))
            for tobj in fab_obj.r_zone_objects():
                tl.extend(_add_alerts(tobj, 'Zone', sev, tobj.r_obj_key(), ''))
            for tobj in fab_obj.r_alias_objects():
                tl.extend(_add_alerts(tobj, 'Alias', sev, tobj.r_obj_key(), ''))
            for tobj in fab_obj.r_login_objects():
                tl.extend(_add_alerts(tobj, 'Login', sev, tobj.r_obj_key(), ''))
            for tobj in fab_obj.r_fdmi_node_objects():
                tl.extend(_add_alerts(tobj, 'FDMI_Node', sev, tobj.r_obj_key(), ''))
            for tobj in fab_obj.r_fdmi_port_objects():
                tl.extend(_add_alerts(tobj, 'FDMI_Port', sev, tobj.r_obj_key(), ''))
        if len(tl) > 0:
            alert_list.append([''])
            alert_list.append(['Fabric: ' + brcddb_fabric.best_fab_name(fab_obj, True)])
            alert_list.extend(tl)

    # Get all the switch and port alerts
    for switch_obj in switch_list:
        tl = list()
        for sev in (al.ALERT_SEV.ERROR, al.ALERT_SEV.WARN):  # Display errors first
            tl.extend(_add_alerts(switch_obj, 'Switch', sev, brcddb_switch.best_switch_name(switch_obj), ''))
            for tobj in switch_obj.r_port_objects():
                tl.extend(_add_alerts(tobj, 'Port', sev, brcddb_port.best_port_name(tobj), tobj.r_obj_key()))
        if len(tl) > 0:
            alert_list.append([''])
            alert_list.append(['Switch: ' + brcddb_switch.best_switch_name(switch_obj, True)])
            alert_list.extend(tl)


    # Now add the alerts to the worksheet

    # Set up the cell formatting
    border = report_fonts.border_type('thin')
    alignment = report_fonts.align_type('wrap')
    font = report_fonts.font_type('std')

    # Add all alerts to the worksheet
    for x in alert_list:
        row += 1
        col = 1
        if len(x) == 0:
            row += 1
        elif len(x) == 1:
            sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(display))
            cell = xl.get_column_letter(col) + str(row)
            sheet[cell].font = report_fonts.font_type('hdr_2')
            if len(x[0]) > 0:
                sheet[cell].fill = report_fonts.fill_type('lightblue')
            sheet[cell] = x[0]
        else:
            for k in display:
                cell = xl.get_column_letter(col) + str(row)
                sheet[cell].border = border
                sheet[cell].font = font
                sheet[cell].alignment = alignment
                sheet[cell] = bp_case[k](x)
                col += 1
