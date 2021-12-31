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
:mod:`brcdd.classes.login` - Defines the login objects LoginObj, FdmiNodeObj, and FdmiPortObj.

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
    | 3.0.3     | 13 Feb 2021   | Improved some method efficiencies                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2021   | Use common util.get_reserved() in r_get_reserved()                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2021   | No functional changes. Replaced bare except with explicit except.                 |
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

import brcddb.classes.alert as alert_class
import brcddb.classes.util as util


class LoginObj:
    """The LoginObj contains all information relevant to a login including:
        * brocade-name-server/fibrechannel-name-server'

    Args:
        name (str): WWN (adjacent port) of the login. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): Fabric (name server) login WWN
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _fabric_key (str): WWN of fabric associated with this login
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj, fabric_key):
        self._obj_key = name
        self._flags = 0
        self._alerts = list()
        self._fabric_key = fabric_key
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _fabric_key=self.r_fabric_key(),
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

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this login

        :return: Fabric principal switch WWN. None if the fabric switches have not been polled
        :rtype: str, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this login

        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def r_port_obj(self):
        """Returns the port object associated with this login

        **Must call brcddb.util.util.build_login_port_map() before using this method**
        :return: Port object. None if the switch is offline or the fabric may not have been polled
        :rtype: PortObj, None
        """
        try:
            return self.r_fabric_obj().r_port_obj(self.r_obj_key())
        except AttributeError:
            return None

    def r_switch_obj(self):
        """Returns the switch object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Switch object. None if the switch is offline or the fabric may not have been polled
        :rtype: SwitchObj, None
        """
        port_obj = self.r_port_obj()
        return None if port_obj is None else port_obj.r_switch_obj()

    def r_chassis_obj(self):
        """Returns the chassis object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Switch object. None if the switch is offline or the fabric may not have been polled
        :rtype: SwitchObj, None
        """
        port_obj = self.r_port_obj()
        return None if port_obj is None else port_obj.r_chassis_obj()

    def r_login_obj(self):
        return self

    def r_login_key(self):
        return self.r_obj_key()

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

    def r_is_share_area(self):
        """Tests the flags against the shared area flag bit ('brocade-name-server/share-area')

        :return: True shared == 'yes'. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/share-area')
        return False if v is None else True if v == 'yes' else False

    def r_is_frame_redirection(self):
        """Tests the flags against the frame redirection flag bit ('brocade-name-server/frame-redirection')

        :return: True frame-redirection == 'yes'. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/frame-redirection')
        return False if v is None else True if v == 'yes' else False

    def r_is_partial(self):
        """Tests the flags against the partial login (login incomplete) flag bit ('brocade-name-server/partial')

        :return: True partial == 'yes'. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/partial')
        return False if v is None else True if v == 'yes' else False

    def r_is_lsan(self):
        """Tests the flags against the LSAN flag bit ('brocade-name-server/lsan')

        :return: True lsan == 'yes'. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/lsan')
        return False if v is None else True if v == 'yes' else False

    def r_is_cascaded_ag(self):
        """Tests the flags against the cascaded access gateway flag bit, 'brocade-name-server/frame-redirection'

        :return: True if cascaded through an access gateway. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/frame-redirection')
        return False if v is None else True if v == 'yes' else False

    def r_is_connected_through_ag(self):
        """Tests the flags against the connected through AG flag bit, 'brocade-name-server/cascaded-ag'

        :return: True if connected through access gateway. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/cascaded-ag')
        return False if v is None else True if v == 'yes' else False

    def r_is_device_behind_ag(self):
        """Tests the flags against the device behind AG flag bit, 'brocade-name-server/real-device-behind-ag'

        :return: True if this login is for a device behind an access gateway. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/real-device-behind-ag')
        return False if v is None else True if v == 'yes' else False

    def r_is_fcoe_device(self):
        """Tests the flags against the LSAN flag bit, 'brocade-name-server/fcoe-device'

        :return: True if the LSAN flag bit is set. Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/fcoe-device')
        return False if v is None else True if v == 'yes' else False

    def r_is_sddq(self):
        """Tests the flags against the SDDQ flag bit, 'brocade-name-server/slow-drain-device-quarantine'

        :return: True if this login is in the slow drain device quarantine (SDDQ). Otherwise False
        :rtype: bool
        """
        v = self.r_get('brocade-name-server/slow-drain-device-quarantine')
        return False if v is None else True if v == 'yes' else False

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


class FdmiNodeObj:
    """The FdmiNodeObj contains all information relevant to the node FDMI including:
        * 'brocade-fdmi/hba'

    Args:
        name (str): Base WWN (HBA node) of the login. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): Base WWN (HBA node) of the login.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _fabric_key (str): WWN of the fabric this HBA belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj, fabric_key):
        self._obj_key = name
        self._flags = 0
        self._alerts = list()
        self._fabric_key = fabric_key
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

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
                _fabric_key=self.r_fabric_key(),
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

    def r_is_boot_bios_enabled(self):
        """Converted brocade-fdmi/hba/boot-bios-enabled to a bool

        :return: Project object
        :rtype: ProjectObj
        """
        v = self.r_get('brocade-fdmi/hba/boot-bios-enabled')
        return False if v is None else bool(v)

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this login

        :return: Fabric principal switch WWN. None if the fabric switches have not been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this login

        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def r_switch_obj(self):
        """Returns the switch object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Switch object. None if the switch is offline or the fabric may not have been polled
        :rtype: SwitchObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key()).r_switch_obj(self.r_obj_key())
        except AttributeError:
            return None

    def r_port_obj(self):
        """Returns the port object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Port object. None if the switch is offline or the fabric may not have been polled
        :rtype: PortObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key()).r_port_obj(self.r_obj_key())
        except AttributeError:
            return None

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


class FdmiPortObj:
    """The FdmiPortObj contains all information relevant to the port FDMI including:
        * 'brocade-fdmi/port'

    Args:
        name (str): WWN of the login. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): WWN of the login.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _fabric_key (str): WWN of the fabric this login belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj, fabric_key):
        self._obj_key = name
        self._flags = 0
        self._alerts = list()
        self._fabric_key = fabric_key
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _fabric_key=self.r_fabric_key(),
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

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this login

        :return: Fabric principal switch WWN. None if the fabric switches have not been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this login
        
        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def r_switch_obj(self):
        """Returns the switch object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Switch object. None if the switch is offline or the fabric may not have been polled
        :rtype: SwitchObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key()).r_switch_obj(self.r_obj_key())
        except AttributeError:
            return None

    def r_port_obj(self):
        """Returns the port object associated with this login

        **Must call brcddb.util.util.login_to_port_map() before using this method**
        :return: Port object. None if the switch is offline or the fabric may not have been polled
        :rtype: PortObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key()).r_port_obj(self.r_obj_key())
        except AttributeError:
            return None

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
