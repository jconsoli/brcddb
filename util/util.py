#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.util.util` - Utility functions for the brcddb libraries

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '19 Jul 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import re
import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log

_DEBUG_FICON = True  # Intended for lab use only. Few, if any, will use this to zone a FICON switch
_MAX_ZONE_NAME_LEN = 64


def ports_for_login(login_list):
    """Returns a list of port objects associated with a list of login objects.

    :param login_list: list of login objects, brcddb.classes.login.LoginObj
    :type login_list: list, tuple
    :return port_list: List of port objects, PortObj, associated with the login objects in login_list
    :rtype: list
    """
    # If it's a SIM port, the WWN is in the name server but not 'neighbor' so check before tyring to append
    return [l._r_port_obj() for l in login_list if l._r_port_obj() is not None]


def port_obj_for_wwn(objx, wwn):
    """Returns the port object for a switch port WWN.

    :param objx: A brcddb class object that has a method port_objects()
    :type objx: ProjectObj, FabricObj, SwitchObj, ChassisObj
    :param wwn: WWN of a switch port
    :type wwn: str
    :return: Port Object. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    # Programmers Tip: The need to know a port WWN is rare. Although the key for all other objects is the WWN, with
    # ports I used the port number because virtual ports do not have a WWN. The only time I needed to associate a port
    # object with a port WWN is when reporting the neighbor switch name. Remember that 'neighbor' in the rest API for
    # the E-Port is the neighbor port WWN, not the switch WWN. This is extremely inefficient but good enough. If you
    # find yourself in a situation where you need to look up a port object from a port WWN often, you should build a
    # table, similar to brcddb_project.build_xref(), for effecient look ups.
    l = match(objx.r_port_objects(), 'wwn', wwn, ignore_case=True, stype='exact')
    return l[0] if len(l) > 0 else None


def get_key_val(obj, keys):
    """Spins through a list of keys separated by a '/' and returns the value associated with the last key.

    :param obj: Starting point in the object
    :type obj: dict, ProjectObj, FabricObj, SwitchObj, PortObj, ZoneCfgObj, ZoneObj, PortObj, LoginObj
    :param keys: Sting of keys to look through
    :type keys: str
    :return: Value associated with last key
    :rtype: int, float, str, list, tuple, dict
    """
    if hasattr(obj, 'r_get') and callable(obj.r_get):
        return obj.r_get(keys)

    v = obj
    for k in keys.split('/'):
        if isinstance(v, dict):
            v = v.get(k)
        elif v is not None:
            brcdapi_log.exception('Object type, ' + str(type(v)) + ', for ' + k + ', in ' + keys +
                                 ' not a dict or brcddb object ', True)
    return v


def sort_obj_num (obj_list, key, r=False, h=False):
    """Sorts a list of objects based on a number (int or float) that is the value of a key value pair in the objects.

    :param obj_list: List of dict or brcddb class objects
    :type obj_list: list, tuple
    :param key: Key for the value to be compared. To look in a substr, seperate keys with a '/'. All keys must be a \
        key to a dict or brcddb object
    :type key: str
    :param r: Reverse flag. If True, sort in reverse order (largest in [0])
    :type r: bool
    :param h: True indicates that the value referenced by the key is a hex number
    :type h: bool
    :return: Sorted list of obects.
    :rtype: list
    """
    count_dict = {}  # key is the count (value of dict item whose key is the input counter). Value is a list of port
                     # objects whose counter matches this count

    for obj in obj_list:
        # Get the object to test against
        v = get_key_val(obj, key)
        if v is not None and h:
            v = int(v, 16)
        if isinstance(v, (int, float)):
            try:
                count_dict[v].append(obj)
            except:
                count_dict.update({v: [obj]})

    # Sort the keys, which are the actual counter values and return the sorted list of objects
    return [v for k in sorted(list(count_dict.keys()), reverse=r) for v in count_dict[k]]


def convert_to_list(obj):
    """Intended for API calls that return a container (dict) for single entry lists of containers. Depending on the type
    of the passed object, returns:
    obj         Return
    None        List with no members
    list        The same passed object, obj, is returned - NOT A COPY
    tuple       Tuple copied to a list
    All else    List with the passed obj as the only member

    :param obj: Object to be converted to list
    :type obj: list, tuple, dict, str, float, int
    :return: Converted list
    :rtype: list
    """
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    elif isinstance(obj, dict):
        if len(obj.keys()) == 0:
            return []
        else:
            return [obj]
    elif isinstance(obj, tuple):
        return list(obj)
    else:
        return [obj]

def sort_ports(obj_list):
    """Sorts a list of port objects by switch, slot, then port number. Note that an ASCII sort doesn't work on s/p
    notation as desired

    :param obj_list: list of PortObj objects - see PortObj - in brcddb.classes.port.PortObj
    :type port_list: list
    :return return_list: Sorted list of port objects from obj_list
    :rtype: list
    """
    return_list = []
    w = {}              # Working dictionary of switch, slots, then ports

    # Split everything out into seperate buckets for switch, slot and port.
    for port_obj in obj_list:
        switch_obj = port_obj.r_switch_obj()
        switch = switch_obj.r_obj_key()
        if switch_obj.r_get('switch-user-friendly-name') is not None:
            switch = switch_obj.r_get('switch-user-friendly-name') + switch
        if switch not in w:
            w.update({switch: {}})
        t = port_obj.r_obj_key().split('/')
        if int(t[0]) not in w[switch]:
            w[switch].update({int(t[0]): {}})
        w[switch][int(t[0])].update({int(t[1]): port_obj})

    # Now sort them and create the return list
    switch_list = list(w.keys())
    switch_list.sort()
    for switch in switch_list:
        slot_list = list(w[switch].keys())
        slot_list.sort()
        for slot in slot_list:
            port_list = list(w[switch][slot].keys())
            port_list.sort()
            for port in port_list:
                return_list.append(w[switch][slot][port])

    return return_list


def remove_duplicates(obj_list):
    """Removes duplicate list entries from a list

    :param obj_list: List of class objects.
    :type obj_list: list, tuple
    :return return_list: Input list less duplicates
    :rtype: list
    """
    seen = set()
    seen_add = seen.add # seen.add isn't changing so making it local makes the next line more effecient
    return [obj for obj in obj_list if not (obj in seen or seen_add(obj))]


def is_wwn(wwn):
    """Validates that the wwn is a properly formed WWN

    :param wwn: WWN
    :type wwn: str
    :return: True - wwn is a valid WWN, False - wwn is not a valid WWN
    :rtype: bool
    """
    if len(wwn) != 23:
        return False
    if wwn[0] == '0':
        return False
    i = 0
    wwn_chars = ''
    for c in wwn:
        if i in (0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22):
            wwn_chars += c
        else:
            if c != ':':
                return False
        i += 1
    if not re.match("^[A-Fa-f0-9]*$", wwn_chars):
        return False
    return True


def is_valid_zone_name(zone_obj):
    """Checks to ensure that a zone object meets the FOS zone object naming convention rules

    :param zone_obj: Zone, zone configuration, or alias name
    :type zone_obj: str
    :return: True if zone object name is a valid format
    :rtype: bool
    """
    global _MAX_ZONE_NAME_LEN

    if zone_obj is None:
        return False
    if len(zone_obj) < 2 or len(zone_obj) > _MAX_ZONE_NAME_LEN:  # At least 1 character and less than or = 64
        return False
    if not re.match("^[A-Za-z0-9]*$", zone_obj[0:1]):
        return False
    if not re.match("^[A-Za-z0-9_-]*$", zone_obj[1:]):
        return False
    return True


def _login_to_port_map(fab_obj):
    """Creates a map of logins to the port where the login occured for build_login_port_map()

    :param fab_obj: Fabric Object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :return map: Dictionary - key: login WWN, value: port object
    :rtype map: dict
    :return base: List of NPIV base port logins
    :rtype base: list
    """
    port_to_wwn_map = {}
    base_list = []
    for port_obj in fab_obj.r_port_objects():
        nl = list(port_obj.r_login_keys())
        if len(nl) > 1:
            base_list.append(nl[0])
        for wwn in nl:
            port_to_wwn_map.update({wwn: port_obj})
    return port_to_wwn_map, base_list


def build_login_port_map(proj_obj):
    """Creates a map of logins to the port where the login occured for each fabric and adds it to the fabric object

    :param proj_obj: Project Object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for fab_obj in proj_obj.r_fabric_objects():
        fab_obj.s_base_logins(None)
        fab_obj.s_port_map(None)
        port_map, base_logins = _login_to_port_map(fab_obj)
        fab_obj.s_port_map(port_map)
        fab_obj.s_base_logins(base_logins)


# Case statements for add_maps_groups()
def _fc_port(switch_obj, group):
    """Adds the MAPS group to the port

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param group: MAPS group
    :type group: dict
    """
    name = group.get('name')
    for port in convert_to_list(group.get('members').get('member')):
        port_obj = switch_obj.r_port_obj(port)
        if port_obj is not None:
            port_obj.s_add_maps_fc_port_group(name)

def _sfp(switch_obj, group):
    """Adds the MAPS group to the port

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param group: MAPS group
    :type group: dict
    """
    name = group.get('name')
    for port in convert_to_list(group.get('members').get('member')):
        port_obj = switch_obj.r_port_obj(port)
        if port_obj is not None:
            port_obj.s_add_maps_sfp_group(name)

# Case tables used by add_maps_groups()
_maps_group_type = {
    'fc-port': _fc_port,
    'sfp': _sfp,
}


def add_maps_groups(proj_obj):
    """Adds the associated maps group to each object. Limited to port objects. Additional objects a future.

    :param proj_obj: Project Object
    :type proj_obj: brcddb.classes.project.ProjectObj
    """
    for switch_obj in proj_obj.r_switch_objects():
        active_rule_list = convert_to_list(get_key_val(switch_obj.r_active_maps_policy(), 'rule-list/rule'))
        for group in convert_to_list(switch_obj.r_get('brocade-maps/group')):
            switch_obj.s_add_group(group)
        for rule in convert_to_list(switch_obj.r_get('brocade-maps/rule')):
            if rule.get('name') in active_rule_list:
                switch_obj.s_add_rule(rule)
        for group in switch_obj.r_active_group_objects():
            try:
                _maps_group_type[group.get('group-type')](switch_obj, group)
            except:
                pass


def global_port_list(fabric_objects, wwn_list):
    """Looks through a list of fabrics for logins in a list of WWNs and returns a list of the associated port objects

    :param fabric_objects: List of fabric objects (brcddb.classes.fabric.FabricObj)
    :type fabric_objects: list, tuple
    :param wwn_list: Login WWN or list of login WWNs to find the port objects for
    :type wwn_list: None, str, list, tuple
    :return: List of port objects (brcddb.classes.port.PortObj)
    :rtype: list
    """
    port_list = []
    for fab_obj in fabric_objects:
        port_list.extend([fab_obj.r_port_obj(wwn) for wwn in convert_to_list(wwn_list)
                          if fab_obj.r_port_obj(wwn) is not None])
    return port_list


def has_alert(obj, al_num, key, p0, p1):
    """Determines if an alert has already been added to an object

    :param obj: Object
    :type obj: Any object in brcddb.classes
    :param key: Alert key
    :type keys: str
    :param p0: Alert parameter p0
    :type p0: str
    :param p1: Alert parameter p1
    :type p2: str
    :return: True if alert already exists in object
    :rtype: bool
    """
    for alert_obj in obj.r_alert_objects():
        if alert_obj.alert_num() == al_num and alert_obj.key() == key and alert_obj.p0() == p0 and alert_obj.p1() == p1:
            return True
    return False


def slot_port(port):
    """Seperate the slot and port number from a s/p port reference. Can also be used to validate s/p notation.

    :param port: Port number in s/p notation
    :type port: str
    :return slot: Slot number. None if port is not in standard s/p notation
    :rtype slot: int, None
    :return port: Port number. None if port is not in standard s/p notation
    :rtype port: int, None
    """
    l = port.split('/')
    if len(l) == 1:
        l.insert(0, '0')
    if len(l) != 2:
        return None, None
    try:
        s = int(l[0])
        p = int(l[1])
    except:
        return None, None
    if s in range(0, 13) and p in range(0, 64):
        return s, p
    return None, None


##################################################################
#
#            Method and tables to parse CLI
#
###################################################################

# Convert CLI commands to the c-type for brcddb.apps.zone
c_type_conv = {
    'aliadd': 'alias-add',
    'alicreate': 'alias-create',
    'alidelete': 'alias-delete',
    'aliremove': 'alias-remove',
    'cfgadd': 'cfg-add',
    'cfgclear': 'cfg-clear',
    'cfgcreate': 'cfg-create',
    'cfgdelete': 'cfg-delete',
    # 'cfgdisable': None,  # Not supported
    'cfgenable': 'cfg-enable',
    'cfgremove': 'cfg-remove',
    'cfgsave': 'cfg-save',
    'defzone': 'defzone',
    'zoneadd': 'zone-add',
    'zonecleanup': 'zone-cleanup',
    'zonecreate': 'zone-create',
    'zonedelete': 'zone-delete',
    'zoneobjectcopy': 'zone-object-copy',
    # 'zoneobjectexpunge': None,  # Not supported
    'zoneobjectrename': 'zone-object-rename',  # Not supported
    # 'zoneobjectreplace': None,  # Not supported
    'zoneremove': 'zone-remove',
}
# It's not uncommon for customers with CLI zone scripts to have show commands in the script
skip_commands = ('alishow', 'cfgactvshow', 'cfgshow', 'cfgtransshow', 'configshow', 'zoneshow')

_state_cmd = 0
_state_operand = _state_cmd + 1
_state_principal = _state_operand + 1
_state_members = _state_principal + 1


def parse_cli(file_buf):
    """Conditions each line read from the file of FOS commands into a list of dictionaries for use with send_zoning()

    WARNING: This is a quick and dirty method that only works on WWN and alias zones. It will not work with d,i
    Ignores all extraneous white space, comments, and null lines. Each dict contains:
    +--------+------------+-----------------------------------------------------------------------------------------+
    | key    | Value Type | Value Description                                                                       |
    +========+============+=========================================================================================+
    | 'c'    | str        | Command                                                                                 |
    +--------+------------+-----------------------------------------------------------------------------------------+
    | 'o'    | str        | Operand                                                                                 |
    +--------+------------+-----------------------------------------------------------------------------------------+
    | 'p0'   | list       | Parameters. For all zone operations, these are the members. For peer zones, these are   |
    |        |            | the principal members.                                                                  |
    +--------+------------+-----------------------------------------------------------------------------------------+
    | 'p1'   | list       | Similar to 'p0'. Only used for peer zones. These are the non-principal members          |
    +--------+------------+-----------------------------------------------------------------------------------------+
    | 'peer' | bool       | If true, zone is a peer zone.                                                           |
    +--------+------------+-----------------------------------------------------------------------------------------+

    In order to preserve the original line numbering, values in dict are None for blank lines
    :param file_buf: List of lines (str) read from input file with FOS  zone commands (CLI)
    :type file_buf: list
    :return: List of commands parsed into the aforementioned dictionary
    :rtype: list
    """
    cond_input = []
    for buf in file_buf:
        mod_line = buf[:buf.find('#')] if buf.find('#') >= 0 else buf
        if not _DEBUG_FICON:
            # Replace double quotes and commas with a space, remove all double space, and trim
            # DOES NOT WORK FOR d,i ZONES
            mod_line = re.sub('\s+', ' ', mod_line.replace(',', ' ').strip())
        # remove all spaces within double quotes
        t = mod_line.split('"')
        mod_line = ''
        for i in range(len(t)):
            if i % 2 != 0:  # The odd indices are what's inside double quotes
                mod_line += re.sub('\s+', '', t[i])
            else:
                mod_line += t[i]
        t = mod_line.split(' ') if len(mod_line) > 0 else []
        for i in range(len(t)):
            t[i] = t[i].replace('"', '')
        c = None
        o = None
        p0 = None
        p1 = None
        peer = False
        flag = False  # Use this to flag malformed command lines
        state = _state_cmd
        for p_buf in t:
            if state == _state_cmd:
                c = p_buf
                state = _state_operand
            elif state == _state_operand:
                if '--peer' in p_buf:
                    peer = True
                else:
                    o = p_buf
                    state = _state_members
            elif state == _state_members:
                if '-members' in p_buf:
                    if not peer:
                        flag = True
                        break
                    continue
                elif '-principal' in p_buf:
                    if not peer:
                        flag = True
                        break
                    state = _state_principal
                else:
                    p0 = p_buf.split(';')
            elif state == _state_principal:
                p1 = p_buf.split(';')
                state = _state_members
        if c is None:
            cond_input.append({})
        elif c in skip_commands:
            cond_input.append({})
        elif flag:
            if c in c_type_conv:
                # 'malformed' will be reported as an unsupported command, but with everything else in the user error
                # message, that's good enough to let the user know what's going on
                cond_input.append({'c-type': 'malformed', 'operand': o, 'p0': p0, 'p1': p1, 'peer': peer})
        else:
            if c in c_type_conv:
                cond_input.append({'c-type': c_type_conv[c], 'operand': o, 'p0': p0, 'p1': p1, 'peer': peer})
            else:
                cond_input.append({'c-type': c + ': Unsupported', 'operand': o, 'p0': p0, 'p1': p1, 'peer': peer})
    return cond_input


def is_di(di):
    """Determines if an str is a d,i pair (used in zoning)

    :param di: Domain index pair as a "d,i" str
    :type di: str
    :return: True - di looks like a d,i pair. Otherwise False.
    :rtype: bool
    """
    buf = di
    buf.replace(' ', '')
    l = buf.split(',')
    if len(l) != 2:
        return False
    try:
        temp = [int(x) for x in l]
        return True
    except:
        return False


def remove_duplicate_space(buf):
    """Removes duplicate spaces

    :param buf: Text to remove duplicate spaces from
    :type buf: str
    :return: Input text with duplicate spaces removed
    :rtype: str
    """
    buf = 'x' + buf
    l = [buf[i] for i in range(1, len(buf)) if buf[i] != ' ' or (buf[i] == ' ' and buf[i-1] != ' ')]
    return ''.join(l)


def str_to_num(buf):
    """Converts an str to an int if it can be represented as an int, otherwise float. 12.0 is returned as a float.

    :param buf: Text to convert to float or int
    :type buf: str
    :return: str converted to number. If the input cannot be converted to a number, it is returned as passed in.
    :rtype: str, float, int
    """
    if isinstance(buf, str):
        if '.' in buf:
            try:
                num = float(buf)
            except ValueError:
                return buf
            else:
                return num
        else:
            try:
                num = int(buf)
            except ValueError:
                return buf
            else:
                return num
    else:
        return buf


def paren_content(buf, p_remove=False):
    """Returns the contents of a string within matching parenthesis. First character must be '('

    :param buf: String to find text within matching parenthesis
    :type buf: str
    :param p_remove: If True, remove the leading and trailing parenthesis
    :return p_text: Text within matching parenthesis
    :rtype p_text: str
    :return x_buf: Remaind of buf after matching parenthesis have been found
    :rtype x_buf: str
    """
    p_count = 0
    r_buf = []
    buf_len = len(buf)
    if len(buf) > 1 and buf[0] == '(':
        p_count += 1  # The first character must be (
        r_buf.append('(')
        for c in buf[1:]:
            r_buf.append(c)
            if c == '(':
                p_count += 1
            elif c == ')':
                p_count -= 1
                if p_count == 0:
                    break

    if p_count != 0:
        brcdapi_log.exception('Input string does not have matching parenthesis:\n' + buf, True)
        r_buf = []
    remainder = '' if len(buf) - len(r_buf) < 1 else buf[len(r_buf):]
    if len(r_buf) > 2 and p_remove:
        r_buf.pop()
        r_buf.pop(0)


    return ''.join(r_buf), remainder
