#!/usr/bin/python
# Copyright 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcdd.classes.iocp` - Defines the IOCP class IOCPObj

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 02 Aug 2020   | Initial                                                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020 Jack Consoli'
__date__ = '02 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import brcddb.classes.alert as alert_class
import brcddb.classes.util as util 

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revist this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


def version():
    """Returns the module version number
    :return: Version
    :rtype: str
    """
    return __version__


class IOCPObj:
    """The ZoneCfgObj contains all information relevant to a zone configuration including:
        * 'brocade-fibrechannel-configuration/zone-configuration'

    Attributes:
        _obj_key (str): Name of the zone configuration.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _members (dict): Dictionary of control units. Key is the CUNUMBER
        _pmembers (list): Dictionary of paths. Key is the CHPID tag
        _alerts (list): List of AlertObj objects associated with this object.

    Control unit dictionaries:
        'path': dict of:
                    chpid tag: link address
        'unitadd': list of unit addresses
        'cuadd': list of CU addresses
        'unit: str - unit type

    Path dictionaries:
        'pchid': str - Physical channel associated with thie CHPID
        'partition: list - List of partitions (str) or LPARs that can use this CHPID
        'link': list - List of link addresses (str) defined for this path
        'cu': list - LIst of control units defined for this path
    """

    def __init__(self, name, project_obj):
        self._obj_key = name
        self._flags = 0
        self._members = {}
        self._pmembers = {}
        self._alerts = []
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        # When adding a reserved key, don't forget you may also need to update brcddb.util.copy
        _reserved_keys = {
            '_obj_key': self.r_obj_key(),
            '_flags': self.r_flags(),
            '_alerts': self.r_alert_objects(),
            '_project_obj': self.r_project_obj(),
            '_members': self.r_cu_objects(),
            '_pmembers': self.r_path_objects(),
        }
        try:
            if k == '_reserved_keys':
                rl = list(_reserved_keys.keys())
                rl.append('_reserved_keys')
                return rl
            else:
                return _reserved_keys[k]
        except:
            return None

    def s_add_alert(self, tbl, num, key=None, p0=None, p1=None):
        """Add an alert to this object

        :param tbl: The table that defines this alert. See brcddb.classes.alert.AlertObj
        :type tbl: dict
        :param num: Alert number. See brcddb.classes.alert.AlertObj
        :type num: int
        :param key: Key associated with this alert. See brcddb.classes.alert.AlertObj
        :type key: str, None
        :param p0: Optional parameter. See brcddb.classes.alert.AlertObj
        :type p1: str, int, float, None
        :param p1: Optional parameter. See brcddb.classes.alert.AlertObj
        :return: Alert object
        :rtype: brcddb.classes.alert.AlertObj
        """
        alert_obj = alert_class.AlertObj(tbl, num, key, p0, p1)
        self._alerts.append(alert_obj)
        return alert_obj

    def r_alert_objects(self):
        """Returns a list of alert objects associated with this object

        :return: List of alert objects (brcddb.classes.alert.AlertObj)
        :rtype: list
        """
        return self._alerts

    def r_alert_nums(self):
        """Returns a list of alert numbers associated with this object

        :return: List of alert objects (brcddb.classes.alert.AlertObj)
        :rtype: list
        """
        return [alert_obj.alert_num() for alert_obj in self._alerts]

    def r_reserved_keys(self):
        """Returns a list of reserved words (keys) associated with this object

        :return: List of reserved words
        :rtype: list
        """
        return self.r_get_reserved('_reserved_keys')

    def r_project_obj(self):
        """Returns the project object associated with this object

        :return: Project object
        :rtype: ProjectObj
        """
        return self._project_obj

    def r_obj_key(self):
        """Returns key that is used in the parent object to retrieve this object

        :return: Object key
        :rtype: str
        """
        return self._obj_key

    def r_flags(self):
        """Returns flags associated with this object. Flags are defined in brcddb_common.py
        :return: Bit flags
        :rtype: int
        """
        return self._flags

    def s_or_flags(self, bits):
        """Performs a logical OR on the flags associated with this object. Flags are defined in brcddb_common.py

        :param bits: Bits to be ORed with the bit flags
        :type bits: int
        :return: Bit flags
        :rtype: int
        """
        self._flags |= bits
        return self._flags

    def s_and_flags(self, bits):
        """Performs a logical AND on the flags associated with this object. Flags are defined in brcddb_common.py

        :param bits: Bits to be ANDed with the bit flags
        :type bits: int
        :return: Bit flags
        :rtype: int
        """
        self._flags &= bits
        return self._flags

    def s_add_cu(self, cu_number, cu_info):
        """Add a control unit definition

        :param cu_number: Control unit number
        :type cu_number: str
        :param cu_info: Control unit dictionary
        :type cu_info: dict
        """
        if cu_number not in self._members:
            self._members.update({cu_number: cu_info})

    def r_cu(self, cu):
        """Returns control unit dictionary for the specified CU

        :param cu: Control unit number
        :type cu: str
        :return: The dictionary associtated with the specified control unit numbers
        :rtype: dict
        """
        return self._members.get(cu)

    def r_cu_list(self):
        """Returns a list of control units in the IOCP

        :return: The control unit numbers in a list of str
        :rtype: list
        """
        return [str(cu) for cu in self._members.keys()]

    def r_cu_objects(self):
        """Returns dictionary of control unit

        :return: Control unit dictionary
        :rtype: dict
        """
        return [self._members]

    def s_add_path(self, tag, path):
        """Add a control unit definition

        :param tag: CHPID tag
        :type tag: str
        :param path: Path dictionary
        :type path: dict
        """
        if tag not in self._pmembers:
            self._pmembers.update({tag: path})

    def r_path(self, tag):
        """Returns pathdictionary for the specified CHPID

        :param tag: CHPID tag
        :type tag: str
        :return: The dictionary associtated with the specified CHPID
        :rtype: dict
        """
        return self._pmembers.get(tag)

    def r_path_list(self):
        """Returns a list of paths in the IOCP

        :return: The path names (CHPID tags) in a list of str
        :rtype: list
        """
        return [str(cu) for cu in self._members.keys()]

    def r_path_objects(self):
        """Returns dictionary of paths

        :return: Path dictionary
        :rtype: dict
        """
        return self._pmembers

    def r_link_addr(self, tag):
        """Returns a tuple of link addresses associated with the specified path

        :param tag: CHPID tag
        :type tag: str
        :return: List of link addresses
        :rtype: tuple
        """
        path = self.r_path(tag)
        return tuple(path.get('link')) if path is not None and path.get('link') is not None else ()

    def r_has_link_addr(self, tag, addr):
        """Checks to see if an FC address or link address is part of a path

        :param tag: CHPID tag
        :type tag: str
        :param addr: Either an FC address (3 bytes) or link address (2 bytes)
        :return: True: Link address is in the path
        :rtype: bool
        """
        link_addr = addr[0: 4] if len(addr) > 4 else addr
        return True if link_addr in self.r_link_addr(tag) else False

    def s_new_key(self, k, v, f=False):
        """Creates a new key/value pair.

        :param k: Key to be added
        :type k: str, int
        :param v: Value to be added. Although any type should be valid, it has only been tested with the types below.
        :type v: str, int, list, dict
        :param f: If True, don't check to see if the key exists. Allows users to change an existing key.
        :type f: bool
        :return: True if the add succeeded or is redundant.
        :rtype: bool
        """
        return util.s_new_key_for_class(self, k, v, f)

    def r_get(self, k):
        """Returns the value for a given key. Keys for nested objects must be separated with '/'.

        :param k: Key
        :type k: str, int
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return util.class_getvalue(self, k)

    def r_keys(self):
        """Returns a list of keys added to this object.

        :return: List of keys
        :rtype: list
        """
        return util.class_getkeys(self)
