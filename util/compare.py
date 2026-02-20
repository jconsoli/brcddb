"""
Copyright 2023, 2024, 2025, 2026 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Developed to support comparing brcddb class objects, but it works on anything. I didn't need everything in DeepDiff and
I needed a way to filter what I was looking for. For example, when trying to determine if TX power levels have changed I
want to filter out minor differences.

compare(), the only public method in this module, returns the number of changes and a dictionary as described below for
each difference.

+-------+-----------------------------------+
| Key   | Description                       |
+=======+===================================+
| b     | The base value                    |
+-------+-----------------------------------+
| c     | The compare value                 |
+-------+-----------------------------------+
| r     | Difference between 'b' and 'c'    |
+-------+-----------------------------------+

For example:

debug_0_d = dict(val_a='dog', val_b='cat', val_c=dict(val_c_a=1, val_c_b=2, val_c_c=3))
debug_1_d = dict(val_a='dog', val_b='horse', val_c=dict(val_c_a=1, val_c_b=2, val_c_c=6))

Will return:

{
    val_b: {
        'b': 'cat',
        'c': 'horse',
        'r': 'Changed',
    val_c: {
        val_c_c: {
            'b': 3
            'c': 6
            'r': 3

**Important Notes**

    * int & float types are treated as the same type to avoid getting a type mismatch. This means 5 and 5.0 are
      considered the same.
    * Base ('b') and compare ('c') values are always converted to a str in the output

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| compare               | External interface to compare utility, _compare                                           |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Fixed case where a key was in the control_tbl as skip but processed anyway            |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 01 Mar 2025   | Fixed issues with deleted items in brcddb class objects getting missed.               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 25 Aug 2025   | Use  class_util.get_simple_class_type(obj, all_types=True) in _simple_type()          |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 20 Feb 2026   | Updated copyright notice.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025, 2026 Jack Consoli'
__date__ = '20 Feb 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.5'

import copy
import re
import brcdapi.log as brcdapi_log
import brcddb.classes.util as class_util
import brcddb.util.util as brcddb_util
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.brcddb_switch as brcddb_switch

_REMOVED = 'Removed'
_NEW = 'Added'
_CHANGED = 'Changed'
_MISMATCH = 'Different types'
_INVALID_REF = 'Programming error. Invalid reference. Check the log for details.'

_brcddb_control_tables = dict()


def _check_control(in_ref, control_tbl):
    """Check the reference against the control table

    :param in_ref: Reference object to look for in the control table
    :type in_ref: str
    :param control_tbl: Control table.
    :type control_tbl: dict
    :return skip_flag: True if the ref was found in control_tbl and the ref indicated that the test should be skipped.
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
                skip_flag = cd.get('skip', False)
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
        brcddb_util.add_to_obj(r_obj, ref, dict(b=b_str, c='', r=_REMOVED))
        return 1
    if b_str != c_str:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=b_str, c=c_str, r=_CHANGED))
        return 1

    return 0


def _bool_compare(r_obj, ref, b_flag, c_flag, control_tbl):
    """int or float compare. See _str_compare() for parameter definitions"""
    global _REMOVED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0
    if c_flag is None:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=str(b_flag), c='', r=_REMOVED))
        return 1
    if c_flag != b_flag:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=str(b_flag), c=str(c_flag), r=_CHANGED))
        return 1

    return 0


def _num_compare(r_obj, ref, b_num, c_num, control_tbl):
    """int or float compare. See _str_compare() for parameter definitions"""
    global _REMOVED

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    buf = None
    if c_num > b_num + gt:
        buf = '+' + str(c_num - b_num)
    elif c_num < b_num - lt:
        buf = '-' + str(b_num - c_num)
    if buf is not None:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=str(b_num), c=str(c_num), r=buf))
        return 1

    return 0


def _brcddb_internal_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two brcddb objects. See _str_compare() for parameter definitions"""
    global _NEW

    c = 0

    # Compare all the class objects
    for k in b_obj.r_get_reserved('_reserved_keys'):
        new_ref = ref + '/' + k if len(ref) > 0 else k
        skip_flag, lt, gt = _check_control(new_ref, control_tbl)
        if not skip_flag:
            c += _compare(r_obj, new_ref, b_obj.r_get_reserved(k), c_obj.r_get_reserved(k), control_tbl)

    # Compare all the added objects
    tl = b_obj.r_keys()
    for k in tl:
        c += _compare(r_obj, ref + '/' + k, b_obj.r_get(k), c_obj.r_get(k), control_tbl)

    # Check for added objects
    for k in c_obj.r_keys():
        if k not in tl:
            brcddb_util.add_to_obj(r_obj, ref, dict(b='', c=k, r=_NEW))
            c += 1

    return c


def _brcddb_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two brcddb objects. See _str_compare() for parameter definitions"""
    global _brcddb_control_tables

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    return _brcddb_internal_compare(
        r_obj,
        ref,
        b_obj,
        c_obj,
        _brcddb_control_tables.get(class_util.get_simple_class_type(b_obj), None)
    )


def _dict_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare dictionary objects. See _str_compare() for parameter definitions"""
    global _REMOVED, _NEW

    skip_flag, lt, gt = _check_control(ref, control_tbl)
    if skip_flag:
        return 0

    c = 0  # Number of changes to be returned

    # Compare the values against the base.
    for k, b_obj_r in b_obj.items():  # Check existing
        new_ref = ref + '/' + k if len(ref) > 0 else k
        c_obj_r = c_obj.get(k)
        if c_obj_r is None:
            skip_flag_0, lt_0, gt_0 = _check_control(new_ref, control_tbl)
            if not skip_flag_0:
                brcddb_util.add_to_obj(r_obj, new_ref, dict(b=k, c='', r=_REMOVED))
                c += 1
        else:
            c += _compare(r_obj, new_ref, b_obj_r, c_obj_r, control_tbl)

    # No need to compare values again. Just check to see if anything was added.
    for k, c_obj_r in c_obj.items():
        new_ref = ref + '/' + k if len(ref) > 0 else k
        if k not in b_obj:
            skip_flag_0, lt_0, gt_0 = _check_control(new_ref, control_tbl)
            if not skip_flag_0:
                brcddb_util.add_to_obj(r_obj, new_ref, dict(b='', c=k, r=_NEW))
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
        brcddb_util.add_to_obj(r_obj, ref, dict(b='length ' + str(len_b_obj), c='length ' + str(len_c_obj), r=_CHANGED))
        return 1

    c = 0
    for i in range(0, len_b_obj):
        c += _compare(r_obj, ref+'['+str(i)+']', b_obj[i], c_obj[i], control_tbl)

    return c


def _unknown_compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compare list objects. See _str_compare() for parameter definitions"""
    global _INVALID_REF

    buf = str(type(b_obj))
    brcdapi_log.exception(['Unknown base object type: ' + buf, ''], echo=True)
    brcddb_util.add_to_obj(r_obj, ref, dict(b=buf, c='', r=_INVALID_REF))

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
    obj_type = class_util.get_simple_class_type(obj, all_types=True)

    return obj_type if obj_type in _obj_type_action else 'unknown'


_compare_feedback_d = dict(ProjectObj=brcddb_project.best_project_name,
                           ChassisObj=brcddb_chassis.best_chassis_name,
                           FabricObj=brcddb_fabric.best_fab_name,
                           SwitchObj=brcddb_switch.best_switch_name)


def _compare(r_obj, ref, b_obj, c_obj, control_tbl):
    """Compares two dict, list, tuple, or brcddb.classes objects

    :param r_obj: Return object - Dictionary or list of changes
    :type r_obj: dict, list
    :param ref: Reference key in slash notation. Used as a key for dictionaries
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
        buf = 'Comparing ' + b_type + ': ' + _compare_feedback_d[b_type](b_obj) + ' to ' + c_type + ': '
        buf += _compare_feedback_d[c_type](c_obj)
        brcdapi_log.log(buf, echo=True)

    # Make sure we have a valid reference.
    if not isinstance(ref, str):
        brcdapi_log.exception('Invalid reference type: ' + str(type(ref)), echo=True)
        return 0

    # Does the base object exist?
    if b_obj is None:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=ref, c='', r=_NEW))
        return 1

    # Does the compare object exist?
    if c_obj is None:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=ref, c='', r=_REMOVED))
        return 1

    # Are we comparing the same types?
    if b_type != c_type:
        brcddb_util.add_to_obj(r_obj, ref, dict(b=b_type, c=c_type, r=_MISMATCH))
        return 1

    return _obj_type_action[b_type](r_obj, ref, b_obj, c_obj, control_tbl)


def compare(b_obj, c_obj, control_tbl=None, brcddb_control_tbl=None):
    """External interface to compare utility, _compare

    :param b_obj: Base object to compare against.
    :type b_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param c_obj: Compare object
    :type c_obj: brcddb.classes - chassis, fabric, login, port, project, switch, zone
    :param control_tbl: Determines what to check. See compare_report.py for an example.
    :type control_tbl: dict, None
    :param brcddb_control_tbl: Same function as control_tbl but for brcddb class objects.
    :type brcddb_control_tbl: dict, None
    :return change_count: Number of changes found
    :rtype change_count: int
    :return change_d: Change structure as described in the Description section of the module header block
    :rtype change_d: dict, list
    """
    global _brcddb_control_tables

    if isinstance(brcddb_control_tbl, dict):
        _brcddb_control_tables = brcddb_control_tbl
    r_obj = dict()

    return _compare(r_obj, '', b_obj, c_obj, control_tbl), r_obj
