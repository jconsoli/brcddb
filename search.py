# Copyright 2020, 2021, 2022 Jack Consoli.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apahche License, Version 2.0 (the "License");
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
:mod:`brcddb.util.search` - Contains search and threshold compare methods.

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | test_threshold        | Filters a list of objects based on a number (int or float) and test condition         |
    +-----------------------+---------------------------------------------------------------------------------------+
    | match                 | Performs a regex match/search or wild card search in dict or brcddb class object(s).  |
    |                       | If search_key is a list of more than one, OR logic applies. Performs an iteritive     |
    |                       | search on any list, tuple, dict, or brcddb object found after the last search key. If |
    |                       | a list is encountered, an iteritive search is performed on the list. If the search    |
    |                       | keys have not been exhausted, then the remaining search keys are applied to the       |
    |                       | iteritive searches.                                                                   |
    +-----------------------+---------------------------------------------------------------------------------------+
    | match_test            | Performs a pre-defined complex test using match() and test_threshold. Any key         |
    |                       | collected from the API and put into an object can be evaluated for an exact match,    |
    |                       | a regex match, a regex search, and wild card match on str value types. Numbers can    |
    |                       | use comparitive operators >, <, >=, <=, !=, and ==. Types bool can only be evaluated  |
    |                       | for True or False.                                                                     |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-4   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 17 Jul 2021   | Fixed match_test() to accept a dict instead of list. Fixed ignore_case in match().|
    |           |               | Added common search terms.                                                        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 14 Aug 2021   | Added common search terms.                                                        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 28 Apr 2022   | Updated documentation                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 22 Jun 2022   | Removed duplicates in logical OR test.                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022 Jack Consoli'
__date__ = '22 Jun 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.8'

import re
import fnmatch
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcddb.util.util as brcddb_util
import brcddb.brcddb_common as brcddb_common

# Common search terms
disabled_ports = dict(k='fibrechannel/is-enabled-state', t='bool', v=False)
enabled_ports = dict(k='fibrechannel/is-enabled-state', t='bool', v=True)
f_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_F)
e_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_E)
target = dict(k='brocade-name-server/fc4-features', v='FCP-Target', t='exact', i=False)
initiator = dict(k='brocade-name-server/fc4-features', v='FCP-Initiator', t='exact', i=False)
port_online = dict(k='fibrechannel/operational-status', t='==', v=2)
port_offline = dict(k='fibrechannel/operational-status', t='==', v=3)
# Reminder: The login speed is only valid if the port is online. Use the port_online filter in conjunction with these:
login_1G = dict(k='fibrechannel/speed', t='==', v=1000000000)  # 1G
login_2G = dict(k='fibrechannel/speed', t='==', v=2000000000)  # 2G
login_4G = dict(k='fibrechannel/speed', t='==', v=4000000000)  # 4G
login_8G = dict(k='fibrechannel/speed', t='==', v=8000000000)  # 8G
login_16G = dict(k='fibrechannel/speed', t='==', v=16000000000)  # 16G
login_32G = dict(k='fibrechannel/speed', t='==', v=32000000000)  # 32G
login_64G = dict(k='fibrechannel/speed', t='==', v=64000000000)  # 64G


# The case statements for numerical_test_case used in test_threshold()
def _test_greater(v1, v2):
    return True if v1 > v2 else False


def _test_less(v1, v2):
    return True if v1 < v2 else False


def _test_equal(v1, v2):
    return True if v1 == v2 else False


def _test_greater_equal(v1, v2):
    return True if v1 >= v2 else False


def _test_lss_equal(v1, v2):
    return True if v1 <= v2 else False


def _test_not_equal(v1, v2):
    return True if v1 != v2 else False


numerical_test_case = {
    '>': _test_greater,
    '<': _test_less,
    '=': _test_equal,
    '==': _test_equal,
    '>=': _test_greater_equal,
    '<=': _test_lss_equal,
    '!=': _test_not_equal,
}


def test_threshold(obj_list, key, test, val):
    """Filters a list of objects based on a number (int or float) and test condition

    :param obj_list: list of brcddb classes - see brcddb.class
    :type obj_list: list
    :param key: Key for the value to be compared. To look in a substr, seperate keys with a '/'. All keys must be a \
        key to a dict or brcddb object
    :type key: str, list, tuple
    :param test: Test condition: '>', '<', '==', '=', '>=', '<=', '!=', '!', 'not'
    :param val: Value to test counter against
    :type val: int
    :return: List of objects from obj_list that meet the filter criteria in the same order as obj_list
    :rtype: list
    """
    return_list = list()

    #  Validate the inputs
    msg = list()
    if not isinstance(obj_list, (list, tuple)):
        msg.append('\nobj_list is type ' + str(type(obj_list)) + '. It must be a list or typle of brcddb objects')
    if not isinstance(key, str):
        msg.append('\nkey is type ' + str(type(key)) + '. It must be a type str')
    if isinstance(test, str):
        if test not in numerical_test_case:
            msg.append('\nUnkown "test": ' + test)
    else:
        msg.append('\n"test" must be str. Actual type is ' + str(type(test)))
    if not isinstance(val, (int, float, str)):
        msg.append('\nval is type ' + str(type(val)) + '. It must be an int, float, or reference (str)')
    if len(msg) > 0:
        brcdapi_log.exception('\nInvalid parameter passed to test_threshold\n' + '\n'.join(msg) + '\n', True)
        return None

    # Now do the test
    for obj in obj_list:
        v = brcddb_util.get_key_val(obj, key)
        c_val = val if isinstance(val, (int, float)) else brcddb_util.get_key_val(obj, val)
        if isinstance(v, (int, float)) and isinstance(c_val, (int, float)) and numerical_test_case[test](v, c_val):
            return_list.append(obj)

    return return_list

def match(search_objects, search_key, in_search_term, ignore_case=False, stype='exact'):
    """Performs a regex match/search or wild card search in dict or brcddb class object(s). If search_key is a list of
       more than one, OR logic applies. Performs an iteritive search on any list, tuple, dict, or brcddb object found
       after the last search key. If a list is encountered, an iteritive search is performed on the list. If the search
       keys have not been exhausted, then the remaining search keys are applied to the iteritive searches.

        **WARNING:** Circular references will result in Python stack overflow issues. Since all brcddb objects have a
        link back to the main project object, at least one key must be used to avoid this circular reference

    :param search_objects: Required. These are the objects to search in. Usually a list
    :type search_objects: str, tuple, list, dict or any brcddb object
    :param search_key: Required. The key, or list of keys, in the objects in search_objects to match against. OR logic
    :type search_key: str, list, tuple
    :param in_search_term: Required. This is what to look for.
    :type in_search_term: str, list, tuple, bool
    :param ignore_case: Default is False. If True, ignores case in search_term. Not that keys are always case sensitive
    :type ignore_case: bool
    :param stype: Valid options are: 'exact', 'wild', 'regex-m', or 'regex-s' ('-m' for match and -s for search)
    :param stype: str
    :return return_list:  List of matching the search criteria - subset of search_objects
    :rtype: list
    """

    # Summary of wild card strings (search the web for 'python fnmatch.fnmatch' for additional informaiton):
    # *         matches everything
    # ?         matches any single character
    # [seq]     matches any character in seq
    # [!seq]    matches any character not in seq

    # Summary of ReGex strings (search the web for 'regex' for additional information:
    # abc…          Letters
    # 123…          Digits
    # \d            Any Digit
    # \D            Any Non - digit character
    # .             Any Character
    # \.            Period
    # [abc]         Only a, b, or c
    # [ ^ abc]      Not a, b, nor c
    # [a - z]       Characters a to z
    # [0 - 9]       Numbers 0 to 9
    # \w            Any Alphanumeric character
    # \W            Any Non - alphanumeric character
    # {m}           m Repetitions
    # {m, n}        m to n Repetitions
    # *             Zero or more repetitions
    # +             One or more repetitions
    # ?             Optional character
    # \s            Any Whitespace
    # \S            Any Non - whitespace character
    # ^ …$          Starts and ends
    # (…)           Capture Group
    # (a(bc))       Capture Sub - group
    # (.*)          Capture all
    # (abc | def )  Matches abc or def

    # Programmers tip: The Python re and fmatch are quite effecient. In order to search for anything in any data
    # structure, this method does not make use of list comprehensions. If you need something more effecient, create
    # a seperate method for a more specific purpose and leave this as a general purpose search and match method.

    return_list = list()
    search_term = in_search_term.lower() if ignore_case else in_search_term

    # Validate user input
    if not isinstance(search_term, (str, list, tuple, bool)):
        brcdapi_log.exception('Invalid search_term type: ' + str(type(search_term)), True)
        return return_list
    if isinstance(stype, str):
        if stype in ('regex-m', 'regex-s'):
            regex_obj = re.compile(search_term, re.IGNORECASE) if ignore_case else re.compile(search_term)
        elif stype not in ('wild', 'exact', 'bool'):
            brcdapi_log.exception('Invalid search type: ' + stype, True)
            return return_list
    else:
        brcdapi_log.exception('Search type must be str. Search type is: ' + str(type(stype)),
                              True)
        return return_list

    search_key_list = brcddb_util.convert_to_list(search_key)
    obj_list = brcddb_util.convert_to_list(search_objects)
    for obj in obj_list:
        for sk in search_key_list:
            sub_obj = brcddb_util.get_key_val(obj, sk)
            if sub_obj is not None:
                if isinstance(sub_obj, dict):
                    if len(match(sub_obj, list(sub_obj.keys()), search_term, ignore_case, stype)) > 0:
                        return_list.append(obj)
                elif isinstance(sub_obj, (str, list, tuple)):
                    for buf in brcddb_util.convert_to_list(sub_obj):  # Any match within that list is a match
                        if isinstance(buf, str):
                            test_buf = buf.lower() if ignore_case else buf
                            if stype == 'regex-m':
                                if regex_obj.match(test_buf):
                                    return_list.append(obj)
                                    break
                            elif stype == 'regex-s':
                                if regex_obj.search(test_buf):
                                    return_list.append(obj)
                                    break
                            elif stype == 'exact':
                                if search_term == test_buf:
                                    return_list.append(obj)
                                    break
                            elif stype == 'wild':
                                if fnmatch.fnmatch(test_buf, search_term):
                                    return_list.append(obj)
                                    break
                            elif stype == 'bool':
                                if isinstance(buf, bool) and isinstance(search_term, bool):
                                    if bool({search_term: buf}):
                                        return_list.append(obj)
                                        break
                        elif isinstance(buf, dict):
                            if len(match([buf.get(k) for k in buf], None, search_term, ignore_case, stype)) > 0:
                                return_list.append(obj)
                                break
                        elif isinstance(buf, (list, tuple)):
                            if len(match(buf, None, search_term, ignore_case, stype)) > 0:
                                return_list.append(obj)
                                break
                elif isinstance(sub_obj, bool):
                    if (search_term and sub_obj) or (not search_term and not sub_obj):
                        return_list.append(obj)
                        break

    if len(return_list) > 0 and 'brcddb' in str(type(return_list[0])):
        return brcddb_util.remove_duplicates(return_list)
    else:
        return return_list


def match_test(obj_list, test_obj, logic=None):
    """Performs a pre-defined complex test using match() and test_threshold.
    Any key collected from the API and put into an object can be evaluated for an exact match, a regex match, a regex
    search, and wild card match on str value types. Numbers can use comparitive operators >, <, >=, <=, !=, and ==.
    Types bool can only be evaluated for True or False.

    :param obj_list: A list of dictionaries or brcddb objects to search
    :type obj_list: dict, list, tuple
    :param test_obj: Pre-defined test. See comments below.
    :type test_obj: dict, list, tuple
    :param logic: Logic to apply to items in 'l'. May be 'and', 'or', 'nand', or 'nor'. If None, default is 'and'
    :type logic: str or None
    :return: Subset of obj_list whose objects meet the test criteria
    :rtype: list
    """
    # test_obj (pre-defined test) dict or list/tuple of dict that defines the logical tests to perform:
    #
    # 'skip'    Optional. Bool. Default is False. If True, effectively comments out the test case.
    #
    # 'l'       Optional. Same as test_obj. When specified, iteratively calls match_test(). This is useful for complex
    #           matches. You can nest these as deep as Python allows which is much deeper than any useful search you can
    #           dream of.
    #
    # 'k'       Required. str. This is the key for the value in the object from the obj_list to test for the match to
    #           what is specifed in 'v'
    #
    # 'v'       Required if 's' not specified. (str, int, float, bool). This is the value to compare against. The value
    #           type must be consistent with the type of value associated with obj.get('k').
    #
    # 's'       Optional. str. NOT YET IMPLEMENTED. Same as 'v' except this is a referenced value. The most common use
    #           is to compare against MAPS policies. Only 'v' or 's' is compared. If both are present, 's' is ignored.
    #
    # 't'       Required. str. This is the type of comparison (test) to make. Comparison types may be:
    #               int types: '>', '<', '<=', '>=', '!=', '==', and, for sloppy programmers, '='.
    #               str types:  'exact'     exact match
    #                           'wild'      Uses Pythons standard fnmatch library for wild card matching.
    #                           'regex-m'   Uses Pythons standard re library (re) for regex matching
    #                           'regex-s'   Uses Pythons standard re library (re) for regex searching
    #                           'bool'      True/False test
    # 'i'       Optional. Bool. Only relevant to str matching. Possible values are:
    #               True - ignore case.
    #               False - Default. match case.
    #
    # 'logic'   Optionial. Logic to apply to items in 'l'. Although the logic is moot for single items in 'l', 'and' is
    #           the most effecient to process the logic. Defined as follows:
    #           'and'   Default. All tests specified in 'l' must evaluate True
    #           'or'    Any test specified in 'l' must evaluate True
    #           'nand'  Opposite of 'and'.
    #           'nor'   Opposfite of 'or'

    w_list = list() if obj_list is None else [obj_list] if not isinstance(obj_list, (list, tuple)) else obj_list
    lg = 'and' if logic is None else logic
    t_list = brcddb_util.convert_to_list(test_obj)  # This is the list of objects to test against
    o_list = list()  # This is the NAND and OR list when 'nand' or 'or' logic is specified

    for t_obj in t_list:
        m_list = list()
        if len(w_list) == 0:
            break
        if 'l' in t_obj:
            m_list = match_test(w_list, t_obj.get('l'), t_obj.get('logic'))
        if 'k' in t_obj and 't' in t_obj and 'v' in t_obj:
            ic = False if t_obj.get('i') is None else t_obj.get('i')

            # Perform the test and put results in m_list
            if t_obj['t'] in ('bool', 'wild', 'regex-m', 'regex-s', 'exact'):
                m_list = match(w_list, t_obj['k'], t_obj['v'], ic, t_obj['t'])
            elif t_obj['t'] in ('>', '<', '<=', '>=', '==', '=', '!='):
                m_list = test_threshold(w_list, t_obj['k'], t_obj['t'], t_obj['v'])
            else:
                brcdapi_log.exception('Invalid search key, ' + t_obj['t'], True)
                return list()

        # Apply the test logic
        if lg == 'and':
            # All tests must evaluate True so modify w_list to only contain objects for tests that evaluated True
            w_list = m_list
        elif lg == 'nand':
            w_list = [obj for obj in w_list if obj not in m_list]
        elif lg == 'or':
            # Any test that evaluates True means the object should be included in the return list and there is no
            # point in performing additional tests so remove it from w_list.
            o_list.extend(m_list)
        elif lg == 'nor':
            # All tests must evaluate False so remove any test that evaluates True from w_list.
            w_list = [obj for obj in w_list if obj not in m_list]
        else:
            brcdapi_log.exception('Invalid logic, ' + lg, True)
            return list()

    if lg == 'or':
        # w_list = o_list
        w_list = gen_util.remove_duplicates(o_list)

    return list(w_list)
