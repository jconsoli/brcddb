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
:mod:`brcdd.classes.fabric` - Defines the fabric object, FabricObj.

Special Note::

    A login object is created for every WWN that registers with the name server. E-Ports do not register with the name
    server but SIM ports and AMP trunk master does register with the name server and therefore will have a login object.
    The 'port-properties' will be 'SIM Port' for a SIM port and 'I/O Analytics Port' for an AMP trunk master. The other
    AMP trunk members of the trunk register with the name server but 'port-properties' is not present. I'm sure there
    is some way to determine this case but it being such a rare scenario, no code was added to make this determiniation.

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
    | 3.0.2     | 22 Jan 2021   | Fixed potential mutable list in s_add_zonecfg(), s_add_eff_zonecfg(),             |
    |           |               | s_add_zone(), s_add_eff_zone, and s_add_alias()                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Improved some method effecienceis                                                 |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 17 Jul 2021   | Added r_eff_di_zones_for_addr() and r_zones_for_di()                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 14 Aug 2021   | Added s_del_eff_zonecfg()                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 21 Aug 2021   | Bug in r_defined_eff_zonecfg_obj(). Added add_switch flag to __init__             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '21 Aug 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import brcddb.brcddb_common as brcddb_common
import brcddb.classes.alert as alert_class
import brcddb.classes.util as util
import brcddb.classes.zone as zone_class
import brcddb.classes.login as login_class

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revisit this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


class FabricObj:
    """The FabricObj contains all information relevant to a fabric including:
        * 'fabric/fabric-switch'
        * brcddb.classes.zone.ZoneCfgObj
        * brcddb.classes.zone.ZoneObj
        * brcddb.classes.zone.AliasObj
        * brcddb.classes.login.LoginObj
        * brcddb.classes.login.FdmiNodeObj
        * brcddb.classes.login.FdmiPortObj

    Args:
        name (str): WWN of the fabric (principal switch WWN). Stored in _obj_key and key in ProjectObj

    Attributes:
        _obj_key (str): WWN of the fabric.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _switch_keys (str): List of logical switch WWNs in this fabric
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _login_objs (dict): Logins for this fabric. Key: login WWN, value: LoginObj.
        _zonecfg_objs (dict): Defined zone configurations. Key: Zone configuration name, value: ZoneCfgObj.
        _alias_objs (dict): Defined aliases for this fabric. Key: Alias name, value: AliasObj.
        _zone_objs (dict): Defined zones for this fabric. Key: zone name, value: ZoneObj.
        _eff_zone_objs (dict): Zones in the effective zone configuration. Key: zone name, value: ZoneObj.
        _fdmi_node_objs (dict): FDMI node information. Key: login WWN, value: FdmiNodeObj.
        _fdmi_port_objs (dict): FDMI port information. Key: login WWN, value: FdmiPortObj.
        _alerts (list): List of AlertObj objects associated with this object.
        _base_logins (list): List of base NPIV login WWNs. Filled in my brcddb.util.util.build_login_port_map()
        _port_map (dict): List of base NPIV login WWNs. Filled in my brcddb.util.util.build_login_port_map()
    """

    def __init__(self, name, project_obj, add_switch=True):  # name is the WWN of the fabric principal switch
        self._obj_key = name
        self._flags = 0
        self._switch_keys = [name] if add_switch else list()
        self._login_objs = dict()
        self._zonecfg_objs = dict()
        self._alias_objs = dict()
        self._zone_objs = dict()
        self._eff_zone_objs = dict()
        self._fdmi_node_objs = dict()
        self._fdmi_port_objs = dict()
        self._alerts = list()
        self._project_obj = project_obj
        self._base_logins = list()
        self._port_map = dict()

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        if k is None:
            return None
        # When adding a reserved key, don't forget you may also need to update brcddb.util.copy
        _reserved_keys = dict(
            _obj_key=self.r_obj_key(),
            _flags=self.r_flags(),
            _alerts=self.r_alert_objects(),
            _project_obj=self.r_project_obj(),
            _switch_keys=self.r_switch_keys(),
            _login_objs=self.r_login_objs(),
            _zonecfg_objs=self.r_zonecfg_objs(),
            _alias_objs=self.r_alias_objs(),
            _zone_objs=self.r_zone_objs(),
            _eff_zone_objs=self.r_eff_zone_objs(),
            _fdmi_node_objs=self.r_fdmi_node_objs(),
            _fdmi_port_objs=self.r_fdmi_port_objs(),
            _base_logins=self.r_base_logins(),
            _port_map=self.r_port_map(),
        )
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

    def s_add_switch(self, wwn):
        """Adds a switch to the project if it doesn't already exist and then adds it to fabric if not already added

        :param wwn: WWN of logical switch
        :type wwn: str
        :return: Switch object
        :rtype: brcddb.classes.zone.SwitchObj
        """
        if wwn not in self._switch_keys:
            self._switch_keys.append(wwn)
        switch_obj = self.r_project_obj().s_add_switch(wwn)  # I need the switch_obj to add the fab key
        switch_obj.s_fabric_key(self.r_obj_key())
        return switch_obj

    def s_add_login(self, wwn):
        """Adds a login to the fabric if it doesn't already exist

        :param wwn: WWN of the login
        :type wwn: str
        :return: Login object
        :rtype: LoginObj
        """
        login_obj = self._login_objs.get(wwn)
        if login_obj is None:
            login_obj = login_class.LoginObj(wwn, self.r_project_obj(), self.r_obj_key())
            self._login_objs.update({wwn : login_obj})
        return login_obj

    def s_del_login(self, wwn):
        """Deletes a login

        :param wwn: WWN of the login
        :type wwn: str
        """
        if wwn in self._login_objs:
            del self._login_objs[wwn]

    def r_login_obj(self, wwn):
        """Gets the login object for a given WWN

        :param wwn: WWN of the login
        :type wwn: str
        :return: Login object or None if login doesn't exist
        :rtype: LoginObj, None
        """
        return self._login_objs[wwn] if wwn in self._login_objs else None

    def r_login_keys(self):
        """Returns all the login WWN

        :return: List of WWNs logged into this fabric
        :rtype: list
        """
        return list(self._login_objs.keys())

    def r_login_objects(self):
        """Returns all the login objects

        :return: List of LoginObj logged into this fabric
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._login_objs.values())

    def r_login_objs(self):
        """Returns the dictionary login objects. Typically only used by the brcddb libraries

        :return: Dictionary of login objects
        :rtype: dict
        """
        return self._login_objs

    def s_add_zonecfg(self, name, in_mem=None):
        """Adds a zone configuration to the fabric if it doesn't already exist

        Similarly, zone members will be added if they don't already exist
        :param name: Name of the zone configuration
        :type name: str
        :param in_mem: List of zone members, by name, in this zone configuration
        :type in_mem: str, list, tuple
        :return: Zone configuration object
        :rtype: zone_class.brcddb.classes.zone.ZoneCfgObj
        """
        mem = list() if in_mem is None else in_mem
        zonecfg_obj = self._zonecfg_objs.get(name)
        if zonecfg_obj is None:
            zonecfg_obj = zone_class.ZoneCfgObj(name, self.r_project_obj(), self.r_obj_key())
            self._zonecfg_objs.update({name: zonecfg_obj})
        zonecfg_obj.s_add_member(mem)
        return zonecfg_obj

    def s_del_zonecfg(self, members):
        """Delete zone configurations

        :param members: Name or list of zone configurations to be deleted
        :type members: None, str, list, tuple
        """
        for mem in [m for m in util.convert_to_list(members) if m in self._zonecfg_objs]:
            del self._zonecfg_objs[mem]

    def r_zonecfg_obj(self, name):
        """Returns the zone configuration object for a given zone configuration

        :param name: Name of the zone configuration
        :type name: str
        :return: Zone configuration object. None if not found.
        :rtype: brcddb.classes.zone.ZoneCfgObj, None
        """
        return self._zonecfg_objs.get(name)

    def r_zonecfg_keys(self):
        """Returns a list of zone configurations, by name, in this fabric

        :return: List of zone configuration names
        :rtype: list
        """
        return list(self._zonecfg_objs.keys())

    def r_zonecfg_objects(self):
        """Returns a list of zone configuration objects in this fabric

        :return: List of brcddb.classes.zone.ZoneCfgObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._zonecfg_objs.values())

    def r_zonecfg_objs(self):
        """Returns the dictionary of zone configuraiton objects. Typically only used by the brcddb libraries

        :return: Dictionary of zone configuraiton objects
        :rtype: dict
        """
        return self._zonecfg_objs

    def r_zonecfgs_for_zone(self, zone):
        """Returns all the zone configurations a zone is used in

        :param zone: Zone name
        :type zone: str
        :return: List of zone configuration names where zone is used
        :rtype: list
        """
        return [obj.r_obj_key() for obj in self.r_zonecfg_objects() if zone in obj.r_members()]

    def r_defined_eff_zonecfg_key(self):
        """Returns the defined zone configuration name for the effective zone.

        :return: Zone configuration name for the defined effective zone configuration. None if no effective zone cfg
        :rtype: str, None
        """
        return self.r_get('brocade-zone/effective-configuration/cfg-name')

    def r_defined_eff_zonecfg_obj(self):
        """Returns the defined zone configuration object for the effective zone.

        :return: Zone configuration object for the defined effective zone configuration. None if no effective zone cfg
        :rtype: brcddb.classes.zone.ZoneCfgObj, None
        """
        return None if self.r_defined_eff_zonecfg_key() is None else self.r_zonecfg_obj(self.r_defined_eff_zonecfg_key)

    def s_add_eff_zonecfg(self, in_members=None):
        """Adds a special zone configuration named '_effective_zone_cfg' if it doesn't already exist.

        Similarly, zone members will be added if they don't already exist
        Note that a leading '_' is not a valid zone configuration name in FOS so this is strictly an internal database
        zone configuration. This special zone configuration name makes it easy to isolate from defined zones as while
        using all the same code to mangae the zone configuration. Don't forget that the effective zone configuration
        includes the zones at the time the defined zone was activated which will not be the same as the defined zone
        configuration if the defined zone configuration has since been modified.
        :param members: Names of the zones in the effective zone configuration
        :type members: str, list, tuple, None
        :return: Zone configuration object for the effective zone configuration
        :rtype: brcddb.classes.zone.ZoneCfgObj
        """
        return self.s_add_zonecfg('_effective_zone_cfg', list() if in_members is None else in_members)

    def s_del_eff_zonecfg(self):
        """Deletes '_effective_zone_cfg' if it exists."""
        self.s_del_zonecfg('_effective_zone_cfg')

    def r_eff_zone_cfg_obj(self):
        """Returns the zone configuration object for the effective zone.

        :return: Zone configuration object for the effective zone configuration
        :rtype: brcddb.classes.zone.ZoneCfgObj
        """
        return self.r_zonecfg_obj('_effective_zone_cfg')

    def s_add_zone(self, name, zone_type, in_mem=None, in_pmem=None):
        """Adds a zone to the fabric if it doesn't already exist. See zone in 'zoning/defined-configuration'

        :param name: Zone name
        :type name: str
        :param zone_type: Zone type
        :type zone_type: int
        :param in_mem: Zone members
        :type in_mem: list, str, None
        :param in_pmem: Principal zone members (relevant to peer zones only)
        :type in_pmem: list, str, None
        :return: Zone configuration object for the effective zone configuration
        :rtype: brcddb.classes.zone.ZoneCfgObj
        """
        mem = list() if in_mem is None else in_mem
        pmem = list() if in_pmem is None else in_pmem
        zone_obj = self.r_zone_obj(name)
        if zone_obj is None:
            zone_obj = zone_class.ZoneObj(name, zone_type, self.r_project_obj(), self.r_obj_key())
            self._zone_objs.update({name: zone_obj})
        zone_obj.s_add_member(mem)
        zone_obj.s_add_pmember(pmem)
        return zone_obj

    def r_zones_for_alias(self, alias):
        """Returns all the zones an alias is used in

        :param alias: Alias name
        :type alias: str
        :return: List of zone names that are either members or principal members
        :rtype: list
        """
        return [obj.r_obj_key() for obj in self.r_zone_objects() if alias in obj.r_members() or alias in
                obj.r_pmembers()]

    def r_zones_for_wwn(self, wwn):
        """Returns all the zones, by name, a WWN is used in whether by WWN explicitly or by alias

        :param wwn: WWN
        :type wwn: str
        :return: List of zone names
        :rtype: list
        """
        if wwn is None:
            return list()
        # Below fills l with the zones defined with wwn
        l = [obj.r_obj_key() for obj in self.r_zone_objects() if wwn in obj.r_members() or wwn in obj.r_pmembers()]
        # Below gets all the zones where wwn is in an alias
        for alias in self.r_alias_for_wwn(wwn):
            l.extend(self.r_zones_for_alias(alias))
        return l

    def r_zones_for_di(self, did, p_index):
        """Returns all the d,i zones, by name, for a domain, index pair. Typically only used for FICON

        :param did: Domain ID in decimal
        :type did: str, int
        :param p_index: Port index
        :type p_index: str, int
        :return: List of zone names associated with domain, index of the FC address
        :rtype: list
        """
        if isinstance(did, int) and isinstance(p_index, int):
            di = str(did) + ',' + str(p_index)
            # Below fills l with the zones defined with d,i
            l = [obj.r_obj_key() for obj in self.r_zone_objects() if di in obj.r_members() or di in obj.r_pmembers()]
            # Below gets all the zones where di is in an alias
            for alias in self.r_alias_for_di(did, p_index):
                l.extend(self.r_zones_for_alias(alias))
            return l
        return list()

    def s_add_eff_zone(self, name, zone_type, in_mem=None, in_pmem=None):
        """Adds a zone to the effective configuration if it doesn't already exist.
        Similarly, zone members will be added if they don't already exist
        **To Do** I think there is a bug in here. The effective zone should only change when the zone configuration is
        enabled in the fabric. This is moot for any application not using this database for real time updates.

        :param name: Zone name
        :type name: str
        :param zone_type: Zone type
        :type zone_type: int
        :param in_mem Zone members (this should be WWN)
        :type in_mem: str, list, tuple, None
        :param in_pmem: Principal zone members (this should be WWN). Only relavant to peer zones
        :type in_pmem: str, list, tuple, None
        :return: Zone configuration object for the effective zone configuration
        :rtype: brcddb.classes.zone.ZoneCfgObj
        """
        mem = util.convert_to_list(in_mem)
        pmem = util.convert_to_list(in_pmem)
        zone_obj = self.r_eff_zone_obj(name)
        if zone_obj is None:
            zone_obj = zone_class.ZoneObj(name, zone_type, self.r_project_obj(), self.r_obj_key())
            self._eff_zone_objs.update({name: zone_obj})
        zone_obj.s_or_flags(brcddb_common.zone_flag_effective)
        for member in mem:
            zone_obj.s_add_member(member)
        for member in pmem:
            zone_obj.s_add_pmember(member)
        return zone_obj

    def r_eff_zone_obj(self, name):
        """Returns the effective zone object for a given zone

        :param name: Zone name
        :type name: str
        :return: Zone object None if not found.
        :rtype: brcddb.classes.zone.ZoneObj, None
        """
        return self._eff_zone_objs.get(name)

    def r_eff_zone_objs(self):
        """Returns the effective zone object list. Typically used for internal purposes only

        :return: Zone object
        :rtype: brcddb.classes.zone.ZoneObj
        """
        return self._eff_zone_objs

    def r_eff_zone_keys(self):
        """Returns a list of all the zone names in the effective zone configuration

        :return: List of zone names
        :rtype: list
        """
        return list(self._eff_zone_objs.keys())

    def r_eff_zone_objects(self):
        """Returns a list of all the zone objects in the effective zone configuration

        :return: List of brcddb.classes.zone.ZoneObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._eff_zone_objs.values())

    def r_eff_zone_objects_for_wwn(self, wwn):
        """Returns all the zone objects a WWN is used in in the effective zone configuration

        :param wwn: WWN
        :type wwn: str
        :return: List of zone objects, brcddb.classes.zone.ZoneObj
        :rtype: list
        """
        ret_list = list()
        for zone_obj in self.r_eff_zone_objects():
            if wwn in zone_obj.r_members() or wwn in zone_obj.r_pmembers():
                ret_list.append(zone_obj)
        return ret_list

    def r_eff_zones_for_wwn(self, wwn):
        """Returns all the zones, by name, a WWN is used in in the effective zone configuration

        :param wwn: WWN
        :type wwn: str
        :return: List of zone names
        :rtype: list
        """
        return [zone_obj.r_obj_key() for zone_obj in self.r_eff_zone_objects_for_wwn(wwn)]

    def r_eff_di_zones_for_addr(self, addr):
        return list()  # WIP

    def s_del_zone(self, members):
        """Deletes zones by name

        :param members: Zone name or list of zone names to be deleted
        :type members: None, str, list, tuple
        """
        for mem in [m for m in util.convert_to_list(members) if m in self._zone_objs]:
            del self._zone_objs[mem]

    def r_zone_obj(self, name):
        """Returns a zone object for a given zone

        :param name: Zone name
        :type name: str
        :return: Zone object None if not found.
        :rtype: brcddb.classes.zone.ZoneObj, None
        """
        return self._zone_objs.get(name)

    def r_zone_keys(self):
        """Returns all the defined zones in the fabric
        :return: List of zone names
        :rtype: list
        """
        return list(self._zone_objs.keys())

    def r_zone_objects(self):
        """Returns all the zone objects for the defined zones in the fabric

        :return: List of brcddb.classes.zone.ZoneObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._zone_objs.values())

    def r_zone_objs(self):
        """Returns the dictionary of zone objects. Typically only used by the brcddb libraries

        :return: Dictionary of zone objects
        :rtype: dict
        """
        return self._zone_objs

    def s_add_alias(self, name, in_mem=None):
        """Adds an alias to the fabric if it doesn't already exist.
        Similarly, alias members will be added if they don't already exist
        Typically, and best practice, there is one WWN member per alias. Multiples are allowed. I've seen it done on
        occasion but don't recommend it. I've never seen it done, but d,i members are allowed

        :param name: Alias name
        :type name: str
        :param in_mem: Alias members
        :type in_mem: str, list, tuple, None
        :return: Zone configuration object for the effective zone configuration
        :rtype: brcddb.classes.zone.ZoneCfgObj
        """
        mem = util.convert_to_list(in_mem)
        if name in self._alias_objs:
            alias_obj = self._alias_objs[name]
        else:
            alias_obj = zone_class.AliasObj(name, self.r_project_obj(), self.r_obj_key())
            self._alias_objs.update({name: alias_obj})
        # No one should try to add the same member twice, but just in case
        alias_obj.s_add_member([wwn for wwn in mem if wwn not in alias_obj.r_members()])
        return alias_obj

    def s_del_alias(self, members):
        """Delete an alias or list of aliases

        :param members: Name or list of the aliases to be deleted
        :type members: None, str, list, tuple
        """
        for mem in [m for m in util.convert_to_list(members) if m in self._alias_objs]:
            del self._alias_objs[mem]

    def r_alias_obj(self, name):
        """Returns the alias object for a given alias

        :param name: Alias name
        :type name: str
        :return: Alias object. None if not found.
        :rtype: brcddb.classes.zone.AliasObj, None
        """
        return self._alias_objs.get(name)

    def r_alias_keys(self):
        """Returns the list of aliases defined in the fabric

        :return: List of aliases by name
        :rtype: list
        """
        return list(self._alias_objs.keys())

    def r_alias_objects(self):
        """Returns the list of alias objects defined in the fabric

        :return: List of brcddb.classes.zone.AliasObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._alias_objs.values())

    def r_alias_objs(self):
        """Returns the dictionary of alias objects. Typically only used by the brcddb libraries

        :return: Dictionary of alias objects
        :rtype: dict
        """
        return self._alias_objs

    def r_alias_obj_for_wwn(self, wwn):
        """Returns a list of alias objects a WWN is a member of

        :param wwn: WWN
        :type wwn: str
        :return: List of brcddb.classes.zone.AliasObj
        :rtype: list
        """
        return [alias_obj for alias_obj in self.r_alias_objects() if wwn in alias_obj.r_members()]

    def r_alias_for_wwn(self, wwn):
        """Returns a list of aliases, by name, a WWN is a member of

        :param wwn: WWN
        :type wwn: str
        :return: List of alias names
        :rtype: list
        """
        return [alias_obj.r_obj_key() for alias_obj in self.r_alias_obj_for_wwn(wwn)]

    def r_alias_obj_for_di(self, did, p_index):
        """Returns a list of alias objects a d,i is a member of

        :param did: Domain ID in decimal
        :type did: str, int
        :param p_index: Port index
        :type p_index: str, int
        :return: List of brcddb.classes.zone.AliasObj
        :rtype: list
        """
        di = str(did) + ',' + str(p_index)
        return [alias_obj for alias_obj in self.r_alias_objects() if di in alias_obj.r_members()]

    def r_alias_for_di(self, did, p_index):
        """Returns a list of aliases, by name, a d,i is a member of

        :param did: Domain ID in decimal
        :type did: str, int
        :param p_index: Port index
        :type p_index: str, int
        :return: List of alias names
        :rtype: list
        """
        return [alias_obj.r_obj_key() for alias_obj in self.r_alias_obj_for_di(did, p_index)]

    def s_add_fdmi_node(self, wwn):
        """Adds an FDMI node, 'brocade-fdmi/hba', to the fabric by it's WWN if it doesn't already exist

        :param wwn: WWN
        :type wwn: str
        :return: FDMI object
        :rtype: FdmiObj
        """
        fdmi_obj = self.r_fdmi_node_obj(wwn)
        if fdmi_obj is None:
            fdmi_obj = login_class.FdmiNodeObj(wwn, self.r_project_obj(), self.r_obj_key())
            self._fdmi_node_objs.update({wwn: fdmi_obj})
        return fdmi_obj

    def s_del_fdmi_node(self, wwn):
        """Deletes an FDMI node

        :param wwn: WWN
        :type wwn: str
        """
        if wwn in self._fdmi_node_objs:
            del self._fdmi_node_objs[wwn]

    def r_fdmi_node_obj(self, wwn):
        """Returns the FDMI node object for a given WWN login

        :param wwn: WWN
        :type wwn: str
        :return: FDMI node object. None if not found.
        :rtype: FdmiObj, None
        """
        return self._fdmi_node_objs.get(wwn)

    def r_fdmi_node_keys(self):
        """Returns the list of FDMI nodes (by WWN) in the fabric

        :return: List of WWNs
        :rtype: list
        """
        return list(self._fdmi_node_objs.keys())

    def r_fdmi_node_objects(self):
        """Returns the list of FDMI node objects in the fabric

        :return: List of FdmiObj
        :rtype: list
        """
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._fdmi_node_objs.values())

    def r_fdmi_node_objs(self):
        """Returns the dictionary of FDMI node objects. Typically only used by the brcddb libraries

        :return: Dictionary of FDMI node objects
        :rtype: dict
        """
        return self._fdmi_node_objs

    def s_add_fdmi_port(self, wwn):
        """Adds an FDMI port, 'brocade-fdmi/port', to the fabric by it's WWN if it doesn't already exist

        :param wwn: WWN
        :type wwn: str
        :return: FDMI object
        :rtype: FdmiObj
        """
        fdmi_obj = self.r_fdmi_port_obj(wwn)
        if fdmi_obj is None:
            fdmi_obj = login_class.FdmiPortObj(wwn, self.r_project_obj(), self.r_obj_key())
            self._fdmi_port_objs.update({wwn: fdmi_obj})
        return fdmi_obj

    def s_del_fdmi_port(self, wwn):
        """Deletes and FDMI port
        :param wwn: WWN
        :type wwn: str
        """
        if wwn in self._fdmi_port_objs:
            del self._fdmi_port_objs[wwn]

    def r_fdmi_port_obj(self, wwn):
        """Returns the FDMI port object for a given WWN login

        :param wwn: WWN
        :type wwn: str
        :return: FDMI node object. None if not found.
        :rtype: FdmiObj, None
        """
        return self._fdmi_port_objs.get(wwn)

    def r_fdmi_port_keys(self):
        """Returns the list of FDMI ports (by WWN) in the fabric

        :return: List of WWNs
        :rtype: list
        """
        return list(self._fdmi_port_objs.keys())

    def r_fdmi_port_objects(self):
        # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
        # https://bugs.python.org/issue32467 For those not at 3.7 yet so always process dict_values as a list
        return list(self._fdmi_port_objs.values())

    def r_fdmi_port_objs(self):
        """Returns the dictionary of FDMI port objects. Typically only used by the brcddb libraries

        :return: Dictionary of FDMI port objects
        :rtype: dict
        """
        return self._fdmi_port_objs

    def r_switch_keys(self):
        """Returns the list of logical switch WWNs in this fabric

        :return: List of switch WWNs
        :rtype: list
        """
        return self._switch_keys

    def r_switch_objects(self):
        """Returns the list of switch objects for the switches in this fabric

        :return: List of brcddb.classes.zone.SwitchObj
        :rtype: list
        """
        proj_obj = self.r_project_obj()
        return [proj_obj.r_switch_obj(k) for k in self.r_switch_keys()]

    def r_switch_obj(self, key):
        """Returns the switch object for a given switch WWN

        :param key: Switch WWN
        :type key: str
        :return: Switch object
        :rtype: brcddb.classes.switch.SwitchObj, None
        """
        return self.r_project_obj().r_switch_obj(key)

    def r_port_keys(self):
        """Returns a list of all ports in this fabric

        :return: List of ports in s/p format
        :rtype: list
        """
        proj_obj = self.r_project_obj()
        return [v for k in self.r_switch_keys() for v in proj_obj.r_switch_obj(k).r_port_keys()]

    def r_port_objects(self):
        """Returns a list of port objects for all ports in this fabric

        :return: List of PortObj
        :rtype: list
        """
        proj_obj = self.r_project_obj()
        return [v for k in self.r_switch_keys() for v in proj_obj.r_switch_obj(k).r_port_objects()]

    def r_port_obj_for_wwn(self, wwn):
        """Returns the port object matching a port index

        :param wwn: WWN of attached device
        :type wwn: str
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        login_obj = self.r_login_obj(wwn)
        return None if login_obj is None else  login_obj.r_port_obj()

    def r_port_obj_for_pid(self, pid):
        """Returns the port object matching a port FC addr

        :param pid: Port ID (fibre channel address)
        :type pid: str
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        if isinstance(pid, str):
            for switch_obj in self.r_switch_objects():
                port_obj = switch_obj.r_port_obj_for_pid(pid)
                if port_obj is not None:
                    return port_obj
        return None

    def r_port_object_for_di(self, di):
        """Returns the port object matching a d,i

        :param di: domain, index
        :type di: str
        :return: PortObj or None if not found
        :rtype: PortObj, None
        """
        buf = di
        buf.replace(' ', '')
        tl = [int(c) for c in buf.split(',') if c.isnumeric()]
        if len(tl) != 2:
            return None
        for switch_obj in self.r_switch_objects():
            did = switch_obj.r_get('brocade-fabric/fabric-switch/domain-id')
            if isinstance(did, int) and did == tl[0]:
                return switch_obj.r_port_object_for_index(tl[1])
        return None

    def r_fabric_obj(self):
        return self

    def r_fabric_key(self):
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

    def s_base_logins(self, wwn_list):
        """Add a wwn or list of wwns to base login list

        :param wwn_list: A WWN or list of WWNs to add to the base login list. If wwn is None, the list is cleared.
        :type wwn_list: tuple, list, str, None
        """
        if wwn_list is None:
            self._base_logins.clear()
        else:
            self._base_logins.extend(util.convert_to_list(wwn_list))

    def r_base_logins(self):
        """Returns a list of base (NPIV) login WWNs for this fabric

        :return: List of base WWNs (str)
        :rtype: list
        """
        return self._base_logins

    def r_is_base_login(self, wwn):
        """Tests to determine if a wwn is a base NPIV login

        :param wwn: Login WWN
        :type wwn: str
        :return: True: wwn is a base login. Flase: wwn is not a base login
        :rtype: bool
        """
        return False if wwn is None else True if wwn in self._base_logins else False

    def s_port_map(self, port_map):
        """Add a wwn or list of wwns to base login list

        :param port_map: dict, as returned from brcddb.util.util.login_to_port_map(), key: login WWN, value: Portobj
        :type port_map: dict, None
        """
        if port_map is None:
            self._port_map.clear()
        else:
            self._port_map.update(port_map)

    def r_port_map(self):
        """Returns map (dictionary) of logins to port objects

        :return: Dictionary of logins to port object. key: login WWN, value: PortObj where the login occured
        :rtype: dict
        """
        return self._port_map

    def r_port_obj(self, wwn):
        """Returns the port object where a wwn logged in.
        **Must call brcddb.util.util.login_to_port_map() before using this method**

        :return: PortObj where the login occured. None if not found
        :rtype: brcddb.classes.port.PortObj
        """
        return self._port_map[wwn] if wwn in self._port_map else None

    def r_switch_obj(self, wwn):
        """Returns the switch object where a wwn logged in.
        **Must call brcddb.util.util.login_to_port_map() before using this method**

        :param wwn: Login WWN
        :type wwn: str
        :return: SwitchObj where the login occured. None if not found
        :rtype: brcddb.classes.port.SwitchObj
        """
        return self._port_map[wwn].r_switch_obj() if wwn in self._port_map else None

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
