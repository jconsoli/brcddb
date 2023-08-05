# Copyright 2023 Consoli Solutions, LLC.  All rights reserved.
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
:mod:`brcddb.util.copy` - Contains brcddb class object copy methods

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | object_copy           | Performs the iterative (deep) copy of plain dict to brcddb object. Used by            |
    |                       | brcddb_to_plain_copy()                                                                |
    +-----------------------+---------------------------------------------------------------------------------------+
    | brcddb_to_plain_copy  | Copies a brcddb dict class to a plain python dict.                                    |
    +-----------------------+---------------------------------------------------------------------------------------+
    | plain_copy_to_brcddb  | Copies a plain object created with brcddb_to_plain_copy back to a brcddb object.      |
    |                       | Typically used after read_dump to convert a plain dict back to a project object - see |
    |                       | brcddb_project.py                                                                     |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023 Consoli Solutions, LLC'
__date__ = '04 August 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.0'

import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log

_default_skip_list = [
    '_alerts',
    '_project_obj',
    '_zonecfg',
    '_base_logins',
    '_port_map',
    '_maps_fc_port_group'
    '_maps_sfp_group',
    '_maps_rules',
    '_maps_group_rules',
    '_maps_groups',
]


def object_copy(obj, objx, flag_obj=None, skip_list=None):
    """Performs the iterative (deep) copy of plain dict to brcddb object. Used by brcddb_to_plain_copy()

    :param obj: Object to be copied.
    :type obj: dict, list
    :param objx: brcddb object where obj is to be copied
    :type objx: brcddb class object
    :param flag_obj: The object to be used for the bit flags.
    :type flag_obj: Any brcddb object
    :param skip_list: Keys to skip
    :type skip_list: list, tuple
    :rtype: None
    """
    if skip_list is None:
        skip_list = list()
    # Programmer’s Tip: Note that the rest object and brcddb object are reversed. My humble apologies for that.
    if isinstance(obj, dict):
        for k in obj.keys():
            if k not in skip_list:
                v = obj.get(k)
                if isinstance(v, (str, int, float)):  # Remember that bool is a sub-class of int
                    if flag_obj is None:
                        if isinstance(objx, dict):
                            objx.update({k: v})
                        elif isinstance(objx, list):
                            objx.append(v)
                        else:
                            brcdapi_log.exception('Unexpected type: ' + str(type(objx)), True)
                elif isinstance(v, dict):
                    if isinstance(objx, dict):
                        d = dict()
                        objx.update({k: d})
                        object_copy(v, d, flag_obj, skip_list)
                    elif isinstance(objx, list):
                        d = list()
                        objx.append(d)
                        object_copy(v, d, flag_obj, skip_list)
                    else:
                        brcdapi_log.exception('Unexpected type: ' + str(type(objx)), True)
                elif isinstance(v, list):
                    if isinstance(objx, dict):
                        d = list()
                        objx.update({k: d})
                        object_copy(v, d, flag_obj, skip_list)
                    elif isinstance(objx, list):
                        d = list()
                        objx.append(d)
                        object_copy(v, d, flag_obj, skip_list)
                    else:
                        brcdapi_log.exception('Unexpected type: ' + str(type(objx)), True)
                elif 'brcddb.classes' in str(type(v)):
                    # This happens when a data structure was added, usually with new_key(), to a brcdb object. Methods,
                    # such as brcddb_fabric.zone_analysis(), do this. Since we are making a plain copy here, the only
                    # thing we can do is make copy of it. The copy back to a brcddb uses the object creation methods
                    # which check to see if the object was already created so it will revert back to just a pointer.
                    # Although this works, it wastes a lot of space which could be problematic with large projects,
                    # hence the exception warning.
                    d1 = dict()
                    objx.update({k: d1})
                    brcddb_to_plain_copy(v, d1, flag_obj, skip_list)
                    brcdapi_log.exception('Making large copies with ' + str(k) +
                                          '. Although it works, it\'s probably ' + 'not what you intended.', True)
                else:
                    brcdapi_log.exception('Type of value associated with ' + str(k) + ' unknown. Type is ' +
                                          str(type(v)), True)
    elif isinstance(obj, list):
        # We never get here for data returned from the API. We only get here if a custom key was added.
        for v in obj:
            if isinstance(v, (str, int)):
                if isinstance(objx, list):
                    objx.append(v)
                else:
                    brcdapi_log.exception('Unexpected objx type: ' + str(type(objx)), True)
            elif isinstance(v, dict):
                if isinstance(objx, list):
                    d = dict()
                    objx.append(d)
                    object_copy(v, d, flag_obj, skip_list)
                elif isinstance(objx, dict):
                    object_copy(v, objx, flag_obj, skip_list)
                else:
                    brcdapi_log.exception('Unexpected objx type: ' + str(type(objx)), True)
            elif isinstance(v, list):
                if isinstance(objx, list):
                    objx.append(v)
                else:
                    brcdapi_log.exception('Unexpected objx type: ' + str(type(objx)), True)
            elif 'brcddb.classes' in str(type(v)):
                d = dict()
                objx.append(d)
                brcddb_to_plain_copy(v, d, flag_obj, skip_list)
            else:
                brcdapi_log.exception('Type of value unknown. Type is ' + str(type(v)), True)
    else:
        brcdapi_log.exception('Unknown type: ' + str(type(obj)), True)


def brcddb_to_plain_copy(objx, obj, flag_obj=None, skip_list=None):
    """Copies a brcddb dict class to a plain python dict.

    :param objx: brcddb object to convert to plain dict
    :type objx: brcddb class object
    :param obj: plain dictionary where objx is to be copied
    :type obj: dict
    :param flag_obj: The object to be used for the bit flags.
    :type flag_obj: Any brcddb object
    :param skip_list: Keys to skip
    :type skip_list: list, tuple
    :rtype: None
    """

    if skip_list is None:
        skip_list = _default_skip_list
    # Copy all the reserved keys
    if hasattr(objx, 'r_reserved_keys') and callable(getattr(objx, 'r_reserved_keys')) and \
            hasattr(objx, 'r_keys') and callable(getattr(objx, 'r_keys')):

        for k in objx.r_reserved_keys():
            if k not in skip_list:
                if k == '_flags' and 'ProjectObj' in str(type(objx)):
                    v = objx.r_flags() & ~brcddb_common.project_error_warn_mask
                else:
                    v = objx.r_get_reserved(k)
                    if v is None:
                        # If a switch is disabled, it's not in a fabric so the value with _fabric_key will be None. I
                        # can't think of any other reserved key that would have a value of None
                        continue
                if isinstance(v, (str, int, tuple)):
                    obj.update({k: v})
                elif isinstance(v, list):
                    d = list()
                    obj.update({k: d})
                    object_copy(v, d, flag_obj, skip_list)
                elif isinstance(v, dict):
                    d = dict()
                    obj.update({k: d})
                    for k1 in v.keys():
                        v1 = v.get(k1)
                        # This wasn't very well thought out. I should have put everything in object_copy() in here
                        # rather than break it out separate.
                        if 'brcddb.classes' in str(type(v1)):
                            d1 = dict()
                            d.update({v1.r_obj_key(): d1})
                            brcddb_to_plain_copy(v1, d1, flag_obj, skip_list)
                        else:
                            object_copy(v, d, flag_obj, skip_list)
                            continue

                elif 'dict_values' in str(type(v)):
                    # Note: isinstance(v, dict_values) returns False. This is a bug fixed in Python 3.7. See
                    # https://bugs.python.org/issue32467. For those not at 3.7 yet, this cheesy check gets by it.
                    # All methods that return dict_values were changed to return list so we shouldn't get in here.
                    d = dict()
                    obj.update({k: d})
                    for obj1 in v:
                        d1 = dict()
                        d.update({obj1.r_obj_key(): d1})
                        brcddb_to_plain_copy(obj1, d1, flag_obj, skip_list)
                else:
                    d = dict()
                    obj.update({k: d})
                    brcddb_to_plain_copy(v, d, flag_obj, skip_list)

        # Process the dynamically added keys
        if objx.r_keys() is not None:
            for k in objx.r_keys():
                if k not in skip_list:
                    v = objx.r_get(k)
                    if v is None or isinstance(v, (str, int, float, list)):
                        obj.update({k: v})
                    elif isinstance(v, dict):
                        d = dict()
                        brcddb_to_plain_copy(v, d, flag_obj, skip_list)
                        obj.update({k: d})
                    else:
                        brcdapi_log.exception('Unknown variable type for key ' + k + '. Type is ' + str(type(v)), True)

    else:
        object_copy(objx, obj, flag_obj, skip_list)


# The functions below effectively make up a C case statement for the reserved words in the brcddb classes
def _brcddb_null(obj=None, objx=None):
    return


def _brcddb_flags_key(obj, objx):  # All
    objx.s_or_flags(obj)


def _brcddb_date_key(obj, objx):  # project and hopefully port someday
    objx._date = obj


def _brcddb_python_version_key(obj, objx):  # project
    objx.s_python_version(obj)


def _brcddb_description_key(obj, objx):  # project
    objx.s_description(obj)


def brcddb_fabrics_key(obj, objx):  # project
    for fkey in obj:
        plain_copy_to_brcddb(obj.get(fkey), objx.s_add_fabric(fkey))


def _brcddb_chassis_objs_key(obj, objx):  # project
    for k in obj:
        plain_copy_to_brcddb(obj.get(k), objx.s_add_chassis(k))


def _brcddb_switch_objs_key(obj, objx):  # project
    for k in obj:
        plain_copy_to_brcddb(obj.get(k), objx.s_add_switch(k))


def _brcddb_switch_keys_key(obj, objx):  # fabric, chassis
    for k in obj:
        objx.s_add_switch(k)


def _brcddb_port_objs_key(obj, objx):  # switch
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_port(k))


def _brcddb_ge_port_objs_key(obj, objx):  # switch
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_ge_port(k))


def _brcddb_fabric_key(obj, objx):  # Many
    if hasattr(objx, 's_fabric_key') and callable(getattr(objx, 's_new_key')):
        objx.s_fabric_key(obj)


def _brcddb_login_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_login(k))


def _brcddb_fabric_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_fabric(k))


def _brcddb_login_keys_key(obj, objx):  # port
    for v in obj:
        objx.s_add_login(v)


def _brcddb_eff_zone_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        zone_obj = obj.get(k)
        objx.s_add_eff_zone(k, zone_obj.get('_type'), zone_obj.get('_members'), zone_obj.get('_pmembers'))


def _brcddb_eff_zonecfg_key(obj, objx):  # fabric
    plain_copy_to_brcddb(obj, objx.s_add_eff_zonecfg(obj.get('_name')))


def _brcddb_alias_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_alias(k))


def _brcddb_zonecfg_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_zonecfg(k))


def _brcddb_zone_objs_key(obj, objx):  # fabric
    for k in obj.keys():
        zone_obj = obj.get(k)
        objx.s_add_zone(k, zone_obj.get('_type'), zone_obj.get('_members'), zone_obj.get('_pmembers'))


def _brcddb_switch_key(obj, objx):  # port
    pass


def _brcddb_members_key(obj, objx):  # All zoning classes
    for v in obj:
        objx.s_add_member(v)


def _brcddb_pmembers_key(obj, objx):  # zone
    for v in obj:
        objx.s_add_pmember(v)


def _brcddb_chassis_key_key(obj, objx):  # Chassis WWN
    objx.s_chassis_key(obj)


def _brcddb_fdmi_port_obj_key(obj, objx):    # LoginObj
    objx.s_add_fdmi_port_obj(obj.get('_fdmiPortObj'))


def _brcddb_fdmi_node_objs_key(obj, objx):  # FabricObj
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_fdmi_node(k))


def _brcddb_fdmi_port_objs_key(obj, objx):  # FabricObj
    for k in obj.keys():
        plain_copy_to_brcddb(obj.get(k), objx.s_add_fdmi_port(k))


r_key_table = dict(
    _alerts=_brcddb_null,
    _reserved_keys=_brcddb_null,
    _project_obj=_brcddb_null,
    _obj_key=_brcddb_null,
    _flags=_brcddb_flags_key,
    _date=_brcddb_date_key,
    _python_version=_brcddb_python_version_key,
    _description=_brcddb_description_key,
    _switch_objs=_brcddb_switch_objs_key,
    _switch_keys=_brcddb_switch_keys_key,
    _chassis_objs=_brcddb_chassis_objs_key,
    _port_objs=_brcddb_port_objs_key,
    _ge_port_objs=_brcddb_ge_port_objs_key,
    _fabric_key=_brcddb_fabric_key,
    _login_objs=_brcddb_login_objs_key,
    _fabric_objs=_brcddb_fabric_objs_key,
    _login_keys=_brcddb_login_keys_key,
    _zonecfg_objs=_brcddb_zonecfg_objs_key,
    _eff_zone_objs=_brcddb_eff_zone_objs_key,
    _eff_zonecfg=_brcddb_eff_zonecfg_key,
    _alias_objs=_brcddb_alias_objs_key,
    _zone_objs=_brcddb_zone_objs_key,
    _switch=_brcddb_switch_key,
    _members=_brcddb_members_key,
    _pmembers=_brcddb_pmembers_key,
    _chassis_key=_brcddb_chassis_key_key,
    _fdmiPortObj=_brcddb_fdmi_port_obj_key,
    _fdmi_node_objs=_brcddb_fdmi_node_objs_key,
    _fdmi_port_objs=_brcddb_fdmi_port_objs_key,
    _zonecfg=_brcddb_null,
    _base_logins=_brcddb_null,
    _port_map=_brcddb_null,
    _maps_fc_port_group=_brcddb_null,
    _maps_sfp_group=_brcddb_null,
    _maps_rules=_brcddb_null,
    _maps_group_rules=_brcddb_null,
    _maps_groups=_brcddb_null,
    _type=_brcddb_null,
    _chpid_objs=_brcddb_null,
    _switch_id=_brcddb_null,
    _link_addr=_brcddb_null,
)


def plain_copy_to_brcddb(obj, objx):
    """Copies a plain object created with brcddb_to_plain_copy back to a brcddb object. Typically used after read_dump
    to convert a plain dict back to a project object - see brcddb_project.py

    :param obj: Source object
    :type obj: dict, list, tuple
    :param objx: Destination Object
    :type objx: brcddb class object
    :rtype: None
    """
    if objx is None:
        return
    if isinstance(obj, dict):
        for k in obj.keys():
            v = obj.get(k)
            if k in r_key_table:
                r_key_table[k](v, objx)
            elif isinstance(v, (str, int, float, list)) or v is None:
                if hasattr(objx, 's_new_key') and callable(getattr(objx, 's_new_key')):
                    objx.s_new_key(k, v)
                else:
                    objx.update({k: v})
            elif isinstance(v, dict):
                if hasattr(objx, 's_new_key') and callable(getattr(objx, 's_new_key')):
                    objx.s_new_key(k, dict())
                    plain_copy_to_brcddb(v, objx.r_get(k))
                else:
                    d = dict()
                    plain_copy_to_brcddb(v, d)
                    objx.update({k: d})
            else:
                brcdapi_log.exception('Unknown v type. Key is: ' + k + ', type is: ' + str(type(v)), True)
                
    elif isinstance(obj, (list, tuple)):
        if isinstance(objx, list):
            for v in obj:
                if isinstance(v, dict):
                    d = dict()
                    plain_copy_to_brcddb(v, d)
                    objx.append(d)
                elif isinstance(v, (list, tuple)):
                    d = list()
                    plain_copy_to_brcddb(v, d)
                    objx.append(d)
                elif isinstance(v, (str, int, float)):
                    objx.append(v)
                else:
                    # This is a code bug. objx should always be a list by the time we get here
                    brcdapi_log.exception('Type of v is unknown. Type is: ' + str(type(v)), True)
                    return
        else:
            for v in obj:
                if isinstance(v, (str, int, float)):
                    if v in r_key_table:
                        r_key_table[v](obj, objx)
                    else:
                        objx.append(v)
                elif isinstance(v, dict):
                    d = dict()
                    plain_copy_to_brcddb(v, d)
                    objx.append(d)
                elif isinstance(v, (list, tuple)):
                    d = list()
                    plain_copy_to_brcddb(v, d)
                    objx.append(d)
                else:
                    # This is a code bug.
                    brcdapi_log.exception('Type of v is unknown. Type is: ' + str(type(v)), True)
                    return
    else:
        brcdapi_log.exception('Unknown obj type, ' + str(type(obj)), True)
