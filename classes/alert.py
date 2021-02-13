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
:mod:`brcddb.classes.alert` - Establishes a common frame work for processing post data collection analysis.

    Alerts are not copied in brcddb.util.brcddb_to_plain_copy() and therefore not saved.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '13 Feb 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

import copy
import brcddb.brcddb_common as brcddb_common

class ALERT_SEV:
    """
    Alert severity levels.

    Tyipically used for determining how to display alerts. See report.py for an example. Test using methods is_error() \
    and is_warn(). Raw code is returned with sev().

    Note: This was origionally more complex, hence it being in a class. After I sipmlified it, I didn't want to change
    all the code that was using the alert levels out of this class.
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
    | anum |  'm'  | Alert message. When formated with self.fmt_msg(), $k is replaced with the value for 'k', $p0 is   |
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
    |      | other | It may be convienent for applications to add other keys, but they are ignored by the methods in   |
    |      |       | this class                                                                                        |
    +------+-------+---------------------------------------------------------------------------------------------------+

    :param msg_tbl: Pointer to the table described above
    :type msg_tbl: dict
    :param anum: User defined alert numnber
    :type anum: int
    :param key: Optional. Object key value associated with the alert
    :type key: str, None
    :param p0: Optional. $p0 in the msg attribute is converted to this parameter
    :type p0: str, int, float, None
    :param p1: Similar to p0
    :type p1: str, int, float, None
    :param flag: Optional. Alert specific
    :type flag: bool
    """

    def __init__(self, msg_tbl, anum, key=None, p0=None, p1=None):

        self._msg_tbl = msg_tbl
        self._alert_num = anum
        self._key = key
        self._p0 = p0
        self._p1 = p1

    def r_get_reserved(self, k):
        """Returns a value for any reserved key

        :param k: Reserved key
        :type k: str
        :return: Value associated with k. None if k is not present
        :rtype: *
        """
        _reserved_keys = {
            '_msg_tbl': self.msg_tbl(),
            '_key': self.key(),
            '_p0': self.p0(),
            '_p1': self.p1(),
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

    def alert_num(self):
        """
        :return: Alert numnber
        :rtype int:
        """
        return self._alert_num

    def msg_tbl(self):
        """
        :return: Message tbale pointer
        :rtype str:
        """
        return self._msg_tbl

    def fmt_msg(self):
        """
        :return: Formatted message
        :rtype str:
        """
        msg = copy.copy(self._msg_tbl.get(self.alert_num()).get('m'))
        if self._key is None:
            msg = msg.replace('$key', '')
        else:
            msg = msg.replace('$key', str(self._key))
        if self._p0 is None:
            msg = msg.replace('$p0', '')
        else:
            msg = msg.replace('$p0', str(self._p0))
        if self._p1 is None:
            msg = msg.replace('$p1', '')
        else:
            msg = msg.replace('$p1', str(self._p1))
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
        :rtype bool:
        """
        return bool(self._msg_tbl.get(self.alert_num()).get('s') == ALERT_SEV.ERROR)

    def is_warn(self):
        """
        :return: True if severity level is ALERT_SEV.WARN
        :rtype bool:
        """
        return bool(self._msg_tbl.get(self.alert_num()).get('s') == ALERT_SEV.WARN)

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
        if 'f' in self._msg_tbl.get(self.alert_num()):
            return self._msg_tbl.get(self.alert_num()).get('f')
        else:
            return False

