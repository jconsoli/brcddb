"""
Copyright 2023, 2024, 2025, 2026 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Common fabric related functions.

Important note about FICON zones:

The zone_* functions were originally private functions in mf_zone.py, which is used to build a zone configuration
workbook for use with zone_config.py. See zone_config_sample.xlsx. I later needed to be able to create zones without
zone_config.py. The workbook therefore isn't always needed. Rather than modify working code, I left everything as is.
This is also why the dictionaries contain keys with upper case letters and spaces. Those keys are used as headers in the
workbooks and decision trees. DO NOT CHANGE KEY NAMES!

The zone_* functions return a list of dictionaries as described below. The list can be passed directly to
brcddb.brcddb_zone.add_zone_worksheet(). Keys that are unused or not applicable for the Zone_Object may not be present,
so use .get() to retrieve the values. Zone_Object is the only required key.

+-------------------+-----------+-----------------------------------------------------------------------------------+
| Key               | Type      | Description                                                                       |
+===================+===========+===================================================================================+
| Action            | None,str  | As of September 2026, "create" was the only action used or tested. Intended for   |
|                   |           | the following actions:                                                            |
|                   |           | Action        Intended Purpose                                                    |
|                   |           | add_mem       Adds a member to an alias, zone, or zone configuration membership   |
|                   |           |               list.                                                               |
|                   |           | copy          Copies an alias, zone, or zone configuration. "Member" is the name  |
|                   |           |               of the zone object to copy.                                         |
|                   |           | create        Creates an alias, zone, or zone configuration.                      |
|                   |           | delete        Deletes an alias, zone, or zone configuration. The effective zone   |
|                   |           |               configuration cannot be deleted.                                    |
|                   |           | full_purge    Performs a "purge" action. Any empty zone or zone configuration     |
|                   |           |               that is not the effective zone configuration as a result of the     |
|                   |           |               purge is also deleted.                                              |
|                   |           | ignore        If the Zone_Object is alias, replaces all instances of the alias    |
|                   |           |               (WWN or d,i) specified in the "Member" cell with what is specified  |
|                   |           |               in the "Principal Member" cell in every zone where used. Similarly, |
|                   |           |               if the Zone_Object is zone, zones are replaced in every zone        |
|                   |           |               configuration where used.                                           |
|                   |           | purge         Supported for alias and zone Zone_Object only. The value in the     |
|                   |           |               "Member" cell is used to define the alias or zone for the purge     |
|                   |           |               action to act on. This is the equivalent to the CLI                 |
|                   |           |               zoneobjectexpunge command. The advantage is that wild card and      |
|                   |           |               regex matching can be used which make it convenient for             |
|                   |           |               decommissioning servers and storage arrays.                         |
|                   |           | remove_mem    Removes members from the zone object. The same rules regarding      |
|                   |           |               "Members" and "Principal Members" in add_mem apply.                 |
|                   |           | rename        Future consideration. Not implemented yet. Rename the zone object   |
|                   |           |               in the "Name" cell with the name in the "Member" cell.              |
|                   |           | replace       For alias, replaces all instances of the alias (WWN or d,i)         |
|                   |           |               specified in the "Member" cell with what is specified in the        |
|                   |           |               "Principal Member" cell in every zone where used. Similarly, zones  |
|                   |           |               are replaced in every zone configuration where used.                |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| Comments          | None,str, | Additional detail about the zone object. As of September 2026, comments were only |
|                   | list      | used in the zone configuration workbooks generated by mf_zone.py.                 |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| Zone_Object       | str       | The zone object type as follows:
|                   |           | Zone Object   Description                                                         |
|                   |           | alias         Alias. Members are in "Members".                                    |
|                   |           | comment       Comments only associated with the zone object specified in "Name".  |
|                   |           |               All other keys are ignored.                                         |
|                   |           | peer_zone     Peer zone. Members are in "Members". Principal members are in       |
|                   |           |               "Principal Members"                                                 |
|                   |           | zone          Standard zone. Members are in "Members".                            |
|                   |           | zone_cfg      Zone configuration. Members are in "Members"                        |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| Name              | str       | The name of the zone object.                                                      |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| Member            | list      | The members of the zone object.                                                   |
+-------------------+-----------+-----------------------------------------------------------------------------------+
| Principal Member  | list      | The principal members of the zone object. Only relevant for peer zones.           |
+-------------------+-----------+-----------------------------------------------------------------------------------+

**Public Methods & Data**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| alias_analysis        | Analyzes the aliases in each fabric and adds an alert if any of the following             |
|                       | conditions exist:                                                                         |
|                       |   * There are multiple identical aliases                                                  |
|                       |   * The alias is not used                                                                 |
|                       |   * The alias contains no members                                                         |
+-----------------------+-------------------------------------------------------------------------------------------+
| aliases_by_name       | Returns a list of aliases defined in the fabric matching the search criteria.             |
+-----------------------+-------------------------------------------------------------------------------------------+
| best_fab_name         | Returns the user friendly fabric name, optionally with the WWN of just the WWN if a user  |
|                       | friendly name wasn't defined.                                                             |
+-----------------------+-------------------------------------------------------------------------------------------+
| check_ficon_zoning    | Check to make sure all control units in the channel path share a zone with the channel    |
+-----------------------+-------------------------------------------------------------------------------------------+
| copy_fab_obj          | Makes a copy of a fabric object                                                           |
+-----------------------+-------------------------------------------------------------------------------------------+
| fab_match             | Returns a list of WWNs matching the search criteria                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| fab_fids              | Returns a list of FIDs in a fabric. Note that there can be multiple FIDs if FID check     |
|                       | is disabled                                                                               |
+-----------------------+-------------------------------------------------------------------------------------------+
| fab_obj_for_name      | Finds the first fabric matching the user friendly fabric name                             |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficon_zone_all        | FICON. Returns a list with a single zone dictionary including all ports except ICL ports. |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficon_zone_all_f      | FICON. Returns a zone dictionary with a single zone that includes all F ports.            |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficon_zone_by_device  | FICON. Returns a list of zones for each CHPID with access to all control units.           |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficon_zone_by_channel | FICON. Returns a list of zones for each CHPID with access to only to the link addresses,  |
|                       | LINK=.                                                                                    |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficon_zone_fab_obj    | Adds zoning information in zdb_l to the fabric object, fab_obj, for use with              |
|                       | brcddb.api.zone.replace_zoning()                                                          |
+-----------------------+-------------------------------------------------------------------------------------------+
| switch_for_did        | Returns the switch object in a fabric for a specified DID.                                |
+-----------------------+-------------------------------------------------------------------------------------------+
| rnid_groups           | Sorts out the mainframe attachments by control unit and channel.                          |
+-----------------------+-------------------------------------------------------------------------------------------+
| unique_alias_name     | Ensure that an alias name is unique by appending a number if a alias name is already used |
+-----------------------+-------------------------------------------------------------------------------------------+
| unique_zone_name      | Ensure that a zone name is unique by appending a number if a zone name is already used.   |
+-----------------------+-------------------------------------------------------------------------------------------+
| unique_zonecfg_name   | Ensure that a zone configuration name is unique by appending a number if a zonecfg name   |
|                       | is already used.                                                                          |
+-----------------------+-------------------------------------------------------------------------------------------+
| zone_analysis         | Analyzes zoning. Finds where all members are. Adds an alert if any issues found. See      |
|                       | method header for details of what checks are preformed.                                   |
+-----------------------+-------------------------------------------------------------------------------------------+
| zone_merge_group      | Determines all logins that would be effected a result of removing a WWN from a fabric     |
+-----------------------+-------------------------------------------------------------------------------------------+
| zone_by_target        | Finds all servers in the effective zone that are zoned to each target, does a speed check,|
|                       | and adds _zoned_servers to each target login object. _zoned_servers is a dictionary.      |
|                       | Key = server WWN, value = list of zones that server and target are in.                    |
+-----------------------+-------------------------------------------------------------------------------------------+
| zone_by_name          | Returns a list of zones defined in the fabric matching the search criteria                |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Added aliases_by_name()                                                               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 09 Mar 2024   | Added missing documentation for aliases_by_name()                                     |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 03 Apr 2024   | Updated documentation.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 15 May 2024   | Added  zone_by_name()                                                                 |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 20 Oct 2024   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 06 Dec 2024   | Removed duplicate formatting of CEC serial number.                                    |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.7     | 25 Aug 2025   | Added support for checking zones with WWN members, wwn_in_zone.                       |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.8     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.9     | 20 Feb 2026   | Added additional debug information for exceptions.                                    |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.0     | 01 Aug 2026   | Modified best_fab_name() to accept fabric, switch, port, or login objects.            |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.1     | 26 Oct 2026   | Moved private functions from mf_zone.py to here so that they could be used by other   |
|           |               | modules. Added ficon_zone_fab_obj()                                                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025, 2026 Jack Consoli'
__date__ = '26 Oct 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.1.1'

import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.brcddb_switch as brcddb_switch
import brcddb.util.util as brcddb_util
import brcddb.util.search as brcddb_search
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_port as brcddb_port
import brcddb.util.iocp as brcddb_iocp
import brcddb.brcddb_zone as brcddb_zone

_check_d = dict(peer_property=False,
                zone_mismatch=False,
                wwn_alias_zone=False,
                wwn_in_zone=False,
                zone_alias_use=False,
                multi_initiator=False,
                max_zone_participation=10000)  # Effectively no max zone participation by default

# _speed_to_gen converts the brocade-name-server/link-speed to a fibre channel generation.
_speed_to_gen = {'1G': 0, '2G': 2, '4G': 3, '8G': 4, '16G': 5, '32G': 6, '64G': 7, '128G': 8}
special_login = {
    'SIM Port': al.ALERT_NUM.LOGIN_SIM,
    # Should never get 'I/O Analytics Port' because I check for AE-Port but rather than overthink it...
    'I/O Analytics Port': al.ALERT_NUM.LOGIN_AMP,
}


class Found(Exception):
    pass


def set_bp_check(key, val):
    """Set the zone checks in _check_d

    :param key: Key in _check_d to be set
    :type key: str
    :param val: State: True or False, or an integer for zone checks
    :type val: bool, int
    """
    global _check_d

    try:
        _check_d[key] = val
    except KeyError:
        brcdapi_log.exception('ERROR: Invalid key: ' + str(val))


def best_fab_name(class_obj, wwn=False, fid=False):
    """Returns the user-friendly fabric name, optionally with the WWN of just the WWN if a user-friendly name wasn't
    defined.

    :param class_obj: Fabric, switch, port, or login object
    :type class_obj: brcddb.classes.fabric.FabricObj, brcddb.classes.switch.SwitchObj, brcddb.classes.port.PortObj,
                     brcddb.classes.login.LoginObj
    :param wwn: If True, append (wwn) to the fabric name
    :type wwn: bool
    :param fid: If True, append (fid) to the fabric name
    :type fid: bool
    :return: Fabric name
    :rtype: str, None
    """
    if class_obj is None:
        return 'Unknown'
    fab_obj = class_obj.r_fabric_obj()
    rbuf = fab_obj.r_obj_key()
    for switch_obj in fab_obj.r_switch_objects():  # The fabric information is stored with the switch
        buf = switch_obj.r_get(brcdapi_util.bfs_fab_user_name)
        if buf is not None and len(buf) > 0:
            rbuf = buf + ' (' + rbuf + ')' if wwn else buf
            break
    rbuf += ' (' + ', '.join([str(i) for i in fab_fids(fab_obj)]) + ')' if fid else ''

    return rbuf


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
        switch_did = switch_obj.r_get(brcdapi_util.bfs_did)
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
                a_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NULL_ALIAS_USED, None,
                                  ', '.join([zone_obj.r_obj_key() for zone_obj in zone_list]), None)
        elif len(alias_members) == 1:  # Duplicate alias? Keeping it simple by only checking 1 member per alias
            alias_name = a_obj.r_obj_key()
            bl = list()
            for c_obj in alias_list:
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
        cec_sn = iocp_obj.r_obj_key()  # The SN is always the same for each IOCP
        for chpid_obj in iocp_obj.r_path_objects():  # For every defined path
            tag = chpid_obj.r_obj_key()

            # Find the port objects for the CHPID and get a list of zones the CHPID is in
            chpid_port_obj = brcddb_port.port_obj_for_chpid(fabric_obj, cec_sn, tag)
            if chpid_port_obj is None:
                continue
            chpid_zone_l = fabric_obj.r_zones_for_di(chpid_port_obj.r_switch_obj().r_did(), chpid_port_obj.r_index())

            # For each link address, get the corresponding port object and check for at least one common zone
            for link_addr in chpid_obj.r_link_addresses():
                if link_addr[2:] == 'FE':
                    link_d = chpid_obj.r_link_addr(link_addr)
                    if link_d is not None:
                        if '2032' in link_d.values():
                            continue  # It's CUP which is a virtual port so skip it.

                # Get the FC address
                did = fabric_obj.r_switch_objects()[0].r_did() if len(fabric_obj.r_switch_keys()) == 1 else None
                switch_id = chpid_obj.r_switch_id() if did is None else None
                fc_addr = brcddb_iocp.link_addr_to_fc_addr(link_addr, switch_id=switch_id, did=did, leading_0x=True)

                # Get the port object for the port corresponding to the link address
                port_obj = brcddb_port.port_obj_for_addr(fabric_obj, fc_addr)
                if port_obj is None:
                    buf = iocp_obj.r_obj_key() + ' CHPID ' + brcddb_iocp.tag_to_text(tag) + ' (' + tag + ')'
                    chpid_port_obj.s_add_alert(al.AlertTable.alertTbl,
                                               al.ALERT_NUM.ZONE_LINK_NO_ADDR,
                                               p0=link_addr,
                                               p1=buf)
                    continue

                # See if the port for the link address and port for the CHPID share a zone
                not_found = True
                for zone in fabric_obj.r_zones_for_di(port_obj.r_switch_obj().r_did(), port_obj.r_index()):
                    if zone in chpid_zone_l:
                        not_found = False
                        break

                if not_found:
                    all_access = fabric_obj.r_get(brcdapi_util.bz_eff_default_zone)
                    if all_access is None or all_access == brcddb_common.DEF_ZONE_NOACCESS:
                        port_obj.s_add_alert(al.AlertTable.alertTbl,
                                             al.ALERT_NUM.ZONE_LINK_ADDR,
                                             None,
                                             iocp_obj.r_obj_key(),
                                             brcddb_iocp.tag_to_text(tag) + ' (' + tag + ')')

    return


def zone_by_target(fab_obj):
    """Finds all servers in the effective zone that are zoned to each target, does a speed check, and adds
    _zoned_servers to each target login object. _zoned_servers is a dictionary. Key = server WWN, value = list of zones
    that server and target are in.

    :param fab_obj: brcddb fabric object
    :type fab_obj: FabricObj class
    """
    global _speed_to_gen, _check_d

    # Get a list of all the target (storage) logins
    t_obj_l = brcddb_search.match(fab_obj.r_login_objects(), brcdapi_util.bns_fc4_features, 'Target',
                                  ignore_case=True, stype='regex-s')  # List of target objects in the fabric

    for t_login_obj in t_obj_l:

        # Get the target port object and speed
        t_wwn = t_login_obj.r_obj_key()
        t_port_obj = t_login_obj.r_port_obj()
        x = None if t_port_obj is None else t_port_obj.r_get('cs_search/speed')
        t_speed = x if isinstance(x, (int, float)) else 0

        # Get a list of all the server login objects zoned to this target
        s_wwn_d = brcddb_zone.eff_zoned_to_wwn(fab_obj, t_wwn, target=False, initiator=True)
        if len(s_wwn_d) > _check_d['max_zone_participation']:
            t_login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MAX_PARTICIPATION)

        # Figure out what all the login speeds of the target and servers zoned to this target
        s_speed_l = list()
        for s_login_obj in gen_util.remove_none([fab_obj.r_login_obj(wwn) for wwn in s_wwn_d]):
            s_port_obj = s_login_obj.r_port_obj()
            x = None if s_port_obj is None else s_port_obj.r_get('cs_search/speed')
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
    * Zone member found in another fabric
    * Zone is not used in any zone configuration
    * Effective zone doesn't match defined zone
    * Zone member not found
    * Base port (HBA) of NPIV logins is in a zone
    * Maximum number of devices zoned to a device. See _check_d['max_zone_participation']
    * Mix of WWN and alias in the same zone
    * Peer zone property member in zone
    * Duplicate aliases
    * WWN instead of an alias used in zone definition when an alias for the WWN exists
    * Calls check_ficon_zoning() - Ensures all CHPID paths are in the same zone as the CHPID

    :param fab_obj: brcddb fabric object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    """
    global _check_d

    # $ToDo - Break this up into multiple methods or review to shorten. This is way too long
    _WWN_MEM = 0b1  # The member was entered as a WWN or d,i, not an alias
    _WWN_IN_ZONE = _WWN_MEM << 1  # A zone contains a WWN member
    _ALIAS_IN_ZONE = _WWN_IN_ZONE << 1  # A zone contains an alias member
    _DI_IN_ZONE = _ALIAS_IN_ZONE << 1  # The zone contains a d,i member
    _IN_DEFINED_ZONECFG = _DI_IN_ZONE << 1  # Zone found in defined zone
    _ZONE_MISMATCH = _IN_DEFINED_ZONECFG << 1  # The effective zone does not match the defined zone
    flag = 0b0  # Bit flags. See _WWN_MEM, etc, above for specific bit definitions.

    # We'll need to figure out where all the logins are so build a table to cross-reference all the neighbor WWNs
    brcddb_util.build_login_port_map(fab_obj.r_project_obj())
    other_fabrics = fab_obj.r_project_obj().r_fabric_objects()
    other_fabrics.remove(fab_obj)

    # Zone analysis
    for zone_obj in fab_obj.r_zone_objects():
        pmem_list = list()  # pmem_list and nmem_list was an after thought to save time resolving them again in the
        nmem_list = list()  # effective zone to defined zone comparison. These are the aliases converted to WWN
        flag &= ~(_IN_DEFINED_ZONECFG | _WWN_IN_ZONE | _ALIAS_IN_ZONE | _DI_IN_ZONE | _WWN_MEM)

        # Is the zone used in any configuration?
        if len(zone_obj.r_zone_configurations()) == 0:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_USED, None, None, None)

        # Check for mixed d,i & WWN zones and make sure the member is in the fabric
        for i in range(0, 2):   # 0 - Get the members, 1 - get the principal members
            mem_list = list()  # Alias members converted to WWNs or d,i
            zmem_list = zone_obj.r_members() if i == 0 else zone_obj.r_pmembers()  # Defined zone members

            for zmem in zmem_list:
                if gen_util.is_wwn(zmem, full_check=False):
                    flag |= _WWN_MEM | _WWN_IN_ZONE
                    mem_list.append(zmem)
                    if _check_d['zone_alias_use'] and len(fab_obj.r_alias_for_wwn(zmem)) > 0:
                        # An alias was defined for this WWN, but the WWN was used to define the zone
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ALIAS_USE, None, zmem,
                                             ', '.join(fab_obj.r_alias_for_wwn(zmem)))
                elif gen_util.is_di(zmem):
                    mem_list.append(zmem)
                else:  # It must be an alias
                    flag |= _ALIAS_IN_ZONE
                    a_obj = fab_obj.r_alias_obj(zmem)
                    if a_obj is None:
                        zone_obj.s_add_alert(
                            al.AlertTable.alertTbl,
                            al.ALERT_NUM.ZONE_UNDEFINED_ALIAS,
                            None,
                            zmem,
                            zone_obj.r_obj_key()
                        )
                    else:
                        mem_list.extend(a_obj.r_members())

            for mem in mem_list:
                if i == 0:
                    nmem_list.append(mem)
                else:
                    pmem_list.append(mem)

                if gen_util.is_di(mem):
                    flag |= _DI_IN_ZONE  # It's a d,i member - typically FICON
                    temp_l = [int(i) for i in mem.split(',') if i.isnumeric()]
                    if len(temp_l) == 2:
                        # Is it in the fabric?
                        try:
                            switch_obj = switch_for_did(fab_obj, temp_l[0])
                            if switch_obj is not None:
                                if brcddb_switch.port_obj_for_index(switch_obj, temp_l[1]) is not None:
                                    raise Found
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)
                        except Found:
                            pass

                elif gen_util.is_wwn(mem, full_check=False):
                    if _check_d['peer_property'] and not gen_util.is_wwn(mem, full_check=True):
                        zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_PROPERTY, None, zmem, None)
                    # Is the member in this fabric?
                    if fab_obj.r_port_obj(mem) is None:
                        # Is it in a different fabric?
                        port_list = brcddb_util.global_port_list(other_fabrics, mem)
                        for port_obj in port_list:
                            buf = 'fabric ' + best_fab_name(port_obj) + ', switch ' +\
                                  brcddb_switch.best_switch_name(port_obj) + ', port ' +\
                                  port_obj.r_obj_key()
                            zone_obj.s_add_alert(al.AlertTable.alertTbl,
                                                 al.ALERT_NUM.ZONE_DIFF_FABRIC,
                                                 key=None,
                                                 p0=mem,
                                                 p1=buf)
                        if len(port_list) == 0:
                            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NOT_FOUND, None, mem)
                else:
                    buf = best_fab_name(fab_obj, wwn=True) + ': ' + 'Standard' if i == 0 else 'Principal'
                    buf += ' member, ' + str(mem) + ', is not valid in zone ' + zone_obj.r_obj_key()
                    if a_obj is not None:
                        buf += '. Last working alias: ' + str(a_obj.r_obj_key())
                    brcdapi_log.exception('ERROR: ' + buf, echo=True)

        # Do all the zone membership count checks
        if zone_obj.r_is_peer():  # It's a peer zone
            # Make sure there is at least one member and one principal member
            if len(pmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_PMEM)
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_PEER_NO_NMEM)
        else:  # It's a standard zone (not a peer zone)
            # Make sure there are at least 2 members
            if len(nmem_list) == 0:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_NO_MEMBERS)
            elif len(nmem_list) == 1:
                zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_ONE_MEMBER)

        # Check for single initiator zoning.
        # elist = brcddb_zone.zoned_initiators(zone_obj)
        elist = list()
        if zone_obj.r_is_peer():
            for mem_l in (pmem_list, nmem_list):
                for wwn in mem_l:
                    login_obj = fab_obj.r_login_obj(wwn)
                    if login_obj is not None:
                        fc4_features = str(login_obj.r_get(brcdapi_util.bns_fc4_features)).lower()
                        if 'target' not in fc4_features and 'initiator' in fc4_features:
                            elist.append(wwn)
                            break
        else:
            for wwn in nmem_list:
                login_obj = fab_obj.r_login_obj(wwn)
                if login_obj is not None:
                    fc4_features = str(login_obj.r_get(brcdapi_util.bns_fc4_features)).lower()
                    if 'target' not in fc4_features and 'initiator' in fc4_features:
                        elist.append(wwn)
        if len(elist) > 1 and _check_d['multi_initiator']:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MULTI_INITIATOR, None, ', '.join(elist))

        # Check for mixed zone members
        if flag & _DI_IN_ZONE and flag & _WWN_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MIXED)
        if _check_d['wwn_alias_zone'] and flag & _WWN_MEM and flag & _ALIAS_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_WWN_ALIAS)

        # Check for zones with WWN members
        if _check_d['wwn_in_zone'] and flag & _WWN_IN_ZONE:
            zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_WWN_IN_ZONE)

        # Make sure the defined zone matches the effective zone
        if _check_d['zone_mismatch']:
            eff_zone_obj = fab_obj.r_eff_zone_obj(zone_obj.r_obj_key())
            if eff_zone_obj is not None:
                zone_obj.s_or_flags(brcddb_common.zone_flag_effective)
                if set(eff_zone_obj.r_pmembers()) != set(pmem_list):
                    zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                    flag |= _ZONE_MISMATCH
                if set(eff_zone_obj.r_members()) != set(nmem_list):
                    zone_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
                    flag |= _ZONE_MISMATCH

    if flag & _ZONE_MISMATCH and _check_d['zone_mismatch']:
        try:
            fab_obj.r_defined_eff_zonecfg_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.ZONE_MISMATCH)
        except AttributeError:
            pass  # Defined configuration was deleted

    for login_obj in fab_obj.r_login_objects():
        wwn = login_obj.r_obj_key()
        port_obj = login_obj.r_port_obj()
        if port_obj is None:
            continue  # This happens when a login is found but data for the switch associated with it wasn't captured

        # Make sure that all logins are zoned.
        if len(fab_obj.r_zones_for_wwn(wwn)) + \
                len(fab_obj.r_zones_for_di(port_obj.r_switch_obj().r_did(), port_obj.r_index())) > 0:
            if wwn in fab_obj.r_base_logins():
                login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_BASE_ZONED)
        elif wwn not in fab_obj.r_base_logins():
            login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_NOT_ZONED)

        # Check zone participation
        buf = login_obj.r_get('port-properties')
        if buf is not None and buf in special_login:
            login_obj.s_add_alert(al.AlertTable.alertTbl, special_login[buf])
            continue

    # Alias analysis, zone speed analysis, and FICON analysis
    alias_analysis(fab_obj)
    zone_by_target(fab_obj)
    check_ficon_zoning(fab_obj)


def fab_obj_for_name(proj_obj, fab_name):
    """Finds the first fabric matching the user-friendly fabric name

    :param proj_obj: brcddb project object
    :type proj_obj: brcddb.classes.project.ProjObj
    :param fab_name: Fabric user-friendly name
    :type fab_name: str
    :return: brcddb fabric object. None if not found
    :rtype: brcddb.classes.fabric.FabricObj, None
    """
    for fab_obj in proj_obj.r_fabric_objects():
        for switch_obj in fab_obj.r_switch_objects():  # The fabric name is returned with
            buf = switch_obj.r_get(brcdapi_util.bfs_fab_user_name)
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
    return gen_util.remove_duplicates(
        gen_util.remove_none([switch_obj.r_fid() for switch_obj in fab_obj.r_switch_objects()])
    )


def copy_fab_obj(fab_obj, fab_key=None, full_copy=False, skip_alias=False, skip_zone=False, skip_zonecfg=False):
    """Makes a copy of a fabric object

    :param fab_obj: The fabric object to be copied
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param fab_key: Name for the copied fabric. If None, the key is the same as for fab_obj with "_copy" appended
    :type fab_key: str, None
    :param full_copy: If True, copies all data added with s_new_key(). Otherwise, just the private members are copied
    :type full_copy: bool
    :param skip_alias: If True, copying of aliases is skipped.
    :type skip_alias: bool
    :param skip_zone: If True, copying of zones is skipped.
    :type skip_zone: bool
    :param skip_zonecfg: If True, copying of zone configurations is skipped.
    :type skip_zonecfg: bool
    :return: Copy of fabric object
    :rtype: brcddb.classes.fabric.FabricObj
    """
    # ToDo - Add ability to copy the switch objects
    proj_obj = fab_obj.r_project_obj()
    new_key = fab_obj.r_obj_key() + '_copy' if fab_key is None else fab_key
    fab_obj_copy = proj_obj.s_add_fabric(new_key, add_switch=False)
    fab_obj_copy.s_or_flags(fab_obj.r_flags())
    for key in fab_obj.r_switch_keys():
        fab_obj_copy.s_add_switch(key, add_fab_key=False)
    for obj in fab_obj.r_login_objects():
        login_obj_copy = fab_obj_copy.s_add_login(obj.r_obj_key())
        if full_copy:
            for key in login_obj_copy.r_keys():
                login_obj_copy.s_new_key(key, obj.r_get(key))
    if not skip_alias:
        for obj in fab_obj.r_alias_objects():
            fab_obj_copy.s_add_alias(obj.r_obj_key(), obj.r_members())
    if not skip_zone:
        for obj in fab_obj.r_zone_objects():
            fab_obj_copy.s_add_zone(obj.r_obj_key(), obj.r_type(), obj.r_members(), obj.r_pmembers())
    if not skip_zonecfg:
        for obj in fab_obj.r_zonecfg_objects():
            if obj.r_obj_key() == '_effective_zone_cfg':
                fab_obj_copy.s_add_eff_zonecfg(obj.r_members())
            else:
                fab_obj_copy.s_add_zonecfg(obj.r_obj_key(), obj.r_members())
    for obj in fab_obj.r_fdmi_node_keys():
        fab_obj_copy.s_add_fdmi_node(obj)
    for obj in fab_obj.r_fdmi_port_keys():
        fab_obj_copy.s_add_fdmi_port(obj)
    if full_copy:
        for key in fab_obj.r_keys():
            fab_obj_copy.s_new_key(key, fab_obj.r_get(key))

    return fab_obj_copy


def _zone_merge_group(wwn_d, missing_l, fab_obj, in_wwn):
    """Internal for zone_merge_group()

    This method was written to support scripts that determine zone migration groups. Keep in mind that it has to be
    iterative because everything associated with every login has to move.

    :param wwn_d: Used to track WWNs already taken into account
    :type wwn_d: dict
    :param missing_l: Running list of WWNs not found
    :type missing_l: list
    :param fab_obj: The fabric object to be copied
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param in_wwn: WWN of the device you want to move
    :type in_wwn: str, None
    :return: List of WWNs need to be grouped together
    :type: list
    """
    rl = list()  # List of WWNs in the zone merge group

    # The user is moving the device off the port so all logins on the port must be considered
    port_obj = fab_obj.r_login_obj(in_wwn).r_port_obj()
    # The WWN may be zoned by not logged into the fabric in which case, it won't be associated with a port
    if port_obj is None:
        missing_l.append(in_wwn)
        wwn_l = [in_wwn]  # We still need to process it because there may be other dependencies
    else:
        wwn_l = port_obj.r_login_keys()

    # Figure out all the zone dependencies for each WWN
    for wwn in wwn_l:
        rl.append(wwn)
        wwn_d.update({wwn: True})
        for d_wwn, zone_l in brcddb_zone.eff_zoned_to_wwn(fab_obj, wwn, target=True, initiator=True).items():
            for zone in zone_l:  # I don't think this loop does anything, but I'm not fixing working code.
                for next_wwn in brcddb_zone.eff_zoned_to_wwn(fab_obj, d_wwn, target=True, initiator=True).keys():
                    if next_wwn not in wwn_d:
                        rl.extend(_zone_merge_group(wwn_d, missing_l, fab_obj, next_wwn))

    return rl


def zone_merge_group(wwn_d, fab_obj, wwn):
    """Determines all logins that would be effected a result of removing a WWN from a fabric.

    This method was written to support scripts that determine zone migration groups. Keep in mind that has to be
    iterative because everything associated with every login has to move.

    :param wwn_d: Used to track WWNs already taken into account
    :type wwn_d: dict
    :param fab_obj: The fabric object to be copied
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param wwn: WWN of the device you want to move
    :type wwn: str, None
    :return wwn_l: WWNs need to be grouped together
    :rtype wwn_l: list
    :return missing_l: WWNs not found
    :rtype missing_l: list
    """
    missing_l = list()
    wwn_l = gen_util.remove_duplicates(_zone_merge_group(wwn_d, missing_l, fab_obj, wwn))
    return wwn_l, gen_util.remove_duplicates(missing_l)


def fab_match(fab_obj, search_term_l_in, s_type='exact'):
    """Returns a list of WWNs logged into the fabric matching the search criteria

    :param fab_obj: The fabric object to be copied.
    :type fab_obj: brcddb.classes.fabric.FabricObj, None
    :param search_term_l_in: List of search terms either by WWN or alias
    :type search_term_l_in: list, None
    :param s_type: Search type: None, 'exact', 'wild', 'regex-m', or 'regex-s'. Applied to search_l. None defaults \
        to 'exact'
    :type s_type: str
    :return: List of matching WWNs
    :rtype: list()
    """
    # Condition the input
    search_term_l = gen_util.convert_to_list(search_term_l_in)
    if len(search_term_l) == 0 or fab_obj is None:
        return list()

    # Perform the search - Get a list of all the matching WWNs
    search_l = [dict(w=wwn, a=fab_obj.r_alias_for_wwn(wwn)) for wwn in fab_obj.r_login_keys()]
    rl = list()
    for search_term in search_term_l:
        rl.extend(brcddb_search.match(search_l, 'w', search_term, ignore_case=False, stype=s_type))  # Matching WWNs
        rl.extend(brcddb_search.match(search_l, 'a', search_term, ignore_case=False, stype=s_type))  # Matching aliases

    return gen_util.remove_duplicates([d['w'] for d in rl])


def aliases_by_name(fab_obj, search_term_l_in, s_type='exact'):
    """Returns a list of aliases defined in the fabric matching the search criteria

    :param fab_obj: The fabric object to be copied. If None, an empty list is returned.
    :type fab_obj: brcddb.classes.fabric.FabricObj, None
    :param search_term_l_in: Search term or list of search terms either by WWN or alias. None returns an empty list.
    :type search_term_l_in: str, list, None
    :param s_type: Search type: None, 'exact', 'wild', 'regex-m', or 'regex-s'. Applied to search_l. None defaults \
        to 'exact'
    :type s_type: str
    :return: List of matching WWNs
    :rtype: list()
    """
    # Condition the input
    search_term_l = gen_util.convert_to_list(search_term_l_in)
    if len(search_term_l) == 0 or fab_obj is None:
        return list()

    # Perform the search - Get a list of all the matching WWNs
    search_l = [dict(a=str(key)) for key in fab_obj.r_alias_keys()]
    rl = list()
    for search_term in search_term_l:
        rl.extend(brcddb_search.match(search_l, 'a', search_term, ignore_case=False, stype=s_type))

    return gen_util.remove_duplicates([d['a'] for d in rl])


def zone_by_name(fab_obj, search_term_l_in, s_type='exact'):
    """Returns a list of zones defined in the fabric matching the search criteria

    :param fab_obj: The fabric object to be copied. If None, an empty list is returned.
    :type fab_obj: brcddb.classes.fabric.FabricObj, None
    :param search_term_l_in: Search term or list of search terms either by WWN or alias. None returns an empty list.
    :type search_term_l_in: str, list, None
    :param s_type: Search type: None, 'exact', 'wild', 'regex-m', or 'regex-s'. Applied to search_l. None defaults \
        to 'exact'
    :type s_type: str
    :return: List of matching WWNs
    :rtype: list()
    """
    # Condition the input
    search_term_l = gen_util.convert_to_list(search_term_l_in)
    if len(search_term_l) == 0 or fab_obj is None:
        return list()

    # Perform the search - Get a list of all the matching WWNs
    search_l = [dict(z=str(key)) for key in fab_obj.r_zone_keys()]
    rl = list()
    for search_term in search_term_l:
        rl.extend(brcddb_search.match(search_l, 'z', search_term, ignore_case=False, stype=s_type))

    return gen_util.remove_duplicates([d['z'] for d in rl])


#####################################################################################
#                                                                                   #
# Creat unique alias, zone, and zonecfg names. Currently only used for FICON.       #
#                                                                                   #
#####################################################################################

def unique_alias_name(fabric_obj, alias_name):
    """Ensure that an alias name is unique by appending a number if a alias name is already used

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param alias_name: Alias name
    :type alias_name: str
    :return: Alias name
    :rtype: str
    """
    i, r_alias_name = 0, alias_name
    while fabric_obj.r_alias_obj(r_alias_name) is not None:
        i += 1
        r_alias_name = alias_name + '_' + str(i)

    return r_alias_name


def unique_zone_name(fabric_obj, zone_name):
    """Ensure that a zone name is unique by appending a number if a zone name is already used

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zone_name: Zone name
    :type zone_name: str
    :return: Zone name
    :rtype: str
    """
    i, r_zone_name = 0, zone_name
    while fabric_obj.r_zone_obj(r_zone_name) is not None:
        i += 1
        r_zone_name = zone_name + '_' + str(i)

    return r_zone_name


def unique_zonecfg_name(fabric_obj, zonecfg_name):
    """Ensure that a zone configuration name is unique by appending a number if a zonecfg name is already used

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zonecfg_name: Zone configuration name
    :type zonecfg_name: str
    :return: Zone name
    :rtype: str
    """
    i, r_zonecfg_name = 0, zonecfg_name
    while fabric_obj.r_zonecfg_obj(r_zonecfg_name) is not None:
        i += 1
        r_zonecfg_name = zonecfg_name + '_' + str(i)

    return r_zonecfg_name


#####################################################################################
#                                                                                   #
# FICON Zoning Functions - See "Important note about FICON zones" in module header. #
#                                                                                   #
#####################################################################################

def rnid_groups(fabric_obj):
    """Sorts out the mainframe attachments by control unit and channel

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :return: Dictionary: key - generic device type. Value - dictionary, key - S/N, value - list of port objects
    :rtype: dict
    """
    # Sort out the ports by sequence number (S/N) and generic type.
    rnid_d = dict()

    for port_obj in [obj for obj in fabric_obj.r_port_objects() if obj.r_is_online()]:
        port_rnid_d = port_obj.r_get('rnid')
        if isinstance(port_rnid_d, dict):
            generic_type = brcddb_iocp.generic_device_type(port_rnid_d.get('type-number'))
            port_rnid_seq = gen_util.remove_leading_char(port_rnid_d.get('sequence-number', 'FFFFFFFFFFFF'), '0')

            # Get the generic device type dictionary from rnid_d. If it hasn't been added yet, add it.
            generic_type_d = rnid_d.get(generic_type)
            if not isinstance(generic_type_d, dict):
                generic_type_d = dict()
                rnid_d.update({generic_type: generic_type_d})

            # Get the port object list for this sequence number
            port_obj_l = generic_type_d.get(port_rnid_seq)
            if not isinstance(port_obj_l, list):
                port_obj_l = list()
                generic_type_d.update({port_rnid_seq: port_obj_l})

            # Add the port object
            port_obj_l.append(port_obj)

    return rnid_d


def ficon_zone_all(fabric_obj, zonecfg, in_notes_l=None):
    """FICON. Returns a list with a single zone dictionary that includes all ports except ICL ports

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zonecfg: Zone configuration name
    :type zonecfg: str
    :param in_notes_l: Error and warning messages. Useful for applications with user feedback.
    :type in_notes_l: None, list
    :return: Lists of dictionaries as described in "Important note about FICON zones" in the module header.
             for use with brcddb.brcddb_zone.add_zone_worksheet()
    :rtype: list
    """
    notes_l = in_notes_l if isinstance(in_notes_l, list) else list()
    buf = best_fab_name(fabric_obj, fid=True)
    zdb_l = [dict(Zone_Object='comment', Comments='All ports except ICL ports. Fabric: ' + buf)]
    member_l, comment_l = list(), list()
    zone_name = unique_zone_name(fabric_obj, 'FICON_zone')

    # Sorting was done for humans reviewing the zoning. It's not necessary for technical reasons.
    for port_obj in [obj for obj in brcddb_util.sort_ports(fabric_obj.r_all_port_objects()) if not obj.r_is_icl()]:
        member_l.append(str(port_obj.r_did()) + ',' + str(port_obj.r_index()))
        comment_l.append(brcddb_port.port_best_desc(port_obj, switch_name=True, did_hex=True, port_num=True))
    if len(member_l) > 1:
        zdb_l.append(dict(Zone_Object='zone', Action='create', Name=zone_name, Member=member_l, Comments=comment_l))
        zdb_l.append(dict(Zone_Object='zone_cfg', Action='create', Name=zonecfg, Member=[zone_name]))
    else:
        notes_l.append('Fabric ' + best_fab_name(fabric_obj, fid=True) + ' contains fewer than 2 ports.')

    return zdb_l


def ficon_zone_all_f(fabric_obj, zonecfg, in_notes_l=None):
    """FICON. Returns a zone dictionary with a single zone that includes all F ports.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zonecfg: Zone configuration name
    :type zonecfg: str
    :param in_notes_l: Error and warning messages. Useful for applications with user feedback.
    :type in_notes_l: None, list
    :return: Dictionaries with zone DB definitions for use with brcddb.brcddb_zone.add_zone_worksheet()
    :rtype: list
    """
    notes_l = in_notes_l if isinstance(in_notes_l, list) else list()
    buf = best_fab_name(fabric_obj, fid=True)
    zdb_l = [dict(Zone_Object='comment', Comments='All F-Ports. Fabric: ' + buf)]
    member_l, comment_l = list(), list()
    zone_name = unique_zone_name(fabric_obj, 'FICON_zone')

    # Sorting was done for humans reviewing the zoning. It's not necessary for technical reasons.
    port_obj_l =\
        [o for o in brcddb_util.sort_ports(fabric_obj.r_all_port_objects()) if o.c_login_type().lower() == 'f-port']
    for port_obj in port_obj_l:
        member_l.append(str(port_obj.r_did()) + ',' + str(port_obj.r_index()))
        comment_l.append(brcddb_port.port_best_desc(port_obj, switch_name=True, did_hex=True, port_num=True))
    if len(member_l) > 1:
        zdb_l.append(dict(Zone_Object='zone', Action='create', Name=zone_name, Member=member_l, Comments=comment_l))
        zdb_l.append(dict(Zone_Object='zone_cfg', Action='create', Name=zonecfg, Member=[zone_name]))
    else:
        notes_l.append('No RNID data found attached to fabric ' + best_fab_name(fabric_obj, fid=True))

    return zdb_l


def ficon_zone_by_device(fabric_obj, zonecfg, rnid_d, in_notes_l=None):
    """FICON. Returns a list of zones for each CHPID with access to all control units.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zonecfg: Zone configuration name
    :type zonecfg: str
    :param in_notes_l: Error and warning messages. Useful for applications with user feedback.
    :type in_notes_l: None, list
    :param rnid_d: RNID dictionary. Output of brcddb_fabric.rnid_groups()
    :type rnid_d: dict
    :return: Dictionaries with zone DB definitions for use with brcddb.brcddb_zone.add_zone_worksheet()
    :rtype: list
    """
    notes_l = in_notes_l if isinstance(in_notes_l, list) else list()
    buf = best_fab_name(fabric_obj, fid=True)
    zdb_l = [dict(Zone_Object='comment', Comments='Single zone for each CHPID for every control unit. Fabric: ' + buf)]
    temp_notes_l, zone_l = list(), list()

    # Create an alias for each control unit
    cu_alias_l = list()
    for key in ('DASD', 'Tape', 'CUP', 'CTC', 'Switch', 'IDG', 'Test', 'UNKN'):
        for sub_key, port_obj_l in rnid_d.get(key, dict()).items():
            member_l, comment_l = list(), list()
            alias = unique_alias_name(fabric_obj, key + '_' + sub_key + '_alias')
            cu_alias_l.append(alias)
            for port_obj in port_obj_l:
                member_l.append(str(port_obj.r_did()) + ',' + str(port_obj.r_index()))
                comment_l.append(brcddb_port.port_best_desc(port_obj, switch_name=True, did_hex=True, port_num=True))
            zdb_l.append(dict(Zone_Object='alias', Action='create', Name=alias, Member=member_l, Comments=comment_l))

    # Create a zone for each CHPID
    for sub_key, port_obj_l in rnid_d.get('CPU', dict()).items():
        for port_obj in port_obj_l:
            tag = port_obj.r_get('rnid/tag')
            if tag is None:
                buf = 'Missing tag for switch ' + brcddb_switch.best_switch_name(port_obj) + ', port '
                buf += port_obj.r_obj_key()
                temp_notes_l.append(buf)
            else:
                for alias in cu_alias_l:
                    zone_name = 'CHPID_' + sub_key + '_' + tag.replace('0x', '') + '_' + alias.split('_')[1]
                    zone_name = unique_zone_name(fabric_obj, zone_name)
                    zone_l.append(zone_name)
                    zdb_l.append({
                        'Zone_Object': 'peer_zone',
                        'Action': 'create',
                        'Name': zone_name,
                        'Member': [str(port_obj.r_did()) + ',' + str(port_obj.r_index())],
                        'Principal Member': [alias]
                    })

    # Create the zone configuration
    if len(zone_l) == 0:
        temp_notes_l.append('Nothing to zone for "By_Device"')
    else:
        if len(temp_notes_l) > 0:
            zdb_l.insert(1, dict(Zone_Object='comment', Comments=temp_notes_l))
        zdb_l.append(dict(Zone_Object='zone_cfg', Action='create', Name=zonecfg, Member=zone_l))
    notes_l.extend(temp_notes_l)

    return zdb_l


def ficon_zone_by_channel(fabric_obj, zonecfg, in_notes_l=None):
    """FICON. Returns a list of zones for each CHPID with access to only to the link addresses, LINK=.

    WARNING: This requires the IOCPs, -iocp option in mf_zone.py, to be processed and present in the project object.

    :param fabric_obj: Fabric object
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zonecfg: Zone configuration name
    :type zonecfg: str
    :param in_notes_l: Error and warning messages. Useful for applications with user feedback.
    :type in_notes_l: None, list
    :return: Dictionaries with zone DB definitions for use with brcddb.brcddb_zone.add_zone_worksheet()
    :rtype: list
    """
    notes_l = in_notes_l if isinstance(in_notes_l, list) else list()
    buf = 'Zone by CHPID with access to defined link addresses only. Fabric: ' + \
          best_fab_name(fabric_obj, fid=True)
    zdb_l = [dict(Zone_Object='comment', Comments=buf)]
    temp_notes_l, zone_l = list(), list()

    # Find all the CHPIDs in this fabric and create a CHPID zone that includes the link addresses
    for iocp_obj in fabric_obj.r_project_obj().r_iocp_objects():
        for chpid_obj in iocp_obj.r_path_objects():
            chpid_port_obj = brcddb_iocp.find_chpid(fabric_obj, iocp_obj.r_obj_key(), chpid_obj.r_obj_key())
            if chpid_port_obj is not None:
                comment_l, cu_di_l = list(), list()
                for addr in [
                    gen_util.pad_string(brcddb_iocp.link_addr_to_fc_addr(a, did=chpid_port_obj.r_did()), 6, '0')
                    for a in chpid_obj.r_link_addresses()
                ]:
                    cu_port_obj = fabric_obj.r_port_obj_for_pid(addr)
                    if cu_port_obj is None:
                        buf = 'Could not find address ' + addr.upper() + ' in fabric '
                        buf += best_fab_name(fabric_obj, fid=True)
                        temp_notes_l.append(buf)
                    else:
                        cu_di_l.append(str(cu_port_obj.r_did()) + ',' + str(cu_port_obj.r_index()))
                        comment_l.append(
                            brcddb_port.port_best_desc(port_obj, switch_name=True, did_hex=True, port_num=True)
                        )
                zone_name = unique_zone_name(fabric_obj, 'CHPID_' + iocp_obj.r_obj_key() + '_' + chpid_obj.r_obj_key())
                zone_l.append(zone_name)
                zdb_l.append({
                        'Zone_Object': 'peer_zone',
                        'Action': 'create',
                        'Name': zone_name,
                        'Member': [str(chpid_port_obj.r_did()) + ',' + str(chpid_port_obj.r_index())],
                        'Principal Member': cu_di_l,
                        'Comments': comment_l,
                    })

    # Create the zone configuration
    if len(zone_l) == 0:
        notes_l.append('Nothing to zone for "By_Channel"')
    else:
        if len(temp_notes_l) > 0:
            zdb_l.insert(1, dict(Zone_Object='comment', Comments=notes_l))
        zdb_l.append(dict(Zone_Object='zone_cfg', Action='create', Name=zonecfg, Member=zone_l))
    notes_l.extend(temp_notes_l)

    return zdb_l


def ficon_zone_fab_obj(fabric_obj, zdb_l):
    """Adds zoning information in zdb_l to the fabric object, fabric_obj, for use with brcddb.api.zone.replace_zoning()

    :param fabric_obj: Fabric object. Typically a copy of the fabric object without any zoning. Example:
                       copy_fabric_obj(fabric_obj, skip_alias=True, skip_zone=True, skip_zonecfg=True)
    :type fabric_obj: brcddb.classes.fabric.FabricObj
    :param zdb_l: List of dictionaries as described in "Important note about FICON zones" in the module header. These
                  lists are returned from ficon_zone_all(), ficon_zone_all_f(), ficon_zone_by_device() and
                  ficon_zone_by_channel()
    :type zdb_l: list
    :return: Nothing
    :rtype: None
    """

    # I can't think of a reason why the database would care what order zoning information is added. Just in case I'm
    # over looking something, I'll do it in logical order.

    # Add the aliases
    for zone_def_d in [d for d in zdb_l if d['Zone_Object'] == 'alias' and d.get('Action', 'None') == 'create']:
        fabric_obj.s_add_alias(zone_def_d['Name'], zone_def_d['Member'])

    # Add the standard zones
    for zone_def_d in [d for d in zdb_l if d['Zone_Object'] == 'zone' and d.get('Action', 'None') == 'create']:
        fabric_obj.s_add_zone(
            zone_def_d['Name'],
            'zone',
            zone_def_d.get('Member'),
            zone_def_d.get('Principal Member')
        )

    # Add the peer zones
    for zone_def_d in [d for d in zdb_l if d['Zone_Object'] == 'peer_zone' and d.get('Action', 'None') == 'create']:
        fabric_obj.s_add_zone(
            zone_def_d['Name'],
            'user-created-peer-zone',
            zone_def_d['Member'],
            zone_def_d['Principal Member']
        )

    # Add the zone configurations
    for zone_def_d in [d for d in zdb_l if d['Zone_Object'] == 'zone_cfg' and d.get('Action', 'None') == 'create']:
        fabric_obj.s_add_zonecfg(zone_def_d['Name'], zone_def_d['Member'])

    return None
