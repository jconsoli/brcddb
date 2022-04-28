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
:mod:`brcdd.classes.port` - Defines the port object, PortObj.

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
    | 3.0.2     | 14 Nov 2020   | Handle all port speeds.                                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 17 Jul 2021   | Added r_addr(), r_index()                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 14 Nov 2021   | Use common util.get_reserved() in r_get_reserved()                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 31 Dec 2021   | No functional changes. Replaced bare except with explicit except.                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 28 Apr 2022   | Added KeyError to except in c_login_type()                                        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022 Jack Consoli'
__date__ = '28 Apr 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.8'

import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as util

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
        _maps_fc_port_group (list): List of MAPS groups associated with the port
        _maps_sfp_group (list): List of MAPS groups associated with the SFP
    """

    def __init__(self, name, project_obj, switch_wwn):
        self._obj_key = name
        self._project_obj = project_obj
        self._switch = switch_wwn
        self._flags = 0
        self._alerts = list()
        self._maps_fc_port_group = list()
        self._maps_sfp_group = list()

    def _i_port_flags(self, k):
        """For internal use only. Returns the state of the specified port flag

        :param k: Key flag
        :type k: str
        :return: True if value is present in port_obj and is True, otherwise False
        :rtype: bool
        """
        try:
            return brcddb_common.port_conversion_tbl[k][self.r_get(k)]
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
        return util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _switch=self.r_switch_key(),
                _maps_fc_port_group=self.r_maps_fc_port_group(),
                _maps_sfp_group=self.r_maps_sfp_group(),
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

    def r_login_keys(self):
        """Returns all the login WWN associated with this port.

        :return: List of WWNs logged into this port
        :rtype: list
        """
        return gen_util.convert_to_list(util.class_getvalue(self, 'fibrechannel/neighbor/wwn'))

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
        if util.class_getvalue(self, 'fibrechannel/port-user-friendly-name') is not None:
            return util.class_getvalue(self, 'fibrechannel/port-user-friendly-name')
        else:
            return '' if util.class_getvalue(self, 'fibrechannel/user-friendly-name') is None else \
                util.class_getvalue(self, 'fibrechannel/user-friendly-name')

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

        :return: True: Port is enabled. False: Port is not enabled
        :rtype: bool
        """
        return self._i_port_flags('fibrechannel/is-enabled-state')

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

    def r_is_online(self):
        """Determines if the port is online

        :return: True: port is online. False: port is offline.
        :rtype: bool
        """
        try:
            return True if brcddb_common.port_conversion_tbl['fibrechannel/operational-status']\
                               [self.r_get('fibrechannel/operational-status')] == 'Online' else False
        except (ValueError, IndexError):
            return False

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

        :return: Slot number
        :rtype: int
        """
        return int(self.r_obj_key().split('/')[0])

    def r_addr(self):
        """Returns the FC address for the port

        :return: FC address in 0xab1200 format. None if unavailable
        :rtype: str, None
        """
        return self.r_get('fibrechannel/fcid-hex')

    def r_index(self):
        """Returns the port index for the port

        :return: Port index. None if unavailable
        :rtype: int, None
        """
        return self.r_get('fibrechannel/index')

    def c_login_type(self):
        """Converts the login type to a human readable port type

        :return: Port type
        :rtype: str
        """
        try:
            return brcddb_common.port_conversion_tbl['fibrechannel/port-type'][self.r_get('fibrechannel/port-type')]
        except (IndexError, ValueError, KeyError):
            return 'Unknown'

    def c_power_on_time_days(self):
        """Converts the power on time to days

        :return: Time in days
        :rtype: int
        """
        v = self.r_get('media-rdp/power-on-time')
        return 0 if v is None else int(v/24 + 0.5)

    def c_media_distance(self):
        """Converts the media (SFP) distance capabilities to a CSV string

        :return: Media distance
        :rtype: str
        """
        return ', '.join(gen_util.convert_to_list(self.r_get('media-rdp/media-distance/distance')))

    def c_media_speed_capability(self):
        """Converts the media (SFP) speed capabilities to a CSV string

        :return: Media speeds
        :rtype: str
        """
        return ', '.join(gen_util.convert_to_list(self.r_get('media-rdp/media-speed-capability/speed')))

    def c_login_speed(self):
        """Converts the login speed to a user friendly string (as is reported in the FOS command 'switchshow')

        :return: Login spped
        :rtype: str
        """
        speed = self.r_get('fibrechannel/speed')
        if isinstance(speed, (int, float)):
            return str(int(speed/1000000000)) + 'N' if self.r_is_auto_neg() else str(int(speed/1000000000)) + 'G'
        else:
            return ''

    def r_chassis_key(self):
        """Returns the chassis key this port belongs to

        :return: Login spped
        :rtype: str
        """
        return self.r_switch_obj().r_chassis_key()

    def r_chassis_obj(self):
        """Returns the chassis object this port belongs to

        :return: Login speed
        :rtype: str
        """
        return self.r_project_obj().r_chassis_obj(self.r_chassis_key())

    def s_add_maps_fc_port_group(self, group):
        """Adds a group to the FC port

        :param group: MAPS group name this port is a member of
        :type group: str
        """
        if group not in self._maps_fc_port_group:
            self._maps_fc_port_group.append(group)

    def r_maps_fc_port_group(self):
        """Returns the list of MAPS group this port is a member of

        :return: List of strings (MAPS group names)
        :rtype: list
        """
        return self._maps_fc_port_group

    def s_add_maps_sfp_group(self, group):
        """Adds a group to the SFP for this port

        :param group: MAPS group name this SFP is a member of
        :type group: str
        """
        if group not in self._maps_sfp_group:
            self._maps_sfp_group.append(group)

    def r_maps_sfp_group(self):
        """Returns the list of MAPS group this port's SFP is a member of

        :return: List of strings (MAPS group names)
        :rtype: list
        """
        return self._maps_sfp_group

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
        return util.s_new_key_for_class(self, k, v, f)

    def r_get(self, k):
        """Returns the value for a given key. Keys for nested objects must be separated with '/'.

        :param k: Key
        :type k: str, int
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return util.class_getvalue(self, k)

    def r_keys(self):
        """Returns a list of keys added to this object.

        :return: List of keys
        :rtype: list
        """
        return util.class_getkeys(self)
