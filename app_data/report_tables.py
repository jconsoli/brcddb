# Copyright 2019, 2020, 2021, 2022 Jack Consoli.  All rights reserved.
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
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '14 Oct 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.3'


class Chassis:
    # Key - Custom key of key from any of the chassis related API responses. Value is the the column header. This table
    # also controls what is populated on the sheet page. Comment/Uncomment entries as needed.
    chassis_display_tbl = {
        # From the API
        'brocade-chassis/chassis/chassis-user-friendly-name': 'Chassis Name',
        'brocade-chassis/chassis/chassis-wwn': 'Chassis WWN',
        'brocade-chassis/chassis/license-id': 'License ID',
        'brocade-chassis/chassis/manufacturer': 'Manufacturer',
        'brocade-chassis/chassis/registered-organization-name': 'Registered Organization Name',
        'brocade-chassis/chassis/organization-registration-date': 'Organization Registration Date',
        'brocade-chassis/chassis/part-number': 'Part Number',
        'brocade-chassis/chassis/serial-number': 'Serial Number',
        'brocade-chassis/chassis/max-blades-supported': 'Maximum Number of Blades Supported',
        'brocade-chassis/chassis/vendor-part-number': 'Vendor Part Number',
        'brocade-chassis/chassis/vendor-serial-number': 'Vendor Serial Number',
        'brocade-chassis/chassis/vendor-revision-number': 'Vendor Revision Number',
        'brocade-chassis/chassis/product-name': 'Product Name',
        'brocade-chassis/chassis/date': 'Date',
        'brocade-chassis/chassis/chassis-enabled': 'Chassis Enabled',
        'brocade-chassis/chassis/message-of-the-day': 'Daily Message',
        'brocade-chassis/chassis/shell-timeout': 'Shell Timeout',
        'brocade-chassis/chassis/session-timeout': 'Session Timeout',
        'brocade-chassis/chassis/usb-device-enabled': 'USB Enabled',
        'brocade-chassis/chassis/usb-available-space': 'USB Available Space',
        'brocade-chassis/chassis/tcp-timeout-level': 'TCP Timeout Level',
        'brocade-chassis/chassis/backplane-revision': 'Backplane Revision',
        'brocade-chassis/chassis/vf-enabled': 'Virtual Fabrics Enabled',
        'brocade-chassis/chassis/vf-supported': 'Virtual Fabrics Supported',
        'brocade-chassis/ha-status/ha-enabled': 'HA Enabled',
        'brocade-chassis/ha-status/heartbeat-up': 'Heart Beat Up',
        'brocade-chassis/ha-status/ha-synchronized': 'HA Synchronized',
        'brocade-chassis/ha-status/active-cp': 'Active CP',
        'brocade-chassis/ha-status/active-slot': 'Active Slot',
        'brocade-chassis/ha-status/recovery-type': 'Recovery Type',
        'brocade-chassis/ha-status/standby-cp': 'Standby CP',
        'brocade-chassis/ha-status/standby-health': 'Standby Health',
        'brocade-chassis/ha-status/standby-slot': 'Standby Slot',
        'brocade-chassis/management-interface-configuration/rest-enabled': 'Rest Enabled',
        'brocade-chassis/management-interface-configuration/https-protocol-enabled': 'HTTPS Protocol Enabled',
        'brocade-chassis/management-interface-configuration/effective-protocol': 'Effective Protocol',
        'brocade-chassis/management-interface-configuration/max-rest-sessions': 'Max Rest Sessions',
        'brocade-chassis/management-interface-configuration/https-keep-alive-enabled': 'HTTPS Keep Alive Enabled',
        'brocade-chassis/management-interface-configuration/https-keep-alive-timeout': 'HTTPS Keep Alive Timeout',
        'brocade-fru/blade': {
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
        'brocade-fru/fan': {
            'part-number': 'Part Number',
            'serial-number': 'S/N',
            'airflow-direction': 'Airflow',
            'operational-state': 'State',
            'speed': 'Speed',
            'unit-number': 'Unit Number',
            'time-alive': 'Time Alive',
            'time-awake': 'Time Awake',
        },
        'brocade-fru/power-supply': {
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

    # Key - Custom key of key from any of the switch related API responses. Value is the the column header. This table
    # also controls what is populated on the sheet page. Comment/Uncomment entries as needed.
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
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/base-switch-enabled': 'Base Switch',
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/default-switch-status': 'Default Switch',
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/ficon-mode-enabled': 'FICON Switch',
        # Configuration
        'brocade-fibrechannel-switch/fibrechannel-switch/banner': 'Banner',
        'brocade-fabric/fabric-switch/chassis-user-friendly-name': 'Chassis',
        'brocade-fabric/fabric-switch/chassis-wwn': 'Chassis WWN',
        'brocade-fabric/fabric-switch/domain-id': 'Domain ID',
        'brocade-fabric/fabric-switch/domain-name': 'Domain Name',
        # 'fabric': brcdapi_util.get_key_val, This is a dict, but I don't know what the members are yet
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id': 'Fabric ID (FID)',
        'brocade-fibrechannel-switch/fibrechannel-switch/fabric-user-friendly-name': 'Fabric Name',
        'brocade-fabric/fabric-switch/fcid-hex': 'FC ID',
        'brocade-fabric/fabric-switch/fcip-address': 'FCIP Address',
        'brocade-fabric/fabric-switch/firmware-version': 'Firmware Version',
        'brocade-fabric/fabric-switch/ip-address': 'Management IPv4 Address',
        'brocade-fibrechannel-switch/fibrechannel-switch/subnet-mask': 'Management Subnet Mask',
        'brocade-fibrechannel-switch/fibrechannel-switch/ip-static-gateway-list/ip-static-gateway': 'IP Static Gateway',
        'brocade-fabric/fabric-switch/ipv6-address': 'Management IPv6 Address',
        'brocade-fabric/fabric-switch/path-count': 'Path Count',
        'brocade-fibrechannel-switch/fibrechannel-switch/model': 'Switch Model',
        # 'brocade-fibrechannel-switch/fibrechannel-switch/name': 'Switch WWN',
        'brocade-fibrechannel-switch/fibrechannel-switch/operational-status': 'Status',
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
        'brocade-fibrechannel-configuration/port-configuration/dynamic-portname-format': 'Dynamic Port Name Format',
        'brocade-fibrechannel-configuration/port-configuration/portname-mode': 'Port Name Mode',
        'brocade-fibrechannel-configuration/switch-configuration/area-mode': 'Address (Area) Mode',
        'brocade-fibrechannel-configuration/switch-configuration/edge-hold-time': 'Edge-Hold-Time (msec)',
        'brocade-fabric/fabric-switch/switch-user-friendly-name': 'Switch Name',
        'brocade-fibrechannel-switch/fibrechannel-switch/up-time': 'Up Time (days)',
        'brocade-fibrechannel-switch/fibrechannel-switch/user-friendly-name': 'Switch Name',
        'brocade-fibrechannel-switch/fibrechannel-switch/vf-id': 'Virtual Fabric ID (FID)',
        'brocade-fibrechannel-switch/fibrechannel-switch/ag-mode': 'Access Gateway Mode',
        'brocade-fibrechannel-configuration/f-port-login-settings/max-logins': 'Maximum switch logins',
        'brocade-fibrechannel-configuration/f-port-login-settings/max-flogi-rate-per-switch': 'Maximum FLOGI rate',
        'brocade-fibrechannel-configuration/f-port-login-settings/stage-interval': 'F-Port enable rate (msec)',
        'brocade-fibrechannel-configuration/f-port-login-settings/enforce-login': 'Duplicate WWN handling',
        'brocade-fibrechannel-configuration/f-port-login-settings/free-fdisc': 'Maximum FDISC logins before staging',
        'brocade-fibrechannel-configuration/f-port-login-settings/max-flogi-rate-per-port':
            'Maximum FLOGI rate (logins/sec)',
        # Flags
        'brocade-fibrechannel-switch/fibrechannel-switch/is-enabled-state': 'Switch Enabled',
        'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/logical-isl-enabled':
            'Logical ISL (XISL) Enabled',
        'brocade-fibrechannel-switch/fibrechannel-switch/principal': 'Fabric Principal',
        'brocade-fibrechannel-configuration/switch-configuration/wwn-port-id-mode': 'Persistent WWN PID Mode',
        'brocade-fibrechannel-configuration/fabric/insistent-domain-id-enabled': 'Insistent Domain ID',
        # RNID
        'brocade-ficon/cup/fmsmode-enabled': 'FICON CUP: Enabled',
        'brocade-ficon/cup/programmed-offline-state-control': 'FICON CUP: Programmed Offline State Control',
        'brocade-ficon/cup/user-alert-mode': 'FICON CUP: User Alert Mode',
        'brocade-ficon/cup/active-equal-saved-mode': 'FICON CUP: Active Equal Saved',
        'brocade-ficon/cup/director-clock-alert-mode': 'FICON CUP: Clock Alert Mode',
        'brocade-ficon/cup/mihpto': 'FICON CUP: MIHPTO',
        'brocade-ficon/cup/unsolicited-alert-mode-fru-enabled': 'FICON CUP: Unsolicited FRU Alert',
        'brocade-ficon/cup/unsolicited-alert-mode-hsc-enabled': 'FICON CUP: Unsolicited HSC Alert',
        'brocade-ficon/cup/unsolicited-alert-mode-invalid-attach-enabled':
            'FICON CUP: Unsolicited Invalid Attach Alert',
        'brocade-ficon/switch-rnid/flags': 'RNID: Flags',
        'brocade-ficon/switch-rnid/node-parameters': 'Node Parameters',
        'brocade-ficon/switch-rnid/type-number': 'RNID: Type',
        'brocade-ficon/switch-rnid/model-number': 'RNID: Model',
        'brocade-ficon/switch-rnid/manufacturer': 'RNID: Manufacturer',
        'brocade-ficon/switch-rnid/plant': 'RNID: Plant',
        'brocade-ficon/switch-rnid/sequence-number': 'RNID: S/N',
        'brocade-ficon/switch-rnid/tag': 'RNID: Tag',
        # MAPS
        'brocade-maps/system-resources/memory-usage': 'MAPS System Memory Usage'
    }


class Zone:
    zone_display_tbl = {
        'brocade-zone/effective-configuration/cfg-name': 'Effective Configuration',
        'brocade-zone/effective-configuration/db-avail': 'DB Avail Memory',
        'brocade-zone/effective-configuration/checksum': 'Checksum',
        'brocade-zone/effective-configuration/db-committed': 'Fabric Committed',
        'brocade-zone/effective-configuration/cfg-action': 'Configuration Action',
        'brocade-zone/effective-configuration/db-max': 'DB Maximum Size',
        'brocade-zone/effective-configuration/default-zone-access': 'Default Zone',
        'brocade-zone/effective-configuration/db-transaction': 'In Progress Transaction',
        'brocade-zone/effective-configuration/transaction-token': 'Transaction Token',
        'brocade-zone/effective-configuration/db-chassis-wide-committed': 'Zone DB Committed',
        'brocade-zone/fabric-lock/lock-principal-domain-id': 'Lock Principal Ddomain ID',
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
    In addition to the keys specified in the Rest API Guide, there are the following speicial keys:
    The keys are either one of the keys defined in 'brocade-interface/fibrechannel' + any of the leafs or one of the
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
    | c     | int   | The column width. Default is whatever the default Excel column width is which is usally 8     |
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
        'fibrechannel/e-port-credit': dict(v=True, c=8, d='E-Port Credit'),
        'fibrechannel/f-port-buffers': dict(v=True, c=8, d='F-Port Buffers'),
        'fibrechannel/fcid': dict(c=10, d='FC Address'),  # Deprecated
        'fibrechannel/fcid-hex': dict(c=10, d='FC Address'),
        'fibrechannel/long-distance': dict(v=True, c=8, d='Long Distance Mode'),
        'fibrechannel/los-tov-mode-enabled': dict(v=True, c=12, d='LOS_TOV Mode'),
        'fibrechannel/neighbor': dict(v=True, c=12, d='Neighbor port WWN'),
        'fibrechannel/neighbor-node-wwn': dict(v=True, c=12, d='Neighbor node WWN'),
        'fibrechannel/npiv-pp-limit': dict(v=True, c=6, d='NPIV Limit'),
        'fibrechannel/octet-speed-combo': dict(c=20, d='Speed Combo'),
        'fibrechannel/operational-status': dict(c=10, d='Status'),
        'fibrechannel/physical-state': dict(c=11, d='State'),
        'fibrechannel/port-type': dict(c=7, d='Port Type'),
        'fibrechannel/rate-limit-enabled': dict(v=True, c=8, d='Rate Limit'),
        'fibrechannel/speed': dict(v=True, c=6, d='Login Speed Gbps'),
        'fibrechannel/max-speed': dict(v=True, c=6, d='Max Speed Gbps'),
        'fibrechannel/user-friendly-name': dict(c=28, d='Port Name'),
        'fibrechannel/wwn': dict(c=22, d='Switch Port WWN'),
        'fibrechannel/average-receive-frame-size': dict(v=True, c=8, d='Average Rx Frame Size'),
        'fibrechannel/average-transmit-frame-size': dict(v=True, c=8, d='Average Tx Frame Size'),
        'fibrechannel/average-transmit-buffer-usage': dict(v=True, c=8, d='Avg Tx buffer usage'),
        'fibrechannel/average-receive-buffer-usage': dict(v=True, c=8, d='Avg Rx buffer usage'),
        'fibrechannel/port-type-string': dict(c=15, d='Port Type'),
        'fibrechannel/reserved-buffers': dict(v=True, c=8, d='Reserved Buffers'),
        'fibrechannel/authentication-protocol': dict(c=15, d='Authentication Protocol'),
        'fibrechannel/chip-buffers-available': dict(v=True, c=8, d='Chip Buffers Available'),
        'fibrechannel/chip-instance': dict(v=True, c=8, d='Chip Instance'),
        'fibrechannel/clean-address-enabled': dict(v=True, c=8, d='Clean Address Enabled'),
        'fibrechannel/encryption-enabled': dict(v=True, c=8, d='Encryption Enabled'),
        'fibrechannel/index': dict(v=True, c=8, d='Port Index'),
        'fibrechannel/le-domain': dict(v=True, c=8, d='LE Domain'),
        'fibrechannel/measured-link-distance': dict(v=True, c=8, d='Measured Link Distance'),
        'fibrechannel/pod-license-state': dict(c=15, d='POD License State'),
        'fibrechannel/port-health': dict(v=True, c=8, d='Port Health'),
        'fibrechannel/port-peer-beacon-enabled': dict(v=True, c=8, d='Port Peer Beacon Enabled'),
        # Flags
        'fibrechannel/auto-negotiate': dict(v=True, m=True, c=5, d='Auto-Negotiate'),
        'fibrechannel/compression-active': dict(v=True, m=True, c=5, d='Compression Active'),
        'fibrechannel/compression-configured': dict(v=True, m=True, c=5, d='Compression Enabled'),
        'fibrechannel/credit-recovery-active': dict(v=True, m=True, c=5, d='Credit Recovery Active'),
        'fibrechannel/credit-recovery-enabled': dict(v=True, m=True, c=5, d='Credit Recovery Enabled'),
        'fibrechannel/csctl-mode-enabled': dict(v=True, m=True, c=5, d='CSCTL Enabled'),
        'fibrechannel/d-port-enable': dict(v=True, m=True, c=5, d='D-Port Enabled'),
        'fibrechannel/e-port-disable': dict(v=True, m=True, c=5, d='E-Port Disabled'),
        # 'fibrechannel/enabled-state': dict(v=True, m=True, c=5, d='Enabled'),  # Deprecated in FOS 8.2.1b
        'fibrechannel/encryption-active': dict(v=True, m=True, c=5, d='Encryption Active'),
        'fibrechannel/ex-port-enabled': dict(v=True, m=True, c=5, d='XISL Enabled'),
        'fibrechannel/fault-delay-enabled': dict(v=True, m=True, c=5, d='Fault Delay Enabled'),
        'fibrechannel/fec-enabled': dict(v=True, m=True, c=5, d='FEC Enabled'),
        'fibrechannel/fec-active': dict(v=True, m=True, c=5, d='FEC Active'),
        'fibrechannel/g-port-locked': dict(v=True, m=True, c=5, d='G-Port Locked'),
        'fibrechannel/is-enabled-state': dict(v=True, m=True, c=5, d='Enabled'),
        'fibrechannel/isl-ready-mode-enabled': dict(v=True, m=True, c=5, d='ISL Ready Mode Enabled'),
        'fibrechannel/mirror-port-enabled': dict(v=True, m=True, c=5, d='Mirror Port Enabled'),
        'fibrechannel/n-port-enabled': dict(v=True, m=True, c=5, d='N-Port Enabled'),
        'fibrechannel/non-dfe-enabled': dict(v=True, m=True, c=5, d='Non-DFE Enabled'),
        'fibrechannel/npiv-enabled': dict(v=True, m=True, c=5, d='NPIV Enabled'),
        'fibrechannel/npiv-flogi-logout-enabled': dict(v=True, m=True, c=5, d='NPIV FLOGI Logout Enabled'),
        'fibrechannel/path-count': dict(v=True, m=True, c=5, d='Path Count'),
        'fibrechannel/persistent-disable': dict(v=True, m=True, c=5, d='Persitent Disable'),
        'fibrechannel/port-autodisable-enabled': dict(v=True, m=True, c=5, d='Autodisable Enabled'),
        'fibrechannel/qos-enabled': dict(v=True, m=True, c=5, d='QoS Enabled'),
        'fibrechannel/rscn-suppression-enabled': dict(v=True, m=True, c=5, d='RSCN Suppression Enabled'),
        'fibrechannel/target-driven-zoning-enable': dict(v=True, m=True, c=5, d='Target Driven Zoning Enabled'),
        'fibrechannel/trunk-port-enabled': dict(v=True, m=True, c=5, d='Trunk Port Enabled'),
        'fibrechannel/vc-link-init': dict(v=True, m=True, c=5, d='VC Link Init'),
        'fibrechannel/via-tts-fec-enabled': dict(v=True, m=True, c=5, d='FEC via TTS Enabled'),
        # Statistics
        'fibrechannel-statistics/address-errors': dict(v=True, c=8, d='Address Errors'),
        'fibrechannel-statistics/bad-eofs-received': dict(v=True, c=8, d='Bad EOF'),
        'fibrechannel-statistics/bb-credit-zero': dict(v=True, c=10, d='Zero BB Credit'),
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit': dict(v=True, c=8, d='Remote BB Credit'),
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit':
            dict(v=True, c=8, d='Remote Peer BB Credit'),
        'fibrechannel-statistics/class-1-frames': dict(v=True, c=8, d='Class 1 Frames'),
        'fibrechannel-statistics/class-2-frames': dict(v=True, c=8, d='Class 2 Frames'),
        'fibrechannel-statistics/class-3-frames': dict(c=14, d='Class 3 Frames'),
        'fibrechannel-statistics/class-3-discards': dict(v=True, c=8, d='C3 Frame Discards'),
        'fibrechannel-statistics/class3-in-discards': dict(v=True, c=8, d='Rx C3 Frames discarded'),
        'fibrechannel-statistics/class3-out-discards': dict(v=True, c=8, d='Tx C3 Frame Discards'),
        'fibrechannel-statistics/crc-errors': dict(v=True, c=8, d='CRC Errors'),
        'fibrechannel-statistics/delimiter-errors': dict(v=True, c=8, d='Delimiter Errors'),
        'fibrechannel-statistics/encoding-disparity-errors': dict(v=True, c=8, d='Encoding Disparity Errors'),
        'fibrechannel-statistics/encoding-errors-outside-frame': dict(v=True, c=8,
                                                                      d='Encoding Errors Outside Frame'),
        'fibrechannel-statistics/f-busy-frames': dict(v=True, c=8, d='Frame Busy'),
        'fibrechannel-statistics/f-rjt-frames': dict(v=True, c=8, d='Frame Rejects'),
        'fibrechannel-statistics/frames-too-long': dict(v=True, c=8, d='Frames Too Long'),
        'fibrechannel-statistics/in-crc-errors': dict(v=True, c=8, d='Incoming CRC Errors'),
        'fibrechannel-statistics/remote-crc-errors': dict(v=True, c=8, d='Remote CRC Errors'),
        'fibrechannel-statistics/in-frame-rate': dict(v=True, c=8, d='Rx Frame Rate'),
        'fibrechannel-statistics/in-frames': dict(c=15, d='Rx Frames'),
        'fibrechannel-statistics/in-lcs': dict(v=True, c=8, d='In LCS'),
        'fibrechannel-statistics/in-link-resets': dict(v=True, c=8, d='Link Resets'),
        'fibrechannel-statistics/in-max-frame-rate': dict(v=True, c=8, d='Rx Max Frame Rate'),
        'fibrechannel-statistics/in-multicast-pkts': dict(v=True, c=8, d='Rx Multi-cast Packets'),
        'fibrechannel-statistics/in-octets': dict(c=14, d='Rx Octets'),
        'fibrechannel-statistics/in-offline-sequences': dict(v=True, c=8, d='Rx Offline Sequence'),
        'fibrechannel-statistics/in-peak-rate': dict(v=True, c=8, d='Rx Peak Rate'),
        'fibrechannel-statistics/in-rate': dict(v=True, c=8, d='Rx Rate'),
        'fibrechannel-statistics/input-buffer-full': dict(v=True, c=8, d='Input Buffer Full'),
        'fibrechannel-statistics/invalid-ordered-sets': dict(v=True, c=8, d='Invalid Ordered Sets'),
        'fibrechannel-statistics/invalid-transmission-words': dict(v=True, c=8,
                                                                   d='Invalid Transmission Words (ITW)'),
        'fibrechannel-statistics/remote-invalid-transmission-words': \
            dict(v=True, c=8, d='Remote Invalid Transmission Words (ITW)'),
        'fibrechannel-statistics/link-failures': dict(v=True, c=8, d='Link Failures'),
        'fibrechannel-statistics/remote-link-failures': dict(v=True, c=8, d='Remote Link Failures'),
        'fibrechannel-statistics/loss-of-signal': dict(v=True, c=8, d='Loss Of Signal'),
        'fibrechannel-statistics/remote-loss-of-signal': dict(v=True, c=8, d='Remote Loss Of Signal'),
        'fibrechannel-statistics/loss-of-sync': dict(v=True, c=8, d='Loss Of Sync'),
        'fibrechannel-statistics/remote-loss-of-sync': dict(v=True, c=8, d='Remote Loss Of Sync'),
        'fibrechannel-statistics/multicast-timeouts': dict(v=True, c=8, d='Multi-cast Timeouts'),
        'fibrechannel-statistics/out-frame-rate': dict(v=True, c=8, d='Tx Frame Rate'),
        'fibrechannel-statistics/out-frames': dict(c=14, d='Tx Frames'),
        'fibrechannel-statistics/out-link-resets': dict(v=True, c=8, d='Tx Link Resets'),
        'fibrechannel-statistics/out-max-frame-rate': dict(v=True, c=8, d='Tx Max Frame Rate'),
        'fibrechannel-statistics/out-multicast-pkts': dict(v=True, c=8, d='Tx Multicast Pkts'),
        'fibrechannel-statistics/out-octets': dict(c=14, d='Tx Octets'),
        'fibrechannel-statistics/out-offline-sequences': dict(v=True, c=8, d='Tx Offline Sequences'),
        'fibrechannel-statistics/out-peak-rate': dict(v=True, c=8, d='Tx Peak Rate'),
        'fibrechannel-statistics/out-rate': dict(v=True, c=8, d='Tx Rate'),
        'fibrechannel-statistics/p-busy-frames': dict(v=True, c=8, d='P-Busy Frames'),
        'fibrechannel-statistics/p-rjt-frames': dict(v=True, c=8, d='P-Reject Frames'),
        'fibrechannel-statistics/pcs-block-errors': dict(v=True, c=8, d='PCS Block Errors'),
        'fibrechannel-statistics/primitive-sequence-protocol-error': dict(v=True, c=8,
                                                                          d='Primitive Sequence Error'),
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error':
            dict(v=True, c=8, d='Remote Primitive Sequence Error'),
        'fibrechannel-statistics/sampling-interval': dict(v=True, c=8, d='Sampling Interval (sec)'),
        'fibrechannel-statistics/time-generated': dict(c=24, d='Time Generated'),
        'fibrechannel-statistics/too-many-rdys': dict(v=True, c=8, d='To Many RDYs'),
        'fibrechannel-statistics/truncated-frames': dict(v=True, c=8, d='Truncated Frames'),
        'fibrechannel-statistics/remote-fec-uncorrected': dict(v=True, c=8, d='Truncated Frames'),
        'fibrechannel-statistics/frames-processing-required': dict(v=True, c=8, d='Frames Processing Required'),
        'fibrechannel-statistics/frames-timed-out': dict(v=True, c=8, d='Frames Timed Out'),
        'fibrechannel-statistics/frames-transmitter-unavailable-errors': dict(v=True, c=8,
                                                                              d='Tx Unavailable Errors'),
        # Media (media-rdp)
        'media-rdp/connector': dict(v=True, c=6, d='Connector Type'),
        'media-rdp/wavelength': dict(v=True, c=8, d='Wavelength'),
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
        'media-rdp/part-number': dict(c=14, d='Part Number'),
        'media-rdp/remote-optical-product-data/part-number': dict(c=17, d='Remote Part Number'),
        'media-rdp/power-on-time': dict(v=True, c=8, d='Power on time (days)'),
        'media-rdp/rx-power': dict(v=True, c=8, d='Rx Power (uW)'),
        'media-rdp/remote-media-rx-power': dict(v=True, c=8, d='Remote Rx Power (uW)'),
        'media-rdp/tx-power': dict(v=True, c=8, d='Tx Power (uW)'),
        'media-rdp/remote-media-tx-power': dict(v=True, c=8, d='Remote Tx Power (uW)'),
        'media-rdp/serial-number': dict(c=18, d='Serial Number'),
        'media-rdp/remote-optical-product-data/serial-number': dict(c=18, d='Remote Serial Number'),
        'media-rdp/temperature': dict(v=True, c=6, d='Temperature (C)'),
        'media-rdp/remote-media-temperature': dict(v=True, c=6, d='Remote Temperature (C)'),
        'media-rdp/vendor-name': dict(c=15, d='Vendor'),
        'media-rdp/remote-optical-product-data/vendor-name': dict(c=10, d='Remote Vendor'),
        'media-rdp/vendor-oui': dict(c=8, d='Vendor OUI'),
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
        'fibrechannel/user-friendly-name',
        'fibrechannel/fcid-hex',
        'fibrechannel/port-type',
        'media-rdp/wavelength',
        'fibrechannel/is-enabled-state',
        'fibrechannel/operational-status',
        'fibrechannel/physical-state',
        '_BEST_DESC',
        '_MAPS_GROUP',
        'fibrechannel/e-port-credit',
        'fibrechannel/f-port-buffers',
        'fibrechannel/long-distance',
        # 'fibrechannel/name',        # Not copied to the object because it is the object key
        # 'fibrechannel/neighbor',    # Handled separately
        'fibrechannel/npiv-pp-limit',
        'fibrechannel/octet-speed-combo',
        'fibrechannel/rate-limit-enabled',
        'fibrechannel/speed',
        # 'fibrechannel/wwn',
        # Flags
        # 'fibrechannel/path-count',  # Has conflicting meaning. RFE #16 to fix.
        'fibrechannel/persistent-disable',
        'fibrechannel/auto-negotiate',
        'fibrechannel/compression-active',
        'fibrechannel/compression-configured',
        'fibrechannel/encryption-active',
        'fibrechannel/target-driven-zoning-enable',
        'fibrechannel/g-port-locked',
        'fibrechannel/e-port-disable',
        'fibrechannel/n-port-enabled',
        'fibrechannel/d-port-enable',
        'fibrechannel/ex-port-enabled',
        'fibrechannel/fec-enabled',
        'fibrechannel/mirror-port-enabled',
        'fibrechannel/credit-recovery-enabled',
        'fibrechannel/credit-recovery-active',
        'fibrechannel/fec-active',
        'fibrechannel/csctl-mode-enabled',
        'fibrechannel/fault-delay-enabled',
        'fibrechannel/trunk-port-enabled',
        'fibrechannel/vc-link-init',
        'fibrechannel/isl-ready-mode-enabled',
        'fibrechannel/rscn-suppression-enabled',
        'fibrechannel/los-tov-mode-enabled',
        'fibrechannel/npiv-enabled',
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
        'fibrechannel/fcid-hex',
        'fibrechannel/port-type',
        '_BEST_DESC',
        'fibrechannel/is-enabled-state',
        'fibrechannel/operational-status',
        'fibrechannel-statistics/time-generated',
        'fibrechannel-statistics/sampling-interval',
        'fibrechannel-statistics/address-errors',
        'fibrechannel-statistics/bad-eofs-received',
        'fibrechannel-statistics/bb-credit-zero',
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit',
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit',
        'fibrechannel-statistics/class-1-frames',
        'fibrechannel-statistics/class-2-frames',
        'fibrechannel-statistics/class-3-discards',
        'fibrechannel-statistics/class-3-frames',
        'fibrechannel-statistics/class3-in-discards',
        'fibrechannel-statistics/class3-out-discards',
        'fibrechannel-statistics/crc-errors',
        'fibrechannel-statistics/remote-crc-errors',
        'fibrechannel-statistics/remote-fec-uncorrected',
        'fibrechannel-statistics/delimiter-errors',
        'fibrechannel-statistics/encoding-disparity-errors',
        'fibrechannel-statistics/encoding-errors-outside-frame',
        'fibrechannel-statistics/f-busy-frames',
        'fibrechannel-statistics/f-rjt-frames',
        'fibrechannel-statistics/frames-too-long',
        'fibrechannel-statistics/in-crc-errors',
        'fibrechannel-statistics/in-frame-rate',
        'fibrechannel-statistics/in-frames',
        'fibrechannel-statistics/in-lcs',
        'fibrechannel-statistics/in-link-resets',
        'fibrechannel-statistics/in-max-frame-rate',
        'fibrechannel-statistics/in-multicast-pkts',
        'fibrechannel-statistics/in-octets',
        'fibrechannel-statistics/in-offline-sequences',
        'fibrechannel-statistics/in-peak-rate',
        'fibrechannel-statistics/in-rate',
        'fibrechannel-statistics/input-buffer-full',
        'fibrechannel-statistics/invalid-ordered-sets',
        'fibrechannel-statistics/invalid-transmission-words',
        'fibrechannel-statistics/remote-invalid-transmission-words',
        'fibrechannel-statistics/link-failures',
        'fibrechannel-statistics/remote-link-failures',
        'fibrechannel-statistics/loss-of-signal',
        'fibrechannel-statistics/remote-loss-of-signal',
        'fibrechannel-statistics/loss-of-sync',
        'fibrechannel-statistics/remote-loss-of-sync',
        'fibrechannel-statistics/multicast-timeouts',
        'fibrechannel-statistics/out-frame-rate',
        'fibrechannel-statistics/out-frames',
        'fibrechannel-statistics/out-link-resets',
        'fibrechannel-statistics/out-max-frame-rate',
        'fibrechannel-statistics/out-multicast-pkts',
        'fibrechannel-statistics/out-octets',
        'fibrechannel-statistics/out-offline-sequences',
        'fibrechannel-statistics/out-peak-rate',
        'fibrechannel-statistics/out-rate',
        'fibrechannel-statistics/p-busy-frames',
        'fibrechannel-statistics/p-rjt-frames',
        'fibrechannel-statistics/pcs-block-errors',
        'fibrechannel-statistics/primitive-sequence-protocol-error',
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error',
        # 'fibrechannel-statistics/reset-statistics', # This is write only. Here for negative testing purposes only.
        'fibrechannel-statistics/too-many-rdys',
        'fibrechannel-statistics/truncated-frames',
        'fibrechannel-statistics/frames-processing-required',
        'fibrechannel-statistics/frames-processing-required',
        'fibrechannel-statistics/frames-timed-out',
        'fibrechannel-statistics/frames-transmitter-unavailable-errors',
        'fibrechannel/average-receive-frame-size',
        'fibrechannel/average-transmit-frame-size',
    )
    # Similar to port_stats_tbl but for a sinlge port when all port objects are a point in time sample
    port_stats1_tbl = (
        'fibrechannel-statistics/time-generated',
        'fibrechannel-statistics/address-errors',
        'fibrechannel-statistics/bad-eofs-received',
        'fibrechannel-statistics/bb-credit-zero',
        'fibrechannel-statistics/remote-buffer-credit-info/bb-credit',
        'fibrechannel-statistics/remote-buffer-credit-info/peer-bb-credit',
        'fibrechannel-statistics/class-1-frames',
        'fibrechannel-statistics/class-2-frames',
        'fibrechannel-statistics/class-3-discards',
        'fibrechannel-statistics/class-3-frames',
        'fibrechannel-statistics/class3-in-discards',
        'fibrechannel-statistics/class3-out-discards',
        'fibrechannel-statistics/crc-errors',
        'fibrechannel-statistics/remote-crc-errors',
        'fibrechannel-statistics/remote-fec-uncorrected',
        'fibrechannel-statistics/delimiter-errors',
        'fibrechannel-statistics/encoding-disparity-errors',
        'fibrechannel-statistics/encoding-errors-outside-frame',
        'fibrechannel-statistics/f-busy-frames',
        'fibrechannel-statistics/f-rjt-frames',
        'fibrechannel-statistics/frames-too-long',
        'fibrechannel-statistics/in-crc-errors',
        'fibrechannel-statistics/in-frame-rate',
        'fibrechannel-statistics/in-frames',
        'fibrechannel-statistics/in-lcs',
        'fibrechannel-statistics/in-link-resets',
        'fibrechannel-statistics/in-max-frame-rate',
        'fibrechannel-statistics/in-multicast-pkts',
        'fibrechannel-statistics/in-octets',
        'fibrechannel-statistics/in-offline-sequences',
        'fibrechannel-statistics/in-peak-rate',
        'fibrechannel-statistics/in-rate',
        'fibrechannel-statistics/input-buffer-full',
        'fibrechannel-statistics/invalid-ordered-sets',
        'fibrechannel-statistics/invalid-transmission-words',
        'fibrechannel-statistics/remote-invalid-transmission-words',
        'fibrechannel-statistics/link-failures',
        'fibrechannel-statistics/remote-link-failures',
        'fibrechannel-statistics/loss-of-signal',
        'fibrechannel-statistics/remote-loss-of-signal',
        'fibrechannel-statistics/loss-of-sync',
        'fibrechannel-statistics/remote-loss-of-sync',
        'fibrechannel-statistics/multicast-timeouts',
        'fibrechannel-statistics/out-frame-rate',
        'fibrechannel-statistics/out-frames',
        'fibrechannel-statistics/out-link-resets',
        'fibrechannel-statistics/out-max-frame-rate',
        'fibrechannel-statistics/out-multicast-pkts',
        'fibrechannel-statistics/out-octets',
        'fibrechannel-statistics/out-offline-sequences',
        'fibrechannel-statistics/out-peak-rate',
        'fibrechannel-statistics/out-rate',
        'fibrechannel-statistics/p-busy-frames',
        'fibrechannel-statistics/p-rjt-frames',
        'fibrechannel-statistics/pcs-block-errors',
        'fibrechannel-statistics/primitive-sequence-protocol-error',
        'fibrechannel-statistics/remote-primitive-sequence-protocol-error',
        'fibrechannel-statistics/too-many-rdys',
        'fibrechannel-statistics/truncated-frames',
        'fibrechannel-statistics/frames-processing-required',
        'fibrechannel-statistics/frames-processing-required',
        'fibrechannel-statistics/frames-timed-out',
        'fibrechannel-statistics/frames-transmitter-unavailable-errors',
        'fibrechannel/average-receive-frame-size',
        'fibrechannel/average-transmit-frame-size',
    )
    port_sfp_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        'fibrechannel/fcid-hex',
        'fibrechannel/port-type',
        'fibrechannel/operational-status',
        'media-rdp/serial-number',
        'media-rdp/remote-optical-product-data/serial-number',
        'media-rdp/wavelength',
        'media-rdp/remote-laser-type',
        'media-rdp/media-distance',
        'media-rdp/media-speed-capability',
        'media-rdp/remote-media-speed-capability',
        'media-rdp/power-on-time',
        'media-rdp/tx-power',
        'media-rdp/remote-media-tx-power',
        'media-rdp/rx-power',
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
        'media-rdp/vendor-name',
        'media-rdp/remote-optical-product-data/vendor-name',
        'media-rdp/vendor-oui',
        'media-rdp/part-number',
        'media-rdp/remote-optical-product-data/part-number',
        'media-rdp/vendor-revision',
        'media-rdp/remote-optical-product-data/vendor-revision',
    )
    port_rnid_tbl = (
        '_PORT_COMMENTS',
        '_SWITCH_NAME',
        '_PORT_NUMBER',
        'fibrechannel/fcid-hex',
        'fibrechannel/operational-status',
        'fibrechannel/port-type',
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
        'fibrechannel/operational-status',
        'fibrechannel/speed',
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
    # seperates the key on '.'. Similarly, FDMI port data is preceded with '_FDMI_PORT'.
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
    # 'l'   The subkey where to look for the key. Use a '/' to delineate nested dictionaries.
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
        'brocade-name-server/fibrechannel-name-server/permanent-port-name': dict(v=False, c=22, d='Permenant Port WWN'),
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
