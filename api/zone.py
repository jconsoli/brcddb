# Copyright 2020, 2021 Jack Consoli.  All rights reserved.
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

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 01 Nov 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '13 Feb 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

import brcdapi.zone as brcdapi_zone
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.api.interface as api_int
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.pyfos_auth as pyfos_auth
import brcddb.brcddb_common as brcddb_common

_MAX_ZONE_SAVE_TRY = 12  # The maximum number of times to try saving zoning changes
_ZONE_SAVE_WAIT = 5  # Length of time to wait between fabric busy when saving zone changes


def build_alias_content(fabObj):
    """Builds the alias dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fabObj: Fabric object
    :type fabObj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {
        'defined-configuration': {
        }
    }
    wd = content['defined-configuration']

    # Add the aliases
    l = []
    for obj in fabObj.r_alias_objects():
        members = obj.r_members()
        if len(members) > 0:
            l.append({'alias-name': obj.r_obj_key(), 'member-entry': {'alias-entry-name': members}})
    if len(l) > 0:
        wd.update({'alias': l})

    return None if len(wd.keys()) == 0 else content


def build_zone_content(fabObj):
    """Builds the zone dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fabObj: Fabric object
    :type fabObj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {
        'defined-configuration': {
        }
    }
    wd = content['defined-configuration']

    # Add the zones
    l = []
    for obj in fabObj.r_zone_objects():
        if obj.r_get('zone-type') is not brcddb_common.ZONE_TARGET_PEER:
            d = {'zone-name': obj.r_obj_key(), 'zone-type': obj.r_type(), 'member-entry': {}}
            me = d.get('member-entry')
            members = obj.r_members()
            if len(members) > 0:
                me.update({'entry-name': members})
            members = obj.r_pmembers()
            if len(members) > 0:
                me.update({'principal-entry-name': members})
            l.append(d)
        wd.update({'zone': l})

    return None if len(wd.keys()) == 0 else content


def build_zonecfg_content(fabObj):
    """Builds the zonecfg dict structure to be converted to JSON and sent to a switch, 'zoning/defined-configuration'

    :param fabObj: Fabric object
    :type fabObj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {
        'defined-configuration': {
        }
    }
    wd = content['defined-configuration']

    # Add the zone configurations
    l = []
    for obj in fabObj.r_zonecfg_objects():
        if obj.r_obj_key() != '_effective_zone_cfg':
            members = obj.r_members()
            if len(members) > 0:
                l.append({'cfg-name': obj.r_obj_key(), 'member-zone': {'zone-name': members}})
    if len(l) > 0:
        wd.update({'cfg': l})

    return None if len(wd.keys()) == 0 else content


def build_all_zone_content(fab_obj):
    """Builds the zonecfg structure to be converted to JSON and sent to a switch, 'brocade-zone/defined-configuration'

    :param fabObj: Fabric object
    :type fabObj: FabricObj
    :return: Dict of requests
    :rtype: dict
    """
    content = {
        'defined-configuration': {
        }
    }
    wd = content['defined-configuration']

    temp_content = build_alias_content(fab_obj)
    if temp_content is not None:
        wd.update({'alias': temp_content.get('defined-configuration').get('alias')})
    temp_content = build_zone_content(fab_obj)
    if temp_content is not None:
        wd.update({'zone': temp_content.get('defined-configuration').get('zone')})
    temp_content = build_zonecfg_content(fab_obj)
    if temp_content is not None:
        wd.update({'cfg': temp_content.get('defined-configuration').get('cfg')})

    return content


def replace_zoning(session, fab_obj, fid):
    """Replaces the zoning datbase in a fabric by clearing it and then PATCHing it with a new zoning database

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
        return pyfos_auth.create_error(400, 'No zone database in ' +
                                          brcddb_fabric.best_fab_name(obj.r_fabric_obj()), '')

    # Get the checksum - this is needed to save the configuration.
    checksum, obj = brcdapi_zone.checksum(session, fid, fab_obj)
    if pyfos_auth.is_error(obj):
        return obj

    # Clear the zone database
    obj = brcdapi_zone.clear_zone(session, fid)
    if not pyfos_auth.is_error(obj):
        # Send the zoning request
        obj = brcdapi_rest.send_request(session, 'brocade-zone/defined-configuration', 'PATCH', content, fid)
        if not pyfos_auth.is_error(obj):
            return brcdapi_zone.save(session, fid, checksum)

    # If we got this far, something went wrong so abort the transaction.
    brcdapi_zone.abort(session, fid)
    return obj
