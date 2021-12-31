# Copyright 2020, 2021 Jack Consoli.  All rights reserved.
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
    | 3.0.1     | 22 Aug 2020   | Fixed r_cu_objects(), was returning a list of dict instead of dict.               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Removed method version().                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2021   | Use common util.get_reserved() in r_get_reserved()                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2021   | Fixed r_path_list() to return paths, not contol units. Fixed r_path_objects() and |
    |           |               | r_cu_objects().                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '31 Dec 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

import brcddb.classes.alert as alert_class
import brcddb.classes.util as util 

# Programmer's Tip: Apparently, .clear() doesn't work on de-referenced list and dict. Rather than write my own, I rely
# on Python garbage collection to clean it up. If delete becomes common, I'll have to revist this but for now, I took
# the easy way out. It may be a good thing that Python threw an exception because I didn't really think through what
# objects that might be sharing a resource with other objects.


class IOCPObj:
    """Contains FICON I/O subsystem information from a parsed IOCP only. It does not contain RNID data from the API.
    RNID data associated with the API is applied to the port objects. This is the equivalent of open systems zoning.

    Attributes:
        _obj_key (str): Name of the IOCP. Typically the CPC serial number.
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this IOCP belongs to.
        _chpid_objs (dict): Dictionary of paths. Key is the CHPID tag, value is the CHPID object, ChpidObj
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, name, project_obj):
        self._obj_key = name
        self._flags = 0
        self._chpid_objs = dict()
        self._alerts = list()
        self._project_obj = project_obj

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _chpid_objs=self.r_path_objects(),
            ),
            k
        )

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

    def s_add_chpid(self, tag, partition, pchid, switch_id):
        """Add a CHPID definition (from the CHPID macro in the IOCP)

        :param tag: CHPID tag
        :type tag: str
        :param partition: List of partitions (LPARs) in the CHPID macro
        :type partition: list
        :param pchid: Physical channel ID (PCHID)
        :type pchid: str
        :param switch_id: Switch ID (from SWITCH=) statement in the CHPID macro
        :type switch_id: str
        :return: CHPID object
        :rtype: ChpidObj
        """
        chpid_obj = self.r_path_obj(tag)
        if chpid_obj is None:
            chpid_obj = ChpidObj(tag, self.r_project_obj(), pchid, switch_id, partition)
            self._chpid_objs.update({tag: chpid_obj})
        return chpid_obj

    def r_path_obj(self, tag):
        """Returns path dictionary for the specified CHPID

        :param tag: CHPID tag
        :type tag: str
        :return: The dictionary associated with the specified CHPID
        :rtype: dict
        """
        return self._chpid_objs.get(tag)

    def r_path_list(self):
        """Returns a list of paths in the IOCP

        :return: The path names (CHPID tags) in a list of str
        :rtype: list
        """
        return [str(chpid) for chpid in self._chpid_objs.keys()]

    def r_path_objects(self):
        """Returns the list of chpid objects in this IOCP

        :return: List of path objects
        :rtype: list
        """
        return self._chpid_objs.values()

    def r_link_addr(self, tag):
        """Returns a list of link addresses associated with the specified path

        :param tag: CHPID tag
        :type tag: str
        :return: List of link addresses (each element is a str)
        :rtype: list
        """
        chpid_obj = self.r_path_obj(tag)
        return list() if chpid_obj is None else chpid_obj.r_link_addresses()

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


class ChpidObj:
    """The ZoneCfgObj contains all information relevant to a zone configuration including:
        * 'brocade-fibrechannel-configuration/zone-configuration'

    Attributes:
        _obj_key (str): CHPID tag
        _flags (int): Flags for each class are defined in brcddb.brcddb_common
        _project_obj (ProjectObj): The project object this fabric belongs to.
        _members (list): Partitions (LPARs) using this CHPID
        _pchid (str): Physical channel ID (PCHID)
        _switch_id (str): Switch ID (SWITCH= in CHPID macro)
        _link_addr (dict): Dictionary of link addresses. Key is the link address, value is a dictionary as follows:
            cu_num: dictionary of control unit numbers, value is the unit type.
        _alerts (list): List of AlertObj objects associated with this object.
    """

    def __init__(self, tag, project_obj, pchid, switch_id, partitions):
        self._obj_key = tag
        self._flags = 0
        self._members = partitions.copy()
        self._alerts = list()
        self._project_obj = project_obj
        self._pchid = pchid
        self._switch_id = switch_id
        self._link_addr = dict()

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return util.get_reserved(
            dict(
                _obj_key=self.r_obj_key(),
                _flags=self.r_flags(),
                _alerts=self.r_alert_objects(),
                _project_obj=self.r_project_obj(),
                _pchid=self.r_pchid(),
                _switch_id=self.r_switch_id(),
                _link_addr=self.r_link_addresses()
            ),
            k
        )

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

    def s_add_path(self, link_addr, cu_num, cu_type):
        """Adds a channel path (link address & control unit) to the CHPID

        :param link_addr: Link address to add (upper 2-bytes of the FC address in hex)
        :type link_addr: str
        :param cu_num: Control unit number (CUNUMBER= in CNTLUNIT macro)
        :type cu_num: str
        :param cu_type: Control unit type
        :type cu_type: str
        """
        link_addr_d = self._link_addr.get(link_addr)
        if link_addr_d is None:
            link_addr_d = dict()
            self._link_addr.update({link_addr: link_addr_d})
        if cu_num not in link_addr_d:
            link_addr_d.update({cu_num: cu_type})

    def r_link_addr(self, link_addr):
        """Returns the link address dictionary associated with the CHPID and specified link address, link_addr

        :param link_addr: Link address in hex
        :type link_addr: str
        :return: Link address dictionary.
        :rtype: dict, None
        """
        return self._link_addr.get(link_addr)

    def r_link_addresses(self):
        """Returns all the link addresses associated with the CHPID

        :return: List of link addresses. Each element is a hex str. Does not include leading '0x'
        :rtype: list
        """
        return [str(key) for key in self._link_addr.keys()]

    def r_link_addresses_d(self):
        """Returns the link address dictionary associated with the CHPID

        :return: Link address dictionary
        :rtype: dict
        """
        return [str(key) for key in self._link_addr.keys()]

    def r_pchid(self):
        """Returns the physical channel ID

        :return: PCHID
        :rtype: str
        """
        return self._pchid

    def r_switch_id(self):
        """Returns the Switch ID

        :return: Switch ID
        :rtype: str
        """
        return self._switch_id

    def s_switch_id(self, switch_id):
        """Sets the Switch ID. Note that this is useful when mapping switch IDs to actual DIDs

        :return: Switch ID
        :rtype: str
        """
        self._switch_id = switch_id

    def r_lpars(self):
        """Returns the list of LPARs using this CHPID

        :return: PCHID
        :rtype: str
        """
        return self._members

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
