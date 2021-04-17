# Copyright 2020, 2021 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.util.compare` - Useful for comparing complex objects

Although primarily developed to support comparing brcddb objects, those objects also contain standard Python data
structures so this module can be used to compare anything.

**Description**

compare(), the only public method in this module, returns a dictionary as noted below.

change_rec = compare(b_obj, c_obj, control_tbl)
  b_obj       Can be any object. This is the base (what you are comparing against)
  c_obj       The compare object.
  control_tbl Controls the comparision. Note that you typically don't want a report cluttered with minor changes. For
              example, if the temperature of an SFP rises by 0.5 degrees, you probably don't care.
              List of dictionaries as follows:
                  'something': {      ReGex sear h string. The search string is built by the dictionary keys
                                      types seperated '/' for each nested level.
                      'skip': flag    If flag is True, skip this test. Assume flag=False if omitted
                      'gt': v         Only report a change if c_obj - b_obj > v. Assume v=0 if omitted
                      'lt': v         Only report a change if b_obj - c_obj > v. Assume v=0 if omitted
                  }

c, change_rec = compare(b_obj, c_obj, control_tbl)

  c           Total number of differences found
  change_rec  A dict as follows:
              {
                  'b':    Base value (numbers are converted to a str, str is left as is, all else is str(type(val))
                  'c':    Compare value (see notes with Base value)
                  'r':    Change. Output depends on type
              }

Important Notes::

    * int & float types are treated as the same type so as to avoid getting a type mismatch. This means 5 and 5.0 are
      considered the same.
    * Base ('b') and compare ('c') values are always converted to a str in the output

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-6   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '17 Apr 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import copy
import re
import brcdapi.log as brcdapi_log
import brcddb.classes.util as class_util

_REMOVED = 'Removed'
_NEW = 'Added'
_CHANGED = 'Changed'
_MISMATCH = 'Different types'
_INVALID_REF = 'Programming error. Invalid reference. Check the log for details.'

_brcddb_control_tables = None


def _update_r_obj(r_obj, d):
    """Utility to update the retrun object

    :param r_obj: Return object
    :type r_obj: dict, list
    :param d: Dictionary or list of dictionaries to add to r_obj
    :type d: dict, list, tuple
    """
    if isinstance(r_obj, list):
        if isinstance(d, (list, tuple)):
            r_obj.extend(d)
        else:
            r_obj.append(d)
    else:
        r_obj.update(d)


def _check_control(ref, control_tbl):
    """Check the reference against the control table

    :param ref: Reference object to look for in the control table
    :type ref: str
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return skip_flag: True if the ref was found in control_tbl and it indicated that the test should be skipped.
    :rtype skip_flag: bool
    :return lt: Less than or equal amount for this ref in control_tbl. 0 if not found
    :rtype lt: int, float
    :return gt: Greater than or equal amount for this ref in control_tbl. 0 if not found
    :rtype gt: int, float
    """
    skip_flag = False
    lt = 0
    gt = 0
    if isinstance(control_tbl, dict):
        for k in control_tbl.keys():
            if re.search(k, ref):
                cd = control_tbl.get(k)
                skip_flag = False if cd.get('skip') is None else cd.get('skip')
                lt = 0 if cd.get('lt') is None else cd.get('lt')
                gt = 0 if cd.get('gt') is None else cd.get('gt')
                break
    return skip_flag, lt, gt


def _str_compare(r_obj, ref, b_str, c_str, control_tbl):
    """Generic string compare

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key.
    :type ref: str
    :param b_str: Base object to compare against.
    :type b_str: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param c_str: Compare object
    :type c_str: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED, _CHANGED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    if c_str is None:
        _update_r_obj(r_obj, {'b': b_str, 'c': '', 'r': _REMOVED})
        return 1
    i_b_str = str(b_str)  # I shouldn't need str(b_str) but just in case I'm over looking something
    i_c_str = str(c_str)
    if i_b_str != i_c_str:
        _update_r_obj(r_obj, {'b': i_b_str, 'c': i_c_str, 'r': _CHANGED})
        return 1
    return 0


def _num_compare(r_obj, ref, b_num, c_num, control_tbl):
    """Generic number compare

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key. Used as the key to the control check (_check_control)
    :type ref: str
    :param b_num: Base hex integer to compare against.
    :type b_num: int, float
    :param c_num: Compare number
    :type c_num: int, float
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    if c_num is None:
        _update_r_obj(r_obj, {'b': str(b_num), 'c': '', 'r': _REMOVED})
        return 1
    if c_num > b_num + gt:
        _update_r_obj(r_obj, {'b': str(b_num), 'c': str(c_num), 'r': '+' + str(c_num - b_num)})
        return 1
    if c_num < b_num - lt:
        _update_r_obj(r_obj, {'b': str(b_num), 'c': str(c_num), 'r': '-' + str(b_num - c_num)})
        return 1
    return 0


def _brcddb_internal_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two brcddb objects

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key. Used as the key to the control check (_check_control)
    :type ref: str
    :param b_obj: Base object to compare against.
    :type b_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param c_obj: Compare object
    :type c_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED

    c = 0

    # Compare all the class objects
    for k in b_obj.r_get_reserved('_reserved_keys'):
        skip_flag, lt, gt = _check_control(ref + '/' + k, control_tbl)
        if not skip_flag:
            b_obj_r = b_obj.r_get_reserved(k)
            new_r_obj = list() if isinstance(b_obj_r, (list, tuple)) else dict()
            x = _compare(new_r_obj, '/' + k, b_obj_r, c_obj.r_get_reserved(k), control_tbl)
            if x > 0:
                r_obj.update({k: copy.deepcopy(new_r_obj)})  # Copy shouldn't be necessary but not changing working code
                c += x

    # Compare all the added objects
    tl = b_obj.r_keys()
    for k in tl:
        new_r_obj = dict()
        x = _compare(new_r_obj, ref + '/' + k, b_obj.r_get(k), c_obj.r_get(k), control_tbl)
        if x > 0:
            r_obj.update({k: copy.deepcopy(new_r_obj)})  # I have no idea why I did a copy here
            c += x

    # Check for removed objects
    for k in c_obj.r_keys():
        if k not in tl:
            r_obj.update({k: {'b': '', 'c': k, 'r': _REMOVED}})
            c += 1

    return c


def _brcddb_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two brcddb objects

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key. Used as the key to the control check (_check_control)
    :type ref: str
    :param b_obj: Base object to compare against.
    :type b_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param c_obj: Compare object
    :type c_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _brcddb_control_tables

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    new_r_obj = dict()
    try:
        ct = _brcddb_control_tables.get(class_util.get_simple_class_type(b_obj))
    except:
        ct = None
    c = _brcddb_internal_compare(new_r_obj, '', b_obj, c_obj, ct)
    if c > 0:
        r_obj.update(copy.deepcopy(new_r_obj))
    return c


def _dict_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare dictionary objects

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key (control_tbl look up).
    :type ref: str
    :param b_obj: Base dict object.
    :type b_obj: dict
    :param c_obj: Compare dict object
    :type c_obj: dict
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED, _NEW, _MISMATCH

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    if not isinstance(c_obj, type(b_obj)):
        _update_r_obj(r_obj, {'b': str(type(b_obj)), 'c': str(type(c_obj)), 'r': _MISMATCH})
        return 1
    c = 0
    for k in b_obj.keys():  # Check existing
        new_ref = ref + '/' + k
        b_obj_r = b_obj.get(k)
        new_r_obj = list() if isinstance(b_obj_r, (list, tuple)) else dict()
        c_obj_r = c_obj.get(k)
        if c_obj_r is None:
            skip_flag_0, lt_0, gt_0 = _check_control(new_ref, control_tbl)
            if not skip_flag_0:
                _update_r_obj(new_r_obj, {'b': k, 'c': '', 'r': _REMOVED})
            x = 1
        else:
            x = _compare(new_r_obj, new_ref, b_obj_r, c_obj_r, control_tbl)
        if x > 0:
            _update_r_obj(r_obj, {k: copy.deepcopy(new_r_obj)})
            c += x
    for k in c_obj.keys():  # Anything added?
        if k not in b_obj:
            skip_flag_0, lt_0, gt_0 = _check_control(ref + '/' + k, control_tbl)
            if not skip_flag_0:
                _update_r_obj(r_obj, {k: {'b': '', 'c': k, 'r': _NEW}})
            c += 1
    return c


def _list_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare list objects

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key (control_tbl look up).
    :type ref: str
    :param b_obj: Base list object.
    :type b_obj: list, tuple
    :param c_obj: Compare list object
    :type c_obj: list, tuple
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED, _NEW, _MISMATCH

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    if not isinstance(c_obj, type(b_obj)):
        _update_r_obj(r_obj, {'b': str(type(b_obj)), 'c': str(type(c_obj)), 'r': _MISMATCH})
        return 1

    # Setup the return values
    change_list = list()
    c = 0

    # If members are all str, it's typically a list of WWNs or zones. We don't care if they are not in the same order.
    # This was shoe horned in long after this module was written. I didn't want to mess with what was already working.
    all_str_flag = True
    obj_list = [b_obj, c_obj]
    compare_obj = obj_list[1]
    for i in range(0, len(obj_list)):
        for buf in obj_list[i]:
            if isinstance(buf, str):
                if buf not in compare_obj:
                    if i == 0:
                        change_list.append({'b': buf, 'c': '', 'r': _REMOVED})
                    else:
                        change_list.append({'b': '', 'c': buf, 'r': _NEW})
                    c += 1
            else:
                all_str_flag = False
                c = 0
                change_list = list()
                break
        compare_obj = obj_list[i]

    if not all_str_flag:
        len_c_obj = len(c_obj)
        len_b_obj = len(b_obj)
        for i in range(0, len_b_obj):
            new_r_obj = dict()
            if i < len_c_obj:
                x = _compare(new_r_obj, ref, b_obj[i], c_obj[i], control_tbl)
            else:
                if isinstance(b_obj[i], (str, int, float)):
                    buf = b_obj[i]
                elif isinstance(b_obj[i], dict):
                    buf = b_obj.get('name') if 'name' in c_obj else ref
                else:
                    buf = ref
                new_r_obj = {'b': buf, 'c': '', 'r': _REMOVED}
                x = 1
            change_list.append(new_r_obj)
            if x > 0:
                c += x

        # Anything new?
        if len_c_obj > len_b_obj:
            for i in range(len_b_obj, len_c_obj):
                if isinstance(c_obj[i], (str, int, float)):
                    buf = c_obj[i]
                elif isinstance(c_obj[i], dict):
                    buf = c_obj.get('name') if 'name' in c_obj else ref
                else:
                    buf = ref
                change_list.append({'b': '', 'c': str(buf), 'r': _NEW})
                c += 1

    if c > 0:
        _update_r_obj(r_obj, change_list.copy())
    return c


def _zone_configuration(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare the zone configurations

    :param r_obj: Return object - Dictionary of changes
    :type r_obj: dict
    :param ref: Reference key (control_tbl look up).
    :type ref: str
    :param b_obj: Base list object.
    :type b_obj: list, tuple
    :param c_obj: Compare list object
    :type c_obj: list, tuple
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Change counter
    :rtype: int
    """
    global _REMOVED, _NEW

    change_list = list()
    c = 0

    # Build a dictionary of base and compare configuration. The key is the configuration name and the value is the list
    # of zone names in the configuraiton
    b_cfg = dict()
    c_cfg = dict()
    obj_list = [dict(c=b_cfg, o=b_obj), dict(c=c_cfg, o=c_obj)]
    for control_d in obj_list:
        cfg_d = control_d['c']
        for d in control_d['o']:
            mem_l = list() if d.get('member-zone') is None or d['member-zone'].get('zone-name') is None else \
                d['member-zone'].get('zone-name')
            cfg_d.update({d['cfg-name']: mem_l})

    # Now compare each zone configuration
    ref = 'Zone configuration '
    cfg_d = obj_list[1]['c']
    for i in range(0, len(obj_list)):
        for k, v in obj_list[i]['c'].items():
            if k not in cfg_d:
                if i == 0:
                    change_list.append({'b': str(k), 'c': '', 'r': _REMOVED})
                else:
                    change_list.append({'b': '', 'c': str(k), 'r': _NEW})
            elif i == 0:
                # We're only comparing zone configuration member lists in common zone configurations so we only need to
                # do this once.
                c += _list_compare(r_obj, str(k) + ' zone config', v, cfg_d[k], control_tbl)

    if len(change_list) > 0:
        _update_r_obj(r_obj, change_list)
        c += len(change_list)

    return c


# Object type look up table used in _compare()
_obj_type_action = {
    'ChassisObj': _brcddb_compare,
    'FabricObj': _brcddb_compare,
    'FdmiNodeObj': _brcddb_compare,
    'FdmiPortObj': _brcddb_compare,
    'LoginObj': _brcddb_compare,
    'PortObj': _brcddb_compare,
    'ProjectObj': _brcddb_compare,
    'SwitchObj': _brcddb_compare,
    'ZoneCfgObj': _brcddb_compare,
    'ZoneObj': _brcddb_compare,
    'AliasObj': _brcddb_compare,
    # 'AlertObj': _null_compare,
    'dict': _dict_compare,
    'bool': _num_compare,
    'int': _num_compare,  # Just in case someone removes normalizing int to num
    'float': _num_compare,  # Just in case someone removes normalizing float to num
    'str': _str_compare,
    'list': _list_compare,
    'tuple': _list_compare,
    'num': _num_compare,
}


def _compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two dict, list, tuple, or brcddb.classes objects

    :param r_obj: Return object - Dictionary or list of changes
    :type r_obj: dict, list
    :param ref: Reference key.
    :type ref: str
    :param b_obj: Base object to compare against.
    :type b_obj: dict, list, tuple, brcddb.classes.*
    :param c_obj: Compare object
    :type c_obj: dict, list, tuple, brcddb.classes.*
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return: Number of mismatches found
    :rtype: int
    """
    global _obj_type_action, _REMOVED, _NEW, _MISMATCH, _INVALID_REF

    # Make sure we have a valid reference.
    if not isinstance(ref, str):
        brcdapi_log.exception('Invalid reference type: ' + str(type(ref)), True)
        _update_r_obj(r_obj, {'b': '', 'c': '', 'r': _INVALID_REF})
        return 0

    # Does the base object exist?
    if b_obj is None:
        _update_r_obj(r_obj, {'b': ref, 'c': '', 'r': _NEW})
        return 1

    # Does the compare object exist?
    if c_obj is None:
        _update_r_obj(r_obj, {'b': ref, 'c': '', 'r': _REMOVED})
        return 1

    # Are we comparing the same types? A mix of int and float is OK so that gets normalized to type 'num'
    b_type = class_util.get_simple_class_type(b_obj)
    if b_type is None:
        b_type = 'num' if isinstance(b_obj, (int, float)) else \
            str(type(b_obj)).replace('<class ', '').replace('>', '').replace("\'", '')
    c_type = class_util.get_simple_class_type(c_obj)
    if c_type is None:
        c_type = 'num' if isinstance(c_obj, (int, float)) else \
            str(type(c_obj)).replace('<class ', '').replace('>', '').replace("\'", '')
    if b_type != c_type:
        _update_r_obj(r_obj, {'b': b_type, 'c': c_type, 'r': _MISMATCH})
        return 1

    if b_type in _obj_type_action:
        return _obj_type_action.get(b_type)(r_obj, ref, b_obj, c_obj, control_tbl)

    brcdapi_log.log('Unknown base object type: ' + b_type, True)
    _update_r_obj(r_obj, {'b': b_type, 'c': '', 'r': _INVALID_REF})
    return 1


def compare(b_obj, c_obj, control_tbl=None, brcddb_control_tbl=None):
    """External interface to compare utility, _compare

    :param b_obj: Base object to compare against.
    :type b_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param c_obj: Compare object
    :type c_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param control_tbl: Determines what to check. See applications.compare_test.test_control_tbl() for an example
    :type control_tbl: dict, None
    :param brcddb_control_tbl: Same function as control_tbl but for brcddb class objects. See \
        applications.compare_report._control_tbl() for an example
    :type brcddb_control_tbl: dict, None
    :return change_count: Number of changes found
    :rtype change_count: int
    :return change_d: Change structure as described in the Description section of the module header block
    :rtype change_d: dict, list
    """
    global _brcddb_control_tables

    if isinstance(brcddb_control_tbl, dict):
        _brcddb_control_tables = copy.deepcopy(brcddb_control_tbl)  # IDK why I made a copy
    r_obj = list() if isinstance(b_obj, (list, tuple)) else dict()
    return _compare(r_obj, '', b_obj, c_obj, control_tbl), r_obj


