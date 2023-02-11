#!/usr/bin/python
# -*- coding: utf-8 -*-
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
:mod:`compare_report` - Creates a report in Excel Workbook format with all differences between two content samples

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-8   | 17 Apr 2021   | Miscellaneous minor bug fixes and usability/report enhancements                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 14 May 2021   | Fixed missing member changes for aliases and zones.                               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 07 Aug 2021   | Fixed call to best_switch_name.                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 14 Nov 2021   | Fixed __date__                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 31 Dec 2021   | Removed old unused code.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.3     | 28 Apr 2022   | Fixed IndexError and relocated libraries.                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.4     | 11 Feb 2023   | Added 9.1.x branches                                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022 Jack Consoli'
__date__ = '11 Feb 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.4'

import argparse
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.file as brcdapi_file
import brcdapi.excel_util as excel_util
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_switch as brcddb_switch
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.util.compare as brcddb_compare
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_common as brcddb_common
import brcddb.report.utils as report_utils
import brcddb.app_data.report_tables as brcddb_rt

_DOC_STRING = False  # Should always be False. Prohibits any code execution. Only useful for building documentation
_DEBUG = False   # When True, use _DEBUG_xxx below instead of parameters passed from the command line.
_DEBUG_bf = '_capture_2023_01_27_17_53_35/combined'
_DEBUG_cf = '_capture_2023_01_29_10_21_27/combined'
_DEBUG_r = 'test/test_compare_report'
_DEBUG_sup = False
_DEBUG_log = '_logs'
_DEBUG_nl = False

# Debug
_DEBUG_R = False
_DEBUG_W = False

_key_conv_tbl = dict()  # List of API keys converted to human readable format for report display
_generic_table_add = (  # Key to add to _key_conv_tbl that are simple key/values in brcddb.app_data.report_tables
    brcddb_rt.Chassis.chassis_display_tbl,
    brcddb_rt.Switch.switch_display_tbl,
    brcddb_rt.Chassis.chassis_display_tbl,
    brcddb_rt.Security.security_display_tbl,
    brcddb_rt.Zone.zone_display_tbl,
)

"""We don't want to clutter the report with expected changes such as time-awake, or minor changes such as a few uW
difference in Tx power. The keys in these tables are used as a RegEx search. Keys in dict() are as follows:
+-------|-----------------------------------------------------------------------------------------------------------|
| Key   | Description                                                                                               |
+=======+===========================================================================================================|
| skip  | True - do not perform any checking on matching keys.                                                      |
+-------|-----------------------------------------------------------------------------------------------------------|
| lt    | Only used for numeric comparisons. The item is marked as changed if the compare object + this value is    |
|       | less  than the base value.                                                                                |
+-------|-----------------------------------------------------------------------------------------------------------|
| gt    | Same as lt except compare object + this value is greater than the base value.                             |
+-------|-----------------------------------------------------------------------------------------------------------|
"""
_control_tables = dict(
    ProjectObj={
        '/_(obj_key|alerts)': dict(skip=True),
    },
    ChassisObj={
        '/_(obj_key|project_obj|alerts)': dict(skip=True),
        '/brocade-chassis/chassis/date': dict(skip=True),
        '/brocade-chassis/management-port-connection-statistics': dict(skip=True),
        '/brocade-fru/fan/speed': dict(lt=500, gt=500),
        '/brocade-fru/fan/time-(awake|alive)': dict(skip=True),
        '/brocade-fru/power-supply/time-(awake|alive)': dict(skip=True),
        '/brocade-fru/power-supply/temperature': dict(lt=5, gt=5),
        '/brocade-fru/power-supply/power-usage': dict(lt=50, gt=50),
        '/brocade-fru/power-supply/input-voltage': dict(lt=10, gt=10),
        '/brocade-fru/power-supply/last-header-update-date': dict(skip=True),
        '/brocade-fru/blade/power-usage': dict(lt=10, gt=10),
        '/brocade-fru/blade/time-(alive|awake)': dict(skip=True),
        '/brocade-fru/blade/last-header-update-date': dict(skip=True),
        '/brocade-fru/sensor/temperature': dict(lt=5, gt=5),
        '/brocade-fru/wwn/time-(alive|awake)': dict(skip=True),
        '/brocade-fru/wwn/time-alive/time-awake': dict(skip=True),
        '/brocade-fru/wwn/last-header-update-date': dict(skip=True),
        '/brocade-fru/fan/last-header-update-date': dict(skip=True),
        '/brocade-logging': dict(skip=True),
        '/brocade-supportlink': dict(skip=True),
        '/management-ethernet-interface': dict(skip=True),
        '/brocade-management-ip-interface': dict(skip=True),
    },
    FabricObj={
        '/_(obj_key|project_obj|alerts|base_logins|port_map)': dict(skip=True),
        '/brocade-zone/(.*)': dict(skip=True),  # Everything in brocade-zone is already in the object
        # The number of fpin notifications is fabric dependent. 20 is somewhat arbitrary
        '/brocade-fabric-traffic-controller/fabric-traffic-controller-device/fpin-send-statistics/congestion-count':
            dict(lt=0, gt=0),
        '/brocade-traffic-optimizer/performance-group/aggregate-iops': dict(skip=True),
        '/brocade-traffic-optimizer/performance-group/aggregate-throughput': dict(skip=True),
        # It wasn't clear what max-io-latency represented in the 9.1.1 Rest API Guide. I'm assuming it's 2.5 usec ticks
        # so 4000,000 = 1 sec. The maximum I/O latency is fabric dependent. 20 msec is somewhat arbitrary
        '/brocade-traffic-optimizer/performance-group/max-io-latency': dict(lt=80000, gt=80000),
    },
    ZoneCfgObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    LoginObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    FdmiNodeObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    FdmiPortObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    ZoneObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    AliasObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
    },
    SwitchObj={
        '/_(obj_key|project_obj|alerts|flags|fabric_key|reserved_keys)': dict(skip=True),
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/(port|ge-port)-member-list/port-member':
            dict(skip=True),
        '/brocade-fibrechannel-switch/fibrechannel-switch/up-time': dict(skip=True),
        '/brocade-fibrechannel-switch/fibrechannel-switch/enabled-state': dict(skip=True),  # Deprecated
        '/brocade-fabric/fabric-switch/fcid': dict(skip=True),  # Deprecated
        '/brocade-maps/dashboard-rule': dict(skip=True),
        '/brocade-maps/dashboard-rule/category': dict(skip=True),  # See above line. I should never get here
        '/brocade-maps/dashboard-rule/name': dict(skip=True),  # See comment above.
        '/brocade-maps/dashboard-history': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/tx-percentage': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/tx-throughput': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/rx-throughput': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/rx-throughput/txrx-throughput': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/txrx-throughput': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/txrx-percentage': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/rx-percentage': dict(skip=True),
        '/brocade-fibrechannel-trunk/performance/rx-percentage/txrx-percentage': dict(skip=True),
        '/brocade-maps/dashboard-rule/objects/object': dict(skip=True),
        '/brocade-maps/dashboard-rule/objects/repetition-count': dict(skip=True),
        '/brocade-maps/dashboard-rule/objects/time-stamp': dict(skip=True),
        '/brocade-maps/dashboard-rule/objects/triggered-count': dict(skip=True),
        'brocade-maps/group/members/member': dict(skip=True),
        'brocade-maps/system-resources/cpu-usage': dict(skip=True),
        'brocade-logging/raslog/(current|default)-severity': dict(skip=True),
        'brocade-logging/raslog/current-severity/default-severity': dict(skip=True),
        'brocade-logging/raslog/message-id': dict(skip=True),
    },
    PortObj={
        '/_(obj_key|project_obj|alerts|sfp_thresholds|maps_fc_port_group|flags|switch|reserved_keys)': dict(skip=True),
        '/fibrechannel/fcid': dict(skip=True),  # Deprecated
        '/fibrechannel/enabled-state': dict(skip=True),  # Deprecated
        '/fibrechannel/average-(receive|transmit)-frame-size': dict(skip=True),
        '/fibrechannel/average-(receive|transmit)-buffer-usage': dict(skip=True),
        '/fibrechannel-statistics/(time-generated|class-3-frames)': dict(skip=True),
        '/fibrechannel-statistics/(in|out)-(rate|octets|frames)': dict(skip=True),
        '/fibrechannel-statistics/(in|out)-(frame|max-frame|peak)-rate': dict(skip=True),
        '/fibrechannel-statistics/frames-processing-required': dict(skip=True),  # What is this?
        '/fibrechannel-statistics/fibrechannel-statistics time-refreshed': dict(skip=True),
        '/media-rdp/temperature': dict(lt=5, gt=5),
        '/media-rdp/current': dict(lt=0.2, gt=0.2),
        '/media-rdp/(r|t)x-power': dict(lt=15, gt=15),
        '/media-rdp/voltage': dict(lt=20, gt=20),
        '/media-rdp/power-on-time': dict(skip=True),
        '/media-rdp/remote-media-temperature': dict(lt=5, gt=5),
        '/media-rdp/remote-media-current': dict(lt=0.2, gt=0.2),
        '/media-rdp/remote-media-(r|t)x-power': dict(lt=20, gt=20),
        '/media-rdp/remote-media-voltage': dict(lt=20, gt=20),
        '/media-rdp/remote-media-(voltage|temperature|tx-bias|tx-power|rx-power)-alert/(high|low)-(warning|alarm)':
            dict(skip=True),  # These remote media values aren't always valid
    },
    AlertObj={
        '/msg_tbl': dict(skip=True),
    },
)

_column_names = dict(
    _flags='Flag',
    _port_objs='FC Port',
    _ge_port_objs='GE Port',
    _maps_rules='MAPS Rule',
    _maps_group_rules='MAPS Group Rule',
    _maps_groups='MAPS Group',
    _login_objs='Login',
    _zonecfg_objs='Zone Configuration',
    _alias_objs='Alias',
    _zone_objs='Zone',
    _eff_zone_objs='Effective Zone Member',
    _fdmi_node_objs='FDMI Node',
    _fdmi_port_objs='FDMI Port',
    _fabric_objs='Fabric'
)


def _format_disp(fk, obj):
    """Converts API keys to human readable format

    :param fk: List of keys to convert
    :type obj: list
    :param obj: Change object
    :type obj: dict
    :return: List of keys in human readable format for report
    :type: list
    """
    # I have no idea what I was thinking when I did this. It works but it's ugly

    global _key_conv_tbl

    b, c = obj.get('b'), obj.get('c')
    tfk = fk.copy()
    if len(tfk) == 2 and tfk[0] == '_port_objs':
        key = 'Port'
    elif len(tfk) > 2 and tfk[0] == '_port_objs':
        tfk[1] = 's/p'
        key = '/'.join(tfk)
        if key in _key_conv_tbl:
            key = 'Port ' + fk[1] + ' ' + _key_conv_tbl[key]
        else:
            key = 'Port ' + fk[1] + '/' + fk[2] + ' ' + '/'.join(tfk[3:])
        try:
            b = str(brcddb_common.port_conversion_tbl[tfk[3]][int(b)])
            c = str(brcddb_common.port_conversion_tbl[tfk[3]][int(c)])
        except (ValueError, KeyError, IndexError):
            try:
                b = str(brcddb_common.port_conversion_tbl[tfk[3]][b])
                c = str(brcddb_common.port_conversion_tbl[tfk[3]][c])
            except (KeyError, IndexError):
                b = obj.get('b')
                c = obj.get('c')
    elif len(tfk) > 2 and tfk[0] == 'brocade-fibrechannel-switch' and tfk[1] == 'fibrechannel-switch':
        key = '/'.join(tfk)
        try:
            b = str(brcddb_common.switch_conversion_tbl[key][int(b)])
            c = str(brcddb_common.switch_conversion_tbl[key][int(c)])
        except (ValueError, KeyError, IndexError):
            b, c = obj.get('b'), obj.get('c')
        if key in _key_conv_tbl:
            key = _key_conv_tbl[key]
    else:
        key = '/'.join(tfk)
        if isinstance(key, str) and key in _key_conv_tbl:
            key = _key_conv_tbl[key]

    return [key, b, c, obj.get('r')]


def _content_append(obj, content):
    """Checks to makes sure we're not adding null content

    :param obj: Object to add
    :type obj: dict
    :param content: List of report content where obj is to be added
    :type content: list
    """
    dl = obj.get('disp')
    if dl is not None and len(dl) == 4:
        if dl[1] is not None and dl[2] is not None:
            content.append(obj)
    else:
        content.append(obj)


def _fabric_name(p_obj, wwn, flag=True):
    return brcddb_fabric.best_fab_name(p_obj.r_fabric_obj(wwn), flag)


def _chassis_name(p_obj, wwn, flag=True):
    return brcddb_chassis.best_chassis_name(p_obj.r_chassis_obj(wwn), flag)


def _switch_name(p_obj, wwn, flag=True):
    return brcddb_switch.best_switch_name(p_obj.r_switch_obj(wwn), flag)


def _basic_add_to_content(obj, b_obj, c_obj, content):
    """Parses a dictionary returned from brcddb.util.compare.compare

    :param obj: Fabric object to parse
    :type obj: dict
    :param b_obj: Base project object. Not used
    :type b_obj: brcddb.classes.project.*Obj
    :param c_obj: Compare project object. Not used
    :type c_obj: brcddb.classes.project.*Obj
    :param content: List of report content where objects in obj are to be added
    :type content: list
    """
    start = len(content)
    if obj is not None:
        for k, v in obj.items():
            _content_append(dict(font='std', align='wrap', disp=('', v.get('b'), v.get('c'), v.get('r'))), content)
    if len(content) == start:
        content.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))


def _alias_add_to_content(obj, b_obj, c_obj, content):
    """Same as _basic_add_to_content() but assumes the data are WWNs and converts them to aliases"""
    start = len(content)
    if obj is not None:
        for k, v in obj.items():
            b_buf = v.get('b')
            alias = b_obj.r_alias_for_wwn(b_buf)
            if len(alias) > 0:
                b_buf = alias[0] + ' (' + b_buf + ')'
            c_buf = v.get('c')
            alias = c_obj.r_alias_for_wwn(c_buf)
            if len(alias) > 0:
                c_buf = alias[0] + ' (' + c_buf + ')'
            _content_append(dict(font='std', align='wrap', disp=('', b_buf, c_buf, v.get('r'))), content)
    if len(content) == start:
        content.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))


def _zoneobj_add_to_content(obj, b_obj, c_obj, content):
    """Same as _basic_add_to_content() but assumes the data are WWNs and converts them to aliases"""
    start = len(content)
    if obj is not None:
        for k, v in obj.items():
            buf = str(k)
            for mem_d in gen_util.convert_to_list(v.get('_members')):
                _content_append(dict(font='std', align='wrap', disp=(buf, mem_d['b'], mem_d['c'], mem_d['r'])), content)
                buf = ''
            for mem_d in gen_util.convert_to_list(v.get('_pmembers')):
                _content_append(dict(font='std', align='wrap', disp=(buf, mem_d['b'], mem_d['c'], mem_d['r'])), content)
                buf = ''
    if len(content) == start:
        content.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))


def _switch_add_to_content(obj, b_obj, c_obj, content):
    """Same as _basic_add_to_content() except obj is a list of switch change objects"""
    start = len(content)
    for change_obj in [t_obj for t_obj in obj if t_obj.get('r') is not None]:
        b_buf = brcddb_switch.best_switch_name(b_obj.r_project_obj().r_switch_obj(change_obj.get('b')), True)
        c_buf = brcddb_switch.best_switch_name(c_obj.r_project_obj().r_switch_obj(change_obj.get('c')), True)
        _content_append(dict(font='std', align='wrap', disp=('', b_buf, c_buf, change_obj.get('r'))), content)
    if len(content) == start:
        content.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))


def _fabric_add_to_content(obj, b_obj, c_obj, content):
    """Same as _basic_add_to_content() but assumes the data are WWNs and converts them to fabric names"""
    start = len(content)
    if obj is not None:
        proj_obj = obj.r_project_obj()
        for k, v in obj.items():
            b_buf = brcddb_fabric.best_fab_name(proj_obj.r_fabric_obj(v.get('b')), True)
            c_buf = brcddb_fabric.best_fab_name(proj_obj.r_fabric_obj(v.get('c')), True)
            _content_append(dict(font='std', align='wrap', disp=('', b_buf, c_buf, v.get('r'))), content)
    if len(content) == start:
        content.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))


def _null(obj, b_obj, c_obj, content):
    """Used for development before comparisons are complete for an item"""
    return


_action_table = dict(
    _fabric_objs=dict(
        _alias_objs=dict(t='Aliases', f=_zoneobj_add_to_content),
        _eff_zone_objs=dict(t='Zones in effective zones configuration', f=_basic_add_to_content),
        _fdmi_node_objs=dict(t='FDMI Nodes', f=_alias_add_to_content),
        _fdmi_port_objs=dict(t='FDMI Ports', f=_alias_add_to_content),
        _login_objs=dict(t='Name server logins', f=_alias_add_to_content),
        _switch_keys=dict(t='Switches in fabric', f=_switch_add_to_content),
        _zone_objs=dict(t='Zones', f=_zoneobj_add_to_content),
        _zonecfg_objs=dict(t='Zone configurations', f=_zoneobj_add_to_content),
    ),
    _chassis_objs=dict(
        _switch_keys=dict(t='Switches in fabric', f=_switch_add_to_content),
    ),
    _switch_objs=dict(
        _fabric_key=dict(t='Member of Fabric', f=_fabric_add_to_content),
        _maps_rules=dict(t='MAPS Rules', f=_basic_add_to_content),
        # _maps_group_rules=dict(t='MAPS Group Rules', f=_basic_add_to_content),
        _maps_group_rules=dict(t='MAPS Group Rules', f=_null),
        _maps_groups=dict(t='MAPS Groups', f=_basic_add_to_content),
    ),
)


def _api_added_compares(obj, k, fk, content):
    """Recursively iterates through a list of changes from compare.compare() for API added content

    :param obj: Added API content or list of API content objects
    :type obj: dict, list, tuple
    :param k: Active key
    :type k: str
    :param fk: List of keys
    :type fk: list
    :param content: Running list of changes to add to report
    :type content: list
    """
    if isinstance(obj, dict):
        t_obj = obj.get(k)
        if isinstance(t_obj, dict):
            fk.append(k)
            for k1 in t_obj.keys():
                _api_added_compares(t_obj, k1, fk.copy(), content)
        elif isinstance(t_obj, (list, tuple)):
            _api_added_compares(t_obj, k, fk, content)
        elif isinstance(t_obj, (str, int, float)):
            if k == 'b':
                _content_append(dict(font='std', align='wrap', disp=_format_disp(fk, obj)), content)
            elif k not in ('c', 'r'):
                brcdapi_log.exception('Unknown element: ' + str(t_obj), True)
        else:
            brcdapi_log.exception('Unknown type: ' + str(type(t_obj)), True)

    elif isinstance(obj, (list, tuple)):
        fk.append(k)
        for i in range(0, len(obj)):
            n_obj = obj[i]
            if isinstance(n_obj, dict):
                for k1 in n_obj.keys():
                    if '[' in fk[len(fk)-1]:
                        fk.pop()
                    fk.append('[' + str(i) + ']')
                    _api_added_compares(n_obj, k1, fk.copy(), content)

    else:
        brcdapi_log.exception('Unknown type: ' + str(type(obj)), True)


def _project_page(wb, sheet_index, b_proj_obj, c_proj_obj, c_obj):
    """Recursively iterates through a list of changes from compare.compare() for fabric. Create fabric pages as needed

    :param wb: Workbook object
    :type wb: dict
    :param sheet_index: Starting sheet index
    :type sheet_index: int
    :param b_proj_obj: Project object for base (project we are comparing against). Typically the older project.
    :type b_proj_obj: brcddb.classes.project.ProjectObj
    :param c_proj_obj: Comparison project object. Typically the newer project.
    :type c_proj_obj: brcddb.classes.project.ProjectObj
    :param c_obj: This is the object from compare.compare() that we are working on
    :type c_obj: dict
    :return sheet_index: Next sheet index
    :rtype sheet_index: int
    :return tbl_contents: Table of contents for the fabrics
    :rtype. tbl_contents: list
    """
    # Set up the table of contents and sheet headers
    content = [
        dict(font='hdr_1', align='wrap', disp='Project changes'),
        dict(),
        dict(font='hdr_2', align='wrap', disp='Fabrics Added:'),
    ]

    # Add fabric changes
    for obj in [d for d in c_obj['_fabric_objs'].values() if d['r'] == 'Added']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_fabric.best_fab_name(c_proj_obj.r_fabric_obj(obj.get('c')), True)))
    content.extend([dict(), dict(font='hdr_2', align='wrap', disp='Fabrics Removed:')])
    for obj in [d for d in c_obj['_fabric_objs'].values() if d['r'] == 'Removed']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_fabric.best_fab_name(b_proj_obj.r_fabric_obj(obj.get('b')), True)))

    # Add switch changes
    content.extend([dict(), dict(font='hdr_2', align='wrap', disp='Switches Added:')])
    for obj in [d for d in c_obj['_switch_objs'].values() if d['r'] == 'Added']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_switch.best_switch_name(c_proj_obj.r_switch_obj(obj.get('c')), True)))
    content.extend([dict(), dict(font='hdr_2', align='wrap', disp='Switches Removed:')])
    for obj in [d for d in c_obj['_switch_objs'].values() if d['r'] == 'Removed']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_switch.best_switch_name(b_proj_obj.r_switch_obj(obj.get('b')), True)))

    # Add chassis changes
    content.extend([dict(), dict(font='hdr_2', align='wrap', disp='Chassis Added:')])
    for obj in [d for d in c_obj['_chassis_objs'].values() if d['r'] == 'Added']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_chassis.best_chassis_name(c_proj_obj.r_chassis_obj(obj.get('c')), True)))
    content.extend([dict(), dict(font='hdr_2', align='wrap', disp='Chassis Removed:')])
    for obj in [d for d in c_obj['_chassis_objs'].values() if d['r'] == 'Removed']:
        content.append(dict(font='std', align='wrap',
                            disp=brcddb_chassis.best_chassis_name(b_proj_obj.r_chassis_obj(obj.get('b')), True)))

    # Sheet name and title
    sname = 'Project_Changes_' + str(sheet_index)
    report_utils.title_page(wb, None, sname, sheet_index, 'Project Changes', content, 80)

    return sheet_index+1, [dict(s=sname, d='Project Changes')]


def _page(wb, sheet_index, b_proj_obj, c_proj_obj, c_obj, page):
    """Recursively iterates through a list of changes from compare.compare() for fabric. Create fabric pages as needed

    :param wb: Workbook object
    :type wb: dict
    :param sheet_index: Starting sheet index
    :type sheet_index: int
    :param b_proj_obj: Project object for base (project we are comparing against). Typically the older project.
    :type b_proj_obj: brcddb.classes.project.ProjectObj
    :param c_proj_obj: Comparison project object. Typically the newer project.
    :type c_proj_obj: brcddb.classes.project.ProjectObj
    :param c_obj: This is the object from compare.compare() that we are working on
    :type c_obj: dict
    :param page: Page type: _fabric_objs, _chassis_objs, or _switch_objs
    :type page: str
    :return sheet_index: Next sheet index
    :rtype sheet_index: int
    :return tbl_contents: Table of contents for the fabrics
    :rtype. tbl_contents: list
    """
    global _main_pages

    # Set up the table of contents and sheet headers
    tbl_contents = list()
    if not isinstance(c_obj, dict):
        return sheet_index, tbl_contents  # This happens when there are no changes
    for base_key, f_obj in c_obj.items():
        b_fab_obj, c_fab_obj = b_proj_obj.r_fabric_obj(base_key), c_proj_obj.r_fabric_obj(base_key)
        t_content = [dict(font='hdr_2', align='wrap', disp=('Key', 'Base Value', 'Compare Value', 'Change'))]
        obj_tbl = _action_table[page]

        # Add each individual item for the brcddb object to the sheet
        if b_fab_obj is not None and c_fab_obj is not None:  # The principal fabric switch may not have been polled
            for k, cntl_tbl in obj_tbl.items():
                obj = f_obj.get(k)
                if obj is not None:
                    # obj can be None if code was upgraded and a new KPI was introduced and captured. This logic skips
                    # reporting on anything new because we have no idea what the previous version would have been
                    t_content.append(dict())
                    t_content.append(dict(font='hdr_2', merge=4, align='wrap', disp=cntl_tbl.get('t')))
                    cntl_tbl.get('f')(obj, b_fab_obj, c_fab_obj, t_content)

        # Add each item added to the brcddb object (these are the items from the API)
        t_content.append(dict())
        t_content.append(dict(font='hdr_2', merge=4, align='wrap', disp='Added from RESTConf API'))
        for k1 in [key for key in f_obj.keys() if key not in obj_tbl]:
            _api_added_compares(f_obj, k1, list(), t_content)
        # Sheet name and title
        title, sname = _main_pages[page]['ts'](b_proj_obj, base_key)
        sname = sname.replace(' ', '_').replace(':', '').replace('-', '_')
        sname = sname[:28] + '_' + str(sheet_index) if len(sname) > 28 else sname + '_' + str(sheet_index)
        tbl_contents.append(dict(s=sname, d=title))

        report_utils.title_page(wb, None, sname, sheet_index, title, _main_pages[page]['sc'](t_content),
                                (42, 45, 45, 24))
        sheet_index += 1

    return sheet_index, tbl_contents


# After the fact, I realized I needed to sort the display output. The next 2 methods sort and filter the output
def _sort_switch(content):
    re, rl = list(), list()
    for obj in content:
        try:
            key = obj.get('disp')[0]
        except (TypeError, IndexError):
            key = ''
        if not key.startswith('brocade-maps/group/members'):
            if key.startswith('Port '):
                re.append(obj)
            else:
                rl.append(obj)

    rl.append(dict())
    rl.append(dict(merge=4, font='hdr_2', align='wrap', disp=('Ports',)))
    if len(re) == 0:
        rl.append(dict(merge=4, font='std', align='wrap', disp=('No changes',)))
    else:
        rl.extend(re)
    return rl


def _sort_null(content):
    return content


def _fabric_ts(o, k):
    """Returns the title of the sheet, which is also used in the report summary page, and the sheet name

    :param o: brcddb class object from which the key, k, is to be retrieved. So far, this has only been a project object
    :type o: brcddb.classes.project.ProjectObj
    :param k: The key for the object to retrieve from o
    :type k: key, str
    :return title: Sheet title
    :rtype title: str
    :return name: Sheet name
    :rtype name: str
    """
    obj = o.r_fabric_obj(k)
    return brcddb_fabric.best_fab_name(obj, True), brcddb_fabric.best_fab_name(obj, False)


def _chassis_ts(o, k):  # Similar to _fabric_ts()
    obj = o.r_chassis_obj(k)
    return brcddb_chassis.best_chassis_name(obj, True), brcddb_chassis.best_chassis_name(obj, False)


def _switch_ts(o, k):  # Similar to _fabric_ts()
    obj = o.r_switch_obj(k)
    return brcddb_switch.best_switch_name(obj, True), brcddb_switch.best_switch_name(obj, False)


_main_pages = dict(  # 's': sheet name. 't': sheet title. 'n': method to return object name
    _fabric_objs=dict(s='F_', t='Fabric Comparisons: ', n=_fabric_name, sc=_sort_null, ts=_fabric_ts),
    _switch_objs=dict(s='S_', t='Switch Comparisons: ', n=_switch_name, sc=_sort_switch, ts=_switch_ts),
    _chassis_objs=dict(s='C_', t='Chassis Comparisons: ', n=_chassis_name, sc=_sort_null, ts=_chassis_ts),
)


def _login_obj_name(obj, k, wwn):
    if obj is None or k is None or wwn is None:
        return wwn
    fab_obj = obj.r_fabric_obj(k)
    if fab_obj is None:
        return wwn
    alias_l = fab_obj.r_alias_for_wwn(wwn)
    return alias_l[0] + ' (' + wwn + ')' if len(alias_l) > 0 else wwn


def parse_args():
    """Parses the module load command line
    
    :return b_file: Base file name for comparison. File is in the format output by capture, multi_capture, and combined.
    :rtype b_file: str
    :return c_file: Compare file name. Same format as the base file
    :rtype c_file: str
    :return o_file: Output file name for Excel report.
    :rtype o_file: str
    """
    global _DEBUG_bf, _DEBUG_cf, _DEBUG_r, _DEBUG_sup, _DEBUG_log, _DEBUG_nl

    if _DEBUG:
        return _DEBUG_bf, _DEBUG_cf, _DEBUG_r, _DEBUG_sup, _DEBUG_log, _DEBUG_nl

    parser = argparse.ArgumentParser(description='Create a comparison report in Excel.')
    buf = 'Base project to compare against. Name of input file generated by capture.py or combine.py. Typically ' \
          'the older data.'
    parser.add_argument('-b', help=buf, required=True)
    buf = 'Project to compare against. Name of input file generated by capture.py or combine.py. Typically the ' \
          'newer data.'
    parser.add_argument('-c', help=buf, required=True)
    parser.add_argument('-r', help='Excel comparison report file name. ".xlsx" is automatically appended.',
                        required=True)
    buf = 'suppress all output to STD_IO except the exit code and argument parsing errors. Useful with batch '\
          'processing where only the exit status code is desired. Messages are still printed to the log file.'
    parser.add_argument('-sup', help=buf, action='store_true', required=False)
    buf = '(Optional) Directory where log file is to be created. Default is to use the current directory. The log ' \
          'file name will always be "Log_xxxx" where xxxx is a time and date stamp.'
    parser.add_argument('-log', help=buf, required=False, )
    buf = '(Optional) No parameters. When set, a log file is not created. The default is to create a log file.'
    parser.add_argument('-nl', help=buf, action='store_true', required=False)
    args = parser.parse_args()
    return args.b, args.c, args.r, args.sup, args.log, args.nl


def _project_scrub(c_obj):
    """Pulls out changes that are really overall project specific from fabric, chassis, and switch objects

    :param c_obj: Change object returned from brcddb.util.compare.compare()
    :type c_obj: dict
    :return: Compare object with '_project_obj'
    :rtype: dict
    """
    project_d = dict(_fabric_objs=dict(), _switch_objs=dict(), _chassis_objs=dict())
    rd = dict(_project_obj=project_d)
    for k0, d0 in c_obj.items():
        if k0 in (project_d.keys()):
            for k1, d1 in d0.items():
                if 'b' in d1 and 'c' in d1 and 'r' in d1:  # It's just an added or removed fabric, switch, or chassis
                    project_d[k0].update({k1: d1})
                else:
                    if k0 not in rd:
                        rd.update({k0: dict()})
                    rd[k0].update({k1: d1})
        else:
            rd.update({k0: d0})

    return rd


def _new_report(c, b_proj_obj, c_proj_obj, c_obj, r_name):
    """Generates an Excel comparison report

    :param c: Total number of changes. Typically the number of changes returned from brcddb.util.compare.compare()
    :type c: int
    :param b_proj_obj: Project object for base (project we are comparing against). Typically the older project.
    :type b_proj_obj: brcddb.classes.project.ProjectObj
    :param c_proj_obj: Comparison project object. Typically the newer project.
    :type c_proj_obj: brcddb.classes.project.ProjectObj
    :param c_obj: Change object returned from brcddb.util.compare.compare()
    :type c_obj: dict
    :param r_name: Name of Excel workbook file
    :type r_name: str
    """
    global _main_pages

    # Set up the workbook
    sheet_index = 0
    wb = excel_util.new_report()

    # Setup the Project summary sheet with table of content
    title = b_proj_obj.r_obj_key() + ' Compared to ' + c_proj_obj.r_obj_key()
    tc_page = 'Project_Summary'
    t_content = [
        dict(font='std', align='wrap', disp=('Total changes', c)),
        dict(),
        dict(font='hdr_2', align='wrap', disp=('Key', 'Base Value', 'Compare Value', 'Change')),
    ]

    # Add any added changes to the project objects
    for k, obj in c_obj.items():
        if k not in _main_pages.keys() and k != '_project_obj':
            t_content.append(dict(font='std', align='wrap', disp=(k, obj.get('b'), obj.get('c'), obj.get('r'))))
    t_content.append(dict())

    # Add the project change sheet
    sheet_index, tbl_contents = _project_page(wb, sheet_index, b_proj_obj, c_proj_obj, c_obj.get('_project_obj'))
    d = tbl_contents[0]
    td = dict(font='link', merge=4, align='wrap', disp=d.get('d'))
    td.update(hyper='#' + d.get('s') + '!A1')
    t_content.append(td)

    # Add all the chassis, switch and fabric sheets
    for k, p_obj in _main_pages.items():
        t_content.append(dict())
        t_content.append(dict(font='hdr_2', merge=4, align='wrap', disp=p_obj.get('t')))
        sheet_index, tbl_contents = _page(wb, sheet_index, b_proj_obj, c_proj_obj, c_obj.get(k), k)
        for d in tbl_contents:
            td = dict(font='link', merge=4, align='wrap', disp=d.get('d'))
            if 's' in d:  # Is there a link to a page?
                td.update(hyper='#' + d.get('s') + '!A1')
                t_content.append(td)

    # Add the project summary with table of contents and save the report.
    report_utils.title_page(wb, None, tc_page, 0, title, t_content, (24, 42, 42, 12))
    excel_util.save_report(wb, r_name)


def pseudo_main():
    """Basically the main(). Did it this way so it can easily be used as a standalone module or called from another.

    :return: Exit code. See exist codes in brcddb.brcddb_common
    :rtype: int
    """
    global _generic_table_add, _key_conv_tbl, _control_tables

    # Debug
    global _DEBUG_W, _DEBUG_R

    # Get and validate the user inputs.
    bf, cf, rf, s_flag, log, nl = parse_args()
    if s_flag:
        brcdapi_log.set_suppress_all()
    if not nl:
        brcdapi_log.open_log(log)
    rf = brcdapi_file.full_file_name(rf, '.xlsx')
    bf = brcdapi_file.full_file_name(bf, '.json')
    cf = brcdapi_file.full_file_name(cf, '.json')
    ml = ['WARNING!!! Debug is enabled'] if _DEBUG else list()
    ml.append(':START: Compare Report:')
    ml.append('    Base file:    ' + bf)
    ml.append('    Compare file: ' + cf)
    ml.append('    Report file:  ' + rf)
    brcdapi_log.log(ml, True)

    # Read the projects to compare and build the cross references
    ml = list()
    b_proj_obj = brcddb_project.read_from(bf)
    c_proj_obj = brcddb_project.read_from(cf)
    if b_proj_obj is None:
        ml.append('Missing or invalid base project.')
    if c_proj_obj is None:
        ml.append('Missing or invalid compare project.')
    if len(ml) > 0:
        brcdapi_log.log(ml, True)
        return brcddb_common.EXIT_STATUS_ERROR
    brcddb_project.build_xref(b_proj_obj)
    brcddb_project.build_xref(c_proj_obj)

    # Build out the key conversion tables. Used in _format_disp()
    for k, v in brcddb_rt.Port.port_display_tbl.items():
        if k[0] != '_':  # Make sure it's not a custom key
            _key_conv_tbl.update({'_port_objs/s/p/' + k: v.get('d')})
    for k, v in brcddb_rt.Login.login_display_tbl.items():
        if k[0] != '_':  # Make sure it's not a custom key
            _key_conv_tbl.update({k: v.get('d')})
    for table_obj in _generic_table_add:
        for k, v in table_obj.items():
            if k[0] != '_':  # Make sure it's not a custom key
                if isinstance(v, dict):
                    for k1, v1 in v.items():
                        _key_conv_tbl.update({k + '/' + k1: v1})
                else:
                    _key_conv_tbl.update({k: v})

    # Compare the two projects
    brcdapi_log.log('Please wait. The comparison may take several seconds', True)
    if _DEBUG_R:
        debug_d = brcdapi_file.read_dump('debug_file.json')
        c, compare_obj = debug_d.get('c'), debug_d.get('compare_obj')
    else:
        c, compare_obj = brcddb_compare.compare(b_proj_obj, c_proj_obj, None, _control_tables)

    # Debug
    if _DEBUG_W:
        brcdapi_log.log('c = ' + str(c), echo=True)
        brcdapi_file.write_dump(dict(c=c, compare_obj=compare_obj), 'debug_file.json')

    brcdapi_log.log('Writing report: ' + rf, echo=True)
    _new_report(c, b_proj_obj, c_proj_obj, _project_scrub(compare_obj), rf)

    return brcddb_common.EXIT_STATUS_OK


##################################################################
#
#                    Main Entry Point
#
###################################################################
if _DOC_STRING:
    print('_DOC_STRING is True. No processing')
    exit(0)

_ec = pseudo_main()
brcdapi_log.close_log('\nProcessing Complete. Exit code: ' + str(_ec))
exit(_ec)
