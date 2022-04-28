# Copyright 2020, 2021, 2022 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.api.zone` - Converts the zoning information in a fabric object (brcddb.classes.fabric.FabricObj) to JSON \
and sends it to a switch.

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------|
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | build_alias_content   | Builds the alias dict structure to be converted to JSON and sent to a switch,         |
    |                       |'zoning/defined-configuration'                                                         |
    +-----------------------+---------------------------------------------------------------------------------------|
    | build_zone_content    | Builds the zone dict structure to be converted to JSON and sent to a switch,          |
    |                       | 'zoning/defined-configuration'                                                        |
    +-----------------------+---------------------------------------------------------------------------------------|
    | build_zonecfg_content | Builds the zonecfg dict structure to be converted to JSON and sent to a switch,       |
    |                       | 'zoning/defined-configuration'                                                        |
    +-----------------------+---------------------------------------------------------------------------------------|
    | build_all_zone_content| Builds the zonecfg structure to be converted to JSON and sent to a switch,            |
    |                       | 'brocade-zone/defined-configuration'                                                  |
    +-----------------------+---------------------------------------------------------------------------------------|
    | replace_zoning        | Replaces the zoning database in a fabric by clearing it and then PATCHing it with a   |
    |                       | new zoning database                                                                   |
    +-----------------------+---------------------------------------------------------------------------------------|
    | enable_zonecfg        | Activates a zone configuration (make a zone configuration effective)                  |
    +-----------------------+---------------------------------------------------------------------------------------|

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 01 Nov 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 14 Aug 2021   | Added enable_zonecfg()                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 31 Dec 2021   | Deprecated pyfos_auth.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 28 Apr 2022   | Updated comments only.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022 Jack Consoli'
__date__ = '28 Apr 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import brcdapi.zone as brcdapi_zone
import brcddb.brcddb_fabric as brcddb_fabric
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.fos_auth as fos_auth
import brcdapi.util as brcdapi_util
import brcddb.brcddb_common as brcddb_common

_MAX_ZONE_SAVE_TRY = 12  # The maximum number of times to try saving zoning changes
_ZONE_SAVE_WAIT = 5  # Length of time to wait between fabric busy when saving zone changes


def build_alias_content(fab_obj):
    """Builds the alias dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {'defined-configuration': dict()}
    wd = content['defined-configuration']

    # Add the aliases
    l = list()
    for obj in fab_obj.r_alias_objects():
        members = obj.r_members()
        if len(members) > 0:
            l.append({'alias-name': obj.r_obj_key(), 'member-entry': {'alias-entry-name': members}})
    if len(l) > 0:
        wd.update(alias=l)

    return None if len(wd.keys()) == 0 else content


def build_zone_content(fab_obj):
    """Builds the zone dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {'defined-configuration': dict()}
    wd = content['defined-configuration']

    # Add the zones
    l = list()
    for obj in fab_obj.r_zone_objects():
        if obj.r_get('zone-type') is not brcddb_common.ZONE_TARGET_PEER:
            d = {'zone-name': obj.r_obj_key(), 'zone-type': obj.r_type(), 'member-entry': dict()}
            me = d.get('member-entry')
            members = obj.r_members()
            if len(members) > 0:
                me.update({'entry-name': members})
            members = obj.r_pmembers()
            if len(members) > 0:
                me.update({'principal-entry-name': members})
            l.append(d)
        wd.update(zone=l)

    return None if len(wd.keys()) == 0 else content


def build_zonecfg_content(fab_obj):
    """Builds the zonecfg dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {'defined-configuration': dict()}
    wd = content['defined-configuration']

    # Add the zone configurations
    l = list()
    for obj in fab_obj.r_zonecfg_objects():
        if not obj.r_is_effective():
            members = obj.r_members()
            if len(members) > 0:
                l.append({'cfg-name': obj.r_obj_key(), 'member-zone': {'zone-name': members}})
    if len(l) > 0:
        wd.update(cfg=l)

    return None if len(wd.keys()) == 0 else content


def build_all_zone_content(fab_obj):
    """Builds the zonecfg structure to be converted to JSON and sent to a switch, 'brocade-zone/defined-configuration'

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {'defined-configuration': dict()}
    wd = content['defined-configuration']

    temp_content = build_alias_content(fab_obj)
    if temp_content is not None:
        wd.update(alias=temp_content.get('defined-configuration').get('alias'))
    temp_content = build_zone_content(fab_obj)
    if temp_content is not None:
        wd.update(zone=temp_content.get('defined-configuration').get('zone'))
    temp_content = build_zonecfg_content(fab_obj)
    if temp_content is not None:
        wd.update(cfg=temp_content.get('defined-configuration').get('cfg'))

    return content


def replace_zoning(session, fab_obj, fid):
    """Replaces the zoning database in a fabric by clearing it and then PATCHing it with a new zoning database

     Relevant resource: 'zoning/defined-configuration'
     An error is returned if there is no zone database in in the fab_obj. Use clear_zoning() to clear out zoning.

    :param session: Login session object from brcdapi.brcdapi_rest.login()
    :type session: dict
    :param fab_obj: Fabric object whose zone database will be sent to the switch
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param fid: Fabric ID. If FID check is disabled, this must be the FID of the switch where the request is sent.
    :type fid: int
    :return: Object returned from FOS API
    :rtype: dict
    """
    # Get the dict to be converted to JSON and sent to the switch
    content = build_all_zone_content(fab_obj)
    if content is None:
        return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST,
                                     'No zone database in ' + brcddb_fabric.best_fab_name(fab_obj.r_fabric_obj()),
                                     '')

    # Get the checksum - this is needed to save the configuration.
    checksum, obj = brcdapi_zone.checksum(session, fid)
    if fos_auth.is_error(obj):
        return obj

    # Clear the zone database
    obj = brcdapi_zone.clear_zone(session, fid)
    if not fos_auth.is_error(obj):
        # Send the zoning request
        obj = brcdapi_rest.send_request(session, 'brocade-zone/defined-configuration', 'PATCH', content, fid)
        if not fos_auth.is_error(obj):
            obj = brcdapi_zone.save(session, fid, checksum)
            if not fos_auth.is_error(obj):
                return obj

    # If we got this far, something went wrong so abort the transaction.
    brcdapi_zone.abort(session, fid)
    return obj


def enable_zonecfg(session, fab_obj, fid, eff_cfg):
    """Activates a zone configuration (make a zone configuration effective)

    :param session: Login session object from brcdapi.brcdapi_rest.login()
    :type session: dict
    :param fab_obj: Not used. Left in here for methods that used it prior to deprecating this parameter.
    :type fab_obj: brcddb.classes.fabric.FabricObj, None
    :param fid: Fabric ID.
    :type fid: int
    :param eff_cfg: Name of the zone configuration to enable. None = no zone configuration to enable
    :type eff_cfg: str, None
    :return: Object returned from FOS API
    :rtype: dict
    """
    # Get the checksum - this is needed to save the configuration.
    checksum, obj = brcdapi_zone.checksum(session, fid)
    if fos_auth.is_error(obj):
        return obj

    # Activate the zone configuration.
    return brcdapi_zone.enable_zonecfg(session, checksum, fid, eff_cfg, True)
