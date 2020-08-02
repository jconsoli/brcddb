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
:mod:`brcddb.apps.report` - Creates a report in Excel Workbook format from a brcddb project

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | Added the IOCP Page                                                               |
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
import brcddb.app_data.report_tables as rt
import brcddb.brcddb_project as brcddb_project
import brcdapi.log as brcdapi_log
import brcddb.util.search as brcddb_search
import brcddb.util.util as brcddb_util
import brcddb.report.utils as report_utils
import brcddb.report.port as report_port
import brcddb.report.chassis as report_chassis
import brcddb.report.fabric as report_fabric
import brcddb.report.switch as report_switch
import brcddb.report.zone as report_zone
import brcddb.report.login as report_login
import brcddb.report.bp as report_bp
import brcddb.report.iocp as report_iocp
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_fabric as brcddb_fabric

_ADD_PROJ_DASHBOARD = True  # Set True to add the project dashboard page
_ADD_CHASSIS = True  # Set True to add the chassis page
_ADD_FABRIC_SUMMARY = True  # Set True to add the fabric summary page
_ADD_FABRIC_DASHBOARD = True  # Set True to add the fabric dashboard
_ADD_SWITCH_PAGE = True  # Set True to add the switch page
_ADD_PORT_PAGE = True  # Set True to add the port page
_ADD_ZONE_PAGE = True  # Set True to add the zone analysis page
_ADD_ALIAS_PAGE = True  # Set True to add the alias detail page
_ADD_LOGIN_PAGE = True  # Set True to add the login page
_ADD_BP_SUMMARY = True  # Add a best practice (really an alert) summary page
_ADD_IOCP_PAGE = True  # Add the IOCP

_MAX_DB_SIZE = 10   # Set the top xx dashboard size

dup_login_tbl = (
    'port-name',
    '_ALIAS',
    '_FABRIC_NAME',
    '_SWITCH_NAME',
    '_PORT_NUMBER',
    'port-id',
    '_ZONES_DEF',
    'fc4-features',
    'link-speed',
    'name-server-device-type',
    'node-name',
    'node-symbolic-name',
    'port-symbolic-name',
)


def proj_title_page(proj_obj, tc, wb, sheet_index, sheet_name, sheet_title, contents):
    """Creates the project title page
    
    :param proj_obj: Project object
    :type proj_obj: ProjectObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: dict
    :param sheet_index: Location for the title page. First sheet is 0
    :type sheet_index: int
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_title: Title for sheet
    :type sheet_title: str
    :param contents: List of objects {'s': sheet name, 'd': reference name (individual sheet titles)}
    :rtype: None
    """
    t_content = [{'new_row': False, 'merge': 2, 'font': 'std', 'align': 'wrap', 'disp': 'Description'},
                 {'font': 'std', 'align': 'wrap', 'disp': proj_obj.c_description()},
                 {'new_row': False, 'merge': 2, 'font': 'std', 'align': 'wrap', 'disp': 'Data collected'},
                 {'font': 'std', 'align': 'wrap', 'disp': proj_obj.r_date()}]

    # Add the table  of contents
    for obj in contents:
        if obj.get('h') is not None and obj.get('h') is True:
            t_content.append({})
            t_content.append({'merge': 3, 'font': 'hdr_2', 'align': 'wrap', 'disp': obj.get('d')})
        elif obj.get('s') is not None:
            t_content.append({'new_row': False, 'disp': ''})  # First column is blank
            t_content.append({'merge': 2, 'font': 'link', 'align': 'wrap', 'disp': obj.get('d'),
                              'hyper': '#'+obj.get('s')+'!A1'})
        else:
            buf = obj.get('font') if 'font' in obj else 'std'
            t_content.append({'merge': 2, 'font': buf, 'align': 'wrap', 'disp': obj.get('d')})

    report_utils.title_page(wb, tc, sheet_name, sheet_index, sheet_title, t_content, (4, 20, 62))


def dashboard(obj, tc, wb, sheet_index, sheet_name, title):
    """Creates a dashboard of ports with the top _MAX_DB_SIZE highest counters.
    
    :param obj: Project, fabric, or switch object
    :type obj: ProjectObj, SwitchObj, FabricObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: dict
    :param sheet_index: Location for the title page. First sheet is 0
    :type sheet_index: int
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param title: Title at top of  sheet
    :type title: str
    :rtype: None
    """
    dashboard_item = collections.OrderedDict()
    dashboard_item['bad-eofs-received'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' Bad EOF', 'port_list': []}
    dashboard_item['class-3-discards'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' C3 Discards', 'port_list': []}
    dashboard_item['in-crc-errors'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' CRC With Good EOF', 'port_list': []}
    dashboard_item['crc-errors'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' CRC', 'port_list': []}
    dashboard_item['loss-of-signal'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' Loss of Signal', 'port_list': []}
    dashboard_item['bb-credit-zero'] = {'title': 'Top ' + str(_MAX_DB_SIZE) + ' BB Credit Zero', 'port_list': []}
    port_list = obj.r_port_objects()
    for k in dashboard_item.keys():
        db = dashboard_item.get(k)
        db_list = brcddb_search.test_threshold(port_list, 'fibrechannel-statistics/' + k, '>', 0)
        db_list = brcddb_util.sort_obj_num(db_list, 'fibrechannel-statistics/' + k, True)
        if len(db_list) > _MAX_DB_SIZE:
            del db_list[_MAX_DB_SIZE:]
        db['port_list'].extend(db_list)
    report_port.performance_dashboard(wb, tc, sheet_name=sheet_name, sheet_i=sheet_index, sheet_title=title,
                                        content=dashboard_item)


def report(proj_obj, outf):
    """Creates an Excel report. Sort of a SAN Health like report.

    :param proj_obj: The project object
    :type proj_obj: brcddb.classes.ProjectObj
    :param outf: Output file name
    :type outf: str
    """
    port_pages = [
        {'s': '_config', 't': rt.Port.port_config_tbl, 'd': 'Port Configurations', 'l': False},
        {'s': '_stats', 't': rt.Port.port_stats_tbl, 'd': 'Port Statistics', 'l': False},
        {'s': '_zl', 't': rt.Port.port_zone_tbl, 'd': 'Ports by Zone and Login', 'l': True},
        {'s': '_sfp', 't': rt.Port.port_sfp_tbl, 'd': 'SFP report', 'l': False},
        {'s': '_ficon', 't': rt.Port.port_rnid_tbl, 'd': 'FICON RNID report', 'l': False},
    ]

    tc_page = proj_obj.r_obj_key()  # Just to save some typing
    tbl_contents = []

    # Set up the workbook
    sheet_index = 0
    wb = report_utils.new_report()

    # Check project for duplicate WWNs
    tbl_contents.append({'h': True, 'd': 'Duplicate WWNs'})
    wl = brcddb_project.dup_wwn(proj_obj)
    if len(wl) > 0:
        sname = 'dup_wwns'
        report_login.login_page(wb, tc_page, sname, sheet_index, 'Duplicate WWNs', wl, dup_login_tbl,
                                rt.Login.login_display_tbl, False)
        tbl_contents.append({'s': sname, 'd': 'Duplicate WWNs'})
        sheet_index += 1
    else:
        tbl_contents.append({'d': 'No Duplicate WWNs Found'})

    # Project dashboard
    if _ADD_PROJ_DASHBOARD:
        tbl_contents.append({'h': True, 'd': 'Project Links'})
        sname = 'proj_dashboard'
        title = 'Project Dashboard'
        dashboard(proj_obj, tc_page, wb, sheet_index, sname, title)
        tbl_contents.append({'s': sname, 'd': title})
        sheet_index += 1

    # Add all the chassis
    if _ADD_CHASSIS:
        tbl_contents.append({'h': True, 'd': 'Chassis'})
        for chassis_obj in proj_obj.r_chassis_objects():
            chassis_name = brcddb_chassis.best_chassis_name(chassis_obj)
            brcdapi_log.log('Processing chassis: ' + chassis_name, True)
            sname = chassis_name.replace(' ', '_').replace(':', '').replace('-', '_')[:22] + '_' + str(sheet_index) + \
                    '_' + str(sheet_index)
            report_chassis.chassis_page(wb, tc_page, sname, sheet_index, 'Chassis Detail For: ' + chassis_name,
                                        chassis_obj, rt.Chassis.chassis_display_tbl)
            tbl_contents.append({'s': sname, 'd': chassis_name})
            sheet_index += 1

    # Add all the fabrics
    for fab_obj in proj_obj.r_fabric_objects():
        fab_name = brcddb_fabric.best_fab_name(fab_obj)
        brcdapi_log.log('Processing fabric: ' + fab_name, True)
        tbl_contents.append({'h': True, 'd': fab_name})
        prefix = fab_name.replace(' ', '_').replace(':', '').replace('-', '_')[:22] + '_' + str(sheet_index)

        # Fabric summary page
        if _ADD_FABRIC_SUMMARY:
            brcdapi_log.log('    Building fabric summary page', True)
            sname = prefix + '_sum'
            report_fabric.fabric_page(wb, tc_page, sheet_index, sname, fab_name + ' Summary', fab_obj)
            tbl_contents.append({'s': sname, 'd': 'Fabric Summary'})
            sheet_index += 1

        # Fabric Dashboard
        if _ADD_FABRIC_DASHBOARD:
            brcdapi_log.log('    Building fabric dashboard', True)
            sname = prefix + '_db'
            dashboard(fab_obj, tc_page, wb, sheet_index, sname, fab_name + ' Dasboard')
            tbl_contents.append({'s': sname, 'd': 'Fabric Dashboard'})
            sheet_index += 1

        # Switch page
        if _ADD_SWITCH_PAGE:
            brcdapi_log.log('    Building switch detail page', True)
            sname = prefix + '_switch'
            report_switch.switch_page(wb, tc_page, sname, sheet_index, 'Switch Detail For Fabric: ' + fab_name,
                                      fab_obj.r_switch_objects(), rt.Switch.switch_display_tbl)
            tbl_contents.append({'s': sname, 'd': 'Switch Detail'})
            sheet_index += 1

        # Now the port pages
        if _ADD_PORT_PAGE:
            brcdapi_log.log('    Building the port pages', True)
            port_list = brcddb_util.sort_ports(fab_obj.r_port_objects())
            for obj in port_pages:
                sname = prefix + obj.get('s')
                report_port.port_page(wb, tc_page, sname, sheet_index, fab_name + ' ' + obj.get('d'), port_list,
                                      obj.get('t'), rt.Port.port_display_tbl, obj.get('l'))
                tbl_contents.append({'s': sname, 'd': obj.get('d')})
                sheet_index += 1

        #  Zone Analysis Page
        if _ADD_ZONE_PAGE:
            brcdapi_log.log('    Building zone analysis page', True)
            sname = prefix + '_zone'
            report_zone.zone_page(fab_obj, tc_page, wb, sname, sheet_index, fab_name + ' Zone Analysis')
            tbl_contents.append({'s': sname, 'd': 'Zone Analysis'})
            sheet_index += 1

        #  Alias Page
        if _ADD_ALIAS_PAGE:
            brcdapi_log.log('    Building alias page', True)
            sname = prefix + '_alias'
            report_zone.alias_page(fab_obj, tc_page, wb, sname, sheet_index, fab_name + ' Alias Detail')
            tbl_contents.append({'s': sname, 'd': 'Alias Detail'})
            sheet_index += 1

        #  Login Page
        if _ADD_LOGIN_PAGE:
            brcdapi_log.log('    Building login page', True)
            sname = prefix + '_login'
            report_login.login_page(wb, tc_page, sname, sheet_index, fab_name + ' Logins', fab_obj.r_login_objects(),
                                    rt.Login.login_tbl, rt.Login.login_display_tbl, True)
            tbl_contents.append({'s': sname, 'd': 'Logins'})
            sheet_index += 1

    #  IOCP Page
    if _ADD_IOCP_PAGE:
        iocp_objects = proj_obj.r_iocp_objects()
        if len(iocp_objects) > 0:
            brcdapi_log.log('Adding the IOCP pages', True)
            tbl_contents.append({'h': True, 'd': 'IOCPs'})
            for iocp_obj in iocp_objects:
                sname = iocp_obj.r_obj_key()
                report_iocp.iocp_page(iocp_obj, tc_page, wb, sname, sheet_index, sname)
                tbl_contents.append({'s': sname, 'd': sname})
                sheet_index += 1

    # Add the Best Practice page
    if _ADD_BP_SUMMARY:
        sname = 'Best_Practice'
        fab_name = 'Best Practice Violations'  # Just borrowing fab_name for the title
        report_bp.bp_page(wb, tc_page, sname, 0, fab_name, proj_obj, rt.BestPractice.bp_tbl,
                          rt.BestPractice.bp_display_tbl)
        tbl_contents.insert(0, {'s': sname, 'd': fab_name})
        tbl_contents.insert(0, {'h': True, 'd': fab_name})

    # Insert the title & contents page
    proj_title_page(proj_obj, None, wb, 0, tc_page, 'Contents', contents=tbl_contents)

    # Save the report.
    report_utils.save_report(wb, outf)