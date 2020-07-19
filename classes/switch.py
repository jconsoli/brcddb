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
:mod:`brcdd.classes.switch` - Defines the switch object, SwitchObj.

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

import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as util 
import brcddb.classes.port as port_class

# Programmer's Tip: Apparently, .clear() doesn't work on dereferenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revist this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.

class SwitchObj:
    """The SwitchObj contains all information relevant to a switch including:
        * 'logical-switch/fibrechannel-logical-switch'
        * 'switch/fibrechannel-switch'

    Args:
        * name (str): WWN of the switch. Stored in _obj_key and key in ProjectObj

    Attributes:
        * _obj_key (str): WWN of the switch.
        * _flags (int): Flags for each class are defined in brcddb.brcddb_common
        * _project_obj (ProjectObj): The project object this fabric belongs to.
        * _port_objs (dict): Dictionary of ports in this switch. Key: s/p, Value: PortObj
        * _ge_port_objs (dict): Dictionary of GE ports in this switch. Key: s/p, Value: PortObj
        * _fabric_key (str): WWN of the fabric this port belongs to.
        * _chassis_key (str): WWN of the chassi this port belongs to.
        * _alerts (list): List of AlertObj objects associated with this object.
        * _maps_rules (dict): Key is active rule name. Value is dict from brocade-maps/rule
        * _maps_group_rules (dict): Key is active group name. Value is list of active rules associated with the group
        * _maps_groups (dict): Key is group name. Value is dict from brocade-maps/group
    """

    def __init__(self,name):
        self._obj_key = name
        self._flags = 0
        self._chassis_key = ''
        self._fabric_key = None
        self._port_objs = {}
        self._ge_port_objs = {}
        self._alerts = []
        self._project_obj = None
        self._maps_rules = {}
        self._maps_group_rules = {}
        self._maps_groups = {}

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
            '_port_objs': self.r_port_objs(),
            '_ge_port_objs': self.r_ge_port_objs(),
            '_fabric_key': self.r_fabric_key(),
            '_chassis_key': self.r_chassis_key(),
            '_maps_rules': self.r_maps_rules(),
            '_maps_group_rules': self.r_maps_group_rules(),
            '_maps_groups': self.r_maps_groups(),
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
        :rtype: brcddb.classes.alert.AlertObj
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

    def s_polled_flag(self):
        """Set the switch polled flag, 'fabric/fabric-switch' requested"""
        self.s_or_flags(brcddb_common.switch_flag_polled)

    def s_fab_polled(self):
        """Set the switch polled flag, 'fabric/fabric-switch' requested"""
        self.s_or_flags(brcddb_common.switch_flag_fab_polled)

    def s_chassis_key(self, k):
        self._chassis_key = k

    def r_chassis_key(self):
        """Returns the chassis key this switch belongs to

        :return: Login spped
        :rtype: str
        """
        return self._chassis_key

    def r_chassis_obj(self):
        """Returns the chassis object this switch belongs to

        :return: Login spped
        :rtype: str
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

        :return: True: Switch is the fabric principal switch. False: Switch is not the fabric principal switch
        :rtype: bool
        """
        return bool(self.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/base-switch-enabled'))

    def r_is_enabled(self):
        """Determines if a switch is enabled

        :return: True if enabled, False if not enabled or unknown
        :rtype: bool
        """
        return bool(self.r_get('brocade-fibrechannel-switch/fibrechannel-switch/is-enabled-state'))

    def r_is_principal(self):
        """Test to determine is switch is the principal switch in the fabric

        :return: True: Switch is the fabric principal switch. False: Switch is not the fabric principal switch
        :rtype: bool
        """
        return bool(self.r_get('brocade-fabric/fabric-switch/principal'))

    def r_is_xisl(self):
        """Test to determine is logical ISLs is enabled in the switch, 'fibrechannel-switch/logical-isl-enabled'

        :return: True: Switch is the fabric principal switch. False: Switch is not the fabric principal switch
        :rtype: bool
        """
        return self.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/logical-isl-enabled')

    def r_is_hif(self):
        """Test to determine if High Integrity Fabric (HIF) is enabled

        :return: True: Switch is configured for FICON. False: Switch is not configured for FICON
        :rtype: bool
        """
        return bool(self.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/ficon-mode-enabled'))

    def r_is_default(self):
        """Test to determine if switch is the default switch, 'fibrechannel-switch/default-switch-status'

        :return: True: Switch is the default switch. False: Switch is not the default switch
        :rtype: bool
        """
        return bool(self.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/default-switch-status'))

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
        try:
            return self._fabric_key
        except:
            return None

    def r_fabric_obj(self):
        """Returns the fabric object associated with this switch

        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        projObj = self.r_project_obj()
        # The switch is not in a fabric if the switch is offline of fabric information wasn't polled
        return None if self._fabric_key is None else projObj.r_fabric_obj(self._fabric_key)

    def s_add_port(self, port):
        """Add a port to the switch

        :param port: Port in s/p notation
        :type port: str
        :return: Port object
        :rtype: PortObj
        """
        portObj = self.r_port_obj(port)
        if portObj is None:
            portObj = port_class.PortObj(port)
            self._port_objs.update({port : portObj})
            portObj._switch = self._obj_key
            portObj.s_project_obj(self.r_project_obj())
        return portObj

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
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so allways process dict_values as a list
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
        """
        return self._port_objs[k] if k in self._port_objs else None

    def s_add_ge_port(self, port):
        """Add a GE port to the switch

        :param port: Port in s/p notation
        :type port: str
        :return: Port object
        :rtype: PortObj
        """
        portObj = self.r_ge_port_obj(port)
        if portObj is None:
            portObj = port_class.PortObj(port)
            self._ge_port_objs.update({port : portObj})
            portObj._switch = self._obj_key
            portObj.s_project_obj(self.r_project_obj())
        return portObj

    def r_ge_port_keys(self):
        """Returns a list of all GE ports in this switch

        :return: List of ports in s/p format
        :rtype: list
        """
        return list(self._ge_port_objs.keys())

    def r_ge_port_objects(self):
        """Returns a list of port objects for all ports in this switch

        :return: List of PortObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so allways process dict_values as a list
        return list(self._ge_port_objs.values())

    def r_ge_port_objs(self):
        """Returns the dictionary of port objects. Typically only used by the brcddb libraries

        :return: Dictionary of port objects
        :rtype: dict
        """
        return self._ge_port_objs

    def r_ge_port_obj(self, k):
        """Returns the port object for a port

        :param k: Port name in s/p notation
        :type k: str
        """
        return self._ge_port_objs[k] if k in self._ge_port_objs else None

    def r_login_keys(self):
        """Returns all the login WWNs associated with this switch. Includes E-Ports

        :return: List of WWNs logged into this switch
        :rtype: list
        """
        k = []
        for p in self.r_port_objects():
            k.extend(p.r_login_keys())
        return k

    def r_login_objects(self):
        """Returns all the login objects for logins on this switch

        :return: List of LoginObj logged into this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return []
        return [fab_obj.r_login_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_login_obj(wwn) is not None]

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this switch.

        :return: List of FDMI node WWNs associated this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return []
        fdmi_keys = fab_obj.r_fdmi_node_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this switch

        :return: List of FdmiNodeObj associated with this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return []
        return [fab_obj.r_fdmi_node_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_node_obj(wwn) is not None]

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this switch.

        :return: List of FDMI port WWNs associated this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return []
        fdmi_keys = fab_obj.r_fdmi_port_keys()
        return [wwn for wwn in self.r_login_keys() if wwn in fdmi_keys]

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this switch

        :return: List of FdmiPortObj associated with this switch
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj is None:
            return []
        return [fab_obj.r_fdmi_port_obj(wwn) for wwn in self.r_login_keys() if fab_obj.r_fdmi_port_obj(wwn) is not None]

    def r_port_object_for_index(self, i):
        """Returns the port object matching a port index

        :param i: Port index
        :type i: int
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        if isinstance(i, int):
            for port_obj in self.r_port_objects():
                if  port_obj.r_get('fibrechannel/default-index') == i:
                    return port_obj
        return None

    def r_port_obj_for_pid(self, pid):
        """Returns the port object matching an FC address

        :param pid: Port ID (fibre channel address)
        :type pid: str
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        if isinstance(pid, str):
            for port_obj in self.r_port_objects():
                if  port_obj.r_get('fibrechannel/fcid-hex') == pid:
                    return port_obj
        return None

    def c_trunk_map(self):
        """Returns the trunk groups for this switch in a map as a list of the following dictionary:

        {dswwn: {group_number: [[src_port_obj, dest_port_obj], [src_port_obj, dest_port_obj], ...]}}
        :return: List of dict as defined above
        :rtype: list
        """
        proj_obj = self.r_project_obj()
        ret = {}
        gdm = {}  # Master: key is group number. Value is [source PortObj, dest SwitchObj, dest PortObj] of trunk master
        gds = {}  # key is group numner. Value is list of [source PortObj, dest PortObj] of trunk members
        for td in util.convert_to_list(self.r_get('brocade-fibrechannel-trunk/trunk')):
            ds_wwn = td.get('neighbor-wwn')
            if ds_wwn not in ret:
                ret.update({ds_wwn: {}})
            g = ret.get(ds_wwn)
            group = td.get('group')
            if group not in g:
                g.update({group: []})
            l = g.get(group)
            li = [self.r_port_object_for_index(td.get('source-port')),
                   proj_obj.r_switch_obj(ds_wwn).r_port_object_for_index(td.get('destination-port'))]
            if len(l) == 0 or not td.get('master'):
                l.append(li)
            else:
                l.insert(0, li)
        return ret

    def r_active_maps_policy(self):
        """Returns the active MAPS policy associated with this switch

        :return: Active MAPS. None if no active MAPS policy
        :rtype: dict, None
        """
        for obj in util.convert_to_list(self.r_get('brocade-maps/maps-policy')):
            if obj.get('is-active-policy'):
                return obj
        return None

    def s_add_group(self, group):
        """Adds a group to _maps_group_rules

        :param name: Group name
        :type name: str
        :param group: Dictionary of group attributes as returned from brocade-maps/group
        :type group: dict
        """
        name = group.get('name')
        if name not in self._maps_groups:
            self._maps_groups.update({name: group})

    def r_maps_rules(self):
        """Returns the maps rules

        :return: Dictionary of rule attributes as returned from brocade-maps/rule
        :type: dict
        """
        return self._maps_rules

    def s_add_rule(self, rule):
        """Adds a rule _maps_rules and adds the rule to _maps_group_rules

        :param name: Rule name
        :type name: str
        :param rule: Dictionary of rule attributes as returned from brocade-maps/rule
        :type rule: dict
        """
        name = rule.get('name')
        if name not in self._maps_rules:
            self._maps_rules.update({name: rule})
            group = rule.get('group-name')
            if group not in self._maps_group_rules:
                self._maps_group_rules.update({group: []})
            self._maps_group_rules.get(group).append(name)

    def r_rule(self, name):
        """Returns the rule dict for the rule

        :param name: Rule name
        :type name: str
        :return: Dictionary of rule attributes as returned from brocade-maps/rule
        :type: dict
        """
        return self._maps_rules.get(name)

    def r_maps_group_rules(self):
        """Adds a group to _maps_group_rules

        :param group: Dictionary of group attributes as returned from brocade-maps/group
        :type group: dict
        """
        return self._maps_group_rules

    def r_rule_objects_for_group(self, name):
        """Returns a list of the rule dictionaries associated with a group

        :param name: Group name
        :type name: str
        :return: List of rule attribute dictionaries as returned from brocade-maps/rule associated with the group
        :type: list
        """
        return [self.r_rule(rule) for rule in self.r_maps_group_rules().get(name) if rule is not None]

    def r_maps_groups(self):
        """Returns the maps groups

        :return: Dictionary of group attributes as returned from brocade-maps/group
        :type: dict
        """
        return self._maps_groups

    def r_group(self, name):
        """Returns the group dict for the group

        :param name: Group name
        :type name: str
        :return: Dictionary of group attributes as returned from brocade-maps/group
        :type: dict
        """
        return self.r_maps_groups().get(name)

    def r_active_groups(self):
        """Returns the list of group names in the active MAPS policy

        :return: List of group names
        :type rule: dict
        """
        return list(self.r_maps_group_rules().keys())

    def r_active_group_objects(self):
        """Returns the list of group objects in the active MAPS policy

        :return: List of group objects
        :type rule: dict
        """
        return [self.r_group(name) for name in self.r_active_groups()]

    def c_switch_model(self):
        """Returns the switch model as an integer

        :return: Switch model as an integer
        :type rule: int
        """
        try:
            return int(float(self.r_get('brocade-fibrechannel-switch/fibrechannel-switch/model')))
        except:
            return 0

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
