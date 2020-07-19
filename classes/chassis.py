#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcdd.classes.chassis` - Defines the chassis object, ChassisObj.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '19 Jul 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import brcddb.classes.alert as alert_class
import brcddb.classes.util as util

# Programmer's Tip: Apparently, .clear() doesn't work on dereferenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revist this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


class ChassisObj:
    """The ChassisObj contains all information relevant to the chassis including:
    * 'brocade-chassis/chassis'
    * 'brocade-chassis/ha-status'
    * 'brocade-fru/blade'
    * 'brocade-fru/fan'
    * 'brocade-fru/power-supply'

    Args:
        name (str): WWN of the chassis. Stored in _obj_key and key in ProjectObj.

    Attributes:
    * _obj_key (str): WWN of the chassis.
    * _flags (int): Flags for each class are defined in brcddb.brcddb_common
    * _switch_keys (str): List of logical switch WWNs defined on this chassis
    * _project_obj (ProjectObj): The project object this chassis belongs to.
    * _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name):
        self._obj_key = name
        self._flags = 0
        self._switch_keys = []
        self._alerts = []
        self._project_obj = None

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        # When adding a reserved key, don't forget youu may also need to update brcddb.util.copy
        _reserved_keys = {
            '_obj_key': self.r_obj_key(),
            '_flags': self.r_flags(),
            '_alerts': self.r_alert_objects(),
            '_project_obj': self.r_project_obj(),
            '_switch_keys': self.r_switch_keys(),
        }
        try:
            if k == '_reserved_keys':
                rl = list(_reserved_keys.keys())
                rl.append('_reserved_keys')
                return rl
            else:
                return _reserved_keys[k]
        except:
            return None

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
        alertObj = alert_class.AlertObj(tbl, num, key, p0, p1)
        self._alerts.append(alertObj)
        return alertObj

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

    def s_project_obj(self, obj):
        """Set the project object this object belongs to

        :param obj: Project object
        :type obj: brcddb.classes.project.ProjectObj
        """
        self._project_obj = obj

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

        :return: True if VF is enabled. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/vf-enabled')
        return False if v is None else v

    def r_is_vf_supported(self):
        """Tests the virtual fabrics (VF) supported flag ('brocade-chassis/vf-supported')

        :return: True if VF is enabled. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/vf-supported')
        return False if v is None else v

    def r_is_ha_enabled(self):
        """Tests the high availability (HA) enabled flag ('brocade-chassis/ha-enabled')

        :return: True if HA is enabled. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/ha-enabled')
        return False if v is None else v

    def r_is_heartbeat_up(self):
        """Tests the heart beat up flag ('brocade-chassis/heartbeat-up')

        :return: True if the HA heart beat is up. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/heartbeat-up')
        return False if v is None else v

    def r_is_ha_sync(self):
        """Tests the high availability (HA) sync flag ('brocade-chassis/ha-status/ha-synchronized')

        :return: True if in HA sync. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/ha-synchronized')
        return False if v is None else v

    def r_is_extension_enabled(self, slot=0):
        """Tests the virtual fabrics enabled flag ('brocade-fru/blade/extension-enabled')

        :param slot: Slot number of board where the extension flag is to be tested
        :return: True if extension is enabled. Otherwise False
        :rtype: bool
        """
        blades = self.r_get('brocade-fru/blade')
        for blade in blades:
            s = blade.get('slot-number')
            if s is not None and s == slot:
                return blade.get('extension-enabled')
        return False

    def r_is_bladded(self):
        """Tests the virtual fabrics enabled flag ('brocade-fru/blade/extension-enabled')

        :param slot: Slot number of board where the extension flag is to be tested
        :return: True if extension is enabled. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-chassis/chassis/max-blades-supported')
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
        :return: List of SwitchObj
        :rtype: list
        """
        for switch_obj in self.r_switch_objects():
            if switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id') == fid:
                return switch_obj
        return None

    def r_fabric_keys(self):
        """Returns the list of fabric keys associated with switches in this chassis

        :return: List of keys (fabric WWNs)
        :rtype: list
        """
        return [switch_obj.r_fabric_key() for switch_obj in self.r_switch_objects() if
                switch_obj.r_fabric_key() is not None]

    def r_fabric_objects(self):
        """Returns the list of fabric objects associated with switches in this chassis

        :return: List of keys (fabric WWNs)
        :rtype: list
        """
        return [switch_obj.r_fabric_obj() for switch_obj in self.r_switch_objects() if
                switch_obj.r_fabric_obj() is not None]

    def r_login_keys(self):
        """Returns all the login WWNs associated with this chassi. Includes E-Ports

        :return: List of WWNs logged into this port
        :rtype: list
        """
        k = []
        for s in self.r_switch_objects():
            k.extend(s.r_login_keys())
        return k

    def r_login_objects(self):
        """Returns all the login objects for logins in this chassis

        :return: List of LoginObj logged into this port
        :rtype: list
        """
        k = []
        for s in self.r_switch_objects():
            k.extend(s.r_login_objects())
        return k

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this chassis.

        :return: List of FDMI node WWNs associated this chassis
        :rtype: list
        """
        rl = []
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_node_keys())
        return rl

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this chassis

        :return: List of FdmiNodeObj associated with this chassis
        :rtype: list
        """
        rl = []
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_node_objects())
        return rl

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this chassis.

        :return: List of FDMI port WWNs associated this chassis
        :rtype: list
        """
        rl = []
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_port_keys())
        return rl

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this chassis

        :return: List of FdmiPortObj associated with this chassis
        :rtype: list
        """
        rl = []
        for fab_obj in self.r_fabric_objects():
            rl.extend(fab_obj.r_fdmi_port_objects())
        return rl

    def r_fid_list(self):
        """Returns the list of logical fabric ID (FID) in this chassis

        :return: List of FIDs (int)
        :rtype: list
        """
        fid = []
        for switch_obj in self.r_switch_objects():
            tf = switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id')
            if tf is not None:
                fid.append(tf)
        return fid

    def r_slot(self, s):
        """Returns the FRU information for a specific blade 'brocade-fru/blade')

        :return: The blade dictionary for a specific blade as returned from the API
        :rtype: dict
        """
        l = util.convert_to_list(self.util.r_get('brocade-fru/blade'))
        for b in l:
            if isinstance(b.get('slot_number'), int) and b.get('slot_number') == s:
                return b
        return None

    def r_port_keys(self):
        """Returns a list of all ports in this chassis

        :return: List of ports in s/p format
        :rtype: list
        """
        return [v for switchObj in self.r_switch_objects() for v in switchObj.r_port_keys()]

    def r_port_objects(self):
        """Returns a list of port objects for all ports in this chassis

        :return: List of PortObj
        :rtype: list
        """
        return [v for switchObj in self.r_switch_objects() for v in switchObj.r_port_objects()]

    def c_fru_blade_map(self):
        """Sorts brocade-fru/blade into a list that can be indexed by slot number

        :return: List of brocade-fru/blade dict. Note that if no blade installed at a slot, the list entry is None
        :rtype: list
        """
        tl = [None, None, None, None, None, None, None, None, None, None, None, None, None]
        try:
            blade_list = self.r_get('brocade-fru/blade')
            for blade in blade_list:
                tl[blade.get('slot-number')] = blade
        except:
            pass
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
        return util.s_new_key_for_class(self, k, v, f)

    def r_get(self, k):
        """Returns the value for a given key. Keys for nested objects must be seperated with '/'.

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
