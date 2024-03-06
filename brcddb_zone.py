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

:mod:`brcddb.brcddb_zone` - Zone utilities.

Public Methods::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | alias_compare         | Compares two aliases                                                                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | is_alias_match        | Simple True/False comparison between two aliases                                      |
    +-----------------------+---------------------------------------------------------------------------------------+
    | zone_compare          | Compares two zones                                                                    |
    +-----------------------+---------------------------------------------------------------------------------------+
    | is_zone_match         | Simple True/False comparison between two zones                                        |
    +-----------------------+---------------------------------------------------------------------------------------+
    | cfg_compare           | Compares two zone configurations. Validates membership only. Does not compare         |
    |                       | individual members                                                                    |
    +-----------------------+---------------------------------------------------------------------------------------+
    | is_cfg_match          | Simple True/False comparison between two configurations                               |
    +-----------------------+---------------------------------------------------------------------------------------+
    | zone_type             | Returns the zone type (User defined peer, Target driven peer, or Standard) in plain   |
    |                       | text                                                                                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | eff_zoned_to_wwn      | Finds all WWNs in the effective zone that are zoned to wwn.                           |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '06 Mar 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.1'

import brcdapi.util as brcdapi_util
import brcddb.brcddb_common as brcddb_common


def alias_compare(base_alias_obj, comp_alias_obj):
    """Compares two aliases
    
    :param base_alias_obj: Alias object to compare against
    :type base_alias_obj: brcddb.classes.zone.AliasObj
    :param comp_alias_obj: New alias object
    :type comp_alias_obj: brcddb.classes.zone.AliasObj
    :return add_members: Members is comp_alias_obj that do not exist in base_alias_obj
    :rtype add_members: list
    :return del_members: Members is base_alias_obj that do not exist in comp_alias_obj
    :rtype del_members: list
    """
    bl, cl = base_alias_obj.r_members(), comp_alias_obj.r_members()
    return [mem for mem in cl if mem not in bl], [mem for mem in bl if mem not in cl]


def is_alias_match(base_alias_obj, comp_alias_obj):
    """Simple True/False comparison between two aliases

    :param base_alias_obj: Alias object to compare against
    :type base_alias_obj: brcddb.classes.zone.AliasObj
    :param comp_alias_obj: New alias object
    :type comp_alias_obj: brcddb.classes.zone.AliasObj
    :return: True if the aliases are the same, otherwise False
    :rtype: bool
    """
    bl, cl = alias_compare(base_alias_obj, comp_alias_obj)
    return True if len(bl) + len(cl) == 0 else False


def zone_compare(base_zone_obj, comp_zone_obj):
    """Compares two zones

    :param base_zone_obj: Zone object to compare against
    :type base_zone_obj: brcddb.classes.zone.ZoneObj
    :param comp_zone_obj: New zone object
    :type comp_zone_obj: brcddb.classes.zone.ZoneObj
    :return type_flag: True if the zone type is the same, False if not
    :rtype type_flag: bool
    :return add_members: Members is comp_zone_obj that do not exist in base_zone_obj
    :rtype add_members: list
    :return del_members: Members is base_zone_obj that do not exist in comp_zone_obj
    :rtype del_members: list
    :return add_pmembers: Principal members is comp_zone_obj that do not exist in base_zone_obj
    :rtype add_pmembers: list
    :return del_pmembers: Principal members is base_zone_obj that do not exist in comp_zone_obj
    :rtype del_pmembers: list
    """
    bl, cl = base_zone_obj.r_members(), comp_zone_obj.r_members()
    pbl, pcl = base_zone_obj.r_pmembers(), comp_zone_obj.r_pmembers()
    return True if base_zone_obj.r_type() != comp_zone_obj.r_type() else False, \
        [mem for mem in cl if mem not in bl], \
        [mem for mem in bl if mem not in cl], \
        [mem for mem in pcl if mem not in pbl], \
        [mem for mem in pbl if mem not in pcl]
            

def is_zone_match(base_zone_obj, comp_zone_obj):
    """Simple True/False comparison between two zones

    :param base_zone_obj: Zone object to compare against
    :type base_zone_obj: brcddb.classes.zone.ZoneObj
    :param comp_zone_obj: New alias object
    :type comp_zone_obj: brcddb.classes.zone.ZoneObj
    :return: True if the zones are the same, otherwise False
    :rtype: bool
    """
    t, bl, cl, pbl, pcl = zone_compare(base_zone_obj, comp_zone_obj)
    return True if t and len(bl) + len(cl) + len(pbl) + len(pcl) == 0 else False


def cfg_compare(base_cfg_obj, comp_cfg_obj):
    """Compares two zone configurations. Validates membership only. Does not compare individual members

    :param base_cfg_obj: Alias object to compare against
    :type base_cfg_obj: brcddb.classes.zone.AliasObj
    :param comp_cfg_obj: New cfg object
    :type comp_cfg_obj: brcddb.classes.zone.AliasObj
    :return add_members: Members is comp_cfg_obj that do not exist in base_cfg_obj
    :rtype add_members: list
    :return del_members: Members is base_cfg_obj that do not exist in comp_cfg_obj
    :rtype del_members: list
    """
    bl, cl = base_cfg_obj.r_members(), comp_cfg_obj.r_members()
    return [mem for mem in cl if mem not in bl], [mem for mem in bl if mem not in cl]


def is_cfg_match(base_cfg_obj, comp_cfg_obj):
    """Simple True/False comparison between two configurations

    :param base_cfg_obj: Alias object to compare against
    :type base_cfg_obj: brcddb.classes.zone.AliasObj
    :param comp_cfg_obj: New cfg object
    :type comp_cfg_obj: brcddb.classes.zone.AliasObj
    :return: True if the configurations are the same, otherwise False
    :rtype: bool
    """
    bl, cl = cfg_compare(base_cfg_obj, comp_cfg_obj)
    return True if len(bl) + len(cl) == 0 else False


def zone_type(zone_obj, num_flag=False):
    """Returns the zone type (User defined peer, Target driven peer, or Standard) in plain text

    :param zone_obj: Zone Object
    :type zone_obj: brcddb_classes.ZoneObj
    :param num_flag: If True, append (type) where type is the numerical zone type returned from the API
    :type num_flag: bool
    :return: Zone type
    :rtype: str
    """
    z_type = zone_obj.r_type()
    try:
        buf = brcddb_common.zone_conversion_tbl['zone-type'][z_type]
        return buf + '(' + str(z_type) + ')' if num_flag else buf
    except KeyError:
        return 'Unknown (' + str(z_type) + ')'


def eff_zoned_to_wwn(fab_obj, wwn, target=False, initiator=False, all_types=False):
    """Finds all WWNs in the effective zone that are zoned to wwn.

    WARNING: if all_types == True, the FC4 type in the login data is not checked and therefore, all WWNs will be
    returned. When filtering on "target" or "initiator", there must be something logged in and the login data from the
    name server must have been retrieved in order to check the login type.

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param wwn: WWN to look for
    :type wwn: str
    :param target: If True, include all online targets
    :type target: bool
    :param initiator: If True, include any online port that is not a target
    :type initiator: bool
    :param all_types: If True, include all ports, online or offline.
    :type all_types: bool
    :return: Dictionary - Key: WWN of device zoned to wwn. Value is the list of zone names common to both WWNs.
    :rtype: dict
    """
    rd, zones_for_wwn_d = dict(), dict()

    for zone in fab_obj.r_eff_zones_for_wwn(wwn):  # Used to find common zones with members
        zones_for_wwn_d.update({zone: True})

    for zone_obj in fab_obj.r_eff_zone_objects_for_wwn(wwn):
        if zone_obj.r_type() == brcddb_common.ZONE_STANDARD_ZONE:
            mem_l = zone_obj.r_members()
        else:
            mem_l = zone_obj.r_members() if wwn in zone_obj.r_pmembers() else zone_obj.r_pmembers()
        for mem in mem_l:
            if mem == wwn or mem in rd:
                continue
            if all_types:
                rd.update({mem: [m for m in fab_obj.r_eff_zones_for_wwn(mem) if bool(zones_for_wwn_d.get(m))]})
                continue
            login_obj = fab_obj.r_login_obj(mem)
            if login_obj is None:
                continue
            fc4 = login_obj.r_get(brcdapi_util.bns_fc4_features)
            if fc4 is None:
                continue
            if target and 'target' in fc4.lower():
                rd.update({mem: [m for m in fab_obj.r_eff_zones_for_wwn(mem) if bool(zones_for_wwn_d.get(m))]})
            elif initiator and 'initiator' in fc4.lower():
                # Used "elif" because if both target & initiator was specified, it will already be in rd
                rd.update({mem: [m for m in fab_obj.r_eff_zones_for_wwn(mem) if bool(zones_for_wwn_d.get(m))]})

    return rd
