# Copyright 2023 Consoli Solutions, LLC.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apahche License, Version 2.0 (the "License");
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
:mod:`brcddb.util.obj_extract` - Extracts a list of objects from one object type to another

Description::

    Getting a list of port objects from a switch object is easy because the switch object has a built in method
    r_port_objects() but extrapolation is not always that straight forward. For example, you may want a list of all
    port objects associated with a zone object. This module contains the method obj_extract() which returns a list of
    any requested object from any object.

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | obj_extract           | Extracts a list of objects from an object or list of objects                          |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023 Consoli Solutions, LLC'
__date__ = '04 August 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.0'

import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcddb.classes.util as brcddb_class_util


def _zone_obj_list(fab_obj, zl):
    """Returns itself as a list

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param zl: List of zone names
    :type zl: list
    :return: List of zone objects, brcddb.classes.zone.ZoneObj, associated with the zone names in zl
    :rtype: list
    """
    return list() if fab_obj is None else gen_util.remove_none([fab_obj.r_zone_obj(z) for z in zl])


def _obj_self(obj):
    """Returns itself as a list

    :param obj: Any brcddb class object
    :type obj: brcddb.classes.*
    :return: obj as a list
    :rtype: list
    """
    return [obj]


def _alert_obj(obj):
    """Returns a list of alert objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_alert_objects()


def _project_obj(obj):
    """Returns the project object associated with obj in a list. See _obj_self() for parameter detail."""
    return gen_util.convert_to_list(obj.r_project_obj())


def _fabric_obj(obj):
    """Returns a list of fabric objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_fabric_objects() if hasattr(obj, 'r_fabric_objects') else [obj.r_fabric_obj()]


def _fdmi_node_obj(obj):
    """Returns a list of FDMI node objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_fdmi_node_objects()


def _fdmi_port_obj(obj):
    """Returns a list of FDMI port objects associated with a chassis obj. See _obj_self() for parameter detail."""
    return obj.r_fdmi_port_objects()


def _login_obj(obj):
    """Returns a list of login objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_login_objects() if hasattr(obj, 'r_login_objects') else [obj.r_login_obj()]


def _port_obj(obj):
    """Returns a list of port objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_port_objects() if hasattr(obj, 'r_port_objects') else [obj.r_port_obj()]


def _switch_obj(obj):
    """Returns a list of port objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_switch_objects() if hasattr(obj, 'r_chassis_objects') else [obj.r_switch_obj()]


def _chassis_obj(obj):
    """Returns a list of chssis objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_chassis_objects() if hasattr(obj, 'r_chassis_objects') else [obj.r_chassis_obj()]


def _alias_obj(obj):
    """Returns a list of alias objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_alias_objects() if hasattr(obj, 'r_alias_objects') else [obj.r_alias_obj()]


def _zone_obj(obj):
    """Returns a list of zone objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_zone_objects() if hasattr(obj, 'r_zone_objects') else [obj.r_zone_obj()]


def _zonecfg_obj(obj):
    """Returns a list of zone configuration objects associated with obj. See _obj_self() for parameter detail."""
    return obj.r_zonecfg_objects() if hasattr(obj, 'r_zonecfg_objects') else [obj.r_zonecfg_obj()]


def _port_obj_for_alias(obj):
    """Returns a list of login objects associated with an alias obj. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    rl = [fab_obj.r_port_obj_for_wwn(mem) for mem in obj.r_members() if gen_util.is_wwn(mem)]
    rl.extend([fab_obj.r_port_object_for_di(mem) for mem in obj.r_members() if gen_util.is_di(mem)])
    return gen_util.remove_none(rl)


def _ports_for_zone_obj(obj):
    """Returns a list of port objects associated with a zone object. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    rl = list()
    for mem in obj.r_members() + obj.r_pmembers():
        if gen_util.is_wwn(mem):
            rl.append(fab_obj.r_port_obj_for_wwn(mem))
        elif gen_util.is_di(mem):
            rl.append(fab_obj.r_port_object_for_di(mem))
        else:  # It must be an alias
            alias_obj = fab_obj.r_alias_obj(mem)
            if alias_obj is not None:
                rl.extend(_port_obj_for_alias(alias_obj))
    return gen_util.remove_none(rl)


def _ports_for_zonecfg_obj(obj):
    """Returns a list of port objects associated with zonecfg object. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_ports_for_zone_obj(zone_obj))
    return rl


def _switch_for_zone_obj(obj):
    """Returns a list of switch objects associated with a zone object. See _obj_self() for parameter detail."""
    return [port_obj.r_switch_obj() for port_obj in _ports_for_zone_obj(obj)]


def _switch_for_zonecfg_obj(obj):
    """Returns a list of switch objects associated with a zone object. See _obj_self() for parameter detail."""
    return [port_obj.r_switch_obj() for port_obj in _ports_for_zonecfg_obj(obj)]


def _chassis_for_zone_obj(obj):
    """Returns a list of chassis objects associated with a zone object. See _obj_self() for parameter detail."""
    return [switch_obj.r_chassis_obj() for switch_obj in _switch_for_zone_obj(obj)]


def _chassis_for_zonecfg_obj(obj):
    """Returns a list of chassis objects associated with a zone object. See _obj_self() for parameter detail."""
    return [switch_obj.r_chassis_obj() for switch_obj in _switch_for_zonecfg_obj(obj)]


def _chassis_obj_for_alias(obj):
    """Returns a list of chassis objects associated with an alias obj. See _obj_self() for parameter detail."""
    return [port_obj.r_chassis_obj() for port_obj in _port_obj_for_alias(obj)]


def _fabric_obj_for_alias(obj):
    """Returns a list of fabric objects associated with an alias obj. See _obj_self() for parameter detail."""
    return [port_obj.r_fabric_obj() for port_obj in _port_obj_for_alias(obj)]


def _switch_obj_for_alias(obj):
    """Returns a list of switch objects associated with an alias obj. See _obj_self() for parameter detail."""
    return [port_obj.r_switch_obj() for port_obj in _port_obj_for_alias(obj)]


def _zone_obj_for_alias(obj):
    """Returns a list of switch objects associated with an alias obj. See _obj_self() for parameter detail."""
    return obj.r_zone_objects()


def _zonecfg_obj_for_alias(obj):
    """Returns a list of zonecfg objects associated with an alias obj. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in obj.r_zone_objects():
        rl.extend(zone_obj.r_zone_configurations())
    return rl


def _fdmi_node_obj_for_alias(obj):
    """Returns a list of FDMI node objects associated with an alias obj. See _obj_self() for parameter detail."""
    rl = list()
    fab_obj = obj.r_fabric_obj()
    if fab_obj is not None:
        for mem in obj.r_members():
            if gen_util.is_wwn(mem):
                rl.append(fab_obj.r_fdmi_node_obj(mem))
    return gen_util.remove_none(rl)


def _fdmi_port_obj_for_alias(obj):
    """Returns a list of FDMI port objects associated with an alias obj. See _obj_self() for parameter detail."""
    rl = list()
    fab_obj = obj.r_fabric_obj()
    if fab_obj is not None:
        for mem in obj.r_members():
            if gen_util.is_wwn(mem):
                rl.append(fab_obj.r_fdmi_port_obj(mem))
    return gen_util.remove_none(rl)


def _login_obj_for_alias(obj):
    """Returns a list of login objects associated with an alias obj. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    return list() if fab_obj is None else [fab_obj.r_login_obj(m) for m in obj.r_members() if gen_util.is_wwn(m)]


def _alias_for_switch(obj):
    """Returns a list of alias objects associated with a switch obj. See _obj_self() for parameter detail."""
    rl, fab_obj = list(), obj.r_fabric_obj()
    if fab_obj is not None:
        for wwn in obj.r_login_keys():
            rl.extend(fab_obj.r_alias_obj_for_wwn(wwn))
    return rl


def _zone_obj_for_chassis(obj):
    """Returns a list of zone objects associated with a chassis. See _obj_self() for parameter detail."""
    rl = list()
    for fab_obj in obj.r_fabric_objects():
        rl.extend(fab_obj.r_zone_objects())
    return rl


def _zonecfg_obj_for_chassis(obj):
    """Returns a list of zone configuration objects associated with a chassis. See _obj_self() for parameter detail."""
    rl = list()
    for fab_obj in obj.r_fabric_objects():
        rl.extend(fab_obj.r_zonecfg_objects())
    return rl


def _alias_obj_for_port(obj):
    """Returns a list of alias objects associated with a fabric. See _obj_self() for parameter detail."""
    rl = list()
    if hasattr(obj, r_switch_obj):
        switch_obj = obj.r_switch_obj()
        if switch_obj is not None:
            fab_obj = switch_obj.r_fabric_obj()
            if fab_obj is not None:
                for wwn in obj.r_login_keys():
                    rl.extend(fab_obj.r_alias_obj_for_wwn(wwn))
    return rl


def _alias_obj_for_switch(obj):
    """Returns a list of alias objects associated with a switch. See _obj_self() for parameter detail."""
    rl, fab_obj = list(), obj.r_fabric_obj()
    if fab_obj is not None:
        for wwn in obj.r_login_keys():
            rl.extend(fab_obj.r_alias_obj_for_wwn(wwn))
    return gen_util.remove_none(rl)


def _alias_obj_for_chassis(obj):
    """Returns a list of alias objects associated with a chassis obj. See _obj_self() for parameter detail."""
    rl = list()
    for switch_obj in obj.r_switch_objects():
        rl.extend(_alias_obj_for_switch(switch_obj))
    return rl


def _chassis_obj_for_fabric(obj):
    """Returns a list of chassis objects associated with a fabric. See _obj_self() for parameter detail."""
    return [switch_obj.r_chassis_obj() for switch_obj in obj.r_switch_objects()]


def _alias_obj_for_key(obj):
    """Returns a list of alias objects associated with the obj key. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return fab_obj.r_alias_obj_for_wwn(obj.r_obj_key())


def _login_obj_for_fdmi(obj):
    """Returns a the switch object in a list for an FDMI node or port obj. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.convert_to_list(fab_obj.r_login_obj(obj.r_obj_key()))


def _port_obj_for_fdmi(obj):
    """Returns a the port object in a list for a node obj. See _obj_self() for parameter detail."""
    return [login_obj.r_port_obj() for login_obj in _login_obj_for_fdmi(obj) if login_obj.r_port_obj() is not None]


def _switch_obj_for_fdmi(obj):
    """Returns a the switch object in a list for an FDMI node or port obj. See _obj_self() for parameter detail."""
    return [login_obj.r_switch_obj() for login_obj in _login_obj_for_fdmi(obj) if login_obj.r_switch_obj() is not None]


def _fabric_obj_for_fdmi(obj):
    """Returns a the switch object in a list for an FDMI node or port obj. See _obj_self() for parameter detail."""
    return [login_obj.r_fabric_obj() for login_obj in _login_obj_for_fdmi(obj) if login_obj.r_fabric_obj() is not None]


def _chassis_obj_for_fdmi(obj):
    """Returns a the chassis object in a list for an FDMI node or port obj. See _obj_self() for parameter detail."""
    return [switch_obj.r_chassis_obj() for switch_obj in _switch_obj_for_fdmi(obj)
            if switch_obj.r_chassis_obj() is not None]


def _zone_obj_for_fdmi(obj):
    """Returns a list of zone objects an FDMI node or port obj participates in. See _obj_self() for parameter detail."""
    rl, fab_obj = list(), obj.r_fabric_obj()
    for login_obj in _login_obj_for_fdmi(obj):
        rl.extend([zone_obj for zone_obj in _zone_obj_list(fab_obj, fab_obj.r_zones_for_wwn(login_obj.r_obj_key()))])
    return rl


def _zonecfg_obj_for_fdmi(obj):
    """Returns a list of zone objects an FDMI node or port obj participates in. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_for_fdmi(obj):
        rl.extend(zone_obj.r_zonecfg_objects())
    return rl


def _fdmi_node_obj_for_login(obj):
    """Returns the FDMI node object in a list for a login obj. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.remove_none(gen_util.convert_to_list(fab_obj.r_fdmi_node_obj(obj.r_obj_key())))


def _fdmi_port_obj_for_login(obj):
    """Returns the FDMI port object in a list for a login obj. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.remove_none(gen_util.convert_to_list(fab_obj.r_fdmi_port_obj(obj.r_obj_key())))


def _fdmi_node_for_fdmi_port(obj):
    """Returns a list of FDMI port objects for a zonecfg. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.remove_none(gen_util.convert_to_list(fab_obj.r_fdmi_node_obj(obj.r_obj_key())))


def _fdmi_port_for_fdmi_node(obj):
    """Returns a list of FDMI port objects for a zonecfg. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.remove_none(gen_util.convert_to_list(fab_obj.r_fdmi_port_obj(obj.r_obj_key())))


def _zone_obj_for_login(obj):
    """Returns a list of zone objects an FDMI node or port obj participates in. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    if fab_obj is None:
        return list()
    return gen_util.remove_none([fab_obj.r_zone_obj(zone) for zone in fab_obj.r_zones_for_wwn(obj.r_obj_key())])


def _zonecfg_obj_for_login(obj):
    """Returns a list of zonecfg objects associated with a login. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_for_login(obj):
        rl.extend(zone_obj.r_zonecfg_objects())
    return rl


def _alias_obj_for_project(obj):
    """Returns a list of alias objects associated with a project. See _obj_self() for parameter detail."""
    rl = list()
    for fab_obj in obj.r_fabric_objects():
        rl.extend(fab_obj.r_alias_objects())
    return gen_util.remove_none(rl)


def _zone_obj_for_project(obj):
    """Returns a list of zone objects in a project object. See _obj_self() for parameter detail."""
    rl = list()
    for fab_obj in obj.r_fabric_objects():
        rl.extend(fab_obj.r_zone_objects())
    return rl


def _zonecfg_obj_for_project(obj):
    """Returns a list of zonecfg objects in a project object. See _obj_self() for parameter detail."""
    rl = list()
    for fab_obj in obj.r_fabric_objects():
        rl.extend(fab_obj.r_zonecfg_objects())
    return rl


def _zone_obj_for_obj(obj):
    """Returns a list of zone objects a port or switch obj participates in. See _obj_self() for parameter detail."""
    zl, fab_obj = list(), obj.r_fabric_obj()
    if fab_obj is not None:
        for wwn in obj.r_login_keys():
            zl.extend(fab_obj.r_zones_for_wwn(wwn))
    return _zone_obj_list(fab_obj, zl)


def _zonecfg_obj_for_obj(obj):
    """Returns a list of zonecfg objects a port or switch obj participates in. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_for_obj(obj):
        rl.extend(zone_obj.r_zonecfg_objects())
    return rl


def _alias_for_zone(obj):
    """Returns a list of alias objects for a zone. See _obj_self() for parameter detail."""
    return [mem for mem in obj.r_members() + obj.r_pmembers() if not gen_util.is_wwn(mem) and
            not gen_util.is_di(mem)]


def _alias_for_zonecfg(obj):
    """Returns a list of alias objects for a zone configuration. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_alias_for_zone(zone_obj))
    return rl


def _login_for_zone(obj):
    """Returns a list of login objects for a zone. See _obj_self() for parameter detail."""
    rl, fab_obj = list(), obj.r_fabric_obj()
    if fab_obj is not None:
        for mem in obj.r_members() + obj.r_pmembers():
            if gen_util.is_wwn(mem):
                rl.append(fab_obj.r_login_obj(mem))
            elif gen_util.is_di(mem):
                port_obj = fab_obj.r_port_object_for_di(mem)
                if port_obj is not None:
                    rl.extend(port_obj.r_login_objects())
            else:  # Assume it's an alias
                zone_obj = fab_obj.r_zone_obj(mem)
                if zone_obj is not None:
                    rl.extend(_login_obj_for_alias(zone_obj))
    return gen_util.remove_none(rl)


def _fdmi_node_for_zone(obj):
    """Returns a list of FDMI node objects for a zone. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    rl = list() if fab_obj is None else \
        [fab_obj.r_fdmi_node_obj(login_obj.r_obj_key()) for login_obj in _login_for_zone(obj) if login_obj is not None]
    return gen_util.remove_none(rl)


def _fdmi_port_for_zone(obj):
    """Returns a list of FDMI port objects for a zone. See _obj_self() for parameter detail."""
    fab_obj = obj.r_fabric_obj()
    rl = list() if fab_obj is None else \
        [fab_obj.r_fdmi_port_obj(login_obj.r_obj_key()) for login_obj in _login_for_zone(obj) if login_obj is not None]
    return gen_util.remove_none(rl)


def _login_for_zonecfg(obj):
    """Returns a list of login objects associated with a zonecfg. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_login_for_zone(zone_obj))
    return rl


def _fdmi_node_for_zonecfg(obj):
    """Returns a list of FDMI node objects associated with a zonecfg. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_fdmi_node_for_zone(zone_obj))
    return rl


def _fdmi_port_for_zonecfg(obj):
    """Returns a list of FDMI port objects for a zonecfg. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_fdmi_port_for_zone(zone_obj))
    return rl


def _zone_obj_for_zonecfg(obj):
    """Returns a list of FDMI port objects for a zonecfg. See _obj_self() for parameter detail."""
    rl = list()
    for zone_obj in _zone_obj_list(obj.r_fabric_obj(), obj.r_members()):
        rl.extend(_fdmi_port_for_zone(zone_obj))
    return rl


def _empty_list(obj):
    """Returns an empty list. See _obj_self() for parameter detail."""
    return list()


# _obj_convert_tbl converts an existing object type to a list of new object types. The first key is the object type
# we're converting from and the second the object type we're converting to. For example, to get a list of port objects
# from a switch object:
# port_obj_list = _obj_convert_tbl['SwitchObj]['PortObj']
_obj_convert_tbl = dict(
    AlertObj=dict(
        AlertObj=_obj_self,
        AliasObj=_empty_list,
        ChassisObj=_empty_list,
        FabricObj=_empty_list,
        FdmiNodeObj=_empty_list,
        FdmiPortObj=_empty_list,
        LoginObj=_empty_list,
        PortObj=_empty_list,
        ProjectObj=_empty_list,
        SwitchObj=_empty_list,
        ZoneObj=_empty_list,
        ZoneCfgObj=_empty_list,
    ),
    AliasObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_obj_self,
        ChassisObj=_chassis_obj_for_alias,
        FabricObj=_fabric_obj_for_alias,
        FdmiNodeObj=_fdmi_node_obj_for_alias,
        FdmiPortObj=_fdmi_port_obj_for_alias,
        LoginObj=_login_obj_for_alias,
        PortObj=_port_obj_for_alias,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj_for_alias,
        ZoneObj=_zone_obj_for_alias,
        ZoneCfgObj=_zonecfg_obj_for_alias,
    ),
    ChassisObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_chassis,
        ChassisObj=_obj_self,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_obj,
        FdmiPortObj=_fdmi_port_obj,
        LoginObj=_login_obj,
        PortObj=_port_obj,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj,
        ZoneObj=_zone_obj_for_chassis,
        ZoneCfgObj=_zonecfg_obj_for_chassis,
    ),
    FabricObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj,
        ChassisObj=_chassis_obj_for_fabric,
        FabricObj=_obj_self,
        FdmiNodeObj=_fdmi_node_obj,
        FdmiPortObj=_fdmi_port_obj,
        LoginObj=_login_obj,
        PortObj=_port_obj,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj,
        ZoneObj=_zone_obj,
        ZoneCfgObj=_zonecfg_obj,
    ),
    FdmiNodeObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_key,
        ChassisObj=_chassis_obj_for_fdmi,
        FabricObj=_fabric_obj_for_fdmi,
        FdmiNodeObj=_obj_self,
        FdmiPortObj=_fdmi_port_for_fdmi_node,
        LoginObj=_login_obj_for_fdmi,
        PortObj=_port_obj_for_fdmi,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj_for_fdmi,
        ZoneObj=_zone_obj_for_fdmi,
        ZoneCfgObj=_zonecfg_obj_for_fdmi,
    ),
    FdmiPortObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_key,
        ChassisObj=_chassis_obj_for_fdmi,
        FabricObj=_fabric_obj_for_fdmi,
        FdmiNodeObj=_fdmi_node_for_fdmi_port,
        FdmiPortObj=_obj_self,
        LoginObj=_login_obj_for_fdmi,
        PortObj=_port_obj_for_fdmi,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj_for_fdmi,
        ZoneObj=_zone_obj_for_fdmi,
        ZoneCfgObj=_zonecfg_obj_for_fdmi,
    ),
    LoginObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_key,
        ChassisObj=_chassis_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_obj_for_login,
        FdmiPortObj=_fdmi_port_obj_for_login,
        LoginObj=_obj_self,
        PortObj=_port_obj,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj,
        ZoneObj=_zone_obj_for_login,
        ZoneCfgObj=_zonecfg_obj_for_login,
    ),
    PortObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_port,
        ChassisObj=_chassis_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_obj,
        FdmiPortObj=_fdmi_port_obj,
        LoginObj=_login_obj,
        PortObj=_obj_self,
        ProjectObj=_project_obj,
        SwitchObj=_switch_obj,
        ZoneObj=_zone_obj_for_obj,
        ZoneCfgObj=_zonecfg_obj_for_obj,
    ),
    ProjectObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_project,
        ChassisObj=_chassis_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_obj,
        FdmiPortObj=_fdmi_port_obj,
        LoginObj=_login_obj,
        PortObj=_port_obj,
        ProjectObj=_obj_self,
        SwitchObj=_switch_obj,
        ZoneObj=_zone_obj_for_project,
        ZoneCfgObj=_zonecfg_obj_for_project,
    ),
    SwitchObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_obj_for_switch,
        ChassisObj=_chassis_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_obj,
        FdmiPortObj=_fdmi_port_obj,
        LoginObj=_login_obj,
        PortObj=_port_obj,
        ProjectObj=_project_obj,
        SwitchObj=_obj_self,
        ZoneObj=_zone_obj_for_obj,
        ZoneCfgObj=_zonecfg_obj_for_obj,
    ),
    ZoneObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_for_zone,
        ChassisObj=_chassis_for_zone_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_for_zone,
        FdmiPortObj=_fdmi_port_for_zone,
        LoginObj=_login_for_zone,
        PortObj=_ports_for_zone_obj,
        ProjectObj=_project_obj,
        SwitchObj=_switch_for_zone_obj,
        ZoneObj=_obj_self,
        ZoneCfgObj=_zonecfg_obj,
    ),
    ZoneCfgObj=dict(
        AlertObj=_alert_obj,
        AliasObj=_alias_for_zonecfg,
        ChassisObj=_chassis_for_zonecfg_obj,
        FabricObj=_fabric_obj,
        FdmiNodeObj=_fdmi_node_for_zonecfg,
        FdmiPortObj=_fdmi_port_for_zonecfg,
        LoginObj=_login_for_zonecfg,
        PortObj=_ports_for_zonecfg_obj,
        ProjectObj=_project_obj,
        SwitchObj=_switch_for_zonecfg_obj,
        ZoneObj=_zone_obj,
        ZoneCfgObj=_obj_self,
    ),
)


def obj_extract(from_obj, to_type):
    """Extracts a list of objects from an object or list of objects

    :param from_obj: The brcddb object or object list the to_obj is to be extracted from
    :type from_obj: list, tuple, brcddb.classes.*
    :param to_type: The object simple object type, brcddb.classes.util.get_simple_class_type(), to extract from from_obj
    :type to_type: str
    :return: List of objects extracted from from_obj associated with to_obj. Redundant objects removed
    :rtype: brcddb.classes.* (whatever type to_obj is)
    """
    rl = list()
    for in_obj in gen_util.convert_to_list(from_obj):
        from_type = brcddb_class_util.get_simple_class_type(in_obj)
        if from_type is None:
            brcdapi_log.exception('Unknown from_obj object type: ' + str(type(from_type)), echo=True)
        else:
            rl.extend([obj for obj in _obj_convert_tbl[from_type][to_type](in_obj) if obj is not None])
    return gen_util.remove_duplicates(rl)
