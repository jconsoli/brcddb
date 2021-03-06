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

:mod:`brcddb_login` - Login level utilities.

    * Best login name

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
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '02 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

_MIN_SYMB_LEN = 10


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
    try:
        buf = fab_obj.r_fdmi_node_obj(wwn).r_get('brocade-fdmi/node-symbolic-name')
        if buf is not None:
            if len(buf) < _MIN_SYMB_LEN:
                maybe = buf
            else:
                return buf
    except:
        pass

    # Try the name server Node data
    buf = login_obj.r_get('brocade-name-server/node-symbolic-name')
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
    except:
        pass

    # Try the name server port data
    buf = login_obj.r_get('brocade-name-server/port-symbolic-name')
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
    try:
        l = fab_obj.r_alias_for_wwn(name)
        if len(l) == 0:
            return name
        else:
            return l[0] + ' (' + name + ')' if flag else l[0]
    except:
        return ''


def login_type(login_obj):
    """Returns the login type, if available. Otherwise ''

    :param login_obj: Chassis Object
    :type login_obj: brcddb_classes.chassis.ChassisObj
    :return: Login type
    :rtype: str
    """
    type = login_obj.r_get('brocade-name-server/fc4-type')
    return '' if type is None else type
