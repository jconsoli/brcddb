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
:mod:`brcddb.util.util` - Utility functions for the brcddb libraries

Public Methods::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | ports_for_login       | Returns a list of port objects associated with a list of login objects.               |
    +-----------------------+---------------------------------------------------------------------------------------+
    | port_obj_for_wwn      | Returns the port object for a switch port WWN.                                        |
    +-----------------------+---------------------------------------------------------------------------------------+
    | sort_ports            | Sorts a list of port objects by switch, then slot, then port number.                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | login_to_port_map     | Creates a map of logins to the port where the login occured for                       |
    |                       | build_login_port_map()                                                                |
    +-----------------------+---------------------------------------------------------------------------------------+
    | build_login_port_map  | Creates a map of logins to the port where the login occured for each fabric and adds  |
    |                       | it to the fabric object                                                               |
    +-----------------------+---------------------------------------------------------------------------------------+
    | add_maps_groups       | Adds the associated maps group to each object. Limited to port objects. Additional    |
    |                       | objects a future.                                                                     |
    +-----------------------+---------------------------------------------------------------------------------------+
    | global_port_list      | Looks through a list of fabrics for logins in a list of WWNs and returns a list of    |
    |                       | the associated port objects                                                           |
    +-----------------------+---------------------------------------------------------------------------------------+
    | has_alert             | Determines if an alert has already been added to an object                            |
    +-----------------------+---------------------------------------------------------------------------------------+
    | parse_cli             | Conditions each line read from the file of FOS commands into a list of dictionaries   |
    |                       | for use with send_zoning()                                                            |
    +-----------------------+---------------------------------------------------------------------------------------+
    | add_to_obj            | Adds a key value pair to obj using '/' notation in the key. If the key already        |
    |                       | exists, it is overwritten.                                                            |
    +-----------------------+---------------------------------------------------------------------------------------+
    | get_from_obj          | Returns the value associated with a key in / notation for a dict or brcddb.class      |
    |                       | object                                                                                |
    +-----------------------+---------------------------------------------------------------------------------------+
    | zone_cli              | Creates CLI commands for fabric zoning                                                |
    +-----------------------+---------------------------------------------------------------------------------------+

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
    | 3.1.5     | 28 Apr 2022   | Moved generic utility stuff to brcdapi.                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.6     | 25 Jul 2022   | Deprecated sp_port_sort(). Moved it to brcdapi.port as sort_ports()               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.7     | 04 Sep 2022   | Added some bullet proofing.                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.8     | 01 Jan 2023   | Added fos_to_dict()                                                               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.1.9     | 09 May 2023   | Fixed recursion error in date_to_epoch()                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.2.0     | 21 May 2023   | Updated documentation                                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '21 May 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.2.0'

import re
import datetime
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcddb.classes.util as brcddb_class_util
import brcdapi.port as brcdapi_port

_DEBUG_FICON = False  # Intended for lab use only. Few, if any, will use this to zone a FICON switch
_MAX_LINE_COUNT = 20  # Maximum number of lines before inserting a space when generating CLI
_MAX_MEM = 3  # Maximum number of members to add to a zone object in a single FOS command (CLI)


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


def sp_port_sort(port_list):
    """Sorts a list of port objects by slot then port number. Deprecated."""
    return brcdapi_port.sort_ports(port_list)


def sort_ports(port_obj_list):
    """Sorts a list of port objects by switch, then slot, then port number.

    :param port_obj_list: list of PortObj objects - see PortObj - in brcddb.classes.port.PortObj
    :type port_obj_list: list
    :return return_list: Sorted list of port objects from obj_list
    :rtype: list
    """
    rl = list()
    if len(port_obj_list) == 0:
        return rl
    proj_obj = port_obj_list[0].r_project_obj()  # Assume the same project for all ports

    # Use wd below to sort the port objects by the switch they belong to
    wd = dict()
    for port_obj in port_obj_list:
        switch_obj = port_obj.r_switch_obj()
        switch_key = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/user-friendly-name')
        if switch_key is None:
            switch_key = switch_obj.r_get('brocade-fabric/fabric-switch/switch-user-friendly-name')
        if switch_key is None:
            switch_key = ''
        switch_key += '_' + switch_obj.r_obj_key()
        switch_d = wd.get(switch_key)
        if switch_d is None:
            switch_d = dict(switch_obj=switch_obj, port_obj_l=list())
            wd.update({switch_key: switch_d})
        switch_d['port_obj_l'].append(port_obj)

    # Sort the switch keys
    switch_key_l = list(wd.keys())
    switch_key_l.sort()

    # Sort the ports on a per switch basis and add to the return list
    for switch_d in [wd[k] for k in switch_key_l]:
        switch_obj = switch_d['switch_obj']
        rl.extend([switch_obj.r_port_obj(port) for port in \
                   brcdapi_port.sort_ports([port_obj.r_obj_key() for port_obj in switch_d['port_obj_l']])] )

    return rl


def login_to_port_map(fab_obj):
    """Creates a map of logins to the port where the login occured for build_login_port_map()

    :param fab_obj: Fabric Object
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :return port_to_wwn_d: Dictionary - key: login WWN, value: port object
    :rtype port_to_wwn_d: dict
    :return base_l: List of NPIV base port logins
    :rtype base_l: list
    """
    base_l, port_to_wwn_d = list(), dict()
    for port_obj in fab_obj.r_port_objects():
        nl = list(port_obj.r_login_keys())
        if len(nl) > 1:
            base_l.append(nl[0])
        for wwn in nl:
            port_to_wwn_d.update({wwn: port_obj})
    return port_to_wwn_d, base_l


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
    try:
        name = group['name']
        for port in gen_util.convert_to_list(group['members']['member']):
            port_obj = switch_obj.r_port_obj(port)
            if port_obj is not None:
                port_obj.s_add_maps_fc_port_group(name)
    except (TypeError, KeyError):
        return


def _sfp(switch_obj, group):
    """Adds the MAPS group to the port

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param group: MAPS group
    :type group: dict
    """
    try:
        name = group['name']
        for port in gen_util.convert_to_list(group['members']['member']):
            port_obj = switch_obj.r_port_obj(port)
            if port_obj is not None:
                port_obj.s_add_maps_sfp_group(name)
    except (TypeError, KeyError):
        return


def _null(switch_obj, group):
    """MAPS groups not yet implemented

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param group: MAPS group
    :type group: dict
    """
    if isinstance(group, dict) and group.get('name') is not None:
        return
    brcdapi_log.exception('Invalid MAPS group', echo=True)


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
        active_rule_list = gen_util.convert_to_list(gen_util.get_key_val(switch_obj.r_active_maps_policy(),
                                                                         'rule-list/rule'))
        for group in gen_util.convert_to_list(switch_obj.r_get('brocade-maps/group')):
            switch_obj.s_add_group(group)
        for rule in gen_util.convert_to_list(switch_obj.r_get('brocade-maps/rule')):
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
                brcdapi_log.exception(buf, echo=True)


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
        port_list.extend([fab_obj.r_port_obj(wwn) for wwn in gen_util.convert_to_list(wwn_list)
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
        # flag, below, is for malformed command lines
        c, o, p0, p1, peer, flag, state = None, None, None, None, False, False, _state_cmd
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


def add_to_obj(obj, k, v):
    """Adds a key value pair to obj using '/' notation in the key. If the key already exists, it is overwritten.

    :param obj: Dictionary or brcddb.class object the key value pair is to be added to
    :type obj: dict, ProjectObj, FabricObj, SwitchObj, AliasObj, ChassisObj, PortObj, AliasObj, ZoneObj, ZoneCfgObj
    :param k: The key
    :type k: str
    :param v: Value associated with the key.
    :type v: int, str, list, dict
    """
    global error_asserted

    if not isinstance(k, str):
        brcdapi_log.exception('Invalid key. Expected type str, received type ' + str(type(k)), echo=True)
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
                              echo=True)
        error_asserted = True
    else:
        key = key_list.pop(0)
        if len(key_list) == 0:
            obj.s_new_key(key, v, f=True)
            return
        r_obj = obj.r_get(key)
        if r_obj is None:
            r_obj = dict()
            obj.s_new_key(key, r_obj)
        add_to_obj(r_obj, '/'.join(key_list), v)


def get_from_obj(obj, k):
    """Returns the value associated with a key in / notation for a dict or brcddb.class object

    :param obj: Dictionary the key is for
    :type obj: dict
    :param k: The key
    :type k: str
    :return: Value associated with the key. None is returned if the key was not found
    :rtype: int, str, list, dict, None
    """
    if isinstance(obj, dict):
        return gen_util.get_from_obj(obj, k)
    elif brcddb_class_util.get_simple_class_type(obj) is None:
        brcdapi_log.exception('Invalid object type.', echo=True)
    else:
        return obj.r_get(k)


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


_letter_to_num = dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10, k=11, l=12, m=13, n=14, o=15, p=16, q=17, r=18,
                      s=19, t=20, u=21, v=22, w=23, x=24, y=25, z=26)  # Used in fos_to_dict()


def fos_to_dict(version_in, valid_check=True):
    """Converts a FOS version into a dictionary to be used for comparing for version numbers

    +-----------+-------+-------------------------------------------------------------------------------+
    | Key       | Type  |Description                                                                    |
    +===========+=======+===============================================================================+
    | version   | str   | Same as version_in                                                            |
    +-----------+-------+-------------------------------------------------------------------------------+
    | major     | int   | In example 9.1.0b, this is 9                                                  |
    +-----------+-------+-------------------------------------------------------------------------------+
    | feature   | int   | In example 9.1.0b, this is 1                                                  |
    +-----------+-------+-------------------------------------------------------------------------------+
    | minor     | int   | In example 9.1.0b, this is 0                                                  |
    +-----------+-------+-------------------------------------------------------------------------------+
    | bug       | int   | In example 9.1.0b, this is 2 (converted to a numeric for easier comparisons). |
    |           |       | In example 9.1.0, this is 0.                                                  |
    +-----------+-------+-------------------------------------------------------------------------------+
    | patch     | str   | In example 9.1.0b, this is an empty str. In 9.1.0b_01, this is "_01"          |
    +-----------+-------+-------------------------------------------------------------------------------+

    :param version_in: FOS version
    :type version_in: str
    :param valid_check: If True, creates an exception entry in the log if the version of FOS is not valid
    :type valid_check: bool
    :return: Dictionary as described above
    :rtype dict
    """
    global _letter_to_num

    try:
        version = version_in.lower()
        if version[0] == 'v':
            version = version[1:]
        version_l = version.split('.')
        if len(version_l[2]) > 1:
            try:
                bug = _letter_to_num[version_l[2][1:2]]
                patch = version_l[2][2:] if len(version_l[2]) > 1 else ''
            except KeyError:
                bug = 0
                patch = version_l[2][1:]
        else:
            bug = 0
            patch = ''
        return dict(version=str(version_in),
                    major=int(version_l[0]),
                    feature=int(version_l[1]),
                    minor=int(version_l[2][0:1]),
                    bug=bug,
                    patch=patch)
    except (IndexError, TypeError, ValueError, AttributeError):
        if valid_check:
            brcdapi_log.exception(['Invalid FOS version: ' + str(version_in), 'Type: ' + str(type(version_in))],
                                  echo=True)

    return dict(version=str(version_in), major=0, feature=0, minor=0, bug=0, patch='')



###################################################################
#
#                    Depracated
#
###################################################################

non_decimal = gen_util.non_decimal
decimal = gen_util.decimal
zone_notes = gen_util.zone_notes
ishex = gen_util.ishex
valid_file_name = gen_util.valid_file_name
date_to_space = gen_util.date_to_space
multiplier = gen_util.multiplier
month_to_num = gen_util.month_to_num
num_to_month = gen_util.num_to_month


def remove_duplicate_space(buf):
    return gen_util.remove_duplicate_space(buf)


def get_key_val(obj, keys):
    return gen_util.get_key_val(obj, keys)


def sort_obj_num(obj_list, key, r=False, h=False):
    return gen_util.sort_obj_num(obj_list, key, r, h)


def convert_to_list(obj):
    return gen_util.convert_to_list(obj)


def remove_duplicates(obj_list):
    return gen_util.remove_duplicates(obj_list)


def remove_none(obj_list):
    return gen_util.remove_none(obj_list)


def is_wwn(wwn, full_check=True):
    return gen_util.is_wwn(wwn, full_check)


def is_valid_zone_name(zone_name):
    return gen_util.is_valid_zone_name(zone_name)


def slot_port(port):
    return gen_util.slot_port(port)


def is_di(di):
    return gen_util.is_di(di)


def remove_duplicate_space(buf):
    return gen_util.remove_duplicate_space(buf)


def str_to_num(buf):
    return gen_util.str_to_num(buf)


def paren_content(buf, p_remove=False):
    return gen_util.paren_content(buf, p_remove)


def get_struct_from_obj(obj, k):
    return gen_util.get_struct_from_obj(obj, k)


def resolve_multiplier(val):
    return gen_util.resolve_multiplier(val)


def dBm_to_absolute(val, r=1):
    return dBm_to_absolute(val, r)


def int_list_to_range(num_list):
    return gen_util.int_list_to_range(num_list)


def date_to_epoch(date_time, fmt=0, utc=False):
    return gen_util.date_to_epoch(date_time, fmt, utc)
