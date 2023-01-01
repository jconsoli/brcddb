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

:mod:`brcddb_login` - Login level utilities.

Public Methods::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | fdmi_node_name        | Returns the FDMI node symbolic name                                                   |
    +-----------------------+---------------------------------------------------------------------------------------+
    | ns_node_name          | Returns the Name Server node symbolic name                                            |
    +-----------------------+---------------------------------------------------------------------------------------+
    | login_best_node_desc  | Finds the first descriptor for what's attached to the port. See module header for     |
    |                       | details                                                                               |
    +-----------------------+---------------------------------------------------------------------------------------+
    | login_best_port_desc  | Finds the first descriptor for what's attached to the port. See module header for     |
    |                       | details.                                                                              |
    +-----------------------+---------------------------------------------------------------------------------------+
    | best_login_name       | Returns the alias, WWN, or d,i for the name parameter                                 |
    +-----------------------+---------------------------------------------------------------------------------------+
    | login_type            | Returns the login type, if available. Otherwise ''                                    |
    +-----------------------+---------------------------------------------------------------------------------------+
    | login_features        | Returns the FC-4 features as returned from the API. Returns '' if unavailable.        |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 15 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 31 Dec 2021   | Miscellaneous clean up. No functional changes.                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 28 Apr 2022   | Updated documentation                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 04 Sep 2022   | Added references for new API branches.                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 01 Jan 2022   | Added login_feature()                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '01 Jan 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import brcddb.util.util as brcddb_util

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
    return None if login_obj is None else login_obj.r_get('brocade-name-server/brocade-name-server/node-symbolic-name')


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
    """Finds the first descriptor for what's attached to the port in this order:
        1   FDMI  Port descriptor
        2   Name server port descriptor

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
        buf = fab_obj.r_fdmi_port_obj(wwn).r_get('brocade-fdmi/port-symbolic-name')
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
    :param flag: If True, include the WWN or d,i in parenthesis
    :return: desc
    :rtype: str
    """
    alias_l = brcddb_util.convert_to_list(fab_obj.r_alias_for_wwn(name))
    return name if len(alias_l) == 0 else alias_l[0] + ' (' + name + ')' if flag else alias_l[0]


def login_type(login_obj):
    """Returns the login type as returned from the API. Returns '' if unavailable.

    :param login_obj: Login Object
    :type login_obj: brcddb_classes.login.LoginObj
    :return: Login type
    :rtype: str
    """
    fc4_type = login_obj.r_get('brocade-name-server/fibrechannel-name-server/fc4-type')
    return '' if fc4_type is None else fc4_type


def login_features(login_obj):
    """Returns the FC-4 features as returned from the API. Returns '' if unavailable.

    :param login_obj: Login Object
    :type login_obj: brcddb_classes.login.LoginObj
    :return: Login type
    :rtype: str
    """
    fc4_feature = login_obj.r_get('brocade-name-server/fibrechannel-name-server/fc4-features')
    return '' if fc4_feature is None else fc4_feature
