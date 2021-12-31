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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
:mod:`brcddb.app_data.bp_tables` - Best practice definitions.

WARNING::

    I have plans to deprecate this table. It grew well beyond the original intended purpose.

     Editing a library to customize a report is not good. In some controlled environments, script writers don't have
     access to the Python lib folder making it impossible to customize reports but until I get around to modifying
     report.py, this file needs to be edited to customize reports.

     This table is read by brcddb.brcddb_bp.best_practice() and brcddb_fabric.py. The intended solution is for report.py
     to read in a table from a user specified file during invocation.

     To net it out, the "Description" section is incorrect. It is what was intended, not what was implemented.

Programmer Note::

    If you add an alert number, don't forget to update brcddb\app_data\alert_tables.py.

Description::

    The tables herein define the default best practices.

Table Definitions::

    These values are passed to brcddb.brcddb_bp.best_practice()

    +-----------+-------------------------------------------------------+
    | Key       | Description                                           |
    +===========+=======================================================+
    | 'm'       | Alert number - See brcddb.app_data.alert_tables       |
    +-----------+-------------------------------------------------------+
    | 'p0'      | Retrieved with obj.getvalue(key) which becomes the    |
    |           | value for brcddb.classes.alert.AlertObj._p0           |
    +-----------+-------------------------------------------------------+
    | 'p1'      | Same as 'p0' but for the _p1 value                    |
    +-----------+-------------------------------------------------------+
    | 'p0h'     | Hard codded value for p0. When this key is present    |
    |           | 'p0' is ignored.                                      |
    +-----------+-------------------------------------------------------+
    | 'p1h'     | Same as 'p0h' but for the _p1h value                  |
    +-----------+-------------------------------------------------------+
    | 'l'       | Tables passed to brcdb.util.search.match_test()       |
    +-----------+-------------------------------------------------------+
    | 'logic'   | Logic passed to brcdb.util.search.match_test()        |
    +-----------+-------------------------------------------------------+
    | 'skip'    | If True, skips the test                               |
    +-----------+-------------------------------------------------------+
    | 's'       | Special test. Use this when a simple key value test   |
    |           | isn't sufficient. The value associated with this key  |
    |           | must be in brcddb_bp.bp_special_case_tbl or           |
    |           | brcddb._bp_special_list_case_tbl. The method          |
    |           | specified in this table is called which gives you the |
    |           | ability to create any best practice test you want.    |
    +-----------+-------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 02 Sep 2020   | Disabled duplicate WWN (FDISC) check                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | PEP8 clean up. No functional changes.                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 17 Jul 2021   | Added custom_tbl and modified comments.                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2021   | Updated comments only. No functional changes.                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '31 Dec 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

import brcddb.brcddb_common as brcddb_common
import brcddb.app_data.alert_tables as al

MAX_ZONE_PARTICIPATION = 30  # Maximum number of devices that can be zoned to a login. See brcddb_fabric.zone_analysis()

# Not used. Examples on how create a best practice check to flag any Emulex LPe3 HBA running firmware driver code 11.x
fdmi_mfg_emulex = dict(k='brocade-fdmi/manufacturer', t='wild', v='Emulex*', i=True)
fdmi_fw = dict(k='brocade-fdmi/firmware-version', t='wild', v='11*')
fdmi_mfg_model = dict(k='brocade-fdmi/model', t='regex-s', v='LPe3[2-5]002-M2')
emulex_fw_test = dict(
    l=(
        fdmi_mfg_emulex,
        fdmi_fw,
        fdmi_mfg_model,
    ),
    logic='and'
)

is_enabled = dict(k='fibrechannel/is-enabled-state', t='bool', v=True)
is_f_port = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_F)
is_e_port = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_E)
is_not_online = dict(k='fibrechannel/operational-status', t='!=', v=2)
is_online = dict(k='fibrechannel/operational-status', t='==', v=2)
is_no_light = dict(k='fibrechannel/physical-state', t='exact', v='no_light')
is_asn = dict(k='fibrechannel/auto-negotiate', t='bool', v=True)

port_tbl = (

    # SFP Health Check
    dict(
        skip=False,
        m=0,  # Alert numbers derived in brcddb_bp._check_sfps()
        s='SFP_HEALTH_CHECK',
    ),
    # Remote SFP Health Check
    dict(
        skip=False,
        m=0,  # Alert numbers derived in brcddb_bp._check_remote_sfps()
        s='REMOTE_SFP_HEALTH_CHECK',
    ),
    # Check for best login speed
    dict(
        skip=False,
        m=al.ALERT_NUM.LOGIN_SPEED_NOT_MAX_W,
        p0='_search/speed',
        p1='_search/max_login_speed',
        l=(dict(k='_search/speed', t='<', v='_search/max_login_speed')), logic='and',
    ),
    # Any F-Port with more than 0 BB credit time 0 counts
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_F_ZERO_CREDIT,
        p0='fibrechannel-statistics/bb-credit-zero',
        l=(
            dict(k='fibrechannel-statistics/bb-credit-zero', t='>', v=0),
            is_f_port,
        ),
        logic='and',
    ),
    # Any port with C3 discards
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_C3_DISCARD,
        p0='fibrechannel-statistics/class-3-discards',
        l=dict(k='fibrechannel-statistics/class-3-discards', t='>', v=0),
    ),
    # Make sure all enabled ports have something attached.
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_ENABLED_NO_LIGHT,
        l=(is_no_light,),  # The status can only be 'no_light' if the port is enabled so no need to check for enabled
    ),
    # Check for bad batch of 16G SWL SFPs, TSB 2019-276
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_TSB_2019_276,
        l=(
            dict(k='media-rdp/part-number', v='57-0000088*', t='wild'),  # A 16G SWL optic
            dict(k='media-rdp/serial-number', v='HAF618*', t='wild'),
        ),
        logic='and'
    ),
    # Port faults
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_FAULT,
        p0='fibrechannel/physical-state',
        l=(
            dict(k='fibrechannel/physical-state', t='exact', v='faulty'),
            dict(k='fibrechannel/physical-state', t='wild', v='*_flt'),
            dict(k='fibrechannel/physical-state', t='regex-s', v='mod_(inv|val)'),
            dict(k='fibrechannel/physical-state', t='exact', v='no_sigdet'),
        ),
        logic='or',
    ),
    # Segmented ports
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_SEGMENTED,
        l=(
            dict(k='media-rdp/physical-state', t='exact', v='segmented'),
        ),
        logic='and',
    ),
    # Check for breakout QSFPs set for auto-speed negotiate. This is not supported as of 8.2.1b
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_QSFP_BRKOUT_ASN,
        l=(
            is_enabled,
            is_asn,
            dict(k='media-rdp/part-number', v='57-1000351-01', t='exact'),
        ),
        logic='and'
    ),
    # Check for SFPs with serial numbers beginning with "HAA" on FC16-48 blade in port 8 manufactured in 2015 or earlier
    dict(
        skip=False,
        m=al.ALERT_NUM.PORT_SFP_HAA_F16_32_P8,
        l=(
            dict(k='brocade-fru/blade/part-number', v='60-1001945-*', t='wild'),  # Pre-2016 FC16-48
            dict(k='fibrechannel/name', v='?/8', t='wild'),  # Port 8
            dict(k='media-rdp/serial-number', v='HAA*', t='wild'),
        ),
        logic='and'
    ),
)

switch_tbl = (
    # Check firmware: 8.2.1c or higher
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_FIRMWARE_8_2,
        p0='brocade-fabric/fabric-switch/firmware-version',
        l=(
            dict(k='brocade-fabric/fabric-switch/firmware-version', v='v8.2.1[c-z]', t='regex-s'),  # >= 8.2.1c
            dict(k='brocade-fabric/fabric-switch/firmware-version', v='v8.2.[2-9]', t='regex-s'),  # >= 8.2.2
            dict(k='brocade-fabric/fabric-switch/firmware-version', v='v9.[0-9]', t='regex-s'),  # 9.0 or higher
        ),
        logic='nor'
    ),
    # Make sure insistent domain ID is set
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_IDID,
        l=dict(k='brocade-fibrechannel-configuration/fabric/insistent-domain-id-enabled', v=False, t='bool')
    ),
    # Duplicate WWN handling should be to accept the second FDISC into the fabric
    dict(
        skip=True,
        m=al.ALERT_NUM.HANDLE_DUP_WWN,
        l=dict(k='brocade-fibrechannel-configuration/f-port-login-settings/enforce-login', v=2, t='!=')
    ),
    # Balanced number of ISLs
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_ISL_IMBALANCE,
        s='ISL_NUM_LINKS',
    ),
    # Check B/W of ISLs
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_ISL_BW,
        s='ISL_BW',
    ),
    # Make sure ISLs are on different FRUs
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_ISL_FRU,
        s='ISL_FRU',
    ),
    # Make sure there are redundant ISL paths
    dict(
        skip=False,
        m=al.ALERT_NUM.SWITCH_ISL_REDUNDANT,
        s='ISL_REDUNDANT',
    ),
)

login_node_tbl = (
    # Make sure FDMI is enabled - Only applicable to HBAs (initiators). Storage has yet to provide HDMI data
    dict(
        skip=False,
        m=al.ALERT_NUM.LOGIN_FDMI_NOT_ENABLED,
        s='FDMI_ENABLED',
        l=(
            dict(k='brocade-name-server/fc4-features', t='exact', v='FCP-Initiator')
        ),
    ),
)

fabric_tbl = ()

chassis_tbl = (
    # Make sure FDMI is enabled - Only applicable to HBAs (initiators). Storage has yet to provide HDMI data
    dict(
        skip=False,
        m=al.ALERT_NUM.CHASSIS_FRU,
        s='CHASSIS_FRU_CHECK',
    ),
    dict(
        skip=True,
        m=al.ALERT_NUM.PORT_SFP_HAA_F16_32_P8,
        s='FC16_32_HAA_SFP_P8',
    ),
)

custom_tbl = dict(
    # Used in brcddb_fabric
    peer_property=False,  # peer property WWNs in a zone. Typically True but False for sh_capture output
    zone_mismatch=False,  # defined zone matches the effective zone. Typically True but False for sh_capture output
    # Used in brcddb_project.py
    dup_wwn=True,  # Duplicate WWNs in project
)
