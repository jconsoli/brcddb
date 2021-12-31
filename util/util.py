# Copyright 2020, 2021 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.util.util` - Utility functions for the brcddb libraries

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-7   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 14 May 2021   | Handled None object in get_key_val()                                              |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.0     | 18 May 2021   | Removed reliance on brcddb.util.search which was causing a circular import issue. |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.1     | 17 Jul 2021   | Added: int_list_to_range(), remove_none()                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.2     | 21 Aug 2021   | Added zone_cli()                                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.3     | 14 Nov 2021   | Made _login_to_port_map() public, changed to login_to_port_map()                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.4     | 31 Dec 2021   | Removed port_obj_for_wwn() and made all "except:" explicit                        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '31 Dec 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.1.4'

import re
import datetime
import brcdapi.log as brcdapi_log
import brcddb.classes.util as brcddb_class_util

_DEBUG_FICON = False  # Intended for lab use only. Few, if any, will use this to zone a FICON switch
_MAX_ZONE_NAME_LEN = 64
error_asserted = False  # Set True any time an error is encountered. Use for debug only.
_MAX_LINE_COUNT = 20  # Maximum number of lines before inserting a space when generating CLI
_MAX_MEM = 3  # Maximum number of members to add to a zone object in a single FOS command (CLI)

# ReGex matching
non_decimal = re.compile(r'[^\d.]+')
decimal = re.compile(r'[\d.]+')  # Use: decimal.sub('', '1.4G') returns 'G'
zone_notes = re.compile(r'[~*#+^]')
ishex = re.compile(r'^[A-Fa-f0-9]*$')  # use: if ishex.match(hex_str) returns True if hex_str represents a hex number
valid_file_name = re.compile(r'\w[ -]')  # use: good_file_name = valid_file_name.sub('_', bad_file_name)
date_to_space = re.compile(r'[-/,]')  # Used to convert special characters in data formats to a space

multiplier = dict(k=1000, K=1000, m=1000000, M=1000000, g=1000000000, G=1000000000, t=1000000000000, T=1000000000000)
_month_to_num = dict(
    jan=1, january=1,
    feb=2, february=2,
    mar=3, march=3,
    apr=4, april=4,
    may=5,
    jun=6, june=6,
    jul=7, july=7,
    aug=8, august=8,
    sep=9, september=9,
    oct=10, october=10,
    nov=11, november=11,
    dec=12, december=12,
)
_tz_utc_offset = dict(est=-4, edt=-5, cst=-5, cdt=-6, pst=-6, pdt=-7)


def ports_for_login(login_list):
    """Returns a list of port objects associated with a list of login objects.

    :param login_list: list of login objects, brcddb.classes.login.LoginObj
    :type login_list: list, tuple
    :return port_list: List of port objects, PortObj, associated with the login objects in login_list
    :rtype: list
    """
    # If it's a SIM port, the WWN is in the name server but not 'neighbor' so check before tyring to append
    return [login_obj.r_port_obj() for login_obj in login_list if login_obj.r_port_obj() is not None]


def port_obj_for_wwn(objx, wwn):
    """Returns the port object for a switch port WWN.

    Programmers Tip: The need to know a port WWN is rare. Although the key for all other objects is the WWN, with
    ports I used the port number because virtual ports do not have a WWN and may not have an index. Furthermore, the WWN
    for the switch port is not prevalent. The only time I needed to associate a port object with a port WWN is with
    E-Ports because the neighbor in that case is the port WWN of the port in the ISLed switch.

    This method is extremely inefficient but since E-Port look up in this manner is infrequent, it's good enough. If you
    find yourself in a situation where you need to look up a port object from a port WWN often, you should build a
    table, similar to brcddb_project.build_xref(), for efficient look ups.

    :param objx: A brcddb class object that has a method port_objects()
    :type objx: ProjectObj, FabricObj, SwitchObj, ChassisObj
    :param wwn: WWN of a switch port
    :type wwn: str
    :return: Port Object. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    for port_obj in objx.r_port_objects():
        port_wwn = port_obj.r_get('wwn')
        if isinstance(port_wwn, str) and port_wwn == wwn:
            return port_obj
    return None


def get_key_val(obj, keys):
    """Spins through a list of keys separated by a '/' and returns the value associated with the last key.

    :param obj: Starting point in the object
    :type obj: dict, ProjectObj, FabricObj, SwitchObj, PortObj, ZoneCfgObj, ZoneObj, PortObj, LoginObj
    :param keys: Sting of keys to look through
    :type keys: str
    :return: Value associated with last key. None if not found
    :rtype: int, float, str, list, tuple, dict
    """
    global error_asserted

    if obj is None:
        return None  # Saves the calling method of having to determine they are working on a valid object
    if hasattr(obj, 'r_get') and callable(obj.r_get):
        return obj.r_get(keys)
    if not isinstance(obj, dict):
        brcdapi_log.exception('Object type, ' + str(type(obj)) + ', not a dict or brcddb object,', True)
        error_asserted = True
        return None

    key_l = keys.split('/')
    if len(key_l) == 0:
        return None
    last_key = key_l[len(key_l)-1]
    v = obj
    for k in key_l:
        if isinstance(v, dict):
            v = v.get(k)
        elif k != last_key:
            brcdapi_log.exception('Object type, ' + str(type(v)) + ', for ' + k + ', in ' + keys +
                                  ' not a dict or brcddb object ', True)
            error_asserted = True
            return None
    return v


def sort_obj_num(obj_list, key, r=False, h=False):
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
    # count_dict: key is the count (value of dict item whose key is the input counter). Value is a list of port objects
    # whose counter matches this count
    count_dict = dict()

    for obj in obj_list:
        # Get the object to test against
        v = get_key_val(obj, key)
        if v is not None and h:
            v = int(v, 16)
        if isinstance(v, (int, float)):
            try:
                count_dict[v].append(obj)
            except KeyError:
                count_dict.update({v: [obj]})

    # Sort the keys, which are the actual counter values and return the sorted list of objects
    return [v for k in sorted(list(count_dict.keys()), reverse=r) for v in count_dict[k]]


def convert_to_list(obj):
    """Depending on the type of the passed object, returns:

    obj         Return
    None        Empty list
    list        The same passed object, obj, is returned - NOT A COPY
    tuple       Tuple copied to a list
    All else    List with the passed obj as the only member

    :param obj: Object to be converted to list
    :type obj: list, tuple, dict, str, float, int
    :return: Converted list
    :rtype: list
    """
    if obj is None:
        return list()
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return list() if len(obj.keys()) == 0 else [obj]
    if isinstance(obj, tuple):
        return list(obj)
    else:
        return [obj]


def sp_port_sort(port_list):
    """Sorts a list of port objects by slot then port number.

    :param port_list: list of ports in s/p notation
    :type port_list: list
    :return return_list: Sorted list of ports
    :rtype: list
    """
    wd = dict()  # Working dictionary of slots which contains a dictionary of ports
    for port in port_list:
        t = port.split('/')
        if int(t[0]) not in wd:
            wd.update({int(t[0]): dict()})
        wd[int(t[0])].update({int(t[1]): port})

    # Now sort them and create the return list
    rl = list()
    slot_l = list(wd.keys())
    slot_l.sort()
    for slot in slot_l:
        port_l = list(wd[slot].keys())
        port_l.sort()
        rl.extend([wd[slot][port] for port in port_l])

    return rl


def sort_ports(port_obj_list):
    """Sorts a list of port objects by switch, slot, then port number. Note that an ASCII sort doesn't work on s/p
    notation as desired

    :param port_obj_list: list of PortObj objects - see PortObj - in brcddb.classes.port.PortObj
    :type port_obj_list: list
    :return return_list: Sorted list of port objects from obj_list
    :rtype: list
    """
    if len(port_obj_list) == 0:
        return list()
    proj_obj = port_obj_list[0].r_project_obj()  # Assume the same project for all ports

    # Sort by switch
    wd = dict()
    for port_obj in port_obj_list:
        switch = port_obj.r_switch_key()
        if switch not in wd:
            wd.update({switch: list()})
        wd[switch].append(port_obj.r_obj_key())
    sl = list(wd.keys())
    sl.sort()

    # Build the return list, sorted by port
    rl = list()
    for switch in sl:
        switch_obj = proj_obj.r_switch_obj(switch)
        rl.extend([switch_obj.r_port_obj(port) for port in sp_port_sort(wd[switch])])

    return rl


def remove_duplicates(obj_list):
    """Removes duplicate list entries from a list

    :param obj_list: List of class objects.
    :type obj_list: list, tuple
    :return return_list: Input list less duplicates
    :rtype: list
    """
    seen = set()
    seen_add = seen.add  # seen.add isn't changing so making it local makes the next line more efficient
    return [obj for obj in obj_list if not (obj in seen or seen_add(obj))]


def remove_none(obj_list):
    """Removes None items from a list

    :param obj_list: List of items.
    :type obj_list: list, tuple
    :return return_list: Input list less items that were None
    :rtype: list
    """
    return [obj for obj in obj_list if obj is not None]


def is_wwn(wwn, full_check=True):
    """Validates that the wwn is a properly formed WWN

    :param wwn: WWN
    :type wwn: str
    :param full_check: When True, the first byte cannot be 0
    :return: True - wwn is a valid WWN, False - wwn is not a valid WWN
    :rtype: bool
    """
    if not isinstance(wwn, str) or len(wwn) != 23 or (wwn[0] == '0' and full_check):
        return False
    clean_wwn = list()
    for i in range(0, len(wwn)):
        if i in (2, 5, 8, 11, 14, 17, 20):
            if wwn[i] != ':':
                return False
        else:
            clean_wwn.append(wwn[i])

    return True if ishex.match(''.join(clean_wwn)) else False


def is_valid_zone_name(zone_obj):
    """Checks to ensure that a zone object meets the FOS zone object naming convention rules

    :param zone_obj: Zone, zone configuration, or alias name
    :type zone_obj: str
    :return: True if zone object name is a valid format, otherwise False
    :rtype: bool
    """
    global _MAX_ZONE_NAME_LEN

    if zone_obj is None:
        return False
    if len(zone_obj) < 2 or len(zone_obj) > _MAX_ZONE_NAME_LEN:  # At least 1 character and less than or = 64
        return False
    if not re.match("^[A-Za-z0-9]*$", zone_obj[0:1]):  # Must begin with letter or number
        return False
    if not re.match("^[A-Za-z0-9_-]*$", zone_obj[1:]):  # Remaining characters must be letters, numbers, '_', or '-'
        return False
    return True


def login_to_port_map(fab_obj):
    """Creates a map of logins to the port where the login occured for build_login_port_map()

    :param fab_obj: Fabric Object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :return map: Dictionary - key: login WWN, value: port object
    :rtype map: dict
    :return base: List of NPIV base port logins
    :rtype base: list
    """
    port_to_wwn_map = dict()
    base_list = list()
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
        fab_obj.s_base_logins(None)  # None clears the base logins
        fab_obj.s_port_map(None)  # None clears the port map
        port_map, base_logins = login_to_port_map(fab_obj)  # Get a fresh base login and port map
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


def _null(switch_obj, group):
    """MAPS groups not yet implemented

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param group: MAPS group
    :type group: dict
    """
    if isinstance(group, dict) and group.get('name') is not None:
        return
    brcdapi_log.exception('Invalid MAPS group', True)


# Case tables used by add_maps_groups()
_maps_group_type = {
    'fc-port': _fc_port,
    'sfp': _sfp,
    'asic': _null,
    'backend-port': _null,
    'fan': _null,
    'chassis': _null,
    'device-pid': _null,
    'power-supply': _null,
    'temperature-sensor': _null,
    'certificate': _null,
    'switch': _null,
    'flow': _null,
    'circuit': _null,
    'circuit-qos': _null,
    'DP': _null,
    'ethernet-port': _null,
    'ge-port': _null,
    'blade': _null,
    'tunnel': _null,
    'tunnel-qos': _null,
    'wwn': _null,
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
                _maps_group_type[group['group-type']](switch_obj, group)
            except KeyError:  # Log it, but don't pester the operator
                brcdapi_log.log('Unknown group type ' + str(group.get('group-type')))
            except ValueError:  # Log it and let the operator know but keep chugging
                buf = 'Invalid MAPS group for switch ' + switch_obj.r_obj_key() + '. group-type: ' +\
                      str(group.get('group-type'))
                brcdapi_log.exception(buf, True)


def global_port_list(fabric_objects, wwn_list):
    """Looks through a list of fabrics for logins in a list of WWNs and returns a list of the associated port objects

    :param fabric_objects: List of fabric objects (brcddb.classes.fabric.FabricObj)
    :type fabric_objects: list, tuple
    :param wwn_list: Login WWN or list of login WWNs to find the port objects for
    :type wwn_list: None, str, list, tuple
    :return: List of port objects (brcddb.classes.port.PortObj)
    :rtype: list
    """
    port_list = list()
    for fab_obj in fabric_objects:
        port_list.extend([fab_obj.r_port_obj(wwn) for wwn in convert_to_list(wwn_list)
                          if fab_obj.r_port_obj(wwn) is not None])
    return port_list


def has_alert(obj, al_num, key, p0, p1):
    """Determines if an alert has already been added to an object

    :param obj: Object
    :type obj: Any object in brcddb.classes
    :param al_num: Alert number
    :type al_num: int
    :param key: Alert key
    :type key: str
    :param p0: Alert parameter p0
    :type p0: str, None
    :param p1: Alert parameter p1
    :type p1: str, None
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
    temp_l = port.split('/')
    if len(temp_l) == 1:
        temp_l.insert(0, '0')
    if len(temp_l) != 2:
        return None, None
    try:
        s = int(temp_l[0])
        p = int(temp_l[1])
    except (ValueError, IndexError):
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
c_type_conv = dict(
    aliadd='alias-add',
    alicreate='alias-create',
    alidelete='alias-delete',
    aliremove='alias-remove',
    cfgadd='cfg-add',
    cfgclear='cfg-clear',
    cfgcreate='cfg-create',
    cfgdelete='cfg-delete',
    # cfgdisable=None,  # Not supported
    cfgenable='cfg-enable',
    cfgremove='cfg-remove',
    cfgsave='cfg-save',
    defzone='defzone',
    zoneadd='zone-add',
    zonecleanup='zone-cleanup',
    zonecreate='zone-create',
    zonedelete='zone-delete',
    zoneobjectcopy='zone-object-copy',
    # zoneobjectexpunge=None,  # Not supported
    zoneobjectrename='zone-object-rename',  # Not supported
    # zoneobjectreplace=None,  # Not supported
    zoneremove='zone-remove',
)
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
    cond_input = list()
    for buf in file_buf:
        mod_line = buf[:buf.find('#')] if buf.find('#') >= 0 else buf
        if not _DEBUG_FICON:
            # Replace double quotes and commas with a space, remove all double space, and trim
            # DOES NOT WORK FOR d,i ZONES
            mod_line = re.sub('\\s+', ' ', mod_line.replace(',', ' ').strip())
        # remove all spaces within double quotes
        temp_l = mod_line.split('"')
        mod_line = ''
        for i in range(len(temp_l)):
            if i % 2 != 0:  # The odd indices are what's inside double quotes
                mod_line += re.sub('\\s+', '', temp_l[i])
            else:
                mod_line += temp_l[i]
        temp_l = mod_line.split(' ') if len(mod_line) > 0 else list()
        for i in range(len(temp_l)):
            temp_l[i] = temp_l[i].replace('"', '')
        c = None
        o = None
        p0 = None
        p1 = None
        peer = False
        flag = False  # Use this to flag malformed command lines
        state = _state_cmd
        for p_buf in temp_l:
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
            cond_input.append(dict())
        elif c in skip_commands:
            cond_input.append(dict())
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
    try:
        temp = [int(x) for x in di.replace(' ', '').split(',')]
        return True if len(temp) == 2 else False
    except ValueError:
        return False


def remove_duplicate_space(buf):
    """Removes duplicate spaces

    :param buf: Text to remove duplicate spaces from
    :type buf: str
    :return: Input text with duplicate spaces removed
    :rtype: str
    """
    buf = 'x' + buf
    temp_l = [buf[i] for i in range(1, len(buf)) if buf[i] != ' ' or (buf[i] == ' ' and buf[i-1] != ' ')]
    return ''.join(temp_l)


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
    return buf


def paren_content(buf, p_remove=False):
    """Returns the contents of a string within matching parenthesis. First character must be '('

    :param buf: String to find text within matching parenthesis
    :type buf: str
    :param p_remove: If True, remove the leading and trailing parenthesis
    :return p_text: Text within matching parenthesis
    :rtype p_text: str
    :return x_buf: Remainder of buf after matching parenthesis have been found
    :rtype x_buf: str
    """
    global error_asserted

    p_count = 0
    r_buf = list()
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
        error_asserted = True
        r_buf = list()
    remainder = '' if len(buf) - len(r_buf) < 1 else buf[len(r_buf):]
    if len(r_buf) > 2 and p_remove:
        r_buf.pop()
        r_buf.pop(0)

    return ''.join(r_buf), remainder


def add_to_obj(obj, k, v):
    """Adds a key value pair to obj using '/' notation in the key. If the key already exists, it is overwritten.

    :param obj: Dictionary or brcddb.class object the key value pair is to be added to
    :type obj: dict
    :param k: The key
    :type k: str
    :param v: Value associated with the key.
    :type v: int, str, list, dict
    """
    global error_asserted

    if not isinstance(k, str):
        brcdapi_log.exception('Invalid key. Expected type str, received type ' + str(type(k)), True)
        error_asserted = True
        return
    key_list = k.split('/')
    if isinstance(obj, dict):
        if len(key_list) == 1:
            obj.update({k: v})
            return
        key = key_list.pop(0)
        d = obj.get(key)
        if d is None:
            d = dict()
            obj.update({key: d})
        add_to_obj(d, '/'.join(key_list), v)
    elif brcddb_class_util.get_simple_class_type(obj) is None:
        brcdapi_log.exception('Invalid object type: ' + str(type(obj)) + '. k = ' + k + ', v type: ' + str(type(v)),
                              True)
        error_asserted = True
    else:
        key = key_list.pop(0)
        if len(key_list) == 0:
            obj.s_new_key(key, v, True)
            return
        r_obj = obj.r_get(key)
        if r_obj is None:
            r_obj = dict()
            obj.s_new_key(key, r_obj)
        add_to_obj(r_obj, '/'.join(key_list), v)


def get_struct_from_obj(obj, k):
    """Returns a Python data structure for a key using / notation in obj with everything not in the key, k, filtered out

    :param obj: Dictionary the key is for
    :type obj: dict
    :param k: The key
    :type k: str
    :return: Filtered data structure. None is returned if the key was not found
    :rtype: int, str, list, dict, None
    """
    global error_asserted

    if not isinstance(k, str) or obj is None or len(k) == 0:
        return None
    r_obj = dict()
    w_obj = r_obj
    kl = k.split('/')
    k0 = None
    v0 = obj
    while len(kl) > 0:
        k0 = kl.pop(0)
        v0 = v0.get(k0) if isinstance(v0, dict) else v0.r_get(k0)
        if v0 is None:
            return None  # The key was not found if we get here
        if len(kl) > 0:
            if isinstance(v0, dict):
                w_obj.update({k0: dict()})
                w_obj = w_obj[k0]
            else:
                brcdapi_log.exception('Expected type dict for ' + k0 + ' in ' + k + '. Actual type: ' + str(type(k0)),
                                      True)
                error_asserted = True
    if k0 is not None:
        w_obj.update({k0: v0})

    return r_obj


def get_from_obj(obj, k):
    """Returns the value associated with a key in / notation for a dict or brcddb.class object

    :param obj: Dictionary the key is for
    :type obj: dict
    :param k: The key
    :type k: str
    :return: Value associated with the key. None is returned if the key was not found
    :rtype: int, str, list, dict, None
    """
    global error_asserted

    if isinstance(obj, dict):
        v0 = get_struct_from_obj(obj, k)
        if v0 is None:
            return None
        kl = k.split('/')
        while len(kl) > 0:
            k0 = kl.pop(0)
            v0 = v0.get(k0)
            if v0 is None:
                return None  # The key was not found if we get here
        return v0
    elif brcddb_class_util.get_simple_class_type(obj) is None:
        brcdapi_log.exception('Invalid object type.', True)
        error_asserted = True
    else:
        return obj.r_get(k)


def resolve_multiplier(val):
    """Converts an str representation of a number. Supported conversions are k, m,, g, or t

    :param val: Dictionary the key is for
    :type val: str
    :return: val as a number. Returns None if
    :rtype: float, None
    """
    if isinstance(val, str):
        try:
            mod_val = float(non_decimal.sub('', val))
            mult = decimal.sub('', val)
            if len(mult) > 0:
                return mod_val * multiplier[mult]
            return mod_val
        except ValueError:
            return None
    return val


def dBm_to_absolute(val, r=1):
    """Converts a number in dBm to it's value

    :param val: dBm value
    :type val: str, float
    :param r: Number of digits to the right of the decimal point to round off to
    :type r: int
    :return: val converted to it's absolute value. None if val cannot be converted to a float.
    :rtype: float, None
    """
    try:
        return round((10 ** (float(val)/10)) * 1000, r)
    except ValueError:
        pass
    return None


def int_list_to_range(num_list):
    """Converts a list of integers to ranges as text. For example: 0, 1, 2, 5, 6, 9 is returned as:

    0:  '0-2'
    1:  '5-6'
    2:  '9'

    :param num_list: List of numeric values, int or float
    :type num_list: list
    :return: List of str as described above
    :rtype: list
    """
    rl = list()
    range_l = list()
    for i in num_list:
        ri = len(range_l)
        if ri > 0 and i != range_l[ri-1] + 1:
            rl.append(str(range_l[0]) if ri == 1 else str(range_l[0]) + '-' + str(range_l[ri-1]))
            range_l = list()
        range_l.append(i)
    ri = len(range_l)
    if ri > 0:
        rl.append(str(range_l[0]) if ri == 1 else str(range_l[0]) + '-' + str(range_l[ri-1]))

    return rl


def zone_cli(fab_obj, filter_fab_obj=None):
    """Creates CLI commands for fabric zoning

    :param fab_obj: Fabric object whose zoning information is to be converted to CLI
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param filter_fab_obj: Output does not include CLI for zones in this object. Useful for zone merging.
    :type filter_fab_obj: brcddb.classes.fabric.FabricObj
    :return: List of CLI commands
    :rtype: list
    """
    global _MAX_LINE_COUNT, _MAX_MEM

    buf = fab_obj.r_obj_key() if filter_fab_obj is None else filter_fab_obj.r_obj_key()
    rl = ['', '# Zone CLI commands for: ' + buf]

    # Aliases
    filter_l = list() if filter_fab_obj is None else [str(k) for k in filter_fab_obj.r_alias_keys()]
    rl.extend(['', '# Aliases'])
    line_count = 0
    for obj in fab_obj.r_alias_objects():
        if obj.r_obj_key() in filter_l:
            continue
        mem_l = obj.r_members()
        buf_0 = ' "' + obj.r_obj_key() + '", '
        buf = 'alicreate' + buf_0
        while len(mem_l) > 0:
            line_count = 0 if line_count >= _MAX_LINE_COUNT else line_count + 1
            if line_count == 0:
                rl.append('')
            x = min(len(mem_l), _MAX_MEM)
            rl.append(buf + '"' + ';'.join(mem_l[0:x]) + '"')
            mem_l = mem_l[x:]
            buf = 'aliadd'

    # Zones
    filter_l = list() if filter_fab_obj is None else [str(k) for k in filter_fab_obj.r_zone_keys()]
    rl.extend(['', '# Zones'])
    line_count = 0
    for obj in fab_obj.r_zone_objects():
        if obj.r_obj_key() in filter_l:
            continue

        # All the regular members first
        mem_l = obj.r_members()
        if len(mem_l) > 0:
            buf = 'zonecreate --peerzone "' + obj.r_obj_key() + '" -members ' if obj.r_is_peer() else\
                'zonecreate "' + obj.r_obj_key() + '", '
            while len(mem_l) > 0:
                line_count = 0 if line_count >= _MAX_LINE_COUNT else line_count + 1
                if line_count == 0:
                    rl.append('')
                x = min(len(mem_l), _MAX_MEM)
                rl.append(buf + '"' + ';'.join(mem_l[0:x]) + '"')
                mem_l = mem_l[x:]
                buf = 'zoneadd --peerzone "' + obj.r_obj_key() + '" -members ' if obj.r_is_peer() else \
                    'zoneadd "' + obj.r_obj_key() + '", '
            buf = 'zoneadd --peerzone "' + obj.r_obj_key() + '" -principal ' if obj.r_is_peer() else \
                'zoneadd "' + obj.r_obj_key() + '", '
        else:
            buf = 'zonecreate --peerzone "' + obj.r_obj_key() + '" -principal ' if obj.r_is_peer() else \
                'zonecreate "' + obj.r_obj_key() + '", '

        # Now all the principal members
        mem_l = obj.r_pmembers()  # This will be empty if it's not a peer zone
        while len(mem_l) > 0:
            line_count = 0 if line_count >= _MAX_LINE_COUNT else line_count + 1
            if line_count == 0:
                rl.append('')
            x = min(len(mem_l), _MAX_MEM)
            rl.append(buf + '"' + ';'.join(mem_l[0:x]))
            mem_l = mem_l[x:]

    # Zone configurations
    filter_l = list() if filter_fab_obj is None else [str(k) for k in filter_fab_obj.r_zonecfg_keys()]
    filter_l.append('_effective_zone_cfg')
    rl.extend(['', '# Zone configurations'])
    line_count = 0
    for obj in fab_obj.r_zonecfg_objects():
        if obj.r_obj_key() in filter_l:
            continue
        buf_0 = ' "' + obj.r_obj_key() + '", '
        buf = 'cfgcreate' + buf_0
        mem_l = obj.r_members()
        while len(mem_l) > 0:
            line_count = 0 if line_count >= _MAX_LINE_COUNT else line_count + 1
            if line_count == 0:
                rl.append('')
            x = min(len(mem_l), _MAX_MEM)
            rl.append(buf + '"' + ';'.join(mem_l[0:x]) + '"')
            mem_l = mem_l[x:]
            buf = 'cfgadd' + buf_0

    rl.append('')

    return rl


_fmt_map = {  # Used in date_to_epoch() to determine the indices for each date/time item. cm=True means month is text
    0: dict(y=2, m=0, d=1, t=3, z=4, cm=True),
    1: dict(y=2, m=1, d=0, t=3, z=4, cm=True),
    2: dict(y=2, m=0, d=1, t=3, z=4, cm=False),
    3: dict(y=2, m=1, d=0, t=3, z=4, cm=False),
    4: dict(y=5, m=1, d=2, t=3, z=4, cm=True),
    5: dict(y=4, m=1, d=2, t=3, cm=True),
    6: dict(y=0, m=1, d=2, t=3, cm=False),
}
for _v in _fmt_map.values():  # Add the minimum size the date/time array needs to be for each format
    _v.update(dict(max=max([_i for _i in _v.values() if not isinstance(_i, bool)])))


def date_to_epoch(date_time, fmt=0, utc=False):
    """Converts a date and time string to epoch time. Originally intended for various date formats in FOS.

    WARNING: Time zone to UTC conversion not yet implemented.

    If .msec is not present in any of the below output it is treated as 0.
    +-------+-------------------------------------------------------------------+---------------+
    | fmt   | Sample                                                            | From CLI      |
    +=======+===================================================================+===============+
    |  0    | Dec 31, 2021 hh:mm:ss.msec EDT (May or may not have the comma)    |               |
    +-------+-------------------------------------------------------------------+---------------+
    |  1    | 31 Dec 2021 hh:mm:ss.msec EDT                                     |               |
    +-------+-------------------------------------------------------------------+---------------+
    |  2    | 12/31/2021 hh:mm:ss.msec EDT (or 12-31-2021 or 12 31 2021)        |               |
    +-------+-------------------------------------------------------------------+---------------+
    |  3    | 31/12/2021 hh:mm:ss.msec EDT (or 31-12-2021 or 31 12 2021)        |               |
    +-------+-------------------------------------------------------------------+---------------+
    |  4    | Tue Dec 31 hh:mm:ss.msec EDT 2021                                 | date          |
    +-------+-------------------------------------------------------------------+---------------+
    |  5    | Tue Dec  3 hh:mm:ss 2020                                          | clihistory    |
    +-------+-------------------------------------------------------------------+---------------+
    |  6    | 2021/12/31-hh:mm:ss                                               | errdump       |
    +-------+-------------------------------------------------------------------+---------------+

    :param date_time: Date and time
    :type date_time: str
    :param fmt: Format. See table above
    :type fmt: int
    :param utc: If True, convert time to UTC
    :type utc: bool
    :return: Epoch time. 0 If an error was encountered.
    :rtype: float
    """
    global _month_to_num, _fmt_map

    # Get and validate the input string.
    ml = list()
    ts_l = remove_duplicate_space(date_to_space.sub(' ', date_time)).split(' ')
    if fmt in _fmt_map:
        if len(ts_l) >= _fmt_map[fmt]['max']:
            d = _fmt_map[fmt]

            # Get the year
            buf = ts_l[d['y']]
            year = int(buf) if buf.isnumeric() else None
            if year is None or year < 1970:
                ml.append('year')

            # Get the month
            buf = ts_l[d['m']]
            month = _month_to_num.get(buf.lower()) if d['cm'] else int(buf) if buf.isnumeric() else None
            if month is None or month < 1 or month > 12:
                ml.append('month')

            # Get the day
            buf = ts_l[d['d']]
            day = int(buf) if buf.isnumeric() else None
            if day is None or day < 1 or day > 31:
                ml.append('day')

            # Get the time
            time_l = [int(buf) if buf.isnumeric() else None for buf in ts_l[d['t']].replace('.', ':').split(':')]
            if len(time_l) == 3:
                time_l.append(0)  # Fractional seconds are not always included with the time stamp
            if len(time_l) != 4 or None in time_l:
                ml.append('time')
        else:
            ml.append('date/time stamp')
    else:
        ml.append('format (fmt)')

    if len(ml) > 0:
        brcdapi_log.exception(['Invalid ' + buf + '. date_time: ' + date_time + ' fmt: ' + str(fmt)], True)
        return 0.0

    return (datetime.datetime(year, month, day, time_l[0], time_l[1], time_l[2], time_l[3]) -
            datetime.datetime(1970, 1, 1)).total_seconds()
