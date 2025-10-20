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

Defines the switch object, SwitchObj.

**Version Control**
+-----------+---------------+--------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Removed obsolete MAPS stuff. Added r_fid()                                            |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Added default value to r_get() and r_alert_obj()                                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Added a hex option to r_did()                                                         |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 26 Dec 2024   | Fixed bug in r_port_obj_for_pid() when PID does not have leading '0x'                 |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 25 Aug 2025   | Added r_defined_scc() and r_active_scc()                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025 Consoli Solutions, LLC'
__date__ = '19 Oct 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.6'

import brcdapi.gen_util as gen_util
import brcdapi.util as brcdapi_util
import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as class_util
import brcddb.classes.port as port_class

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this but for now, I took
# the easy way out.


class SwitchObj:
    """The SwitchObj contains all information relevant to a switch

    Args:
        * name (str): WWN of the switch. Stored in _obj_key and key in ProjectObj

    Attributes:
        * _obj_key (str): WWN of the switch.
        * _flags (int): Flags for each class are defined in brcddb.brcddb_common
        * _project_obj (ProjectObj): The project object this fabric belongs to.
        * _port_objs (dict): Dictionary of ports in this switch. Key: s/p, Value: PortObj
        * _ge_port_objs (dict): Dictionary of GE ports in this switch. Key: s/p, Value: PortObj
        * _fabric_key (str): WWN of the fabric this port belongs to.
        * _chassis_key (str): WWN of the chassis this port belongs to.
        * _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj):
        self._obj_key = name
        self._flags = 0
        self._chassis_key = ''
        self._fabric_key = None
        self._port_objs = dict()
        self._ge_port_objs = dict()
        self._ve_port_objs = dict()
        self._alerts = list()
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return class_util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _port_objs=self.r_port_objs(),
                _ge_port_objs=self.r_ge_port_objs(),
                _ve_port_objs=self.r_ve_port_objs(),
                _fabric_key=self.r_fabric_key(),
                _chassis_key=self.r_chassis_key(),
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

    def r_obj_key(self):
        """Returns key that is used in the parent object to retrieve this object
        :return: Object key
        :rtype: str
        """
        return self._obj_key

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

    def s_polled_flag(self):
        """Set the switch polled flag, 'fabric/fabric-switch' requested"""
        self.s_or_flags(brcddb_common.switch_flag_polled)

    def s_chassis_key(self, k):
        self._chassis_key = k

    def r_chassis_key(self):
        """Returns the chassis key this switch belongs to
        :return: Login speed
        :rtype: str
        """
        return self._chassis_key

    def r_chassis_obj(self):
        """Returns the chassis object this switch belongs to
        :return: Chassis object
        :rtype: brcddb.classes.chassis.ChassisObj
        """
        return self.r_project_obj().r_chassis_obj(self.r_chassis_key())

    def r_is_polled(self):
        """Tests to determined if the switch has been polled, 'fabric/fabric-switch' requested
        :return: True: Switch has been polled. False: Switch has not been polled
        :rtype: bool
        """
        return bool(self._flags & brcddb_common.switch_flag_polled)

    def r_is_base(self):
        """Test to determine is switch is defined as a base switch, 'fibrechannel-switch/base-switch-enabled'
        :return: If True, the switch is defined as a base switch.
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfls_base_sw_en, False)

    def r_is_default(self):
        """Test to determine if switch is the default switch, 'fibrechannel-switch/default-switch-status'
        :return: If True, the switch is the default switch.
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfls_def_sw_status, False)

    def r_is_ficon(self):
        """Test to determine if switch is defined as FICON
        :return: If True, the switch is defined as a FICON switch.
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfls_ficon_mode_en, False)

    def r_is_enabled(self):
        """Determines if a switch is enabled
        :return: True if enabled, False if not enabled or unknown
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfs_enabled_state, False)

    def r_is_principal(self):
        """Test to determine is switch is the principal switch in the fabric
        :return: If True, this is the fabric principal switch.
        :rtype: bool
        """
        p = self.r_get(brcdapi_util.bfs_isprincipal)
        if p is not None:
            return p
        # As of 9.1, the two URIs below were deprecated
        return bool(self.r_get(brcdapi_util.bfs_principal, self.r_get('brocade-fabric/fabric-switch/principal')))

    def r_is_xisl(self):
        """Test to determine is logical ISLs is enabled in the switch, 'fibrechannel-switch/logical-isl-enabled'
        :return: True: Switch is the fabric principal switch. False: Switch is not the fabric principal switch
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfls_isl_enabled)

    def r_is_hif(self):
        """Test to determine if High Integrity Fabric (HIF) is enabled
        :return: True: Switch is configured for FICON. False: Switch is not configured for FICON
        :rtype: bool
        """
        return self.r_get(brcdapi_util.bfls_ficon_mode_en, False)

    def r_did(self, hex_did=False):
        """Returns the domain ID, in decimal
        :param hex_did: If True, return the DID in hex.
        :return: Domain ID as an int if hex_did is False. Otherwise, a string. None if unavailable
        :rtype: int, str, None
        """
        did = self.r_get(brcdapi_util.bfs_did, self.r_get('brocade-fabric/fabric-switch/domain-id'))
        if hex_did and did is not None:
            return hex(did)
        return did

    def r_fid(self):
        """Returns the fabric ID, in decimal
        :return: Fabric ID. None if unavailable
        :rtype: int, None
        """
        return self.r_get(brcdapi_util.bfls_fid)

    def s_fabric_key(self, wwn):
        """Set the fabric key to the WWN of the fabric
        :param wwn: WWN of fabric switch
        :type wwn: str
        """
        self._fabric_key = wwn

    def r_switch_obj(self):
        return self

    def r_switch_key(self):
        return self.r_obj_key()

    def r_fabric_key(self):
        """Returns the fabric WWN this switch is a member of
        :return: Fabric principal switch WWN. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this switch
        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        proj_obj = self.r_project_obj()
        # The switch is not in a fabric if the switch is offline of fabric information wasn't polled
        return None if self._fabric_key is None else proj_obj.r_fabric_obj(self._fabric_key)

    def r_defined_scc(self, default=None):
        """Returns the defined SCC_POLICY membership list.

        :param default: Value to return if key is not found
        :type default: None, list
        :return: Defined SCC member
        :rtype: None, list
        """
        scc_d = self.r_get('brocade-security/defined-scc-policy-member-list')
        return default if scc_d is None else [d['switch-wwn'] for d in scc_d if isinstance(d.get('switch-wwn'), str)]

    def r_active_scc(self, default=None):
        """Returns the active SCC_POLICY membership list.

        :param default: Value to return if key is not found
        :type default: None, list
        :return: Defined SCC member
        :rtype: None, list
        """
        scc_d = self.r_get('brocade-security/active-scc-policy-member-list')
        return default if scc_d is None else [d['switch-wwn'] for d in scc_d if isinstance(d.get('switch-wwn'), str)]

    def s_add_port(self, port):
        """Add a port to the switch
        :param port: Port in s/p notation
        :type port: str
        :return: Port object
        :rtype: PortObj
        """
        port_obj = self.r_port_obj(port)
        if port_obj is None:
            port_obj = port_class.PortObj(port, self.r_project_obj(), self._obj_key)
            self._port_objs.update({port: port_obj})
        return port_obj

    def r_port_keys(self):
        """Returns a list of all ports in this switch
        :return: List of ports in s/p format
        :rtype: list
        """
        return list(self._port_objs.keys())

    def r_port_objects(self):
        """Returns a list of port objects for all ports in this switch
        :return: List of PortObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._port_objs.values())

    def r_port_objs(self):
        """Returns the dictionary of port objects. Typically only used by the brcddb libraries
        :return: Dictionary of port objects
        :rtype: dict
        """
        return self._port_objs

    def r_port_obj(self, k):
        """Returns the port object for a port
        :param k: Port name in s/p notation
        :type k: str
        :return: Port object. None if port not found.
        :rtype: brcddb.classes.port.PortObj, None
        """
        return self._port_objs.get(k)

    def s_add_ge_port(self, port):
        """Add a GE port to the switch
        :param port: Port in s/p notation
        :type port: str
        :return: Port object
        :rtype: PortObj
        """
        port_obj = self.r_ge_port_obj(port)
        if port_obj is None:
            port_obj = port_class.PortObj(port, self.r_project_obj(), self._obj_key)
            self._ge_port_objs.update({port: port_obj})
        return port_obj

    def r_ge_port_keys(self):
        """Returns a list of all GE ports in this switch
        :return: List of ports in s/p format
        :rtype: list
        """
        return list(self._ge_port_objs.keys())

    def r_ge_port_objects(self):
        """Returns a list of port objects for all GE ports in this switch
        :return: List of PortObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._ge_port_objs.values())

    def r_ge_port_objs(self):
        """Returns the dictionary of port objects. Typically only used by the brcddb libraries
        :return: Dictionary of port objects
        :rtype: dict
        """
        return self._ge_port_objs

    def r_ge_port_obj(self, k):
        """Returns the port object for a GE port
        :param k: Port name in s/p notation
        :type k: str
        :return: GE Port object. None if not found.
        :rtype: brcddb.classes.port.PortObj
        """
        return self._ge_port_objs.get(k)

    def s_add_ve_port(self, port):
        """Add a VE port to the switch
        :param port: Port in s/p notation
        :type port: str
        :return: Port object
        :rtype: brcddb.classes.port.PortObj
        """
        port_obj = self.r_ve_port_obj(port)
        if port_obj is None:
            port_obj = port_class.PortObj(port, self.r_project_obj(), self._obj_key)
            self._ve_port_objs.update({port: port_obj})
        return port_obj

    def r_ve_port_keys(self):
        """Returns a list of all VE ports in this switch
        :return: List of ports in s/p format
        :rtype: list
        """
        return list(self._ve_port_objs.keys())

    def r_ve_port_objects(self):
        """Returns a list of port objects for all VE ports in this switch
        :return: List of PortObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._ve_port_objs.values())

    def r_ve_port_objs(self):
        """Returns the dictionary of port objects. Typically only used by the brcddb libraries
        :return: Dictionary of port objects
        :rtype: dict
        """
        return self._ve_port_objs

    def r_ve_port_obj(self, k):
        """Returns the port object for a VE port
        :param k: Port name in s/p notation
        :type k: str
        :return: Port object. None if matching port not found
        :rtype: brcddb.classes.port.PortObj, None
        """
        return self._ve_port_objs.get(k)

    def r_all_port_objects(self, ve=False):
        """Returns a list of all FC, GE, and optionally VE port objects in this switch.
        :param ve: If True, include VE port objects
        :type ve: bool
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = self.r_port_objects() + self.r_ge_port_objects()
        if ve:
            rl.extend(self.r_ve_port_objects())
        return rl

    def r_all_port_keys(self, ve=False):
        """Returns a list of all FC, GE, and optionally VE port keys in this switch.
        :param ve: If True, include VE port keys
        :type ve: bool
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = self.r_port_keys() + self.r_ge_port_keys()
        if ve:
            rl.extend(self.r_ve_port_keys())
        return rl

    def r_any_port_obj(self, k, ve=False):
        """Returns the port object for an FC port or GE port. Optionally include VE ports in search.
        :param k: Port name in s/p notation
        :type k: str
        :param ve: If True, include VE ports in search
        :type ve: bool
        :return: Port object. None if port not found.
        :rtype: brcddb.classes.port.PortObj, None
        """
        for port_obj in self.r_all_port_objects(ve):
            if port_obj.r_obj_key() == k:
                return port_obj
        return None

    def r_login_keys(self):
        """Returns all the login WWNs associated with this switch. Includes E-Ports
        :return: List of WWNs logged into this switch
        :rtype: list
        """
        key_l = list()
        for port_obj in self.r_port_objects():
            key_l.extend(port_obj.r_login_keys())
        return key_l

    def r_login_objects(self):
        """Returns all the login objects for logins on this switch
        :return: List of LoginObj logged into this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list if fab_obj is None else \
            gen_util.remove_none([fab_obj.r_login_obj(wwn) for wwn in self.r_login_keys()])

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this switch.
        :return: List of FDMI node WWNs associated this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return list()
        fdmi_keys = fab_obj.r_fdmi_node_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this switch
        :return: List of FdmiNodeObj associated with this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else\
            [fab_obj.r_fdmi_node_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_node_obj(wwn) is not None]

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this switch.
        :return: List of FDMI port WWNs associated this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return list()
        fdmi_keys = fab_obj.r_fdmi_port_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this switch
        :return: List of FdmiPortObj associated with this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else \
            [fab_obj.r_fdmi_port_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_port_obj(wwn) is not None]

    def r_port_object_for_index(self, i):
        """Returns the port object matching the port index i
        :param i: Port index
        :type i: int
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        if isinstance(i, int):
            for port_obj in self.r_port_objects():
                port_index = port_obj.r_index()
                if isinstance(port_index, int) and port_index == i:
                    return port_obj
        return None

    def r_port_obj_for_pid(self, in_pid):
        """Returns the port object matching an FC address
        :param in_pid: Port ID (fibre channel address)
        :type in_pid: str
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        pid = in_pid.replace('0x', '')
        for port_obj in self.r_port_objects():
            port_pid = port_obj.r_get(brcdapi_util.fc_fcid_hex)
            if isinstance(port_pid, str) and port_pid.replace('0x', '') == pid:
                return port_obj
        return None

    def c_trunk_map(self):
        """Returns the trunk groups for this switch in a map as a list of the following dictionary:
        {dswwn: {group_number: [[src_port_obj, dest_port_obj], [src_port_obj, dest_port_obj], ...]}}
        :return: List of dict as defined above
        :rtype: list
        """
        proj_obj = self.r_project_obj()
        ret = dict()
        for td in gen_util.convert_to_list(self.r_get('brocade-fibrechannel-trunk/trunk')):
            ds_wwn = td.get('neighbor-wwn')
            if ds_wwn not in ret:
                ret.update({ds_wwn: dict()})
            g = ret.get(ds_wwn)
            group = td.get('group')
            if group not in g:
                g.update({group: list()})
            group_l = g.get(group)
            li = [self.r_port_object_for_index(td.get('source-port')),
                  proj_obj.r_switch_obj(ds_wwn).r_port_object_for_index(td.get('destination-port'))]
            if len(group_l) == 0 or not td.get('master'):
                group_l.append(li)
            else:
                group_l.insert(0, li)
        return ret

    def r_active_maps_policy(self):
        """Returns the active MAPS policy associated with this switch
        :return: Active MAPS. None if no active MAPS policy
        :rtype: dict, None
        """
        for obj in gen_util.convert_to_list(self.r_get(brcdapi_util.maps_policy)):
            if obj.get('is-active-policy'):
                return obj
        return None

    def c_switch_model(self):
        """Returns the switch model as an integer
        :return: Switch model as an integer
        :rtype: int
        """
        try:
            return int(float(self.r_get(brcdapi_util.bfs_model)))
        except TypeError:
            return 0

    def s_new_key(self, k, v, f=False):
        """Creates a new key/value pair.
        :param k: Key to be added
        :type k: str, int
        :param v: Value to be added. Although any type should be valid, it has only been tested with the types below.
        :type v: str, int, list, dict
        :param f: If True, don't check to see if the key exists. Allows users to change an existing value.
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
