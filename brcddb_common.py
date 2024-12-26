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

:mod:`brcddb_common` - Class and data only. Except for the program control flags, all data defined herein is access via
the objects they are associated with.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 4.0.2     | 26 Dec 2024   | Added Port type by string                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '26 Dec 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.2'

import brcdapi.util as brcdapi_util

#################################################################################
#                                   Project                                     #
#################################################################################
# obj._flags - read and set with obj.flags(), obj.and_flags(), and obj.or_flags
# Individual flags read with (returns True of False)
#   obj.is_build_xref_called()
# If the order of any of the warnings or errors below change or a new warn/error flag is added, _exit_code() for class
#  ProjectObj in brcddb_classes.py must be modified
project_warn = 0b1                            # Encountered a recoverable programming error
project_api_warn = project_warn << 1          # Encountered a recoverable error in the API response
project_user_warn = project_api_warn << 1     # Encountered a recoverable error in a user application
project_error = project_user_warn << 1        # Encountered a non-recoverable programming error
project_api_error = project_error << 1        # Encountered a non-recoverable error in the API response
project_user_error = project_api_error << 1   # Encountered a non-recoverable error in a user application
# If you add any warn or error flags, add it to project_error_warn_mask. The copy utility
project_error_warn_mask = project_warn | project_api_warn | project_user_warn | project_error | project_api_error \
    | project_user_error
# WARNING: If you add a new flag, make sure you update _project_next_avail
project_next_avail = project_user_error << 1

# Exit codes - see _user_friendly_exit_codes
EXIT_STATUS_OK = 0
EXIT_STATUS_WARN = 1
EXIT_STATUS_API_WARN = 2
EXIT_STATUS_USER_WARN = 3
EXIT_STATUS_ERROR = 4  # Programming errors in the brcddb library encountered
EXIT_STATUS_API_ERROR = 5  # Error in the API encountered
EXIT_STATUS_USER_ERROR = 6  # Encountered a non-recoverable error in the application
EXIT_STATUS_INPUT_ERROR = 7  # Invalid user input to an application

exit_code_for_flag = {
    0: EXIT_STATUS_OK,
    project_warn: EXIT_STATUS_WARN,
    project_api_warn: EXIT_STATUS_API_WARN,
    project_user_warn: EXIT_STATUS_USER_WARN,
    project_error: EXIT_STATUS_ERROR,
    project_api_error: EXIT_STATUS_API_ERROR,
    project_user_error: EXIT_STATUS_USER_ERROR,
}

user_friendly_exit_codes = {
    EXIT_STATUS_OK: 'OK',
    EXIT_STATUS_WARN: 'Recoverable error in brcddb encountered. Results may be incomplete.',
    EXIT_STATUS_API_WARN: 'Recoverable error in the API encountered. Results may be incomplete.',
    EXIT_STATUS_USER_WARN: 'Recoverable error in a user application encountered. Results may be incomplete.',
    EXIT_STATUS_ERROR: 'Non-recoverable error in the brcddb library encountered. Processing aborted.',
    EXIT_STATUS_API_ERROR: 'Non-recoverable error in the API encountered. Processing aborted.',
    EXIT_STATUS_USER_ERROR: 'Non-recoverable error in the application encountered. Processing aborted.',
    EXIT_STATUS_INPUT_ERROR: 'User input error to application.'
}

#################################################################################
#                                     Fabric                                    #
#################################################################################

#################################################################################
#                              Zone Configuration                               #
#################################################################################
DEF_ZONE_NOACCESS = 0
DEF_ZONE_ALLACCESS = 1
CFG_ACTION_READ_NOT_AP = 0  # Read not applicable but what is the action with write?
CFG_ACTION_SAVE = 1  # Save pending changes
CFG_ACTION_DISABLE = 2  # Disable the effective zone configuration
CFG_ACTION_CLEAR = 3  # Clear the entire zone DB
CFG_ACTION_CLEAR_PEND = 4  # Clear any pending changes
zonecfg_conversion_tbl = {
    'default-zone-access': {
        DEF_ZONE_NOACCESS: 'Disabled',
        DEF_ZONE_ALLACCESS: 'Enabled',
    },
    'cfg-action': {
        CFG_ACTION_READ_NOT_AP: 'None',
        CFG_ACTION_SAVE: 'Save pending changes',
        CFG_ACTION_DISABLE: 'Disable effective configuration',
        CFG_ACTION_CLEAR: 'Clear the entire zone database',
        CFG_ACTION_CLEAR_PEND: 'Clear pending changes',
    },
    'zone-type': {  # zone-type-type
        0: 'zone',
        1: 'user-created-peer-zone',
        2: 'target-created-peer-zone'
    },

}

#################################################################################
#                                      Zone                                     #
#################################################################################
# obj._flags - read and set with obj.flags(), obj.and_flags(), and obj.or_flags
# There are no zone flags returned from the Rest API. These only get set if brcddb_fabric.zone_analysis() is called
zone_flag_effective = 0b1  # This is the effective zone object

ZONE_STANDARD_ZONE = 0
ZONE_USER_PEER = 1
ZONE_TARGET_PEER = 2
zone_conversion_tbl = {
    'zone-type': {
        ZONE_STANDARD_ZONE: 'Standard',
        ZONE_USER_PEER: 'User defined peer',
        ZONE_TARGET_PEER: 'Target driven peer',
    },
}


#################################################################################
#                              Name Server                                      #
#################################################################################
login_conversion_tbl = {
    # Flags
    brcdapi_util.bns_share_area: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_redirection: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_partial: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_lsan: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_cascade_ag: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_connect_ag: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_dev_behind_ag: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_fcoe_dev: {
        'no': False,
        'yes': True,
    },
    brcdapi_util.bns_sddq: {
        'no': False,
        'yes': True,
    },
}

#################################################################################
#                                        HBA                                    #
#################################################################################

#################################################################################
#                                      Chassis                                  #
#################################################################################
chassis_flag_polled = 0b1  # brocade-chassis/chassis
chassis_flag_ls_polled = chassis_flag_polled << 1  # logical-switch/fibrechannel-logical-switch
# WARNING: If you add a new flag, make sure you update chassis_flag_next_avail
chassis_flag_next_avail = chassis_flag_ls_polled << 1

#################################################################################
#                                      Switch                                   #
#################################################################################
# obj._flags - read and set with obj.flags(), obj.and_flags(), and obj.or_flags
switch_flag_polled = 0b1  # Fibre channel switch was polled.
# WARNING: If you add a new flag, make sure you update switch_flag_next_avail
switch_flag_next_avail = switch_flag_polled << 1

switch_conversion_tbl = {
    brcdapi_util.bfc_fport_enforce_login: {
        0: '0 - First login takes precedence',
        1: '1 - Second login takes precedence',
        2: '2 - First FLOGI takes precedence, second FDISC (NPIV) takes precedence',
    },
    brcdapi_util.bfs_ag_mode: {
        0: 'Not supported',
        1: 'Supported, not enabled',
        3: 'Enabled',
    },
    brcdapi_util.bfs_op_status: {
        0: 'Undefined',
        2: 'Enabled',
        3: 'Disabled',
        7: 'In test',
    },
    brcdapi_util.bfs_principal: {
        0: 'No',
        1: 'Yes',
    },
    brcdapi_util.bfls_base_sw_en: {
        0: 'No',
        1: 'Yes',
    },
    brcdapi_util.bfls_def_sw_status: {
        0: 'No',
        1: 'Yes',
    },
    brcdapi_util.bfls_isl_enabled: {
        0: 'No',
        1: 'Yes',
    },
    brcdapi_util.bfls_ficon_mode_en: {
        0: 'No',
        1: 'Yes',
    },
}


#################################################################################
#                                       Port                                    #
#################################################################################
PORT_TYPE_UNKNOWN = 0
PORT_TYPE_UNKONWN = 0  # Just in case a method is using the misspelled port type
PORT_TYPE_E = 7
PORT_TYPE_G = 10
PORT_TYPE_U = 11
PORT_TYPE_F = 15
PORT_TYPE_L = 16
PORT_TYPE_FCOE = 17
PORT_TYPE_EX = 19
PORT_TYPE_D = 20
PORT_TYPE_SIM = 21
PORT_TYPE_AF = 22
PORT_TYPE_AE = 23
PORT_TYPE_VE = 25
PORT_TYPE_ETH_FLEX = 26
PORT_TYPE_FLEX = 29
PORT_TYPE_N = 30
PORT_TYPE_MIRROR = 31
PORT_TYPE_ICL = 32
PORT_TYPE_FC_LAG = 33
PORT_TYPE_LB = 32768

port_conversion_tbl = {
    brcdapi_util.fc_port_type: {
        PORT_TYPE_UNKNOWN: 'Unknown',
        PORT_TYPE_E: 'E-Port',
        PORT_TYPE_G: 'G-Port',
        PORT_TYPE_U: 'U-Port',
        PORT_TYPE_F: 'F-Port',
        PORT_TYPE_L: 'L-Port',
        PORT_TYPE_FCOE: 'FCoE-Port',
        PORT_TYPE_EX: 'EX-Port,',
        PORT_TYPE_D: 'D-Port',
        PORT_TYPE_SIM: 'SIM-Port',
        PORT_TYPE_AF: 'AF-Port',
        PORT_TYPE_AE: 'AE-Port',
        PORT_TYPE_VE: 'VE-Port',
        PORT_TYPE_ETH_FLEX: 'Ethernet Flex Port',
        PORT_TYPE_FLEX: 'Flex Port',
        PORT_TYPE_N: 'N-Port',
        PORT_TYPE_MIRROR: 'Mirror',
        PORT_TYPE_ICL: 'ICL',
        PORT_TYPE_FC_LAG: 'FC-LAG',
        PORT_TYPE_LB: 'LB-Port',
    },
    brcdapi_util.fc_port_type_str: {
        'n-port': 'N-Port',
        'nl-port': 'NL-Port',
        'f/nl-port': 'F/NL-Port',
        'nx-port': 'NX-Port',
        'f-port': 'F-Port',
        'fl-port': 'FL_Port',
        'e-port': 'E-Port',
        'b-port': 'B-Port',
        'a-port': 'A-Port',
    },
    brcdapi_util.fc_op_status: {
        0: 'Undefined',
        2: 'Online',
        3: 'Offline',
        5: 'Faulty',
        6: 'Testing',
    },
    'fibrechannel/long-distance': {
        0: 'Disabled',
        1: 'L0',
        2: 'L1',
        3: 'L2',
        4: 'LE',
        5: 'L0.5',
        6: 'LD',
        7: 'LS',
    },
    'fibrechannel/octet-speed-combo': {
        -1: 'Not Applicable',
        1:  '32, 16, 8, 4, and 2 Gbps',
        2:  '10, 8, 4, and 2 Gbps',
        3:  '16 and 10 Gbps',
    },
    'fibrechannel/rate-limit-enabled': {
        -1:     'N/A',
        0:      'Not Set',
        200:    200,
        400:    400,
        600:    600,
        800:    800,
        1000:   1000,
        1500:   1500,
        2000:   2000,
        2500:   2500,
        3000:   3000,
        3500:   3500,
        4000:   4000,
        5000:   5000,
        7000:   7000,
        8000:   8000,
        9000:   9000,
        10000:  10000,
        11000:  11000,
        12000:  12000,
        13000:  13000,
        14000:  14000,
        15000:  15000,
        16000:  16000,
    },
    brcdapi_util.fc_los_tov: {
        0:  'Disabled',
        1:  'Enabled Fixed',
        2:  'Enabled Auto',
    },
    # Old flag types
    brcdapi_util.fc_auto_neg: {
        0: False,
        1: True,
    },
    brcdapi_util.fc_comp_act: {
        0: False,
        1: True,
    },
    brcdapi_util.fc_comp_en: {
        0: False,
        1: True,
    },
    brcdapi_util.fc_credit_recov_act: {
        0: False,
        1: True,
    },
    brcdapi_util.fc_credit_recov_en: {
        0: False,
        1: True,
    },
    'fibrechannel/csctl-mode-enabled': {
        0: False,
        1: True,
    },
    brcdapi_util.fc_d_port_en: {
        0: False,
        1: True,
    },
    brcdapi_util.fc_e_port_dis: {
        0: False,
        1: True,
    },
    'fibrechannel/encryption-active': {
        0: False,
        1: True,
    },
    'fibrechannel/ex-port-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/fault-delay-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/via-tts-fec-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/fec-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/fec-active': {
        0: False,
        1: True,
    },
    'fibrechannel/g-port-locked': {
        0: False,
        1: True,
    },
    brcdapi_util.fc_enabled: {  # I don't think this is ever used because fibrechannel/is-enabled-state is a bool
        0: False,
        1: True,
    },
    'fibrechannel/isl-ready-mode-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/mirror-port-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/n-port-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/non-dfe-enabled': {
        0: False,
        1: True,
    },
    brcdapi_util.fc_npiv_en: {
        0: False,
        1: True,
    },
    'fibrechannel/npiv-flogi-logout-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/persistent-disable': {
        0: False,
        1: True,
    },
    'fibrechannel/port-autodisable-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/qos-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/rscn-suppression-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/target-driven-zoning-enable': {
        0: False,
        1: True,
    },
    'fibrechannel/trunk-port-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/vc-link-init': {
        0: False,
        1: True,
    },
    'fibrechannel/sim-port-enabled': {
        0: False,
        1: True,
    },
}

#################################################################################
#                                      Login                                    #
#################################################################################

#################################################################################
#                                       FDMI                                    #
#################################################################################

#################################################################################
#                                     Logging                                   #
#################################################################################
logging_flag_polled = 0b1
# WARNING: If you add a new flag, make sure you update login_flag_next_avail
login_flag_next_avail = logging_flag_polled << 1

fdmi_port_conversion_tbl = {
    'port-state': {
        '0x0': 'Undefined',
        '0x1': 'Unknown',
        '0x2': 'Fully Operational',
        '0x3': 'Administratively Offline',
        '0x4': 'Bypassed',
        '0x5': 'In Diagnostics Mode',
        '0x6': 'Link Down',
        '0x7': 'Phy Error',
        '0x8': 'Loopback',
        '0x9': 'Degraded, but Operational Mode',
    }
}

#################################################################################
#                                   MAPS                                        #
#################################################################################
maps_flag_polled = 0b1
maps_flag_is_predefined = maps_flag_polled << 1
maps_flag_is_modifiable = maps_flag_is_predefined << 1
maps_flag_clear_data = maps_flag_is_modifiable << 1
maps_flag_quiet_time_clear = maps_flag_clear_data << 1
maps_flag_un_quarantine_clear = maps_flag_quiet_time_clear << 1
maps_flag_is_active_policy = maps_flag_un_quarantine_clear << 1
maps_flag_is_predefined_policy = maps_flag_is_active_policy << 1
maps_flag_is_read_only = maps_flag_is_predefined_policy << 1
maps_flag_is_rule_on_rule_supported = maps_flag_is_read_only << 1
maps_flag_is_quiet_time_supported = maps_flag_is_rule_on_rule_supported << 1
# WARNING: If you add a new flag, make sure you update maps_flag_next_avail
maps_flag_next_avail = maps_flag_is_quiet_time_supported << 1
maps_flag_friendly = {
    maps_flag_polled: 'Polled',
    maps_flag_is_predefined: 'Predefined',
    maps_flag_is_modifiable: 'Modifiable',
    maps_flag_clear_data: 'Clear Data',
    maps_flag_quiet_time_clear: 'Quiet Time Clear',
    maps_flag_un_quarantine_clear: 'Un-quarantine Clear',
    maps_flag_is_active_policy: 'Active Policy',
    maps_flag_is_predefined_policy: 'Predefined Policy',
    maps_flag_is_read_only: 'Read Only',
    maps_flag_is_rule_on_rule_supported: 'Rule On Rule Supported',
    maps_flag_is_quiet_time_supported: 'Quiet Time Supported',
}
# Used by obj.rest_flag to match keys to a flag.
maps_bool_flags = {
    'is-predefined': maps_flag_is_predefined,
    'is-modifiable': maps_flag_is_modifiable,
    'clear-data': maps_flag_clear_data,
    'quiet-time-clear': maps_flag_quiet_time_clear,
    'un-quarantine-clear': maps_flag_un_quarantine_clear,
    'is-active-policy': maps_flag_is_active_policy,
    'is-predefined-policy': maps_flag_is_predefined_policy,
    'is-read-only': maps_flag_is_read_only,
    'is-rule-on-rule-supported': maps_flag_is_rule_on_rule_supported,
    'is-quiet-time-supported': maps_flag_is_quiet_time_supported,
}

#################################################################################
#                           Remote SFP Speed                                    #
#################################################################################
# These are used when to determine the speed of the remote SFP by HBA type when the speed information is not returned
# from the remote SFP
hba_2G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LP10000', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LP9002', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_4G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe11000', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe11002', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe1105', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='A800[3|2]A', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPem1100[0|2]', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_8G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe1200[0|2]', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='SN1200E[0|2]P', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='aj763', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='ah403', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe1205', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='554FLB', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='NC553i', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_16G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe160', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe3100', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='7101684', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='SN1200E', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_32G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe3200[0|2]', i=True),
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe3500[0|2]', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_64G_d = dict(
    l=(
        dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='Emulex', i=True),
        dict(
            l=(
                dict(k=brcdapi_util.bns_node_symbol, t='regex-s', v='LPe3600[0|2]', i=True),
            ),
            logic='or',
        )
    ),
    logic='and',
)
hba_remote_speed = (
    dict(f=hba_64G_d, s=[64, 32, 16]),
    dict(f=hba_32G_d, s=[32, 16, 8]),
    dict(f=hba_16G_d, s=[16, 8, 4]),
    dict(f=hba_8G_d, s=[8, 4, 2]),
    dict(f=hba_4G_d, s=[4, 2, 1]),
    dict(f=hba_2G_d, s=[2, 1]),
)
