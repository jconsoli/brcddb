"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Support for project level operations.

**Public Methods & Data**

+---------------------------+---------------------------------------------------------------------------------------+
| Method                    | Description                                                                           |
+===========================+=======================================================================================+
| new                       | Creates a new project object                                                          |
+---------------------------+---------------------------------------------------------------------------------------+
| dup_wwn                   | Searches all fabrics in the project for duplicate WWNs.                               |
+---------------------------+---------------------------------------------------------------------------------------+
| read_from                 | Creates a new project object from a JSON dump of a previous project object.           |
+---------------------------+---------------------------------------------------------------------------------------+
| build_xref                | Builds cross-references for brcddb objects. This is necessary because it's not        |
|                           | immediately obvious how request data is interrelated.                                 |
+---------------------------+---------------------------------------------------------------------------------------+
| add_custom_search_terms   | The search utility cannot dereference embedded lists so create custom search terms.   |
|                           | See module header for details.                                                        |
+---------------------------+---------------------------------------------------------------------------------------+
| fab_obj_for_user_name     | Returns a list of fabric objects matching a user-friendly name. It may be a regex     |
|                           | match, regex search, wild card, or exact match.                                       |
+---------------------------+---------------------------------------------------------------------------------------+
| switch_obj_for_user_name  | Returns a list of switch objects matching a user-friendly name. It may be a regex     |
|                           | match, regex search, wild card, or exact match.                                       |
+---------------------------+---------------------------------------------------------------------------------------+
| best_project_name         | Returns the project object key                                                        |
+---------------------------+---------------------------------------------------------------------------------------+
| fab_obj_for_fid           | Returns a list of fabric objects matching a FID.                                      |
+---------------------------+---------------------------------------------------------------------------------------+
| scan                      | Returns a list of text containing basic fabric information for a project.             |
+---------------------------+---------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Removed call to obsolete add_maps_groups(), added scan()                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 16 Apr 2024   | Improved report output of scan()                                                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 16 Jun 2024   | Fixed spelling mistakes in messages.                                                  |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 06 Dec 2024   | Added the FID number to the logical switch in scan()                                  |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '06 Dec 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

import brcdapi.log as brcdapi_log
import brcdapi.file as brcdapi_file
import brcdapi.gen_util as gen_util
import brcdapi.util as brcdapi_util
import brcddb.classes.project as project_class
import brcddb.util.copy as brcddb_copy
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_common as brcddb_common
import brcddb.util.search as brcddb_search
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_switch as brcddb_switch

# _STAND_ALONE: True: Executes as a standalone module taking input from the command line. False: Does not automatically
# execute. This is useful when importing this module into another module that calls psuedo_main().
_STAND_ALONE = True  # See note above

_dup_wwn_check = False


def new(name, date):
    """Creates a new project object

    :param name: User defined project date
    :type name: str
    :param date: Project date
    :type date: str
    """
    return project_class.ProjectObj(name, date)


def set_dup_wwn(state):
    """Sets _dup_wwn

    :param state: True or False
    :type state: bool
    """
    global _dup_wwn_check

    _dup_wwn_check = state


def dup_wwn(proj_obj):
    """Searches all fabrics in the project for duplicate WWNs.

    :param proj_obj: Project object
    :type proj_obj: ProjectObj
    :return: List of login objects for the duplicate WWNs. None entry separates multiple duplicates
    :rtype: list
    """
    global _dup_wwn_check

    dup_login_l = list()
    if not _dup_wwn_check:
        return dup_login_l

    for wwn in gen_util.remove_duplicates(proj_obj.r_login_keys()):
        login_l = proj_obj.r_login_obj(wwn)
        if len(login_l) > 1:
            dup_login_l.extend(login_l)
            proj_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_DUP_LOGIN, None, wwn)
            temp_l = list()
            for login_obj in login_l:
                temp_l.append('Switch: ' + brcddb_switch.best_switch_name(login_obj.r_switch_obj(), wwn=True) +
                              ' Port: ' + login_obj.r_port_obj().r_obj_key())
            for login_obj in login_l:
                login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_DUP_LOGIN, p0='; '.join(temp_l))

    return dup_login_l


def read_from(inf):
    """Creates a new project object from a JSON dump of a previous project object.

    :param inf: Input file name written with brcdapi_file.write_dump()
    :type inf: str
    :return: Project object
    :rtype: None, brcddb.classes.project.ProjectObj
    """
    obj = brcdapi_file.read_dump(inf)
    if not isinstance(obj, dict) or obj.get('_obj_key') is None or obj.get('_date') is None:
        brcdapi_log.log(inf + ' is not a valid project file.', echo=True)
        return None
    # Make sure there is a valid Excel tab name.
    proj_obj = new(obj.get('_obj_key').replace(' ', '_').replace(':', '').replace('-', '_')[:32], obj.get('_date'))
    brcddb_copy.plain_copy_to_brcddb(obj, proj_obj)
    return proj_obj


def build_xref(proj_obj):
    """Builds cross-references for brcddb objects. This is necessary because it's not immediately obvious how request
       data is interrelated.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    # We'll need to figure out where all the logins are so build a table to cross-reference all the neighbor WWNs
    brcddb_util.build_login_port_map(proj_obj)


def add_custom_search_terms(proj_obj):
    """The search utility cannot dereference embedded lists so create custom search terms. Terms added are:

    Port Objects:
    cs_search/sfp_max_speed (in Gbps)
    cs_search/sfp_min_speed (in Gbps)
    cs_search/remote_sfp_max_speed (in Gbps)
    cs_search/remote_sfp_min_speed (in Gbps)
    cs_search/max_login_speed (in Gbps. This is the maximum common to both the local and remote SFPs)
    cs_search/speed (in Gbps - This is fibrechannel/speed, which is bps, converted to Gbps. The actual login speed)

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for port_obj in proj_obj.r_port_objects():
        # Find the maximum speed & add something to the port & login objects we can search against.
        max_sfp = max_r_sfp = None
        search = port_obj.r_get('cs_search')
        if search is None:
            search = dict()
            port_obj.s_new_key('cs_search', search)

        # Get the maximum and minimum speeds supported by the switch SFP
        speed_l = port_obj.r_get(brcdapi_util.sfp_speed)
        if isinstance(speed_l, (list, tuple)):
            max_sfp = max(speed_l)
            if 'sfp_max_speed' not in search:
                search.update(sfp_max_speed=max_sfp)
            if 'sfp_min_speed' not in search:
                search.update(sfp_min_speed=min(speed_l))

        # Get the maximum and minimum speeds supported by the remote (attached device) SFP
        speed_l = port_obj.r_get(brcdapi_util.sfp_remote_speed)
        if speed_l is None:  # No speed from remote SFP so try to figure it out based on the HBA type
            for d in brcddb_common.hba_remote_speed:
                if len(brcddb_search.match_test(port_obj.r_login_objects(), d['f'])) > 0:
                    speed_l = d['s']
                    break
        if isinstance(speed_l, (list, tuple)):
            max_r_sfp = max(speed_l)
            if 'remote_sfp_max_speed' not in search:
                search.update(remote_sfp_max_speed=max_r_sfp)
            if 'remote_sfp_min_speed' not in search:
                search.update(remote_sfp_min_speed=min(speed_l))

        # Get the maximum supported speed (either the maximum local speed or the maximum attached speed)
        if isinstance(max_sfp, int) and isinstance(max_r_sfp, int):
            if 'max_login_speed' not in search:
                search.update(max_login_speed=min([max_sfp, max_r_sfp]))

        # Convert the actual login speed, which is bps, to Gbps for easier comparisons to the SFP speed capabilities
        if 'speed' not in search:
            v = gen_util.non_decimal.sub('', port_obj.c_login_speed())
            if len(v) > 0:
                search.update(speed=int(v))


def fab_obj_for_user_name(proj_obj, name, match_type='exact'):
    """Returns a list of fabric objects matching a user-friendly name.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param name: User friendly fabric name
    :type name: str
    :param match_type: Type of match to perform. Accepts 'exact', 'regex_m', 'regex_s', and 'wild'
    :type match_type: str
    :return: List of fabric objects matching name
    :rtype: list
    """
    sl = brcddb_search.match_test(
        proj_obj.r_switch_objects(),
        dict(k='brcdapi_util.bfs_fab_user_name', v=name, t=match_type, i=False)
    )
    return gen_util.remove_duplicates([switch_obj.r_fabric_obj() for switch_obj in sl])


def switch_obj_for_user_name(proj_obj, name, match_type='exact'):
    """Returns a list of switch objects matching a user-friendly name.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param name: User friendly switch name
    :type name: str
    :param match_type: Allowed types are: 'exact', 'wild', 'regex-m', 'regex-s'
    """
    return gen_util.remove_duplicates(
        brcddb_search.match_test(
            proj_obj.r_switch_objects(),
            dict(k=brcdapi_util.bfs_sw_user_name, v=name, t=match_type, i=False)
        )
    )


def best_project_name(proj_obj):
    """Returns the user-friendly project name.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :return: Project description
    :rtype: str
    """
    try:
        return proj_obj.r_obj_key()
    except AttributeError:
        pass
    return 'unknown'


def fab_obj_for_fid(proj_obj, fid):
    """Returns a list of fabric objects matching a FID.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param fid: Fabric ID
    :type fid: int
    :return: List of fabric objects matching the fid
    :rtype: list
    """
    rl = list()
    for fab_obj in proj_obj.r_fabric_objects():
        for switch_obj in fab_obj.r_switch_objects():
            local_fid = switch_obj.r_get(brcdapi_util.bfls_fid)
            if isinstance(local_fid, int) and local_fid == fid:
                rl.append(fab_obj)
                break
    return rl


def _scan_fabric(fab_obj, in_prefix=None, logical_switch=False):
    """Internal function for scan(). Determine the fabric WWN, FID , and zone configurations

    :param fab_obj: Fabric object
    :type fab_obj:: brcddb.classes.fabric.FabricObj
    :param in_prefix: Message prefix. Typically spaces for report formatting
    :type in_prefix: None, str
    :param logical_switch: If True, include logical switch information
    :type logical_switch: bool
    :return: Fabric, zone, and logical switch information messages
    :rtype: list
    """
    # Fabric name and FIDs
    pbuf = '' if in_prefix is None else in_prefix
    ml = ['',
          brcddb_fabric.best_fab_name(fab_obj, wwn=True, fid=True),
          '',
          '  Zone Configurations:']

    # Zone Configurations
    eff_zonecfg = fab_obj.r_defined_eff_zonecfg_key()
    for buf in [str(b) for b in fab_obj.r_zonecfg_keys()]:
        if isinstance(eff_zonecfg, str) and eff_zonecfg == buf:
            ml.append('  *' + buf)
        elif buf != '_effective_zone_cfg':
            ml.append('  ' + buf)

    # Logical switches
    if logical_switch:
        ml.extend(['', '  Logical Switches:'])
        for switch_obj in fab_obj.r_switch_objects():
            ml.append('    ' + brcddb_switch.best_switch_name(switch_obj, wwn=True, did=True, fid=True))

    return [pbuf + buf for buf in ml]


def scan(proj_obj, fab_only=False, logical_switch=False):
    """Scan the project for each fabric and determine the fabric WWN, FID , and zone configurations

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param fab_only: If True, return info for fabrics only. Otherwise, report chassis + fabric info
    :type fab_only: bool
    :param logical_switch: If True, include logical switch information
    :type logical_switch: bool
    :return: fabric WWN, FID , and zone configurations for each logical fabric
    :rtype: list
    """
    rl = list()

    if fab_only:
        for fab_obj in proj_obj.r_fabric_objects():
            rl.extend(_scan_fabric(fab_obj, logical_switch=logical_switch))
    else:
        for chassis_obj in proj_obj.r_chassis_objects():
            rl.extend(['Chassis: ' + brcddb_chassis.best_chassis_name(chassis_obj, wwn=True), ''])
            for switch_obj in chassis_obj.r_switch_objects():
                fab_obj = switch_obj.r_fabric_obj()
                zonecfg_l = list()
                if fab_obj is not None:
                    for zonecfg_obj in fab_obj.r_zonecfg_objects():
                        buf = '      ' + zonecfg_obj.r_obj_key()
                        if '_effective_zone_cfg' not in buf:
                            if zonecfg_obj.r_is_effective():
                                buf += ' (effective zone configuration)'
                            zonecfg_l.append(buf)
                rl.extend([
                    '  Switch: ' + brcddb_switch.best_switch_name(switch_obj, did=True, wwn=True, fid=True),
                    '    Member of Fabric: ' + brcddb_fabric.best_fab_name(fab_obj, wwn=True, fid=True),
                    '    Zone Configurations: ',
                ])
                if len(zonecfg_l) == 0:
                    zonecfg_l.append('      None')
                rl.extend(zonecfg_l)
                rl.append('')
    return rl
