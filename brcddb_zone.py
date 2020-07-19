#!/usr/bin/python
# Copyright 2019 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.brcddb_zone` - Zone utilities.

*********************************************************************************************************

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
    bl = base_alias_obj.r_members()
    cl = comp_alias_obj.r_members()
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
    """Compares two aliases

    :param base_zone_obj: Alias object to compare against
    :type base_zone_obj: brcddb.classes.zone.AliasObj
    :param comp_zone_obj: New alias object
    :type comp_zone_obj: brcddb.classes.zone.AliasObj
    :return type_flag: True if the zone type is the same, False if not
    :rtype type_flag: bool
    :return add_members: Members is comp_alias_obj that do not exist in base_alias_obj
    :rtype add_members: list
    :return del_members: Members is base_alias_obj that do not exist in comp_alias_obj
    :rtype del_members: list
    :return add_pmembers: Principal members is comp_zone_obj that do not exist in base_zone_obj
    :rtype add_pmembers: list
    :return del_pmembers: Principal members is base_zone_obj that do not exist in comp_zone_obj
    :rtype del_pmembers: list
    """
    bl = base_zone_obj.r_members()
    cl = comp_zone_obj.r_members()
    pbl = base_zone_obj.r_pmembers()
    pcl = comp_zone_obj.r_pmembers()
    return True if base_zone_obj.r_type() != comp_zone_obj.r_type() else False, \
                [mem for mem in cl if mem not in bl], [mem for mem in bl if mem not in cl], \
                [mem for mem in pcl if mem not in pbl], [mem for mem in pbl if mem not in pcl]
            

def is_zone_match(base_zone_obj, comp_zone_obj):
    """Simple True/False comparison between two zones

    :param base_zone_obj: Alias object to compare against
    :type base_zone_obj: brcddb.classes.zone.AliasObj
    :param comp_zone_obj: New alias object
    :type comp_zone_obj: brcddb.classes.zone.AliasObj
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
    bl = base_cfg_obj.r_members()
    cl = comp_cfg_obj.r_members()
    return [mem for mem in cl if mem not in bl], [mem for mem in bl if mem not in cl]


def is_cfg_match(base_cfg_obj, comp_cfg_obj):
    """Simple True/False comparison between two cfges

    :param base_cfg_obj: Alias object to compare against
    :type base_cfg_obj: brcddb.classes.zone.AliasObj
    :param comp_cfg_obj: New cfg object
    :type comp_cfg_obj: brcddb.classes.zone.AliasObj
    :return: True if the cfges are the same, otherwise False
    :rtype: bool
    """
    bl, cl = cfg_compare(base_cfg_obj, comp_cfg_obj)
    return True if len(bl) + len(cl) == 0 else False


def zone_type(zone_obj, num_flag=False):
    """Returns the zone type (User defined peer, Target driven peer, or Stnadard) in plain text

    :param port_obj: Zone Object
    :type port_obj: brcddb_classes.ZoneObj
    :param num_flag: If True, append (type) where type is the numerical zone type returned from the API
    :type num_flag: bool
    :return: Port type
    :rtype: str
    """
    type = zone_obj.r_type()
    try:
        buf = brcddb_common.zone_conversion_tbl['zone-type'][type]
        return buf + '(' + str(type) + ')' if num_flag else buf
    except:
        return 'Unknown (' + str(type) + ')'