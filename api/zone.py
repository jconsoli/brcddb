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

**Description**

Collection of zoning operations. The primary purpose is to enable zone configurations and to replace the zone database.

**Public Methods & Data**

Typically, only replace_zoning() and enable_zonecfg() are called externally.

+-------------------------------+-----------------------------------------------------------------------------------|
| Method                        | Description                                                                       |
+===============================+===================================================================================+
| build_alias_content           | Builds the alias dict structure to be converted to JSON and sent to a switch,     |
|                               |'zoning/defined-configuration', from a fabric object.                              |
+-------------------------------+-----------------------------------------------------------------------------------|
| build_zone_content            | Builds the zone dict structure to be converted to JSON and sent to a switch,      |
|                               | 'zoning/defined-configuration', from a fabric object.                            |
+-------------------------------+-----------------------------------------------------------------------------------|
| build_zonecfg_content         | Builds the zonecfg dict structure to be converted to JSON and sent to a switch,   |
|                               | 'zoning/defined-configuration', from a fabric object.                             |
+-------------------------------+-----------------------------------------------------------------------------------|
| build_all_zone_content        | Builds the zonecfg structure to be converted to JSON and sent to a switch,        |
|                               | 'brocade-zone/defined-configuration', from a fabric object. Calls                 |
|                               |  build_alias_content(), build_zone_content(), build_zonecfg_content().            |
+-------------------------------+-----------------------------------------------------------------------------------|
| plus_effective_zone_alias     | Makes a copy of fab_obj and adds zone and associated aliases that are in the      |
|                               | effective zone configuration that are not in fab_obj to the copy.                 |
+-------------------------------+-----------------------------------------------------------------------------------|
| replace_zoning                | Replaces the zoning database in a fabric by clearing it and then PATCHing it with |
|                               | a new zoning database                                                             |
+-------------------------------+-----------------------------------------------------------------------------------|
| enable_zonecfg                | Activates a zone configuration (make a zone configuration effective)              |
+-------------------------------+-----------------------------------------------------------------------------------|

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 03 Apr 2024   | Added plus_effective_zone_alias(). Added eff option to replace_zoning().              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 15 May 2024   | Fixed bad checksum in replace_zoning()                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '15 May 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.3'

import copy
import sys
import datetime
import brcdapi.log as brcdapi_log
import brcdapi.zone as brcdapi_zone
import brcddb.brcddb_fabric as brcddb_fabric
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.fos_auth as fos_auth
import brcdapi.util as brcdapi_util
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_common as brcddb_common
import brcddb.api.interface as api_int

_MAX_ZONE_SAVE_TRY = 12  # The maximum number of times to try saving zoning changes
_ZONE_SAVE_WAIT = 5  # Length of time to wait between fabric busy when saving zone changes

# Data for capture
_zone_uri_l = (
    'running/brocade-fibrechannel-switch/fibrechannel-switch',
    'running/brocade-interface/fibrechannel',
    'running/brocade-zone/defined-configuration',
    'running/brocade-zone/effective-configuration',
    'running/brocade-fibrechannel-configuration/zone-configuration',
    'running/brocade-fibrechannel-configuration/fabric',
)


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
    alias_l = list()
    for obj in fab_obj.r_alias_objects():
        members = obj.r_members()
        if len(members) > 0:
            alias_l.append({'alias-name': obj.r_obj_key(), 'member-entry': {'alias-entry-name': members}})
    if len(alias_l) > 0:
        wd.update(alias=alias_l)

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
    zone_l = list()
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
            zone_l.append(d)
        wd.update(zone=zone_l)

    return None if len(wd.keys()) == 0 else content


def build_zonecfg_content(fab_obj):
    """Builds the zonecfg dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :return: Dictionary of requests
    :rtype: dict
    """
    content = {'defined-configuration': dict()}
    wd = content['defined-configuration']

    # Add the zone configurations
    zonecfg_l = list()
    for obj in fab_obj.r_zonecfg_objects():
        if obj.r_obj_key() != '_effective_zone_cfg':
            members = obj.r_members()
            if len(members) > 0:
                zonecfg_l.append({'cfg-name': obj.r_obj_key(), 'member-zone': {'zone-name': members}})
    if len(zonecfg_l) > 0:
        wd.update(cfg=zonecfg_l)

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

    for key, method in dict(alias=build_alias_content, zone=build_zone_content, cfg=build_zonecfg_content).items():
        temp_content = method(fab_obj)
        if temp_content is not None:
            wd.update({key: temp_content.get('defined-configuration').get(key)})

    return content


def plus_effective_zone_alias(session, fab_obj, fid):
    """Makes a copy of fab_obj and adds zone and associated aliases that are in the effective zone configuration that
    are not in fab_obj to the copy.

    :param session: Login session object from brcdapi.brcdapi_rest.login()
    :type session: dict
    :param fab_obj: Fabric object of the fabric the zone database is being restored from.
    :type fab_obj: FabricObj
    :param fid: Fabric ID. If FID check is disabled, this must be the FID of the switch where the request is sent.
    :type fid: int
    :return error_l: Error messages.
    :rtype error_l: list
    :return fab_obj: A copy of fab_obj with zones and aliases in the effective zone. None if there are no zones or
        aliases to preserve.
    :rtype: FabricObj, None
    """
    global _zone_uri_l

    mod_flag, error_l = False, list()

    # Note: To avoid confusion, all objects from the target switch are preceeded with t_

    # Get a temorary proj_obj & fabric information for the target switch
    proj_obj = brcddb_project.new("Captured_data", datetime.datetime.now().strftime('%d %b %Y %H:%M:%S'))
    proj_obj.s_python_version(sys.version)
    proj_obj.s_description('Temporary project object for determining the effective zone configuration.')
    error_flag = api_int.get_batch(session, proj_obj, _zone_uri_l, fid=fid)
    buf = 'FID ' + str(fid) + ' does not exist in the target switch.'
    if not error_flag:
        return [buf], None
    try:  # If the FID doesn't exist we should never get here. try/except is just belt and suspenders.
        t_fab_obj = proj_obj.r_fabric_objs_for_fid(fid)[0]
    except IndexError:
        return [buf], None

    # Figure out what zones and aliases need to be preserved
    t_fab_obj = brcddb_fabric.copy_fab_obj(fab_obj, full_copy=True)  # The fabric object to return
    t_eff_zonecfg_obj = t_fab_obj.r_eff_zone_cfg_obj()
    if t_eff_zonecfg_obj is None:
        return list(), None
    for t_zone_obj in t_eff_zonecfg_obj.r_zone_objects():
        zone_obj = fab_obj.r_zone_obj(t_zone_obj.r_obj_key())
        if zone_obj is None:
            mod_flag = True
            t_fab_obj.s_add_zone(zone_obj.r_obj_key(),
                                 zone_obj.r_type(),
                                 zone_obj.r_name(),
                                 zone_obj.r_members(),
                                 zone_obj.r_pmembers())

    return list(), t_fab_obj if mod_flag else None



def replace_zoning(session, fab_obj, fid, eff=None):
    """Replaces the zoning database in a fabric and, optionally, enables a zone configuration. Keep in mind that FOS
        does not allow zones that are in the effective zone to be deleted. As a result, none of the aliases in those
        zones can be deleted. This function preserves zones and associated aliases that are in the effective zone
        configuration. If eff is set, that zone configuration is enabled and then the preserved zones and aliases are
        deleted.

     Relevant resource: 'zoning/defined-configuration'
     An error is returned if there is no zone database in the fab_obj. Use clear_zoning() to clear out zoning.

    :param session: Login session object from brcdapi.brcdapi_rest.login()
    :type session: dict
    :param fab_obj: Fabric object whose zone database will be sent to the switch. Must contatin at least one zone or
        alias.
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param fid: Fabric ID. If FID check is disabled, this must be the FID of the switch where the request is sent.
    :type fid: int
    :param eff: A zone configuration in fab_obj to enable after the zoning updates are completed.
    :return: Object returned from FOS API
    :rtype: dict
    """
    # Some basic error checking
    if eff is not None:
        if not isinstance(eff, str):
            brcdapi_log.exception('Invalid eff parameter type, ' + str(type(eff)) + str(eff), echo=True)
            return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST,
                                         'Invalid eff parameter',
                                         msg=['Expected type str', 'Received ' + str(type(eff))])
        if fab_obj.r_zonecfg_obj(eff) is None:
            return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST,
                                         'Effective zone configuration does not exist',
                                         msg=eff)

    # Get a fabric object with fab_obj + whaterver is in the effective zone configuration that is not in fab_obj
    error_l, fab_obj_eff = plus_effective_zone_alias(session, fab_obj, fid)
    if len(error_l) > 0:
        if len(error_l) == 0:
            error_l.append('Unknown error.')  # We should never get here.
        return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST, 'Could not replace zoning.', error_l)

    # Get the data structure to be converted to JSON and sent to the switch
    send_fab_obj = fab_obj if fab_obj_eff is None else fab_obj is fab_obj_eff
    content = build_all_zone_content(send_fab_obj)
    if content is None:
        return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST,
                                     'No zone database in ' + brcddb_fabric.best_fab_name(fab_obj.r_fabric_obj()),
                                     ['This function is not intended for clearing a zone database.',
                                      'Use brcdapi_zone.clear_zone() to clear the zone database.'])

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

    # Enable the effective zone or save the zoning changes
    if eff is not None:
        obj = brcdapi_zone.enable_zonecfg(session, checksum, fid, eff, echo=False)
        if fos_auth.is_error(obj):
            brcdapi_zone.abort(session, fid)
            return obj
        return replace_zoning(session, fab_obj, fid, eff=None)
    obj = brcdapi_zone.save(session, fid, checksum)
    if fos_auth.is_error(obj):
        brcdapi_zone.abort(session, fid)
        brcdapi_log.log('Failed to save zoning changes', echo=True)

    return obj


def enable_zonecfg(session, fid, eff_cfg):
    """Activates a zone configuration (make a zone configuration effective)

    :param session: Login session object from brcdapi.brcdapi_rest.login()
    :type session: dict
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
