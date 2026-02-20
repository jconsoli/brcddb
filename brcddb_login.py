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

Login level utilities.

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| fdmi_node_name        | Returns the FDMI node symbolic name                                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| ns_node_name          | Returns the Name Server node symbolic name                                                |
+-----------------------+-------------------------------------------------------------------------------------------+
| login_best_node_desc  | Finds the first descriptor for what's attached to the port. See module header for details |
+-----------------------+-------------------------------------------------------------------------------------------+
| login_best_port_desc  | Finds the first descriptor for this login using the FDMI port descriptor, name server,    |
|   `                   | and FDMI node descriptor.                                                                 |
+-----------------------+-------------------------------------------------------------------------------------------+
| best_login_name       | Returns the alias, WWN, or d,i for the name parameter                                     |
+-----------------------+-------------------------------------------------------------------------------------------+
| login_type            | Returns the login type, if available. Otherwise, ''                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| login_features        | Returns the FC-4 features as returned from the API. Returns '' if unavailable.            |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 20 Feb 2026   | Updated copyright notice.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025, 2026 Jack Consoli'
__date__ = '20 Feb 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.5'

import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util

_MIN_SYMB_LEN = 10


def fdmi_node_name(fdmi_obj, wwn):
    """Returns the FDMI node symbolic name

    :param fdmi_obj: Login Object
    :type fdmi_obj: brcddb.classes.login.FdmiNodeObj
    :param wwn: WWN
    :type wwn: str
    :return: Node name
    :rtype: str, None
    """
    if fdmi_obj is not None and isinstance(wwn, str):
        buf = fdmi_obj.r_get('brocade-fdmi/hba/node-symbolic-name')
        if isinstance(buf, str) and len(buf) < _MIN_SYMB_LEN:
            return buf
    return None


def ns_node_name(login_obj):
    """Returns the Name Server node symbolic name

    :param login_obj: Login Object
    :type login_obj: brcddb.classes.login.LoginObj
    :return: Node name
    :rtype: str, None
    """
    try:
        return login_obj.r_get(brcdapi_util.bns_node_symbol)
    except AttributeError:
        return None


def login_best_node_desc(login_obj):
    """Finds the first descriptor for what's attached to the port in this order:
        1   FDMI  Node (HBA) descriptor
        2   Name server node descriptor

    :param login_obj: Login Object
    :type login_obj: brcddb.classes.login.login_obj
    :return: desc
    :rtype: str
    """
    if login_obj is None:
        return ''
    maybe = None
    fab_obj = login_obj.r_fabric_obj()
    wwn = login_obj.r_obj_key()

    # Try FDMI node (HBA) data
    buf = fdmi_node_name(fab_obj.r_fdmi_node_obj(wwn), wwn)
    if buf is not None:
        if len(buf) < _MIN_SYMB_LEN:
            maybe = buf
        else:
            return buf

    # Try the name server Node data
    buf = ns_node_name(login_obj)
    if buf is not None:
        if len(buf) < _MIN_SYMB_LEN:
            maybe = buf
        else:
            return buf

    return '' if maybe is None else maybe


def login_best_port_desc(login_obj):
    """Finds the first descriptor for this login using the FDMI port descriptor, name server, and FDMI node descriptor

    :param login_obj: Login Object
    :type login_obj: brcddb.classes.login.login_obj
    :return: desc
    :rtype: str
    """
    if login_obj is None:
        return ''
    maybe = ''
    fab_obj = login_obj.r_fabric_obj()
    wwn = login_obj.r_obj_key()

    # Try FDMI port data
    try:
        buf = fab_obj.r_fdmi_port_obj(wwn).r_get('brocade-fdmi/port/port-symbolic-name')
        if buf is not None:
            if len(buf) < _MIN_SYMB_LEN:
                maybe = buf
            else:
                return buf
    except AttributeError:
        pass

    # Try the name server port data
    buf = login_obj.r_get('brocade-name-server/brocade-name-server/port-symbolic-name')
    if buf is not None:
        if _MIN_SYMB_LEN > len(buf) > len(maybe):
            maybe = buf
        else:
            return buf

    # Try the node
    buf = login_best_node_desc(login_obj)

    return maybe if len(maybe) > len(buf) else buf


def best_login_name(fab_obj, name, flag=False):
    """Returns the alias, WWN, or d,i for the name parameter

    :param fab_obj: Fabric Object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param name: WWN or d,i
    :type name: str
    :param flag: If True, include the WWN or d,i in parentheses
    :return: desc
    :rtype: str
    """
    alias_l = gen_util.convert_to_list(fab_obj.r_alias_for_wwn(name))
    return name if len(alias_l) == 0 else alias_l[0] + ' (' + name + ')' if flag else alias_l[0]


def login_type(login_obj):
    """Returns the login type as returned from the API. Returns '' if unavailable.

    :param login_obj: Login Object
    :type login_obj: brcddb_classes.login.LoginObj
    :return: Login type
    :rtype: str
    """
    try:
        fc4_type = login_obj.r_get('brocade-name-server/fibrechannel-name-server/fc4-type')
        return '' if fc4_type is None else fc4_type
    except AttributeError:
        return ''


def login_features(login_obj):
    """Returns the FC-4 features as returned from the API. Returns '' if unavailable.

    :param login_obj: Login Object
    :type login_obj: brcddb_classes.login.LoginObj
    :return: Login type
    :rtype: str
    """
    try:
        fc4_feature = login_obj.r_get(brcdapi_util.bns_fc4_features)
        return '' if fc4_feature is None else fc4_feature
    except AttributeError:
        return ''
