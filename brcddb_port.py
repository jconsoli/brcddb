"""
Copyright 2023, 2024, 2025 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Methods and tables to support the class ChassisObj.

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| port_best_desc        | Finds the first descriptor for what's attached to the port. See module header for details.|
+-----------------------+-------------------------------------------------------------------------------------------+
| best_port_name        | Returns the user defined port name, if available. Otherwise, the port number              |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_obj_for_index    | Returns the port object for a port index.                                                 |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_obj_for_wwn      | Returns the port object for a logged in WWN                                               |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_obj_for_chpid    | Returns the port object matching the rnid/sequence-number and rnid/tag. Used for finding  |
|                       | CHPIDs                                                                                    |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_obj_for_addr     | Returns the port object for a port in a given fabric matching a link address. Used for    |
|                       | finding control units                                                                     |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_objects_for_addr | Returns a list of port objects using an exact, wild card, or regex match of the fibre     |
|                       | channel address.                                                                          |
+-----------------------+-------------------------------------------------------------------------------------------+
| port_objects_for_name | Returns a list of port objects using an exact, wild card, or regex match of the port name |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Added more error checking. Deleted port_type()                                        |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Added more RNID data to port_best_desc()                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 26 Dec 2024   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025 Consoli Solutions, LLC'
__date__ = '19 Oct 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.6'

import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.brcddb_switch as brcddb_switch
import brcddb.brcddb_login as brcddb_login
import brcddb.util.search as brcddb_search
import brcddb.util.iocp as brcddb_iocp


# _rnid_keys is used in port_best_desc() to add additional RNID data. This is not a complete list of RNID data
_rnid_keys = ('manufacturer', 'model-number', 'sequence-number', 'tag', 'flags')


def port_best_desc(port_obj):
    """Finds the first descriptor for what's attached to the port in this order:
        1   RNID data if RNID data is present
        2   If E-Port, the upstream switch & port
        3   FDMI  Node descriptor
        4   FDMI Port descriptor
        5   Name server node descriptor
        6   Name server port descriptor

    :param port_obj: Port Object
    :type port_obj: brcddb.classes.port.PortObj
    :return: desc
    :rtype: str
    """
    global _rnid_keys

    if port_obj is None:
        return 'Unknown'

    # Try RNID data
    rnid_d = port_obj.r_get('rnid')
    if isinstance(rnid_d, dict) and 'type-number' in rnid_d:
        return (brcddb_iocp.dev_type_desc(rnid_d['type-number']) + ' ' +
                ' '.join([rnid_d.get(k, '') for k in _rnid_keys]))

    wwn_list = port_obj.r_get(brcdapi_util.fc_neighbor_wwn, list())
    if len(wwn_list) == 0:
        return ''

    # Try E-Port
    fab_obj = port_obj.r_fabric_obj()
    if fab_obj is None:
        return ''
    if port_obj.c_login_type() in ('E-Port', 'AE-Port'):
        brcddb_util.build_login_port_map(fab_obj.r_project_obj())
        pobj = fab_obj.r_get('_port_map').get(wwn_list[0])
        return '' if pobj is None else brcddb_switch.best_switch_name(pobj.r_switch_obj()) + ' port ' + pobj.r_obj_key()

    # Try Node, then port
    login_obj = fab_obj.r_login_obj(wwn_list[0])
    if login_obj is None:
        return ''
    buf = brcddb_login.login_best_node_desc(login_obj)
    if len(buf) > 2:
        return buf
    return brcddb_login.login_best_port_desc(login_obj)


def best_port_name(port_obj, port_num=False):
    """Returns the user defined port name, if available. Otherwise, the port number

    :param port_obj: Port Object
    :type port_obj: brcddb_classes.port.PortObj
    :param port_num: If True, append (port number) to the port name
    :type port_num: bool
    :return: Port name
    :rtype: str
    """
    buf = port_obj.r_get(brcdapi_util.fc_user_name)
    if buf is None:
        return port_obj.r_obj_key()
    if port_num:
        return buf + ' (' + port_obj.r_obj_key() + ')'
    return buf


def port_obj_for_index(obj, index):
    """Returns the port object for a port index.

    :param obj: Object with port objects, obj.r_port_objects()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param index: Port index
    :type index: int
    :return: Port object. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    for port_obj in obj.r_port_objects():
        port_index = port_obj.r_get(brcdapi_util.fc_index)
        if port_index is not None and port_index == index:
            return port_obj

    return None  # If we got this far, we didn't find it.


def port_obj_for_wwn(obj, wwn):
    """Returns the port object for a logged in WWN

    :param obj: Object with port objects, obj.r_port_objects()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param wwn: Login WWN
    :type wwn: str
    :return: Port object. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    if not gen_util.is_wwn(wwn):
        return None
    for port_obj in obj.r_port_objects():
        for port_wwn in gen_util.convert_to_list(port_obj.r_get(brcdapi_util.fc_neighbor_wwn)):
            if port_wwn is not None and port_wwn == wwn:
                return port_obj

    return None  # If we got this far, we didn't find it.


def port_obj_for_chpid(obj, seq, tag):
    """Returns the port object matching the rnid/sequence-number and rnid/tag. Used for finding CHPIDs

    :param obj: Object with port objects, obj.r_port_objects()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param seq: Serial number (sequence number) for CEC
    :type seq: str
    :param tag: CHPID tag
    :type tag: str
    :return: Port object where this CHPID is connected. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    # The tag from the IOCP will never have '0x' prefix, so adding it if it's missing is in case I ever use this
    # function for a tag that came from elsewhere.
    port_list = brcddb_search.match_test(
        obj.r_port_objects(),
        {
            'l': (
                dict(k='rnid/sequence-number', t='exact', v=brcddb_iocp.full_cpc_sn(seq), i=True),
                dict(k='rnid/tag', t='exact', v=tag if '0x' in tag else '0x' + tag, i=True),
                dict(k='rnid/flags', t='exact', v='0x10'),  # Indicates the RNID data is valid for a channel
            ),
            'logic': 'and'  # 'and' is the default logic so this is just for clarity for the reader
        }
    )
    return port_list[0] if len(port_list) > 0 else None


def port_objects_for_addr(obj, addr, search='exact'):
    """Returns a list of port objects using an exact, wild card, or regex match of the fibre channel address.

    :param obj: Object with port objects, obj.r_port_objects()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param addr: Hex FC address. Not case-sensitive. Must begin with '0x'. Remaining characters depend on search type.
    :type addr: str
    :param search: Search type. Must be one of the search types accepted by brcddb_search.match_test()
    :type search: str
    :return: Port object matching the link address. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    return brcddb_search.match_test(
        obj.r_port_objects(),
        dict(k='fibrechannel/fcid-hex', t=search, v=addr, i=True)
    )


def port_obj_for_addr(obj, addr):
    """Returns the port object for a port matching a fibre channel address.

    WARNING: Project objects may contain multiple switches with the same DID, therefore, it's possible to match multiple
    ports to the same address. This function returns the first port object found.

    :param obj: Object with port objects, obj.r_port_objects(). See warning above.
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param addr: Hex FC address (format is 0x123400)
    :type addr: str
    :return: Port object matching the link address. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    port_list = port_objects_for_addr(obj, addr)
    return port_list[0] if len(port_list) > 0 else None


def port_objects_for_name(obj, name, search='exact'):
    """Returns a list of port objects using an exact, wild card, or regex match of the port name.

    :param obj: Object with port objects, obj.r_port_objects()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.fabric.FabricObj, brcddb.classes.project.ProjectObj,
                brcddb.classes.chassis.ChassisObj
    :param name: Port name + search characters (if applicable). Case-sensitive.
    :type name: str
    :param search: Search type. Must be one of the search types accepted by brcddb_search.match_test()
    :type search: str
    :return: Port object matching the link address. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    return brcddb_search.match_test(
        obj.r_port_objects(),
        dict(k=brcdapi_util.fc_user_name, t=search, v=name, i=False)
    )
