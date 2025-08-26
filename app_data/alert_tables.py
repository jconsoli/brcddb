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

Alert definitions for class AlertTable. Defines how alerts are displayed. It could probably be reduced to one simple
dictionary. It started as something more complicated. I left it this way because other code references the class herein.
Adding lookup_d was an afterthought.

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 26 Jun 2024   | Changed SWITCH_FIRMWARE to CHASSIS_FIRMWARE                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Made LOGIN_FDMI_NOT_ENABLED a port level alert, PORT_FDMI_NOT_ENABLED                 |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 25 Aug 2025   | Added ZONE_WWN_IN_ZONE and SWITCH_SCC_MATCH                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025 Consoli Solutions, LLC'
__date__ = '25 Aug 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

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
    SWITCH_FIRMWARE_8_2 = SWITCH_IDID + 1  # Deprecated 6 Dec 2022
    HANDLE_DUP_WWN = SWITCH_FIRMWARE_8_2 + 1
    SWITCH_ISL_IMBALANCE = HANDLE_DUP_WWN + 1
    SWITCH_ISL_BW = SWITCH_ISL_IMBALANCE + 1
    SWITCH_ISL_FRU = SWITCH_ISL_BW + 1
    SWITCH_ISL_REDUNDANT = SWITCH_ISL_FRU + 1
    SWITCH_SCC_MATCH = SWITCH_ISL_REDUNDANT + 1

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
    # case that ever changes, I added warn level alerts, xxx_W, but as of this writing, none of the warn level alerts
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
    PORT_FDMI_NOT_ENABLED = PORT_QSFP_BRKOUT_ASN + 1
    # Below are the remote port thresholds. Note that remote optics still have the old alarm & warn thresholds
    REMOTE_PORT_H_TXP_W = PORT_FDMI_NOT_ENABLED + 1
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
    SWITCH_LIMITED_SPEED = LOGIN_SPEED_NOT_MAX_W + 1
    GROUP_SPEED_NOT_MAX = SWITCH_LIMITED_SPEED + 1
    PORT_SFP_HAA_F16_32_P8 = GROUP_SPEED_NOT_MAX + 1
    PORT_TXC3_DISCARD = PORT_SFP_HAA_F16_32_P8 + 1
    PORT_RXC3_DISCARD = PORT_TXC3_DISCARD + 1
    PORT_LOGICAL_ERRORS = PORT_RXC3_DISCARD + 1
    PORT_BIT_ERRORS = PORT_LOGICAL_ERRORS + 1
    PORT_FRAME_ERRORS = PORT_BIT_ERRORS + 1

    # Login level alerts
    LOGIN_BASE = 500
    LOGIN_DUP_LOGIN = LOGIN_BASE + 1
    LOGIN_NOT_ZONED = LOGIN_DUP_LOGIN + 1
    LOGIN_BASE_ZONED = LOGIN_NOT_ZONED + 1
    LOGIN_MAX_ZONE_PARTICIPATION = LOGIN_BASE_ZONED + 1
    LOGIN_SIM = LOGIN_MAX_ZONE_PARTICIPATION + 1
    LOGIN_AMP = LOGIN_SIM + 1
    LOGIN_MIXED_SPEED_T = LOGIN_AMP + 1
    LOGIN_FASTER_S = LOGIN_MIXED_SPEED_T + 1
    LOGIN_SPEED_DIFF_W = LOGIN_FASTER_S + 1  # Deprecated
    LOGIN_SPEED_DIFF_E = LOGIN_SPEED_DIFF_W + 1  # Deprecated
    LOGIN_SPEED_IMP_W = LOGIN_SPEED_DIFF_E + 1  # Deprecated
    LOGIN_SPEED_IMP_E = LOGIN_SPEED_IMP_W + 1  # Deprecated

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
    ZONE_WWN_IN_ZONE = ZONE_WWN_ALIAS + 1
    ZONE_BASE_ZONED = ZONE_WWN_IN_ZONE + 1
    ZONE_MAX_PARTICIPATION = ZONE_BASE_ZONED + 1
    ZONE_DUP_ALIAS = ZONE_MAX_PARTICIPATION + 1
    ZONE_NULL_ALIAS = ZONE_DUP_ALIAS + 1
    ZONE_NULL_ALIAS_USED = ZONE_NULL_ALIAS + 1
    ZONE_ALIAS_NOT_USED = ZONE_NULL_ALIAS_USED + 1
    ZONE_MULTI_INITIATOR = ZONE_ALIAS_NOT_USED + 1
    ZONE_UNDEFINED_ALIAS = ZONE_MULTI_INITIATOR + 1
    ZONE_PEER_PROPERTY = ZONE_UNDEFINED_ALIAS + 1  # A WWN beginning with 00 is in the zone. Typically, a properties WWN
    ZONE_LINK_ADDR = ZONE_PEER_PROPERTY + 1  # Port associated with link address not in same zone as CHPID
    ZONE_LINK_NO_ADDR = ZONE_LINK_ADDR + 1
    # The remaining zone alerts are support applications that modify zones
    ZONE_ADD_ZONE = ZONE_LINK_NO_ADDR + 1  # Newly created zone
    ZONE_KEPT = ZONE_ADD_ZONE + 1  # Existing zone kept
    ZONE_REMOVED = ZONE_KEPT + 1  # Zone removed/not needed
    ALIAS_INITIATOR_UPPER = ZONE_REMOVED + 1

    # Chassis alerts
    CHASSIS_BASE = 700
    CHASSIS_FRU = CHASSIS_BASE + 1
    CHASSIS_TEMP_ERROR = CHASSIS_FRU + 1
    CHASSIS_TEMP_WARN = CHASSIS_TEMP_ERROR + 1
    CHASSIS_FIRMWARE = CHASSIS_TEMP_WARN + 1

    # IOCP alerts
    IOCP_BASE = 800
    IOCP_MIXED_CU_TYPES = IOCP_BASE + 1

    # General & customer alerts
    GENERAL_BASE = 900
    FREE_TEXT_INFO = GENERAL_BASE + 1
    FREE_TEXT_WARN = FREE_TEXT_INFO + 1
    FREE_TEXT_ERROR = FREE_TEXT_WARN + 1
    ERROR_LOG_INFO = FREE_TEXT_ERROR + 1
    ERROR_LOG_WARN = ERROR_LOG_INFO + 1
    ERROR_LOG_ERROR = ERROR_LOG_WARN + 1


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
        ALERT_NUM.PROJ_PROGRAM_ERROR: \
            dict(m='Programming error encountered. Check the log for details. $p0 $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.PROJ_USER_ERROR: dict(m='Invalid user supplied data. $p0 $p1', s=al.ALERT_SEV.ERROR),

        # Fabric

        # Switch
        ALERT_NUM.SWITCH_IDID: \
            dict(m='Insistent Domain ID not set', s=al.ALERT_SEV.WARN, k='insistent-domain-id-enabled'),
        ALERT_NUM.SWITCH_FIRMWARE_8_2: dict(m='Firmware is $p0. It should be v8.2.1c or higher', s=al.ALERT_SEV.ERROR,
                                            k='firmware-version'),  # Deprecated 6 Dec 2022
        ALERT_NUM.HANDLE_DUP_WWN: \
            dict(m='Login enforcement must be 2. Refer to $key', s=al.ALERT_SEV.ERROR, k='f-port-login-settings/enforce-login'),
        ALERT_NUM.SWITCH_ISL_IMBALANCE: dict(m='ISL imbalance from $p0 to $p1', s=al.ALERT_SEV.ERROR, k='_isl'),
        ALERT_NUM.SWITCH_ISL_BW: \
            dict(m='ISL trunks with different speeds from $p0 to $p1', s=al.ALERT_SEV.ERROR, k='_isl'),
        ALERT_NUM.SWITCH_ISL_FRU: dict(m='ISLs on same slot from $p0 to $p1', s=al.ALERT_SEV.WARN, k='_isl'),
        ALERT_NUM.SWITCH_ISL_REDUNDANT: \
            dict(m='Non-redundant ISL trunks from $p0 to $p1', s=al.ALERT_SEV.ERROR, k='_isl'),
        ALERT_NUM.SWITCH_SCC_MATCH: dict(m='SCC_POLICY mismatch', s=al.ALERT_SEV.ERROR),

        # Port
        ALERT_NUM.PORT_ENABLED_NO_LIGHT: \
            dict(m='Enabled port has no logins', s=al.ALERT_SEV.GENERAL, k='fibrechannel/enabled-state'),
        ALERT_NUM.PORT_C3_DISCARD: \
            dict(m='$p0 C3 discards on this port', s=al.ALERT_SEV.ERROR, k='fibrechannel-statistics/class-3-discards'),
        ALERT_NUM.PORT_TXC3_DISCARD: \
            dict(m='$p0 TxC3 discards on this port', s=al.ALERT_SEV.ERROR, k='fibrechannel-statistics/class-3-discards'),
        ALERT_NUM.PORT_RXC3_DISCARD: \
            dict(m='$p0 RxC3 discards on this port', s=al.ALERT_SEV.ERROR, k='fibrechannel-statistics/class-3-discards'),
        ALERT_NUM.PORT_LOGICAL_ERRORS: \
            dict(m='$p0 Logical errors.', s=al.ALERT_SEV.WARN, k='fibrechannel-statistics/bb-credit-zero'),
        ALERT_NUM.PORT_BIT_ERRORS: \
            dict(m='$p0 Bit errors.', s=al.ALERT_SEV.WARN, k='fibrechannel-statistics/bb-credit-zero'),
        ALERT_NUM.PORT_FRAME_ERRORS: \
            dict(m='$p0 Framing errors.', s=al.ALERT_SEV.WARN, k='fibrechannel-statistics/bb-credit-zero'),
        ALERT_NUM.PORT_F_ZERO_CREDIT: \
            dict(m='F-Port with $p0 zero credits', s=al.ALERT_SEV.WARN, k='fibrechannel-statistics/bb-credit-zero'),
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
        ALERT_NUM.PORT_FDMI_NOT_ENABLED: \
            dict(m='FDMI on attached HBA is not enabled. Switch $p0. Port: $p1', s=al.ALERT_SEV.GENERAL),
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
        ALERT_NUM.LOGIN_SPEED_NOT_MAX_W: \
            dict(m='Port login speed is $p0G but link is capable of $p1G', s=al.ALERT_SEV.WARN),
        ALERT_NUM.SWITCH_LIMITED_SPEED: \
            dict(m='Attached device is capable of $p0G but switch SFP is limited to $p1G', s=al.ALERT_SEV.WARN),
        ALERT_NUM.GROUP_SPEED_NOT_MAX: \
            dict(m='Login speed, $p0, is less than maximum speed of group $p1', s=al.ALERT_SEV.WARN),

        # Login
        ALERT_NUM.LOGIN_DUP_LOGIN: dict(m='Duplicate WWN. Found in ', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.LOGIN_NOT_ZONED: dict(m='Inaccessible. Not in any zone.', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.LOGIN_BASE_ZONED: dict(m='Base NPIV login address in zone', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION: \
            dict(m='$p1 devices zoned to this target. Maximum allowed is $p0.', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SIM: dict(m='SIM port', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.LOGIN_AMP: dict(m='AMP', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.LOGIN_MIXED_SPEED_T: dict(m='Mixed server login speeds zoned to this target.', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_FASTER_S: dict(m='Faster server(s) zoned to this target.', s=al.ALERT_SEV.WARN),
        # Deprecated
        ALERT_NUM.LOGIN_SPEED_DIFF_W: \
            dict(m='$p0 logged in at slower speed also zoned to target(s): $p1.', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_DIFF_E: \
            dict(m='$p0 logged in at slower speed also zoned to target(s): $p1.', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.LOGIN_SPEED_IMP_W: dict(m='Mixed server login speeds zoned to this target.', s=al.ALERT_SEV.WARN),
        ALERT_NUM.LOGIN_SPEED_IMP_E: \
            dict(m='Mixed speeds zoned to this target. Search for $p0 and $p1', s=al.ALERT_SEV.ERROR),

        # Zoning
        # Zones
        ALERT_NUM.ZONE_NO_MEMBERS: dict(m='No members', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_ONE_MEMBER: dict(m='Single member', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_PEER_NO_PMEM: dict(m='Peer zone with no principle members', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_PEER_NO_NMEM: dict(m='Peer zone with no members', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_MIXED: dict(m='Mixed WWN and d,i zone', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_WWN_ALIAS: dict(m='Mixed use of WWN and alias in zone', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_WWN_IN_ZONE: dict(m='WWN used in zone', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NOT_USED: dict(m='Not used', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_MISMATCH: dict(m='Effective zone does not match defined zone', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_PEER_PROPERTY: \
            dict(m='Peer property WWN, $p0, should not be included in the zone definition', s=al.ALERT_SEV.GENERAL),
        # In ZONE_LINK_ADDR below: $p0 - CPC serial (sequence) number, $p1 CHPID tag
        ALERT_NUM.ZONE_LINK_ADDR: dict(m='Not in same zone for CPC $p0 CHPID $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_LINK_NO_ADDR: \
            dict(m='Matching link address $p0 in path CPC $p1 not in fabric', s=al.ALERT_SEV.ERROR),

        # Zone members. In all cases, p0 must be the WWN because that is how the report associates an alert with a
        # member rather than the zone itself. 'f' = True is used to indicate the alert is relevant to the member.
        ALERT_NUM.ZONE_ALIAS_USE: dict(m='Consider using alias $p1', s=al.ALERT_SEV.WARN, f=True),
        ALERT_NUM.ZONE_PROB_AMP: \
            dict(m='SIM Port or AMP trunk link', s=al.ALERT_SEV.GENERAL, f=True),
        ALERT_NUM.ZONE_DIFF_FABRIC: dict(m='Zone member $p0 found in $p1.', s=al.ALERT_SEV.ERROR, f=True),
        ALERT_NUM.ZONE_NOT_FOUND: dict(m='Not found', s=al.ALERT_SEV.GENERAL, f=True),
        ALERT_NUM.ZONE_BASE_ZONED: dict(m='Base NPIV zoned', s=al.ALERT_SEV.ERROR, f=True),
        ALERT_NUM.ZONE_MAX_PARTICIPATION: dict(m='Maximum zone participation exceeded', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_DUP_ALIAS: dict(m='Duplicate alias for $p1. Same as $p0', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NULL_ALIAS: dict(m='Alias has no member', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ZONE_NULL_ALIAS_USED: dict(m='Null alias used in $p0)', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ZONE_ALIAS_NOT_USED: dict(m='Not used', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_MULTI_INITIATOR: dict(m='Multiple initiators: $p0', s=al.ALERT_SEV.WARN),
        # Application specific zone alerts
        ALERT_NUM.ZONE_ADD_ZONE: dict(m='Added $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_KEPT: dict(m='Kept. $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_REMOVED: dict(m='Removed. $p0', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ZONE_UNDEFINED_ALIAS: dict(m='Alias $p0 used in zone $p1 does not exist.', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.ALIAS_INITIATOR_UPPER: \
            dict(m='Alias for initiator contains uppercase characters.', s=al.ALERT_SEV.WARN),

        # Chassis
        ALERT_NUM.PORT_SFP_HAA_F16_32_P8: \
            dict(m='SFP with S/N HAA* in port 8 of pre-2016 FC16-48 should be HAF type', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.CHASSIS_FRU: dict(m='FRU $p0. State: $p1', s=al.ALERT_SEV.ERROR),
        # Warn or Error severity for CHASSIS_TEMP is set in brcddb_bp._chassis_temp_check()
        ALERT_NUM.CHASSIS_TEMP_ERROR: dict(m='Sensor $p0 temperature $p1', s=al.ALERT_SEV.ERROR),
        ALERT_NUM.CHASSIS_TEMP_WARN: dict(m='Sensor $p0 temperature $p1', s=al.ALERT_SEV.WARN),
        ALERT_NUM.CHASSIS_FIRMWARE: dict(m='Required minimum firmware is $p0. Actual is $p1', s=al.ALERT_SEV.ERROR),

        # IOCP
        ALERT_NUM.IOCP_MIXED_CU_TYPES: \
            dict(m='Mixed control unit types on the same CHPID, $p0. Control unit types: $p1', s=al.ALERT_SEV.WARN),

        # General & customer alerts
        # f=True is used in brcddb.report.zone to determine if login or port alerts should be displayed
        ALERT_NUM.FREE_TEXT_INFO: dict(m='$p1', s=al.ALERT_SEV.GENERAL, f=True),
        ALERT_NUM.FREE_TEXT_WARN: dict(m='$p1', s=al.ALERT_SEV.WARN, f=True),
        ALERT_NUM.FREE_TEXT_ERROR: dict(m='$p1', s=al.ALERT_SEV.ERROR, f=True),
        ALERT_NUM.ERROR_LOG_INFO: dict(m='$p0: $p1', s=al.ALERT_SEV.GENERAL),
        ALERT_NUM.ERROR_LOG_WARN: dict(m='$p0: $p1', s=al.ALERT_SEV.WARN),
        ALERT_NUM.ERROR_LOG_ERROR: dict(m='$p0: $p1', s=al.ALERT_SEV.ERROR),
    }
    zone_alert_nums = {  # Application specific zone alerts intentionally left out of this list
        # ZONE
        # LOGIN
        'login_base_zoned': ALERT_NUM.LOGIN_BASE_ZONED,
        'login_max_zone_participation': ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION,
    }
    maps_alerts = (ALERT_NUM.MAPS_DASH_INFO, ALERT_NUM.MAPS_DASH_WARN, ALERT_NUM.MAPS_DASH_ERROR)


lookup_d = dict(
    # MAPS
    MAPS_DASH_ERROR=ALERT_NUM.MAPS_DASH_ERROR,
    MAPS_DASH_WARN=ALERT_NUM.MAPS_DASH_WARN,
    MAPS_DASH_INFO=ALERT_NUM.MAPS_DASH_INFO,

    # Project
    PROJ_DUP_LOGIN=ALERT_NUM.PROJ_DUP_LOGIN,
    PROJ_FAILED_LOGIN=ALERT_NUM.PROJ_FAILED_LOGIN,
    PROJ_CHASSIS_API_ERROR=ALERT_NUM.PROJ_CHASSIS_API_ERROR,
    PROJ_SWITCH_API_ERROR=ALERT_NUM.PROJ_SWITCH_API_ERROR,
    PROJ_PROGRAM_ERROR=ALERT_NUM.PROJ_PROGRAM_ERROR,
    PROJ_USER_ERROR=ALERT_NUM.PROJ_USER_ERROR,

    # Switch
    SWITCH_IDID=ALERT_NUM.SWITCH_IDID,
    SWITCH_FIRMWARE_8_2=ALERT_NUM.SWITCH_FIRMWARE_8_2,
    HANDLE_DUP_WWN=ALERT_NUM.HANDLE_DUP_WWN,
    SWITCH_ISL_IMBALANCE=ALERT_NUM.SWITCH_ISL_IMBALANCE,
    SWITCH_ISL_BW=ALERT_NUM.SWITCH_ISL_BW,
    SWITCH_ISL_FRU=ALERT_NUM.SWITCH_ISL_FRU,
    SWITCH_ISL_REDUNDANT=ALERT_NUM.SWITCH_ISL_REDUNDANT,
    SWITCH_SCC_MATCH=ALERT_NUM.SWITCH_SCC_MATCH,

    # Port
    PORT_ENABLED_NO_LIGHT=ALERT_NUM.PORT_ENABLED_NO_LIGHT,
    PORT_C3_DISCARD=ALERT_NUM.PORT_C3_DISCARD,
    PORT_TXC3_DISCARD=ALERT_NUM.PORT_TXC3_DISCARD,
    PORT_RXC3_DISCARD=ALERT_NUM.PORT_RXC3_DISCARD,
    PORT_LOGICAL_ERRORS=ALERT_NUM.PORT_LOGICAL_ERRORS,
    PORT_BIT_ERRORS=ALERT_NUM.PORT_BIT_ERRORS,
    PORT_FRAME_ERRORS=ALERT_NUM.PORT_FRAME_ERRORS,
    PORT_F_ZERO_CREDIT=ALERT_NUM.PORT_F_ZERO_CREDIT,
    PORT_TSB_2019_274_WARN=ALERT_NUM.PORT_TSB_2019_274_WARN,
    PORT_TSB_2019_274_ALERT=ALERT_NUM.PORT_TSB_2019_274_ALERT,
    PORT_TSB_2019_276=ALERT_NUM.PORT_TSB_2019_276,
    PORT_H_TXP_A=ALERT_NUM.PORT_H_TXP_A,
    PORT_H_TXP_W=ALERT_NUM.PORT_H_TXP_W,
    PORT_L_TXP_A=ALERT_NUM.PORT_L_TXP_A,
    PORT_L_TXP_W=ALERT_NUM.PORT_L_TXP_W,
    PORT_H_RXP_A=ALERT_NUM.PORT_H_RXP_A,
    PORT_H_RXP_W=ALERT_NUM.PORT_H_RXP_W,
    PORT_L_RXP_A=ALERT_NUM.PORT_L_RXP_A,
    PORT_L_RXP_W=ALERT_NUM.PORT_L_RXP_W,
    PORT_H_CUR_A=ALERT_NUM.PORT_H_CUR_A,
    PORT_H_CUR_W=ALERT_NUM.PORT_H_CUR_W,
    PORT_L_CUR_A=ALERT_NUM.PORT_L_CUR_A,
    PORT_L_CUR_W=ALERT_NUM.PORT_L_CUR_W,
    PORT_H_VLT_A=ALERT_NUM.PORT_H_VLT_A,
    PORT_H_VLT_W=ALERT_NUM.PORT_H_VLT_W,
    PORT_L_VLT_A=ALERT_NUM.PORT_L_VLT_A,
    PORT_L_VLT_W=ALERT_NUM.PORT_L_VLT_W,
    PORT_H_TEMP_A=ALERT_NUM.PORT_H_TEMP_A,
    PORT_H_TEMP_W=ALERT_NUM.PORT_H_TEMP_W,
    PORT_L_TEMP_A=ALERT_NUM.PORT_L_TEMP_A,
    PORT_L_TEMP_W=ALERT_NUM.PORT_L_TEMP_W,
    PORT_FAULT=ALERT_NUM.PORT_FAULT,
    PORT_SEGMENTED=ALERT_NUM.PORT_SEGMENTED,
    PORT_QSFP_BRKOUT_ASN=ALERT_NUM.PORT_QSFP_BRKOUT_ASN,
    PORT_FDMI_NOT_ENABLED=ALERT_NUM.PORT_FDMI_NOT_ENABLED,
    REMOTE_PORT_H_TXP_A=ALERT_NUM.REMOTE_PORT_H_TXP_A,
    REMOTE_PORT_H_TXP_W=ALERT_NUM.REMOTE_PORT_H_TXP_W,
    REMOTE_PORT_L_TXP_A=ALERT_NUM.REMOTE_PORT_L_TXP_A,
    REMOTE_PORT_L_TXP_W=ALERT_NUM.REMOTE_PORT_L_TXP_W,
    REMOTE_PORT_H_RXP_A=ALERT_NUM.REMOTE_PORT_H_RXP_A,
    REMOTE_PORT_H_RXP_W=ALERT_NUM.REMOTE_PORT_H_RXP_W,
    REMOTE_PORT_L_RXP_A=ALERT_NUM.REMOTE_PORT_L_RXP_A,
    REMOTE_PORT_L_RXP_W=ALERT_NUM.REMOTE_PORT_L_RXP_W,
    REMOTE_PORT_H_CUR_A=ALERT_NUM.REMOTE_PORT_H_CUR_A,
    REMOTE_PORT_H_CUR_W=ALERT_NUM.REMOTE_PORT_H_CUR_W,
    REMOTE_PORT_L_CUR_A=ALERT_NUM.REMOTE_PORT_L_CUR_A,
    REMOTE_PORT_L_CUR_W=ALERT_NUM.REMOTE_PORT_L_CUR_W,
    REMOTE_PORT_H_VLT_A=ALERT_NUM.REMOTE_PORT_H_VLT_A,
    REMOTE_PORT_H_VLT_W=ALERT_NUM.REMOTE_PORT_H_VLT_W,
    REMOTE_PORT_L_VLT_A=ALERT_NUM.REMOTE_PORT_L_VLT_A,
    REMOTE_PORT_L_VLT_W=ALERT_NUM.REMOTE_PORT_L_VLT_W,
    REMOTE_PORT_H_TEMP_A=ALERT_NUM.REMOTE_PORT_H_TEMP_A,
    REMOTE_PORT_H_TEMP_W=ALERT_NUM.REMOTE_PORT_H_TEMP_W,
    REMOTE_PORT_L_TEMP_A=ALERT_NUM.REMOTE_PORT_L_TEMP_A,
    REMOTE_PORT_L_TEMP_W=ALERT_NUM.REMOTE_PORT_L_TEMP_W,
    LOGIN_SPEED_NOT_MAX_W=ALERT_NUM.LOGIN_SPEED_NOT_MAX_W,
    SWITCH_LIMITED_SPEED=ALERT_NUM.SWITCH_LIMITED_SPEED,
    GROUP_SPEED_NOT_MAX=ALERT_NUM.GROUP_SPEED_NOT_MAX,

    # Login
    LOGIN_DUP_LOGIN=ALERT_NUM.LOGIN_DUP_LOGIN,
    LOGIN_NOT_ZONED=ALERT_NUM.LOGIN_NOT_ZONED,
    LOGIN_BASE_ZONED=ALERT_NUM.LOGIN_BASE_ZONED,
    LOGIN_MAX_ZONE_PARTICIPATION=ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION,
    LOGIN_SIM=ALERT_NUM.LOGIN_SIM,
    LOGIN_AMP=ALERT_NUM.LOGIN_AMP,
    LOGIN_MIXED_SPEED_T=ALERT_NUM.LOGIN_MIXED_SPEED_T,
    LOGIN_FASTER_S=ALERT_NUM.LOGIN_FASTER_S,

    # Deprecated
    LOGIN_SPEED_DIFF_W=ALERT_NUM.LOGIN_SPEED_DIFF_W,
    LOGIN_SPEED_DIFF_E=ALERT_NUM.LOGIN_SPEED_DIFF_E,
    LOGIN_SPEED_IMP_W=ALERT_NUM.LOGIN_SPEED_IMP_W,
    LOGIN_SPEED_IMP_E=ALERT_NUM.LOGIN_SPEED_IMP_E,

    # Zoning
    # Zones
    ZONE_NO_MEMBERS=ALERT_NUM.ZONE_NO_MEMBERS,
    ZONE_ONE_MEMBER=ALERT_NUM.ZONE_ONE_MEMBER,
    ZONE_PEER_NO_PMEM=ALERT_NUM.ZONE_PEER_NO_PMEM,
    ZONE_PEER_NO_NMEM=ALERT_NUM.ZONE_PEER_NO_NMEM,
    ZONE_MIXED=ALERT_NUM.ZONE_MIXED,
    ZONE_WWN_ALIAS=ALERT_NUM.ZONE_WWN_ALIAS,
    ZONE_NOT_USED=ALERT_NUM.ZONE_NOT_USED,
    ZONE_MISMATCH=ALERT_NUM.ZONE_MISMATCH,
    ZONE_PEER_PROPERTY=ALERT_NUM.ZONE_PEER_PROPERTY,
    ZONE_LINK_ADDR=ALERT_NUM.ZONE_LINK_ADDR,
    ZONE_LINK_NO_ADDR=ALERT_NUM.ZONE_LINK_NO_ADDR,
    ZONE_ALIAS_USE=ALERT_NUM.ZONE_ALIAS_USE,
    ZONE_PROB_AMP=ALERT_NUM.ZONE_PROB_AMP,
    ZONE_DIFF_FABRIC=ALERT_NUM.ZONE_DIFF_FABRIC,
    ZONE_NOT_FOUND=ALERT_NUM.ZONE_NOT_FOUND,
    ZONE_BASE_ZONED=ALERT_NUM.ZONE_BASE_ZONED,
    ZONE_MAX_PARTICIPATION=ALERT_NUM.ZONE_MAX_PARTICIPATION,
    ZONE_DUP_ALIAS=ALERT_NUM.ZONE_DUP_ALIAS,
    ZONE_NULL_ALIAS=ALERT_NUM.ZONE_NULL_ALIAS,
    ZONE_NULL_ALIAS_USED=ALERT_NUM.ZONE_NULL_ALIAS_USED,
    ZONE_ALIAS_NOT_USED=ALERT_NUM.ZONE_ALIAS_NOT_USED,
    ZONE_MULTI_INITIATOR=ALERT_NUM.ZONE_MULTI_INITIATOR,
    ZONE_ADD_ZONE=ALERT_NUM.ZONE_ADD_ZONE,
    ZONE_KEPT=ALERT_NUM.ZONE_KEPT,
    ZONE_REMOVED=ALERT_NUM.ZONE_REMOVED,
    ZONE_UNDEFINED_ALIAS=ALERT_NUM.ZONE_UNDEFINED_ALIAS,
    ALIAS_INITIATOR_UPPER=ALERT_NUM.ALIAS_INITIATOR_UPPER,

    # Chassis
    PORT_SFP_HAA_F16_32_P8=ALERT_NUM.PORT_SFP_HAA_F16_32_P8,
    CHASSIS_FRU=ALERT_NUM.CHASSIS_FRU,
    CHASSIS_TEMP_ERROR=ALERT_NUM.CHASSIS_TEMP_ERROR,
    CHASSIS_TEMP_WARN=ALERT_NUM.CHASSIS_TEMP_WARN,

    # IOCP
    IOCP_MIXED_CU_TYPES=ALERT_NUM.IOCP_MIXED_CU_TYPES,

    # General & customer alerts
    FREE_TEXT_INFO=ALERT_NUM.FREE_TEXT_INFO,
    FREE_TEXT_WARN=ALERT_NUM.FREE_TEXT_WARN,
    FREE_TEXT_ERROR=ALERT_NUM.FREE_TEXT_ERROR,
)
