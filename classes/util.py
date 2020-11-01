#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.classes.util` - Intended for internal use only. Includes methods common to class methods

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 29 Sep 2020   | Added more debug information in s_new_key_for_class()                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 01 Nov 2020   | Made _simple_class_type public (changed to _simple_class_type)                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '01 Nov 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.3'

import brcdapi.log as brcdapi_log

force_msg = 'To overwrite a key, set f=True in the call to s_new_key()\n'

simple_class_type = ('AlertObj', 'AliasObj', 'ChassisObj', 'FabricObj', 'LoginObj', 'FdmiNodeObj', 'FdmiPortObj',
                      'PortObj', 'ProjectObj', 'SwitchObj', 'ZoneCfgObj', 'ZoneObj')


# Used in class_getvalue():
def get_simple_class_type(obj):
    """Returns a simple 'ProjectObj', 'SwitchObj', ... for brcddb.classes.* types

    :param obj: Any brcddb object.
    :type obj: All brcddb.classes
    :return: Simple class type
    :rtype: str
    """
    global simple_class_type

    for k in simple_class_type:
        if k in str(type(obj)):
            return k
    return None  # It's not a brcddb class object


# Case statements for reserved words in
def _obj_key(obj):
    return obj._obj_key

def _alerts(obj):
    return obj._alerts

def _reserved_keys(obj):
    return obj._reserved_keys

def _project_obj(obj):
    return obj._project_obj

def _flags(obj):
    return obj._flags

def _date(obj):
    return obj._date

def _python_version(obj):
    return obj._python_version

def _description(obj):
    return obj._description

def _switch_objs(obj):
    return obj._switch_objs

def _switch_keys(obj):
    return obj._switch_keys

def _chassis_objs(obj):
    return obj._chassis_objs

def _port_objs(obj):
    return obj._port_objs

def _fabric_key(obj):
    return obj._fabric_key

def _login_objs(obj):
    return obj._login_objs

def _fabric_objs(obj):
    return _fabric_objs

def _login_keys(obj):
    return obj._login_keys

def _zonecfg_objs(obj):
    return obj._zonecfg_objs

def _eff_zone_objs(obj):
    return obj._eff_zone_objs

def _eff_zonecfg(obj):
    return obj._eff_zonecfg

def _alias_objs(obj):
    return obj._alias_objs

def _zone_objs(obj):
    return obj._zone_objs

def _switch(obj):
    return obj._switch

def _members(obj):
    return obj._members

def _pmembers(obj):
    return obj._pmembers

def _chassis_key(obj):
    return obj._chassis_key

def _fdmiPortObj(obj):
    return obj._fdmiPortObj

def _fdmi_node_objs(obj):
    return obj._fdmi_node_objs

def _fdmi_port_objs(obj):
    return obj._fdmi_port_objs

def _zonecfg(obj):
    return obj._zonecfg

def _base_logins(obj):
    return obj._base_logins

def _port_map(obj):
    return obj._port_map

def _maps_fc_port_group(obj):
    return obj._maps_fc_port_group

def _maps_sfp_group(obj):
    return obj._maps_sfp_group

def _maps_rules(obj):
    return obj._maps_rules

def _maps_group_rules(obj):
    return obj._maps_group_rules

def _maps_groups(obj):
    return obj._maps_groups


_class_reserved_case = {
    '_alerts': _alerts,
    '_reserved_keys': _reserved_keys,
    '_project_obj': _project_obj,
    '_obj_key': _obj_key,
    '_flags': _flags,
    '_date': _date,
    '_python_version': _python_version,
    '_description': _description,
    '_switch_objs': _switch_objs,
    '_switch_keys': _switch_keys,
    '_chassis_objs': _chassis_objs,
    '_port_objs': _port_objs,
    '_fabric_key': _fabric_key,
    '_login_objs': _login_objs,
    '_fabric_objs': _fabric_objs,
    '_login_keys': _login_keys,
    '_zonecfg_objs': _zonecfg_objs,
    '_eff_zone_objs': _eff_zone_objs,
    '_eff_zonecfg': _eff_zonecfg,
    '_alias_objs': _alias_objs,
    '_zone_objs': _zone_objs,
    '_switch': _switch,
    '_members': _members,
    '_pmembers': _pmembers,
    '_chassis_key': _chassis_key,
    '_fdmiPortObj': _fdmiPortObj,
    '_fdmi_node_objs': _fdmi_node_objs,
    '_fdmi_port_objs': _fdmi_port_objs,
    '_zonecfg': _zonecfg,
    '_base_logins': _base_logins,
    '_port_map': _port_map,
    '_maps_fc_port_group': _maps_fc_port_group,
    '_maps_sfp_group': _maps_sfp_group,
    '_maps_rules': _maps_rules,
    '_maps_group_rules': _maps_group_rules,
    '_maps_groups': _maps_groups,
}


def _class_reserved(obj, k):
    """Returns the value for a reserved key word

    :param obj: Any brcddb object.
    :type obj: All brcddb.classes
    :param k: Key or keys seperated by '/' to look up.
    :type k: str
    :return: Value associated with the key. None if the key was not found.
    :rtype: str
    """
    # Programmer's Tip: Everything in Python is an object and __dict__ contains the namespace for all objects.
    # Attributes added in obj.__init__() are not returned with obj.__dict__.keys() unless they are updated after object
    # creation. Most reserved keys are for attributes initialized in obj.__int__() and are not updated afterwards.
    # Since all FOS API data, and anything a user wants to add to objects, is added dynamically obj.__dict__ is used
    # to determine what's in the name space. This method returns the value for reserved keys by direct access.
    #
    # Why do attributes created in obj.__init__() not appear in obj.__dict__.keys()? I did not take the time to research
    # it. This was something I learned the hard way.
    global _class_reserved_case

    try:
        return _class_reserved_case[k](obj)
    except:
        return None


# Case statements for special in s_new_key_for_class
def special_key_scr(obj, k, v, v1):
    """Case for 'state-change-registration'

    This the RSCN handling and is only valid on the chassis where the login occured. RSCN handling is not distributed in
    the fabric. The value in the name server is None and returned as an empty string, '', in the API on all chassis
    except the chassis where the login occured.
    :param obj: brcddb object. Should be a LoginObj. The object type is assumed to be correct.
    :type obj: LoginObj
    :param k: Key to be added. We should only get here if k == 'state-change-registration'
    :type k: str
    :param v: New value
    :type v: str
    :param v1: Previous value
    :type v: str
    :return: None if no errors were encountered. Otherwise, an error message.
    :rtype: str
    """
    if len(v) > 0:
        if len(v1) > 0:
            return 'Attempted to add key who\'s value is changing. Old value is: ' + str(v1)
        else:
            setattr(obj, k, v)
    return None


def special_key_lower(obj, k, v, v1):
    """Case for keys who's lower int value should take precedence.

    :param obj: brcddb object.
    :type obj: Any class defined herein
    :param k: Key to be added.
    :type k: str
    :param v: New value
    :type v: str
    :param v1: Previous value
    :type v: str
    :return: None if no errors were encountered. Otherwise, an error message.
    :rtype: str
    """
    if v < v1:
        setattr(obj, k, v)
    return None


def special_key_higher(obj, k, v, v1):
    """Case for keys who's higher int value should take precedence.

    :param obj: brcddb object.
    :type obj: Any class defined herein
    :param k: Key to be added.
    :type k: str
    :param v: New value
    :type v: str
    :param v1: Previous value
    :type v: str
    :return: None if no errors were encountered. Otherwise, an error message.
    :rtype: str
    """
    if v > v1:
        setattr(obj, k, v)
    return None


def special_key_ignore(obj, k, v, v1):
    """Case for keys who's values and value types may change.

    To Do: Choose the preferred format.
    :param obj: brcddb object.
    :type obj: Any class defined herein
    :param k: Key to be added.
    :type k: str
    :param v: New value
    :type v: str
    :param v1: Previous value
    :type v: str
    :return: None if no errors were encountered. Otherwise, an error message.
    :rtype: str
    """
    return None


def _add_to_dict(from_dict, to_dict):
    # Support method for s_new_key_for_class() to add to dict. Adding from from_dict to to_dict
    for k in from_dict.keys():
        v = from_dict.get(k)
        if k in to_dict:
            v1 = to_dict.get(k)
            if type(v) != type(v1):
                return 'Type mismatch. ' + str(type(v)) + ', ' + str(type(v1))
            if isinstance(v, (str, int, float)):
                if v != v1:
                    return 'Attempting to change value. Old value: ' + str(v) + ', new value: ' + str(v1)
            elif isinstance(v, list):
                buf = _add_to_list(v, v1)
                if buf is not None:
                    return buf
            elif isinstance(v, dict):
                buf = _add_to_dict(v, v1)
                if buf is not None:
                    return buf
        else:
            to_dict.update({k: v})


def _add_to_list(from_list, to_list):
    # Support method for s_new_key_for_class to add to lists. Adding from from_list to to_list
    for v in from_list:
        if isinstance(v, (str, int, float)):
            if v not in to_list:
                to_list.append(v)
        elif isinstance(v, list):
            if v in to_list:
                v1 = to_list[to_list.index(v)]
                if isinstance(v1, list):
                    buf = _add_to_list(v, v1)
                    if buf is not None:
                        return buf
                else:
                    return 'Type mismatch. Attempted to add a list to ' + str(type(v1))
            else:
                to_list.append(v)
        elif isinstance(v, dict):
            if v in to_list:
                v1 = to_list[to_list.index(v)]
                if isinstance(v1, dict):
                    buf = _add_to_dict(v, v1)
                    if buf is not None:
                        return buf
                else:
                    return 'Type mismatch. Attempted to add a dict to ' + str(type(v1))
            else:
                to_list.append(v)
        else:
            return 'Unknown type in list: ' + str(type(v))


special = {
    'state-change-registration': special_key_scr,
    'firmware-version': special_key_ignore,
    'dns-servers': special_key_ignore,
    'ip-static-gateway-list': special_key_ignore,
    'ip-address': special_key_ignore,
    'db-avail': special_key_lower,
    'db-max': special_key_lower,
    'db-chassis-wide-committed': special_key_higher,
}


def s_new_key_for_class(obj, k, v, f=False):
    """Creates a new key/value pair in a brcddb object.

    The value associated with the key can be of any type; however, there are some rules:
        1)  brcdd.util.util.brcddb_to_plain_copy() will raise an exception and abort the program if an added key, not in
            _reserved_keys, has a circular reference. All brcddb objects contain circular references and therefore
            should not be added using the new_key() method.
        2)  You cannot add a reserved word as a key
        3)  You cannot add a key that has the same name as a method.
        4)  You cannot overwrite the value of type str, int, or float for an existing key. Since different Rest API
            calls may return the same information, as an expediant, this method will return True and supress all error
            messages as long as the value type is the same and is not changing. Note that since only pointers are
            stored, you can append to a list or update a dict stored in the object.
        5)  Some API requests return different information based on the chassis or different formats based on the
            requests. These are handled as special cases.

    :param obj: Object to associate the new key with
    :type obj: class object defined herein
    :param k: Key to be added
    :type k: str, int
    :param v: Value to be added. Although any type should be valid, it has only been tested ith the types below.
    :type v: str, int, list, dict
    :param f: If True, don't check to see if the key exists. Allows users to change an existing key.
    :type f: bool
    :return: True if the add succeeded or is redundant.
    :rtype: bool
    """
    global force_msg

    buf = None
    if k in obj.r_reserved_keys():
        buf = 'Attempted to add a reserved key.'
    elif hasattr(obj, k) and not f:
        if k in obj.__dict__.keys():
            # The key and value pair already exists
            v1 = obj.r_get(k)
            if k in special:
                buf = special[k](obj, k, v, v1)
                if buf is None:
                    return False  # False so that no additional processing is done
            elif type(v) != type(v1):
                buf = force_msg + 'Key already exists. Value type ' + str(type(v)) + ' is changing. New value type:' +\
                      str(type(v1))
            elif isinstance(v, (str, int, float)):
                if v != v1:
                    # If the key/value pair exists but the value is not changing ignore it. It is common for fabric wide
                    # keys to be present in multiple chassis.
                    buf = force_msg + 'Attempted to add key who\'s value is changing. Old value is: ' + str(v1)
            elif isinstance(v, list):
                buf = _add_to_list(v, v1)
            elif isinstance(v, dict):
                buf = _add_to_dict(v, v1)
            else:
                buf = force_msg + 'Attempted to add existing key.'
        else:
            # callable() would tell us for sure, but what else could it be? Even if I'm over looking something, the
            # error message won't be right but the trace stack and information provided should be adequate for most
            # programmers to figure out what's going on.
            buf = 'Attempted to add a key that has the same name as an existing method.'
    else:
        setattr(obj, k, v)
    if buf is None:
        return True
    else:
        ml = ['Object:     ' + str(type(obj))]
        if get_simple_class_type(obj) is not None:
            ml.append('Object Key: ' + obj.r_obj_key())
        ml.append('Key:        ' + k)
        ml.append('Value type: ' + str(type(v)))
        if isinstance(v, (str, int, float)):
            ml.append('Value:      ' + str(v))
        brcdapi_log.exception(ml, True)
        return False


def convert_to_list(obj):
    """Converts an object to a list as follows:

    +-----------+-----------------------------------------------------------+
    | obj       | Return                                                    |
    +===========+===========================================================+
    | None      | List with no members                                      |
    +-----------+-----------------------------------------------------------+
    | list      | The same passed object, obj, is returned - NOT A COPY     |
    +-----------+-----------------------------------------------------------+
    | tuple     | Tuple copied to a list                                    |
    +-----------+-----------------------------------------------------------+
    | All else  | List with the passed obj as the only member               |
    +-----------+-----------------------------------------------------------+

    :param obj: Object to be converted to list
    :type obj: list, tuple, dict, str, float, int
    :return: Converted list
    :rtype: list
    """
    # This is a copy and paste from brcddb_util.convert_to_list(). It takes care of scenarios that should never be
    # encountered here but I didn't want to change something that was working and its future proof.
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        if len(obj.keys()) == 0:
            return []
        return [obj]
    if isinstance(obj, tuple):
        return list(obj)
    return [obj]


def class_getvalue(obj, keys, flag=False):
    """Returns the value associated with a key.

    :param obj: Any brcddb.classes object
    :type obj: ChassisObj, FabricObj, LoginObj, FdmiNodeObj, FdmiPortObj, PortObj, ProjectObj, SwitchObj, ZoneCfgObj \
        ZoneObj, AliasObj
    :param keys: Key who's value is sought. None is allowed to simplify processing lists of keys that may not be present
    :type keys: str, None
    :param flag: If True, combine the first two keys into a single key. Used for port keys.
    :type flag: bool
    :return: Value associated with key
    :rtype: any
    """
    if keys is None or obj is None or len(keys) == 0:
        return None
    kl = keys.split('/')
    if flag:
        # The next key is going to be for the port which is in slot/port notation. The split above will seperate the
        # 2 keys so the code below puts the port key back together.
        if len(kl) > 1:
            kl[0] = kl.pop(0) + '/' + kl[0]
        else:
            return None  # Someone called this with missing keys if we get here.

    if hasattr(obj, '_reserved_keys') and kl[0] in obj._reserved_keys:
        # Typically get here when someone did an obj.r_get() on a reserved key
        new_obj = _class_reserved(obj, kl.pop(0), )
        if len(kl) > 0:
            s_type = get_simple_class_type(obj)
            return class_getvalue(new_obj, '/'.join(kl), True if s_type is not None and s_type == 'PortObj' else False)
        else:
            return new_obj
    elif hasattr(obj, '__dict__'):
        # This is where you go for anything added to a brcddb object
        v0 = obj
        while len(kl) > 0:
            k0 = kl.pop(0)
            try:
                v0 = v0.get(k0) if isinstance(v0, dict) else v0.__dict__.get(k0)
            except:
                return None  # The key was not found if we get here
        return v0
    else:
        brcdapi_log.exception('Unknown object type: ' + str(type(obj)) + '. keys: ' + keys, True)


def class_getkeys(obj):
    """Returns a list of keys added to this object.

    :return: List of keys
    :rtype: list
    """
    a = list(obj.__dict__.keys())
    for i, e in reversed(list(enumerate(a))):
        if e in obj.r_reserved_keys():
            a.pop(i)
    return a
