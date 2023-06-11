# Copyright 2020, 2021, 2022, 2023 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.util.compare` - Useful for comparing complex objects

Although primarily developed to support comparing brcddb objects, those objects also contain standard Python data
structures so this module can be used to compare anything.

**Description**

compare(), the only public method in this module, returns a dictionary as noted below.

change_rec = compare(b_obj, c_obj, control_tbl)
  b_obj       Can be any object. This is the base (what you are comparing against)
  c_obj       The compare object.
  control_tbl Controls the comparison. Note that you typically don't want a report cluttered with minor changes. For
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

**Important Notes**

    * int & float types are treated as the same type so as to avoid getting a type mismatch. This means 5 and 5.0 are
      considered the same.
    * Base ('b') and compare ('c') values are always converted to a str in the output

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | compare               | External interface to compare utility, _compare                                       |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-6   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 14 May 2021   | Updated comments                                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 31 Dec 2021   | Removed unused code.                                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 28 Apr 2022   | Updated documentation                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 04 Sep 2022   | Minor performance enhancements. No functional changes.                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 11 Feb 2023   | Added user feedback for long projects and better handling of lists                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 21 May 2023   | Removed unused code.                                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '21 May 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.2'

import copy
import re
import brcdapi.log as brcdapi_log
import brcddb.classes.util as class_util
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_switch as brcddb_switch

_REMOVED = 'Removed'
_NEW = 'Added'
_CHANGED = 'Changed'
_MISMATCH = 'Different types'
_INVALID_REF = 'Programming error. Invalid reference. Check the log for details.'

_brcddb_control_tables = None


def _update_r_obj(r_obj, d):
    """Utility to update the return object

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


def _check_control(in_ref, control_tbl):
    """Check the reference against the control table

    :param in_ref: Reference object to look for in the control table
    :type in_ref: str
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return skip_flag: True if the ref was found in control_tbl and it indicated that the test should be skipped.
    :rtype skip_flag: bool
    :return lt: Less than or equal amount for this ref in control_tbl. 0 if not found
    :rtype lt: int, float
    :return gt: Greater than or equal amount for this ref in control_tbl. 0 if not found
    :rtype gt: int, float
    """
    skip_flag, lt, gt = False, 0, 0
    if isinstance(control_tbl, dict):

        # Remove the list index
        ref_l = in_ref.split('[')
        i, ref, len_rel_l = 1, ref_l[0], len(ref_l)
        while i < len_rel_l:
            try:
                ref += ref_l[i].split(']')[1]
            except IndexError:
                pass
            i += 1

        for k in control_tbl.keys():
            if re.search(k, ref):
                cd = control_tbl.get(k)
                skip_flag = bool(cd.get('skip'))
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
    if b_str != c_str:
        _update_r_obj(r_obj, {'b': b_str, 'c': c_str, 'r': _CHANGED})
        return 1

    return 0


def _bool_compare(r_obj, ref, b_flag, c_flag, control_tbl):
    """int or float compare. See _str_compare() for parameter definitions"""
    global _REMOVED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0
    if c_flag is None:
        _update_r_obj(r_obj, {'b': str(b_flag), 'c': '', 'r': _REMOVED})
        return 1
    if c_flag != b_flag:
        _update_r_obj(r_obj, {'b': str(b_flag), 'c': str(c_flag), 'r': _CHANGED})
        return 1
    return 0


def _num_compare(r_obj, ref, b_num, c_num, control_tbl):
    """int or float compare. See _str_compare() for parameter definitions"""
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
    """Compares two brcddb objects. See _str_compare() for parameter definitions"""
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
    """Compares two brcddb objects. See _str_compare() for parameter definitions"""
    global _brcddb_control_tables

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    new_r_obj = dict()
    try:
        ct = _brcddb_control_tables.get(class_util.get_simple_class_type(b_obj))
    except KeyError:
        ct = None
    c = _brcddb_internal_compare(new_r_obj, '', b_obj, c_obj, ct)
    if c > 0:
        r_obj.update(copy.deepcopy(new_r_obj))  # IDK why I did a copy here
    return c


def _dict_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare dictionary objects. See _str_compare() for parameter definitions"""
    global _REMOVED, _NEW

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

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
            _update_r_obj(r_obj, {k: copy.deepcopy(new_r_obj)})  # IDK why I made all these copies
            c += x
    for k in c_obj.keys():  # Anything added?
        if k not in b_obj:
            skip_flag_0, lt_0, gt_0 = _check_control(ref + '/' + k, control_tbl)
            if not skip_flag_0:
                _update_r_obj(r_obj, {k: {'b': '', 'c': k, 'r': _NEW}})
            c += 1

    return c


def _list_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare list or tuple objects. See _str_compare() for parameter definitions"""
    global _REMOVED, _NEW, _MISMATCH, _CHANGED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    # Are they the same length?
    len_b_obj, len_c_obj = len(b_obj), len(c_obj)
    if len_b_obj == 0 and len_c_obj == 0:
        return 0
    if len_b_obj != len_c_obj:
        _update_r_obj(r_obj, {'b': str(b_obj), 'c': str(c_obj), 'r': _CHANGED})
        return 1

    c = 0
    for i in range(0, len_b_obj):
        c += _compare(r_obj, ref+'['+str(i)+']', b_obj[i], c_obj[i], control_tbl)

    return c


def _unknown_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare list objects. See _str_compare() for parameter definitions"""
    global _INVALID_REF

    brcdapi_log.exception('Unknown base object type: ' + str(type(b_obj)), echo=True)
    _update_r_obj(r_obj, {'b': str(type(b_obj)), 'c': '', 'r': _INVALID_REF})
    return 1


# Object type look up table used in _compare()
_obj_type_action = dict(
    ChassisObj=_brcddb_compare,
    FabricObj=_brcddb_compare,
    FdmiNodeObj=_brcddb_compare,
    FdmiPortObj=_brcddb_compare,
    LoginObj=_brcddb_compare,
    PortObj=_brcddb_compare,
    ProjectObj=_brcddb_compare,
    SwitchObj=_brcddb_compare,
    ZoneCfgObj=_brcddb_compare,
    ZoneObj=_brcddb_compare,
    AliasObj=_brcddb_compare,
    # AlertObj=null_compare,
    dict=_dict_compare,
    bool=_num_compare,
    int=_num_compare,
    float=_num_compare,
    str=_str_compare,
    list=_list_compare,
    tuple=_list_compare,
    unknown=_unknown_compare
)


def _simple_type(obj):
    """Used to create the type for use in _obj_type_action"""
    obj_type = class_util.get_simple_class_type(obj)
    if obj_type is None:
        obj_type = 'bool' if isinstance(obj, bool) else \
            'int' if isinstance(obj, int) else \
            'float' if isinstance(obj, float) else \
            'dict' if isinstance(obj, dict) else \
            'str' if isinstance(obj, str) else \
            'list' if isinstance(obj, list) else \
            'tuple' if isinstance(obj, tuple) else \
            'unknown'
    return obj_type if obj_type in _obj_type_action else 'unknown'


_compare_feedback_d = dict(ProjectObj=brcddb_project.best_project_name,
                           ChassisObj=brcddb_chassis.best_chassis_name,
                           FabricObj=brcddb_fabric.best_fab_name,
                           SwitchObj=brcddb_switch.best_switch_name)


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

    b_type, c_type = _simple_type(b_obj), _simple_type(c_obj)
    if b_type in _compare_feedback_d:
        brcdapi_log.log('Comparing ' + b_type + ': ' + _compare_feedback_d[b_type](b_obj), echo=True)

    # Make sure we have a valid reference.
    if not isinstance(ref, str):
        brcdapi_log.exception('Invalid reference type: ' + str(type(ref)), echo=True)
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

    # Are we comparing the same types?
    if b_type != c_type:
        _update_r_obj(r_obj, {'b': b_type, 'c': c_type, 'r': _MISMATCH})
        return 1

    return _obj_type_action[b_type](r_obj, ref, b_obj, c_obj, control_tbl)


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
