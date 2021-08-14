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
:mod:`brcddb_fabric` - Fabric level utilities. Primarily:

    * Add FOS RESTConf requested fabric information (fabric, name server, and FDMI) to brcddb class objects
    * Analyze zoning

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-7   | 17 Apr 2021   | Added switch_for_did(), fab_obj_for_name(), and miscellaneous bug fixes.          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 17 Jul 2021   | Added check_ficon_zoning() and fixed buf in count of servers zoned to each target.|
    |           |               | Added zone_by_target()                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 07 Aug 2021   | Return fabric WWN in best_fab_name() if wwn=False but the fabric is not named.    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 14 Aug 2021   | Commented out alert for LOGIN_BASE_ZONED.                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '14 Aug 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.0'

import pprint
import brcdapi.log
import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.app_data.bp_tables as bt
import brcddb.util.search as brcddb_search
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_login as brcddb_login
import brcddb.brcddb_port as brcddb_port
import brcddb.util.iocp as brcddb_iocp
import brcddb.brcddb_zone as brcddb_zone

_MIN_SYMB_LEN = 10
_CHECK_PEER_PROPERTY = True if bt.custom_tbl.get('peer_property') is None else bt.custom_tbl.get('peer_property')
_CHECK_ZONE_MISMATCH = True if bt.custom_tbl.get('zone_mismatch') is None else bt.custom_tbl.get('zone_mismatch')
# _speed_to_gen converts the brocade-name-server/link-speed to a fibre channel generation bump.
# $ToDo - Check below. It looks off by 1.
_speed_to_gen = {'1G': 0, '2G': 1, '4G': 2, '8G': 3, '16G': 4, '32G': 5, '64G': 6, '128G': 7}
special_login = {
    'SIM Port': al.ALERT_NUM.LOGIN_SIM,
    # Should never get 'I/O Analytics Port' because I check for AE-Port but rather than over think it...
    'I/O Analytics Port': al.ALERT_NUM.LOGIN_AMP,
}


def best_fab_name(fab_obj, wwn=False):
    """Returns the user friendly fabric name, optionally with the WWN of just the WWN if a user friendly name wasn't
    defined.

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :param wwn: If True, append (wwn) to the fabric name
    :type wwn: bool
    :return: Fabric name
    :rtype: str, None
    """
    if fab_obj is None:
        return 'Unknown'
    for switch_obj in fab_obj.r_switch_objects():  # The fabric information is stored with the switch
        buf = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/fabric-user-friendly-name')
        if buf is not None and len(buf) > 0:
            return buf + ' (' + fab_obj.r_obj_key() + ')' if wwn else buf

    return fab_obj.r_obj_key()


def switch_for_did(fab_obj, did):
    """Returns the switch object in a fabric for a specified DID.

    :param fab_obj: Fabric object
    :type fab_obj: FabricObj
    :param did: Domain ID
    :type did: int
    :return: Switch object matching did. None if not found
    :rtype: brcddb.classes.switch.SwitchObj, None
    """
    if fab_obj is None:
        return None
    for switch_obj in fab_obj.r_switch_objects():  # The fabric information is stored with the switch
        switch_did = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/domain-id')
        if isinstance(switch_did, int) and switch_did == did:
            return switch_obj

    return None


def alias_analysis(fabric_obj):
    """Analyzes the aliases in each fabric and adds an alert if any of the following conditions exist:
    * There are multiple identical aliases
    * The alias is not used
    * The alias contains no members

    :param fabric_obj: brcddb fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    """
    alias_list = fabric_obj.r_alias_objects()
    for a_obj in alias_list:
        alias_members = a_obj.r_members()
        zone_list = a_obj.r_zone_objects()
        if len(zone_list) == 0:  # is the alias used?
            a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ALIAS_NOT_USED, None, None, None)
        if len(alias_members) == 0:  # Does the alias have any members?
            if len(zone_list) == 0:
                a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NULL_ALIAS, None, None, None)
            else:
                a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NULL_ALIAS_USED, None, \
                                  ', '.join([zone_obj.r_obj_key() for zone_obj in zone_list]), None)
        elif len(alias_members) == 1:  # Duplicate alias? Keeping it simple by only checking 1 member per alias
            alias_name = a_obj.r_obj_key()
            bl = list()
            for c_obj in alias_list:
                mem = c_obj.r_members()[0] if len(c_obj.r_members()) == 1 else None
                if c_obj.r_obj_key() != alias_name and len(c_obj.r_members()) == 1 and \
                        alias_members[0] == c_obj.r_members()[0]:
                    bl.append(c_obj.r_obj_key())
            if len(bl) > 0:
                a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_DUP_ALIAS, None, ', '.join(bl),
                                  a_obj.r_members()[0])


def check_ficon_zoning(fabric_obj):
    """Check to make sure all control units in the channel path share a zone with the channel

    :param fabric_obj: brcddb fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    """
    for iocp_obj in fabric_obj.r_project_obj().r_iocp_objects():
        cec_sn = brcddb_iocp.full_cpc_sn(iocp_obj.r_obj_key())  # The SN is always the same for each IOCP
        for tag, d in iocp_obj.r_path_objects().items():  # For every defined path

            # Find the port objects for the CHPID and get a list of zones the CHPID is in
            chpid_port_obj = brcddb_port.port_obj_for_chpid(fabric_obj, cec_sn, tag)
            if chpid_port_obj is None:
                continue
            chpid_zone_l = fabric_obj.r_zones_for_di(chpid_port_obj.r_switch_obj().r_did(), chpid_port_obj.r_index())

            # For each link address, get the corresponding port object and check for at least one common zone
            for link_addr in d['link']:

                # Get the port object for the port corresponding to the link address
                port_obj = brcddb_port.port_obj_for_addr(fabric_obj, '0x' + link_addr + '00')
                if port_obj is None:
                    chpid_port_obj.s_add_alert(al.AlertTable.alertTbl,
                                               al.ALERT_NUM.ZONE_LINK_NO_ADDR,
                                               None,
                                               iocp_obj.r_obj_key(),
                                               tag)
                    continue

                # See if the port for the link address and port for the CHPID share a zone
                not_found = True
                for zone in fabric_obj.r_zones_for_di(port_obj.r_switch_obj().r_did(), port_obj.r_index()):
                    if zone in chpid_zone_l:
                        not_found = False
                        break
                if not_found:
                    port_obj.s_add_alert(al.AlertTable.alertTbl,
                                         al.ALERT_NUM.ZONE_LINK_ADDR,
                                         None,
                                         iocp_obj.r_obj_key(),
                                         tag)

    return


def zone_by_target(fab_obj):
    """Finds all servers in the effective zone that are zoned to each target, does a speed check, and adds
    _zoned_servers to each target login object. _zoned_servers is a dictionary. Key = server WWN, value = list of zones
    that server and target are in.

    :param fab_obj: brcddb fabric object
    :type fab_obj: FabricObj class
    """
    global _speed_to_gen

    # Get a list of all the target (storage) logins
    t_obj_l = brcddb_search.match(fab_obj.r_login_objects(), 'brocade-name-server/fc4-features', 'Target',
                                  ignore_case=True, stype='regex-s')  # List of target objects in the fabric

    for t_login_obj in t_obj_l:

        # Get the target port object and speed
        t_wwn = t_login_obj.r_obj_key()
        t_port_obj = t_login_obj.r_port_obj()
        x = None if t_port_obj is None else t_port_obj.r_get('_search/speed')
        t_speed = x if isinstance(x, (int, float)) else 0

        # Get a list of all the server login objects zoned to this target
        s_wwn_l = brcddb_zone.eff_zoned_to_wwn(fab_obj, t_wwn, target=False, initiator=True)
        if len(s_wwn_l) > bt.MAX_ZONE_PARTICIPATION:
            t_login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MAX_PARTICIPATION)
        t_login_obj.s_new_key('_zoned_servers', s_wwn_l)

        # Figure out what all the login speeds of the target and servers zoned to this target
        s_speed_l = list()
        for s_login_obj in brcddb_util.remove_none([fab_obj.r_login_obj(wwn) for wwn in s_wwn_l]):
            s_port_obj = s_login_obj.r_port_obj()
            x = None if s_port_obj is None else s_port_obj.r_get('_search/speed')
            if isinstance(x, (int, float)):
                s_speed_l.append(dict(obj=s_login_obj, s=x))

        # Perform speed checks and add alerts when applicable
        alert_l = [obj.alert_num() for obj in t_login_obj.r_alert_objects()]
        speed_l = [d['s'] for d in s_speed_l]
        if len(speed_l) > 0:
            max_s_speed = max(speed_l)
            min_s_speed = min(speed_l)
            if min_s_speed != max_s_speed and al.ALERT_NUM.LOGIN_MIXED_SPEED_T not in alert_l:
                t_login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_MIXED_SPEED_T)
            if max_s_speed > t_speed and al.ALERT_NUM.LOGIN_FASTER_S not in alert_l:
                t_login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_FASTER_S)

    return


def zone_analysis(fab_obj):
    """Analyzes zoning. Finds where all members are. Adds an alert if any of the following conditions exist:
    * Calls alias_analysis() - multiple identical aliases, unused alias, and alias with no members
    * Calls zone_by_target() - Checks for speed mismatches, potential slow drain device
    * Zone has less than 2 members
    * Peer zone doesn't have at least one principal and one regular member
    * Mixed d,i and WWN zones
    * Zone member in another fabric
    * Zone is not used in any zone configuration
    * Effective zone doesn't match defined zone
    * Zone member not found
    * Base port (HBA) of NPIV logins is in a zone
    * Maximum number of devices zoned to a device. See brcddb.app_data.bp_tables.MAX_ZONE_PARTICIPATION
    * Mix of WWN and alias in the same zone
    * Peer zone property member in zone
    * Duplicate aliases
    * Calls check_ficon_zoning() - Ensures all CHPID paths are in the same zone as the CHPID

    :param fab_obj: brcddb fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    """
    global _CHECK_ZONE_MISMATCH, _CHECK_PEER_PROPERTY

    # $ToDo - Break this up into multiple methods or review to shorten. This is way too long
    _WWN_MEM = 0b1  # The member was entered as a WWN or d,i, not an alias
    _WWN_IN_ZONE = _WWN_MEM << 1  # A zone contains a WWN member
    _ALIAS_IN_ZONE = _WWN_IN_ZONE << 1  # A zone contains an alias member
    _DI_IN_ZONE = _ALIAS_IN_ZONE << 1  # The zone contains a d,i member
    _IN_DEFINED_ZONECFG = _DI_IN_ZONE << 1  # Zone found in defined zone
    _ZONE_MISMATCH = _IN_DEFINED_ZONECFG << 1  # The effective zone does not match the defined zone

    # We'll need to figure out where all the logins are so build a table to cross-reference all the neighbor WWNs
    brcddb_util.build_login_port_map(fab_obj.r_project_obj())
    other_fabrics = fab_obj.r_project_obj().r_fabric_objects()
    other_fabrics.remove(fab_obj)
    flag = 0b0

    # Zone analysis
    for zone_obj in fab_obj.r_zone_objects():
        pmem_list = list()  # pmem_list and nmem_list was an after thought to save time resolving them again in the
        nmem_list = list()  # effective zone to defined zone comparison. These are the aliases converted to WWN
        flag &= ~(_IN_DEFINED_ZONECFG | _WWN_IN_ZONE | _ALIAS_IN_ZONE | _DI_IN_ZONE)

        # Is the zone used in any configuration?
        if len(zone_obj.r_zone_configurations()) == 0:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_USED, None, None, None)

        # Check for mixed d,i & WWN zones and make sure the member is in the fabric
        for i in range(0, 2):   # 0 - Get the members, 1 - get the principal members
            mem_list = list()
            zmem_list = zone_obj.r_members() if i == 0 else zone_obj.r_pmembers()
            for zmem in zmem_list:
                if brcddb_util.is_wwn(zmem, full_check=False):
                    flag |= _WWN_MEM
                    mem_list.append(zmem)
                    if len(fab_obj.r_alias_for_wwn(zmem)) > 0:
                        # An alias was defined for this WWN, but the WWN was used to define the zone
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ALIAS_USE, None, zmem,
                                             ', '.join(fab_obj.r_alias_for_wwn(zmem)))
                elif brcddb_util.is_di(zmem):
                    mem_list.append(zmem)
                else:  # It must be an alias
                    flag |= _ALIAS_IN_ZONE
                    a_obj = fab_obj.r_alias_obj(zmem)
                    if a_obj is None:
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_UNDEFINED_ALIAS, None, zmem,
                                             zone_obj.r_obj_key())
                    else:
                        mem_list.extend(a_obj.r_members())

            for mem in mem_list:
                if i == 0:
                    nmem_list.append(mem)
                else:
                    pmem_list.append(mem)

                if brcddb_util.is_di(mem):
                    flag |= _DI_IN_ZONE  # It's a d,i member - typically FICON
                    t = mem.split(',')

                    # Is it in the fabric?
                    found_flag = False
                    for switch_obj in fab_obj.r_switch_objects():
                        if isinstance(switch_obj.r_get('domain_id'), int) and switch_obj.r_get('domain_id') == t[0]:
                            found_flag = True
                            break
                    if not found_flag:
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)

                elif brcddb_util.is_wwn(mem, full_check=False):
                    flag |= _WWN_IN_ZONE
                    if _CHECK_PEER_PROPERTY and not brcddb_util.is_wwn(zmem, full_check=True):
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_PROPERTY, None, zmem, None)
                    # Is the member in this fabric?
                    if fab_obj.r_port_obj(mem) is None:
                        # Is it in a different fabric?
                        port_list = brcddb_util.global_port_list(other_fabrics, mem)
                        if len(port_list) > 0:
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_DIFF_FABRIC, None, mem,
                                                 best_fab_name(port_list[0].r_fabric_obj()))
                        else:
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)
                else:
                    brcdapi.log.exception('Zone member type undetermined: ' + str(mem), True)

        # Do all the zone membership count checks
        if zone_obj.r_is_peer():  # It's a peer zone
            # Make sure there is at least one member and one principal member
            if len(pmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_PMEM)
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_NMEM)
        else:  # It's an old style zone (not a peer zone)
            # Make sure there are at least 2 members
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NO_MEMBERS)
            elif len(nmem_list) == 1:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ONE_MEMBER)
        if flag and ():
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MIXED)

        # Check for single initiator zoning.
        elist = list()
        if zone_obj.r_is_peer():
            for wwn in pmem_list:
                login_obj = fab_obj.r_login_obj(wwn)
                if login_obj is not None:
                    if login_obj.r_get('brocade-name-server/name-server-device-type') == 'Initiator':
                        elist.append(wwn)
                        break
            for wwn in nmem_list:
                login_obj = fab_obj.r_login_obj(wwn)
                if login_obj is not None:
                    if login_obj.r_get('brocade-name-server/name-server-device-type') == 'Initiator':
                        elist.append(wwn)
                        break
        else:
            for wwn in nmem_list:
                login_obj = fab_obj.r_login_obj(wwn)
                if login_obj is not None:
                    if login_obj.r_get('brocade-name-server/name-server-device-type') == 'Initiator':
                        elist.append(wwn)
        if len(elist) > 1:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MULTI_INITIATOR, None,
                                 ', '.join(elist))

        # Check for mixed zone members
        if flag & _DI_IN_ZONE and flag & _WWN_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MIXED)
        if flag & _WWN_MEM and flag & _ALIAS_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_WWN_ALIAS)

        # Make sure the defined zone matches the effective zone
        if _CHECK_ZONE_MISMATCH:
            eff_zone_obj = fab_obj.r_eff_zone_obj(zone_obj.r_obj_key())
            if eff_zone_obj is not None:
                zone_obj.s_or_flags(brcddb_common.zone_flag_effective)
                if set(eff_zone_obj.r_pmembers()) != set(pmem_list):
                    zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                    flag |= _ZONE_MISMATCH
                if set(eff_zone_obj.r_members()) != set(nmem_list):
                    zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                    flag |= _ZONE_MISMATCH

    if flag & _ZONE_MISMATCH and _CHECK_ZONE_MISMATCH:
        try:
            fab_obj.r_defined_eff_zonecfg_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
        except:
            pass  # Defined configuration was deleted - I'm not certian FOS allows it so this is just to be sure

    for login_obj in fab_obj.r_login_objects():
        wwn = login_obj.r_obj_key()

        # Make sure that all logins are zoned.
        if len(fab_obj.r_zones_for_wwn(wwn)) > 0:
            if wwn in fab_obj.r_base_logins():
                pass  # I need to think this through
                # login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_BASE_ZONED)
        elif wwn not in fab_obj.r_base_logins():
            login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_NOT_ZONED)

        # Check zone participation
        port_obj = login_obj.r_port_obj()
        buf = login_obj.r_get('port-properties')
        if buf is not None and buf in special_login:
            login_obj.s_add_alert(al.AlertTable.alertTbl, special_login[buf])
            continue

    # Alias analysis, zone speed analysis, and FICON analysis
    alias_analysis(fab_obj)
    zone_by_target(fab_obj)
    check_ficon_zoning(fab_obj)


def fab_obj_for_name(proj_obj, fab_name):
    """Finds the first fabric matching the user friendly fabric name

    :param proj_obj: brcddb project object
    :type proj_obj: brcddb.classes.project.ProjObj
    :param fab_name: Fabric user friendly name
    :type fab_name: str
    :return: brcddb fabric object. None if not found
    :rtype: brcddb.classes.fabric.FabricObj, None
    """
    for fab_obj in proj_obj.r_fabric_objects():
        for switch_obj in fab_obj.r_switch_objects():  # The fabric name is returned with
            buf = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/fabric-user-friendly-name')
            if buf is not None and buf == fab_name:
                return fab_obj

    return None  # If we got this far, we didn't find it


def fab_fids(fab_obj):
    """Returns a list of FIDs in a fabric. Note that there can be multiple FIDs if FID check is disabled

    :param fab_obj: Fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :return: List of FIDs as int
    :rtype: list
    """
    rl = list()
    for switch_obj in fab_obj.r_switch_objects():
        fid = switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id')
        if fid is not None and fid not in rl:
            rl.append(fid)

    return rl
