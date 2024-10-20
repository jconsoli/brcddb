"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Defines the chassis object, ChassisObj.

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Added default value to r_get() and r_alert_obj().                                     |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '20 Oct 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.2'

import brcdapi.util as brcdapi_util
import brcddb.classes.alert as alert_class
import brcddb.classes.util as class_util

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


class ChassisObj:
    """The ChassisObj contains all information relevant to the chassis

    Args:
        name (str): WWN of the chassis. Stored in _obj_key and key in ProjectObj.

    Attributes:
    * _obj_key (str): WWN of the chassis.
    * _flags (int): Flags for each class are defined in brcddb.brcddb_common
    * _switch_keys (str): List of logical switch WWNs defined on this chassis
    * _project_obj (ProjectObj): The project object this chassis belongs to.
    * _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj):
        self._obj_key = name
        self._flags = 0
        self._switch_keys = list()
        self._alerts = list()
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.
         :param k: Reserved key
         :type k: str
         :return: Value associated with k. None if k is not present
         :rtype: None, bool, int, float, str, dict, list, tuple, AlertObj, ProjectObj
         """
        return class_util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _switch_keys=self.r_switch_keys(),
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
        :rtype: alert_class.AlertObj
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

    def r_is_vf_enabled(self):
        """Tests the virtual fabrics (VF) enabled flag ('brocade-chassis/vf-enabled')

        :return: True if VF is enabled. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bp_vf_enabled)
        return False if v is None else v

    def r_is_vf_supported(self):
        """Tests the virtual fabrics (VF) supported flag ('brocade-chassis/vf-supported')
        :return: True if VF is enabled. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bc_vf)
        return False if v is None else v

    def r_is_ha_enabled(self):
        """Tests the high availability (HA) enabled flag ('brocade-chassis/ha-enabled')
        :return: True if HA is enabled. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bc_ha_enabled)
        return False if v is None else v

    def r_is_heartbeat_up(self):
        """Tests the heart beat up flag ('brocade-chassis/heartbeat-up')
        :return: True if the HA heart beat is up. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bc_heartbeat)
        return False if v is None else v

    def r_is_ha_sync(self):
        """Tests the high availability (HA) sync flag ('brocade-chassis/ha-status/ha-synchronized')
        :return: True if in HA sync. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bc_ha_sync)
        return False if v is None else v

    def r_is_extension_enabled(self, slot=0):
        """Tests the virtual fabrics enabled flag ('brocade-fru/blade/extension-enabled')
        :param slot: Slot number of board where the extension flag is to be tested
        :return: True if extension is enabled. Otherwise, False
        :rtype: bool
        """
        blades = self.r_get(brcdapi_util.fru_blade)
        for blade in blades:
            s = blade.get('slot-number')
            if s is not None and s == slot:
                return blade.get('extension-enabled')
        return False

    def r_is_bladded(self):
        """Determines if the chassis is bladed or fixed port
        :return: True if director class. Otherwise, False
        :rtype: bool
        """
        v = self.r_get(brcdapi_util.bc_max_blades)
        return False if not isinstance(v, int) else True if v > 1 else False

    def s_add_switch(self, wwn):
        """Adds a switch to the project if it doesn't already exist and then adds it to chassis if not already added
        :param wwn: WWN of logical switch
        :type wwn: str
        """
        if wwn not in self._switch_keys:
            self._switch_keys.append(wwn)
        switch_obj = self.r_project_obj().s_add_switch(wwn)
        switch_obj.s_chassis_key(self.r_obj_key())
        return switch_obj

    def s_del_switch(self, wwn):
        """Deletes a switch key from the fabric. It does not delete the switch object from the project.
        :param wwn: WWN of logical switch
        :type wwn: str
        :rtype: None
        """
        self._switch_keys = list(filter(lambda item: item != wwn, self._switch_keys))

    def r_switch_keys(self):
        """Returns the list of logical switch WWNs in this chassis
        :return: List of switch WWNs
        :rtype: list
        """
        return list(self._switch_keys)

    def r_switch_objects(self):
        """Returns the list of switch objects for the switches in this chassis
        :return: List of SwitchObj
        :rtype: list
        """
        return [self.r_project_obj().r_switch_obj(k) for k in self.r_switch_keys()]

    def r_switch_obj_for_fid(self, fid):
        """Returns the switch objects for the fid in this chassis
        :param fid: Fabric ID
        :type fid: int
        :return: Switch object matching fid. None if not found
        :rtype: None, brcddb.chassis.switch.SwitchObj
        """
        for switch_obj in self.r_switch_objects():
            if switch_obj.r_get(brcdapi_util.bfls_fid) == fid:
                return switch_obj
        return None

    def r_default_switch_obj(self):
        """Returns the switch object for the default switch in this chassis
        :return: Switch object. None if default switch object not found (logical switches haven't been polled yet)
        :rtype: brcddb.classes.switch.SwitchObj, None
        """
        for switch_obj in self.r_switch_objects():
            if switch_obj.r_get(brcdapi_util.bfls_def_sw_status):
                return switch_obj
        return None

    def r_default_switch_fid(self):
        """Returns the FID for the default switch in this chassis
        :return: Fabric ID. None if not found.
        :rtype: int, None
        """
        switch_obj = self.r_default_switch_obj()
        return None if switch_obj is None else switch_obj.r_get(brcdapi_util.bfls_fid)

    def r_fabric_keys(self):
        """Returns the list of fabric keys associated with switches in this chassis
        :return: List of keys (fabric WWNs)
        :rtype: list
        """
        # If FID checking is disabled, two switches in this chassis can be in the same fabric. This is why I remove
        # duplicates. If the data capture did not include all chassis, a switch object may return None for the fabric
        return gen_util.remove_duplicates(gen_util.remove_none([obj.r_fabric_key() for obj in self.r_switch_objects()]))

    def r_fabric_objects(self):
        """Returns the list of fabric objects associated with switches in this chassis
        :return: List of keys (fabric WWNs)
        :rtype: list
        """
        # If FID checking is disabled, two switches in this chassis can be in the same fabric. This is why I look up the
        # fabric object based on the list of fabric keys returned from self.r_fabric_keys().
        proj_obj = self.r_project_obj()
        return [proj_obj.r_fabric_obj(wwn) for wwn in self.r_fabric_keys()]

    def r_ve_port_keys(self):
        """Returns a list of all VE ports in this switch
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_ve_port_keys())
        return rl

    def r_ve_port_objects(self):
        """Returns a list of port objects for all VE ports in this switch
        :return: List of PortObj
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_ve_port_objects())
        return rl

    def r_ve_port_obj(self, k):
        """Returns the port object for a VE port
        :param k: Port name in s/p notation
        :type k: str
        :return: Port object. None if matching port not found
        :rtype: brcddb.classes.port.PortObj, None
        """
        for switch_obj in self.r_switch_objects():
            ve_port_obj = switch_obj.r_ve_port_obj(k)
            if ve_port_obj is not None:
                return ve_port_obj
        return None

    def r_login_keys(self):
        """Returns all the login WWNs associated with this chassis. Includes E-Ports
        :return: List of WWNs logged into this port
        :rtype: list
        """
        key_l = list()
        for switch_obj in self.r_switch_objects():
            key_l.extend(switch_obj.r_login_keys())
        return key_l

    def r_login_objects(self):
        """Returns all the login objects for logins in this chassis
        :return: List of LoginObj logged into this port
        :rtype: list
        """
        login_obj_l = list()
        for switch_obj in self.r_switch_objects():
            login_obj_l.extend(switch_obj.r_login_objects())
        return login_obj_l

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this chassis.
        :return: List of FDMI node WWNs associated this chassis
        :rtype: list
        """
        rl = list()
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_node_keys())
        return rl

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this chassis
        :return: List of FdmiNodeObj associated with this chassis
        :rtype: list
        """
        rl = list()
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_node_objects())
        return rl

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this chassis.
        :return: List of FDMI port WWNs associated this chassis
        :rtype: list
        """
        rl = list()
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_port_keys())
        return rl

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this chassis
        :return: List of FdmiPortObj associated with this chassis
        :rtype: list
        """
        rl = list()
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_port_objects())
        return rl

    def r_fid_list(self):
        """Returns the list of logical fabric ID (FID) in this chassis
        :return: List of FIDs (int)
        :rtype: list
        """
        return gen_util.remove_none([switch_obj.r_get(brcdapi_util.bfls_fid) for switch_obj in self.r_switch_objects()])

    def r_slot(self, s):
        """Returns the FRU information for a specific blade

        :return: The blade dictionary for a specific blade as returned from the API
        :rtype: dict
        """
        for b in gen_util.convert_to_list(self.r_get(brcdapi_util.fru_blade)):
            if isinstance(b.get('slot_number'), int) and b.get('slot_number') == s:
                return b
        return None

    def r_port_keys(self):
        """Returns a list of all ports in this chassis

        :return: List of ports in s/p format
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_port_keys())
        return rl

    def r_port_objects(self):
        """Returns a list of port objects for all ports in this chassis

        :return: List of PortObj
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_port_objects())
        return rl

    def r_port_obj(self, port):
        """Returns the port object for a port

        :param port: Port name in s/p notation
        :type port: str
        :return: Port object. None if not found
        :type: None, brcddb.classes.port.PortObj
        """
        for switch_obj in self.r_switch_objects():
            port_obj = switch_obj.r_port_obj(port)
            if port_obj is not None:
                return port_obj
        return None

    def r_port_object_for_index(self, i):
        """Returns the port object matching a port index
        :param i: Port index
        :type i: int
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        if isinstance(i, int):
            for port_obj in self.r_all_port_objects():
                port_index = port_obj.r_index()
                if isinstance(port_index, int) and port_index == i:
                    return port_obj
        return None

    def r_ge_port_keys(self):
        """Returns a list of all GE ports in this chassis
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_ge_port_keys())
        return rl

    def r_ge_port_objects(self):
        """Returns a list of port objects for all GE ports in this chassis
        :return: List of PortObj
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_ge_port_objects())
        return rl

    def r_ge_port_obj(self, k):
        """Returns the port object for a GE port
        :param k: Port name in s/p notation
        :type k: str
        :return: Port object. None if port not found.
        :rtype: brcddb.classes.port.PortObj, None
        """
        for switch_obj in self.r_switch_objects():
            if switch_obj.r_ge_port_obj(k) is not None:
                return switch_obj.r_ge_port_obj(k)
        return None

    def r_all_port_objects(self, ve=False):
        """Returns a list of all FC, GE, and optionally VE port objects in this chassis.
        :param ve: If True, include VE port objects
        :type ve: bool
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_all_port_objects(ve))
        return rl

    def r_all_port_keys(self, ve=False):
        """Returns a list of all FC, GE, and optionally VE port keys in this fabric.
        :param ve: If True, include VE port keys
        :type ve: bool
        :return: List of ports in s/p format
        :rtype: list
        """
        rl = list()
        for switch_obj in self.r_switch_objects():
            rl.extend(switch_obj.r_all_port_keys(ve))
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
        for switch_obj in self.r_switch_objects():
            port_obj = switch_obj.r_any_port_obj(k, ve)
            if port_obj is not None:
                return port_obj
        return None

    def c_fru_blade_map(self):
        """Sorts brocade-fru/blade into a list that can be indexed by slot number

        :return: List of brocade-fru/blade dict. Note that if no blade installed at a slot, the list entry is None
        :rtype: list
        """
        tl = [None, None, None, None, None, None, None, None, None, None, None, None, None]
        for blade in [b for b in gen_util.convert_to_list(self.r_get(brcdapi_util.fru_blade)) if
                      isinstance(b, int) and b < len(tl)]:
            tl[blade.get('slot-number')] = blade
        return tl

    def r_chassis_obj(self):
        return self

    def r_chassis_key(self):
        return self.r_obj_key()

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
