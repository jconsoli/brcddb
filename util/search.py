"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

:mod:`brcddb.util.search` - Contains search and threshold compare methods.

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | test_threshold        | Filters a list of objects based on a number (int or float) and test condition         |
    +-----------------------+---------------------------------------------------------------------------------------+
    | match                 | Performs a regex match/search or wild card search in dict or brcddb class object(s).  |
    |                       | If search_key is a list of more than one, OR logic applies. Performs an iterative     |
    |                       | search on any list, tuple, dict, or brcddb object found after the last search key. If |
    |                       | a list is encountered, an iterative search is performed on the list. If the search    |
    |                       | keys have not been exhausted, then the remaining search keys are applied to the       |
    |                       | iterative searches.                                                                   |
    +-----------------------+---------------------------------------------------------------------------------------+
    | match_test            | Performs a pre-defined complex test using match() and test_threshold. Any key         |
    |                       | collected from the API and put into an object can be evaluated for an exact match,    |
    |                       | a regex match, a regex search, and wild card match on str value types. Numbers can    |
    |                       | use comparative operators >, <, >=, <=, !=, and ==. Types bool can only be evaluated  |
    |                       | for True or False.                                                                     |
    +-----------------------+---------------------------------------------------------------------------------------+

**Summary of wild card strings**

Search the web for 'python fnmatch.fnmatch' for additional information

*         matches everything
?         matches any single character
[seq]     matches any character in seq
[!seq]    matches any character not in seq

**Summary of ReGex strings**

Search the web for 'regex' for additional information. A regex match must match the beginning of the string. A regex
search must match any instance of the regex in the string.

abc…          Letters
123…          Digits
\d            Any Digit
\D            Any Non - digit character
.             Any Character
\.            Period
[abc]         Only a, b, or c
[ ^ abc]      Not a, b, nor c
[a - z]       Characters a to z
[0 - 9]       Numbers 0 to 9
\w            Any Alphanumeric character
\W            Any Non - alphanumeric character
{m}           m Repetitions
{m, n}        m to n Repetitions
*             Zero or more repetitions
+             One or more repetitions
?             Optional character
\s            Any Whitespace
\S            Any Non - whitespace character
^ …$          Starts and ends
(…)           Capture Group
(a(bc))       Capture Sub - group
(.*)          Capture all
(abc | def )  Matches abc or def

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 03 Apr 2024   | Fixed bug in match() whereby multiple search terms were not processed properly        |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 15 May 2024   | Fixed ignore case with wild card matching.                                            |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 16 Jun 2024   | Fixed bad reference, raise found. Should have been "raise Found"                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 20 Oct 2024   | PEP 8 corrections to login speeds in brcddb.util.search.login_xxx                     |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '20 Oct 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.5'

import re
import fnmatch
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common

# Common search terms
disabled_ports = dict(k='fibrechannel/is-enabled-state', t='bool', v=False)
enabled_ports = dict(k='fibrechannel/is-enabled-state', t='bool', v=True)
f_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_F)
e_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_E)
non_icl_ports = dict(k='fibrechannel/port-type', t='!=', v=brcddb_common.PORT_TYPE_ICL)
icl_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_ICL)
fc_lag_ports = dict(k='fibrechannel/port-type', t='==', v=brcddb_common.PORT_TYPE_FC_LAG)
target = dict(k='brocade-name-server/fibrechannel-name-server/fc4-features', v='FCP-Target', t='exact', i=False)
initiator = dict(k='brocade-name-server/fibrechannel-name-server/fc4-features', v='FCP-Initiator', t='exact', i=False)
port_online = dict(k='fibrechannel/operational-status', t='==', v=2)
port_offline = dict(k='fibrechannel/operational-status', t='==', v=3)
# Reminder: The login speed is only valid if the port is online. Use the port_online filter in conjunction with these:
login_1g = dict(k='fibrechannel/speed', t='==', v=1000000000)  # 1G
login_2g = dict(k='fibrechannel/speed', t='==', v=2000000000)  # 2G
login_4g = dict(k='fibrechannel/speed', t='==', v=4000000000)  # 4G
login_8g = dict(k='fibrechannel/speed', t='==', v=8000000000)  # 8G
login_16g = dict(k='fibrechannel/speed', t='==', v=16000000000)  # 16G
login_32g = dict(k='fibrechannel/speed', t='==', v=32000000000)  # 32G
login_64g = dict(k='fibrechannel/speed', t='==', v=64000000000)  # 64G
login_128g = dict(k='fibrechannel/speed', t='==', v=128000000000)  # 128G

_regex_m_type_d = {'regexm': True, 'regex_m': True, 'regex-m': True}
_regex_s_type_d = {'regexs': True, 'regex_s': True, 'regex-s': True}
_valid_stype = dict(exact=True, wild=True, bool=True)
_valid_stype.update(_regex_m_type_d)
_valid_stype.update(_regex_s_type_d)


class Found(Exception):
    pass


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
    :param key: Key for the value to be compared. To look in a substr, separate keys with a '/'. All keys must be a \
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
        msg.append('\nobj_list is type ' + str(type(obj_list)) + '. It must be a list or tuple of brcddb objects')
    if not isinstance(key, str):
        msg.append('\nkey is type ' + str(type(key)) + '. It must be a type str')
    if isinstance(test, str):
        if test not in numerical_test_case:
            msg.append('\nUnknown "test": ' + test)
    else:
        msg.append('\n"test" must be str. Actual type is ' + str(type(test)))
    if not isinstance(val, (int, float, str)):
        msg.append('\nval is type ' + str(type(val)) + '. It must be an int, float, or reference (str)')
    if len(msg) > 0:
        brcdapi_log.exception('\nInvalid parameter passed to test_threshold\n' + '\n'.join(msg) + '\n', echo=True)
        return None

    # Now do the test
    for obj in obj_list:
        v = gen_util.get_key_val(obj, key)
        c_val = val if isinstance(val, (int, float)) else gen_util.get_key_val(obj, val)
        if isinstance(v, (int, float)) and isinstance(c_val, (int, float)) and numerical_test_case[test](v, c_val):
            return_list.append(obj)

    return return_list


def match(search_objects, search_key, in_search_term, ignore_case=False, stype='exact'):
    """Performs a regex match/search or wild card search in dict or brcddb class object(s). If search_key is a list of
       more than one, OR logic applies. Performs an iterative search on any list, tuple, dict, or brcddb object found
       after the last search key. If a list is encountered, an iterative search is performed on the list. If the search
       keys have not been exhausted, then the remaining search keys are applied to the iterative searches.

    **WARNING:**
    Circular references will result in Python stack overflow issues. Since all brcddb objects have a link back to the
    main project object, at least one key must be used to avoid this circular reference

    **Programmers Tip**
    The Python re and fmatch are quite efficient. In order to search for anything in any data structure, this method
    does not make use of list comprehensions. If you need something more efficient, create a separate method for a more
    specific purpose and leave this as a general purpose search and match method.

    :param search_objects: Required. These are the objects to search in. Usually a list
    :type search_objects: str, tuple, list, dict or any brcddb object
    :param search_key: Required. The key, or list of keys, in the objects in search_objects to match against. OR logic
    :type search_key: str, list, tuple
    :param in_search_term: Required. This is what to look for.
    :type in_search_term: str, list, tuple, bool
    :param ignore_case: Default is False. If True, ignores case in search_term. Not that keys are always case-sensitive
    :type ignore_case: bool
    :param stype: See _valid_stype
    :param stype: str
    :return return_list: List of matching the search criteria - subset of search_objects
    :rtype: list
    """
    global _valid_stype, _regex_m_type_d, _regex_s_type_d

    return_list = list()
    for search_term in gen_util.convert_to_list(in_search_term):

        # Validate user input
        if not isinstance(search_term, (str, bool)):
            brcdapi_log.exception('Invalid search_term type: ' + str(type(search_term)), echo=True)
            return return_list
        if isinstance(stype, str):
            if _regex_m_type_d.get(stype, False) or _regex_s_type_d.get(stype, False):
                regex_obj = re.compile(search_term, re.IGNORECASE) if ignore_case else re.compile(search_term)
            elif not _valid_stype.get(stype, False):
                brcdapi_log.exception('Invalid search type: ' + stype, echo=True)
                return return_list
        else:
            brcdapi_log.exception('Search type must be str. Search type is: ' + str(type(stype)),
                                  True)
            return return_list

        # Input was validated, so find the matches
        search_key_list = gen_util.convert_to_list(search_key)
        for obj in gen_util.convert_to_list(search_objects):
            try:
                for sk in search_key_list:
                    sub_obj = gen_util.get_key_val(obj, sk)
                    if sub_obj is None:
                        continue
                    if isinstance(sub_obj, dict):
                        if len(match(sub_obj, list(sub_obj.keys()), search_term, ignore_case, stype)) > 0:
                            raise Found
                    elif isinstance(sub_obj, (str, list, tuple)):
                        for buf in gen_util.convert_to_list(sub_obj):  # Any match within that list is a match
                            if isinstance(buf, str):
                                test_buf = buf.lower() if ignore_case else buf
                                if _regex_m_type_d.get(stype, False):
                                    if regex_obj.match(test_buf):
                                        raise Found
                                elif _regex_s_type_d.get(stype, False):
                                    if regex_obj.search(test_buf):
                                        raise Found
                                elif stype == 'exact':
                                    if ignore_case and search_term.lower() == test_buf.lower():
                                        raise Found
                                    elif search_term == test_buf:
                                        raise Found
                                elif stype == 'wild':
                                    if ignore_case and fnmatch.fnmatch(test_buf, search_term):
                                        raise Found
                                    elif fnmatch.fnmatchcase(test_buf, search_term):
                                        raise Found
                                elif stype == 'bool':
                                    if isinstance(buf, bool) and isinstance(search_term, bool):
                                        if bool({search_term: buf}):
                                            raise Found
                            elif isinstance(buf, dict):
                                if len(match([buf.get(k) for k in buf], None, search_term, ignore_case, stype)) > 0:
                                    raise Found
                            elif isinstance(buf, (list, tuple)):
                                if len(match(buf, None, search_term, ignore_case, stype)) > 0:
                                    raise Found
                    elif isinstance(sub_obj, bool):
                        if (search_term and sub_obj) or (not search_term and not sub_obj):
                            raise Found
            except Found:
                return_list.append(obj)

    if len(return_list) > 0 and 'brcddb' in str(type(return_list[0])):
        return gen_util.remove_duplicates(return_list)
    else:
        return return_list


def match_test(obj_list, test_obj, logic=None):
    """Performs a pre-defined complex test using match() and test_threshold.
    Any key collected from the API and put into an object can be evaluated for an exact match, a regex match, a regex
    search, and wild card match on str value types. Numbers can use comparative operators >, <, >=, <=, !=, and ==.
    Types bool can only be evaluated for True or False.

    test_obj (pre-defined test) dict or list/tuple of dict that defines the logical tests to perform:

    'skip'    Optional. Bool. Default is False. If True, effectively comments out the test case.

    'l'       Optional. Same as test_obj. When specified, iteratively calls match_test(). This is useful for complex
              matches. You can nest these as deep as Python allows which is much deeper than any useful search you can
              dream of.

    'k'       Required. str. This is the key for the value in the object from the obj_list to test for the match to
              what is specifed in 'v'

    'v'       Required if 's' not specified. (str, int, float, bool). This is the value to compare against. The value
              type must be consistent with the type of value associated with obj.get('k').

    's'       Optional. str. NOT YET IMPLEMENTED. Same as 'v' except this is a referenced value. The most common use
              is to compare against MAPS policies. Only 'v' or 's' is compared. If both are present, 's' is ignored.

    't'       Required. str. This is the type of comparison (test) to make. Comparison types may be:
                  int types: '>', '<', '<=', '>=', '!=', '==', and, for sloppy programmers, '='.
                  str types:  'exact'     exact match
                              'wild'      Uses Pythons standard fnmatch library for wild card matching.
                              'regexm'    Uses Pythons standard re library (re) for regex matching
                              'regex_m'   Same as regexm
                              'regex-m'   Same as regexm
                              'regexs'    Uses Pythons standard re library (re) for regex searching
                              'regex-s'   Same as regexs
                              'regex_s'   Same as regexs
                              'bool'      True/False test
    'i'       Optional. Bool. Only relevant to str matching. Possible values are:
                  True - ignore case.
                  False - Default. match case.

    'logic'   Optional. Logic to apply to items in 'l'. Although the logic is moot for single items in 'l', 'and' is
              the most efficient to process the logic. Defined as follows:
              'and'   Default. All tests specified in 'l' must evaluate True
              'or'    Any test specified in 'l' must evaluate True
              'nand'  Opposite of 'and'.
              'nor'   Opposite of 'or'

    :param obj_list: A list of dictionaries or brcddb objects to search
    :type obj_list: dict, list, tuple
    :param test_obj: Pre-defined test. See comments below.
    :type test_obj: dict, list, tuple
    :param logic: Logic to apply to items in 'l'. May be 'and', 'or', 'nand', or 'nor'. If None, default is 'and'
    :type logic: str or None
    :return: Subset of obj_list whose objects meet the test criteria
    :rtype: list
    """
    global _valid_stype

    w_list = list() if obj_list is None else [obj_list] if not isinstance(obj_list, (list, tuple)) else obj_list
    lg = 'and' if logic is None else logic
    t_list = gen_util.convert_to_list(test_obj)  # This is the list of objects to test against
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
            if _valid_stype.get(t_obj['t'], False):
                m_list = match(w_list, t_obj['k'], t_obj['v'], ic, t_obj['t'])
            elif t_obj['t'] in ('>', '<', '<=', '>=', '==', '=', '!='):
                m_list = test_threshold(w_list, t_obj['k'], t_obj['t'], t_obj['v'])
            else:
                brcdapi_log.exception('Invalid search key, ' + t_obj['t'], echo=True)
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
            brcdapi_log.exception('Invalid logic, ' + lg, echo=True)
            return list()

    if lg == 'or':
        w_list = gen_util.remove_duplicates(o_list)

    return list(w_list)
