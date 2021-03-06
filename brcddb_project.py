#!/usr/bin/python
# Copyright 2019, 2020, 2021 Jack Consoli.  All rights reserved.
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
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '26 Jan 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.3'

import brcddb.classes.project as project_class
import brcddb.brcddb_fabric as brcddb_fabric
import brcdapi.log as brcdapi_log
import brcddb.util.copy as brcddb_copy
import brcddb.util.file as brcddb_file
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_common as brcddb_common


def new(name, date):
    """Creates a new project object
    :param name: User defined project date
    :type name: str
    :param date: Project date
    :type date: str
    """
    return project_class.ProjectObj(name, date)


def dup_wwn(proj_obj):
    """Searches all fabrics in the project for duplicate WWNs.
    :param proj_obj: Project object
    :type proj_obj: ProjectObj
    :return: List of login objects for the duplicate WWNS. None entry seperates multiple duplicates
    :rtype: list
    """
    dup_wwn = list()
    dup_login = list()
    for fabObj in proj_obj.r_fabric_objects():
        other_fab_list = proj_obj.r_fabric_objects()
        other_fab_list.remove(fabObj)

        for wwn in fabObj.r_login_keys():
            dup_login_len = len(dup_login)
            for fobj in other_fab_list:
                if fobj.r_login_obj(wwn) is not None:
                    if wwn not in dup_wwn:
                        dup_wwn.append(wwn)
                        proj_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_DUP_LOGIN, None, wwn)
                    login_obj = fobj.r_login_obj(wwn)
                    if login_obj not in dup_login:
                        dup_login.append(login_obj)
                        login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_DUP_LOGIN, None,
                                              brcddb_fabric.best_fab_name(fabObj))
                    login_obj = fabObj.r_login_obj(wwn)
                    if login_obj not in dup_login:
                        dup_login.append(login_obj)
                        login_obj.s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.LOGIN_DUP_LOGIN, None,
                                                        brcddb_fabric.best_fab_name(fobj))
            if len(dup_login) > dup_login_len:
                dup_login.append(None)

    return dup_login


def read_from(inf):
    """Creates a new project object from a JSON dump of a previous project object.

    :param inf: Input file name written with brcddb_util.write_dump()
    :type name: str
    """
    obj = brcddb_file.read_dump(inf)
    if obj is None or obj.get('_obj_key') is None or obj.get('_date') is None:
        brcdapi_log.log(inf + ' is not a valid project file.', True)
        return None
    # Make sure there is a valid Excel tab name
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
    _search/speed (in Gbps - This is fibrechannel/speed, which is bps, converted to Gbps)

    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for port_obj in proj_obj.r_port_objects():
        # Find the maximum speed & add something to the port & login objects we can search against.
        max_r_sfp = None
        max_sfp = None
        search = port_obj.r_get('_search')
        if search is None:
            search = dict()
            port_obj.s_new_key('_search', search)

        # Get the maximum and minimum speeds supported by the switch SFP
        l = port_obj.r_get('media-rdp/media-speed-capability/speed')
        if isinstance(l, (list, tuple)):
            max_sfp = max(l)
            if 'sfp_max_speed' not in search:
                search.update({'sfp_max_speed': max_sfp})
            if 'sfp_min_speed' not in search:
                search.update({'sfp_min_speed': min(l)})

        # Get the maximum and minimum speeds supported by the remote (attached device) SFP
        l = port_obj.r_get('media-rdp/remote-media-speed-capability/speed')
        if isinstance(l, (list, tuple)):
            max_r_sfp = max(l)
            if 'remote_sfp_max_speed' not in search:
                search.update({'remote_sfp_max_speed': max_r_sfp})
            if 'remote_sfp_min_speed' not in search:
                search.update({'remote_sfp_min_speed': min(l)})

        # Get the maximum supported speed (the lesser of the maximum local speed and maximum attached speed)
        if isinstance(max_sfp, int) and isinstance(max_r_sfp, int):
            if 'max_login_speed' not in search:
                search.update({'max_login_speed': min([max_sfp, max_r_sfp])})

        # Convert the actual login speed, which is bps, to Gbps for easier comparisons to the SFP speed capabilities
        if 'speed' not in search:
            v = brcddb_util.non_decimal.sub('', port_obj.c_login_speed())
            if len(v) > 0:
                search.update({'speed': int(v)})
