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
    | 3.0.2     | 02 Sep 2020   | Added the ability to customize the report                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 29 Sep 2020   | used brcddb.report.utils.valid_sheet_name for uniform sheet name conventions.     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 31 Dec 2020   | Added summary of chassis not included in audit.                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '31 Dec 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

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
import brcddb.brcddb_switch as brcddb_switch

_report_pages = dict(
    proj_dashboard=dict(s=True, d='Project dashboard page'),
    chassis=dict(s=True, d='Chassis page'),
    fabric_summary=dict(s=True, d='Fabric summary page'),
    fabric_dashboard=dict(s=True, d='Fabric dashboard'),
    switch=dict(s=True, d='Switch page'),
    port_config=dict(s=True, d='Port configuration page'),
    port_config_error=dict(s=False, d='Port configuration alert summary page. Not yet implemented.'),
    port_stats=dict(s=True, d='Port statistics page'),
    port_stats_error=dict(s=False, d='Port statistics alert summary page. Not yet implemented.'),
    port_zone=dict(s=True, d='Port by login, alias and zone page'),
    port_zone_error=dict(s=False, d='Port zone/login alert summary page. Not yet implemented.'),
    port_sfp=dict(s=True, d='Port SFP page'),
    port_sfp_error=dict(s=False, d='Port SFP alert summary page. Not yet implemented.'),
    port_rnid=dict(s=False, d='Port RNID page. Typically only used for FICON'),
    port_rnid_error=dict(s=False, d='Port RNID alert summary page. Not yet implemented.'),
    zone_page=dict(s=True, d='Zone analysis page'),
    zone_error=dict(s=False, d='Alias alert summary page. Not yet implemented.'),
    alias=dict(s=True, d='Alias detail page'),
    alias_error=dict(s=False, d='Alias alert summary page. Not yet implemented.'),
    login=dict(s=True, d='Login page'),
    login_error=dict(s=False, d='Login alert summary page. Not yet implemented.'),
    bp=dict(s=True, d='Project wide best practice alert summary page'),
    iocp=dict(s=True, d='IOCP page. Only added if IOCPs were added. FICON only.'),
)

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
    t_content = [dict(new_row=False, merge=2, font='std', align='wrap', disp='Description'),
                 dict(font='std', align='wrap', disp=proj_obj.c_description()),
                 dict(new_row=False, merge=2, font='std', align='wrap', disp='Data collected'),
                 dict(font='std', align='wrap', disp=proj_obj.r_date())]

    # Add the table  of contents
    for obj in contents:
        m = 3  # Number of cells to merge
        if obj.get('h') is not None and obj.get('h') is True:
            t_content.append(dict())
            t_content.append(dict(merge=m, font='hdr_2', align='wrap', disp=obj.get('d')))
            continue
        if obj.get('sc') is not None:
            for i in range(0, obj.get('sc')):
                t_content.append(dict(new_row=False, disp=''))  # Column is blank
                m -= 1
        if obj.get('s') is not None:
            t_content.append(dict(merge=m, font='link', align='wrap', disp=obj.get('d'), hyper='#'+obj.get('s')+'!A1'))
        else:
            buf = obj.get('font') if 'font' in obj else 'std'
            t_content.append(dict(merge=m, font=buf, align='wrap', disp=obj.get('d')))

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
    dashboard_item['bad-eofs-received'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' Bad EOF', port_list=list())
    dashboard_item['class-3-discards'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' C3 Discards', port_list=list())
    dashboard_item['in-crc-errors'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' CRC With Good EOF', port_list=list())
    dashboard_item['crc-errors'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' CRC', port_list=list())
    dashboard_item['loss-of-signal'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' Loss of Signal', port_list=list())
    dashboard_item['bb-credit-zero'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' BB Credit Zero', port_list=list())
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


def report_pages(remove_pages, add_pages):
    """Use to modify the default pages for the report

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
    dashboard_item['bad-eofs-received'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' Bad EOF', port_list=list())
    dashboard_item['class-3-discards'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' C3 Discards', port_list=list())
    dashboard_item['in-crc-errors'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' CRC With Good EOF', port_list=list())
    dashboard_item['crc-errors'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' CRC', port_list=list())
    dashboard_item['loss-of-signal'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' Loss of Signal', port_list=list())
    dashboard_item['bb-credit-zero'] = dict(title='Top ' + str(_MAX_DB_SIZE) + ' BB Credit Zero', port_list=list())
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


def customize_help():
    """Returns a list of help messages for remove_pages and add_pages parameters in report()

    :return: List of help messages
    :rtype: list
    """
    # Figure out which key is the longest
    lkey = 0
    for k in _report_pages.keys():
        lkey = max(lkey, len(k))
    lkey += 2

    # Format the help messages
    rl = list('\n')
    for k, v in _report_pages.items():
        key = k
        while len(key) < lkey:
            key += ' '
        default_value = 'Default      ' if v['s'] else 'Not default  '
        rl.append(key + default_value + v['d'])
    rl.append('\n')

    return rl


def report(proj_obj, outf, remove_pages=None, add_pages=None):
    """Creates an Excel report. Sort of a SAN Health like report.

    :param proj_obj: The project object
    :type proj_obj: brcddb.classes.ProjectObj
    :param outf: Output file name
    :type outf: str
    :param remove_pages: List of default pages to remove. Done first so you can clear all then add pages.
    :type remove_pages: None, str, list
    :param add_pages: Pages, in addition to the defaults, to add to the report
    :type add_pages: None, str, list
    """

    # Figure out what pages to include in the report
    for key in brcddb_util.convert_to_list(remove_pages):
        d = _report_pages.get(key)
        if d is None:
            if key == 'all':
                for obj in _report_pages.values():
                    obj['s'] = False
                break
            else:
                brcdapi_log.log(key + ' is unkonwn in remove page list. ignored')
        else:
            d['s'] = False
    for key in brcddb_util.convert_to_list(add_pages):
        d = _report_pages.get(key)
        if d is None:
            if key == 'all':
                for obj in _report_pages.values():
                    obj['s'] = True
                break
            else:
                brcdapi_log.log(key + ' is unkonwn in add page list. ignored')
        else:
            d['s'] = True


    """port_pages is used to determine how to display pages
    +-------+-------------------------------------------------------------------------------+
    |  key  | Description                                                                   |
    +=======+===============================================================================+
    |   c   | Key in the _report_pages table                                                |
    +-------+-------------------------------------------------------------------------------+
    |   s   | Sheet name prefix                                                             |
    +-------+-------------------------------------------------------------------------------+
    |  sc   | Number of columns to skip                                                     |
    +-------+-------------------------------------------------------------------------------+
    |   t   | The table used to control how the port data is displayed.                     |
    +-------+-------------------------------------------------------------------------------+
    |   d   | Text to display as a header on the worksheet.                                 |
    +-------+-------------------------------------------------------------------------------+
    |   l   | When true, displays all the logins. Otherwise, just the base WWN is reported. |
    +-------+-------------------------------------------------------------------------------+
    """
    port_pages = [
        dict(c='port_config', sc=1, s='_config', t=rt.Port.port_config_tbl, d='Port Configurations', l=False),
        dict(c='port_config_error', sc=1, s='_config_error', t=rt.Port.port_config_tbl, d='Port Configurations Error Summary',
             l=False),
        dict(c='port_stats', sc=1, s='_stats', t=rt.Port.port_stats_tbl, d='Port Statistics', l=False),
        dict(c='port_stats_error', sc=1, s='_stats_error', t=rt.Port.port_stats_tbl, d='Port Statistics Error Summary',
             l=False),
        dict(c='port_zone', sc=1, s='_zl', t=rt.Port.port_zone_tbl, d='Ports by Zone and Login', l=True),
        dict(c='port_zone_error', sc=1, s='_zl_error', t=rt.Port.port_zone_tbl, d='Ports by Zone and Login Error Summary',
             l=True),
        dict(c='port_sfp', sc=1, s='_sfp', t=rt.Port.port_sfp_tbl, d='SFP report', l=False),
        dict(c='port_sfp_error', sc=1, s='_sfp_error', t=rt.Port.port_sfp_tbl, d='SFP Error Summary', l=False),
        dict(c='port_rnid', sc=1, s='_ficon', t=rt.Port.port_rnid_tbl, d='Port RNID data', l=False),
    ]

    tc_page = proj_obj.r_obj_key()  # Just to save some typing
    tbl_contents = list()

    # Set up the workbook
    sheet_index = 0
    wb = report_utils.new_report()

    # Check project for duplicate WWNs
    tbl_contents.append(dict(h=True, d='Duplicate WWNs'))
    wl = brcddb_project.dup_wwn(proj_obj)
    if len(wl) > 0:
        sname = 'dup_wwns'
        report_login.login_page(wb, tc_page, sname, sheet_index, 'Duplicate WWNs', wl, dup_login_tbl,
                                rt.Login.login_display_tbl, False)
        tbl_contents.append(dict(sc=1, s=sname, d='Duplicate WWNs'))
        sheet_index += 1
    else:
        tbl_contents.append(dict(sc=1, d='No Duplicate WWNs Found'))

    # Project dashboard
    if _report_pages['proj_dashboard']['s']:
        tbl_contents.append(dict(h=True, d='Project Links'))
        sname = 'proj_dashboard'
        title = 'Project Dashboard'
        dashboard(proj_obj, tc_page, wb, sheet_index, sname, title)
        tbl_contents.append(dict(sc=1, s=sname, d=title))
        sheet_index += 1

    # Add all the chassis
    if _report_pages['chassis']['s']:
        tbl_contents.append(dict(h=True, d='Chassis'))
        for chassis_obj in proj_obj.r_chassis_objects():
            chassis_name = brcddb_chassis.best_chassis_name(chassis_obj)
            brcdapi_log.log('Processing chassis: ' + chassis_name, True)
            sname = report_utils.valid_sheet_name.sub('', chassis_name.replace(' ', '_'))[:22] + '_' + str(sheet_index)
            report_chassis.chassis_page(wb, tc_page, sname, sheet_index, 'Chassis Detail For: ' + chassis_name,
                                        chassis_obj, rt.Chassis.chassis_display_tbl)
            tbl_contents.append(dict(sc=1, s=sname, d=chassis_name))
            sheet_index += 1

    # Add all the fabrics
    for fab_obj in proj_obj.r_fabric_objects():
        fab_name = brcddb_fabric.best_fab_name(fab_obj)
        brcdapi_log.log('Processing fabric: ' + fab_name, True)
        tbl_contents.append(dict(h=True, d=fab_name))
        prefix = report_utils.valid_sheet_name.sub('', fab_name.replace(' ', '_'))[:22] + '_' + str(sheet_index)

        # Fabric summary page
        if _report_pages['fabric_summary']['s']:
            brcdapi_log.log('    Building fabric summary page', True)
            sname = prefix + '_sum'
            report_fabric.fabric_page(wb, tc_page, sheet_index, sname, fab_name + ' Summary', fab_obj)
            tbl_contents.append(dict(sc=1, s=sname, d='Fabric Summary'))
            sheet_index += 1

        # Fabric Dashboard
        if _report_pages['fabric_dashboard']['s']:
            brcdapi_log.log('    Building fabric dashboard', True)
            sname = prefix + '_db'
            dashboard(fab_obj, tc_page, wb, sheet_index, sname, fab_name + ' Dasboard')
            tbl_contents.append(dict(sc=1, s=sname, d='Fabric Dashboard'))
            sheet_index += 1

        # Switch page
        if _report_pages['switch']['s']:
            brcdapi_log.log('    Building switch detail page', True)
            sname = prefix + '_switch'
            report_switch.switch_page(wb, tc_page, sname, sheet_index, 'Switch Detail For Fabric: ' + fab_name,
                                      fab_obj.r_switch_objects(), rt.Switch.switch_display_tbl)
            tbl_contents.append(dict(sc=1, s=sname, d='Switch Detail'))
            sheet_index += 1

        # Now the port pages
        brcdapi_log.log('    Building the port pages', True)
        port_list = brcddb_util.sort_ports(fab_obj.r_port_objects())
        for obj in port_pages:
            if _report_pages[obj['c']]['s']:
                sname = prefix + obj.get('s')
                report_port.port_page(wb, tc_page, sname, sheet_index, fab_name + ' ' + obj.get('d'), port_list,
                obj.get('t'), rt.Port.port_display_tbl, obj.get('l'))
                tbl_contents.append(dict(sc=1, s=sname, d=obj.get('d')))
                sheet_index += 1

        #  Zone Analysis Page
        if _report_pages['zone_page']['s']:
            brcdapi_log.log('    Building zone analysis page', True)
            sname = prefix + '_zone'
            report_zone.zone_page(fab_obj, tc_page, wb, sname, sheet_index, fab_name + ' Zone Analysis')
            tbl_contents.append(dict(sc=1, s=sname, d='Zone Analysis'))
            sheet_index += 1

        #  Alias Page
        if _report_pages['alias']['s']:
            brcdapi_log.log('    Building alias page', True)
            sname = prefix + '_alias'
            report_zone.alias_page(fab_obj, tc_page, wb, sname, sheet_index, fab_name + ' Alias Detail')
            tbl_contents.append(dict(sc=1, s=sname, d='Alias Detail'))
            sheet_index += 1

        #  Login Page
        if _report_pages['login']['s']:
            brcdapi_log.log('    Building login page', True)
            sname = prefix + '_login'
            report_login.login_page(wb, tc_page, sname, sheet_index, fab_name + ' Logins', fab_obj.r_login_objects(),
                                    rt.Login.login_tbl, rt.Login.login_display_tbl, True)
            tbl_contents.append(dict(sc=1, s=sname, d='Logins'))
            sheet_index += 1

    #  IOCP Page
    if _report_pages['iocp']['s']:
        iocp_objects = proj_obj.r_iocp_objects()
        if len(iocp_objects) > 0:
            brcdapi_log.log('Adding the IOCP pages', True)
            tbl_contents.append(dict(h=True, d='IOCPs'))
            for iocp_obj in iocp_objects:
                sname = report_utils.valid_sheet_name.sub('', iocp_obj.r_obj_key())[:22]
                report_iocp.iocp_page(iocp_obj, tc_page, wb, sname, sheet_index, sname)
                tbl_contents.append(dict(sc=1, s=sname, d=sname))
                sheet_index += 1

    # Add the Best Practice page
    if _report_pages['bp']['s']:
        sname = 'Best_Practice'
        fab_name = 'Best Practice Violations'  # Just borrowing fab_name for the title
        report_bp.bp_page(wb, tc_page, sname, 0, fab_name, proj_obj, rt.BestPractice.bp_tbl,
                          rt.BestPractice.bp_display_tbl)
        tbl_contents.insert(0, dict(sc=1, s=sname, d=fab_name))
        tbl_contents.insert(0, dict(h=True, d=fab_name))

    # Add the missing chassis (chassis not polled) to the title & contents page
    i = 0
    tbl_contents.append(dict(h=True, merge=3, d='Missing chassis (discovered in fabrics but not polled)'))
    for chassis_obj in proj_obj.r_chassis_objects():
        if chassis_obj.r_get('brocade-chassis') is None:
            # Try to find a chassis name
            chassis_name = None
            for obj in chassis_obj.r_switch_objects():
                chassis_name = obj.r_get('brocade-fabric/fabric-switch/chassis-user-friendly-name')
                if chassis_name is not None:
                    break
            if chassis_name is None:
                chassis_name = 'Unknown'
            chassis_name += ' (' + chassis_obj.r_obj_key() + ')'
            tbl_contents.append(dict(sc=1, d=chassis_name))
            for obj in chassis_obj.r_switch_objects():
                tbl_contents.append(dict(sc=2, d=brcddb_switch.best_switch_name(obj, True)))
            i += 1
    if i == 0:
        tbl_contents.append(dict(sc=1, d='None'))

    # Insert the title & contents page
    proj_title_page(proj_obj, None, wb, 0, tc_page, 'Contents', contents=tbl_contents)

    # Save the report.
    report_utils.save_report(wb, outf)
