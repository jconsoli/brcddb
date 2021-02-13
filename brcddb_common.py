# Copyright 2019, 2020, 2021 Jack Consoli.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`brcddb_common` - Class and data only. Except for the program control flags, all data defined herein is access via
the objects they are associated with.

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
    | 3.0.2     | 02 Sep 2020   | Added 0 auto-negotiate no-sync to fibrechannel/speed to port_conversion_tbl       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 01 Nov 2020   | Removed depricated conversions. Added 9.0 status values to port operational-status|
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2020   | Removed 'fibrechannel/speed' and 'fibrechannel/max-speed' from                    |
    |           |               | port_conversion_tbl in favor of calculating speed so as to accomodate all speeds  |
    |           |               | in code.                                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 13 Feb 2021   | Fixed PORT_TYPE_L                                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '13 Feb 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

#################################################################################
#                                   Project                                     #
#################################################################################
# obj._flags - read and set with obj.flags(), obj.and_flags(), and obj.or_flags
# Individual flags read with (returns True of False)
#   obj.is_build_xref_called()
# If the order of any of the warings or errors below change or a new warn/error flag is added, _exit_code() for class
#  ProjectObj in brcddb_classes.py must be modified
project_warn = 0b1                             # Encountered a recoverable programming error
project_api_warn = project_warn << 1          # Encountered a recoverable error in the API response
project_user_warn = project_api_warn << 1     # Encountered a recoverable error in a user application
project_error = project_user_warn << 1        # Encoountered a non-recoverrable programming error
project_api_error = project_error << 1        # Encoountered a non-recoverrable error in the API response
project_user_error = project_api_error << 1   # Encoountered a non-recoverrable error in a user application
# If you add any warn or error flags, add it to project_error_warn_mask. The copy utility
project_error_warn_mask = project_warn | project_api_warn | project_user_warn | project_error | project_api_error \
    | project_user_error
# WARNING: If you add a new flag, make sure you update _project_next_avail
project_next_avail     = project_user_error << 1

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
zone_flag_effective    = 0b1 # This is the effective zone object
zone_flag_wwn          = zone_flag_effective << 1 # If set, zone contains WWN zones
zone_flag_di           = zone_flag_wwn << 1 # If set, zone contains d,i members

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
    'brocade-name-server/share-area': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/frame-redirection': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/partial': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/lsan': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/cascaded-ag': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/connected-through-ag': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/real-device-behind-ag': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/fcoe-device': {
        'no': False,
        'yes': True,
    },
    'brocade-name-server/slow-drain-device-quarantine': {
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
chassis_flag_next_avail   = chassis_flag_ls_polled << 1

#################################################################################
#                                      Switch                                   #
#################################################################################
# obj._flags - read and set with obj.flags(), obj.and_flags(), and obj.or_flags
switch_flag_polled = 0b1 # Fibre channel switch was polled.
# WARNING: If you add a new flag, make sure you update switch_flag_next_avail
switch_flag_next_avail = switch_flag_polled << 1

switch_conversion_tbl = {
    'brocade-fibrechannel-configuration/f-port-login-settings/enforce-login': {
        0: '0 - First login takes precedence',
        1: '1 - Second login takes precedence',
        2: '2 - First FLOGI takes precedence, second FDISC (NPIV) takes precedence',
    },
    'brocade-fibrechannel-switch/fibrechannel-switch/ag-mode': {
        0: 'Not supported',
        1: 'Supported, not enabled',
        3: 'Enabled',
    },
    'brocade-fibrechannel-switch/fibrechannel-switch/operational-status': {
        0: 'Undefined',
        2: 'Enabled',
        3: 'Disabled',
        7: 'In test',
    },
    'brocade-fibrechannel-switch/fibrechannel-switch/principal': {
        0: 'No',
        1: 'Yes',
    },
    'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/base-switch-enabled': {
        0: 'No',
        1: 'Yes',
    },
    'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/default-switch-status': {
        0: 'No',
        1: 'Yes',
    },
    'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/logical-isl-enabled': {
        0: 'No',
        1: 'Yes',
    },
    'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/ficon-mode-enabled': {
        0: 'No',
        1: 'Yes',
    },
}


#################################################################################
#                                       Port                                    #
#################################################################################
PORT_TYPE_UNKONWN = 0
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
PORT_TYPE_LB = 32768

port_conversion_tbl = {
    'fibrechannel/port-type': {
        PORT_TYPE_UNKONWN: 'Unknown',
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
        PORT_TYPE_LB: 'LB-Port',
    },
    'fibrechannel/operational-status': {
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
    'fibrechannel/los-tov-mode-enabled': {
        0:  'Disabled',
        1:  'Enabled Fixed',
        2:  'Enabled Auto',
    },
    # Old flag types
    'fibrechannel/auto-negotiate': {
        0: False,
        1: True,
    },
    'fibrechannel/compression-active': {
        0: False,
        1: True,
    },
    'fibrechannel/compression-configured': {
        0: False,
        1: True,
    },
    'fibrechannel/credit-recovery-active': {
        0: False,
        1: True,
    },
    'fibrechannel/credit-recovery-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/csctl-mode-enabled': {
        0: False,
        1: True,
    },
    'fibrechannel/d-port-enable': {
        0: False,
        1: True,
    },
    'fibrechannel/e-port-disable': {
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
    'fibrechannel/is-enabled-state': {
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
    'fibrechannel/npiv-enabled': {
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
    'port-state' : {
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
maps_flag_un_quarantine_clear = maps_flag_quiet_time_clear <<1
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
