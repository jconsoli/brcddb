# Copyright 2023 Consoli Solutions, LLC.  All rights reserved.
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
:mod:`brcddb.util.maps` -Utility methods for handling MAPS alarms and groups.

Overview::

    This module associates MAPS groups with each port object. The intent was to also pull MAPS dashboard alerts and add
    them to the associated brcddb object but as of FOS 8.2.2, the time stamp in the dashboard was missing the year.
    Since most people don't want a report filled with ancient data, there is no way to filter it without the year. The
    reason for doing this in the first place is because the RAS log was not exposed in the API as of FOS 8.2.2 either.
    If the RAS log is exposed at the same time or sooner, this module will probably go away because it's rare, if ever,
    for someone to not have a RAS log event action with a MAPS threshold. I'll think that through a little more when the
    time comes.

$ToDo - Much of This is stubbed out because MAPS dashboards were incomplete and did not have a valid timestamp

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023 Consoli Solutions, LLC'
__date__ = '04 August 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.0'

import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al


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


# In FOS 8.x, the user friendly name 'Port Health' was used. This was "fixed" in FOS 9.0. I guessed at the others.
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
    'port-health': _port_category,  # Not documented in the Yang models but I saw this come in
    'marginal-port-health': _port_category,
    'faulty-port-health': _port_category,
    'missing-sfp-health': _port_category,
    'error-port-health': _port_category,
    'expired-certificate-health': _switch_category,
    'airflow-mismatch-health': _chassis_category,
    'marginal-sfp-health': _switch_category,
    'trusted-fos-certificate-health': _switch_category,
    'fabric-state-changes': _fabric_category,  # Not documented in the Yang models but I saw this come in
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
