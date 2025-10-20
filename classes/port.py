"""
Copyright 2023, 2024, 2025 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Defines the port object, PortObj.

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Removed obsolete MAPS stuff                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Added default value to r_get() and r_alert_obj()                                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Added r_did()                                                                         |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 26 Dec 2024   | Fixed confusion over duplicate use of "hex"                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 04 Apr 2025   | Use current port user friendly name first in r_port_name() first.                     |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.7     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025 Consoli Solutions, LLC'
__date__ = '19 Oct 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.7'

import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as class_util

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this.


class PortObj:
    """The PortObj contains all information relevant to a port including:
        * 'logical-switch/fibrechannel-logical-switch/port-member'
        * 'brocade-interface/fibrechannel-statistics'
        * 'brocade-interface/fibrechannel'
        * 'brocade-interface/extension-ip-interface'
        * 'brocade-interface/gigabitethernet'
        * 'brocade-interface/gigabitethernet-statistics'
        * 'brocade-media/media-rdp'

    Args:
        name (str): s/p of the port. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): s/p of the port.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this port belongs to.
        _switch (str): WWN of the switch this port belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj, switch_wwn):
        self._obj_key = name
        self._project_obj = project_obj
        self._switch = switch_wwn
        self._flags = 0
        self._alerts = list()

    def _i_port_flags(self, k):
        """For internal use only. Returns the state of the specified port flag

        :param k: Key flag
        :type k: str
        :return: True if value is present in port_obj and is True, otherwise False
        :rtype: bool
        """
        try:
            return brcddb_common.port_conversion_tbl[k][self.r_get(k, False)]
        except (ValueError, KeyError):
            pass
        return False

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        # When adding a reserved key, don't forget you may also need to update brcddb.util.copy
        return class_util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _switch=self.r_switch_key(),
            ),
            k
        )

    def s_add_alert(self, tbl, num, key=None, p0=None, p1=None):
        """Add an alert to this object

        :param tbl: The table that defines this alert. See brcddb.classes.alert.AlertObj
        :type tbl: dict
        :param num: Alert number. See brcddb.classes.alert.AlertObj
        :type num: int
        :param key: Key associated with this alert. See brcddb.classes.alert.AlertObj
        :type key: str, None
        :param p0: Optional parameter. See brcddb.classes.alert.AlertObj
        :type p1: str, int, float, None
        :param p1: Optional parameter. See brcddb.classes.alert.AlertObj
        :return: Alert object
        :rtype: brcddb.classes.alert.AlertObj
        """
        alert_obj = alert_class.AlertObj(tbl, num, key, p0, p1)
        self._alerts.append(alert_obj)
        return alert_obj

    def r_alert_objects(self):
        """Returns a list of alert objects associated with this object

        :return: List of alert objects (brcddb.classes.alert.AlertObj)
        :rtype: list
        """
        return self._alerts

    def r_alert_nums(self):
        """Returns a list of alert numbers associated with this object

        :return: List of alert objects (brcddb.classes.alert.AlertObj)
        :rtype: list
        """
        return [alert_obj.alert_num() for alert_obj in self._alerts]

    def r_alert_obj(self, alert_num):
        """Returns the alert object for a specific alert number

        :return: Alert object. None if not found.
        :rtype: None, brcddb.classes.alert.AlertObj
        """
        for alert_obj in self.r_alert_objects():
            if alert_obj.alert_num() == alert_num:
                return alert_obj
        return None

    def r_reserved_keys(self):
        """Returns a list of reserved words (keys) associated with this object

        :return: List of reserved words
        :rtype: list
        """
        return self.r_get_reserved('_reserved_keys')

    def r_project_obj(self):
        """Returns the project object associated with this object

        :return: Project object
        :rtype: ProjectObj
        """
        return self._project_obj

    def r_port_obj(self):
        return self

    def r_port_key(self):
        return self.r_obj_key()

    def r_switch_key(self):
        """Returns the WWN for the switch this port belongs to

        :return: Switch WWN
        :rtype: str
        """
        return self._switch
    
    def r_switch_obj(self):
        """Returns the switch object this port belongs to

        :return: Switch object
        :rtype: SwitchObj
        """
        return self.r_project_obj().r_switch_obj(self.r_switch_key())

    def r_fabric_obj(self):
        """Returns the fabric object associated with this port

        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        return self.r_switch_obj().r_fabric_obj()

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this port

        :return: Fabric principal switch WWN. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        return self.r_switch_obj().r_fabric_key()

    def s_add_login(self, wwn):
        """Adds a login to the fabric for this port if it doesn't already exist

        :param wwn: WWN of the login
        :type wwn: str
        :return: Login object
        :rtype: LoginObj
        """
        fab_obj = self.r_fabric_obj()
        login_obj = fab_obj.s_add_login(wwn)
        wwn_l = class_util.get_or_add(self, 'fibrechannel/neighbor/wwn', list())
        if wwn not in wwn_l:
            wwn_l.append(wwn)
        return login_obj

    def r_login_keys(self):
        """Returns all the login WWN associated with this port.

        :return: List of WWNs logged into this port
        :rtype: list
        """
        return gen_util.convert_to_list(class_util.class_getvalue(self, 'fibrechannel/neighbor/wwn'))

    def r_login_objects(self):
        """Returns all the login objects for logins on this port

        :return: List of LoginObj logged into this port
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else \
            [fab_obj.r_login_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_login_obj(wwn) is not None]

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this port.

        :return: List of FDMI node WWNs associated this port
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return list()
        fdmi_keys = fab_obj.r_fdmi_node_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this port

        :return: List of FdmiNodeObj associated with this port
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else \
            [fab_obj.r_fdmi_node_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_node_obj(wwn) is not None]

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this port.

        :return: List of FDMI port WWNs associated this port
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return list()
        fdmi_keys = fab_obj.r_fdmi_port_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this port

        :return: List of FdmiPortObj associated with this port
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else \
            [fab_obj.r_fdmi_port_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_port_obj(wwn) is not None]

    def r_obj_key(self):
        """Returns key that is used in the parent object to retrieve this object

        :return: Object key
        :rtype: str
        """
        return self._obj_key

    def r_port_name(self):
        """Returns the defined name for this port
        :return: Port name
        :rtype: str
        """
        return class_util.class_getvalue(
            self,
            'fibrechannel/user-friendly-name',
            default=class_util.class_getvalue(self, 'fibrechannel/port-user-friendly-name', default=''))

    def r_flags(self):
        """Returns flags associated with this object. Flags are defined in brcddb_common.py

        :return: Bit flags
        :rtype: int
        """
        return self._flags

    def s_or_flags(self, bits):
        """Performs a logical OR on the flags associated with this object. Flags are defined in brcddb_common.py

        :param bits: Bits to be ORed with the bit flags
        :type bits: int
        :return: Bit flags
        :rtype: int
        """
        self._flags |= bits
        return self._flags

    def s_and_flags(self, bits):
        """Performs a logical AND on the flags associated with this object. Flags are defined in brcddb_common.py

        :param bits: Bits to be ANDed with the bit flags
        :type bits: int
        :return: Bit flags
        :rtype: int
        """
        self._flags &= bits
        return self._flags

    def r_is_enabled(self):
        """Determines if the port is enabled

        :return: True: Port is enabled. False: Port is not enabled or state is unknown
        :rtype: bool
        """
        return self.r_get(brcdapi_util.fc_enabled, False)

    def r_is_dport(self):
        """Determines if the diagnostic port (D-Port) is enabled

        :return: True: D-Port is enabled. False: D-Port is not enabled
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/d-port-enable')

    def r_is_persistent_disable(self):
        """Determines if the port is persistently disabled

        :return: True: Port is persistently disabled. False: Port is not persistently disabled
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/persistent-disable')

    def r_is_qos_enabled(self):
        """Determines if QoS is enabled on the port

        :return: True: QoS is enabled. False: QoS is not enabled
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/qos-enabled')

    def r_is_target_zone_enabled(self):
        """Determines if target zoning is allowed

        :return: True: Target driven zoning is allowed. False: Target driven zoning is not allowed.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/target-driven-zoning-enable')

    def r_is_auto_neg(self):
        """Determines if auto-speed negotiation is enabled

        :return: True: Auto-speed negotiation is enabled. False: Auto-speed negotiation is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/auto-negotiate')

    def r_is_locked_g_port(self):
        """Determines if port is locked as a G-Port

        :return: True: Port type is locked as a G-Port. False: Port type is not locked as a G-Port.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/g-port-locked')

    def r_is_e_port_disable(self):
        """Determines if ISL mode (E-Port) is disabled

        :return: True: E-Port is disabled. False: E-Port is not disabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/e-port-disable')

    def r_is_n_port_enabled(self):
        """Determines if node port (N-Port) is allowed

        :return: True: N-Port is disabled. False: N-Port is not disabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/n-port-enabled')

    def r_is_compression_configured(self):
        """Determines if compression is enabled

        :return: True: compression is enabled. False: compression is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/compression-configured')

    def r_is_compression_active(self):
        """Determines if compression is active

        :return: True: Compression is active. False: Compression is not active.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/compression-active')

    def r_is_encryption_active(self):
        """Determines if encryption is active

        :return: True: encryption is active. False: encryption is not active.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/encryption-active')

    def r_is_sim_port(self):
        """Determines if simulation port (Sim-Port) is enabled, 'brocade-interface/fibrechannel/sim-port-enabled' == 1

        :return: True: encryption is active. False: encryption is not active.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/sim-port-enabled')

    def r_is_mirror_port(self):
        """Determines if mirroring is enabled
        :return: True: mirroring is enabled. False: mirroring is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/mirror-port-enabled')

    def r_is_credit_recovery_enabled(self):
        """Determines if credit recovery is enabled, 'brocade-interface/fibrechannel/credit-recovery-enabled' == 1

        :return: True: credit recovery is enabled. False: credit recovery is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/credit-recovery-enabled')

    def r_is_credit_recovery_active(self):
        """Determines if credit recovery is active
        :return: True: credit recovery is active. False: credit recovery is not active.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/credit-recovery-active')

    def r_is_fec_active(self):
        """Determines if forward error correction (FEC) is active

        :return: True: FEC is active. False: FEC is not active.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/fec-active')

    def r_is_csctl(self):
        """Determines if external QoS (CSCTL) is enabled

        :return: True: CSCTL is enabled. False: CSCTL is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/csctl-mode-enabled')

    def r_is_fault_delay_ra_tov(self):
        """Determines if fault delay is enabled

        :return: True: fault delay is enabled. False: fault delay is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/fault-delay-enabled')

    def r_is_trunk_port_enabled(self):
        """Determines if trunking is enabled

        :return: True: trunking is enabled. False: trunking is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/trunk-port-enabled')

    def r_is_vc_link_init_enabled(self):
        """Determines if VC link initialization is enabled

        :return: True: VC link init is enabled. False: VC link init is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/vc-link-init')

    def r_is_isl_ready_enabled(self):
        """Determines if ISL ready mode is enabled

        :return: True: ISL ready mode is enabled. False: ISL ready mode is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/isl-ready-mode-enabled')

    def r_is_supress_rscn(self):
        """Determines if suppress RSCN mode is enabled

        :return: True: supress RSCN mode is enabled. False: supress RSCN mode is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/rscn-suppression-enabled')

    def r_is_npiv_enabled(self):
        """Determines if NPIV is allowed

        :return: True: NPIV is allowed. False: NPIV is not allowed.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/npiv-enabled')

    def r_is_npiv_flogi_lockout(self):
        """Determines if NPIV FLOGI is lockout is enabled

        :return: True: NPIV FLOGI is lockout is enabled. False: NPIV FLOGI is lockout is not enabled
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/npiv-flogi-logout-enabled')

    def r_is_ex_port_enabled(self):
        """Determines if EX-Port is allowed

        :return: True: EX-Port is allowed. False: EX-Port is not allowed.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/ex-port-enabled')

    def r_is_fec_enabled(self):
        """Determines if FEC is enabled

        :return: True: FEC is enabled. False: FEC is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/fec-enabled')

    def r_is_fec_tts_enabled(self):
        """Determines if FEC via TTS is enabled

        :return: True: FEC via TTS is enabled. False: FEC via TTS is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/via-tts-fec-enabled')

    def r_is_auto_disable(self):
        """Determines if auto disabled is enabled

        :return: True: auto disabled is enabled. False: auto disabled is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/port-autodisable-enabled')

    def r_is_non_dfe_enabled(self):
        """Determines if non-DEF mode is enabled

        :return: True: non-DEF mode is enabled. False: non-DEF mode is not enabled.
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/non-dfe-enabled')

    def r_status(self):
        """Returns the port status using FOS 9.0 string type first. Old converted integer if string type not found.

        :return: Port status
        :rtype: str
        """
        try:
            return self.r_get(
                brcdapi_util.fc_op_status_str,
                brcddb_common.port_conversion_tbl[brcdapi_util.fc_op_status][self.r_get(brcdapi_util.fc_op_status)]
            )
        except (KeyError, ValueError, IndexError):
            return 'Unknown'

    def r_is_online(self):
        """Determines if the port is online

        :return: True: port is online. False: port is offline.
        :rtype: bool
        """
        return True if self.r_status().lower() == 'online' else False

    def r_is_icl(self):
        """Determines if the port is on a core blade

        :return: True: Port is on a core blade (ICL), otherwise False
        :rtype: bool
        """
        try:
            return True if 'core' in self.r_chassis_obj().c_fru_blade_map()[self.r_slot()].get('blade-type') else False
        except (ValueError, AttributeError):
            return False

    def r_slot(self):
        """Returns the slot number for the port

        :return: Slot number. None if slot number is not valid (which only happens here with a code bug)
        :rtype: int, None
        """
        return gen_util.slot_port(self.r_obj_key())[0]

    def r_port(self):
        """Returns the port number for the port

        :return: Port number, which may be a GE port. None if port number is not valid
        :rtype: int, str, None
        """
        slot, port, ge_port = gen_util.slot_port(self.r_obj_key())
        return port if isinstance(port, int) else ge_port

    def r_addr(self):
        """Returns the FC address for the port

        :return: FC address in 0xab1200 format. None if unavailable
        :rtype: str, None
        """
        return self.r_get(brcdapi_util.fc_fcid_hex)

    def r_did(self, hex_did=False):
        """Returns the domain ID, in decimal
        :param hex_did: If True, return the DID in hex.
        :return: Domain ID as an int if hex is False. Otherwise, a string. None if unavailable
        :rtype: int, str, None
        """
        try:
            return self.r_switch_obj().r_did(hex_did=hex_did)
        except TypeError:
            # Just future proofing. The port object always belonged to a switch object when this was written
            return None

    def r_index(self):
        """Returns the port index for the port

        :return: Port index. None if unavailable
        :rtype: int, None
        """
        return self.r_get(brcdapi_util.fc_index)

    def c_login_type(self):
        """Converts the login type to a human-readable port type

        :return: Port type
        :rtype: str
        """
        try:
            return self.r_get(
                brcdapi_util.fc_port_type_str,
                brcddb_common.port_conversion_tbl[brcdapi_util.fc_port_type][self.r_get(brcdapi_util.fc_port_type)]
            )
        except (IndexError, ValueError, KeyError):
            return 'Unknown'

    def c_power_on_time_days(self):
        """Converts the power on time to days

        :return: Time in days
        :rtype: int
        """
        v = self.r_get(brcdapi_util.sfp_power_on)
        return 0 if v is None else int(v/24 + 0.5)

    def c_media_distance(self):
        """Converts the media (SFP) distance capabilities to a CSV string

        :return: Media distance
        :rtype: str
        """
        return ', '.join(gen_util.convert_to_list(self.r_get(brcdapi_util.sfp_distance)))

    def c_media_speed_capability(self):
        """Converts the media (SFP) speed capabilities to a CSV string

        :return: Media speeds
        :rtype: str
        """
        return ', '.join(gen_util.convert_to_list(self.r_get(brcdapi_util.sfp_speed)))

    def c_login_speed(self):
        """Converts the login speed to a user-friendly string (as is reported in the FOS command 'switchshow')

        :return: Login speed
        :rtype: str
        """
        speed = self.r_get(brcdapi_util.fc_speed)
        if isinstance(speed, (int, float)):
            return str(int(speed/1000000000)) + 'N' if self.r_is_auto_neg() else str(int(speed/1000000000)) + 'G'
        else:
            return ''

    def r_chassis_key(self):
        """Returns the chassis key this port belongs to

        :return: Login speed
        :rtype: str
        """
        return self.r_switch_obj().r_chassis_key()

    def r_chassis_obj(self):
        """Returns the chassis object this port belongs to

        :return: Chassis object
        :rtype: ChassisObj
        """
        return self.r_project_obj().r_chassis_obj(self.r_chassis_key())

    def s_new_key(self, k, v, f=False):
        """Creates a new key/value pair.

        :param k: Key to be added
        :type k: str, int
        :param v: Value to be added. Although any type should be valid, it has only been tested with the types below.
        :type v: str, int, list, dict
        :param f: If True, don't check to see if the key exists. Allows users to change an existing key.
        :type f: bool
        :return: True if the add succeeded or is redundant.
        :rtype: bool
        """
        return class_util.s_new_key_for_class(self, k, v, f)

    def r_get(self, k, default=None):
        """Returns the value for a given key. Keys for nested objects must be separated with '/'.

        :param k: Key
        :type k: str, int
        :param default: Value to return if key is not found
        :type default: str, bool, int, float, list, dict, tuple
        :return: Value matching the key/value pair of dflt_val if not found.
        :rtype: str, bool, int, float, list, dict, tuple
        """
        return class_util.class_getvalue(self, k, default=default)

    def rs_key(self, k, v):
        """Return the value of a key. If the key doesn't exist, create it with value v

        :param k: Key
        :type k: str, int
        :param v: Value to be added if not already present.
        :type v: None, bool, float, str, int, list, dict
        :return: Value
        :rtype: None, bool, float, str, int, list, dict
        """
        return class_util.get_or_add(self, k, v)

    def r_keys(self):
        """Returns a list of keys added to this object.

        :return: List of keys
        :rtype: list
        """
        return class_util.class_getkeys(self)

    def r_format(self, full=False):
        """Returns a list of formatted text for the object. Intended for error reporting.

        :param full: If True, expand (pprint) all data added with obj.s_new_key() pprint.
        :type full: bool
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return class_util.format_obj(self, full=full)
