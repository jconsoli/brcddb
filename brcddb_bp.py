"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Best Practices checking

This module is primarily contains tables that define how best practice checks are to be performed. There are two
methods for checking best practices:

    * Complex checks which require
    * Checks that can be defined with a single dictionary to be passed to brcddb.util.search

    The alert levels (error, warning, informational) and display formatting is defined in brcddb.app_data.alert_tables.

**WARNING**

This module imports other modules from the same directory. To avoid circular imports, this module should only be
imported by applications uses the brcddb libraries not no any of the library modules within brcddb.

**Public Methods & Data**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| best_practice         | Checks for defined conditions and adds an alert for every out of bounds condition.        |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Fixed speed search terms.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 16 Jun 2024   | Added bp_sheet, ability to specify the sheet to read, in best_practice()              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 26 Jun 2024   | Check firmware in chassis instead of switch (new in FOS 9.?)                          |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 20 Oct 2024   | Added more error checking.                                                            |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '20 Oct 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

import collections
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.util as brcdapi_util
import brcdapi.excel_util as excel_util
import brcddb.report.utils as report_utils
import brcddb.util.util as brcddb_util
import brcddb.util.search as brcddb_search
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_switch as brcddb_switch
import brcddb.brcddb_login as brcddb_login
import brcddb.app_data.alert_tables as al
import brcddb.util.maps as brcddb_maps
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_fabric as brcddb_fabric

_high_temp_error, _high_temp_warn = 1000, 1000
_sfp_rules, _sfp_file = None, None
_alert_tbl_d = dict()

is_no_light = dict(k=brcdapi_util.fc_state, t='exact', v='no_light')
is_asn = dict(k=brcdapi_util.fc_auto_neg, t='bool', v=True)
_port_bit_errors = (brcdapi_util.stats_in_crc,
                    brcdapi_util.stats_crc,
                    brcdapi_util.stats_fec_un)
_port_framing_errors = (brcdapi_util.stats_ios,
                        brcdapi_util.stats_long,
                        brcdapi_util.stats_tunc,
                        brcdapi_util.stats_addr,
                        brcdapi_util.stats_delimiter,
                        brcdapi_util.stats_enc_disp,
                        brcdapi_util.stats_bad_eof,
                        brcdapi_util.stats_enc,
                        brcdapi_util.stats_itw,
                        brcdapi_util.stats_seq)
_port_logical_errors = (brcdapi_util.stats_in_reset,
                        brcdapi_util.stats_out_reset,
                        brcdapi_util.stats_off_seq,
                        brcdapi_util.stats_out_off_seq,
                        brcdapi_util.stats_rdy,
                        brcdapi_util.stats_multicast_to,
                        brcdapi_util.stats_in_lcs,
                        brcdapi_util.stats_buf_full,
                        brcdapi_util.stats_f_busy,
                        brcdapi_util.stats_p_busy,
                        brcdapi_util.stats_f_rjt,
                        brcdapi_util.stats_p_rjt,
                        brcdapi_util.stats_link_fail,
                        brcdapi_util.stats_loss_sig,
                        brcdapi_util.stats_loss_sync,
                        brcdapi_util.stats_lli,
                        brcdapi_util.stats_fpr,
                        brcdapi_util.stats_to,
                        brcdapi_util.stats_trans,
                        brcdapi_util.stats_nos_in,
                        brcdapi_util.stats_nos_out)

"""The _rule_template table determines how to check SFPs against the MAPS rules.
Key - KPI of the parameter to test
  t   The type of test to perform. The test value comes from the MAPS worksheet which is a passed parameter.
  a   The alert number to add to the port object if the test evaluates True
  l   True - check only online ports for the test, otherwise, check all enabled ports. The need for a port to be
      online should be obvious for Rx power but I discovered that offline ports often have very low current draw and
      very low Tx power. Although I could not find this documented, it seemed to make sense so I didn't look to hard
      to find documentation for it."""
_rule_template = {
    'media-rdp/current': {
        'Current High (mA)': dict(t='>=', a=al.ALERT_NUM.PORT_H_CUR_A, l=False),
        'Current Low (mA)': dict(t='<=', a=al.ALERT_NUM.PORT_L_CUR_A, l=True),
    },
    'media-rdp/voltage': {
        'Voltage High (mV)': dict(t='>=', a=al.ALERT_NUM.PORT_H_VLT_A, l=False),
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
"""The remote SFPs still return the old alarm and warning levels so that's what is used for the remote media tests.
I looked into matching the SFP part number to the part numbers defined in sfp_rules_rxx.xlsx. I already had legacy
code that did the check against values returned by the SFP so I took the easy way out and used that code. If erroneous
alarms becomes a problem, I'll revisit this. For now, this is good enough.

_remote_current_rules is an ordered dictionary because once something to alert on is found, the remaining rules are
skipped. This is to prevent cluttering the report with alarms."""
_remote_current_rules = collections.OrderedDict()
_remote_current_rules[brcdapi_util.sfp_cur_high_alarm] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_CUR_A)
_remote_current_rules[brcdapi_util.sfp_cur_high_warn] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_CUR_W)
_remote_current_rules[brcdapi_util.sfp_cur_low_alarm] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_CUR_A)
_remote_current_rules[brcdapi_util.sfp_cur_low_warn] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_CUR_W)
_remote_voltage_rules = collections.OrderedDict()
_remote_voltage_rules[brcdapi_util.sfp_volt_high_alarm] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_VLT_A)
_remote_voltage_rules[brcdapi_util.sfp_volt_high_warn] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_VLT_W)
_remote_voltage_rules[brcdapi_util.sfp_volt_low_alarm] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_VLT_A)
_remote_voltage_rules[brcdapi_util.sfp_volt_low_warn] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_VLT_W)
_remote_temp_rules = collections.OrderedDict()
_remote_temp_rules[brcdapi_util.sfp_temp_high_alarm] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TEMP_A)
_remote_temp_rules[brcdapi_util.sfp_temp_high_warn] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TEMP_W)
_remote_temp_rules[brcdapi_util.sfp_temp_low_alarm] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TEMP_A)
_remote_temp_rules[brcdapi_util.sfp_temp_low_warn] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TEMP_W)
_remote_tpx_rules = collections.OrderedDict()
_remote_tpx_rules[brcdapi_util.sfp_txp_high_alarm] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TXP_A)
_remote_tpx_rules[brcdapi_util.sfp_txp_high_warn] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_TXP_W)
_remote_tpx_rules[brcdapi_util.sfp_txp_low_alarm] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TXP_A)
_remote_tpx_rules[brcdapi_util.sfp_txp_low_warn] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_TXP_W)
_remote_rpx_rules = collections.OrderedDict()
_remote_rpx_rules[brcdapi_util.sfp_rxp_high_alarm] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_RXP_A)
_remote_rpx_rules[brcdapi_util.sfp_rxp_high_warn] = dict(t='>=', a=al.ALERT_NUM.REMOTE_PORT_H_RXP_W)
_remote_rpx_rules[brcdapi_util.sfp_rxp_low_alarm] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_RXP_A)
_remote_rpx_rules[brcdapi_util.sfp_rxp_low_warn] = dict(t='<=', a=al.ALERT_NUM.REMOTE_PORT_L_RXP_W)
_remote_rule_template = {
    # There is either a defect or bad documentation with 'media-rdp/remote-media-current' and
    # 'media-rdp/remote-media-temperature',  Skipping these checks until these leaves are better understood.
    # 'media-rdp/remote-media-current': _remote_current_rules,  Something is wrong here
    'media-rdp/remote-media-voltage': _remote_voltage_rules,
    'media-rdp/remote-media-tx-power': _remote_tpx_rules,
    'media-rdp/remote-media-rx-power': _remote_rpx_rules,
}


def _amp_in_switch_pair(switch_pair):
    """Determines if either switch in a switch pair from FabricObj.r_isl_map() is an AMP

    There is no guarantee that each switch was polled, so you can't rely on knowing the switch type. In fact, AMP
    probably isn't ever polled. brcddb_fabric.zone_analysis() adds an alert to logins if the login is to an AMP
    unit. So we spin through all the logins associated with the ports to determine if any of them are an AMP.
    :param switch_pair: Dictionary of switches and trunks as returned from brcddb.classes.switch.c_trunk_map()
    :type switch_pair: dict
    :return: True if any of the ports are connected to an AMP
    :rtype: bool
    """
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


############################################################
#                                                          #
#        Rule check actions, ('a' in _bp_tbl_d)            #
#                                                          #
############################################################
def _isl_num_links(rule, switch_obj_l, t_obj):
    """Check to see if the number of ISL in each trunk group is the same (balanced)

    :param rule: Rule name or alert number
    :type rule: str, int
    :param switch_obj_l: List of switch objects
    :type switch_obj_l: brcddb.classes.switch.switch_obj
    :param t_obj: Individual test item from the test_list passed to best_practice(). Not used
    :type t_obj: dict
    """
    global _alert_tbl_d

    for switch_obj in switch_obj_l:

        proj_obj = switch_obj.r_project_obj()
        isl_map = switch_obj.c_trunk_map()
        for k in isl_map.keys():
            switch_pair = isl_map.get(k)
            if _amp_in_switch_pair(switch_pair):
                continue
            isls_per_trunk = list()
            for k1 in switch_pair.keys():
                tl = switch_pair.get(k1)
                for trunk in tl:
                    isls_per_trunk.append(len(trunk))
            if len(gen_util.remove_duplicates(isls_per_trunk)) > 1:
                switch_obj.s_add_alert(_alert_tbl_d,
                                       al.ALERT_NUM.SWITCH_ISL_IMBALANCE,
                                       key='trunk',
                                       p0=brcddb_switch.best_switch_name(switch_obj),
                                       p1=brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)))


def _isl_bw(rule, switch_obj_l, t_obj):
    """Check to see that all trunk masters logged in at the same speed. See _isl_num_links() for parameters"""
    global _alert_tbl_d

    for switch_obj in switch_obj_l:

        proj_obj = switch_obj.r_project_obj()
        isl_map = switch_obj.c_trunk_map()
        for k in isl_map.keys():
            switch_pair = isl_map.get(k)
            if _amp_in_switch_pair(switch_pair):
                continue
            speeds = list()
            for k1 in switch_pair.keys():
                try:
                    s = switch_pair.get(k1)[0][0].r_get('fibrechannel/speed')
                    if s is not None:
                        speeds.append(s)
                except TypeError:
                    pass  # We get here if all switches in the project were not polled
            if len(gen_util.remove_duplicates(speeds)) > 1:
                switch_obj.s_add_alert(_alert_tbl_d,
                                       al.ALERT_NUM.SWITCH_ISL_BW,
                                       key='trunk',
                                       p0=brcddb_switch.best_switch_name(switch_obj),
                                       p1=brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)))


def _isl_fru(rule, obj_l, t_obj):
    """Check to see if the trunks land on different FRUs. Ignores connections to AMP and fixed port switches. See \
    _isl_num_links() for parameters"""
    global _alert_tbl_d

    for switch_obj in obj_l:
        proj_obj = switch_obj.r_project_obj()
        isl_map = switch_obj.c_trunk_map()
        for k in isl_map.keys():
            switch_pair = isl_map.get(k)
            if _amp_in_switch_pair(switch_pair):
                continue
            slots = list()
            for k1 in switch_pair.keys():
                tl = switch_pair.get(k1)
                for trunk in tl:
                    if trunk[0] is not None:
                        slots.append(trunk[0].r_obj_key().split('/')[0])
            if len(gen_util.remove_duplicates(slots)) == 1 and slots[0] != '0':
                switch_obj.s_add_alert(_alert_tbl_d,
                                       al.ALERT_NUM.SWITCH_ISL_FRU,
                                       key='trunk',
                                       p0=brcddb_switch.best_switch_name(switch_obj),
                                       p1=brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)))


def _isl_redundant(rule, switch_obj_l, t_obj):
    """Check to see if there are at least two ISLs between switch pairs. See _isl_num_links() for parameters"""
    global _alert_tbl_d

    for switch_obj in switch_obj_l:
        proj_obj = switch_obj.r_project_obj()
        isl_map = switch_obj.c_trunk_map()
        for k in isl_map.keys():
            switch_pair = isl_map.get(k)
            if _amp_in_switch_pair(switch_pair):
                continue
            if len(list(switch_pair.keys())) == 1:
                switch_obj.s_add_alert(_alert_tbl_d,
                                       al.ALERT_NUM.SWITCH_ISL_REDUNDANT,
                                       k='trunk',
                                       p0=brcddb_switch.best_switch_name(switch_obj),
                                       p1=brcddb_switch.best_switch_name(proj_obj.r_switch_obj(k)))


def _fc16_48_haa_p8(rule, chassis_obj_l, t_obj):
    """Check to see if there is a pre-2015 FC16-32 blade with an SFP matching S/N HAA* in port 8. See _isl_num_links() \
    for parameters"""
    global _alert_tbl_d

    for chassis_obj in chassis_obj_l:
        temp_l = gen_util.convert_to_list(chassis_obj.r_get(brcdapi_util.fru_blade))
        fru_list = brcddb_search.match(temp_l, 'part-number', '60-1001945-*', False, 'wild')
        temp_l = [str(fru.get('slot-number')) for fru in fru_list]

        # Get a list of ports we just figured out above that have an SFP matching S/N HAA*
        if len(temp_l) > 0:
            lt = [dict(k=brcdapi_util.sfp_sn, v='HAA*', t='wild'),
                  dict(k=brcdapi_util.fc_name, v='[' + ','.join(temp_l) + ']/(8 | 32)', t='regex-m')]
            ml = brcddb_search.match_test(chassis_obj.r_port_objects(), lt, 'and')
            for port_obj in ml:
                port_obj.s_add_alert(_alert_tbl_d, al.ALERT_NUM.PORT_SFP_HAA_F16_32_P8)


def _chassis_fru_check(rule, chassis_obj_l, t_obj):
    """Check temperature sensors and H/W faults. See _isl_num_links() for parameters"""
    global _alert_tbl_d, _high_temp_error, _high_temp_warn

    for chassis_obj in chassis_obj_l:
        # Blades
        for d in gen_util.convert_to_list(chassis_obj.r_get(brcdapi_util.fru_blade)):
            v = str(d.get('blade-state'))
            if 'ault' in v:  # Sometimes it's 'fault' and sometimes it's 'Fault'.
                chassis_obj.s_add_alert(_alert_tbl_d,
                                        al.ALERT_NUM.CHASSIS_FRU,
                                        p0='blade: ' + str(d.get('slot-number')),
                                        p1=v)

        # Fans
        for d in gen_util.convert_to_list(chassis_obj.r_get(brcdapi_util.fru_fan)):
            v = str(d.get('operational-state'))
            if v.upper() != 'OK':
                chassis_obj.s_add_alert(_alert_tbl_d,
                                        al.ALERT_NUM.CHASSIS_FRU,
                                        p0='Fan: ' + str(d.get('unit-number')),
                                        p1=v)

        # Power Supply
        for d in gen_util.convert_to_list(chassis_obj.r_get(brcdapi_util.fru_ps)):
            v = str(d.get('operational-state'))
            if v.upper() != 'OK':
                chassis_obj.s_add_alert(_alert_tbl_d,
                                        al.ALERT_NUM.CHASSIS_FRU,
                                        p0='Power Supply: ' + str(d.get('unit-number')),
                                        p1=v)

        # Temp Sensor
        for d in gen_util.convert_to_list(chassis_obj.r_get(brcdapi_util.fru_sensor)):
            v = str(d.get('state'))
            if v.upper() != 'ABSENT':
                if v.upper() != 'OK':
                    p0 = 'Temp Sensor ID: ' + str(d.get('id')) + \
                         str(d.get('slot-number')) if d.get('slot-number') is not None else ''
                    chassis_obj.s_add_alert(_alert_tbl_d, al.ALERT_NUM.CHASSIS_FRU, p0=p0, p1=v)
                v1 = d.get('temperature')
                if isinstance(v1, (int, float)):
                    if v1 >= _high_temp_warn:
                        a = al.ALERT_NUM.CHASSIS_TEMP_ERROR if v1 >= _high_temp_error else \
                            al.ALERT_NUM.CHASSIS_TEMP_WARN
                        p0 = '' if d.get('slot-number') is None else 'Slot: ' + str(d.get('slot-number')) + ' '
                        p0 += '' if d.get('id') is None else 'ID: ' + str(d.get('id'))
                        chassis_obj.s_add_alert(_alert_tbl_d, a, p0=p0)


def _chassis_err_log(rule, chassis_obj_l, t_obj):
    """Check the error log for alerts. See _isl_num_links() for parameters"""
    global _alert_tbl_d

    sev_type_d = dict()  # The severity levels to look for
    try:
        buf, remainder_buf = gen_util.paren_content(rule[rule.index('('):], p_remove=True)
        def_l = [b.strip().lower() for b in buf.split(',')]
        look_back_sec = int(def_l.pop(0))
        for sev_level in def_l:
            alert_num = al.ALERT_NUM.ERROR_LOG_ERROR if 'error' in sev_level or 'critical' in sev_level else \
                al.ALERT_NUM.ERROR_LOG_WARN if 'warn' in sev_level else al.ALERT_NUM.ERROR_LOG_INFO
            sev_type_d.update({sev_level: alert_num})
    except (ValueError, TypeError, IndexError):
        brcdapi_log.log('Best practice rule ' + rule + ' is invalid in the best practice workbook.', echo=True)
        return

    for chassis_obj in chassis_obj_l:
        check_time = int(gen_util.date_to_epoch(chassis_obj.r_project_obj().r_date(), fmt=1)) - look_back_sec
        for error_d in reversed(chassis_obj.r_get('brocade-logging/error-log', list())):
            # I've never seen the error log ordered any other way than by oldest first. Spinning through it in
            # reverse allows me to bail out as soon as I'm past alerts we're not looking for.
            if int(gen_util.date_to_epoch(error_d['time-stamp'], fmt=8)) < check_time:
                break
            try:  # There are other formats for non-port specific errors. Some day I may get to them
                al_num = sev_type_d.get(error_d['severity-level'])
                if isinstance(al_num, int):
                    event_info_l = error_d['event-info'].split(' ')
                    # Just capturing port messages in the error log but this is set up for other errors.
                    obj = chassis_obj.r_port_obj(event_info_l[1]) if event_info_l[0] == 'PORT' else None
                    if obj is not None:
                        obj.s_add_alert(_alert_tbl_d, al_num, p0=error_d['message-id'], p1=error_d['message-text'])
            except (KeyError, ValueError, IndexError):
                pass

    return


def _min_firmware(rule, chassis_obj_l, t_obj):
    """Validate the firmware level. See _isl_num_links() for parameters."""
    for chassis_obj in chassis_obj_l:
        fos_version = brcddb_chassis.firmware_version(chassis_obj)
        if fos_version == 'Unknown':
            continue
        fos_d = brcdapi_util.fos_to_dict(fos_version)
        try:
            compare_fos_d = brcdapi_util.fos_to_dict(gen_util.paren_content('(' + rule.split('(')[1], p_remove=True)[0])
        except IndexError:
            brcdapi_log.log('Rule ' + str(rule) + ' is not valid.', echo=True)
            return
        if compare_fos_d['major'] == 0:
            brcdapi_log.log('Rule ' + str(rule) + ' is not valid.', echo=True)
            return
        for key in ('major', 'feature', 'minor', 'bug'):
            if fos_d[key] > compare_fos_d[key]:
                break
            if compare_fos_d[key] > fos_d[key]:
                chassis_obj.s_add_alert(_alert_tbl_d,
                                        al.ALERT_NUM.CHASSIS_FIRMWARE,
                                        p0=compare_fos_d['version'],
                                        p1=fos_d['version'])
                break


def _check_sfps(rule, port_obj_l, t_obj):
    """Checks SFP levels and adds appropriate alerts to port objects. See _isl_num_links() for parameters"""
    global _rule_template, _sfp_rules, _alert_tbl_d, _sfp_file

    if _sfp_rules is None:
        return

    # Perform all the checks for the SFPs on the switch. SFP data is not valid for disabled ports
    enabled_ports = brcddb_search.match_test(port_obj_l, brcddb_search.enabled_ports)
    for rule in _sfp_rules:
        group = 'Unknown' if rule.get('Group') is None else rule.get('Group')
        try:
            pn_l = rule.get('Mfg. P/N')
            if pn_l is not None and pn_l != '':
                for pn in [p.strip() for p in pn_l.split(',')]:
                    plist = brcddb_search.match_test(enabled_ports, dict(k=brcdapi_util.sfp_pn, t='exact', v=pn))
                    if len(plist) > 0:
                        online_plist = brcddb_search.match_test(plist, brcddb_search.port_online)
                        for k0, obj_0 in _rule_template.items():
                            for k1, obj_1 in obj_0.items():
                                val = float(rule.get(k1))  # The threshold to test against
                                m = obj_1.get('a')  # Alert number
                                tlist = online_plist if obj_1.get('l') else plist
                                for p_obj in brcddb_search.match_test(tlist, dict(k=k0, t=obj_1.get('t'), v=val)):
                                    p_obj.s_add_alert(_alert_tbl_d, m, k0, p_obj.r_get(k0), val)
            else:
                brcdapi_log.log('Missing P/N in ' + _sfp_file + ', Group: ' + str(group), echo=True)

        except BaseException as e:
            e_buf = str(type(e)) + ': ' + str(e)
            ml = ['Invalid SFP rules file ' + _sfp_file, 'Group: ' + str(group), e_buf]
            brcdapi_log.exception(ml, echo=True)
            return


def _check_remote_sfps(rule, port_obj_l, t_obj):
    """Checks remote SFP levels and adds appropriate alerts to port objects. See _isl_num_links() for parameters"""
    global _remote_rule_template, _alert_tbl_d

    for port_obj in brcddb_search.match_test(port_obj_l, brcddb_search.port_online):
        v = port_obj.r_get(brcdapi_util.sfp_volt_high_alarm)
        if v is None or v == 0:
            continue  # Sometimes threshold data is all 0 when it's not valid. Just checking the voltage makes it easy

        # Check threshold levels
        for k, rules in _remote_rule_template.items():
            try:
                v = port_obj.r_get(k)
                if v is None:
                    continue
                for k1, rules_1 in rules.items():
                    tv = port_obj.r_get(k1)
                    if rules_1.get('t') == '>=':
                        if v >= tv:
                            port_obj.s_add_alert(_alert_tbl_d, rules_1.get('a'), k1, v, tv)
                            break
                    else:
                        if v <= tv:
                            port_obj.s_add_alert(_alert_tbl_d, rules_1.get('a'), k1, v, tv)
                            break
            except (TypeError, ValueError, IndexError, KeyError):
                pass  # Remote data wasn't provided if we get here.


def _alias_initiator_lower(rule, login_obj_l, t_obj):
    """Makes sure all aliases for initiators are lower case. See _isl_num_links() for parameters"""
    global _alert_tbl_d

    for login_obj in login_obj_l:
        fc4_features = brcddb_login.login_features(login_obj).lower()
        if 'initiator' in fc4_features and 'target' not in fc4_features:
            for alias_obj in login_obj.r_fabric_obj().r_alias_obj_for_wwn(login_obj.r_obj_key()):
                if any(char.isupper() for char in alias_obj.r_obj_key()):
                    alias_obj.s_add_alert(_alert_tbl_d, al.ALERT_NUM.ALIAS_INITIATOR_UPPER)


def _set_zone_check_property(rule, obj_l, t_obj):
    """Sets the specific zone check properties in brcddb_fabric. See _isl_num_links() for parameters"""
    brcddb_fabric.set_bp_check(rule, True)


def _zone_check(rule, fabric_obj_l, t_obj):
    """Performs zone checking. See _isl_num_links() for parameters"""
    for fab_obj in fabric_obj_l:  # Get a zone analysis on all fabrics
        brcdapi_log.log('Performing zone analysis for fabric ' + brcddb_fabric.best_fab_name(fab_obj), echo=True)
        brcddb_fabric.zone_analysis(fab_obj)


def _set_dup_wwn(rule, obj_list, test_list):
    """Sets the duplicate WWN check flag in brcddb_project. See _isl_num_links() for parameters"""
    brcddb_project.set_dup_wwn(True)


def _set_high_temp_error(rule, obj_list, test_list):
    """Sets high temperature error threshold. See _isl_num_links() for parameters"""
    global _high_temp_error

    try:
        _high_temp_error = int(rule.split('(')[1].split(')')[0])
    except IndexError:
        brcdapi_log.log('Rule ' + str(rule) + ' is not valid.', echo=True)


def _set_high_temp_warn(rule, obj_list, test_list):
    """Sets high temperature warn threshold. See _isl_num_links() for parameters"""
    global _high_temp_warn

    try:
        _high_temp_warn = int(rule.split('(')[1].split(')')[0])
    except IndexError:
        brcdapi_log.log('Rule ' + str(rule) + ' is not valid.', echo=True)


def _max_zone_participation(rule, obj_l, t_obj):
    """Sets the maximum zone participation value in brcddb_fabric. See _isl_num_links() for parameters"""
    brcddb_fabric.set_bp_check(rule, True)
    temp_l = rule.split('(')
    try:
        brcddb_fabric.set_bp_check(temp_l[0], int(temp_l[1].split(')')[0]))
    except IndexError:
        brcdapi_log.log('Rule ' + str(rule) + ' is not valid.', echo=True)


def _check_best_practice(rule, obj_l, t_obj):
    """Simple best practice check. See _isl_num_links() for parameters."""
    global _alert_tbl_d

    for obj in brcddb_search.match_test(obj_l, t_obj.get('l'), t_obj.get('logic')):
        px_d = dict(p0=None, p1=None)
        for key in px_d.keys():
            for sub_key in gen_util.convert_to_list(t_obj.get(key)):
                val = obj.r_get(sub_key)
                if val is not None:
                    if px_d[key] is None:
                        px_d[key] = val
                    elif isinstance(val, bool):
                        if val:
                            px_d[key] = val
                    elif isinstance(val, (int, float)):
                        px_d[key] += val
                    elif isinstance(val, str):
                        px_d[key] += ',' + val
                    else:
                        ml = ['Invalid parameter type for ' + key + ':' + sub_key + ' (' + str(type(val)) + ')',
                              'Object key: ' + obj.r_obj_key() + ', Object type: ' + str(type(obj))]
                        brcdapi_log.exception(ml, echo=True)

        obj.s_add_alert(_alert_tbl_d, rule, key=t_obj.get('key'), p0=px_d['p0'], p1=px_d['p1'])


def _fdmi_enabled(rule, obj_l, t_obj):
    """Check to see if FDMI data was presented for initiators. See _isl_num_links() for parameters."""
    # ToDo - Fix this.
    brcdapi_log.log('FDMI checking disabled in this version of report.py. Check was ignored.', echo=True)
    return

    for port_obj in obj_l:
        fabric_obj = port_obj.r_fabric_obj()
        # Mainframes present RNID data instead of FDMI data.
        if port_obj.r_get('rnid') is not None:
            continue  # It's a mainframe
        login_obj_l = port_obj.r_login_objects()
        if len(login_obj_l) == 0:
            continue
        for login_obj in login_obj_l:
            initiator_flag, ns = False, login_obj.r_get(brcdapi_util.bns_node_symbol, 'None')
            fc4_type = login_obj.r_get(brcdapi_util.bns_fc4_features, '')
            for hba_type in _servers_in_ns_l:
                if hba_type in ns:
                    initiator_flag = True
                    if len(fc4_type) > 0:
                        break
            if initiator_flag:
                port_obj.s_add_alert(
                    _alert_tbl_d,
                    al.ALERT_NUM.PORT_FDMI_NOT_ENABLED,
                    p0=brcddb_switch.best_switch_name(port_obj.r_switch_obj()),
                    p1=port_obj.r_obj_key()
                )

    return


def _read_bp_workbook(bp_file, bp_sheet=None):
    """Checks for defined conditions and adds an alert for every out of bounds condition.

    :param bp_file: Name of best practice file
    :type bp_file: str
    :param bp_sheet: Name of sheet in bp_file to read. If None, defaults to "active"
    :type bp_sheet: str, None
    :return: Dictionary of best practices
    :type: None, dict
    :return: List of best practice checks to perform
    :rtype: list
    """
    global _bp_tbl_d

    bp_l = list()
    if bp_file is None:
        return bp_l

    # Read the workbook with best practice rules
    bp_sheet = 'active' if bp_sheet is None else bp_sheet
    error_l, sheet_l = excel_util.read_workbook(bp_file, dm=3, sheets='active' if bp_sheet is None else bp_sheet)
    if len(sheet_l) == 0 and len(error_l) == 0:
        error_l.append('"active" sheet not found in ' + bp_file + '.')
    if len(error_l) > 0:
        brcdapi_log.log(error_l, echo=True)
        return bp_l

    for sheet_d in sheet_l:  # sheet_l can only have one sheet in it

        # Figure out where the columns are and validate that at lease Check and Rule is present
        if len(sheet_d['al']) < 2:
            continue
        col, ml, hdr_d = 0, list(), dict()
        for buf in sheet_d['al'][0]:
            hdr_d.update({buf: col})
            col += 1
        for buf in ('Check', 'Rule'):
            if buf not in hdr_d:
                ml.append(buf + ' missing in ' + bp_file)
        if len(ml) > 0:
            ml.append('Skipping best practices')
            brcdapi_log.log(ml, echo=True)
            return bp_l

        # Load the return list with the rule keys
        ml, row = list(), 2
        for row_l in sheet_d['al'][1:]:
            if len(row_l) >= hdr_d['Check'] and bool(row_l[hdr_d['Check']]):
                rule = al.lookup_d.get(row_l[hdr_d['Rule']])
                if rule is None:
                    rule = row_l[hdr_d['Rule']]
                    if isinstance(rule, str) and rule.split('(')[0] in _bp_tbl_d:
                        bp_l.append(rule)
                    else:
                        ml.append('  Row: ' + gen_util.pad_string(str(row), 3, ' ') + ' Rule: ' +
                                  str(row_l[hdr_d['Rule']]))
                else:
                    bp_l.append(rule)
            row += 1
        if len(ml) > 0:
            ml.insert(0, 'The following rules are unknown in ' + bp_file + ':')
            brcdapi_log.log(ml, echo=True)

    return bp_l


"""_bp_tbl_d defines what objects to test and how each best practice rule is checked

Key     The key is one of:
        * The alert number in brcddb.app_data.alert_tables (always an integer)
        * A special key defined for complex checks (always a string)
        as
Value   Dictionary as described in the table below

+-------+-------------------+---------------------------------------------------------------------------------------+
| Key   | Type              | Description                                                                           |
+=======+===================+=======================================================================================+
| a     | method pointer    | Pointer to the method to call to perform the test                                     |
+-------+-------------------+---------------------------------------------------------------------------------------+
| d     | str               | The type of objects to perform the test against as defined in                         |
|       |                   | brcddb.classes.util.simple_class_type. If the object type is not relevant,            |
|       |                   | the object type won't matter; however, using "ProjectObj" is recommended.             |
+-------+-------------------+---------------------------------------------------------------------------------------+
| t     | dict, None        | Test dictionary passed to brcddb.util.search. Note that complex checks derive their   |
|       |                   | own test definitions.                                                                 |
+-------+-------------------+---------------------------------------------------------------------------------------+
"""
_bp_tbl_d = {

    # Project
    'dup_wwn': dict(a=_set_dup_wwn, d='ProjectObj'),
    'high_temp_error': dict(a=_set_high_temp_error, d='ProjectObj'),
    'high_temp_warn': dict(a=_set_high_temp_warn, d='ProjectObj'),

    # Chassis
    'chassis_fru_check': dict(a=_chassis_fru_check, d='ChassisObj'),
    'fc16_32_haa_sfp_p8': dict(a=_fc16_48_haa_p8, d='ChassisObj'),
    'err_log': dict(a=_chassis_err_log, d='ChassisObj'),
    'min_firmware': dict(a=_min_firmware, d='ChassisObj'),

    # Fabric

    # Zone
    'master_zone_check': dict(a=_zone_check, d='FabricObj'),
    'peer_property': dict(a=_set_zone_check_property, d='ProjectObj'),
    'zone_mismatch': dict(a=_set_zone_check_property, d='ProjectObj'),
    'zone_alias_use': dict(a=_set_zone_check_property, d='ProjectObj'),
    'wwn_alias_zone': dict(a=_set_zone_check_property, d='ProjectObj'),
    'multi_initiator': dict(a=_set_zone_check_property, d='ProjectObj'),
    'max_zone_participation': dict(a=_max_zone_participation, d='ProjectObj'),

    # Switch
    al.ALERT_NUM.SWITCH_FIRMWARE_8_2: dict(a=_check_best_practice, d='SwitchObj', t=dict(
        p0=brcdapi_util.bf_fw_version,
        l=(dict(k=brcdapi_util.bf_fw_version, v='v8.2.1[c-z]', t='regex-s'),
           dict(k=brcdapi_util.bf_fw_version, v='v8.2.[2-9]', t='regex-s'),
           dict(k=brcdapi_util.bf_fw_version, v='v9.[0-9]', t='regex-s')),
        logic='nor')
                                           ),
    al.ALERT_NUM.SWITCH_IDID: dict(a=_check_best_practice, d='SwitchObj', t=dict(
        l=dict(k=brcdapi_util.bfc_idid, v=False, t='bool'))),
    al.ALERT_NUM.HANDLE_DUP_WWN: dict(a=_check_best_practice, d='SwitchObj', t=dict(
        l=dict(k=brcdapi_util.bfc_fport_enforce_login, v=2, t='!='))),
    'isl_num_links': dict(a=_isl_num_links, d='SwitchObj'),
    'isl_bw': dict(a=_isl_bw, d='SwitchObj'),
    'isl_fru': dict(a=_isl_fru, d='SwitchObj'),
    'isl_redundant': dict(a=_isl_redundant, d='SwitchObj'),

    # Ports
    'sfp_health_check': dict(a=_check_sfps, d='PortObj'),
    'remote_sfp_health_check': dict(a=_check_remote_sfps, d='PortObj'),
    al.ALERT_NUM.LOGIN_SPEED_NOT_MAX_W: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0='cs_search/speed',
        p1='cs_search/max_login_speed',
        l=(dict(k='cs_search/speed', t='<', v='cs_search/max_login_speed'),),
        logic='and')
    ),
    al.ALERT_NUM.SWITCH_LIMITED_SPEED: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0='cs_search/remote_sfp_max_speed',
        p1='cs_search/sfp_max_speed',
        l=(dict(k='cs_search/sfp_max_speed', t='<', v='cs_search/remote_sfp_max_speed'),),
        logic='and')
    ),
    al.ALERT_NUM.PORT_F_ZERO_CREDIT: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=brcdapi_util.stats_bb_credit,
        l=(dict(k=brcdapi_util.stats_bb_credit, t='>', v=0),
           brcddb_search.f_ports),
        logic='and')
    ),
    al.ALERT_NUM.PORT_C3_DISCARD: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=brcdapi_util.stats_c3,
        l=dict(k=brcdapi_util.stats_c3, t='>', v=0))
    ),
    al.ALERT_NUM.PORT_TXC3_DISCARD: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=brcdapi_util.stats_c3_out,
        l=dict(k=brcdapi_util.stats_c3_out, t='>', v=0))
    ),
    al.ALERT_NUM.PORT_RXC3_DISCARD: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=brcdapi_util.stats_c3_in,
        l=dict(k=brcdapi_util.stats_c3_in, t='>', v=0))
    ),
    al.ALERT_NUM.PORT_BIT_ERRORS: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=_port_bit_errors,
        l=[dict(k=buf, t='>', v=0) for buf in _port_bit_errors],
        logic='or')
    ),
    al.ALERT_NUM.PORT_FRAME_ERRORS: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=_port_framing_errors,
        l=[dict(k=buf, t='>', v=0) for buf in _port_framing_errors],
        logic='or')
    ),
    al.ALERT_NUM.PORT_LOGICAL_ERRORS: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=_port_logical_errors,
        l=[dict(k=buf, t='>', v=0) for buf in _port_logical_errors],
        logic='or')
    ),
    al.ALERT_NUM.PORT_ENABLED_NO_LIGHT: dict(a=_check_best_practice, d='PortObj', t=dict(l=(is_no_light,))),
    al.ALERT_NUM.PORT_TSB_2019_276: dict(a=_check_best_practice, d='PortObj', t=dict(
        l=(
            dict(k=brcdapi_util.sfp_pn, v='57-0000088*', t='wild'),  # A 16G SWL optic
            dict(k=brcdapi_util.sfp_sn, v='HAF618*', t='wild'),
        ),
        logic='and')
    ),
    al.ALERT_NUM.PORT_FAULT: dict(a=_check_best_practice, d='PortObj', t=dict(
        p0=brcdapi_util.fc_state,
        l=(
            dict(k=brcdapi_util.fc_state, t='exact', v='faulty'),
            dict(k=brcdapi_util.fc_state, t='wild', v='*_flt'),
            dict(k=brcdapi_util.fc_state, t='regex-s', v='mod_(inv|val)'),
            dict(k=brcdapi_util.fc_state, t='exact', v='no_sigdet'),
        ),
        logic='or')
    ),
    al.ALERT_NUM.PORT_SEGMENTED: dict(a=_check_best_practice, d='PortObj', t=dict(
        l=(dict(k=brcdapi_util.sfp_state, t='exact', v='segmented'),),
        logic='and')
    ),
    al.ALERT_NUM.PORT_QSFP_BRKOUT_ASN: dict(a=_check_best_practice, d='PortObj', t=dict(
        l=(brcddb_search.enabled_ports,
           is_asn,
           dict(k=brcdapi_util.sfp_pn, v='57-1000351-01', t='exact')),
        logic='and')
    ),
    al.ALERT_NUM.PORT_SFP_HAA_F16_32_P8: dict(a=_check_best_practice, d='PortObj', t=dict(
        l=(dict(k=brcdapi_util.fru_blade_pn, v='60-1001945-*', t='wild'),  # Pre-2016 FC16-48
           dict(k=brcdapi_util.fc_name, v='?/8', t='wild'),  # Port 8
           dict(k=brcdapi_util.sfp_sn, v='HAA*', t='wild')),
        logic='and')
    ),
    'fdmi_enabled': dict(a=_fdmi_enabled, d='PortObj',),
    'alias_initiator_lower': dict(a=_alias_initiator_lower, d='LoginObj'),
}


def best_practice(bp_file, sfp_file, a_tbl, proj_obj, bp_sheet=None):
    """Checks for defined conditions and adds an alert for every out of bounds condition.

    :param bp_file: Name of best practice file
    :type bp_file: str, None
    :param sfp_file: Name of file with SFP thresholds
    :type sfp_file: str, None
    :param a_tbl: The table that defines this alert. See brcddb.classes.alert.AlertObj
    :type a_tbl: dict
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param bp_sheet: Name of sheet in bp_file to read. If None, defaults to "active"
    :type bp_sheet: str, None
    """
    global _alert_tbl_d, _bp_tbl_d, _sfp_file, _sfp_rules

    _alert_tbl_d = a_tbl  # I could have handled this better, but I'm not fixing working code.
    if sfp_file is not None:
        _sfp_file = sfp_file
        _sfp_rules = report_utils.parse_sfp_file(sfp_file)
    obj_d = dict(
        ProjectObj=[proj_obj],
        ChassisObj=proj_obj.r_chassis_objects(),
        FabricObj=proj_obj.r_fabric_objects(),
        SwitchObj=proj_obj.r_switch_objects(),
        PortObj=proj_obj.r_port_objects(),
        LoginObj=proj_obj.r_login_objects(),
    )

    brcdapi_log.log('Checking best practices', echo=True)
    for rule in _read_bp_workbook(bp_file, bp_sheet):
        rule_d = _bp_tbl_d[rule.split('(')[0]] if isinstance(rule, str) else _bp_tbl_d[rule]
        try:
            rule_d['a'](rule, obj_d[rule_d['d']], rule_d.get('t'))
        except KeyError:
            brcdapi_log.exception('Programming error. Improperly formatted rule, ' + rule + ', in _bp_tbl_d.',
                                  echo=True)

    brcddb_maps.maps_dashboard_alerts(proj_obj)
