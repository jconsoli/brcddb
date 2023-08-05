# Copyright 2023 Consoli Solutions, LLC.  All rights reserved.
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

import copy
import brcdapi.log as brcdapi_log
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
        if obj.r_obj_key() != '_effective_zone_cfg':
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
        brcdapi_log.log('Failed to get checksum', echo=True)
        return obj

    # Clear the zone database
    obj = brcdapi_zone.clear_zone(session, fid)
    if fos_auth.is_error(obj):
        brcdapi_zone.abort(session, fid)
        brcdapi_log.log('Failed to clear zone database', echo=True)
        return obj

    # Send the zoning request
    for k, zone_l in content['defined-configuration'].items():
        temp_content = {'defined-configuration': {k: copy.deepcopy(zone_l)}}
        obj = brcdapi_rest.send_request(session, 'brocade-zone/defined-configuration', 'PATCH', temp_content, fid)
        if fos_auth.is_error(obj):
            brcdapi_zone.abort(session, fid)
            brcdapi_log.log('Failed to update ' + str(k) + ' in zone database', echo=True)
            return obj

    # Save the zoning changes
    obj = brcdapi_zone.save(session, fid, checksum)
    if fos_auth.is_error(obj):
        brcdapi_zone.abort(session, fid)
        brcdapi_log.log('Failed to save zoning changes', echo=True)

    return obj


def replace_zoning_save(session, fab_obj, fid):
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
    :param eff_cfg: Name of the zone configuration to enable.
    :type eff_cfg: str
    :return: Object returned from FOS API
    :rtype: dict
    """
    # Get the checksum - this is needed to save the configuration.
    checksum, obj = brcdapi_zone.checksum(session, fid)
    if not fos_auth.is_error(obj):
        # Activate the zone configuration.
        obj = brcdapi_zone.enable_zonecfg(session, checksum, fid, eff_cfg)

    return obj
