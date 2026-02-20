"""
Copyright 2023, 2024, 2025 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Utility functions to simplify MAPS

**Public Methods**

+---------------------------+---------------------------------------------------------------------------------------+
| Method or Data            | Description                                                                           |
+===========================+=======================================================================================+
| build_maps_alerts         | WIP. Does nothing. Features in FOS 9.1 and above should be available to complete      |
|                           | this. It hasn't been touched since 2019.                                              |
+---------------------------+---------------------------------------------------------------------------------------+
| maps_dashboard_alerts     | WIP. Performs some rudimentary MAPS dashboard checking. Intended for reports.         |
|                           | Features in FOS 9.1 and above should be available to complete this. It hasn't         |
|                           | been touched since 2019.                                                              |
+---------------------------+---------------------------------------------------------------------------------------+
| update_maps               | Adds and optionally deletes MAPS rules, groups, and policies to match a reference     |
|                           | switch. The intended use is for creating custom MAPS rules, groups, and policies as a |
|                           | template and applying that template to other switches. Examples:                      |
|                           |                                                                                       |
|                           | * brocade-rest-api-applications/maps_config.py defines MAPS parameters from an Excel  |
|                           |   Workbook.                                                                           |
|                           | * brocade-rest-api-applications/restore.py reads MAPS configuration parameters from   |
|                           |    another switch.                                                                    |
|                           |                                                                                       |
|                           | In addition to simplifying MAPS configuration, this module breaks up API requests     |
|                           | into pieces that should take no more than 20 seconds to complete.                     |
+---------------------------+---------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Added update_maps().                                                                  |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 25 Aug 2025   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 20 Feb 2026   | Updated copyright notice.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025, 2026 Jack Consoli'
__date__ = '20 Feb 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

from deepdiff import DeepDiff
import collections
import brcdapi.log as brcdapi_log
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.gen_util as gen_util
import brcdapi.util as brcdapi_util
import brcdapi.fos_auth as fos_auth
import brcddb.brcddb_switch as brcddb_switch
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al

_MAX_CHANGES = 32  # Maximum number of MAPS changes to make in a single request

_compare_to_http = dict(Added='POST', Removed='DELETE', Changed='PATCH')

_rule_keys = ('name', 'is-rule-on-rule', 'monitoring-system', 'time-base', 'logical-operator', 'threshold-value',
              'group-name', 'actions', 'quiet-time', 'event-severity', 'is-predefined')
_group_keys = ('name', 'group-type', 'members', 'is-predefined')
_policy_keys = ('name', 'rule-list', 'is-predefined-policy')
_ro_keys_d = {'is-predefined': True, 'is-predefined-policy': True}
_uri_map_d = {'rule': brcdapi_util.maps_rule, 'group': brcdapi_util.maps_group, 'maps-policy': brcdapi_util.maps_policy}


class Skip(Exception):
    pass


def _nochange(val):
    return val


def _csv_to_list(val):
    return [b.strip() for b in val.split(',')] if isinstance(val, str) else val


def _event_severity(val):
    return None if isinstance(val, str) and len(val) == 0 else val


def _convert_to_str(val):
    return str(val)


def _actions(val):
    return dict(action=_csv_to_list(val)) if isinstance(val, str) else val


def _policy_rule(val):
    if isinstance(val, str):
        return dict(rule=_csv_to_list(val)) if len(val) > 0 else dict(rule=list())
    elif val is None:
        return dict(rule=list())
    return val


def _group_member(val):
    if isinstance(val, str):
        return dict(member=_csv_to_list(val)) if len(val) > 0 else dict(member=[''])
    elif val is None:
        return dict(member=[''])
    return val


_rule_values = dict()
for _key in _rule_keys:
    _rule_values.update({_key: _nochange})
_rule_values['actions'] = _actions
_rule_values['threshold-value'] = _convert_to_str
_rule_values['event-severity'] = _event_severity

_group_values = dict()
for _key in _group_keys:
    _group_values.update({_key: _nochange})
_group_values['members'] = _group_member

_policy_values = dict()
for _key in _policy_keys:
    _policy_values.update({_key: _nochange})
_policy_values['rule-list'] = _policy_rule


def _clean_maps(maps_l, key_d, predefined_key):
    """Builds two dictionaries of items pointed to by maps_d with only the keys in key_l. One for predefined items and
       one for non-predefined items.

    :param maps_l: From MAPS brocade-maps/rule, brocade-maps/maps-policy, or brocade-maps/group
    :type maps_l: list
    :param key_d: Table to convert values. Must be _rule_values, _group_values, or policy_values
    :type key_d: dict
    :param predefined_key: Key for predefined ("is-predefined" or "is-predefined-policy")
    :type predefined_key: str
    :return predefined_d: Dictionary. Key is the item name. Value is a dictionary of key/value pairs in key_l
    :rtype predefined_d: dict
    :return non_predefined_d: Same as predefined_d but for non-predefined items
    :rtype non_predefined_d: dict
    """
    predefined_d, non_predefined_d, remove_keys_d = dict(), dict(), dict()

    # Build the return dictionaries
    for maps_d in gen_util.convert_to_list(maps_l):
        content_d = dict()
        for key, action in key_d.items():
            val = action(maps_d.get(key))
            if val is not None:
                content_d.update({key: val})
        if content_d[predefined_key]:
            predefined_d.update({content_d['name']: content_d})
        else:
            non_predefined_d.update({content_d['name']: content_d})

    return predefined_d, non_predefined_d


def _maps_add(uri, diff_d, s_maps_d, key_l):
    """Builds API content for policies, groups, or rules to be added, replaced, or deleted with POST or DELETE

    :param uri: API URI
    :type uri: str
    :param diff_d: Output of brcddb.util.compare(). 'b' is the source and 'c' is the target
    :type diff_d: dict
    :param s_maps_d: Output of _clean_maps() for the source switch
    :type s_maps_d: dict
    :param key_l: Valid keys
    :type key_l: list
    :return: MAPS items to add or replace with POST
    :rtype: list
    """
    global _sort_maps_control_d

    return_l = list()
    for name, d in diff_d.items():
        change = str(d.get('r'))  # 'r' won't be present if it's a change (for PATCH)
        if change == 'Removed':  # The comparison is from the target perspective so add it from the source
            return_d = collections.OrderedDict()  # Some API requests require an ordered dictionary
            for key in [k for k in key_l if k != _sort_maps_control_d[uri]['pre_defined']]:
                return_d.update({key: s_maps_d[key]})
            return_l.append(return_d)

    return return_l


_l = brcdapi_util.maps_policy.split('/')
_policy_leaf = _l[len(_l)-1]
_l = brcdapi_util.maps_rule.split('/')
_rule_leaf = _l[len(_l)-1]
_l = brcdapi_util.maps_group.split('/')
_group_leaf = _l[len(_l)-1]
"""_sort_maps_control_d is used in _add_maps() to determine what needs to be added (POST), deleted (DELETE), and
modified (PATCH). The key is the URI and the value is a dictionary as follows:

+---------------+-----------+---------------------------------------------------------------------------------------+
| Key           | Type      | Description                                                                           |
+===============+===========+=======================================================================================+
| leaf          | str       | The final leaf portion of the URI ("maps-policy", "group", or "rule").                |
+---------------+-----------+---------------------------------------------------------------------------------------+
| uri           | str       | URI ("brocade-maps/maps-policy", "brocade-maps/group", or "brocade-maps/rule")        |
+---------------+-----------+---------------------------------------------------------------------------------------+
| control_d     | dict      | The control dictionary passed as control_tbl to brcddb_compare.compare() when the     |
|               |           | item is not predefined.                                                               | 
+---------------+-----------+---------------------------------------------------------------------------------------+
| p_control_d   | dict      | Same as control_d but for predefined items.                                           | 
+---------------+-----------+---------------------------------------------------------------------------------------+
| pre_defined   | str       | Key to determine if the item is predefined ("is-predefined" or                        |
|               |           | "is-predefined-policy")                                                               |
+---------------+-----------+---------------------------------------------------------------------------------------+
| v             | dict      | Used to determine what leaves to consider when updating a MAPS item and how to        |
|               |           | interpret the values. Passed to _clean_maps() in _add_maps().                        |
+---------------+-----------+---------------------------------------------------------------------------------------+
| POST          | method    | Method used to build the API POST request content.                                    |
+---------------+-----------+---------------------------------------------------------------------------------------+
| PATCH         | method    | Same as POST but for PATCH content.                                                   |
+---------------+-----------+---------------------------------------------------------------------------------------+
| DELETE        | method    | Same as POST but for DELETE content.                                                  |
+---------------+-----------+---------------------------------------------------------------------------------------+
"""
_sort_maps_control_d = {
    brcdapi_util.maps_policy: dict(
        leaf=_policy_leaf,
        uri=brcdapi_util.maps_policy,
        v=_policy_values,
        control_d={'is-predefined-policy': dict(skip=True)},
        p_control_d={'is-predefined': dict(skip=True), 'members': dict(skip=True)},
        pre_defined='is-predefined-policy',
    ),
    brcdapi_util.maps_group: dict(
        leaf=_group_leaf,
        uri=brcdapi_util.maps_group,
        v=_group_values,
        control_d={'is-predefined': dict(skip=True)},
        p_control_d={'is-predefined': dict(skip=True), 'members': dict(skip=True), 'group-type': dict(skip=True)},
        pre_defined='is-predefined',
    ),
    brcdapi_util.maps_rule: dict(
        leaf=_rule_leaf,
        uri=brcdapi_util.maps_rule,
        v=_rule_values,
        control_d={'is-predefined': dict(skip=True)},
        p_control_d={'is-predefined': dict(skip=True)},
        pre_defined='is-predefined',
    ),
}


def _add_maps(session, fid, s_switch_d, t_switch_d, key_table, value_table, maps_type, echo):
    """Used by _add_groups(), _add_rules(), and _add_policies to send additions to MAPS

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param fid: Fabric ID of target switch
    :type fid: int
    :param s_switch_d: Source switch for rules, groups, or policies. This is the output of _clean_maps()
    :type s_switch_d: dict
    :param t_switch_d: Target switch for rules, groups, or policies. This is the output of _clean_maps()
    :type t_switch_d: dict
    :param maps_type: Type of MAPS area. Options are: rule, group, or maps-policy
    :type maps_type: str
    :param echo: If True, echo status to STD_OUT
    :type echo: bool
    :return: Error message
    :rtype: list
    """
    global _ro_keys_d, _uri_map_d

    changes, content_l, error_l, d = 0, list(), list(), dict()

    # Figure out what rules to send to the switch
    for k, maps_d in s_switch_d.items():
        if len(DeepDiff(maps_d, t_switch_d.get(k))) == 0:
            continue  # The item is already present in the target switch and matches the item in the source switch
        if len(content_l) == 0 or len(content_l[len(content_l) - 1]) >= _MAX_CHANGES:
            content_l.append(list())
        d = collections.OrderedDict()  # Some API requests require an ordered dictionary
        for key in [k for k in key_table if not _ro_keys_d.get(k, False)]:
            val = value_table[key](s_switch_d[k].get(key))
            if val is not None:
                d.update({key: val})
        content_l[len(content_l)-1].append(d)

    # Send the updates to the switch
    for sub_content_l in content_l:
        ml = ['_add_maps fid: ' + str(fid) + ', Type: ' + maps_type]
        ml.extend(['  ' + str(d['name']) for d in sub_content_l])
        brcdapi_log.log(ml, echo=echo)
        obj = brcdapi_rest.send_request(session,
                                        'running/' + _uri_map_d[maps_type],
                                        'POST',
                                        {maps_type: sub_content_l},
                                        fid)
        if fos_auth.is_error(obj):
            brcdapi_log.log(fos_auth.formatted_error_msg(obj), echo=echo)
            error_l.append('Failed to add MAPS ' + maps_type + ', ' + str(d.get('name')) + ', to FID ' + str(fid))
            if maps_type == 'rule':
                # Some versions of FOS don't support certain rules so try one at a time.
                for d in sub_content_l:
                    brcdapi_log.log('Attempting to update ' + str(d.get('name')), echo=echo)
                    obj = brcdapi_rest.send_request(session,
                                                    'running/' + _uri_map_d[maps_type],
                                                    'POST',
                                                    {maps_type: [d]},
                                                    fid)
                    if fos_auth.is_error(obj):
                        brcdapi_log.log([fos_auth.formatted_error_msg(obj), 'Failed'], echo=echo)
                        error_l.append('Failed to add MAPS ' + maps_type + ', ' + str(d.get('name')) + ', to FID ' +
                                       str(fid))
                    else:
                        changes += 1

            elif maps_type == 'maps-policy':  # $ToDo groups have to be done one member at a time.
                brcdapi_log.log('Failed', echo=True)

            elif maps_type == 'maps-policy':  # $ToDo policies have to be done one member at a time.
                brcdapi_log.log('Failed', echo=True)

        else:
            changes += len(sub_content_l)
            brcdapi_log.log('Success', echo=echo)

    return error_l, changes


def _add_groups(session, fid, s_switch_d, t_switch_d, echo):
    """Adds any non-predefined groups in the source switch to the target switch

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param fid: Fabric ID of target switch
    :type fid: int
    :param s_switch_d: Source switch groups. This is the output of _clean_maps()
    :type s_switch_d: dict
    :param t_switch_d: Target switch groups. This is the output of _clean_maps()
    :type t_switch_d: dict
    :param echo: If True, echo status to STD_OUT
    :type echo: bool
    :return: Error message
    :rtype: list
    """
    global _group_keys, _group_values
    return _add_maps(session, fid, s_switch_d, t_switch_d, _group_keys, _group_values, 'group', echo)


def _add_rules(session, fid, s_switch_d, t_switch_d, echo):
    """Adds any non-predefined rules in the source switch to the target switch. See _add_groups for parameters"""
    global _rule_keys, _rule_values
    return _add_maps(session, fid, s_switch_d, t_switch_d, _rule_keys, _rule_values, 'rule', echo)


def _add_policies(session, fid, s_switch_d, t_switch_d, echo):
    """Adds any non-predefined policies in the source switch to the target switch. See _add_groups for parameters"""
    global _policy_keys, _policy_values
    return _add_maps(session, fid, s_switch_d, t_switch_d, _policy_keys, _policy_values, 'maps-policy', echo)


def _delete_maps(session, fid, s_switch_d, t_switch_d, maps_type, echo):
    """Used by _del_groups(), _del_rules(), and _del_policies. See _add_maps() for parameters"""
    global _uri_map_d

    changes, content_l, error_l = 0, list(), list()

    # Figure out what to delete
    for k in t_switch_d.keys():
        if s_switch_d.get(k) is None:
            # Add comes first. We already updated the target switch to match the source in _add_maps(). All we need to
            # do is delete items that are in the target but not in the source
            if len(content_l) == 0 or len(content_l[len(content_l) - 1]) >= _MAX_CHANGES:
                content_l.append(list())
            content_l[len(content_l)-1].append(dict(name=k))

    # Send the updates to the switch
    for sub_content_l in content_l:
        name_l = ['  ' + str(d['name']) for d in sub_content_l]
        ml = ['_delete_maps fid: ' + str(fid) + ' type: ' + maps_type]
        ml.extend(name_l)
        brcdapi_log.log(ml, echo=echo)
        obj = brcdapi_rest.send_request(session,
                                        'running/' + _uri_map_d[maps_type],
                                        'DELETE',
                                        {maps_type: sub_content_l},
                                        fid)
        if fos_auth.is_error(obj):
            brcdapi_log.log(fos_auth.formatted_error_msg(obj), echo=echo)
            error_l.append('Failed to delete the following MAPS ' + maps_type + ' from FID ' + str(fid) + ':')
            error_l.extend(name_l)
        else:
            changes += len(sub_content_l)
            brcdapi_log.log('Success', echo=echo)

    return error_l, changes


def _delete_groups(session, fid, s_switch_d, t_switch_d, echo):
    """Deletes any non-predefined groups in the target that are not in the switch. See _add_groups for parameters"""
    global _group_keys, _group_values
    return _delete_maps(session, fid, s_switch_d, t_switch_d, 'group', echo)


def _delete_rules(session, fid, s_switch_d, t_switch_d, echo):
    """Deletes any non-predefined rules in the target that are not in the switch. See _add_groups for parameters"""
    global _rule_keys, _rule_values
    return _delete_maps(session, fid, s_switch_d, t_switch_d, 'rule', echo)


def _delete_policies(session, fid, s_switch_d, t_switch_d, echo):
    """Deletes any non-predefined policies in the target that are not in the switch. See _add_groups for parameters"""
    global _policy_keys, _policy_values
    return _delete_maps(session, fid, s_switch_d, t_switch_d, 'maps-policy', echo)


def update_maps(session, chassis_obj, s_switch_obj, fid_map_l, add_only=False, echo=False):
    """Adds and optionally deletes MAPS rules, groups, and policies to match a reference switch

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param s_switch_obj: Switch object as read from the workbook
    :type s_switch_obj: brcddb.classes.switch.SwitchObj
    :param fid_map_l: FID map. Index is the target switch FID. Value is the matching FID of the source switch
    :type fid_map_l: list
    :param add_only: If True, only additions are made. No policies, groups, or rules are deleted.
    :type add_only: bool
    :param echo: If True, echo status to STD_OUT
    :type echo: bool
    :return: Error messages
    :rtype: list
    """
    error_l, changes = list(), 0

    s_fid = brcddb_switch.switch_fid(s_switch_obj)
    if s_fid is None:
        error_l.append('switch object for ' + brcddb_switch.best_switch_name(s_switch_obj, wwn=True, did=True) +
                       ' is not valid')
        return error_l

    # Set up a control table to determine what gets done and in what order
    for t_switch_obj in chassis_obj.r_switch_objects():
        t_fid = brcddb_switch.switch_fid(t_switch_obj)

        try:
            if fid_map_l[t_fid] != s_fid:
                continue

            # These dictionaries are used to simplify matching non-predefined policies, groups, and rules in the target
            d, t_rule_d = _clean_maps(t_switch_obj.r_get(brcdapi_util.maps_rule), _rule_values, 'is-predefined')
            d, s_rule_d = _clean_maps(s_switch_obj.r_get(brcdapi_util.maps_rule), _rule_values, 'is-predefined')
            d, t_group_d = _clean_maps(t_switch_obj.r_get(brcdapi_util.maps_group), _group_values, 'is-predefined')
            d, s_group_d = _clean_maps(s_switch_obj.r_get(brcdapi_util.maps_group), _group_values, 'is-predefined')
            d, t_policy_d = _clean_maps(t_switch_obj.r_get(brcdapi_util.maps_policy), _policy_values,
                                        'is-predefined-policy')
            d, s_policy_d = _clean_maps(s_switch_obj.r_get(brcdapi_util.maps_policy), _policy_values,
                                        'is-predefined-policy')

            el, i = _add_groups(session, t_fid, s_group_d, t_group_d, echo)
            error_l.extend(el)
            changes += i
            el, i = _add_rules(session, t_fid, s_rule_d, t_rule_d, echo)
            error_l.extend(el)
            changes += i
            el, i = _add_policies(session, t_fid, s_policy_d, t_policy_d, echo)
            error_l.extend(el)
            changes += i
            if not add_only:
                el, i = _delete_policies(session, t_fid, s_policy_d, t_policy_d, echo)
                error_l.extend(el)
                changes += i
                el, i = _delete_rules(session, t_fid, s_rule_d, t_rule_d, echo)
                error_l.extend(el)
                changes += i
                el, i = _delete_groups(session, t_fid, s_group_d, t_group_d, echo)
                error_l.extend(el)
                changes += i

        except (TypeError, IndexError):
            error_l.append('Switch object for ' + brcddb_switch.best_switch_name(s_switch_obj, wwn=True, did=True) +
                           ' is not valid')

    return error_l, changes


def build_maps_alerts(proj_obj):
    """Looks through the MAPS alerts dashboard and adds an alert to the associated object.

    **WARNING:** As of 21 April 2019, there was not a reliable means of correlating MAPS alerts in the dashboard to a
    specific object. An RFE was submitted
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    return

# Case statements in _maps_category - To be modified once the RFE for dashboard alerts is complete


_event_severity = dict(
    critical=al.ALERT_NUM.MAPS_DASH_ERROR,
    default=al.ALERT_NUM.MAPS_DASH_WARN,
    error=al.ALERT_NUM.MAPS_DASH_ERROR,
    info=al.ALERT_NUM.MAPS_DASH_INFO,
    warning=al.ALERT_NUM.MAPS_DASH_WARN,
)


def _unknown_category(switch_obj, dash_obj):
    brcdapi_log.log('MAPS: Unknown dashboard category:\n' + str(dash_obj), False)


def _port_category(switch_obj, dash_obj):
    p0 = dash_obj.get('name')
    o_list = brcddb_util.get_key_val(dash_obj, 'objects/object')
    buf = o_list[0]
    if '-Port' in buf or 'SFP' in buf:
        port = buf.split(' ')[1].split(':')[0]
        port = '0/' + port if '/' not in port else port
    elif 'Pid' in buf:
        # I've stumbled across so many quirks in the MAPS dashboard, it wouldn't surprise me in a rule for a removed
        # port is still in the dashboard.
        try:
            port = switch_obj.r_port_obj_for_pid(buf.split(' ')[1].split(':')[0]).r_obj_key()
        except (IndexError, KeyError, TypeError):
            return
    else:
        brcdapi_log.exception('Unknown MAPS object: ' + buf, True)
        return
    sev = dash_obj.get('event-severity') if dash_obj.get('event-severity') in _event_severity else 'default'
    al_num = _event_severity[sev]
    port_obj = switch_obj.r_port_obj(port)
    if port_obj is not None and not brcddb_util.has_alert(port_obj, al_num, None, p0, None):
        port_obj.s_add_alert(al.AlertTable.alertTbl, al_num, None, p0, None)


def _switch_category(switch_obj, dash_obj):
    p0 = dash_obj.get('name')
    sev = dash_obj.get('event-severity') if dash_obj.get('event-severity') in _event_severity else 'default'
    al_num = _event_severity[sev]
    if not brcddb_util.has_alert(switch_obj, al_num, None, p0, None):
        switch_obj.s_add_alert(al.AlertTable.alertTbl, al_num, None, p0, None)


def _fabric_category(switch_obj, dash_obj):
    p0 = dash_obj.get('name')
    sev = dash_obj.get('event-severity') if dash_obj.get('event-severity') in _event_severity else 'default'
    al_num = _event_severity[sev]
    fabric_obj = switch_obj.r_chassis_obj()
    if not brcddb_util.has_alert(fabric_obj, al_num, None, p0, None):
        fabric_obj.s_add_alert(al.AlertTable.alertTbl, al_num, None, p0, None)


def _chassis_category(switch_obj, dash_obj):
    p0 = dash_obj.get('name')
    sev = dash_obj.get('event-severity') if dash_obj.get('event-severity') in _event_severity else 'default'
    al_num = _event_severity[sev]
    chassis_obj = switch_obj.r_chassis_obj()
    if not brcddb_util.has_alert(chassis_obj, al_num, None, p0, None):
        chassis_obj.s_add_alert(al.AlertTable.alertTbl, al_num, None, p0, None)


# In FOS 8.x, the user-friendly name 'Port Health' was used. This was "fixed" in FOS 9.0. I guessed at the others.
_maps_category = {
    # FOS 8.x
    'Port Health': _port_category,
    'Backend Port Health': _port_category,
    'Extension GE Port Health': _port_category,
    'Security Violations': _switch_category,
    'Fabric State Changes': _fabric_category,
    'Fru Health': _chassis_category,
    'extension-health': _chassis_category,
    'Switch Resources': _chassis_category,
    'Fabric Performance Impact': _port_category,
    'Traffic Performance': _fabric_category,
    # FOS 9.x - And what the categories always should have been
    'security-violations': _switch_category,
    'switch-health': _switch_category,
    'power-supply-health': _chassis_category,
    'fan-health': _chassis_category,
    'wwn-health': _chassis_category,
    'temperature-sensor-health': _chassis_category,
    'ha-health': _chassis_category,
    'control-processor-health': _chassis_category,
    'core-blade-health': _chassis_category,
    'blade-health': _chassis_category,
    'flash-health': _chassis_category,
    'port-health': _port_category,  # Not documented in the Yang models, but I saw this come in
    'marginal-port-health': _port_category,
    'faulty-port-health': _port_category,
    'missing-sfp-health': _port_category,
    'error-port-health': _port_category,
    'expired-certificate-health': _switch_category,
    'airflow-mismatch-health': _chassis_category,
    'marginal-sfp-health': _switch_category,
    'trusted-fos-certificate-health': _switch_category,
    'fabric-state-changes': _fabric_category,  # Not documented in the Yang models but, I saw this come in
    'fabric-performance-impact': _fabric_category,
    'io-latency': _fabric_category,
    'unknown': _unknown_category,
}


def maps_dashboard_alerts(proj_obj):
    """Looks through the MAPS alerts dashboard and adds an alert to the associated object.

    **WARNING:** As of 21 April 2019, there was not a reliable means of correlating MAPS alerts in the dashboard to a
    specific object. This just parses the dashboard for some obvious ones. An RFE was submitted

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for switch_obj in proj_obj.r_switch_objects():
        for dash_obj in gen_util.convert_to_list(switch_obj.r_get('brocade-maps/dashboard-rule')):
            cat = dash_obj.get('category')
            if cat is None or cat not in _maps_category:
                cat = 'unknown'
            _maps_category[cat](switch_obj, dash_obj)
