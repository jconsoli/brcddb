"""
Copyright 2023, 2024, 2025 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Descrition**

Methods and tables to support the class SwitchObj.

**Public Methods**

+-----------------------+---------------------------------------------------------------------------------------+
| Method                | Description                                                                           |
+=======================+=======================================================================================+
| add_rest_port_data    | Adds port statistics from rest request 'brocade-interface/fibrechannel-statistics' to |
|                       | each port object                                                                      |
+-----------------------+---------------------------------------------------------------------------------------+
| best_switch_name      | Returns the user friendly switch name, optionally with the switch WWN in parenthesis. |
|                       | If the switch is not named, ust the switch WWN is returned                            |
+-----------------------+---------------------------------------------------------------------------------------+
| copy_switch_obj       | Makes a copy of a switch object                                                       |
+-----------------------+---------------------------------------------------------------------------------------+
| port_obj_for_index    | Returns the port object matching port_index                                           |
+-----------------------+---------------------------------------------------------------------------------------+
| switch_fid            | Returns the switch FID as an integer                                                  |
+-----------------------+---------------------------------------------------------------------------------------+
| switch_ge_ports       | Returns the list of GE ports in the switch                                            |
+-----------------------+---------------------------------------------------------------------------------------+
| switch_ports          | Returns the list of ports in the switch                                               |
+-----------------------+---------------------------------------------------------------------------------------+
| switch_type           | Returns the switch type: Default, FICON, Base, FCP                                    |
+-----------------------+---------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 20 Feb 2026   | Updated copyright notice.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025, 2026 Jack Consoli'
__date__ = '20 Feb 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

import time
import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.util.copy as brcddb_copy

area_mode = {
    0: ' 10-bit addressing mode',
    1: ' Zero-based area assignment',
    2: ' Port-based area assignment',
}


def add_rest_port_data(switch_obj, pobj, flag_obj=None, in_skip_list=None):
    """Adds port statistics from rest request 'brocade-interface/fibrechannel-statistics' to each port object

    :param switch_obj: Switch object
    :type switch_obj: SwitchObj
    :param pobj: Object returned from the FOS Rest API
    :type pobj: dict
    :param flag_obj: Not used. Must be here for methods that call rest add methods from a table.
    :type flag_obj: None
    :param in_skip_list: Keys to skip
    :type in_skip_list: (list, tuple)
    :rtype: None
    """
    skip_list = in_skip_list if isinstance(in_skip_list, (list, tuple)) else list()
    sl = ['name', 'enabled-state']
    sl.extend(skip_list)
    for k in pobj.keys():
        for pdict in gen_util.convert_to_list(pobj.get(k)):
            if k == 'media-rdp':
                # The media name is in the format type/s/p, but for everything else, it's just s/p, which is how the key
                # is created for the port object in the switch object. By splitting on '/', removing the first list
                # element, and joining the rest with '/', I end up with just s/p.
                port_obj = switch_obj.s_add_port('/'.join(pdict.get('name').split('/')[1:]))
            else:
                port_obj = switch_obj.s_add_port(pdict.get('name'))
            v = dict()
            port_obj.s_new_key(k, v)
            brcddb_copy.object_copy(pdict, v, port_obj, sl)
            # Make sure there is a login object for every login found
            fab_obj = switch_obj.r_fabric_obj()
            if fab_obj is not None:
                for wwn in port_obj.r_login_keys():
                    fab_obj.s_add_login(wwn)


def best_switch_name(switch_obj, wwn=False, did=False, fid=False):
    """Returns the user-friendly switch name, optionally with the switch WWN in parentheses. If the switch is not named,
       just the switch WWN is returned

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param wwn: If True, append (wwn) to the switch name
    :type wwn: bool
    :param did: If True, append (DID) to the switch name
    :type did: bool
    :param fid: If Ture, append (FID) to switch name
    :type fid: bool
    :return: Switch name
    :rtype: str
    """
    wwn_f = wwn
    if switch_obj is None:
        return 'Unknown'
    buf = switch_obj.r_get(brcdapi_util.bfs_sw_user_name)
    if buf is None:
        buf = switch_obj.r_get(brcdapi_util.bf_sw_user_name)
    if buf is None:
        buf = ''
        wwn_f = True
    if fid:
        fid_num = switch_obj.r_get(brcdapi_util.bfls_fid)
        if fid_num is not None:
            buf += ' FID: ' + str(fid_num)
    if did:
        did_num = switch_obj.r_get(brcdapi_util.bfs_did)
        if did_num is None:
            did_num = switch_obj.r_get('brocade-fabric/fabric-switch/domain-id')
        if did_num is not None:
            buf += ' DID: ' + str(did_num)
    if wwn_f:
        buf += ' (' + switch_obj.r_obj_key() + ')'

    return buf


def switch_type(switch_obj):
    """Returns the switch type: Default, FICON, Base, FCP

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Switch type. None if switch_obj is None
    :rtype: str, None
    """
    if switch_obj is None:
        return None
    if switch_obj.r_get(brcdapi_util.bfls_def_sw_status):
        return 'Default'
    if switch_obj.r_get(brcdapi_util.bfls_ficon_mode_en):
        return 'FICON'
    if switch_obj.r_get(brcdapi_util.bfls_base_sw_en):
        return 'Base'
    return 'FCP'


def switch_fid(switch_obj):
    """Returns the switch FID as an integer

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Switch FID. Returns None if non-VF, logical switch data not yet captured, or  or switch_obj is None
    :rtype: int, None
    """
    return None if switch_obj is None else switch_obj.r_get(brcdapi_util.bfls_fid)


def switch_ports(switch_obj):
    """Returns the list of ports in the switch

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: List of ports in switch. Empty if no ports but None if not polled or switch_obj is None
    :rtype: list, None
    """
    return None if switch_obj is None else\
        switch_obj.r_get(brcdapi_util.bfls_mem_list)


def switch_ge_ports(switch_obj):
    """Returns the list of GE ports in the switch

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: List of GE ports in switch. Empty if no ports but None if not polled or switch_obj is None
    :rtype: list, None
    """
    return None if switch_obj is None else\
        switch_obj.r_get(brcdapi_util.bfls_ge_mem_list)


def port_obj_for_index(switch_obj, port_index):
    """Returns the port object matching port_index

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param port_index: Port index
    :type port_index: int
    :return: List of GE ports in switch. Empty if no ports but None if not polled or switch_obj is None
    :rtype: list, None
    """
    for port_obj in switch_obj.r_port_objects():
        i = port_obj.r_index()
        if isinstance(i, int) and i == port_index:
            return port_obj
    return None


def copy_switch_obj(switch_obj, switch_key=None, full_copy=False):
    """Makes a copy of a switch object

    :param switch_obj: The switch object to be copied
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param switch_key: Name for the copied switch. If None, the key is the same as for switch_obj with "_copy" appended
    :type switch_key: str, None
    :param full_copy: If True, copies all data added with s_new_key(). Otherwise, just the private members are copied
    :type full_copy: bool
    :return: Copy of switch object
    :rtype: brcddb.classes.switch.SwitchObj
    """
    proj_obj = switch_obj.r_project_obj()
    new_key = switch_obj.r_obj_key() + '_copy' if switch_key is None else switch_key
    switch_obj_copy = proj_obj.s_add_switch(new_key)
    switch_obj_copy.s_or_flags(switch_obj.r_flags())
    switch_obj_copy.s_fabric_key(switch_obj.r_fabric_key())
    switch_obj_copy.s_chassis_key(switch_obj.r_chassis_key())
    for obj in switch_obj.r_port_objects():
        port_obj_copy = switch_obj_copy.s_add_port(obj.r_obj_key())
        if full_copy:
            for key in obj.r_keys():
                port_obj_copy.s_new_key(key, obj.r_get(key))
    for obj in switch_obj.r_ge_port_objects():
        port_obj_copy = switch_obj_copy.s_add_ge_port(obj.r_obj_key())
        if full_copy:
            for key in obj.r_keys():
                port_obj_copy.s_new_key(key, obj.r_get(key))
    if full_copy:
        for key in switch_obj.r_keys():
            switch_obj_copy.s_new_key(key, switch_obj.r_get(key))

    return switch_obj_copy
