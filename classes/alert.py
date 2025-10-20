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

Establishes a common framework for processing post data collection analysis.

Alerts are not copied in brcddb.util.brcddb_to_plain_copy() and therefore not saved.

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 26 Dec 2024   | Fixed error condition when checking for error level with invalid errors.              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025 Consoli Solutions, LLC'
__date__ = '19 Oct 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.4'

import copy
import brcddb.classes.util as class_util

import brcdapi.log as brcdapi_log


class ALERT_SEV:
    """
    Alert severity levels.

    Topically used for determining how to display alerts. See report.py for an example. Test using methods is_error() \
    and is_warn(). Raw code is returned with sev().

    Note: This was originally more complex, hence it being in a class. After I simplified it, I didn't want to change
    all the code that was using the alert levels out of this class. As to why I didn't make it camel case, as is
    appropriate for a class name, I have no idea what I was thinking when I did it.
    """
    GENERAL = 0
    WARN = 1
    ERROR = 2


_sev_to_text = {
    ALERT_SEV.GENERAL: 'General',
    ALERT_SEV.WARN: 'Warn',
    ALERT_SEV.ERROR: 'Error',
}


class AlertObj:
    """Lightweight object for alerts and comments associated with brcddb.classes.

    Alerts are referenced from a user defined dictionary of dictionaries in msg_tbl as follows

    +------+------+----------------------------------------------------------------------------------------------------+
    |  k0  |  k1  | val                                                                                                |
    +======+=======+===================================================================================================+
    | anum |  'm'  | Alert message. When formatted with self.fmt_msg(), $k is replaced with the value for 'k', $p0 is  |
    |      |       | replaced with the value for 'p0', and $p1 is replaced with the value for 'p1'                     |
    +      +-------+---------------------------------------------------------------------------------------------------+
    |      |  's'  | Severity level defined by ALERT_SEV.                                                              |
    +      +-------+---------------------------------------------------------------------------------------------------+
    |      |  'f'  | Optional. Alert specific flag.                                                                    |
    +      +-------+---------------------------------------------------------------------------------------------------+
    |      |  'p0' | Optional. Typically filled in by the method generating the alert                                  |
    +      +-------+---------------------------------------------------------------------------------------------------+
    |      |  'p1' | Optional. Typically filled in by the method generating the alert                                  |
    +      +-------+---------------------------------------------------------------------------------------------------+
    |      | other | It may be convenient for applications to add other keys, but they are ignored by the methods in   |
    |      |       | this class                                                                                        |
    +------+-------+---------------------------------------------------------------------------------------------------+

    :param msg_tbl: Pointer to the table described above
    :type msg_tbl: dict
    :param anum: User defined alert number
    :type anum: int
    :param key: Optional. Object key value associated with the alert
    :type key: str, None
    :param p0: Optional. $p0 in the msg attribute is converted to this parameter
    :type p0: str, int, float, None
    :param p1: Similar to p0
    :type p1: str, int, float, None
    """

    def __init__(self, msg_tbl, anum, key=None, p0=None, p1=None):
        self._msg_tbl = msg_tbl
        self._alert_num = anum
        self._key = key
        self._p0 = p0
        self._p1 = p1

    def r_get_reserved(self, k):
        """Returns a value for any reserved key. Don't forget to update brcddb.util.copy when adding a new key.

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        return class_util.get_reserved(
            dict(
                _msg_tbl=self.msg_tbl(),
                _key=self.key(),
                _p0=self.p0(),
                _p1=self.p1(),
            ),
            k
        )

    def alert_num(self):
        """
        :return: Alert number
        :rtype int:
        """
        return self._alert_num

    def msg_tbl(self):
        """
        :return: Message table pointer
        :rtype str:
        """
        return self._msg_tbl

    def fmt_msg(self):
        """
        :return: Formatted message
        :rtype str:
        """
        msg = copy.copy(self._msg_tbl.get(self.alert_num()).get('m'))
        msg = msg.replace('$key', '') if self._key is None else msg.replace('$key', str(self._key))
        msg = msg.replace('$p0', '') if self._p0 is None else msg.replace('$p0', str(self._p0))
        msg = msg.replace('$p1', '') if self._p1 is None else msg.replace('$p1', str(self._p1))
        return msg

    def sev(self):
        """
        :return: Severity level
        :rtype int:
        """
        return self._msg_tbl.get(self.alert_num()).get('s')

    def fmt_sev(self):
        """
        :return: Severity level
        :rtype int:
        """
        return _sev_to_text[self.sev()]

    def is_error(self):
        """
        :return: True if severity level is ALERT_SEV.ERROR
        :rtype: bool
        """
        try:
            return True if self._msg_tbl[self.alert_num()]['s'] == ALERT_SEV.ERROR else False
        except (KeyError, IndexError, TypeError):
            pass
        return False

    def is_warn(self):
        """
        :return: True if severity level is ALERT_SEV.WARN
        :rtype bool:
        """
        try:
            return True if self._msg_tbl[self.alert_num()]['s'] == ALERT_SEV.WARN else False
        except (KeyError, IndexError, TypeError):
            pass
        return False

    def key(self):
        """
        :return: Value associated with 'key'
        :rtype (str, None):
        """
        return self._key

    def p0(self):
        """
        :return: Value associated with 'p0'
        :rtype (str, int, float, None):
        """
        return self._p0

    def p1(self):
        """
        :return: Value associated with 'p1'
        :rtype (str, int, float, None):
        """
        return self._p1

    def is_flag(self):
        """
        :return: Value associated with 'f'
        :rtype bool:
        """
        return self._msg_tbl.get(self.alert_num()).get('f') if 'f' in self._msg_tbl.get(self.alert_num()) else False

    def r_format(self, full=False):
        """Returns a list of formatted text for the object. Intended for error reporting.

        :param full: If True, expand (pprint) all data added with obj.s_new_key() pprint.
        :type full: bool
        :return: Value
        :rtype: Same type as used when the key/value pair was added
        """
        return class_util.format_obj(self, full=full)
