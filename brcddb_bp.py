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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.bp
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`brcddb_bp` - Best Practices checking

Primary methods:

best_practice()     Accepts a list of objects and a list of best practice or standards by key to be found in the objects
                    to compare against. Comments categorized. Although any number of categories with any key can be
                    defined, '_e' and '_w', are used in brcdapi.report to determine how comments are to be displayed.
                    '_e' is displayed in bold red font (error_font). '_w' is displayed in bold orange font (warn_font).
                    All other comments are displayed in standard font (std_font).

                    Although intended for determining best practice and standards (drift) violations, it can be used
                    for any application that requires individual key comparisons.

                    see brcddb.app_data.alert_tables for details in consturcting these tables

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
    | 3.0.2     | 14 Nov 2020   | Added ability to parse multiple SFP part numbers for the same rule. This was done |
    |           |               | to accomodated the new secure SFPs for Gen7.                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 26 Jan 2021   | Use standardized brcddb object types                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 17 Jul 2021   | Updated comments only.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '17 Jul 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

import collections
import brcddb.util.util as brcddb_util
import brcddb.util.search as brcddb_search
import brcdapi.log as brcdapi_log
import brcddb.brcddb_switch as brcddb_switch
import brcddb.app_data.alert_tables as al
import brcddb.app_data.bp_tables as bp_tables
import brcddb.util.maps as brcddb_maps
import brcddb.classes.util as brcddb_class_util

HIGH_TEMP_ERROR = 65
HIGH_TEMP_WARN = 60
sfp_rules = None
_alert_tbl = dict()

# The _rule_template table determines how to check SFPs against the MAPS rules.
# Key - KPI of the parameter to test
#   t   The type of test to perform. The test value comes from the MAPS worksheet which is a passed parameter.
#   a   The alert number to add to the port object if the test evaluates True
#   l   True - check only online ports for the test, otherwise, check all enabled ports. The need for a port to be
#       online should be obvious for Rx power but I discovered that offline ports often have very low current draw and
#       very low Tx power. Although I could not find this documented, it seemed to make sense so I didn't look to hard
#       to find documentation for it.
_rule_template = {
    'media-rdp/current': {
        'Current High (mA)': dict(t='>=', a=al.ALERT_NUM.PORT_H_CUR_A, l=False),
        'Current Low (mA)': dict(t='<=', a=al.ALERT_NUM.PORT_L_CUR_A, l=True),
    },
    'media-rdp/voltage': {
        'Voltage High (mV)': dict(t='>=', a=al.ALERT_NUM.PORT_H_VLT_A, l= False),
        'Voltage Low (mV)': dict(t='<=', a=al.ALERT_NUM.PORT_L_VLT_A, l=False),
    },
    'media-rdp/temperature': {
        'Temp High (C)': dict(t='>=', a=al.ALERT_NUM.PORT_H_TEMP_A, l=False),
        'Temp Low (C)': dict(t='<=', a=al.ALERT_NUM.PORT_L_TXP_A, l=False),
    },
    'media-rdp/tx-power': {
        'Tx High (uW)': dict(t='>=', a=al.ALERT_NUM.PORT_H_TXP_A, l=False),
        'Tx Low (uW)': dict(t='<=', a=al.ALERT_NUM.PORT_L_TXP_A, l=True),
    },
    'media-rdp/rx-power': {
        'Rx High (uW)': dict(t='>=', a=al.ALERT_NUM.PORT_H_RXP_A, l=True),
        'Rx Low (uW)': dict(t='<=', a=al.ALERT_NUM.PORT_L_RXP_A, l=True),
    }
}
# The remote SFPs still return the old alarm and warning levels so that's what we will use for the remote media tests.
# It's an ordered dictionary because once we find something to alert on, the remaining rules are skipped. This is to
# prevent a warning alert if an alarm was already found.
_remote_current_rules = collections.OrderedDict()
_remote_current_rules['media-rdp/remote-media-tx-bias-alert/high-alarm'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_CUR_A)
_remote_current_rules['media-rdp/remote-media-tx-bias-alert/high-warning'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_CUR_W)
_remote_current_rules['media-rdp/remote-media-tx-bias-alert/low-alarm'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_CUR_A)
_remote_current_rules['media-rdp/remote-media-tx-bias-alert/low-warning'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_CUR_W)
_remote_voltage_rules = collections.OrderedDict()
_remote_voltage_rules['media-rdp/remote-media-voltage-alert/high-alarm'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_VLT_A)
_remote_voltage_rules['media-rdp/remote-media-voltage-alert/high-warning'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_VLT_W)
_remote_voltage_rules['media-rdp/remote-media-voltage-alert/low-alarm'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_VLT_A)
_remote_voltage_rules['media-rdp/remote-media-voltage-alert/low-warning'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_VLT_W)
_remote_temp_rules = collections.OrderedDict()
_remote_temp_rules['media-rdp/remote-media-temperature-alert/high-alarm'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TEMP_A)
_remote_temp_rules['media-rdp/remote-media-temperature-alert/high-warning'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TEMP_W)
_remote_temp_rules['media-rdp/remote-media-temperature-alert/low-alarm'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TEMP_A)
_remote_temp_rules['media-rdp/remote-media-temperature-alert/low-warning'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TEMP_W)
_remote_tpx_rules = collections.OrderedDict()
_remote_tpx_rules['media-rdp/remote-media-tx-power-alert/high-alarm'] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TXP_A)
_remote_tpx_rules['media-rdp/remote-media-tx-power-alert/high-warning'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TXP_W)
_remote_tpx_rules['media-rdp/remote-media-tx-power-alert/low-alarm'] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TXP_A)
_remote_tpx_rules['media-rdp/remote-media-tx-power-alert/low-warning'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TXP_W)
_remote_rpx_rules = collections.OrderedDict()
_remote_rpx_rules['media-rdp/remote-media-rx-power-alert/high-alarm'] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_RXP_A)
_remote_rpx_rules['media-rdp/remote-media-rx-power-alert/high-warning'] =\
    dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_RXP_W)
_remote_rpx_rules['media-rdp/remote-media-rx-power-alert/low-alarm'] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_RXP_A)
_remote_rpx_rules['media-rdp/remote-media-rx-power-alert/low-warning'] =\
    dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_RXP_W)
_remote_rule_template = {
    # There is either a defect or bad documentation with 'media-rdp/remote-media-current' and
    # 'media-rdp/remote-media-temperature'. Skipping those checks until those leaves are better understood.
    # 'media-rdp/remote-media-current': _remote_current_rules,
    'media-rdp/remote-media-voltage': _remote_voltage_rules,
    'media-rdp/remote-media-tx-power': _remote_tpx_rules,
    'media-rdp/remote-media-rx-power': _remote_rpx_rules,
}


def _amp_in_switch_pair(s_switch_obj, dwwn, switch_pair):
    """Determines if either switch in a switch pair from FabricObj.r_isl_map() is an AMP

    There is no gaurantee that each switch was polled so you can't rely on knowing the switch type. In fact, AMP
    probably isn't ever polled. brcddb_fabric.zone_analysis() adds an alert to logins if the login is to an AMP
    unit. So we spin through all the logins associated with the ports to determine if any of them are an AMP.
    :param s_switch_obj: Source switch object
    :type s_switch_obj: brcddb.classes.switch.switch_obj
    :param dwwn: WWN of destination switch
    :type dwwn: str
    :param switch_pair: Dictionary of switches and trunks as returned from brcddb.clases.switch.c_trunk_map()
    :type switch_pair: dict
    :return: True if any of the ports are connected to an AMP
    :rtype: bool
    """
    fab_obj = s_switch_obj.r_fabric_obj()
    for k in switch_pair.keys():
        tl = switch_pair.get(k)
        for i in range(0, len(tl)):
            for x in range(0, 2):
                if tl[i][x] is not None:
                    for login_obj in tl[i][x].r_login_objects():
                        for alert_obj in login_obj.r_alert_objects():
                            if alert_obj.alert_num() == al.ALERT_NUM.LOGIN_AMP:
                                return True
    return False

# Cases for bp_special(). For each case method:


def _isl_num_links(obj, t_obj):
    """Check to see if the number of ISL in each trunk group is the same

    :param obj: Switch object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    :return: List of alert dictionaries {'a': alert number, 'p0': p0, 'p1': p1, 'k': '_isl_map'}
    :rtype: list
    """
    r_list = list()
    # Validate input
    obj_type = brcddb_class_util.get_simple_class_type(obj)
    if obj_type is None:
        obj_type = str(type(obj))
    if obj_type != 'SwitchObj':
        brcdapi_log.exception('Invalid object type. Expected switch_obj. Received: ' + obj_type, True)
        return r_list

    proj_obj = obj.r_project_obj()
    isl_map = obj.c_trunk_map()
    for k in isl_map.keys():
        switch_pair = isl_map.get(k)
        if _amp_in_switch_pair(obj, k, switch_pair):
            continue
        isls_per_trunk = list()
        for k1 in switch_pair.keys():
            tl = switch_pair.get(k1)
            for trunk in tl:
                isls_per_trunk.append(len(trunk))
        if len(brcddb_util.remove_duplicates(isls_per_trunk)) > 1:
            r_list.append({'a': t_obj.get('m'),
                           'p0': brcddb_switch.best_switch_name(obj),
                           'p1': brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)),
                           'k': 'trunk'})
    return r_list


def _isl_bw(obj, t_obj):
    """Check to see that all trunk masters logged in at the same speed

    :param obj: Switch object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    :return: List of alert dictionaries {'a': alert number, 'p0': p0, 'p1': p1, 'k': '_isl_map'}
    :rtype: list
    """
    r_list = list()
    # Validate input
    obj_type = brcddb_class_util.get_simple_class_type(obj)
    if obj_type is None:
        obj_type = str(type(obj))
    if obj_type != 'SwitchObj':
        brcdapi_log.exception('Invalid object type. Expected switch_obj. Received: ' + obj_type, True)
        return r_list

    proj_obj = obj.r_project_obj()
    isl_map = obj.c_trunk_map()
    for k in isl_map.keys():
        switch_pair = isl_map.get(k)
        if _amp_in_switch_pair(obj, k, switch_pair):
            continue
        speeds = list()
        for k1 in switch_pair.keys():
            try:
                s = switch_pair.get(k1)[0][0].r_get('fibrechannel/speed')
                if s is not None:
                    speeds.append(s)
            except:
                pass  # We get here if all switches in the project were not polled
        if len(brcddb_util.remove_duplicates(speeds)) > 1:
            r_list.append({'a': t_obj.get('m'),
                           'p0': brcddb_switch.best_switch_name(obj),
                           'p1': brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)),
                           'k': 'trunk'})
    return r_list


def _isl_fru(obj, t_obj):
    """Check to see if the trunks land on different FRUs. Ignores connections to AMP and fixed port switches

    :param obj: Switch object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    :return: List of alert dictionaries {'a': alert number, 'p0': p0, 'p1': p1, 'k': '_isl_map'}
    :rtype: list
    """
    r_list = list()
    # Validate input
    obj_type = brcddb_class_util.get_simple_class_type(obj)
    if obj_type is None:
        obj_type = str(type(obj))
    if obj_type != 'SwitchObj':
        brcdapi_log.exception('Invalid object type. Expected switch_obj. Received: ' + obj_type, True)
        return r_list

    proj_obj = obj.r_project_obj()
    isl_map = obj.c_trunk_map()
    for k in isl_map.keys():
        switch_pair = isl_map.get(k)
        if _amp_in_switch_pair(obj, k, switch_pair):
            continue
        slots = list()
        for k1 in switch_pair.keys():
            tl = switch_pair.get(k1)
            for trunk in tl:
                if trunk[0] is not None:
                    slots.append(trunk[0].r_obj_key().split('/')[0])
        if len(brcddb_util.remove_duplicates(slots)) == 1 and slots[0] != '0':
            r_list.append({'a': t_obj.get('m'),
                           'p0': brcddb_switch.best_switch_name(obj),
                           'p1': brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)),
                           'k': 'trunk'})
    return r_list


def _isl_redundant(obj, t_obj):
    """Check to see if there are at least two ISLs between switch pairs. Ignores connections to AMP

    :param obj: Switch object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    :return: List of alert dictionaries {'a': alert number, 'p0': p0, 'p1': p1, 'k': '_isl_map'}
    :rtype: list
    """
    r_list = list()
    # Validate input
    obj_type = brcddb_class_util.get_simple_class_type(obj)
    if obj_type is None:
        obj_type = str(type(obj))
    if obj_type != 'SwitchObj':
        brcdapi_log.exception('Invalid object type. Expected switch_obj. Received: ' + obj_type, True)
        return r_list

    proj_obj = obj.r_project_obj()
    isl_map = obj.c_trunk_map()
    for k in isl_map.keys():
        switch_pair = isl_map.get(k)
        if _amp_in_switch_pair(obj, k, switch_pair):
            continue
        if len(list(switch_pair.keys())) == 1:
            r_list.append({'a': t_obj.get('m'),
                           'p0': brcddb_switch.best_switch_name(obj),
                           'p1': brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)),
                           'k': 'trunk'})
    return r_list


def _fc16_48_haa_p8(obj, t_obj):
    """Check to see if there is a pre-2015 FC16-32 blade with an SFP matching S/N HAA* in port 8

    :param obj: Chassis object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    :return: Alerts are applied to the ports found that meet this criteria so an empty list is always returned
    :rtype: list
    """
    global _alert_tbl

    # Get all the ports number 8 in for FC16-32 blades matching P/N 60-1001945-* (built before 2016)
    temp_l = brcddb_util.convert_to_list(obj.r_get('brocade-fru/blade'))
    fru_list = brcddb_search.match(temp_l, 'part-number', '60-1001945-*', False, 'wild')
    temp_l = [str(fru.get('slot-number')) for fru in fru_list]

    # Get a list of ports we just figured out above that have an SFP matching S/N HAA*
    if len(temp_l) > 0:
        lt = [
            {'k': 'media-rdp/serial-number', 'v': 'HAA*', 't': 'wild'},
            {'k': 'fibrechannel/name', 'v': '[' + ','.join(temp_l) + ']/(8 | 32)', 't': 'regex-m'}
        ]
        ml = brcddb_search.match_test(obj.r_port_objects(), lt, 'and')
        for port_obj in ml:
            port_obj.s_add_alert(_alert_tbl, t_obj.get('m'))

    return list()


def _chassis_fru_check(obj, t_obj):
    """Check temperature sensors and H/W faults.

    :param obj: Chassis object from the object list, obj_list, passed to best_practice()
    :type obj: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice().
    :type t_obj: dict
    :return: List of alert dictionaries {'a': alert number, 'p0': p0, 'p1': p1, 'k': '_isl_map'}
    :rtype: list
    """
    global _alert_tbl

    r_list = list()
    # Blades
    for d in brcddb_util.convert_to_list(obj.r_get('brocade-fru/blade')):
        v = str(d.get('blade-state'))
        if 'ault' in v:  # Sometimes it's 'fault' and sometimes it's 'Fault'.
            r_list.append({'a': t_obj.get('m'), 'p0': 'blade: ' + str(d.get('slot-number')), 'p1': v, 'k': None})

    # Fans
    for d in brcddb_util.convert_to_list(obj.r_get('brocade-fru/fan')):
        v = str(d.get('operational-state'))
        if v.upper() != 'OK':
            r_list.append({'a': t_obj.get('m'), 'p0': 'Fan: ' + str(d.get('unit-number')), 'p1': v, 'k': None})

    # Power Supply
    for d in brcddb_util.convert_to_list(obj.r_get('brocade-fru/power-supply')):
        v = str(d.get('operational-state'))
        if v.upper() != 'OK':
            r_list.append({'a': t_obj.get('m'), 'p0': 'Power Supply: ' + str(d.get('unit-number')), 'p1': v, 'k': None})

    # Temp Sensor
    for d in brcddb_util.convert_to_list(obj.r_get('brocade-fru/sensor')):
        v = str(d.get('state'))
        if v.upper() != 'ABSENT':
            if v.upper() != 'OK':
                p0 = 'Temp Sensor ID: ' + str(d.get('id')) + \
                     str(d.get('slot-number')) if d.get('slot-number') is not None else ''
                r_list.append({'a': t_obj.get('m'), 'p0': p0, 'p1': v, 'k': None})
            v1 = d.get('temperature')
            if isinstance(v1, (int, float)):
                if v1 >= HIGH_TEMP_WARN:
                    a = al.ALERT_NUM.CHASSIS_TEMP_ERROR if v1 >= HIGH_TEMP_ERROR else al.ALERT_NUM.CHASSIS_TEMP_WARN
                    p0 = '' if d.get('slot-number') is None else 'Slot: ' + str(d.get('slot-number')) + ' '
                    p0 += '' if d.get('id') is None else 'ID: ' + str(d.get('id'))
                    r_list.append({'a': a , 'p0': p0, 'p1': v1, 'k': None})

    return r_list


def _check_sfps(obj_list, t_obj):
    """Checks SFP levels and adds appropriate alerts to port objects

    :param obj_list: Port object
    :type obj_list: list
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    """
    global _rule_template, sfp_rules, _alert_tbl

    if sfp_rules is None or obj_list is None:
        return

    # Perform all the checks for the SFPs on the switch.
    enabled_ports = brcddb_search.match_test(obj_list, bp_tables.is_enabled)  # SFP data is not valid for disabled ports
    for rule in sfp_rules:
        group = 'Unkonwn' if rule.get('Group') is None else rule.get('Group')
        try:
            pn_l = rule.get('Mfg. P/N')
            if pn_l is not None and pn_l != '':
                for pn in [p.strip() for p in pn_l.split(',')]:
                    plist = brcddb_search.match_test(enabled_ports,
                                                     {'k': 'media-rdp/part-number', 't': 'exact', 'v': pn})
                    if len(plist) > 0:
                        online_plist = brcddb_search.match_test(plist, bp_tables.is_online)
                        for k0, obj_0 in _rule_template.items():
                            for k1, obj_1 in obj_0.items():
                                val = float(rule.get(k1))  # The threshold to test against
                                m = obj_1.get('a')  # Alert number
                                tlist = online_plist if obj_1.get('l') else plist
                                for p_obj in brcddb_search.match_test(tlist, {'k': k0, 't': obj_1.get('t'), 'v': val}):
                                    p_obj.s_add_alert(_alert_tbl, m, k0, p_obj.r_get(k0), val)
            else:
                brcdapi_log.log('Missing P/N in ' + sfp_rules + ', Group: ' + str(group), True)

        except:
            brcdapi_log.exception('Invalid SFP rules file ' + sfp_rules + '. Group: ' + str(group), True)
            return

    return


def _check_remote_sfps(obj_list, t_obj):
    """Checks remote SFP levels and adds appropriate alerts to port objects

    :param obj_list: List of port object
    :type obj_list: brcddb.classes.PortObj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    """
    global _remote_rule_template, _alert_tbl

    for p_obj in brcddb_search.match_test(obj_list, bp_tables.is_online):
        v = p_obj.r_get('media-rdp/remote-media-voltage-alert/high-alarm')
        if v is None or v == 0:
            continue  # Sometimes threshold data is all 0 when it's not valid. Just checking the voltage makes it easy

        # Check threshold levels
        for k, rules in _remote_rule_template.items():
            try:
                v = p_obj.r_get(k)
                if v is None:
                    continue
                for k1, rules_1 in rules.items():
                    tv = p_obj.r_get(k1)
                    if rules_1.get('t') == '>=':
                        if v >= tv:
                            p_obj.s_add_alert(_alert_tbl, rules_1.get('a'), k1, v, tv)
                            break
                    else:
                        if v <= tv:
                            p_obj.s_add_alert(_alert_tbl, rules_1.get('a'), k1, v, tv)
                            break
            except:
                pass  # Remote data wasn't provided if we get here.


_bp_special_case_tbl = {
    'ISL_NUM_LINKS': _isl_num_links,
    'ISL_BW': _isl_bw,
    'ISL_FRU': _isl_fru,
    'ISL_REDUNDANT': _isl_redundant,
    'FC16_32_HAA_SFP_P8': _fc16_48_haa_p8,
    'SFP_HEALTH_CHECK': _check_sfps,
    'REMOTE_SFP_HEALTH_CHECK': _check_remote_sfps,
    'CHASSIS_FRU_CHECK': _chassis_fru_check,
}
_bp_special_process_by_list = ('SFP_HEALTH_CHECK', 'REMOTE_SFP_HEALTH_CHECK')


def _bp_special(obj_list, t_obj):
    """Processes special best practice tests.

    Best practice special tests require more than just a simple comparison of a key value. Programmers can add a
    special type to the bp_tables and add it to be_special_case_tbl. Add a method to do whatever you want.
    :param obj_list: A list of dictionaries or brcdapi objects to search. Must all be the same type
    :type obj_list: (dict, list, tuple)
    :param t_obj: Best practice rules. See brcddb.app_data.bp_tables for details
    :type t_obj: dict
    """
    global _alert_tbl

    sc = t_obj.get('s')
    if sc in _bp_special_process_by_list:
        _bp_special_case_tbl[sc](obj_list, t_obj)
    else:
        for obj in obj_list:
            for a in  _bp_special_case_tbl[sc](obj, t_obj):
                obj.s_add_alert(_alert_tbl, a.get('a'), a.get('k'), a.get('p0'), a.get('p1'))


def _fdmi_enabled(obj_list, t_obj):
    """Check to see if FDMI should be enabled on the attached device.

    :param obj_list: List of login objects, brcddb.classes.login.LoginObj, passed to best_practice()
    :type obj_list: list
    :param t_obj: Individual test item from the test_list passed to best_practice().
    :type t_obj: dict
    :return: List of port objects, brcddb.classes.port.PortObj, matching the test criteria in t_obj
    :rtype: list
    """
    ret_list = list()
    for obj in brcddb_search.match_test(obj_list, t_obj.get('l'), t_obj.get('logic')):
        port_obj = obj.r_port_obj()
        if port_obj is None:
            continue
        wwn = obj.r_obj_key()
        try:
            if port_obj.r_get('fibrechannel/neighbor/wwn')[1] == wwn:
                if obj.r_fabric_obj().r_fdmi_port_obj(wwn) is None:
                    ret_list.append(port_obj)
        except:
            if obj.r_fabric_obj().r_fdmi_port_obj(wwn) is None:
                ret_list.append(port_obj)
    return ret_list


_bp_special_list_case_tbl = dict(FDMI_ENABLED=_fdmi_enabled)


def _bp_special_list(obj_list, t_obj):
    """Processes special best practice tests. Similar to _bp_special() but the associated methods return a list of all
    objects matching the test criteria and the same alert is applied to

    :param obj_list: A list of dictionaries or brcdapi objects to search. Must all be the same type
    :type obj_list: (dict, list, tuple)
    :param t_obj: Best practice rules. See brcddb.app_data.bp_tables for details
    :type t_obj: dict
    """
    global _alert_tbl

    anum = t_obj.get('m')
    k = brcddb_util.convert_to_list(t_obj.get('l'))[0].get('k')
    p0 = t_obj.get('p0')
    p1 = t_obj.get('p1')
    for obj in _bp_special_list_case_tbl[t_obj.get('s')](obj_list, t_obj):
        obj.s_add_alert(_alert_tbl, anum, k, obj.r_get(p0), obj.r_get(p1))


def _check_best_practice(obj_list, test_list):
    """Checks for defined conditions and adds an alert for every out of bounds condition.

    :param obj_list: A list of dictionaries or brcdapi objects to search. Must all be the same type
    :type obj_list: dict, list, tuple
    :param test_list: Pointer to table of best practice rules. See brcddb.app_data.bp_tables for details
    :type test_list: dict
    """
    global _alert_tbl

    # Validate user input
    if len(obj_list) == 0:
        return
    if not isinstance(test_list, (list, tuple)):
        brcdapi_log.exception('Invalid test_list type, ' + str(type(test_list)), True)
        return


    # Spin through each item in the test_list and perform the specified test
    for t_obj in test_list:
        if 'skip' in t_obj and t_obj.get('skip'):
            continue
        special = t_obj.get('s')
        if special is not None:
            if special in _bp_special_case_tbl:
                _bp_special(obj_list, t_obj)
            elif special in _bp_special_list_case_tbl:
                _bp_special_list(obj_list, t_obj)
            else:
                brcdapi_log.exception(
                    'Unknown special test case: ' + str(special) + ', type: ' + str(type(special)),
                    True)

        else:
            for obj in brcddb_search.match_test(obj_list, t_obj.get('l'), t_obj.get('logic')):
                # See documentation in brcddb.app_data.bp_tables for an explanation of 'm', 'p0', 'p0h', 'p1', & 'p1h'
                p0 = t_obj.get('p0h') if t_obj.get('p0h') is not None else obj.r_get(t_obj.get('p0'))
                p1 = t_obj.get('p1h') if t_obj.get('p1h') is not None else obj.r_get(t_obj.get('p1'))
                obj.s_add_alert(_alert_tbl, t_obj.get('m'), brcddb_util.convert_to_list(t_obj.get('l'))[0].get('k'),
                               p0, p1)


def best_practice(a_tbl, proj_obj):
    """Checks for defined conditions and adds an alert for every out of bounds condition.

    :param a_tbl: The table that defines this alert. See brcddb.classes.alert.AlertObj
    :type a_tbl: dict
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    global _alert_tbl

    _alert_tbl = a_tbl  # I could have handled this better but I'm not fixing working code.

    brcdapi_log.log('Checking best practices', True)
    _check_best_practice(proj_obj.r_port_objects(), bp_tables.port_tbl)
    _check_best_practice(proj_obj.r_switch_objects(), bp_tables.switch_tbl)
    _check_best_practice(proj_obj.r_login_objects(), bp_tables.login_node_tbl)
    _check_best_practice(proj_obj.r_fabric_objects(), bp_tables.fabric_tbl)
    _check_best_practice(proj_obj.r_chassis_objects(), bp_tables.chassis_tbl)
    brcddb_maps.maps_dashboard_alerts(proj_obj)
