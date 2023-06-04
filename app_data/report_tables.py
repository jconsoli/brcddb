# Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli.  All rights reserved.
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
:mod:`report_tables` - Control tables for brcddb.report.xxxx_page modules.

Dynamic control of worksheets is only available for chassis, switch, and page sheets at this time. Possible uses for
these tables are:

    * Retrieve the pointers to the tables directly from this library
    * Put a copy of this module in your private collection of libraries
        * This allows you to modify the table entries for your own customized reports

Important Classes::

    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Class         | Sub-class             | Description                                                           |
    +===============+=======================+=======================================================================+
    | Chassis       | chassis_display_tbl   | Determines what fields to display and the column header               |
    |               |                       | Used with brcddb.report.chassis.chassis_page()                        |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Switch       | switch_display_tbl     | Determines what fields to display and the column header               |
    |               |                       | Used with brcddb.report.switch.switch_page()                          |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Port          | port_display_tbl      | Determines how data is to be displayed                                |
    |               |                       | Used with brcddb.report.port.port_page()                              |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Port          | port_config_tbl       | Determines what fields to display. Tailored for port configurations   |
    |               |                       | Used with brcddb.report.chassis.chassis_page()                        |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Port          | port_stats_tbl        | Determines what fields to display. Tailored for port statistics       |
    |               |                       | Used with brcddb.report.chassis.chassis_page()                        |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Port          | port_stats1_tbl       | Determines what fields to display. Tailored for port statistics       |
    |               |                       | from a single port.                                                   |
    +---------------+-----------------------+-----------------------------------------------------------------------+
    | Port          | port_sfp_tbl          | Determines what fields to display. Tailored for SFPs                  |
    |               |                       | Used with brcddb.report.chassis.chassis_page()                        |
    +---------------+-----------------------+-----------------------------------------------------------------------+

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
    | 3.0.2     | 22 Aug 2020   | Fixed typo in Path Count                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 02 Sep 2020   | Added the port address to the default port pages.                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 29 Sep 2020   | Removed duplicate table entries.                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 29 Nov 2020   | Added average-transmit-buffer-usage and average-receive-buffer-usage              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 13 Mar 2021   | Added 'fibrechannel/speed' to port_zone_tbl                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 17 Jul 2021   | Updated comments                                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 31 Dec 2021   | Added more user friendly names.                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 28 Apr 2022   | Added _CONFIG_LINK, _STATS_LINK, _ZONE_LINK, _SFP_LINK, _RNID_LINK                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 22 Jun 2022   | Fixed missing fibrechannel-name-server in brocade-name-server in                  |
    |           |               | Login.login_display_tbl and Login.login_tbl                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 04 Sep 2022   | Fixed brocade-fdmi references. Used _LOGIN_WWN login_tbl                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.3     | 14 Oct 2022   | Added port type to the port configuration table, port_display_tbl.port_sfp_tbl.   |
    |           |               | Adjust some default column widths.                                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.4     | 26 Mar 2023   | Added the port index to port_rnid_tbl                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.5     | 21 May 2023   | Updated documentation                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.6     | 04 Jun 2023   | Added _ALIAS to all port tables.                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '04 Jun 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.6'

import brcdapi.util as brcdapi_util


class Chassis:
    # Key - Custom key of key from any of the chassis related API responses. Value is the the column header. This table
    # also controls what is populated on the sheet page. Comment/Uncomment entries as needed.
    chassis_display_tbl = {
        # From the API
        brcdapi_util.bc_user_name: 'Chassis Name',
        brcdapi_util.bc_wwn: 'Chassis WWN',
        brcdapi_util.bc_license_id: 'License ID',
        brcdapi_util.bc_mfg: 'Manufacturer',
        brcdapi_util.bc_org_name: 'Registered Organization Name',
        brcdapi_util.bc_org_reg_date: 'Organization Registration Date',
        brcdapi_util.bc_pn: 'Part Number',
        brcdapi_util.bc_serial_num: 'Serial Number',
        brcdapi_util.bc_max_blades: 'Maximum Number of Blades Supported',
        brcdapi_util.bc_vendor_pn: 'Vendor Part Number',
        brcdapi_util.bc_vendor_sn: 'Vendor Serial Number',
        brcdapi_util.bc_vendor_rev_num: 'Vendor Revision Number',
        brcdapi_util.bc_product_name: 'Product Name',
        brcdapi_util.bc_date: 'Date',
        brcdapi_util.bc_enabled: 'Chassis Enabled',
        brcdapi_util.bc_motd: 'Daily Message',
        brcdapi_util.bc_shell_to: 'Shell Timeout',
        brcdapi_util.bc_session_to: 'Session Timeout',
        brcdapi_util.bc_usb_enbled: 'USB Enabled',
        brcdapi_util.bc_usb_avail_space: 'USB Available Space',
        brcdapi_util.bc_tcp_to_level: 'TCP Timeout Level',
        brcdapi_util.bc_bp_rev: 'Backplane Revision',
        brcdapi_util.bp_vf_enabled: 'Virtual Fabrics Enabled',
        brcdapi_util.bc_vf: 'Virtual Fabrics Supported',
        brcdapi_util.bc_ha: 'HA Enabled',
        brcdapi_util.bc_heartbeat: 'Heart Beat Up',
        brcdapi_util.bc_sync: 'HA Synchronized',
        brcdapi_util.bc_active_cp: 'Active CP',
        brcdapi_util.bc_active_slot: 'Active Slot',
        brcdapi_util.bc_ha_recovery: 'Recovery Type',
        brcdapi_util.bc_ha_standby_cp: 'Standby CP',
        brcdapi_util.bc_ha_standby_health: 'Standby Health',
        brcdapi_util.bc_ha_standby_slot: 'Standby Slot',
        brcdapi_util.bc_rest_enabled: 'Rest Enabled',
        brcdapi_util.bc_https_enabled: 'HTTPS Protocol Enabled',
        brcdapi_util.bc_eff_protocol: 'Effective Protocol',
        brcdapi_util.bc_max_rest: 'Max Rest Sessions',
        brcdapi_util.bc_https_ka: 'HTTPS Keep Alive Enabled',
        brcdapi_util.bc_https_ka_to: 'HTTPS Keep Alive Timeout',
        brcdapi_util.fru_blade: {
            'part-number': 'Part Number',
            'serial-number': 'S/N',
            'blade-id': 'Blade ID',
            'blade-state': 'State',
            'blade-type': 'Type',
            'fc-port-count': 'Port Count',
            'extension-enabled': 'Extension Enabled',
            # 'firmware-version': 'Firmware',
            # 'manufacturer': 'Manufacturer',
            'slot-number': 'Slot',
            'power-consumption': 'Power Consumed',
            'power-usage': 'Power Used',
            'time-alive': 'Time Alive',
            'time-awake': 'Time Awake',
        },
        brcdapi_util.fru_fan: {
            'part-number': 'Part Number',
            'serial-number': 'S/N',
            'airflow-direction': 'Airflow',
            'operational-state': 'State',
            'speed': 'Speed',
            'unit-number': 'Unit Number',
            'time-alive': 'Time Alive',
            'time-awake': 'Time Awake',
        },
        brcdapi_util.fru_ps: {
            'part-number': 'Part Number',
            'serial-number': 'S/N',
            'operational-state': 'State',
            'power-source': 'Source',
            'unit-number': 'Unit Number',
            'time-alive': 'Time Alive',
            'time-awake': 'Time Awake',
        },
    }


class Switch:

    # Key - Key from any of the switch related API responses. Value is the the column header. This table also controls
    # what is populated on the sheet page. Comment/Uncomment entries as needed.
    switch_display_tbl = {
        # Custom
        # '_FABRIC_NAME': 'Fabric',
        # '_FABRIC_NAME_AND_WWN': 'Fabric',
        # '_FABRIC_WWN': 'Fabric',
        # '_SWITCH_NAME': 'Switch',
        # '_SWITCH_NAME_AND_WWN': 'Switch',
        # '_SWITCH_WWN': 'Switch',
        '_SWITCH_ACTIVE_MAPS_POLICY_NAME': 'Active MAPS Policy',
        # Status Flags
        brcdapi_util.bfls_base_sw_en: 'Base Switch',
        brcdapi_util.bfls_def_sw_status: 'Default Switch',
        brcdapi_util.bfls_ficon_mode_en: 'FICON Switch',
        # Configuration
        brcdapi_util.bfs_banner: 'Banner',
        brcdapi_util.bc_user_name: 'Chassis',
        brcdapi_util.bc_wwn: 'Chassis WWN',
        brcdapi_util.bfs_did: 'Domain ID',
        brcdapi_util.bfs_domain_name: 'Domain Name',
        # 'brocade-fabric/fabric-switch/chassis-user-friendly-name': 'Chassis',  # Depracated?
        # 'brocade-fabric/fabric-switch/chassis-wwn': 'Chassis WWN',  # Depracated?
        # 'brocade-fabric/fabric-switch/domain-id': 'Domain ID',  # Depracated?
        # 'brocade-fabric/fabric-switch/domain-name': 'Domain Name',  # Depracated?
        # 'fabric': brcdapi_util.get_key_val, This is a dict, but I don't know what the members are yet
        brcdapi_util.bfls_fid: 'Fabric ID (FID)',
        brcdapi_util.bfs_fab_user_name: 'Fabric Name',
        brcdapi_util.bfs_fcid_hex: 'FC ID',
        # 'brocade-fabric/fabric-switch/fcid-hex': 'FC ID',
        'brocade-fabric/fabric-switch/fcip-address': 'FCIP Address',
        brcdapi_util.bfs_fw_version: '',
        # 'brocade-fabric/fabric-switch/firmware-version': 'Firmware Version',
        'brocade-fabric/fabric-switch/ip-address': 'Management IPv4 Address',
        'brocade-fibrechannel-switch/fibrechannel-switch/subnet-mask': 'Management Subnet Mask',
        'brocade-fibrechannel-switch/fibrechannel-switch/ip-static-gateway-list/ip-static-gateway': 'IP Static Gateway',
        'brocade-fabric/fabric-switch/ipv6-address': 'Management IPv6 Address',
        'brocade-fabric/fabric-switch/path-count': 'Path Count',
        brcdapi_util.bfs_model: 'Switch Model',
        # 'brocade-fibrechannel-switch/fibrechannel-switch/name': 'Switch WWN',
        brcdapi_util.bfs_op_status: 'Status',
        # Performance all comes back as a list. Need a custom type for this.
        # 'brocade-fibrechannel-trunk/performance/group': 'Performance Group',
        # 'brocade-fibrechannel-trunk/performance/rx-bandwidth': 'Rx Bandwidth (Gb/s)',
        # 'brocade-fibrechannel-trunk/performance/rx-percentage': 'Rx Bandwidth % of Max Bandwidth',
        # 'brocade-fibrechannel-trunk/performance/rx-bandwidth': 'Rx Bandwidth (Gb/s)',
        # 'brocade-fibrechannel-trunk/performance/tx-throughput': 'Rx Throughput Frame Rate (b/s)',
        # 'brocade-fibrechannel-trunk/performance/tx-bandwidth': 'Tx Bandwidth (Gb/s)',
        # 'brocade-fibrechannel-trunk/performance/tx-percentage': 'Tx Bandwidth % of Max Bandwidth',
        # 'brocade-fibrechannel-trunk/performance/tx-bandwidth': 'Tx Bandwidth (Gb/s)',
        # 'brocade-fibrechannel-trunk/performance/tx-throughput': 'Tx Throughput Frame Rate (b/s)',
        # 'brocade-fibrechannel-trunk/performance/txrx-bandwidth': 'Combined Tx + Rx Bandwidth (Gb/s)',
        # 'brocade-fibrechannel-trunk/performance/txrx-throughput': 'Combined Tx + Rx Throughput Frame Rate (b/s)',
        # 'brocade-fibrechannel-trunk/performance/txrx-percentage': 'Combined Tx + Rx Bandwidth % of Max Bandwidth',
        # 'brocade-fibrechannel-trunk/trunk-area/trunk-active': 'Trunking Active',
        # 'brocade-fibrechannel-trunk/trunk-area/trunk-active/master': 'Master',
        brcdapi_util.bfc_portname_format: 'Dynamic Port Name Format',
        brcdapi_util.bfc_portname_mode: 'Port Name Mode',
        brcdapi_util.bfc_area_mode: 'Address (Area) Mode',
        brcdapi_util.bfs_edge_hold: 'Edge-Hold-Time (msec)',
        brcdapi_util.bfs_sw_user_name: 'Switch Name',
        brcdapi_util.bfc_up_time: 'Up Time (days)',
        brcdapi_util.bfs_vf_id: 'Virtual Fabric ID (FID)',
        brcdapi_util.bfs_ag_mode: 'Access Gateway Mode',
        brcdapi_util.bfc_max_logins: 'Maximum switch logins',
        brcdapi_util.bfc_max_flogi_rate: 'Maximum FLOGI rate',
        brcdapi_util.bfc_stage_interval: 'F-Port enable rate (msec)',
        brcdapi_util.bfc_fport_enforce_login: 'Duplicate WWN handling',
        brcdapi_util.bfc_free_fdisc: 'Maximum FDISC logins before staging',
        brcdapi_util.bfc_max_flogi_rate_port: 'Maximum FLOGI rate (logins/sec)',
        # Flags
        brcdapi_util.bfs_enabled_state: 'Switch Enabled',
        brcdapi_util.bfls_isl_enabled: 'Logical ISL (XISL) Enabled',
        brcdapi_util.bfs_principal: 'Fabric Principal',
        brcdapi_util.bfc_port_id_mode: 'Persistent WWN PID Mode',
        brcdapi_util.bfc_idid: 'Insistent Domain ID',
        # RNID
        brcdapi_util.ficon_cup_en: 'FICON CUP: Enabled',
        brcdapi_util.ficon_posc: 'FICON CUP: Programmed Offline State Control',
        brcdapi_util.ficon_uam: 'FICON CUP: User Alert Mode',
        brcdapi_util.ficon_asm: 'FICON CUP: Active Equal Saved',
        brcdapi_util.ficon_dcam: 'FICON CUP: Clock Alert Mode',
        brcdapi_util.ficon_mihpto: 'FICON CUP: MIHPTO',
        brcdapi_util.ficon_uam_fru: 'FICON CUP: Unsolicited FRU Alert',
        brcdapi_util.ficon_uam_hsc: 'FICON CUP: Unsolicited HSC Alert',
        brcdapi_util.ficon_uam_invalid_attach: 'FICON CUP: Unsolicited Invalid Attach Alert',
        brcdapi_util.ficon_sw_rnid_flags: 'RNID: Flags',
        brcdapi_util.ficon_sw_node_params: 'Node Parameters',
        brcdapi_util.ficon_sw_rnid_type: 'RNID: Type',
        brcdapi_util.ficon_sw_rnid_model: 'RNID: Model',
        brcdapi_util.ficon_sw_rnid_mfg: 'RNID: Manufacturer',
        brcdapi_util.ficon_sw_rnid_pant: 'RNID: Plant',
        brcdapi_util.ficon_sw_rnid_seq: 'RNID: S/N',
        brcdapi_util.ficon_sw_rnid_tag: 'RNID: Tag',
        # MAPS
        'brocade-maps/system-resources/memory-usage': 'MAPS System Memory Usage'
    }


class Zone:
    zone_display_tbl = {
        brcdapi_util.bz_eff_cfg: 'Effective Configuration',
        brcdapi_util.bz_eff_db_avail: 'DB Avail Memory',
        brcdapi_util.bz_eff_checksum: 'Checksum',
        brcdapi_util.bz_eff_db_committed: 'Fabric Committed',
        brcdapi_util.bz_eff_cfg_action: 'Configuration Action',
        brcdapi_util.bz_eff_db_max: 'DB Maximum Size',
        brcdapi_util.bz_eff_default_zone: 'Default Zone',
        brcdapi_util.bz_eff_db_trans: 'In Progress Transaction',
        brcdapi_util.bz_eff_trans_token: 'Transaction Token',
        brcdapi_util.bz_eff_db_chassis_committed: 'Zone DB Committed',
        'brocade-zone/fabric-lock/lock-principal-domain-id': 'Lock Principal Domain ID',
        'brocade-zone/fabric-lock/lock-principal-transaction-token': 'Lock Principal Transaction Token',
        'brocade-zone/fabric-lock/timeout': 'Timeout',
        'brocade-zone/fabric-lock/remaining-time': 'Remaining Time',
        'brocade-zone/fabric-lock/client-role': 'Client Role',
        'brocade-zone/fabric-lock/client-user-name': 'Client User Name',
        'brocade-zone/fabric-lock/client-ip-address': 'Client IP Address',
        'brocade-zone/fabric-lock/client-interface': 'Client Interface',
        'brocade-zone/fabric-lock/client-application-name': 'Client Application Name',
    }


class Security:
    security_display_tbl = {
        'brocade-security/sec-crypto-cfg-template/name': 'Crypto Template Name',
        'brocade-security/sec-crypto-cfg-template/name/template': 'Crypto Name Template',
        'brocade-security/sec-crypto-cfg-template/template': 'Crypto CFG Template',
    }


class Port:
    """How to display a port object key value is determined by looking up the key in the list of keys in display passed
    to port_page() in port_display_tbl. If a key is not found but exists in the port object, it is displayed with all
    the default settings. When NPIV is active, only the root login is applicable to the first row displayed for a
    port. If _LOGIN_WWN or _LOGIN_ADDR is specified, then each additional login is displayed directly below.
    In addition to the keys specified in the Rest API Guide, there are the following special keys:
    The keys are either one of the keys defined in 'brocade-interface/fibrechannel' + any of the leaves or one of the
      _BEST_DESC          Finds the first descriptor for the associated WWN in this order:
                              1   If E-Port, the upstream switch & port
                              2   FDMI  Node descriptor - base port only when multiple logins (NPIV) are present
                              3   Name server node descriptor - base port only when multiple logins (NPIV) are present
                              4   FDMI Port descriptor
                              5   Name server port descriptor
                              6   FDMI Node descriptor - Additional NPIV logins only
                              7   Name server node descriptor - Additional NPIV logins only
      _PORT_COMMENTS      Display alerts
      _FABRIC_NAME        Lookup the fabric name. WWN is used if fabric is not named
      _FABRIC_NAME_AND_WWN Lookup the fabric name and include the wwn in parenthesis
      _FABRIC_WWN         Lookup wth fabric WWN
      _SWITCH_NAME        Lookup the switch name. WWN is used if the switch is not named
      _SWITCH_NAME_AND_WWN Lookup the switch name and include the wwn in parenthesis
      _SWITCH_WWN         Lookup wth switch WWN
      _ALIAS              Lookup aliases for the logged in WWNs.
      _PORT_WWN           Switch port WWN. Typically not used. The attached port WWN is _BASE_WWN and _NPIV_WWN
      _LOGIN_WWN          Login WWN on this port. Multiple logins WWNs are listed directly below on the same row.
      _LOGIN_ADDR         Login address on this port. Multiple logins WWNs are listed directly below on the same row.
      _ZONES_DEF          Lookup all zones associated with the login WWN with _ALIAS
      _ZONES_EFF          Same as _ZONES_DEF but for the effective zone only.  See note with _ALIAS
      _NAME_SERVER_NODE   Node symbol in the name server data
      _NAME_SERVER_PORT   Port symbol in the name server data
      _FDMI_NODE          Node symbol in the FDMI data
      _FDMI_PORT          Port symbol in the FDMI data
      _MAPS_GROUP         MAPS group(s) associated with this port
      _PORT_NUMBER        Port number - as it appears on the demarcation panel
      _CONFIG_LINK        'Config' & link, if available, to the port on the "Port Configurations" worksheet
      _STATS_LINK         'Stats' & link, if available, to the port on the "Port Configurations" worksheet
      _ZONE_LINK          'Zone' & link, if available, to the port on the "Port Configurations" worksheet
      _SFP_LINK           'SFP' & link, if available, to the port on the "Port Configurations" worksheet
      _RNID_LINK          'RNID' & link, if available, to the port on the "Port Configurations" worksheet

    The values are dictionaries whose keys are as follows:

    +-------+-------+-----------------------------------------------------------------------------------------------+
    | key   | Type  | Description                                                                                   |
    +=======+=======+===============================================================================================+
    | c     | int   | The column width. Default is whatever the default Excel column width is which is usually 8    |
    +-------+-------+-----------------------------------------------------------------------------------------------+
    | d     | str   | Descriptor (column header). If not specified, the key is used.                                |
    +-------+-------+-----------------------------------------------------------------------------------------------+
    | dc    | bool  | If True, key is for display control only. No content is associated with the record            |
    +-------+-------+-----------------------------------------------------------------------------------------------+
    | m     | bool  | If True, the data (not the column header) should be centered. Default is False                |
    +-------+-------+-----------------------------------------------------------------------------------------------+
    | v     | bool  | If True, displays the column header vertically and centered. Default is False                 |
    +-------+-------+-----------------------------------------------------------------------------------------------+
    """
    port_display_tbl = {
        # Custom
        '_ALIAS': dict(c=28, d='Alias'),
        '_BEST_DESC': dict(c=32, d='Description'),
        '_FABRIC_NAME': dict(c=28, d='Fabric Name'),
        '_FABRIC_NAME_AND_WWN': dict(c=28, d='Fabric Name'),
        '_FABRIC_WWN': dict(c=22, d='Fabric WWN'),
        '_FDMI_NODE': dict(c=35, d='FDMI Node Symbol'),
        '_FDMI_PORT': dict(c=35, d='FDMI Port Symbol'),
        '_LOGIN_ADDR': dict(c=10, d='Login Address'),
        '_LOGIN_WWN': dict(c=22, d='Login WWN'),
        '_MAPS_GROUP': dict(c=22, d='MAPS Group'),
        '_NAME_SERVER_NODE': dict(c=35, d='Name Server Node Symbol'),
        '_NAME_SERVER_PORT': dict(c=35, d='Name Server Port Symbol'),
        '_PORT_COMMENTS': dict(c=26, d='Comments'),
        '_PORT_NUMBER': dict(c=7, d='Port'),
        '_CONFIG_LINK': dict(c=8, d='Config'),
        '_STATS_LINK': dict(c=8, d='Stats'),
        '_ZONE_LINK': dict(c=8, d='Zone'),
        '_SFP_LINK': dict(c=8, d='SFP'),
        '_RNID_LINK': dict(c=8, d='RNID'),
        '_SWITCH_NAME': dict(c=22, d='Switch Name'),
        '_SWITCH_NAME_AND_WWN': dict(c=22, d='Switch Name'),
        '_SWITCH_WWN': dict(c=22, d='Switch WWN'),
        '_ZONES_DEF': dict(c=48, d='In Defined Zone(s)'),
        '_ZONES_EFF': dict(c=48, d='In Effective Zone(s)'),
        # Internal
        '_search/sfp_max_speed': dict(v=True, c=5, d='Max switch port speed Gbps'),
        '_search/sfp_min_speed': dict(v=True, c=5, d='Min switch port speed Gbps'),
        '_search/remote_sfp_max_speed': dict(v=True, c=5, d='Max remote port speed Gbps'),
        '_search/remote_sfp_min_speed': dict(v=True, c=5, d='Min remote port speed Gbps'),
        '_search/speed': dict(v=True, c=5, d='Login speed Gbps'),
        # fibrechannel
        brcdapi_util.fc_eport_credit: dict(v=True, c=8, d='E-Port Credit'),
        brcdapi_util.fc_fport_buffers: dict(v=True, c=8, d='F-Port Buffers'),
        brcdapi_util.fc_fcid: dict(c=10, d='FC Address'),  # Deprecated
        brcdapi_util.fc_fcid_hex: dict(c=10, d='FC Address'),
        brcdapi_util.fc_long_distance: dict(v=True, c=8, d='Long Distance Mode'),
        brcdapi_util.fc_los_tov: dict(v=True, c=12, d='LOS_TOV Mode'),
        brcdapi_util.fc_neighbor: dict(v=True, c=12, d='Neighbor port WWN'),
        brcdapi_util.fc_neighbor_node_wwn: dict(v=True, c=12, d='Neighbor node WWN'),
        brcdapi_util.fc_npiv_pp_limit: dict(v=True, c=6, d='NPIV Limit'),
        brcdapi_util.fc_speed_combo: dict(c=20, d='Speed Combo'),
        brcdapi_util.fc_op_status: dict(c=10, d='Status'),
        brcdapi_util.fc_state: dict(c=11, d='State'),
        brcdapi_util.fc_port_type: dict(c=7, d='Port Type'),
        brcdapi_util.fc_rate_limited_en: dict(v=True, c=8, d='Rate Limit'),
        brcdapi_util.fc_speed: dict(v=True, c=6, d='Login Speed Gbps'),
        brcdapi_util.fc_max_speed: dict(v=True, c=6, d='Max Speed Gbps'),
        brcdapi_util.fc_user_name: dict(c=28, d='Port Name'),
        brcdapi_util.fc_wwn: dict(c=22, d='Switch Port WWN'),
        'fibrechannel/average-receive-frame-size': dict(v=True, c=8, d='Average Rx Frame Size'),
        'fibrechannel/average-transmit-frame-size': dict(v=True, c=8, d='Average Tx Frame Size'),
        'fibrechannel/average-transmit-buffer-usage': dict(v=True, c=8, d='Avg Tx buffer usage'),
        'fibrechannel/average-receive-buffer-usage': dict(v=True, c=8, d='Avg Rx buffer usage'),
        'fibrechannel/port-type-string': dict(c=15, d='Port Type'),
        'fibrechannel/reserved-buffers': dict(v=True, c=8, d='Reserved Buffers'),
        'fibrechannel/authentication-protocol': dict(c=15, d='Authentication Protocol'),
        brcdapi_util.fc_chip_buf_avail: dict(v=True, c=8, d='Chip Buffers Available'),
        brcdapi_util.fc_chip_instance: dict(v=True, c=8, d='Chip Instance'),
        'fibrechannel/clean-address-enabled': dict(v=True, c=8, d='Clean Address Enabled'),
        brcdapi_util.fc_encrypt: dict(v=True, c=8, d='Encryption Enabled'),
        brcdapi_util.fc_index: dict(v=True, c=8, d='Port Index'),
        'fibrechannel/le-domain': dict(v=True, c=8, d='LE Domain'),
        'fibrechannel/measured-link-distance': dict(v=True, c=8, d='Measured Link Distance'),
        'fibrechannel/pod-license-state': dict(c=15, d='POD License State'),
        'fibrechannel/port-health': dict(v=True, c=8, d='Port Health'),
        'fibrechannel/port-peer-beacon-enabled': dict(v=True, c=8, d='Port Peer Beacon Enabled'),
        # Flags
        brcdapi_util.fc_auto_neg: dict(v=True, m=True, c=5, d='Auto-Negotiate'),
        brcdapi_util.fc_comp_act: dict(v=True, m=True, c=5, d='Compression Active'),
        brcdapi_util.fc_comp_en: dict(v=True, m=True, c=5, d='Compression Enabled'),
        brcdapi_util.fc_credit_recov_act: dict(v=True, m=True, c=5, d='Credit Recovery Active'),
        brcdapi_util.fc_credit_recov_en: dict(v=True, m=True, c=5, d='Credit Recovery Enabled'),
        'fibrechannel/csctl-mode-enabled': dict(v=True, m=True, c=5, d='CSCTL Enabled'),
        brcdapi_util.fc_d_port_en: dict(v=True, m=True, c=5, d='D-Port Enabled'),
        brcdapi_util.fc_e_port_dis: dict(v=True, m=True, c=5, d='E-Port Disabled'),
        # 'fibrechannel/enabled-state': dict(v=True, m=True, c=5, d='Enabled'),  # Deprecated in FOS 8.2.1b
        'fibrechannel/encryption-active': dict(v=True, m=True, c=5, d='Encryption Active'),
        'fibrechannel/ex-port-enabled': dict(v=True, m=True, c=5, d='XISL Enabled'),
        'fibrechannel/fault-delay-enabled': dict(v=True, m=True, c=5, d='Fault Delay Enabled'),
        'fibrechannel/fec-enabled': dict(v=True, m=True, c=5, d='FEC Enabled'),
        'fibrechannel/fec-active': dict(v=True, m=True, c=5, d='FEC Active'),
        'fibrechannel/g-port-locked': dict(v=True, m=True, c=5, d='G-Port Locked'),
        brcdapi_util.fc_enabled: dict(v=True, m=True, c=5, d='Enabled'),
        'fibrechannel/isl-ready-mode-enabled': dict(v=True, m=True, c=5, d='ISL Ready Mode Enabled'),
        'fibrechannel/mirror-port-enabled': dict(v=True, m=True, c=5, d='Mirror Port Enabled'),
        'fibrechannel/n-port-enabled': dict(v=True, m=True, c=5, d='N-Port Enabled'),
        'fibrechannel/non-dfe-enabled': dict(v=True, m=True, c=5, d='Non-DFE Enabled'),
        brcdapi_util.fc_npiv_en: dict(v=True, m=True, c=5, d='NPIV Enabled'),
        'fibrechannel/npiv-flogi-logout-enabled': dict(v=True, m=True, c=5, d='NPIV FLOGI Logout Enabled'),
        'fibrechannel/path-count': dict(v=True, m=True, c=5, d='Path Count'),
        'fibrechannel/persistent-disable': dict(v=True, m=True, c=5, d='Persistent Disable'),
        'fibrechannel/port-autodisable-enabled': dict(v=True, m=True, c=5, d='Autodisable Enabled'),
        'fibrechannel/qos-enabled': dict(v=True, m=True, c=5, d='QoS Enabled'),
        'fibrechannel/rscn-suppression-enabled': dict(v=True, m=True, c=5, d='RSCN Suppression Enabled'),
        'fibrechannel/target-driven-zoning-enable': dict(v=True, m=True, c=5, d='Target Driven Zoning Enabled'),
        'fibrechannel/trunk-port-enabled': dict(v=True, m=True, c=5, d='Trunk Port Enabled'),
        'fibrechannel/vc-link-init': dict(v=True, m=True, c=5, d='VC Link Init'),
        'fibrechannel/via-tts-fec-enabled': dict(v=True, m=True, c=5, d='FEC via TTS Enabled'),
        # Statistics
        brcdapi_util.stats_addr: dict(v=True, c=8, d='Address Errors'),
        brcdapi_util.stats_bad_eof: dict(v=True, c=8, d='Bad EOF'),
        brcdapi_util.stats_bb_credit: dict(v=True, c=10, d='Zero BB Credit'),
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit': dict(v=True, c=8, d='Remote BB Credit'),
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit':
            dict(v=True, c=8, d='Remote Peer BB Credit'),
        'fibrechannel-statistics/class-1-frames': dict(v=True, c=8, d='Class 1 Frames'),
        'fibrechannel-statistics/class-2-frames': dict(v=True, c=8, d='Class 2 Frames'),
        'fibrechannel-statistics/class-3-frames': dict(c=14, d='Class 3 Frames'),
        brcdapi_util.stats_c3: dict(v=True, c=8, d='C3 Frame Discards'),
        brcdapi_util.stats_c3_in: dict(v=True, c=8, d='Rx C3 Frames discarded'),
        brcdapi_util.stats_c3_out: dict(v=True, c=8, d='Tx C3 Frame Discards'),
        brcdapi_util.stats_crc: dict(v=True, c=8, d='CRC Errors'),
        brcdapi_util.stats_delimiter: dict(v=True, c=8, d='Delimiter Errors'),
        brcdapi_util.stats_enc_disp: dict(v=True, c=8, d='Encoding Disparity Errors'),
        brcdapi_util.stats_enc: dict(v=True, c=8, d='Encoding Errors Outside Frame'),
        brcdapi_util.stats_f_busy: dict(v=True, c=8, d='Frame Busy'),
        brcdapi_util.stats_f_rjt: dict(v=True, c=8, d='Frame Rejects'),
        brcdapi_util.stats_long: dict(v=True, c=8, d='Frames Too Long'),
        brcdapi_util.stats_in_crc: dict(v=True, c=8, d='Incoming CRC Errors'),
        'fibrechannel-statistics/remote-crc-errors': dict(v=True, c=8, d='Remote CRC Errors'),
        'fibrechannel-statistics/in-frame-rate': dict(v=True, c=8, d='Rx Frame Rate'),
        brcdapi_util.stats_in_frames: dict(c=15, d='Rx Frames'),
        brcdapi_util.stats_in_lcs: dict(v=True, c=8, d='In LCS'),
        brcdapi_util.stats_in_reset: dict(v=True, c=8, d='Link Resets'),
        'fibrechannel-statistics/in-max-frame-rate': dict(v=True, c=8, d='Rx Max Frame Rate'),
        'fibrechannel-statistics/in-multicast-pkts': dict(v=True, c=8, d='Rx Multi-cast Packets'),
        'fibrechannel-statistics/in-octets': dict(c=14, d='Rx Octets'),
        brcdapi_util.stats_off_seq: dict(v=True, c=8, d='Rx Offline Sequence'),
        'fibrechannel-statistics/in-peak-rate': dict(v=True, c=8, d='Rx Peak Rate'),
        'fibrechannel-statistics/in-rate': dict(v=True, c=8, d='Rx Rate'),
        'fibrechannel-statistics/input-buffer-full': dict(v=True, c=8, d='Input Buffer Full'),
        brcdapi_util.stats_ios: dict(v=True, c=8, d='Invalid Ordered Sets'),
        brcdapi_util.stats_itw: dict(v=True, c=8, d='Invalid Transmission Words (ITW)'),
        'fibrechannel-statistics/remote-invalid-transmission-words': \
            dict(v=True, c=8, d='Remote Invalid Transmission Words (ITW)'),
        brcdapi_util.stats_link_fail: dict(v=True, c=8, d='Link Failures'),
        'fibrechannel-statistics/remote-link-failures': dict(v=True, c=8, d='Remote Link Failures'),
        brcdapi_util.stats_loss_sig: dict(v=True, c=8, d='Loss Of Signal'),
        'fibrechannel-statistics/remote-loss-of-signal': dict(v=True, c=8, d='Remote Loss Of Signal'),
        brcdapi_util.stats_loss_sync: dict(v=True, c=8, d='Loss Of Sync'),
        'fibrechannel-statistics/remote-loss-of-sync': dict(v=True, c=8, d='Remote Loss Of Sync'),
        brcdapi_util.stats_multicast_to: dict(v=True, c=8, d='Multi-cast Timeouts'),
        'fibrechannel-statistics/out-frame-rate': dict(v=True, c=8, d='Tx Frame Rate'),
        brcdapi_util.stats_out_frames: dict(c=14, d='Tx Frames'),
        brcdapi_util.stats_out_reset: dict(v=True, c=8, d='Tx Link Resets'),
        'fibrechannel-statistics/out-max-frame-rate': dict(v=True, c=8, d='Tx Max Frame Rate'),
        'fibrechannel-statistics/out-multicast-pkts': dict(v=True, c=8, d='Tx Multicast Pkts'),
        'fibrechannel-statistics/out-octets': dict(c=14, d='Tx Octets'),
        brcdapi_util.stats_out_off_seq: dict(v=True, c=8, d='Tx Offline Sequences'),
        'fibrechannel-statistics/out-peak-rate': dict(v=True, c=8, d='Tx Peak Rate'),
        'fibrechannel-statistics/out-rate': dict(v=True, c=8, d='Tx Rate'),
        brcdapi_util.stats_p_busy: dict(v=True, c=8, d='P-Busy Frames'),
        brcdapi_util.stats_p_rjt: dict(v=True, c=8, d='P-Reject Frames'),
        'fibrechannel-statistics/pcs-block-errors': dict(v=True, c=8, d='PCS Block Errors'),
        brcdapi_util.stats_seq: dict(v=True, c=8, d='Primitive Sequence Error'),
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error':
            dict(v=True, c=8, d='Remote Primitive Sequence Error'),
        'fibrechannel-statistics/sampling-interval': dict(v=True, c=8, d='Sampling Interval (sec)'),
        brcdapi_util.stats_time: dict(c=24, d='Time Generated'),
        brcdapi_util.stats_rdy: dict(v=True, c=8, d='To Many RDYs'),
        brcdapi_util.stats_tunc: dict(v=True, c=8, d='Truncated Frames'),
        'fibrechannel-statistics/remote-fec-uncorrected': dict(v=True, c=8, d='Truncated Frames'),
        brcdapi_util.stats_fpr: dict(v=True, c=8, d='Frames Processing Required'),
        brcdapi_util.stats_to: dict(v=True, c=8, d='Frames Timed Out'),
        brcdapi_util.stats_trans: dict(v=True, c=8,
                                                                              d='Tx Unavailable Errors'),
        # Media (media-rdp)
        'media-rdp/connector': dict(v=True, c=6, d='Connector Type'),
        brcdapi_util.sfp_wave: dict(v=True, c=8, d='Wavelength'),
        'media-rdp/remote-laser-type': dict(c=15, d='Remote Laser Type'),
        'media-rdp/current': dict(v=True, c=8, d='Current (mAmps)'),
        'media-rdp/remote-media-current': dict(v=True, c=8, d='Remote Current (mAmps)'),
        'media-rdp/date-code': dict(v=True, c=8, d='Date Code'),
        'media-rdp/remote-optical-product-data/date-code': dict(v=True, c=8, d='Remote Date Code'),
        'media-rdp/encoding': dict(v=True, c=8, d='Encoding'),
        'media-rdp/identifier': dict(v=True, c=6, d='Identifier'),
        'media-rdp/remote-identifier': dict(v=True, c=6, d='Remote Identifier'),
        'media-rdp/media-distance': dict(c=18, d='Distance'),
        'media-rdp/media-speed-capability': dict(c=8, d='Speed'),
        'media-rdp/remote-media-speed-capability': dict(c=8, d='Remote Speed'),
        brcdapi_util.sfp_pn: dict(c=14, d='Part Number'),
        'media-rdp/remote-optical-product-data/part-number': dict(c=17, d='Remote Part Number'),
        brcdapi_util.sfp_power_on: dict(v=True, c=8, d='Power on time (days)'),
        brcdapi_util.sfp_rx_pwr: dict(v=True, c=8, d='Rx Power (uW)'),
        'media-rdp/remote-media-rx-power': dict(v=True, c=8, d='Remote Rx Power (uW)'),
        brcdapi_util.sfp_tx_pwr: dict(v=True, c=8, d='Tx Power (uW)'),
        'media-rdp/remote-media-tx-power': dict(v=True, c=8, d='Remote Tx Power (uW)'),
        brcdapi_util.sfp_sn: dict(c=18, d='Serial Number'),
        'media-rdp/remote-optical-product-data/serial-number': dict(c=18, d='Remote Serial Number'),
        'media-rdp/temperature': dict(v=True, c=6, d='Temperature (C)'),
        'media-rdp/remote-media-temperature': dict(v=True, c=6, d='Remote Temperature (C)'),
        brcdapi_util.sfp_vendor: dict(c=15, d='Vendor'),
        'media-rdp/remote-optical-product-data/vendor-name': dict(c=10, d='Remote Vendor'),
        brcdapi_util.sfp_oui: dict(c=8, d='Vendor OUI'),
        'media-rdp/vendor-revision': dict(v=True, m=True, c=4, d='Revision'),
        'media-rdp/remote-optical-product-data/vendor-revision': dict(v=True, m=True, c=4, d='Remote Revision'),
        'media-rdp/voltage': dict(v=True, c=8, d='Voltage (mVolts)'),
        'media-rdp/remote-media-voltage': dict(v=True, c=8, d='Remote Voltage (mVolts)'),
        # Not using any of the remote alarm or warn levels. This is the remote equivalent to what MAPS replaced
        'media-rdp/remote-media-temperature-alert/high-alarm': dict(v=True, c=6, d='Remote Temp High Alarm'),
        'media-rdp/remote-media-temperature-alert/high-warning': dict(v=True, c=6, d='Remote Temp High Warning'),
        'media-rdp/remote-media-temperature-alert/low-alarm': dict(v=True, c=6, d='Remote Temp Low Alarm'),
        'media-rdp/remote-media-temperature-alert/low-warning': dict(v=True, c=6, d='Remote Temp Low Warning'),
        'media-rdp/remote-media-tx-bias-alert/high-alarm': dict(v=True, c=6, d='Remote Current High Alarm'),
        'media-rdp/remote-media-tx-bias-alert/high-warning': dict(v=True, c=6, d='Remote Current High Warning'),
        'media-rdp/remote-media-tx-bias-alert/low-alarm': dict(v=True, c=6, d='Remote Current Low Alarm'),
        'media-rdp/remote-media-tx-bias-alert/low-warning': dict(v=True, c=6, d='Remote Current Low Warning'),
        'media-rdp/remote-media-tx-power-alert/high-alarm': dict(v=True, c=6, d='Remote Tx Power High Alarm'),
        'media-rdp/remote-media-tx-power-alert/high-warning': dict(v=True, c=6, d='Remote Tx Power High Warning'),
        'media-rdp/remote-media-tx-power-alert/low-alarm': dict(v=True, c=6, d='Remote Tx Power Low Alarm'),
        'media-rdp/remote-media-tx-power-alert/low-warning': dict(v=True, c=6, d='Remote Tx Power Low Warning'),
        'media-rdp/remote-media-rx-power-alert/high-alarm': dict(v=True, c=6, d='Remote Rx Power High Alarm'),
        'media-rdp/remote-media-rx-power-alert/high-warning': dict(v=True, c=6, d='Remote Rx Power High Warning'),
        'media-rdp/remote-media-rx-power-alert/low-alarm': dict(v=True, c=6, d='Remote Rx Power Low Alarm'),
        'media-rdp/remote-media-rx-power-alert/low-warning': dict(v=True, c=6, d='Remote Rx Power Low Warning'),
        'media-rdp/remote-media-voltage-alert/high-alarm': dict(v=True, c=6, d='Remote Voltage High Alarm'),
        'media-rdp/remote-media-voltage-alert/high-warning': dict(v=True, c=6, d='Remote Voltage High Warning'),
        'media-rdp/remote-media-voltage-alert/low-alarm': dict(v=True, c=6, d='Remote Voltage Low Alarm'),
        'media-rdp/remote-media-voltage-alert/low-warning': dict(v=True, c=6, d='Remote Voltage Low Warning'),
        # RNID
        'rnid/format': dict(v=True, c=5, d='Format'),
        'rnid/flags': dict(c=8, d='Flags'),
        'rnid/node-parameters': dict(c=20, d='Node Parameters'),
        'rnid/type-number': dict(c=10, d='Type'),
        'rnid/model-number': dict(c=10, d='Model'),
        'rnid/manufacturer': dict(c=8, d='Mfg'),
        'rnid/plant': dict(c=8, d='Plant'),
        'rnid/sequence-number': dict(c=16, d='S/N'),
        'rnid/tag': dict(c=8, d='Tag'),
    }

    port_config_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        brcdapi_util.fc_user_name,
        '_ALIAS',
        brcdapi_util.fc_fcid_hex,
        brcdapi_util.fc_port_type,
        brcdapi_util.sfp_wave,
        brcdapi_util.fc_enabled,
        brcdapi_util.fc_op_status,
        brcdapi_util.fc_state,
        '_BEST_DESC',
        '_MAPS_GROUP',
        brcdapi_util.fc_eport_credit,
        brcdapi_util.fc_fport_buffers,
        brcdapi_util.fc_long_distance,
        # 'fibrechannel/name',        # Not copied to the object because it is the object key
        # brcdapi_util.fc_neighbor,    # Handled separately
        brcdapi_util.fc_npiv_pp_limit,
        brcdapi_util.fc_speed_combo,
        brcdapi_util.fc_rate_limited_en,
        brcdapi_util.fc_speed,
        # brcdapi_util.fc_wwn,
        # Flags
        # 'fibrechannel/path-count',  # Has conflicting meaning. RFE #16 to fix.
        'fibrechannel/persistent-disable',
        brcdapi_util.fc_auto_neg,
        brcdapi_util.fc_comp_act,
        brcdapi_util.fc_comp_en,
        'fibrechannel/encryption-active',
        'fibrechannel/target-driven-zoning-enable',
        'fibrechannel/g-port-locked',
        brcdapi_util.fc_e_port_dis,
        'fibrechannel/n-port-enabled',
        brcdapi_util.fc_d_port_en,
        'fibrechannel/ex-port-enabled',
        'fibrechannel/fec-enabled',
        'fibrechannel/mirror-port-enabled',
        brcdapi_util.fc_credit_recov_en,
        brcdapi_util.fc_credit_recov_act,
        'fibrechannel/fec-active',
        'fibrechannel/csctl-mode-enabled',
        'fibrechannel/fault-delay-enabled',
        'fibrechannel/trunk-port-enabled',
        'fibrechannel/vc-link-init',
        'fibrechannel/isl-ready-mode-enabled',
        'fibrechannel/rscn-suppression-enabled',
        brcdapi_util.fc_los_tov,
        brcdapi_util.fc_npiv_en,
        'fibrechannel/npiv-flogi-logout-enabled',
        'fibrechannel/non-dfe-enabled',
        'fibrechannel/via-tts-fec-enabled',
        'fibrechannel/port-autodisable-enabled',
        'fibrechannel/qos-enabled',
    )

    # Similar to port_config_tbl but for the port statistics page. From brocade-interface/fibrechannel-statistics
    port_stats_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        brcdapi_util.fc_fcid_hex,
        brcdapi_util.fc_port_type,
        '_ALIAS',
        '_BEST_DESC',
        brcdapi_util.fc_enabled,
        brcdapi_util.fc_op_status,
        brcdapi_util.stats_time,
        'fibrechannel-statistics/sampling-interval',
        brcdapi_util.stats_addr,
        brcdapi_util.stats_bad_eof,
        brcdapi_util.stats_bb_credit,
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit',
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit',
        'fibrechannel-statistics/class-1-frames',
        'fibrechannel-statistics/class-2-frames',
        brcdapi_util.stats_c3,
        'fibrechannel-statistics/class-3-frames',
        brcdapi_util.stats_c3_in,
        brcdapi_util.stats_c3_out,
        brcdapi_util.stats_crc,
        'fibrechannel-statistics/remote-crc-errors',
        'fibrechannel-statistics/remote-fec-uncorrected',
        brcdapi_util.stats_delimiter,
        brcdapi_util.stats_enc_disp,
        brcdapi_util.stats_enc,
        brcdapi_util.stats_f_busy,
        brcdapi_util.stats_f_rjt,
        brcdapi_util.stats_long,
        brcdapi_util.stats_in_crc,
        'fibrechannel-statistics/in-frame-rate',
        brcdapi_util.stats_in_frames,
        brcdapi_util.stats_in_lcs,
        brcdapi_util.stats_in_reset,
        'fibrechannel-statistics/in-max-frame-rate',
        'fibrechannel-statistics/in-multicast-pkts',
        'fibrechannel-statistics/in-octets',
        brcdapi_util.stats_off_seq,
        'fibrechannel-statistics/in-peak-rate',
        'fibrechannel-statistics/in-rate',
        'fibrechannel-statistics/input-buffer-full',
        brcdapi_util.stats_ios,
        brcdapi_util.stats_itw,
        'fibrechannel-statistics/remote-invalid-transmission-words',
        brcdapi_util.stats_link_fail,
        'fibrechannel-statistics/remote-link-failures',
        brcdapi_util.stats_loss_sig,
        'fibrechannel-statistics/remote-loss-of-signal',
        brcdapi_util.stats_loss_sync,
        'fibrechannel-statistics/remote-loss-of-sync',
        brcdapi_util.stats_multicast_to,
        'fibrechannel-statistics/out-frame-rate',
        brcdapi_util.stats_out_frames,
        brcdapi_util.stats_out_reset,
        'fibrechannel-statistics/out-max-frame-rate',
        'fibrechannel-statistics/out-multicast-pkts',
        'fibrechannel-statistics/out-octets',
        brcdapi_util.stats_out_off_seq,
        'fibrechannel-statistics/out-peak-rate',
        'fibrechannel-statistics/out-rate',
        brcdapi_util.stats_p_busy,
        brcdapi_util.stats_p_rjt,
        'fibrechannel-statistics/pcs-block-errors',
        brcdapi_util.stats_seq,
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error',
        # 'fibrechannel-statistics/reset-statistics', # This is write only. Here for negative testing purposes only.
        brcdapi_util.stats_rdy,
        brcdapi_util.stats_tunc,
        brcdapi_util.stats_fpr,
        brcdapi_util.stats_fpr,
        brcdapi_util.stats_to,
        brcdapi_util.stats_trans,
        'fibrechannel/average-receive-frame-size',
        'fibrechannel/average-transmit-frame-size',
    )
    # Similar to port_stats_tbl but for a single port when all port objects are a point in time sample
    port_stats1_tbl = (
        brcdapi_util.stats_time,
        brcdapi_util.stats_addr,
        brcdapi_util.stats_bad_eof,
        brcdapi_util.stats_bb_credit,
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit',
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit',
        'fibrechannel-statistics/class-1-frames',
        'fibrechannel-statistics/class-2-frames',
        brcdapi_util.stats_c3,
        'fibrechannel-statistics/class-3-frames',
        brcdapi_util.stats_c3_in,
        brcdapi_util.stats_c3_out,
        brcdapi_util.stats_crc,
        'fibrechannel-statistics/remote-crc-errors',
        'fibrechannel-statistics/remote-fec-uncorrected',
        brcdapi_util.stats_delimiter,
        brcdapi_util.stats_enc_disp,
        brcdapi_util.stats_enc,
        brcdapi_util.stats_f_busy,
        brcdapi_util.stats_f_rjt,
        brcdapi_util.stats_long,
        brcdapi_util.stats_in_crc,
        'fibrechannel-statistics/in-frame-rate',
        brcdapi_util.stats_in_frames,
        brcdapi_util.stats_in_lcs,
        brcdapi_util.stats_in_reset,
        'fibrechannel-statistics/in-max-frame-rate',
        'fibrechannel-statistics/in-multicast-pkts',
        'fibrechannel-statistics/in-octets',
        brcdapi_util.stats_off_seq,
        'fibrechannel-statistics/in-peak-rate',
        'fibrechannel-statistics/in-rate',
        'fibrechannel-statistics/input-buffer-full',
        brcdapi_util.stats_ios,
        brcdapi_util.stats_itw,
        'fibrechannel-statistics/remote-invalid-transmission-words',
        brcdapi_util.stats_link_fail,
        'fibrechannel-statistics/remote-link-failures',
        brcdapi_util.stats_loss_sig,
        'fibrechannel-statistics/remote-loss-of-signal',
        brcdapi_util.stats_loss_sync,
        'fibrechannel-statistics/remote-loss-of-sync',
        brcdapi_util.stats_multicast_to,
        'fibrechannel-statistics/out-frame-rate',
        brcdapi_util.stats_out_frames,
        brcdapi_util.stats_out_reset,
        'fibrechannel-statistics/out-max-frame-rate',
        'fibrechannel-statistics/out-multicast-pkts',
        'fibrechannel-statistics/out-octets',
        brcdapi_util.stats_out_off_seq,
        'fibrechannel-statistics/out-peak-rate',
        'fibrechannel-statistics/out-rate',
        brcdapi_util.stats_p_busy,
        brcdapi_util.stats_p_rjt,
        'fibrechannel-statistics/pcs-block-errors',
        brcdapi_util.stats_seq,
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error',
        brcdapi_util.stats_rdy,
        brcdapi_util.stats_tunc,
        brcdapi_util.stats_fpr,
        brcdapi_util.stats_fpr,
        brcdapi_util.stats_to,
        brcdapi_util.stats_trans,
        'fibrechannel/average-receive-frame-size',
        'fibrechannel/average-transmit-frame-size',
    )
    port_sfp_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        brcdapi_util.fc_fcid_hex,
        brcdapi_util.fc_port_type,
        brcdapi_util.fc_op_status,
        '_ALIAS',
        '_BEST_DESC',
        brcdapi_util.sfp_sn,
        'media-rdp/remote-optical-product-data/serial-number',
        brcdapi_util.sfp_wave,
        'media-rdp/remote-laser-type',
        'media-rdp/media-distance',
        'media-rdp/media-speed-capability',
        'media-rdp/remote-media-speed-capability',
        brcdapi_util.sfp_power_on,
        brcdapi_util.sfp_tx_pwr,
        'media-rdp/remote-media-tx-power',
        brcdapi_util.sfp_rx_pwr,
        'media-rdp/remote-media-rx-power',
        'media-rdp/temperature',
        'media-rdp/remote-media-temperature',
        'media-rdp/current',
        'media-rdp/remote-media-current',
        'media-rdp/voltage',
        'media-rdp/remote-media-voltage',
        'media-rdp/identifier',
        'media-rdp/remote-identifier',
        'media-rdp/connector',
        'media-rdp/date-code',
        'media-rdp/remote-optical-product-data/date-code',
        'media-rdp/encoding',
        brcdapi_util.sfp_vendor,
        'media-rdp/remote-optical-product-data/vendor-name',
        brcdapi_util.sfp_oui,
        brcdapi_util.sfp_pn,
        'media-rdp/remote-optical-product-data/part-number',
        'media-rdp/vendor-revision',
        'media-rdp/remote-optical-product-data/vendor-revision',
    )
    port_rnid_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        brcdapi_util.fc_index,
        brcdapi_util.fc_fcid_hex,
        '_ALIAS',
        '_BEST_DESC',
        brcdapi_util.fc_op_status,
        brcdapi_util.fc_port_type,
        'rnid/format',
        'rnid/flags',
        'rnid/node-parameters',
        'rnid/type-number',
        'rnid/model-number',
        'rnid/manufacturer',
        'rnid/plant',
        'rnid/sequence-number',
        'rnid/tag',
    )
    port_zone_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        brcdapi_util.fc_op_status,
        brcdapi_util.fc_speed,
        '_LOGIN_ADDR',
        '_LOGIN_WWN',
        '_ALIAS',
        '_ZONES_DEF',
        '_ZONES_EFF',
        '_NAME_SERVER_NODE',
        '_NAME_SERVER_PORT',
        '_FDMI_NODE',
        '_FDMI_PORT',
    )

    
class Login:
    # Includes FDMI as well. FDMI node data is preceded with '_FDMI_NODE.' followed by the key. brcddb.report.login
    # separates the key on '.'. Similarly, FDMI port data is preceded with '_FDMI_PORT'.
    # How to display a login object key value is determined by looking up the key in the list of keys in display passed
    # to login_page() in login_display_tbl. If a key is not found but exists in the login object, it is displayed with
    # all the default settings. The keys are either one of the keys defined in 'brocade-interface/fibrechannel' or one
    # of the special keys below:
    #   _LOGIN_COMMENTS     Display alerts
    #   _FABRIC_NAME        Lookup the fabric name. WWN is used if fabric is not named
    #   _FABRIC_NAME_AND_WWN Lookup the fabric name and include the wwn in parenthesis
    #   _FABRIC_WWN         Lookup wth switch WWN
    #   _SWITCH_NAME        Lookup the switch name. WWN is used if the switch is not named
    #   _SWITCH_NAME_AND_WWN Lookup the switch name and include the wwn in parenthesis
    #   _SWITCH_WWN         Lookup wth switch WWN
    #   _ALIAS              Lookup aliases for the login WWN.
    #   _ZONES_DEF          Lookup all zones associated with the login WWN
    #   _ZONES_EFF          Same as _ZONES_DEF but for the effective zone only.
    #   _NAME_SERVER_PORT   Port symbol in the name server data
    #   _FDMI_PORT          Port symbol in the FDMI data
    #   _PORT_NUMBER        Port number - as it appears on the demarcation panel
    # The values are dictionaries whose keys are as follows:
    # 'v'   If True, displays the column header vertically. Default is False
    # 'c'   The column width. Default is whatever the default Excel column width is
    # 'l'   The sub-key where to look for the key. Use a '/' to delineate nested dictionaries.
    # 'd'   Descriptor (column header). If not specified, try check brcddb_common.port_flag_friendly, then use key.
    # 'dc'  If True, key is for display control only. No content is associated with the record
    login_display_tbl = {
        # Custom
        '_LOGIN_COMMENTS': dict(c=26, d='Comments'),
        '_LOGIN_WWN': dict(c=22, d='Login WWN'),
        '_FABRIC_NAME': dict(c=28, d='Fabric Name'),
        '_FABRIC_NAME_AND_WWN': dict(c=22, d='Fabric Name'),
        '_FABRIC_WWN': dict(c=22, d='Fabric WWN'),
        '_SWITCH_NAME': dict(c=28, d='Switch Name'),
        '_SWITCH_NAME_AND_WWN': dict(c=50, d='Switch Name'),
        '_SWITCH_WWN': dict(c=22, d='Switch WWN'),
        '_PORT_NUMBER': dict(c=7, d='Port'),
        '_ALIAS': dict(c=28, d='Alias'),
        '_ZONES_DEF': dict(c=48, d='In Defined Zone(s)'),
        '_ZONES_EFF': dict(c=48, d='In Effective Zone(s)'),
        # fibrechannel-name-server
        'brocade-name-server/fibrechannel-name-server/class-of-service': dict(v=True, c=8, d='Class of Service'),
        'brocade-name-server/fibrechannel-name-server/fabric-port-name': dict(v=False, c=22, d='Fabric Port WWN'),
        'brocade-name-server/fibrechannel-name-server/fc4-features': dict(v=False, c=24, d='FC4 Features'),
        'brocade-name-server/fibrechannel-name-server/fc4-type': dict(v=False, c=12, d='FC4 Type'),
        'brocade-name-server/fibrechannel-name-server/link-speed': dict(v=False, c=8, d='Speed'),
        'brocade-name-server/fibrechannel-name-server/name-server-device-type': dict(v=False, c=30, d='Device Type'),
        'brocade-name-server/fibrechannel-name-server/node-name': dict(v=False, c=22, d='HBA Node WWN'),
        'brocade-name-server/fibrechannel-name-server/node-symbolic-name': dict(v=False, c=42, d='Node Symbol'),
        'brocade-name-server/fibrechannel-name-server/permanent-port-name': dict(v=False, c=22, d='Permanent Port WWN'),
        'brocade-name-server/fibrechannel-name-server/port-id': dict(v=False, c=10, d='Address'),
        'brocade-name-server/fibrechannel-name-server/port-index': dict(v=False, c=6, d='Port Index'),
        'brocade-name-server/fibrechannel-name-server/port-name': dict(v=False, c=22, d='Login WWN'),
        'brocade-name-server/fibrechannel-name-server/port-properties': dict(v=False, c=12, d='Port properties'),
        'brocade-name-server/fibrechannel-name-server/port-symbolic-name': dict(v=False, c=35, d='Port Symbol'),
        'brocade-name-server/fibrechannel-name-server/port-type': dict(v=False, c=7, d='Port Type'),
        'brocade-name-server/fibrechannel-name-server/state-change-registration': dict(v=False, c=30,
                                                                                       d='State Change Registration'),

        'brocade-name-server/fibrechannel-name-server/share-area': dict(v=True, m=True, c=5,
                                                                        d='Shared area addressing'),
        'brocade-name-server/fibrechannel-name-server/frame-redirection': dict(v=True, m=True, c=5,
                                                                               d='Frame redirection zoning'),
        'brocade-name-server/fibrechannel-name-server/partial': dict(v=True, m=True, c=5, d='Login incomplete'),
        'brocade-name-server/fibrechannel-name-server/lsan': dict(v=True, m=True, c=5, d='Part of LSAN zone'),
        'brocade-name-server/fibrechannel-name-server/cascaded-ag': dict(v=True, m=True, c=5, d='Connected to AG'),
        'brocade-name-server/fibrechannel-name-server/connected-through-ag': dict(v=True, m=True, c=5,
                                                                                  d='Connected through AG'),
        'brocade-name-server/fibrechannel-name-server/real-device-behind-ag':
            dict(v=True, m=True, c=5, d='Real device (not NPIV) in AG'),
        'brocade-name-server/fibrechannel-name-server/fcoe-device': dict(v=True, m=True, c=5, d='FCoE device'),
        'brocade-name-server/fibrechannel-name-server/slow-drain-device-quarantine': dict(v=True, m=True, c=5,
                                                                                          d='SDDQ'),

        # FDMI Node
        '_FDMI_NODE.brocade-fdmi/hba/boot-bios-version': dict(v=True, c=12, d='FDMI Boot BIOS Version'),
        '_FDMI_NODE.brocade-fdmi/hba/domain-id': dict(v=True, c=5, d='FDMI Node Domain ID'),
        '_FDMI_NODE.brocade-fdmi/hba/driver-version': dict(v=False, c=12, d='FDMI Driver Version'),
        '_FDMI_NODE.brocade-fdmi/hba/fabric-name': dict(v=False, c=22, d='FDMI Node Fabric Name'),
        '_FDMI_NODE.brocade-fdmi/hba/firmware-version': dict(v=False, c=12, d='FDMI Firmware Version'),
        '_FDMI_NODE.brocade-fdmi/hba/hardware-version': dict(v=False, c=12, d='FDMI Hardware Version'),
        '_FDMI_NODE.brocade-fdmi/hba/manufacturer': dict(v=False, c=13, d='FDMI Manufacturer'),
        '_FDMI_NODE.brocade-fdmi/hba/max-ct-payload': dict(v=True, c=8, d='FDMI Max Payload'),
        '_FDMI_NODE.brocade-fdmi/hba/model': dict(v=False, c=12, d='FDMI Model'),
        '_FDMI_NODE.brocade-fdmi/hba/model-description': dict(v=False, c=30, d='FDMI Model Description'),
        '_FDMI_NODE.brocade-fdmi/hba/node-name': dict(v=False, c=22, d='FDMI Node Name'),
        '_FDMI_NODE.brocade-fdmi/hba/node-symbolic-name': dict(v=False, c=35, d='FDMI Node Symbolic Name'),
        '_FDMI_NODE.brocade-fdmi/hba/number-of-ports': dict(v=True, c=5, d='FDMI Number Of Ports'),
        '_FDMI_NODE.brocade-fdmi/hba/option-rom-version': dict(v=False, c=12, d='FDMI ROM Version'),
        '_FDMI_NODE.brocade-fdmi/hba/os-name-and-version': dict(v=False, c=30, d='FDMI OS Version'),
        '_FDMI_NODE.brocade-fdmi/hba/serial-number': dict(v=False, c=16, d='FDMI Serial Number'),
        '_FDMI_NODE.brocade-fdmi/hba/vendor-id': dict(v=False, c=12, d='FDMI Vendor ID'),

        # FDMI Port
        '_FDMI_PORT.brocade-fdmi/port/active-fc4-type': dict(v=False, c=13, d='FDMI Active FC4 Type'),
        '_FDMI_PORT.brocade-fdmi/port/current-port-speed': dict(v=False, c=12, d='FDMI Current Port Speed'),
        '_FDMI_PORT.brocade-fdmi/port/domain-id': dict(v=True, c=5, d='FDMI Port Domain ID'),
        '_FDMI_PORT.brocade-fdmi/port/fabric-name': dict(v=False, c=22, d='FDMI Fabric Name'),
        '_FDMI_PORT.brocade-fdmi/port/hba-id': dict(v=False, c=22, d='FDMI HBA ID'),
        '_FDMI_PORT.brocade-fdmi/port/host-name': dict(v=False, c=22, d='FDMI Host Name'),
        '_FDMI_PORT.brocade-fdmi/port/maximum-frame-size': dict(v=True, c=6, d='FDMI Maximum Frame Size'),
        '_FDMI_PORT.brocade-fdmi/port/node-name': dict(v=False, c=22, d='FDMI Node Name'),
        '_FDMI_PORT.brocade-fdmi/port/number-of-discovered-ports': dict(v=True, c=5, d='FDMI Discovered Ports'),
        '_FDMI_PORT.brocade-fdmi/port/os-device-name': dict(v=False, c=13, d='FDMI OS Device Name'),
        '_FDMI_PORT.brocade-fdmi/port/port-id': dict(v=False, c=9, d='FDMI Port ID'),
        '_FDMI_PORT.brocade-fdmi/port/port-name': dict(v=False, c=22, d='FDMI Port Name'),
        '_FDMI_PORT.brocade-fdmi/port/port-state': dict(v=False, c=11, d='FDMI Port State'),
        '_FDMI_PORT.brocade-fdmi/port/port-symbolic-name': dict(v=False, c=35, d='FDMI Port Symbolic Name'),
        '_FDMI_PORT.brocade-fdmi/port/port-type': dict(v=False, c=8, d='FDMI Port Type'),
        '_FDMI_PORT.brocade-fdmi/port/supported-class-of-service': dict(v=False, c=10,
                                                                        d='FDMI Supported Class Of Service'),
        '_FDMI_PORT.brocade-fdmi/port/supported-fc4-type': dict(v=False, c=29, d='FDMI Supported FC4 Type'),
        '_FDMI_PORT.brocade-fdmi/port/supported-speed': dict(v=False, c=22, d='FDMI Supported Speed'),
    }

    login_tbl = (
        # Namne Server
        '_LOGIN_COMMENTS',
        '_LOGIN_WWN',
        '_ALIAS',
        '_FABRIC_NAME',
        # '_FABRIC_NAME_AND_WWN',
        # '_FABRIC_WWN',
        '_SWITCH_NAME',
        # '_SWITCH_NAME_AND_WWN',
        # '_SWITCH_WWN',
        '_PORT_NUMBER',
        'brocade-name-server/fibrechannel-name-server/port-id',
        '_ZONES_DEF',
        '_ZONES_EFF',
        'brocade-name-server/fibrechannel-name-server/class-of-service',
        # 'fabric-port-name',  # This is the WWN of the switch port where this logged in.
        'brocade-name-server/fibrechannel-name-server/fc4-features',
        'brocade-name-server/fibrechannel-name-server/fc4-type',
        # '_FDMI_PORT.brocade-fdmi/port/active-fc4-type',
        'brocade-name-server/fibrechannel-name-server/link-speed',
        'brocade-name-server/fibrechannel-name-server/name-server-device-type',
        'brocade-name-server/fibrechannel-name-server/node-name',
        'brocade-name-server/fibrechannel-name-server/node-symbolic-name',
        'brocade-name-server/fibrechannel-name-server/port-symbolic-name',
        '_FDMI_NODE.brocade-fdmi/hba/node-symbolic-name',
        '_FDMI_PORT.brocade-fdmi/port/port-symbolic-name',
        # 'brocade-name-server/fibrechannel-name-server/permanent-port-name',
        # 'brocade-name-server/fibrechannel-name-server/port-index',
        'brocade-name-server/fibrechannel-name-server/port-properties',
        'brocade-name-server/fibrechannel-name-server/port-type',
        'brocade-name-server/fibrechannel-name-server/state-change-registration',

        # Flags
        'brocade-name-server/fibrechannel-name-server/share-area',
        'brocade-name-server/fibrechannel-name-server/frame-redirection',
        'brocade-name-server/fibrechannel-name-server/partial',
        'brocade-name-server/fibrechannel-name-server/lsan',
        'brocade-name-server/fibrechannel-name-server/cascaded-ag',
        'brocade-name-server/fibrechannel-name-server/connected-through-ag',
        'brocade-name-server/fibrechannel-name-server/real-device-behind-ag',
        'brocade-name-server/fibrechannel-name-server/fcoe-device',
        'brocade-name-server/fibrechannel-name-server/slow-drain-device-quarantine',

        # Remaining FDMI Node
        '_FDMI_NODE.brocade-fdmi/hba/boot-bios-version',
        '_FDMI_NODE.brocade-fdmi/hba/domain-id',
        '_FDMI_NODE.brocade-fdmi/hba/driver-version',
        '_FDMI_NODE.brocade-fdmi/hba/fabric-name',
        '_FDMI_NODE.brocade-fdmi/hba/firmware-version',
        '_FDMI_NODE.brocade-fdmi/hba/hardware-version',
        '_FDMI_NODE.brocade-fdmi/hba/manufacturer',
        '_FDMI_NODE.brocade-fdmi/hba/max-ct-payload',
        '_FDMI_NODE.brocade-fdmi/hba/model',
        '_FDMI_NODE.brocade-fdmi/hba/model-description',
        '_FDMI_NODE.brocade-fdmi/hba/node-name',
        '_FDMI_NODE.brocade-fdmi/hba/number-of-ports',
        '_FDMI_NODE.brocade-fdmi/hba/option-rom-version',
        '_FDMI_NODE.brocade-fdmi/hba/os-name-and-version',
        '_FDMI_NODE.brocade-fdmi/hba/serial-number',
        '_FDMI_NODE.brocade-fdmi/hba/vendor-id',

        # Remaining FDMI Port
        '_FDMI_PORT.brocade-fdmi/port/active-fc4-type',
        '_FDMI_PORT.brocade-fdmi/port/current-port-speed',
        '_FDMI_PORT.brocade-fdmi/port/domain-id',
        '_FDMI_PORT.brocade-fdmi/port/fabric-name',
        '_FDMI_PORT.brocade-fdmi/port/hba-id',
        '_FDMI_PORT.brocade-fdmi/port/host-name',
        '_FDMI_PORT.brocade-fdmi/port/maximum-frame-size',
        '_FDMI_PORT.brocade-fdmi/port/node-name',
        '_FDMI_PORT.brocade-fdmi/port/number-of-discovered-ports',
        '_FDMI_PORT.brocade-fdmi/port/os-device-name',
        '_FDMI_PORT.brocade-fdmi/port/port-id',
        '_FDMI_PORT.brocade-fdmi/port/port-name',
        '_FDMI_PORT.brocade-fdmi/port/port-state',
        '_FDMI_PORT.brocade-fdmi/port/port-type',
        '_FDMI_PORT.brocade-fdmi/port/supported-class-of-service',
        '_FDMI_PORT.brocade-fdmi/port/supported-fc4-type',
        '_FDMI_PORT.brocade-fdmi/port/supported-speed',
    )


class BestPractice:
    # How to display best practices
    #   _TYPE               Type of alert
    #   _SEV                Severity level
    #   _AREA_1             Top level descriptor
    #   _AREA_2             Next level descriptor
    #   _LINK               Link to object
    #   _DESCRIPTION        Alert message

    # The values are dictionaries whose keys are as follows:
    # 'v'   If True, displays the column header vertically. Default is False
    # 'c'   The column width. Default is whatever the default Excel column width is
    # 'd'   Descriptor (column header).
    # 'dc'  If True, key is for display control only. No content is associated with the record
    bp_display_tbl = dict(
        # Custom
        _TYPE=dict(c=14, d='Type'),
        _SEV=dict(c=6, d='Sev'),
        _AREA_1=dict(c=42, d='Area 1'),
        _AREA_2=dict(c=8, d='Area 2'),
        _LINK=dict(c=5, d='Link'),
        _DESCRIPTION=dict(c=60, d='Description'),
    )

    bp_tbl = (
        '_TYPE',
        '_SEV',
        '_AREA_1',
        '_AREA_2',
        '_LINK',
        '_DESCRIPTION',
    )
