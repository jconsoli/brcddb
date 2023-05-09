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
:mod:`brcdd.classes.zone` - Defines the zone classes ZoneCfgObj, ZoneObj, and AliasObj

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 01 Nov 2020   | Changed return in r_zone_configurations() to list rather than generator type.     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 13 Feb 2021   | Improved some method efficiencies                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 17 Jul 2021   | Removed obsolete r_is_wwm(), r_is_di(), and r_is_mixed methods                    |
    |           |               | Added c_members() and c_pmembers() to ZoneObj                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 14 Nov 2021   | Use common util.get_reserved() in r_get_reserved(). Added s_type() to ZoneObj     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 31 Dec 2021   | No functional changes. Replaced bare except with explicit except.                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 04 Sep 2022   | Added r_alert_nums() to ZoneObj and AliasObj                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 01 Jan 2023   | Added rs_key()                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 26 Mar 2023   | Added r_format(). Fixed missing removal of peer members in s_del_member           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 09 May 2023   | Added s_sort_members()                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '09 May 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.1'

import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as util 

# Programmer's Tip: Apparently, .clear() doesn't work on a dereference list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


class ZoneCfgObj:
    """The ZoneCfgObj contains all information relevant to a zone configuration including:
        * 'brocade-fibrechannel-configuration/zone-configuration'

    Attributes:
        _obj_key (str): Name of the zone configuration.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _members (list): List of zone members by zone name
        _fabric_key (str): WWN of fabric this zone configuration belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj, fabric_key):
        self._obj_key = name
        self._flags = 0
        self._members = list()
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
                _members=self.r_members(),
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

    def r_is_effective(self):
        """Determines if this is the effective zone configuration

        :return: True - If this is the effective zone configuration, otherwise False
        :rtype: bool
        """
        name = self.r_obj_key()
        if name == '_effective_zone_cfg':
            return True
        eff_name = self.r_fabric_obj().r_get('brocade-zone/effective-configuration/cfg-name')
        return False if eff_name is None else True if eff_name == name else False

    def s_add_member(self, members):
        """Adds zone members to the zone configuration if the zone is not already a member of the zone configuration

        :param members: Member or members to add
        :type members: list, str, None
        """
        try:
            self._members.extend([mem for mem in util.convert_to_list(members) if mem not in self._members])
        except TypeError:
            return

    def s_del_member(self, members):
        """Deletes zone members from the zone configuration

        :param members: Member
        :type members: str, list
        """
        for mem in util.convert_to_list(members):
            for i, e in reversed(list(enumerate(self._members))):
                if e == mem:
                    self._members.pop(i)
                    break

    def r_members(self):
        """Returns a list of zones in the zone configuration

        :return: Members
        :rtype: list
        """
        return self._members.copy()

    def r_has_member(self, mem):
        """Checks to see if a zone exists in the zone configuration

        :param mem: Zone name
        :type mem: str
        :return: True: zone found. False: zone not found
        :rtype: bool
        """
        return True if mem in self._members else False

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this zone configuration

        :return: Fabric principal switch WWN. None if the fabric switches have not been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this zone configuration

        :return: Fabric object
        :rtype: FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def r_zonecfg_obj(self):
        return self

    def r_zonecfg_key(self):
        return self.r_obj_key()

    def r_zone_objects(self):
        """Returns a list of zone objects in this zone configuration

        :return: List of brcddb.classes.zone.ZoneObj
        :rtype: list
        """
        # I can't think of a way for fab_obj or zone_obj to be None but rather than over think it ...
        fab_obj = self.r_fabric_obj()
        return list() if fab_obj is None else \
            [fab_obj.r_zone_obj(zone) for zone in self.r_members() if fab_obj.r_zone_obj(zone) is not None]

    def s_copy(self, zonecfg):
        """Copy self to a new zone

        :param zonecfg: Name of new alias to create
        :type zonecfg: str
        :return: Zone configuration object. None if zone configuration already exists
        :rtype: brcddb.classes.alert.ZoneCfgObj, None
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj.r_zonecfg_obj(zonecfg) is not None:
            return None
        return fab_obj.s_add_zonecfg(zonecfg, self.r_members())

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

    def r_format(self, full=False):
        """Returns a list of formatted text for the object. Intended for error reporting.

        :param full: If True, expand (pprint) all data added with obj.s_new_key() pprint.
        :type full: bool
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return util.format_obj(self, full=full)

    def s_sort_members(self):
        """Sorts the membership list. This is useful for simple zone configuration comparisons"""
        self._members.sort()


class ZoneObj:
    """The ZoneObj contains all information relevant to a zone including:
        * 'brocade-fibrechannel-configuration/zone-configuration/zone'

    Args:
        name (str): Name of the zone. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): Name of the zone.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _members (list): List of zone members.
        _pmembers (list): List of principal zone members.
        _fabric_key (str): WWN of fabric this zone configuration belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, zone_type, project_obj, fabric_key):
        self._obj_key = name   # Zone name
        self._flags = 0
        self._members = list()  # 'member-entry' - Zone members
        self._pmembers = list()  # 'principal-member-entry' - Principal zone members - for peer zones
        self._alerts = list()
        self._type = zone_type   # Zone type from brocade-zone/brocade-zone (0 default, 1 user peer, 2 target  peer)
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
                _members=self.r_members(),
                _pmembers=self.r_pmembers(),
                _type=self.r_type(),
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

    def r_is_peer(self):
        """Test to determine if zone is a user defined peer zone, 'brocade-zone/zone-type' == 1

        :return: True: zone is a peer zone, FalseL zone is not a peer zone
        :rtype: bool
        """
        zone_type = self.r_type()
        if isinstance(zone_type, int):
            return True if zone_type == brcddb_common.ZONE_USER_PEER else False
        return False

    def r_is_target_driven(self):
        """Test to determine if zone is a target driven peer zone, 'brocade-zone/zone-type' == 2

        :return: True: zone is a peer zone, False zone is not a peer zone
        :rtype: bool
        """
        zone_type = self.r_type()
        if isinstance(zone_type, int):
            return True if zone_type == brcddb_common.ZONE_TARGET_PEER else False
        return False

    def r_is_effective(self):
        """Test to determine if the zone object represents an effective zone

        :return: True: zone object represents an effective zone, False zone object is a defined zone object
        :rtype: bool
        """
        return bool(self._flags & brcddb_common.zone_flag_effective)

    def r_zone_obj(self):
        return self

    def r_zone_key(self):
        return self.r_obj_key()

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this zone

        :return: Fabric principal switch WWN. None if the fabric switches have not been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this zone

        :return: Fabric object
        :rtype: FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def s_add_member(self, members):
        """Adds members to the zone

        :param members: Member
        :type members: str, list
        """
        self._members.extend([mem for mem in util.convert_to_list(members) if mem not in self._members])

    def s_del_member(self, members):
        """Deletes members from the zone
        :param members: Member
        :type members: str, list
        """
        for mem in util.convert_to_list(members):
            for i, e in reversed(list(enumerate(self._members))):
                if e == mem:
                    self._members.pop(i)
                    break
            for i, e in reversed(list(enumerate(self._pmembers))):
                if e == mem:
                    self._pmembers.pop(i)
                    break

    def r_members(self):
        """Returns a list of members in the zone

        :return: Members
        :rtype: list
        """
        return self._members.copy()

    def c_members(self):
        """Same as r_members() but with aliases resolved

        :return: Members
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        rl = list()
        for mem in self._members:
            alias_obj = fab_obj.r_alias_obj(mem)
            if alias_obj is None:
                rl.append(mem)
            else:
                rl.extend(alias_obj.r_members())
        return rl

    def r_has_member(self, mem):
        """Checks to see if a member exists in the zone

        :param mem: Zone member
        :type mem: str
        :return: True: member found. False: member not found
        :rtype: bool
        """
        return True if mem in self._members else False

    def s_add_pmember(self, members):
        """Adds principal members to the zone

        :param members: Member
        :type members: str, list
        """
        self._pmembers.extend([mem for mem in util.convert_to_list(members) if mem not in self._pmembers])

    def s_del_pmember(self, members):
        """Deletes principal members from the zone

        :param members: Member
        :type members: str, list
        """
        for mem in util.convert_to_list(members):
            for i, e in reversed(list(enumerate(self._pmembers))):
                if e == mem:
                    self._pmembers.pop(i)
                    break

    def r_pmembers(self):
        """Returns a list of principal members in the zone

        :return: Members
        :rtype: list
        """
        return self._pmembers.copy()

    def c_pmembers(self):
        """Same as r_pmembers() but with aliases resolved

        :return: Members
        :rtype: list
        """
        fab_obj = self.r_fabric_obj()
        rl = list()
        for mem in self._pmembers:
            alias_obj = fab_obj.r_alias_obj(mem)
            if alias_obj is None:
                rl.append(mem)
            else:
                rl.extend(alias_obj.r_members())
        return rl

    def r_has_pmember(self, mem):
        """Checks to see if a principal member exists in the zone

        :param mem: Principal zone member
        :type mem: str
        :return: True: member found. False: member not found
        :rtype: bool
        """
        return True if mem in self._pmembers else False

    def r_zonecfg_objects(self):
        """Returns the zone configuration objects of defined zone configurations this zone is a member of

        :return: Zone configurations
        :rtype: list
        """
        zone = self.r_obj_key()
        return [z for z in self.r_fabric_obj().r_zonecfg_objects() if z.r_has_member(zone) and
                z.r_obj_key() != '_effective_zone_cfg']

    def r_zone_configurations(self):
        """Returns the names of defined (not effective) zone configuration this zone is a member of.

        :return: Zone configurations
        :rtype: list
        """
        return [obj.r_obj_key() for obj in self.r_zonecfg_objects()]

    def r_type(self):
        """Returns zone type

        :return: Zone type
        :rtype: int
        """
        return self._type

    def s_type(self, zone_type):
        """Set the zone type

        :return: Zone type
        :rtype: int
        """
        self._type = zone_type

    def s_copy(self, zone):
        """Copy self to a new zone

        :param zone: Name of new alias to create
        :type zone: str
        :return: Zone object. None if zone object already exists
        :rtype: brcddb.classes.alert.ZoneObj, None
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj.r_zone_obj(zone) is not None:
            return None
        return fab_obj.s_add_zone(zone, self.r_type(), self.r_members(), self.r_pmembers())

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

        :rtype: list
        """
        return util.class_getkeys(self)

    def r_format(self, full=False):
        """Returns a list of formatted text for the object. Intended for error reporting.

        :param full: If True, expand (pprint) all data added with obj.s_new_key() pprint.
        :type full: bool
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return util.format_obj(self, full=full)

    def s_sort_members(self):
        """Sorts the membership list. This is useful for simple zone configuration comparisons"""
        self._members.sort()
        self._pmembers.sort()


class AliasObj:
    """The AliasObj contains all information relevant to an alias including:
        * 'brocade-fibrechannel-configuration/zone-configuration/alias'

    Args:
        name (str): Name of the alias. Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): Name of the alias.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _members (list): List of WWNs or d,i pairs associated with this alias.
        _fabric_key (str): WWN of fabric this alias belongs to.
        _alerts (list): List of AlertObj objects associated with this object.
    """
    def __init__(self, name, project_obj, fabric_key):
        self._obj_key = name  # Alias name
        self._flags = 0
        self._members = list()  # alias members
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
                _members=self.r_members(),
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

    def s_add_member(self, members):
        """Adds members to the alias

        :param members: Member
        :type members: str, list
        """
        self._members.extend([mem for mem in util.convert_to_list(members) if mem not in self._members])

    def s_del_member(self, members):
        """Deletes members from the alias

        :param members: Member
        :type members: str, list
        """
        for mem in util.convert_to_list(members):
            for i, e in reversed(list(enumerate(self._members))):
                if e == mem:
                    self._members.pop(i)
                    break

    def r_members(self):
        """Returns a list of members in the alias

        :return: Members
        :rtype: list
        """
        return self._members.copy()

    def r_has_member(self, mem):
        """Checks to see if a member exists in the alias

        :param mem: Alias member
        :type mem: str
        :return: True: member found. False: member not found
        :rtype: bool
        """
        return True if mem in self._members else False

    def r_login_obj(self):
        return self

    def r_login_key(self):
        return self.r_obj_key()

    def r_fabric_key(self):
        """Returns the fabric WWN associated with this alias

        :return: Fabric principal switch WWN. None if the switch is offline or the fabric may not have been polled
        :rtype: FabricObj, None
        """
        return self._fabric_key

    def r_fabric_obj(self):
        """Returns the fabric object associated with this alias

        :return: Fabric object. None if the switch is offline or the fabric may not have been polled
        :rtype: brcddb.classes.fabric.FabricObj, None
        """
        try:
            return self.r_project_obj().r_fabric_obj(self.r_fabric_key())
        except AttributeError:
            return None

    def r_zone_objects(self):
        """Returns a list of zone objects where this alias is used

        :return: List of brcddb.classes.zone.ZoneObj
        :rtype: list
        """
        alias = self.r_obj_key()
        return [z for z in self.r_fabric_obj().r_zone_objects() if alias in z.r_members() or alias in z.r_pmembers()]

    def s_copy(self, alias):
        """Copy self to a new alias.

        :param alias: Name of new alias to create
        :type alias: str
        :return: Alert object. None if alert object already exists
        :rtype: brcddb.classes.alert.AlertObj, None
        """
        fab_obj = self.r_fabric_obj()
        if fab_obj.r_alias_obj(alias) is not None:
            return None
        return fab_obj.s_add_alias(alias, self.r_members())

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

    def rs_key(self, k, v):
        """Return the value of a key. If the key doesn't exist, create it with value v

        :param k: Key
        :type k: str, int
        :return: Value
        :rtype: None, int, float, str, list, dict
        """
        return util.get_or_add(self, k, v)

    def r_keys(self):
        """Returns a list of keys added to this object.

        :return: List of keys
        :rtype: list
        """
        return util.class_getkeys(self)

    def r_format(self, full=False):
        """Returns a list of formatted text for the object. Intended for error reporting.

        :param full: If True, expand (pprint) all data added with obj.s_new_key() pprint.
        :type full: bool
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return util.format_obj(self, full=full)

    def s_sort_members(self):
        """Sorts the membership list. This is useful for simple zone configuration comparisons"""
        self._members.sort()
