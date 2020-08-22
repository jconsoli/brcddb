#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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

Primary Methods::

    +-------------------------------+-------------------------------------------------------------------------------+
    | Method                        | Description                                                                   |
    +===============================+===============================================================================+
    | zone_analysis()               | Analyzes zoning                                                               |
    +-------------------------------+-------------------------------------------------------------------------------+
    | build_zoning()                | Builds the dict structure to be passed to brcdapi_rest.api_request() to PATCH |
    |                               | 'zoning/defined-configuration'.                                               |
    +-------------------------------+-------------------------------------------------------------------------------+

Support Methods::

    +-------------------------------+-------------------------------------------------------------------------------+
    | Method                        | Description                                                                   |
    +===============================+===============================================================================+
    | best_fab_name()               | Returns the user friendly fabric name, optionally with the WWN of just the    |
    |                               | if a user friendly name wasn't defined.                                       |
    +-------------------------------+-------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | Removed unused varriables. Added check for when an alias is used in a zone but    |
    |           |               | the alias does not exists (ZONE_UNDEFINED_ALIAS)                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 22 Aug 2020   | Fixed check for logged in WWNs                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '22 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.2'

import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.app_data.bp_tables as bt
import brcddb.util.search as brcddb_search
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_login as brcddb_login

_MIN_SYMB_LEN = 10
# _speed_to_gen converts the brocade-name-server/link-speed to a fibre channel generation bump.
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
    :return: Fabridc name
    :rtype: str, None
    """
    buf = None
    if fab_obj is None:
        return 'Unknown'
    for switch_obj in fab_obj.r_switch_objects():  # The fabric information is stored with the switch
        # In some versions of FOS, this comes back as a dictionary and in others a list. I think it's supposed to always
        # be a dict.
        l = brcddb_util.convert_to_list(switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch'))
        for obj in l:
            buf = obj.get('fabric-user-friendly-name')
            if buf is not None:
                break
        if buf is not None:
            break
    if buf is None or buf == '':
        return fab_obj.r_obj_key()
    return buf + ' (' + fab_obj.r_obj_key() + ')' if wwn else buf


def alias_analysis(fabric_obj):
    """Analyzes the aliases in each fabric and adds an alert if any of the following conditions exist:
    * There are multiple identical aliases
    * The alias is not used
    * The alias contains no members

    :param fabric_obj: brcddb fabric object
    :type fabric_obj: FabricObj class
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
            bl = []
            for c_obj in alias_list:
                if c_obj != a_obj and len(c_obj.r_members()) == 1 and alias_members[0] == c_obj.r_members()[0]:
                    bl.append(c_obj.r_obj_key())
            if len(bl) > 0:
                a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_DUP_ALIAS, None, ', '.join(bl), None)


def wwn_zone_speed_check(fab_obj):
    """For each target, finds each server in the effective zone zoned to that target and alerts on speed differences

    Notes:

    * Although the problem is the same regardless of how it was zoned, d,i is almost exclusively for FICON and
      mainframe disk replication. The logic to determine this problem is the same but the method to pull the data out
      is different. It wasn't a huge time savings to skip accounting for d,i zones but since mainframe environments are
      typically very well structured (unlikely to have this problem) coupled with the fact that few mainframe people
      will run scripts like this in their environment led me to not bother with it.
    * Speed mis-matches with targets can be problematic as well. This method is limited to looking for server speed
      mis-matches only. The intent is to add checking for target speed mis-matches at a future date.
    * Any virtual device who's FC-4 type is both server and target are treated as targets. There isn't a good technical
      explanation for this. I just wasn't sure what to do with them at the time of this writting and treating them as
      targets was just a coding expedient.

    :param fab_obj: brcddb fabric object
    :type fab_obj: FabricObj class
    """
    global _speed_to_gen
    alert_d = [{}, {}]  # List in alert_d contains two dictionaries. alert_d[0] are the error level alerts and [1] are
                        # the warn level alerts. An error level alerts is 2 or more FC generations apart and a warn
                        # level alert is just one FC generation apart. The key for the dictionaries in this list are the
                        # WWNs of the faster (newer generation) server and the value is a dictionary whose key is the
                        # WWN of the slower server. The value in this dictionary is a list of target WWNs the two
                        # servers are zonedd to. The purpose of setting this up is to ensure duplicate alerts are not
                        # attached to the associated login objects. If the customer is following good zoning practices,
                        # duplicates should never happen but in practice, that's not always achievable.
    server_alert = [al.ALERT_NUM.LOGIN_SPEED_DIFF_E, al.ALERT_NUM.LOGIN_SPEED_DIFF_W]
    target_alert = [al.ALERT_NUM.LOGIN_SPEED_IMP_E, al.ALERT_NUM.LOGIN_SPEED_IMP_W]

    # Get a list of all the target (storage) logins
    t_obj_l = brcddb_search.match(fab_obj.r_login_objects(), 'brocade-name-server/fc4-features', 'Target',
                                 ignore_case=True, stype='regex-s')  # List of target objects
    t_wwn_l = [t_obj.r_obj_key() for t_obj in t_obj_l]  # List of the WWNs associated with the targets

    # For each target, find all servers zoned to it.
    for t_obj in t_obj_l:
        t_wwn = t_obj.r_obj_key()  # Store the target WWN we're working on in a local variable for effeciency
        l = []  # Working list of WWNs zoned to the target, t_obj
        
        # Determine all WWNs zoned to this target
        for z_obj in fab_obj.r_eff_zone_objects_for_wwn(t_wwn):
            if z_obj.r_is_di():  # Not checking d,i zones
                continue
            if z_obj.r_is_peer() or z_obj.r_is_target_driven():  # Is it a peer zone?
                if z_obj.r_has_pmember(t_wwn):  # If the target is a principal member, it's zoned to all the members
                    l.extend(z_obj.r_members())
                else:  # Otherwise, it's zoned to all the principal members
                    l.extend(z_obj.r_pmembers())
            else:  # It's a traditional zone
                l.extend(z_obj.r_members())
        if len(l) == 0:
            continue  # l is empty when t_wwn is not in the effective zone
        brcddb_util.remove_duplicates(l)
        wwn_list = [wwn for wwn in l if wwn not in t_wwn_l]

        # Figure out the FC speed generation difference between each login and the target. I toyed with a more effecient
        # algorithm but time is not of the essence here. Handling each possible FC generation keeps it simple.
        gen_l = [[] for i in range(0, len(_speed_to_gen))]
        try:
            t_gen = _speed_to_gen[t_obj.r_get('brocade-name-server/link-speed')]  # FC gen of the target
        except:
            continue  # Something went wrong in the data collection if we get here but stuff goes wrong sometimes
        for obj in [fab_obj.r_login_obj(wwn) for wwn in wwn_list if fab_obj.r_login_obj(wwn) is not None]:
            try:  # Mixed speeds only matter if they are slower than the storage, I think, so cap it at the target gen
                gen_l[min(_speed_to_gen[obj.r_get('brocade-name-server/link-speed')], t_gen)].append(obj)
            except:  # Name server data may not always be distributed throughout the fabric
                pass

        # Figure out if an alert is needed.
        for i in range(0, len(gen_l) - 1):

            # Get a list of server objects that are 2 or more FC generations apart (error level alerts) and a list of
            # server objects that are just one FC generation apart (warn level alerts).
            for obj in gen_l[i]:  # obj is the slower server (older gen)
                # Error lvel alerts - Any time there are multiple servers more then 2 FC generations apart
                l = [[], []]  # l[0] are the objects 2 or more gen levels apart and l[1] just one gen apart
                x = i + 2
                while x < len(gen_l):
                    l[0].extend(gen_l[x])
                    x += 1
                l[1] = gen_l[i+1] if i + 1 < len(gen_l) else []

                for x in range(0, len(l)):
                    for obj_n in l[x]:  # obj_n is the faster server (newer gen)
                        wwn = obj_n.r_obj_key()  # wwn is the faster server (newer gen)
                        if wwn == obj.r_obj_key():
                            continue  # This can happen because server speed is capped at the storage speed. The same
                                      # server zoned to two different storage devices can result in the same server
                                      # appearing to be two different speeds.
                        if wwn in alert_d[x]:
                            a_obj = alert_d[x].get(wwn)
                        else:
                            a_obj = {}
                            alert_d[x].update({wwn: a_obj})
                        wwn = obj.r_obj_key()
                        tl = a_obj.get(wwn)
                        if tl is None:
                            tl = []
                            a_obj.update({wwn: tl})
                        if t_wwn not in tl:
                            tl.append(t_wwn)

    # Now add the alerts
    for x in range(0, len(alert_d)):
        d = alert_d[x]
        for wwn in d.keys():  # wwn is the faster (newer gen) server WWN
            sd = d.get(wwn)
            for s_wwn in sd.keys():  # s_wwn is the slower server WWN
                p0 = brcddb_login.best_login_name(fab_obj, s_wwn, True)
                l = []
                for t_wwn in sd.get(s_wwn):
                    fab_obj.r_login_obj(t_wwn).s_add_alert(al.AlertTable.alertTbl, target_alert[x], None, p0, \
                                                           brcddb_login.best_login_name(fab_obj, wwn, True))
                    l.append(brcddb_login.best_login_name(fab_obj, t_wwn, True))
                fab_obj.r_login_obj(wwn).s_add_alert(al.AlertTable.alertTbl, server_alert[x], None, p0, ', '.join(l))


def zone_analysis(fab_obj):
    """Analyzes zoning. Finds where all members are. Adds an alert if any of the following conditions exist:
    * Calls alias_analysis() - additional alias checking
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

    :param fab_obj: brcddb fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    """
    # To-Do: Break this up into multiple methods or review to shorten. This is way too long
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
        pmem_list = []  # pmem_list and nmem_list was an after thought to save time resolving them again in the
        nmem_list = []  # effective zone to defined zone comparison. These are de-referenced (alias converted to WWN)
        flag &= ~(_IN_DEFINED_ZONECFG | _WWN_IN_ZONE | _ALIAS_IN_ZONE | _DI_IN_ZONE)

        # Check for d,i zones, mixed d,i & WWN zones, and make sure the member is in the fabric
        for i in range(0, 2):   # 0 - Get the members, 1 - get the principal members
            zmem_list = zone_obj.r_members() if i == 0 else zone_obj.r_pmembers()
            for zmem in zmem_list:
                if brcddb_util.is_wwn(zmem):
                    flag |= _WWN_MEM | _WWN_IN_ZONE
                    mem_list = [zmem]
                else:
                    flag &= ~_WWN_MEM
                    flag |= _ALIAS_IN_ZONE
                    a_obj = fab_obj.r_alias_obj(zmem)
                    if a_obj is None:
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_UNDEFINED_ALIAS, None, zmem,
                                             zone_obj.r_obj_key())
                        mem_list = []
                    else:
                        mem_list = a_obj.r_members()
                for mem in mem_list:
                    if i == 0:
                        nmem_list.append(mem)
                    else:
                        pmem_list.append(mem)
                    # FOS won't allow the user to configure a bad zone member so it's either d,i or WWN
                    if brcddb_util.is_di(mem):
                        # It's a d,i member - typically FICON
                        flag |= _DI_IN_ZONE
                        t = mem.split(',')
                        zone_obj.s_or_flags(brcddb_common.zone_flag_di)
                        found_flag = False
                        for switch_obj in fab_obj.r_switch_objects():
                            if isinstance(switch_obj.r_get('domain_id'), int) and switch_obj.r_get('domain_id') == t[0]:
                                found_flag = True
                                break
                        if not found_flag:
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)
                    else:
                        # It's a WWN
                        zone_obj.s_or_flags(brcddb_common.zone_flag_wwn)
                        if flag & _WWN_MEM and len(fab_obj.r_alias_for_wwn(mem)) > 0:
                            # An alias was defined for this WWN, but the WWN was used to define the zone
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ALIAS_USE, None, mem,
                                               ', '.join(fab_obj.r_alias_for_wwn(mem)))
                        # Is the member in this fabric?
                        if fab_obj.r_port_obj(mem) is None:
                            # Is it in a different fabric?
                            port_list = brcddb_util.global_port_list(other_fabrics, mem)
                            if len(port_list) > 0:
                                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_DIFF_FABRIC, None, mem,
                                                     best_fab_name(port_list[0].r_fabric_obj()))
                            else:
                                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)

        # Do all the zone membership count checks
        if zone_obj.r_is_peer():
            if len(pmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_PMEM)
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_NMEM)
        else:
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NO_MEMBERS)
            elif len(nmem_list) == 1:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ONE_MEMBER)
        if zone_obj.r_is_wwn() and zone_obj.r_is_di():
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MIXED)

        # Check for single initiator zoning.
        elist = []
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
        if flag & _WWN_IN_ZONE and flag & _ALIAS_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_WWN_ALIAS)

        # Make sure the defined zone matches the effective zone
        effZoneObj = fab_obj.r_eff_zone_obj(zone_obj.r_obj_key())
        if effZoneObj is not None:
            zone_obj.s_or_flags(brcddb_common.zone_flag_effective)
            if set(effZoneObj.r_pmembers()) != set(pmem_list):
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                flag |= _ZONE_MISMATCH
            if set(effZoneObj.r_members()) != set(nmem_list):
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                flag |= _ZONE_MISMATCH

    if flag & _ZONE_MISMATCH:
        try:
            fab_obj.r_defined_eff_zonecfg_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
        except:
            pass  # Defined configuration was deleted - I'm not certian FOS allows it so this is just to be sure

    for login_obj in fab_obj.r_login_objects():
        wwn = login_obj.r_obj_key()

        # Make sure that all logins are zoned.
        if len(fab_obj.r_zones_for_wwn(wwn)) > 0:
            if wwn in fab_obj.r_base_logins():
                login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_BASE_ZONED)
        else:
            login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_NOT_ZONED)

        # Check zone participation
        port_obj = login_obj.r_port_obj()
        buf = login_obj.r_get('port-properties')
        if buf is not None and buf in special_login:
            login_obj.s_add_alert(al.AlertTable.alertTbl, special_login[buf])
            continue
        # Figure out how many devices are zoned to this device
        eList = []  # List of effective zones this login participates in
        for zone_obj in fab_obj.r_eff_zone_objects_for_wwn(wwn):
            if zone_obj.r_is_peer():
                if wwn in zone_obj.r_pmembers():
                    eList.extend(zone_obj.r_members())
                else:
                    eList.extend(zone_obj.r_members())
            else:
                eList.extend(zone_obj.r_members())
        if wwn in eList:  # If it's not zoned, it's not in eList
            eList.remove(wwn)
        if len(eList) > bt.MAX_ZONE_PARTICIPATION:
            login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_MAX_ZONE_PARTICIPATION, None,
                                  bt.MAX_ZONE_PARTICIPATION)

    # Alias analysis
    alias_analysis(fab_obj)

    # Zone speed analysis
    wwn_zone_speed_check(fab_obj)
