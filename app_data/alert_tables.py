#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apahche License, Version 2.0 (the "License");
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

:mod:`alert_tables` - Alert definitions for class AlertTable

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | Fixed overlapping zone and chassis alerts & added ZONE_UNDEFINED_ALIAS            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 22 Aug 2020   | Added ZONE_WWN_ALIAS. Set sev level of ZONE_ALIAS_USE to WARN.                    |
    |           |               | Cleaned up language in LOGIN_NOT_ZONED alert.                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '22 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.2'

import brcddb.classes.alert as al


class ALERT_NUM:
    # MAPS alerts
    MAPS_BASE = 0
    MAPS_DASH_INFO = MAPS_BASE + 1
    MAPS_DASH_WARN = MAPS_DASH_INFO + 1
    MAPS_DASH_ERROR = MAPS_DASH_WARN + 1

    # Project level alerts
    PROJ_BASE = 100
    PROJ_DUP_LOGIN = PROJ_BASE + 1
    PROJ_FAILED_LOGIN = PROJ_DUP_LOGIN + 1
    PROJ_CHASSIS_API_ERROR = PROJ_FAILED_LOGIN + 1
    PROJ_SWITCH_API_ERROR = PROJ_CHASSIS_API_ERROR + 1
    PROJ_PROGRAM_ERROR = PROJ_SWITCH_API_ERROR + 1
    PROJ_USER_ERROR = PROJ_PROGRAM_ERROR + 1

    # Fabric level alerts
    FABRIC_BASE = 200

    # Switch level alerts
    SWITCH_BASE = 300
    SWITCH_IDID = SWITCH_BASE + 1
    SWITCH_FIRMWARE_8_2 = SWITCH_IDID + 1
    HANDLE_DUP_WWN = SWITCH_FIRMWARE_8_2 + 1
    SWITCH_ISL_IMBALANCE = HANDLE_DUP_WWN + 1
    SWITCH_ISL_BW = SWITCH_ISL_IMBALANCE + 1
    SWITCH_ISL_FRU = SWITCH_ISL_BW + 1
    SWITCH_ISL_REDUNDANT = SWITCH_ISL_FRU + 1

    # Port level alerts
    PORT_BASE = 400
    PORT_ENABLED_NO_LIGHT = PORT_BASE + 1
    PORT_C3_DISCARD = PORT_ENABLED_NO_LIGHT + 1
    PORT_F_ZERO_CREDIT = PORT_C3_DISCARD + 1
    PORT_E_ZERO_CREDIT = PORT_F_ZERO_CREDIT + 1
    PORT_TSB_2019_274_WARN = PORT_E_ZERO_CREDIT + 1
    PORT_TSB_2019_274_ALERT = PORT_TSB_2019_274_WARN + 1
    PORT_TSB_2019_276 = PORT_TSB_2019_274_ALERT + 1
    # The individual warn and alert levels were replaced with a single threshold when FOS v7.4 was released. Just in
    # case that ever changes, I added warn level alerts, xxx_W, but as of this writting, none of the warn level alerts
    # are used.
    PORT_H_TXP_A = PORT_TSB_2019_276 + 1
    PORT_H_TXP_W = PORT_H_TXP_A + 1
    PORT_L_TXP_A = PORT_H_TXP_W + 1
    PORT_L_TXP_W = PORT_L_TXP_A + 1
    PORT_H_RXP_A = PORT_L_TXP_W + 1
    PORT_H_RXP_W = PORT_H_RXP_A + 1
    PORT_L_RXP_A = PORT_H_RXP_W + 1
    PORT_L_RXP_W = PORT_L_RXP_A + 1
    PORT_H_CUR_A = PORT_L_RXP_W + 1
    PORT_H_CUR_W = PORT_H_CUR_A + 1
    PORT_L_CUR_A = PORT_H_CUR_W + 1
    PORT_L_CUR_W = PORT_L_CUR_A + 1
    PORT_H_VLT_A = PORT_L_CUR_W + 1
    PORT_H_VLT_W = PORT_H_VLT_A + 1
    PORT_L_VLT_A = PORT_H_VLT_W + 1
    PORT_L_VLT_W = PORT_L_VLT_A + 1
    PORT_H_TEMP_A = PORT_L_VLT_W + 1
    PORT_H_TEMP_W = PORT_H_TEMP_A + 1
    PORT_L_TEMP_A = PORT_H_TEMP_W + 1
    PORT_L_TEMP_W = PORT_L_TEMP_A + 1
    PORT_FAULT = PORT_L_TEMP_W + 1
    PORT_SEGMENTED = PORT_FAULT + 1
    PORT_QSFP_BRKOUT_ASN = PORT_SEGMENTED + 1
    # Below are the remote port thresholds. Note that remote optics still have the old alarm & warn thresholds
    REMOTE_PORT_H_TXP_W = PORT_QSFP_BRKOUT_ASN + 1
    REMOTE_PORT_H_TXP_A = REMOTE_PORT_H_TXP_W + 1
    REMOTE_PORT_L_TXP_W = REMOTE_PORT_H_TXP_A + 1
    REMOTE_PORT_L_TXP_A = REMOTE_PORT_L_TXP_W + 1
    REMOTE_PORT_H_RXP_W = REMOTE_PORT_L_TXP_A + 1
    REMOTE_PORT_H_RXP_A = REMOTE_PORT_H_RXP_W + 1
    REMOTE_PORT_L_RXP_W = REMOTE_PORT_H_RXP_A + 1
    REMOTE_PORT_L_RXP_A = REMOTE_PORT_L_RXP_W + 1
    REMOTE_PORT_H_CUR_W = REMOTE_PORT_L_RXP_A + 1
    REMOTE_PORT_H_CUR_A = REMOTE_PORT_H_CUR_W + 1
    REMOTE_PORT_L_CUR_W = REMOTE_PORT_H_CUR_A + 1
    REMOTE_PORT_L_CUR_A = REMOTE_PORT_L_CUR_W + 1
    REMOTE_PORT_H_VLT_W = REMOTE_PORT_L_CUR_A + 1
    REMOTE_PORT_H_VLT_A = REMOTE_PORT_H_VLT_W + 1
    REMOTE_PORT_L_VLT_W = REMOTE_PORT_H_VLT_A + 1
    REMOTE_PORT_L_VLT_A = REMOTE_PORT_L_VLT_W + 1
    REMOTE_PORT_H_TEMP_W = REMOTE_PORT_L_VLT_A + 1
    REMOTE_PORT_H_TEMP_A = REMOTE_PORT_H_TEMP_W + 1
    REMOTE_PORT_L_TEMP_W = REMOTE_PORT_H_TEMP_A + 1
    REMOTE_PORT_L_TEMP_A = REMOTE_PORT_L_TEMP_W + 1
    LOGIN_SPEED_NOT_MAX_W = REMOTE_PORT_L_TEMP_A + 1
    PORT_SFP_HAA_F16_32_P8 = LOGIN_SPEED_NOT_MAX_W + 1

    _DEBUG_A = 900

    # Login level alerts
    LOGIN_BASE = 500
    LOGIN_DUP_LOGIN = LOGIN_BASE + 1
    LOGIN_NOT_ZONED = LOGIN_DUP_LOGIN + 1
    LOGIN_BASE_ZONED = LOGIN_NOT_ZONED + 1
    LOGIN_MAX_ZONE_PARTICIPATION = LOGIN_BASE_ZONED + 1
    LOGIN_SIM = LOGIN_MAX_ZONE_PARTICIPATION + 1
    LOGIN_AMP = LOGIN_SIM + 1
    LOGIN_FDMI_NOT_ENABLED = LOGIN_AMP + 1
    LOGIN_SPEED_DIFF_W = LOGIN_FDMI_NOT_ENABLED + 1
    LOGIN_SPEED_DIFF_E = LOGIN_SPEED_DIFF_W + 1
    LOGIN_SPEED_IMP_W = LOGIN_SPEED_DIFF_E + 1
    LOGIN_SPEED_IMP_E = LOGIN_SPEED_IMP_W + 1

    # Zoning alerts
    ZONE_BASE = 600
    ZONE_NO_MEMBERS = ZONE_BASE + 1
    ZONE_ONE_MEMBER = ZONE_NO_MEMBERS + 1
    ZONE_PEER_NO_PMEM = ZONE_ONE_MEMBER + 1
    ZONE_PEER_NO_NMEM = ZONE_PEER_NO_PMEM + 1
    ZONE_ALIAS_USE = ZONE_PEER_NO_NMEM + 1
    ZONE_PROB_AMP = ZONE_ALIAS_USE + 1
    ZONE_DIFF_FABRIC = ZONE_PROB_AMP + 1
    ZONE_NOT_FOUND = ZONE_DIFF_FABRIC + 1
    ZONE_NOT_USED = ZONE_NOT_FOUND + 1
    ZONE_MISMATCH = ZONE_NOT_USED + 1
    ZONE_MIXED = ZONE_MISMATCH + 1
    ZONE_WWN_ALIAS = ZONE_MIXED + 1
    ZONE_BASE_ZONED = ZONE_WWN_ALIAS + 1
    ZONE_MAX_PARTICIPATION = ZONE_BASE_ZONED + 1
    ZONE_DUP_ALIAS = ZONE_MAX_PARTICIPATION + 1
    ZONE_NULL_ALIAS = ZONE_DUP_ALIAS + 1
    ZONE_NULL_ALIAS_USED = ZONE_NULL_ALIAS + 1
    ZONE_ALIAS_NOT_USED = ZONE_NULL_ALIAS_USED + 1
    ZONE_MULTI_INITIATOR = ZONE_ALIAS_NOT_USED + 1
    ZONE_UNDEFINED_ALIAS = ZONE_MULTI_INITIATOR + 1
    # The remaining zone alerts are support applications that modify zones
    ZONE_ADD_ZONE = ZONE_UNDEFINED_ALIAS + 1  # Newly created zone
    ZONE_KEPT = ZONE_ADD_ZONE + 1  # Existing zone kept
    ZONE_REMOVED = ZONE_KEPT + 1  # Zone removed/not needed

    # Chassis alerts
    CHASSIS_BASE = 700
    CHASSIS_FRU = CHASSIS_BASE + 1
    CHASSIS_TEMP_ERROR = CHASSIS_FRU + 1
    CHASSIS_TEMP_WARN = CHASSIS_TEMP_ERROR + 1


_power_above_threshold = ' above threshold. Threshold: $p1 uW. Actual: $p0 uW.'
_power_below_threshold = ' below threshold. Threshold: $p1 uW. Actual: $p0 uW.'
_temp_above_threshold = ' above threshold. Threshold: $p1 C. Actual: $p0 C.'
_temp_below_threshold = ' below threshold. Threshold: $p1 C. Actual: $p0 C.'
_volt_above_threshold = ' above threshold. Threshold: $p1 V. Actual: $p0 V.'
_volt_below_threshold = ' below threshold. Threshold: $p1 V. Actual: $p0 V.'
_cur_above_threshold = ' above threshold. Threshold: $p1 mA. Actual: $p0 mA.'
_cur_below_threshold = ' below threshold. Threshold: $p1 mA. Actual: $p0 mA.'


class AlertTable:
    """
    **alertTbl** key/value pair definitions are defined in brcddb.classes.alert.AlertObj()
    **zone_alert_nums** Used by brcddb.brcddb_alert.zone_alert_nums() when evaluating zones
    """
    alertTbl = {
        # MAPS
        ALERT_NUM.MAPS_DASH_ERROR: dict(m='MAPS rule $p0', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.MAPS_DASH_WARN: dict(m='MAPS rule $p0', s=al.ALERT_SEV.WARN),
        ALERT_NUM.MAPS_DASH_INFO: dict(m='MAPS rule $p0', s=al.ALERT_SEV.GENERAL),

        # Project
        ALERT_NUM.PROJ_DUP_LOGIN: dict(m='Duplicate WWN: $p0', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_FAILED_LOGIN: dict(m='Login to xxx.xxx.xxx.$p0 failed. $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_CHASSIS_API_ERROR: dict(m='API error to chassis $p0. $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_SWITCH_API_ERROR: dict(m='API error to switch $p0. $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_PROGRAM_ERROR: dict(m='Programming error encountered. Check the log for details. $p0 $p1',
                                           s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_USER_ERROR: dict(m='Invalid user supplied data. $p0 $p1', s=al.ALERT_SEV.ERROR),

        # Fabric

        # Switch
        ALERT_NUM.SWITCH_IDID: dict(m='Insistent Domain ID not set', s=al.ALERT_SEV.WARN,
                                    k='insistent-domain-id-enabled'),
        ALERT_NUM.SWITCH_FIRMWARE_8_2: dict(m='Firmware must be v8.2.1c or higher', s=al.ALERT_SEV.ERROR,
                                            k='firmware-version'),
        ALERT_NUM.HANDLE_DUP_WWN: dict(m='Login enforcement must be 2. Refer to $key', s=al.ALERT_SEV.ERROR,
                                       k='f-port-login-settings/enforce-login'),
        ALERT_NUM.SWITCH_ISL_IMBALANCE: dict(m='ISL imbalance from $p0 to $p1', s=al.ALERT_SEV.ERROR, k='_isl'),
        ALERT_NUM.SWITCH_ISL_BW: dict(m='ISL trunks with different speeds from $p0 to $p1', s=al.ALERT_SEV.ERROR,
                                      k='_isl'),
        ALERT_NUM.SWITCH_ISL_FRU: dict(m='ISLs on same slot from $p0 to $p1', s=al.ALERT_SEV.WARN, k='_isl'),
        ALERT_NUM.SWITCH_ISL_REDUNDANT: dict(m='Non-redundant ISL trunks from $p0 to $p1', s=al.ALERT_SEV.ERROR,
                                             k='_isl'),

        # Port
        ALERT_NUM.PORT_ENABLED_NO_LIGHT: dict(m='Enabled port has no logins', s=al.ALERT_SEV.WARN,
                                              k='fibrechannel/enabled-state'),
        ALERT_NUM.PORT_C3_DISCARD: dict(m='$p0 C3 discards on this port', s=al.ALERT_SEV.ERROR,
                                        k='fibrechannel-statistics/class-3-discards'),
        ALERT_NUM.PORT_F_ZERO_CREDIT: dict(m='F-Port with $p0 zero credits', s=al.ALERT_SEV.WARN,
                                           k='fibrechannel-statistics/bb-credit-zero'),
        ALERT_NUM.PORT_TSB_2019_274_WARN: dict(m='Potential bad SFP per TSB 2019-274', s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_TSB_2019_274_ALERT: dict(m='Bad SFP per TSB 2019-274. Low Tx Power: $p0', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_TSB_2019_276: dict(m='Potential bad SFP per TSB 2019-276', s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_H_TXP_A: dict(m='Alert: Tx power' + _power_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_H_TXP_W: dict(m='Warn: Tx power' + _power_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_L_TXP_A: dict(m='Alert: Tx power' + _power_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_L_TXP_W: dict(m='Warn: Tx power' + _power_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_H_RXP_A: dict(m='Alert: Rx power' + _power_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_H_RXP_W: dict(m='Warn: Rx power' + _power_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_L_RXP_A: dict(m='Alert: Rx power' + _power_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_L_RXP_W: dict(m='Warn: Rx power' + _power_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_H_CUR_A: dict(m='Alert: SFP Current' + _cur_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_H_CUR_W: dict(m='Warn: SFP Current' + _cur_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_L_CUR_A: dict(m='Alert: SFP Current' + _cur_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_L_CUR_W: dict(m='Warn: SFP Current' + _cur_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_H_VLT_A: dict(m='Alert: SFP Voltage' + _volt_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_H_VLT_W: dict(m='Warn: SFP Voltage' + _volt_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_L_VLT_A: dict(m='Alert: SFP Voltage' + _volt_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_L_VLT_W: dict(m='Warn: SFP Voltage' + _volt_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_H_TEMP_A: dict(m='Alert: SFP Temperature' + _temp_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_H_TEMP_W: dict(m='Warn: SFP Temperature' + _temp_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_L_TEMP_A: dict(m='Alert: SFP Temperature' + _temp_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_L_TEMP_W: dict(m='Warn: SFP Temperature' + _temp_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.PORT_FAULT: dict(m='Port fault: $p0', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_SEGMENTED: dict(m='Segmented port', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PORT_QSFP_BRKOUT_ASN: dict(m='ASN not supported on breakout QSFP', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_TXP_A: dict(m='Remote Tx power' + _power_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_TXP_W: dict(m='Remote Tx power' + _power_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_L_TXP_A: dict(m='Remote Tx power' + _power_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_L_TXP_W: dict(m='Remote Tx power' + _power_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_H_RXP_A: dict(m='Remote Rx power' + _power_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_RXP_W: dict(m='Remote Rx power' + _power_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_L_RXP_A: dict(m='Remote Rx power' + _power_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_L_RXP_W: dict(m='Remote Rx power' + _power_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_H_CUR_A: dict(m='Remote SFP Current' + _cur_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_CUR_W: dict(m='Remote SFP Current' + _cur_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_L_CUR_A: dict(m='Remote SFP Current' + _cur_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_L_CUR_W: dict(m='Remote SFP Current' + _cur_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_H_VLT_A: dict(m='Remote SFP Voltage' + _volt_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_VLT_W: dict(m='Remote SFP Voltage' + _volt_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_L_VLT_A: dict(m='Remote SFP Voltage' + _volt_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_L_VLT_W: dict(m='Remote SFP Voltage' + _volt_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_H_TEMP_A: dict(m='Remote SFP Temperature' + _temp_above_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_H_TEMP_W: dict(m='Remote SFP Temperature' + _temp_above_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.REMOTE_PORT_L_TEMP_A: dict(m='Remote SFP Temperature' + _temp_below_threshold, s=al.ALERT_SEV.ERROR),
        ALERT_NUM.REMOTE_PORT_L_TEMP_W: dict(m='Remote SFP Temperature' + _temp_below_threshold, s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_NOT_MAX_W: dict(m='Port login speed is $p0G but link is capable of $p1G',
                                              s=al.ALERT_SEV.WARN),

        # Login
        ALERT_NUM.LOGIN_DUP_LOGIN: dict(m='Duplicate WWN. Also found in fabric $p0', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.LOGIN_NOT_ZONED: dict(m='Inaccessible. Not in any zone.', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_BASE_ZONED: dict(m='Base NPIV login address in zone', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION: dict(m='Max zone participation allowed is $p0', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SIM: dict(m='SIM port', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.LOGIN_AMP: dict(m='AMP', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.LOGIN_FDMI_NOT_ENABLED: dict(m='FDMI on attached HBA is not enabled', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_DIFF_W: dict(m='$p0 logged in at slower speed also zonned to target(s): $p1.',
                                           s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_DIFF_E: dict(m='$p0 logged in at slower speed also zonned to target(s): $p1.',
                                           s=al.ALERT_SEV.ERROR),
        ALERT_NUM.LOGIN_SPEED_IMP_W: dict(m='Mixed speeds zoned to this target. Search for $p0 and $p1',
                                          s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_IMP_E: dict(m='Mixed speeds zoned to this target. Search for $p0 and $p1',
                                          s=al.ALERT_SEV.ERROR),

        # Zoning
        # Zones
        ALERT_NUM.ZONE_NO_MEMBERS: dict(m='No members', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_ONE_MEMBER: dict(m='Single member', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_PEER_NO_PMEM: dict(m='Peer zone with no principle members', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_PEER_NO_NMEM: dict(m='Peer zone with no members', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_MIXED: dict(m='Mixed WWN and d,i zone', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_WWN_ALIAS: dict(m='Mixed use of WWN and alias in zone', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NOT_USED: dict(m='Not used', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_MISMATCH: dict(m='Effective zone does not match defined zone', s=al.ALERT_SEV.WARN),

        # Zone members. In all cases, _p0 must be the WWN because that is how the report associates an alert with a
        # member rather than the zone itself. 'f' = True is used to indicate the alert is relevant to the member.
        ALERT_NUM.ZONE_ALIAS_USE: dict(m='Consider using alias $p1', s=al.ALERT_SEV.WARN, f=True),
        ALERT_NUM.ZONE_PROB_AMP: dict(m='SIM Port or AMP trunk link', s=al.ALERT_SEV.GENERAL,
                                      f=True),
        ALERT_NUM.ZONE_DIFF_FABRIC: dict(m='Member found in fabric $p1', s=al.ALERT_SEV.ERROR, f=True),
        ALERT_NUM.ZONE_NOT_FOUND: dict(m='Not found', s=al.ALERT_SEV.GENERAL, f=True),
        ALERT_NUM.ZONE_BASE_ZONED: dict(m='Base NPIV zoned', s=al.ALERT_SEV.ERROR, f=True),
        ALERT_NUM.ZONE_MAX_PARTICIPATION: dict(m='Maximum zone participation excceded', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_DUP_ALIAS: dict(m='Duplicate alias. Same as $p0', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NULL_ALIAS: dict(m='Alias has no member', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NULL_ALIAS_USED: dict(m='Null alias used in $p0)', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_ALIAS_NOT_USED: dict(m='Not used', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_MULTI_INITIATOR: dict(m='Multiple initiators: $p0', s=al.ALERT_SEV.WARN),
        # Application specific zone alerts
        ALERT_NUM.ZONE_ADD_ZONE: dict(m='Added $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_KEPT: dict(m='Kept. $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_REMOVED: dict(m='Removed. $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_UNDEFINED_ALIAS: dict(m='Alias $p0 used in zone $p1 does not exist.', s=al.ALERT_SEV.ERROR),

        # Chassis
        ALERT_NUM.PORT_SFP_HAA_F16_32_P8: dict(
            m='SFP with S/N HAA* in port 8 of pre-2016 FC16-48 should be HAF type',
            s=al.ALERT_SEV.ERROR),
        ALERT_NUM.CHASSIS_FRU: dict(m='FRU $p0. State: $p1', s=al.ALERT_SEV.ERROR),
        # Warn or Error severity for CHASSIS_TEMP is set in brcddb_bp._chassis_temp_check()
        ALERT_NUM.CHASSIS_TEMP_ERROR: dict(m='Sensor $p0 temperature $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.CHASSIS_TEMP_WARN: dict(m='Sensor $p0 temperature $p1', s=al.ALERT_SEV.WARN),
    }
    zone_alert_nums = {  # Application specific zone alerts intentionally left out of this list
        # ZONE
        # LOGIN
        'login_base_zoned': ALERT_NUM.LOGIN_BASE_ZONED,
        'login_max_zone_participation': ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION,
    }
    maps_alerts = (ALERT_NUM.MAPS_DASH_INFO, ALERT_NUM.MAPS_DASH_WARN, ALERT_NUM.MAPS_DASH_ERROR)
