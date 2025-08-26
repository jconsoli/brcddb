"""
Copyright 2023, 2024, 2025 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Parses output from NX OS (Cisco CLI output).

The methods herein convert NX-OS command output to the equivalent JSON produced when piping commands to json. The
intended use was for handling commands on older versions of NX-OS that do not support "| json". Methods were written on
an as needed basis. Only a limited number of commands are covered in this module. Since they were written as needed,
little thought went into coding style and consistency.

VSANs are interpreted as FIDs. The "show fcdomain" output, show_fcdomain(), must be performed first so as to pick up all
the VSANs.

**WARNINGS**

    * Intended for internal Consoli-Solutions use only
    * Smart zoning has not been implemented.
    * This was a hack when I ran into some command output that didn't support | JSON. The comments are off.

**Public Methods & Data**

+-------------------------------+-------------------------------------------------------------------------------+
| Method                        | Description                                                                   |
+===============================+===============================================================================+
| show_device_alias_database    | Parses "show device-alias database" output into the equivalent of             |
|                               | json.loads("show device-alias database | json")                               |
+-------------------------------+-------------------------------------------------------------------------------+
| show_interface_brief          | Parses "show interface brief" output into the equivalent of                   |
|                               | json.loads("show interface brief | json | no-more")                           |
+-------------------------------+-------------------------------------------------------------------------------+
| show_zoneset                  | Parses the output of "show zoneset" into brcddb objects                       |
+-------------------------------+-------------------------------------------------------------------------------+
| show_fcdomain                 | Parses "show zoneset" output into the equivalent of                           |
|                               | json.loads("show fcdomain | json | no-more")                                  |
+-------------------------------+-------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025 Consoli Solutions, LLC'
__date__ = '25 Aug 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.2'

import re
import time
import collections
import copy
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.brcddb_port as brcddb_port

_BFS_FS = 'brocade-fibrechannel-switch/fibrechannel-switch/'
_BF_FS = 'brocade-fabric/fabric-switch/'
_BFLS_FLS = 'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/'


_standard_zone_type = 0
_peer_zone_type = 1
_ns_key = 'brocade-name-server/'


def _int_val(buf):
    """Converts a str to int

    :param buf: String containing a number to convert to an integer
    :type buf: str, int, float
    """
    return int(buf)


###################################################################
#
#                  show device-alias database
#
# Public method is show_interface_brief() preceded by support methods
#
###################################################################

def show_device_alias_database(content_l):
    """Parses "show device-alias database" output into the equivalent of json.loads("show device-alias database | json")

    :param content_l: Command output. May or may not include the invocation (command prompt & command)
    :type content_l: list
    :return: Equivalent of json.loads("show device-alias database | json | no-more")
    :rtype: dict
    """
    rl = list()
    rd = dict(TABLE_device_alias_database=dict(ROW_device_alias_database=rl))

    for buf_l in [b.split(' ') for b in [gen_util.remove_duplicate_space(c).strip() for c in content_l if len(c) > 3]]:
        if buf_l[0] == 'device-alias':
            rl.append(dict(dev_alias_name=buf_l[2], pwwn=buf_l[4]))

    return rd


###################################################################
#
#                           show interface brief
#
# Public method is show_interface_brief() preceded by support methods
#
###################################################################

"""WARNING: I'm counting on the fact that the output will always look like:

-----------------------------------------------------------------------------------------
Interface  Vsan   Admin  Admin   Status       SFP    Oper  Oper   Port     Logical
                  Mode   Trunk                       Mode  Speed  Channel   Type
                         Mode                              (Gbps)
-----------------------------------------------------------------------------------------"""
_show_interface_brief_map = [
    'interface_fc',  # 0
    'vsan_brief',  # 1
    'admin_mode',  # 2
    'admin_trunk_mode',  # 3
    'status',  # 4
    'fcot_info',  # 5
    'port_rate_mode',  # 6
    'oper_speed',  # 7
    'port_channel',  # 8
    'logical_type',  # 9
]


def show_interface_brief(content_l):
    """Parses "show interface brief" output into the equivalent of json.loads("show interface brief | json | no-more")

    :param content_l: Command output. May or may not include the invocation (command prompt & command)
    :type content_l: list
    :return: Equivalent of json.loads("show interface brief | json | no-more")
    :rtype: dict
    """
    global _show_interface_brief_map

    rl = list()
    rd = dict(TABLE_interface_brief_fc=dict(ROW_interface_brief_fc=rl))

    working_l = [gen_util.remove_duplicate_space(b).strip() for b in content_l if len(b) > 0]

    # Skip past the header
    i = 0  # i counts the header breaks, '------------'
    while len(working_l) > 0 and i < 2:
        if '-----------' in working_l[0]:
            i += 1
        working_l.pop(0)

    for buf_l in [b.split(' ') for b in working_l]:
        if len(buf_l) < len(_show_interface_brief_map):
            break
        i, d = 0, dict()
        for buf in buf_l:
            d.update({_show_interface_brief_map[i]: buf})
            i += 1
        rl.append(d)

    return rd


###################################################################
#
#                           show zoneset
#
# Public method is show_zoneset() preceded by support methods
#
###################################################################

def _show_zoneset_zoneset_name(rd, zoneset_d, zone_d, control_d, buf):
    """Parse the output of "zoneset name" in "show zoneset".

    :param rd: Pointer to top level dictionary
    :type rd: dict
    :param zoneset_d: Active zoneset dictionary
    :type zoneset_d: dict
    :param zone_d: Active zone dictionary
    :type zone_d: dict
    """
    buf_l = gen_util.remove_duplicate_space(buf).split()
    r_zoneset_d = dict(zoneset_name=buf_l[2],
                       zoneset_vsan_id=int(buf_l[4]),
                       zoneset_alias=dict(),
                       zoneset_wip=None,
                       TABLE_zone=dict(ROW_zone=list()))
    rd['TABLE_zoneset']['ROW_zoneset'].append(r_zoneset_d)
    return r_zoneset_d, None


def _show_zoneset_zone_name(rd, zoneset_d, zone_d, control_d, buf):
    """Parse the output of "zone name" in "show zoneset". See _show_zoneset_zoneset_name()"""
    buf_l = gen_util.remove_duplicate_space(buf).split()
    r_zone_d = dict(zone_name=buf_l[2], zone_vsan_id=int(buf_l[4]), TABLE_zone_member=dict(ROW_zone_member=list()))
    zoneset_d['TABLE_zone']['ROW_zone'].append(r_zone_d)
    zoneset_d['zoneset_wip'] = None
    return zoneset_d, r_zone_d


def _show_zoneset_zone_member(rd, zoneset_d, zone_d, control_d, buf):
    """Parse the zone member content in "show zoneset". See _show_zoneset_zoneset_name()"""
    buf_l = gen_util.remove_duplicate_space(buf).split()
    if 'alias' in buf_l[0]:
        zone_d['TABLE_zone_member']['ROW_zone_member'].append(dict(dev_alias=buf_l[1]))
    elif 'wwn' in buf_l[0]:
        if isinstance(zoneset_d['zoneset_wip'], list):
            zoneset_d['zoneset_wip'].append(buf_l[1])
        else:
            zone_d['TABLE_zone_member']['ROW_zone_member'].append(dict(wwn=buf_l[1]))
    return zoneset_d, zone_d


def _fcalias_zone_member(rd, zoneset_d, zone_d, control_d, buf):
    """The zone contains an alias definitition - 'fcalias name' """
    buf_l = gen_util.remove_duplicate_space(buf).split()
    try:
        if int(buf_l[4]) != zoneset_d['zoneset_vsan_id']:
            e_buf = 'vsan id in ' + buf + ' does not match vsan for zoneset ' + zoneset_d['zoneset_name']
            brcdapi_log.exception(e_buf, echo=True)
            return zoneset_d, zone_d
    except TypeError:
        e_buf = 'Expected vsan integer in ' + buf + '. Received ' + str(buf_l[4]) + '.  in ' + zoneset_d['zoneset_name']
        brcdapi_log.exception(e_buf, echo=True)
        return zoneset_d, zone_d
    except IndexError:
        pass
    zone_d['TABLE_zone_member']['ROW_zone_member'].append(dict(dev_alias=buf_l[2]))
    zoneset_d['zoneset_wip'] = list()
    zoneset_d['zoneset_alias'].update({buf_l[2]: zoneset_d['zoneset_wip']})
    return zoneset_d, zone_d


_show_zoneset_parse_d = {
    'zoneset name': _show_zoneset_zoneset_name,
    'zone name': _show_zoneset_zone_name,
    'device-alias': _show_zoneset_zone_member,
    'fcalias name': _fcalias_zone_member,
    'fcalias': _show_zoneset_zone_member,
    'pwwn': _show_zoneset_zone_member,
}


def show_zoneset(content_l):
    """Parses "show zoneset" output into the equivalent of json.loads("show fcdomain | json | no-more")

    :param content_l: Command output. May or may not include the invocation (command prompt & command)
    :type content_l: list
    :return: Equivalent of json.loads("show fcdomain | json | no-more")
    :rtype: dict
    """
    global _show_zoneset_parse_d

    action, active_key, control_d, key_l = None, None, dict(), _show_zoneset_parse_d.keys()
    zoneset_d, zone_d, rd = None, None, dict(TABLE_zoneset=dict(ROW_zoneset=list()))
    working_d = rd['TABLE_zoneset']['ROW_zoneset']

    for buf in [gen_util.remove_duplicate_space(b).strip() for b in content_l]:

        # Skip blank lines
        if len(buf) == 0:
            if isinstance(zoneset_d, dict):
                zoneset_d['zoneset_wip'] = None
            continue

        # Something new to process?
        active_key = None
        for key in key_l:
            if len(buf) >= len(key) and buf[0: len(key)] == key:
                active_key = key
                break

        # Parse it
        if active_key is None:
            brcdapi_log.exception('Unknown key in ' + buf + '.', True)
            continue
        try:
            zoneset_d, zone_d = _show_zoneset_parse_d[active_key](rd, zoneset_d, zone_d, control_d, buf)
        except BaseException as e:
            ml = ['', 'Error processing: ' + buf, 'Exception is: ' + str(type(e)) + ': ' + str(e), '']
            brcdapi_log.exception(ml, True)

    return rd


###################################################################
#
#                           show fcdomain
#
# Public method is show_fcdomain() preceded by support methods
#
###################################################################

def _show_fcdomain_config_gen(sub_d, info_d, buf):
    info_d.update({sub_d['k']: ':'.join(buf.split(':'))[1:]})


def _show_fcdomain_config_optimized_mode(sub_d, info_d, buf):
    if 'disabled' in buf.lower():
        return
    buf_l = buf.split('(')
    info_d.update({sub_d['k']: buf_l[0].strip()})
    val, remainder = gen_util.paren_content('(' + buf_l[1], p_remove=True)
    info_d.update({sub_d['k0']: val.strip()})


def _show_fcdomain_domain_id(sub_d, info_d, buf):
    buf_l = buf.split(')')
    info_d.update({sub_d['k']: buf_l[0].strip()+')'})
    val, remainder = gen_util.paren_content(buf_l[1].strip()+')', p_remove=False)
    info_d.update({sub_d['k0']: val.strip()})
    return


def _show_fcdomain_vsan(control_d, switch_l, buf):
    """Parse the VSAN

    :param control_d: Dictionary in _show_fcdomain_parse_d for this state
    :type control_d: dict
    :param switch_l: List of individual switch dictionaries
    :type switch_l: list
    :param buf: Current line being parsed
    :type buf: str
    """
    switch_l.append(dict(vsan_id=int(buf.split(' ')[1])))


def _show_fcdomain_role(control_d, switch_l, buf):
    """Determine if switch role is Principal or Subordinate. See _show_fcdomain_vsan()"""
    switch_l[len(switch_l)-1].update(local_switch_info=buf)


def _show_fcdomain_run_time_info(control_d, switch_l, buf):
    """Determine if switch role is Principal or Subordinate. See _show_fcdomain_vsan()"""
    switch_d = switch_l[len(switch_l)-1]
    info_l = gen_util.get_key_val(switch_d, 'TABLE_localswitch_run_info/ROW_localswitch_run_info')
    if info_l is None:
        switch_d.update(TABLE_localswitch_run_info=dict(ROW_localswitch_run_info=[dict(), dict()]))
        return
    sub_control_d = control_d['sub_d']
    buf_l = [b.strip() for b in buf.split(':')]
    sub_d = sub_control_d.get(buf_l.pop(0))
    if sub_d is not None:
        info_l[sub_d['i']].update({sub_d['k']: ':'.join(buf_l)})


def _show_fcdomain_configuration_info(control_d, switch_l, buf):
    """Determine if switch role is Principal or Subordinate. See _show_fcdomain_vsan()"""
    switch_d = switch_l[len(switch_l)-1]
    info_d = gen_util.get_key_val(switch_d, 'TABLE_localswitch_config_info/ROW_localswitch_config_info')
    if info_d is None:
        switch_d.update(TABLE_localswitch_config_info=dict(ROW_localswitch_config_info=dict()))
        return
    sub_control_d = control_d['sub_d']
    buf_l = buf.split(':')
    sub_d = sub_control_d.get(buf_l.pop(0))
    if sub_d is not None:
        sub_d['a'](sub_d, info_d, ':'.join(buf_l))
    sub_d = sub_control_d.get(buf_l.pop(0))
    if sub_d is not None:
        sub_d['a'](sub_d, info_d, ':'.join(buf_l))


def _show_fcdomain_principalswitch_run_info(control_d, switch_l, buf):
    """Parse principalswitch_run_info. See _show_fcdomain_vsan()"""
    switch_d = switch_l[len(switch_l)-1]
    info_d = gen_util.get_key_val(switch_d, 'TABLE_principalswitch_run_info/ROW_principalswitch_run_info')
    if info_d is None:
        switch_d.update(TABLE_principalswitch_run_info=dict(ROW_principalswitch_run_info=dict()))
        return
    buf_l = buf.split(':')
    sub_d = control_d['sub_d'].get(buf_l.pop(0))
    if sub_d is not None:
        info_d.update({sub_d['k']: sub_d['a'](':'.join(buf_l))})


def _show_fcdomain_interface(control_d, switch_l, buf):
    """Parse principalswitch_run_info. See _show_fcdomain_vsan()"""
    if '----------------' in buf:
        return  # It's just the header/content seperator
    switch_d = switch_l[len(switch_l)-1]
    info_l = gen_util.get_key_val(switch_d, 'TABLE_fcdom_interface/ROW_fcdom_interface')
    if info_l is None:
        switch_d.update(TABLE_fcdom_interface=dict(ROW_fcdom_interface=list()))
        return
    buf_l = [b.strip() for b in buf.split(' ')]
    info_l.append({'interface': buf_l[0], 'role': buf_l[1], 'rcf-reject': buf_l[2]})


_show_fcdomain_parse_d = {
    'VSAN': dict(a=_show_fcdomain_vsan),
    'The local switch is': dict(a=_show_fcdomain_role),
    'Local switch run time information':
        dict(a=_show_fcdomain_run_time_info,
             sub_d={'State': dict(k='State', i=0),
                    'Local switch WWN': dict(k='local_switch_wwn', i=0),
                    'Running fabric name': dict(k='running_fabric_name', i=0),
                    'Running priority': dict(k='running_priority', i=1),
                    'Current domain ID': dict(k='current_domain_id', i=1)}),
    'Local switch configuration information':
        dict(a=_show_fcdomain_configuration_info,
             sub_d={'State': dict(k='state', a=_show_fcdomain_config_gen),
                    'FCID persistence': dict(k='fcid_persistence', a=_show_fcdomain_config_gen),
                    'Auto-reconfiguration': dict(k='auto_reconfig', a=_show_fcdomain_config_gen),
                    'Contiguous-allocation': dict(k='contiguous_allocation', a=_show_fcdomain_config_gen),
                    'Configured fabric name': dict(k='config_fabric_name', a=_show_fcdomain_config_gen),
                    'Optimize Mode': dict(k='optimized_mode', k0='optimized_mode_type',
                                          a=_show_fcdomain_config_optimized_mode),
                    'Configured priority': dict(k='config_priority', a=_show_fcdomain_config_gen),
                    'Configured domain ID': dict(k='config_domain_id', k0='config_domain_id_type',
                                                 a=_show_fcdomain_domain_id)}),
    'Principal switch run time information': dict(a=_show_fcdomain_principalswitch_run_info,
                                                  sub_d={'Running priority': dict(k='running_priority',
                                                                                  a=_int_val)}),
    'Interface Role RCF-reject': dict(a=_show_fcdomain_interface)
}


def show_fcdomain(content_l):
    """Parses "show zoneset" output into the equivalent of json.loads("show fcdomain | json | no-more")

    :param content_l: Command output. May or may not include the invocation (command prompt & command)
    :type content_l: list
    :return: Equivalent of json.loads("show fcdomain | json | no-more")
    :rtype: dict
    """
    global _show_fcdomain_parse_d

    action, active_key, switch_l, key_l = None, None, list(), _show_fcdomain_parse_d.keys()
    rd = dict(TABLE_switch_status=dict(ROW_switch_status=switch_l))

    for buf in [gen_util.remove_duplicate_space(b).strip() for b in content_l]:

        # Something new to process?
        for key in key_l:
            if len(buf) >= len(key) and buf[0: len(key)] == key:
                active_key = key
                break

        # Parse it
        if active_key is not None:
            control_d = _show_fcdomain_parse_d[active_key]
            control_d['a'](control_d, switch_l, buf)

    return rd
