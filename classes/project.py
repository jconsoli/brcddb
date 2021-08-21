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
:mod:`brcdd.classes.project` - Defines the project object, ProjectObj.

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
    | 3.0.2     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Improved some method effecienceis                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 21 Aug 2021   | Added flag for automatic switch add in s_add_fabric().                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '21 Aug 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as util
import brcddb.classes.chassis as chassis_class
import brcddb.classes.switch as switch_class
import brcddb.classes.fabric as fabric_class
import brcddb.classes.iocp as iocp_class

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this but for now, I took
# the easy way out.


class ProjectObj:
    """This is the primary object of the brcddb library. All other objects are either a member of this class or a member
    of a member in this class

    Args:
        * name (str): This is the key, stored in _obj_key.
        * date (str): Date project was created.

    Attributes:
        * _obj_key (str): For the project object, the key is insignificant. A project name is recommended.
        * _flags (int): Flags for each class are defined in brcddb.brcddb_common
        * _date (str): Date this project was created
        * _python_version (str): Version of Python used to create this object
        * _description (str): Project description
        * _fabric_objs (dict): Dictionary of FabricObj objects. Key is the WWN of the fabric
        * _switch_objs (dict): Dictionary of SwitchObj objects. Key is the WWN of the switch
        * _chassis_objs (dict): Dictionary of ChassisObj objects. Key is the WWN of the chassis
        * _iocp_objs (dict): Dictionary of IOCPObj objects. Key is the CEC serial number
        * _alerts (list): List of AlertObj objects associated with this object.
    """
#    _reserved_keys = ('_reserved_keys', '_obj_key', '_flags', '_date', '_python_version', '_description',
#                      '_fabric_objs', '_switch_objs', '_chassis_objs', '_alerts')

    def __init__(self, name, date):
        self._obj_key = name
        self._flags = 0
        self._date = date
        self._python_version = ''
        self._description = None
        self._fabric_objs = dict()  # fabric objects. Key is principal switch WWN
        self._switch_objs = dict()  # Switch objects. Key is switch WWN
        self._chassis_objs = dict()  # Chassis objects. Key is chassis WWN
        self._iocp_objs = dict()  # IOCP objects. Key is the CEC serial number
        self._alerts = list()

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        # When adding a reserved key, don't forget you may also need to update brcddb.util.copy
        if k is None:
            return None
        _reserved_keys = {
            '_obj_key': self.r_obj_key(),
            '_flags': self.r_flags(),
            '_date': self.r_date(),
            '_python_version': self.r_python_version(),
            '_description': self.r_description(),
            '_fabric_objs': self.r_fabric_objs(),
            '_switch_objs': self.r_switch_objs(),
            '_chassis_objs': self.r_chassis_objs(),
            '_alerts': self.r_alert_objects(),
        }
        if k == '_reserved_keys':
            rl = list(_reserved_keys.keys())
            rl.append('_reserved_keys')
            return rl
        return _reserved_keys.get(k)

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
        """To make it easy for code that wants to get the project object from any object

        :return: Project object
        :rtype: ProjectObj
        """
        return self

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

    def r_is_warn(self):
        """Tests the flags against the project warn flag bit (brcddb_common.project_warn)

        :return: True if the project warn flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self._flags & brcddb_common.project_warn)

    def r_is_api_warn(self):
        """Tests the flags against the project API warn flag bit (brcddb_common.project_api_warn)

        :return: True if the project API warn flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self._flags & brcddb_common.project_api_warn)

    def r_is_user_warn(self):
        """Tests the flags against the project user warn flag bit (brcddb_common.project_user_warn)

        :return: True if the project user warn flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self._flags & brcddb_common.project_user_warn)

    def r_is_any_warn(self):
        """Tests the flags against the project all the warn flag bits

        :return: True if any project warn bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self.r_is_warn() | self.r_is_api_warn() | self.r_is_user_warn())

    def r_is_error(self):
        """Tests the flags against the project error flag bit (brcddb_common.project_error)
        :return: True if the project error flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self.r_flags() & brcddb_common.project_error)

    def r_is_api_error(self):
        """Tests the flags against the project API error flag bit (brcddb_common.project_api_error)

        :return: True if the project API error flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self.r_flags() & brcddb_common.project_api_error)

    def r_is_user_error(self):
        """Tests the flags against the project user error flag bit (brcddb_common.project_user_error)

        :return: True if the project user error flag bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self.r_flags() & brcddb_common.project_user_error)

    def r_is_any_error(self):
        """Tests the flags against the project all the error flag bits

        :return: True if any project warn bit is set. Otherwise False
        :rtype: bool
        """
        return bool(self.r_is_error() | self.r_is_api_error() | self.r_is_user_error())

    def s_warn_flag(self):
        """Sets the project warn bit flag (brcddb_common.project_warn)"""
        self.s_or_flags(brcddb_common.project_warn)

    def s_error_flag(self):
        """Sets the project error bit flag (brcddb_common.project_error)"""
        self.s_or_flags(brcddb_common.project_error)

    def s_api_warn_flag(self):
        """Sets the project warn API bit flag (brcddb_common.project_api_warn)"""
        self.s_or_flags(brcddb_common.project_api_warn)

    def s_api_error_flag(self):
        """Sets the project error API bit flag (brcddb_common.project_api_error)"""
        self.s_or_flags(brcddb_common.project_api_error)

    def s_user_warn_flag(self):
        """Sets the project user warn bit flag (brcddb_common.project_user_warn)"""
        self.s_or_flags(brcddb_common.project_user_warn)

    def s_user_error_flag(self):
        """Sets the project user error bit flag (brcddb_common.project_user_error)"""
        self.s_or_flags(brcddb_common.project_user_error)

    def r_exit_code(self):
        """Returns the exit code status. Priority then user, brcddb, then fos API when there is an error

        :return: Exit code
        :rtype: int
        """
        i = brcddb_common.project_user_error
        while i >= brcddb_common.project_warn:
            if self.r_flags() & i:
                return brcddb_common.exit_code_for_flag[i]
            i >>= 1
        return 0

    def r_exit_msg(self):
        """Returns a user friendly message for the exit code.

        :return: Exit message
        :rtype: str
        """
        return brcddb_common.user_friendly_exit_codes[self.r_exit_code()]

    def r_date(self):
        """Returns the date the project was created.

        :return: Date
        :rtype: str
        """
        return self._date

    def s_python_version(self, version):
        """Sets the Python version number used to create the project

        :param version: Python version number
        :type version: str
        """
        self._python_version = version

    def r_python_version(self):
        """Returns the Python version number used to create the project

        :return: Python version
        :rtype: str
        """
        return self._python_version

    def s_description(self, desc):
        """Sets the description for the project

        :param desc: Description
        :type desc: str
        """
        self._description = desc

    def r_description(self):
        """Returns the project description

        :return: Project description
        :rtype: str
        """
        return self._description

    def c_description(self):
        """Returns the project description. If None, returns ''

        :return: Project description
        :rtype: str
        """
        return '' if self._description is None else self._description

    def s_add_fabric(self, principal_wwn, add_switch=True):
        """Add a faric to the project if the fabric doesn't already exist

        :param principal_wwn: Principal WWN of the fabric
        :type principal_wwn: str
        :return: Fabric object
        :rtype: FabricObj
        """
        fab_obj = self.r_fabric_obj(principal_wwn)
        if fab_obj is None:
            fab_obj = fabric_class.FabricObj(principal_wwn, self, add_switch)
            self._fabric_objs.update({principal_wwn: fab_obj})
        if add_switch:
            self.s_add_switch(principal_wwn).s_fabric_key(principal_wwn)
        return fab_obj

    def s_del_fabric(self, principal_wwn):
        """Delete a fabric from the project

        :param principal_wwn: Fabric key (principal WWN) to be deleted
        :type principal_wwn: str
        """
        self._fabric_objs.pop(principal_wwn, None)

    def r_fabric_obj(self, key):  # key is the fabric principal WWNs
        """Returns the fabric object for a certain fabric

        :param key: Principal WWN of the fabric
        :type key: str
        :return: Fabric object
        :rtype: FabricObj, None
        """
        return self._fabric_objs.get(key)

    def r_fabric_keys(self):
        """Returns the list of fabric keys (principal fabric switch WWN) added to this project

        :return: Fabric WWN list
        :rtype: list
        """
        return list(self._fabric_objs.keys())

    def r_fabric_objects(self):
        """Returns the list of fabric objects added to this project

        :return: List of FabricObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._fabric_objs.values())

    def r_fabric_objs(self):
        """Returns the dictionary of fabric objects. Typically only used by the brcddb libraries

        :return: Dictionary of fabric objects
        :rtype: dict
        """
        return self._fabric_objs

    def r_fabric_objs_for_fid(self, fid):
        """Returns a list of fabric objects associated with a FID

        :param fid: Fabric ID
        :type fid: int
        :return: Dictionary of fabric objects
        :rtype: dict
        """
        k = 'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id'
        return [obj.r_fabric_obj() for obj in self.r_switch_objects() if obj.r_get(k) == fid]

    def r_login_keys(self):
        """Returns the list of login keys added to the fabrics in this project

        :return: List of WWNs
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_login_keys())
        return v

    def r_login_objects(self):
        """Returns the list of login objects added to the fabrics in this project

        :return: List of LoginObj
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_login_objects())
        return v

    def r_fdmi_node_keys(self):
        """Returns all the FDMI node WWNs associated with this project.

        :return: List of FDMI node WWNs associated this project
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_fdmi_node_keys())
        return v

    def r_fdmi_node_objects(self):
        """Returns all the FDMI node objects for logins associated with this project

        :return: List of FdmiNodeObj associated with this project
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_fdmi_node_objects())
        return v

    def r_fdmi_port_keys(self):
        """Returns all the FDMI port WWNs associated with this project.

        :return: List of FDMI port WWNs associated this project
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_fdmi_port_keys())
        return v

    def r_fdmi_port_objects(self):
        """Returns all the FDMI port objects for logins associated with this project

        :return: List of FdmiPortObj associated with this project
        :rtype: list
        """
        v = list()
        for fab_obj in self.r_fabric_objects():
            v.extend(fab_obj.r_fdmi_port_objects())
        return v

    def s_add_switch(self, wwn):
        """Add a switch to the project if the switch doesn't already exist

        :param wwn: Switch WWN
        :type wwn: str
        :return: Switch object
        :rtype: SwitchObj
        """
        switch_obj = self.r_switch_obj(wwn)
        if switch_obj is None:
            switch_obj = switch_class.SwitchObj(wwn, self)
            self._switch_objs.update({wwn: switch_obj})
        return switch_obj

    def r_switch_obj(self, key):  # key is the switch WWN
        """Returns the switch object for a given switch WWN
        
        :param key: Switch WWN
        :type key: str
        :return: Switch object
        :rtype: SwitchObj, None
        """
        return self._switch_objs.get(key)

    def r_switch_keys(self):
        """Returns the list of switch WWNs of switches added to this project

        :return: List of switch WWNs
        :rtype: list
        """
        return list(self._switch_objs.keys())

    def r_switch_objects(self):
        """Returns the list of switch objects added to this project

        :return: List of SwitchObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._switch_objs.values())

    def r_switch_objs(self):
        """Returns the dictionary of switch objects. Typically only used by the brcddb libraries

        :return: Dictionary of switch objects
        :rtype: dict
        """
        return self._switch_objs

    def s_add_chassis(self, wwn):
        """Add a chassis to the project if the chassis doesn't already exist

        :param wwn: Chassis WWN
        :type wwn: str
        :return: Chassis object
        :rtype: ChassisObj
        """
        chassis_obj = self.r_chassis_obj(wwn)
        if chassis_obj is None:
            chassis_obj = chassis_class.ChassisObj(wwn, self)
            self._chassis_objs.update({wwn : chassis_obj})
        return chassis_obj

    def r_chassis_obj(self, key):  # key is the chassis WWN
        """Returns the chassis object for a given chassis key
        
        :param key: Chassis WWN
        :type key: str
        :return: Chassis object matching the key. None if not found
        :rtype: ChassisObj, None
        """
        return self._chassis_objs[key] if key in self._chassis_objs else None

    def r_chassis_keys(self):
        """Returns the WWNs for all the chassis in this project

        :return: List of chassis WWNs
        :rtype: list
        """
        return list(self._chassis_objs.keys())

    def r_chassis_objects(self):
        """Returns the chassis objects for the chassis in this project

        :return: List of ChassisObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._chassis_objs.values())

    def r_chassis_objs(self):
        """Returns the dictionary of chassis objects. Typically only used by the brcddb libraries

        :return: Dictionary of chassis objects
        :rtype: dict
        """
        return self._chassis_objs

    def r_port_keys(self):
        """Returns a list of all ports in this project

        :return: List of ports in s/p format
        :rtype: list
        """
        return [v for switch_obj in self.r_switch_objects() for v in switch_obj.r_port_keys()]

    def r_port_objects(self):
        """Returns a list of port objects for all ports in this project

        :return: List of PortObj
        :rtype: list
        """
        return [v for switch_obj in self.r_switch_objects() for v in switch_obj.r_port_objects()]

    def r_project_key(self):
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

    def s_add_iocp(self, cec_sn):
        """Add an IOCP to the project if the IOCP doesn't already exist

        :param cec_sn CEC serial number
        :type cec_sn: str
        :return: IOCP object
        :rtype: brcddb.classes.iocp.IOCPObj
        """
        iocp_obj = self.r_iocp_obj(cec_sn)
        if iocp_obj is None:
            iocp_obj = iocp_class.IOCPObj(cec_sn, self)
            self._iocp_objs.update({cec_sn: iocp_obj})
        return iocp_obj

    def r_iocp_obj(self, key):
        """Returns the IOCP object for a given CEC serial number

        :param key: CEC serial number
        :type key: str
        :return: IOCP object
        :rtype: brcddb.classes.iocp.IOCPObj, None
        """
        return self._iocp_objs.get(key)

    def r_iocp_keys(self):
        """Returns the list of CEC serial numbers for IOCPs added to this project

        :return: List of CEC serial numbers
        :rtype: list
        """
        return list(self._iocp_objs.keys())

    def r_iocp_objects(self):
        """Returns the list of IOCP objects added to this project

        :return: List of brcddb.classes.iocp.IOCPObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._iocp_objs.values())

    def r_iocp_objs(self):
        """Returns the dictionary of IOCP objects. Typically only used by the brcddb libraries

        :return: Dictionary of IOCP objects
        :rtype: dict
        """
        return self._iocp_objs

