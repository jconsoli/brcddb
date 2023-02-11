# Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli.  All rights reserved.
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
:mod:`brcddb_project` - Support for project level operations.

Public Methods & Data::

    +---------------------------+-----------------------------------------------------------------------------------+
    | Method                    | Description                                                                       |
    +===========================+===================================================================================+
    | new                       | Creates a new project object                                                      |
    +---------------------------+-----------------------------------------------------------------------------------+
    | dup_wwn                   | Searches all fabrics in the project for duplicate WWNs.                           |
    +---------------------------+-----------------------------------------------------------------------------------+
    | read_from                 | Creates a new project object from a JSON dump of a previous project object.       |
    +---------------------------+-----------------------------------------------------------------------------------+
    | build_xref                | Builds cross references for brcddb objects. This is necessary because it's not    |
    |                           | immediately obvious how request data is interrelated.                             |
    +---------------------------+-----------------------------------------------------------------------------------+
    | add_custom_search_terms   | The search utility cannot dereference embedded lists so create custom search      |
    |                           | terms. See module header for details.                                             |
    +---------------------------+-----------------------------------------------------------------------------------+
    | fab_obj_for_user_name     | Returns a list of fabric objects matching a user friendly name. May be a regex    |
    |                           | match, regex search, wild card, or exact match.                                   |
    +---------------------------+-----------------------------------------------------------------------------------+
    | switch_obj_for_user_name  | Returns a list of switch objects matching a user friendly name. May be a regex    |
    |                           | match, regex search, wild card, or exact match.                                   |
    +---------------------------+-----------------------------------------------------------------------------------+
    | best_project_name         | Returns the project object key                                                    |
    +---------------------------+-----------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 14 Nov 2020   | Handle all port speeds.                                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 14 Mar 2021   | Added fab_obj_for_user_name()                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 17 Jul 2021   | Get _DUP_WWN_CHECK from brcddb/app_data.bp_tables.                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 14 Nov 2021   | Improved readability and updated comments. No functional changes                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 31 Dec 2021   | Added ability to determine remote SFP speed by HBA when remote speed unavailable  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 28 Apr 2022   | Updated documentation.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 23 Jun 2022   | Added switch_obj_for_user_name()                                                  |
    |           |               | Use proj_obj.r_login_obj() in dup_wwn() to find duplicate WWNs.                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 25 Jul 2022   | Improved error messaging in read_from() for invalid project files.                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 10 Dec 2022   | Added the ability to set duplicate WWN checking externally. See _dup_wwn_check    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.3     | 11 Feb 2023   | Added best_project_name()                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '11 Feb 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.3'

import brcdapi.log as brcdapi_log
import brcdapi.file as brcdapi_file
import brcdapi.gen_util as gen_util
import brcddb.classes.project as project_class
import brcddb.util.copy as brcddb_copy
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_common as brcddb_common
import brcddb.util.search as brcddb_search
import brcddb.brcddb_switch as brcddb_switch

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
    """Builds cross references for brcddb objects. This is necessary because it's not immediately obvious how request
       data is interrelated.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    # We'll need to figure out where all the logins are so build a table to cross-reference all the neighbor WWNs
    brcddb_util.build_login_port_map(proj_obj)
    brcddb_util.add_maps_groups(proj_obj)


def add_custom_search_terms(proj_obj):
    """The search utility cannot dereference embedded lists so create custom search terms. Terms added are:

    Port Objects:
    _search/sfp_max_speed (in Gbps)
    _search/sfp_min_speed (in Gbps)
    _search/remote_sfp_max_speed (in Gbps)
    _search/remote_sfp_min_speed (in Gbps)
    _search/max_login_speed (in Gbps. This is the maximum common to both the local and remote SFPs)
    _search/speed (in Gbps - This is fibrechannel/speed, which is bps, converted to Gbps. The actual login speed)

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for port_obj in proj_obj.r_port_objects():
        # Find the maximum speed & add something to the port & login objects we can search against.
        max_sfp = max_r_sfp = None
        search = port_obj.r_get('_search')
        if search is None:
            search = dict()
            port_obj.s_new_key('_search', search)

        # Get the maximum and minimum speeds supported by the switch SFP
        l = port_obj.r_get('media-rdp/media-speed-capability/speed')
        if isinstance(l, (list, tuple)):
            max_sfp = max(l)
            if 'sfp_max_speed' not in search:
                search.update(sfp_max_speed=max_sfp)
            if 'sfp_min_speed' not in search:
                search.update(sfp_min_speed=min(l))

        # Get the maximum and minimum speeds supported by the remote (attached device) SFP
        l = port_obj.r_get('media-rdp/remote-media-speed-capability/speed')
        if l is None:  # No speed from remote SFP so try to figure it out based on the HBA type
            for d in brcddb_common.hba_remote_speed:
                if len(brcddb_search.match_test(port_obj.r_login_objects(), d['f'])) > 0:
                    l = d['s']
                    break
        if isinstance(l, (list, tuple)):
            max_r_sfp = max(l)
            if 'remote_sfp_max_speed' not in search:
                search.update(remote_sfp_max_speed=max_r_sfp)
            if 'remote_sfp_min_speed' not in search:
                search.update(remote_sfp_min_speed=min(l))

        # Get the maximum supported speed (the lesser of the maximum local speed and maximum attached speed)
        if isinstance(max_sfp, int) and isinstance(max_r_sfp, int):
            if 'max_login_speed' not in search:
                search.update(max_login_speed=min([max_sfp, max_r_sfp]))

        # Convert the actual login speed, which is bps, to Gbps for easier comparisons to the SFP speed capabilities
        if 'speed' not in search:
            v = gen_util.non_decimal.sub('', port_obj.c_login_speed())
            if len(v) > 0:
                search.update(speed=int(v))


def fab_obj_for_user_name(proj_obj, name, match_type='exact'):
    """Returns a list of fabric objects matching a user friendly name.

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
        dict(
            k='brocade-fibrechannel-switch/fibrechannel-switch/fabric-user-friendly-name',
            v=name,
            t=match_type,
            i=False
        )
    )
    return gen_util.remove_duplicates([switch_obj.r_fabric_obj() for switch_obj in sl])


def switch_obj_for_user_name(proj_obj, name, match_type='exact'):
    """Returns a list of switch objects matching a user friendly name.

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param name: User friendly switch name
    :type name: str
    :param match_type: Allowed types are: 'exact', 'wild', 'regex-m', 'regex-s'
    """
    return gen_util.remove_duplicates(
        brcddb_search.match_test(
            proj_obj.r_switch_objects(),
            dict(
                k='brocade-fibrechannel-switch/fibrechannel-switch/user-friendly-name',
                v=name,
                t=match_type,
                i=False)
        )
    )


def best_project_name(proj_obj):
    """Returns the user friendly project name.

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
