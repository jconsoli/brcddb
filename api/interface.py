"""
Copyright 2023, 2024, 2025 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Single interface to brcdapi. Intended for all applications using brcddb apps

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| get_chassis           | Gets the  chassis object and objects for all logical switches in the chassis.             |
+-----------------------+-------------------------------------------------------------------------------------------+
| login                 | Wrapper around login of a Rest API session using brcdapi.brcdapi_rest.login()             |
+-----------------------+-------------------------------------------------------------------------------------------+
| logout                | Wrapper around logout of a Rest API session using brcdapi.brcdapi_rest.logout()           |
+-----------------------+-------------------------------------------------------------------------------------------+
| get_rest              | Wraps logging around a call to brcdapi.brcdapi_rest.get_request() and adds responses to   |
|                       | the associated object.                                                                    |
+-----------------------+-------------------------------------------------------------------------------------------+
| get_batch             | Processes a batch API requests and adds responses to the associated object. All chassis   |
|                       | request are performed first, followed by processing of logical switch requests.           |
+-----------------------+-------------------------------------------------------------------------------------------+
| results_action        | Updates the brcddb database for an API request response. Typically only called by         |
|                       | get_rest() and get_batch() so making this public was a future consideration.              |
+-----------------------+-------------------------------------------------------------------------------------------+

ToDo in get_batch() - All raw output for CLI goes to the switch object which is fine for now. This will have to be
modified if CLI commands are used for data that should be associated with an object other than the switch

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Added no_mask option to get_batch(). Added CLI command handling. Added logout()       |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 20 Oct 2024   | Use port_obj.r_addr() instead of hard coded key r_get()                               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 06 Dec 2024   | Removed out dated URI references.                                                     |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 01 Mar 2025   | Removed skip of 'member-entry' in _effective_zonecfg_case()                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 25 Aug 2025   | Added additional error checking to logout()                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025 Consoli Solutions, LLC'
__date__ = '19 Oct 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.6'

import http.client
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.fos_auth as fos_auth
import brcdapi.util as brcdapi_util
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.fos_cli as fos_cli
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_switch as brcddb_switch
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util
import brcddb.util.util as brcddb_util
import brcddb.util.parse_cli as parse_cli

_GEN_CASE_ERROR_MSG = '. A request for was made for something that needs to be added to an object that does not exist'

_default_ip_list = (  # List of keys that are IP addresses. Used to determine if all but the last byte should be masked
    'ip-address',
    'ip-address-list',
    'ip-static-gateway-list',
    'ip-gateway-list',
    'dns-servers',
)
_ip_list = _default_ip_list
_parse_cli_ref = dict(  # Used in get_batch() for CLI commands
    portcfgshow=parse_cli.portcfgshow,
    portbuffershow=parse_cli.portbuffershow,
)


def _process_errors(session, uri, obj, wobj, e=None):
    """Checks for errors in the API response and adds alerts to the object if there is an error

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param uri: URI, less the prefix
    :type uri: str
    :param obj: FOS API object
    :type obj: dict
    :param wobj: The brcddb class object we were working when the error occurred
    :type wobj: brcddb.classes.project.ProjectObj, brcddb.classes.chassis.ChassisObj, brcddb.classes.switch.SwitchObj,\
        None
    :param e: Exception code
    :type e: str, None
    """
    if not fos_auth.is_error(obj):
        return
    ip_addr = brcdapi_util.mask_ip_addr(session.get('ip_addr'))
    p1 = fos_auth.formatted_error_msg(obj)
    ml = [' Request FAILED for :' + ip_addr, p1]
    if e is not None:
        ml.append(e)
    brcdapi_log.log(ml, echo=True)
    if wobj is None:
        return
    proj_obj = wobj.r_project_obj()
    proj_obj.s_api_error_flag()
    error_table = dict(
        ProjectObj=dict(
            p0=ip_addr,
            al_num=al.ALERT_NUM.PROJ_FAILED_LOGIN if '/rest/login' in uri else al.ALERT_NUM.PROJ_CHASSIS_API_ERROR
        ),
        ChassisObj=dict(p0=brcddb_chassis.best_chassis_name(wobj), al_num=al.ALERT_NUM.PROJ_CHASSIS_API_ERROR),
        SwitchObj=dict(p0=brcddb_switch.best_switch_name(wobj), al_num=al.ALERT_NUM.PROJ_SWITCH_API_ERROR)
    )
    simple_type = brcddb_class_util.get_simple_class_type(wobj)
    if simple_type in error_table:
        p0 = error_table[simple_type]['p0']
        al_num = error_table[simple_type]['al_num']
    else:
        brcdapi_log.exception('Unknown object type: ' + str(type(wobj)))
        return
    proj_obj.s_add_alert(al.AlertTable.alertTbl, al_num, None, p0, p1)


def get_chassis(session, proj_obj):
    """Gets the  chassis object and objects for all logical switches in the chassis.

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param proj_obj: The project object
    :type proj_obj: brcddb.classes.project.ProjectObj
    :return: Chassis object
    :rtype: brcddb.classes.ChassisObj
    """
    chassis_obj = None
    # See if we already got it
    if 'chassis_wwn' in session:
        chassis_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn'))
        if chassis_obj is not None:
            return chassis_obj

    # Go get it
    uri = 'running/' + brcdapi_util.bcc_uri
    obj = brcdapi_rest.get_request(session, uri, None)
    if fos_auth.is_error(obj):
        return None
    try:
        wwn = obj['chassis']['chassis-wwn']
        chassis_obj = proj_obj.s_add_chassis(wwn)
        results_action(session, chassis_obj, obj, uri)
        session.update(chassis_wwn=wwn)
        # Get all the switches in this chassis
        if chassis_obj.r_is_vf_enabled():  # Get all the logical switches in this chassis
            uri = 'running/' + brcdapi_util.bfls_uri
            obj = brcdapi_rest.get_request(session, uri, None)
            _process_errors(session, uri, obj, chassis_obj)
            results_action(session, chassis_obj, obj, uri)
        # Get the logical switch configurations
        for fid in chassis_obj.r_fid_list():
            uri = 'running/' + brcdapi_util.bfsw_uri
            obj = brcdapi_rest.get_request(session, uri, fid)
            _process_errors(session, uri, obj, chassis_obj)
            results_action(session, chassis_obj, obj, uri)
    except BaseException as e:
        _process_errors(session, uri, session, proj_obj, str(type(e)) + ': ' + str(e))

    return chassis_obj


def login(user_id, pw, ip_addr, https='none', proj_obj=None):
    """Wrapper around login of a Rest API session using brcdapi.brcdapi_rest.login()

    :param user_id: User ID
    :type user_id: str
    :param pw: Password
    :type pw: str
    :param ip_addr: IP address
    :type ip_addr: str
    :param https: If 'CA' or 'self', uses https to login. Otherwise, http.
    :type https: None, str
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj, None
    :return: session
    :rtype: dict
    """
    # Attempt to log in
    tip = brcdapi_util.mask_ip_addr(ip_addr, keep_last=True)
    session = brcdapi_rest.login(user_id, pw, ip_addr, https)
    if fos_auth.is_error(session):
        brcdapi_log.log(tip + ' Login failed', echo=True)
        _process_errors(session, '/rest/login', session, proj_obj)
        return session
    else:
        brcdapi_log.log(tip + ' Login succeeded', echo=True)
    return session


def logout(session):
    """Wrapper around logout of a Rest API session using brcdapi.brcdapi_rest.logout()

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict, None
    :return: Logout confirmation message or, if any, error messages
    :rtype: list
    """
    rl = list()

    # Logout of the SSH session, if one exists
    fos_cli.logout(session)

    # Logout of the API session
    try:
        obj = brcdapi_rest.logout(session)
        if fos_auth.is_error(obj):
            rl.extend(['Logout failed. Error is:', fos_auth.formatted_error_msg(obj)])
        else:
            rl.append('API logout succeeded')
    except (http.client.CannotSendRequest, http.client.ResponseNotReady):
        rl.append('Could not logout. You may need to terminate this session via the CLI',
                   'mgmtapp --showsessions, mgmtapp --terminate')
    except BaseException as e:
        buf = 'Unknown error occured while attempting to logout of the switch at '
        buf += brcdapi_util.mask_ip_addr(session.get('ip_addr'))
        rl.extend([buf, str(type(e)) + ': ' + str(e)])

    return rl


def get_rest(session, uri, wobj=None, fid=None):
    """Wraps logging around a call to brcdapi.brcdapi_rest.get_request() and adds responses to the associated object.

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param uri: URI, less the prefix
    :type uri: str
    :param wobj: Working object
    :type: ProjectObj, FabricObj, SwitchObj, ChassisObj
    :param fid: Fabric ID
    :type fid: int, None
    :return: obj
    :rtype: dict
    """
    brcdapi_log.log('GET: ' + uri + brcdapi_util.vfid_to_str(fid), echo=True)
    obj = brcdapi_rest.get_request(session, uri, fid)
    _process_errors(session, uri, obj, wobj)
    return obj


# Below is used in _switch_port_case(), see _port_case_case, to determine what port object (GE port, FC port, media) to
# add to the switch and returns the added port object
def _port_case_fc(objx, port):
    return objx.s_add_port(port.get('name'))


def _port_case_ge(objx, port):
    return objx.s_add_ge_port(port.get('name'))


def _port_case_media(objx, port):
    return objx.s_add_port('/'.join(port.get('name').split('/')[1:]))  # Strip off the media type


def _port_case_rnid(objx, port):
    # RNID data is matched to a port by the link address. I don't think a leading '0x' is present, but just in case...
    fc_addr = port.get('link-address') + '00'
    for port_obj in objx.r_port_objects():
        if str(port_obj.r_addr()).replace('0x', '') == fc_addr:
            return port_obj
    return None


_port_case_case = {
    'fibrechannel-statistics': _port_case_fc,
    'fibrechannel': _port_case_fc,
    'extension-ip-interface': _port_case_ge,
    'gigabitethernet': _port_case_ge,
    'gigabitethernet-statistics': _port_case_ge,
    'media-rdp': _port_case_media,
    'rnid': _port_case_rnid,
}

# These are the case statements, see rest_methods, called from get_batch() with the following parameters:
#    :param objx: One of the classes in brcddb.classes
#    :type objx: brcddb class
#    :param obj: List element from FOS API object
#    :type obj: dict
#    :param uri: URI, less the prefix
#    :type uri: str
# All the case methods add to brcddb.classes objects


def _convert_ip_addr(obj):
    if isinstance(obj, dict):
        d = dict()
        for k, v in obj.items():
            d.update({k: _convert_ip_addr(v)})
        return d
    elif isinstance(obj, (list, tuple)):
        return [_convert_ip_addr(v) for v in obj]
    else:
        return brcdapi_util.mask_ip_addr(obj)


def _update_brcddb_obj_from_list(objx, obj, uri, skip_list=None):
    """Adds a FOS API request response that is a list. Each item in the list is added to a brcddb class object

    All parameters as in comments above except:
    :param skip_list: Skip list. List of elements to not add to objx
    :type skip_list: None, int, float, str, list, tuple
    """
    global _GEN_CASE_ERROR_MSG

    skip_d = dict()
    for k in gen_util.convert_to_list(skip_list):
        skip_d.update({k: True})

    try:
        temp_l = brcdapi_util.split_uri(uri, run_op_out=True)
        key = '/'.join(temp_l)
        obj_key = temp_l.pop()
        _mask_ip_addr(obj, keep_last=True)
        working_obj = obj[obj_key] if obj_key in obj else obj
        for k, v in working_obj.items():
            if not skip_d.get(k, False):
                brcddb_util.add_to_obj(objx, key + '/' + k, v)
    except BaseException as e:
        e_buf = str(type(e)) + ': ' + str(e)
        brcdapi_log.exception([_GEN_CASE_ERROR_MSG, e_buf], echo=True)
        objx.r_project_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_PROGRAM_ERROR, None,
                                         _GEN_CASE_ERROR_MSG, e_buf)
        try:
            objx.r_project_obj().s_warn_flag()
        except (TypeError, AttributeError):
            try:
                objx.s_warn_flag()
            except (TypeError, AttributeError):
                pass


# Case methods for rest_methods
def _update_brcddb_obj(objx, obj, uri):
    global _GEN_CASE_ERROR_MSG

    if objx is None:
        # This happens when fabric information is polled from a switch but the principal fabric switch wasn't polled,
        # and we don't know what the principal fabric switch WWN is.
        return

    try:
        temp_l = brcdapi_util.split_uri(uri, run_op_out=True)
        key = '/'.join(temp_l)
        obj_key = temp_l.pop()
        working_obj = _mask_ip_addr(obj, keep_last=True)
        if obj_key in working_obj:
            working_obj = working_obj[obj_key]
        if isinstance(working_obj, dict):
            for k, v in working_obj.items():
                brcddb_util.add_to_obj(objx, key + '/' + k, v)
        else:
            brcddb_util.add_to_obj(objx, key, working_obj)
    except BaseException as e:
        e_buf = str(type(e)) + ': ' + str(e)
        brcdapi_log.exception([_GEN_CASE_ERROR_MSG, e_buf, 'uri: ' + str(uri)], echo=True)
        objx.r_project_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_PROGRAM_ERROR, None,
                                         _GEN_CASE_ERROR_MSG, e_buf)
        try:
            objx.r_project_obj().s_warn_flag()
        except (TypeError, AttributeError):
            try:
                objx.s_warn_flag()
            except (TypeError, AttributeError):
                pass


def _null_case(objx, obj, uri):
    return


def _fabric_case(objx, obj, uri):
    _update_brcddb_obj(objx.r_fabric_obj(), obj, uri)


def _defined_zonecfg_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    if fab_obj is None:
        return  # The switch is not in a fabric if it's disabled. We also get here if the principal switch is unknown
    dobj = obj.get('defined-configuration')
    if dobj is not None:
        for zobj in gen_util.convert_to_list(dobj.get('cfg')):
            zonecfg_obj = fab_obj.s_add_zonecfg(zobj.get('cfg-name'), zobj['member-zone'].get('zone-name'))
            _update_brcddb_obj(zonecfg_obj, zobj, uri)
        for zobj in gen_util.convert_to_list(dobj.get('zone')):
            if 'member-entry' in zobj:
                mem_list = zobj.get('member-entry').get('entry-name')
                pmem_list = zobj.get('member-entry').get('principal-entry-name')
            else:
                mem_list = None
                pmem_list = None
            fab_obj.s_add_zone(zobj.get('zone-name'), zobj.get('zone-type'), mem_list, pmem_list)
        for zobj in gen_util.convert_to_list(dobj.get('alias')):
            mem_list = zobj.get('member-entry').get('alias-entry-name') if 'member-entry' in zobj else None
            fab_obj.s_add_alias(zobj.get('alias-name'), mem_list)


def _effective_zonecfg_case(objx, obj, uri):
    if 'effective-configuration' in obj:  # None when there is no zone configuration enabled
        fab_obj = objx.r_fabric_obj()
        if fab_obj is None:
            return  # This happens when the principal switch in the fabric is unknown.
        dobj = obj.get('effective-configuration')
        if not isinstance(dobj, dict):
            return
        _update_brcddb_obj_from_list(fab_obj, dobj, uri)
        for zobj in gen_util.convert_to_list(dobj.get('enabled-zone')):
            if 'member-entry' in zobj:
                zone_obj = fab_obj.s_add_eff_zone(zobj.get('zone-name'),
                                                  zobj.get('zone-type'),
                                                  zobj['member-entry'].get('entry-name'),
                                                  zobj['member-entry'].get('principal-entry-name'))
            else:  # I don't know how there can be items in the enabled-zone without a 'member-entry'. Just in case ...
                zone_obj = fab_obj.s_add_eff_zone(zobj.get('zone-name'))
            _update_brcddb_obj(zone_obj, zobj, uri)
        fab_obj.s_add_eff_zonecfg(fab_obj.r_eff_zone_keys())


def _add_switch_to_chassis_int(chassis_obj, switch, uri, switch_wwn):
    switch_obj = chassis_obj.s_add_switch(switch_wwn)
    _update_brcddb_obj_from_list(switch_obj, switch, uri)

    # Add the ports
    try:
        for port in gen_util.convert_to_list(switch.get('port-member-list').get('port-member')):
            switch_obj.s_add_port(port)
    except (TypeError, AttributeError):
        pass

    # Add the GE ports
    try:
        for port in gen_util.convert_to_list(switch.get('ge-port-member-list').get('port-member')):
            switch_obj.s_add_ge_port(port)
    except (TypeError, AttributeError):
        pass


def _add_fab_switch_to_chassis_case(chassis_obj, obj, uri):
    sl, fab_obj, proj_obj = list(), None, chassis_obj.r_project_obj()
    for switch in gen_util.convert_to_list(obj.get(uri.split('/').pop())):
        c_obj = proj_obj.s_add_chassis(switch.get('chassis-wwn'))
        s_wwn = switch.get('name')
        switch_obj = c_obj.s_add_switch(s_wwn)
        sl.append(switch_obj)
        _update_brcddb_obj_from_list(switch_obj, switch, uri)
        if switch.get('is-principal') or switch.get('principal'):
            fab_obj = proj_obj.s_add_fabric(s_wwn)
    if fab_obj is not None:
        for switch_obj in sl:
            switch_obj.s_fabric_key(fab_obj.r_obj_key())
            fab_obj.s_add_switch(switch_obj.r_obj_key())


def _add_ls_switch_to_chassis_case(chassis_obj, obj, uri):
    existing_switch_wwns = chassis_obj.r_switch_keys()
    for switch in gen_util.convert_to_list(obj.get(uri.split('/').pop())):
        wwn = switch.get('switch-wwn')
        if wwn in existing_switch_wwns:
            continue  # The switch is already there. This method is not intended to modify an existing switch object
        switch_obj = chassis_obj.s_add_switch(wwn)
        _update_brcddb_obj_from_list(switch_obj, switch, uri)
        try:
            for port in gen_util.convert_to_list(switch['port-member-list'].get('port-member')):
                switch_obj.s_add_port(port)
        except (TypeError, AttributeError, KeyError):  # Shouldn't this just be KeyError?
            pass
        try:
            for port in gen_util.convert_to_list(switch['ge-port-member-list'].get('port-member')):
                switch_obj.s_add_ge_port(port)
        except (TypeError, AttributeError, KeyError):  # Shouldn't this just be KeyError?
            pass


def _fabric_switch_case(switch_obj, obj, uri):
    proj_obj = switch_obj.r_project_obj()
    tl = brcdapi_util.split_uri(uri, run_op_out=True)
    leaf = tl[len(tl)-1]
    wwn_ref = 'switch-wwn' if leaf == 'fibrechannel-logical-switch' else 'name'
    for switch in gen_util.convert_to_list(obj.get('fibrechannel-switch')):
        wwn = switch.get(wwn_ref)
        if gen_util.is_wwn(wwn):  # Yes, got bit by a bad WWN once
            proj_obj.s_add_switch(wwn)
            if switch.get('principal'):
                proj_obj.s_add_fabric(wwn)
            _update_brcddb_obj_from_list(switch_obj, switch, uri)
        else:
            brcdapi_log.log('Bad switch WWN, , returned from ' + uri + ' for switch ' +
                            brcddb_switch.best_switch_name(switch_obj), echo=True)


def _switch_from_list_case(switch_obj, obj, uri):
    try:
        _update_brcddb_obj_from_list(switch_obj, gen_util.convert_to_list(obj.get(uri.split('/').pop()))[0], uri)
        if switch_obj.r_is_principal():
            switch_obj.r_project_obj().s_add_fabric(switch_obj.r_obj_key())
    except (TypeError, AttributeError):
        pass


def _switch_from_list_match_case(switch_obj, obj, uri):
    switch_wwn = switch_obj.r_obj_key()
    element = uri.split('/').pop()
    i = 0
    for s_obj in gen_util.convert_to_list(obj.get(element)):
        fos_switch_wwn = s_obj.get('switch-wwn')
        if fos_switch_wwn is not None and fos_switch_wwn == switch_wwn:
            _update_brcddb_obj_from_list(switch_obj, gen_util.convert_to_list(obj.get(element))[i], uri)
            return
        i += 1


def _fabric_ns_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for ns_obj in gen_util.convert_to_list(obj.get('fibrechannel-name-server')):
        login_obj = fab_obj.s_add_login(ns_obj.get('port-name'))
        _update_brcddb_obj(login_obj, ns_obj, uri)


def _fabric_fdmi_hba_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for obj in gen_util.convert_to_list(obj.get('hba')):
        try:
            for wwn in gen_util.convert_to_list(obj['hba-port-list'].get('wwn')):
                fab_obj.s_add_fdmi_port(wwn)
        except (TypeError, AttributeError):
            pass
        _update_brcddb_obj(fab_obj.s_add_fdmi_node(obj.get('hba-id')), obj, uri)


def _fabric_fdmi_port_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for obj in gen_util.convert_to_list(obj.get('port')):
        _update_brcddb_obj(fab_obj.s_add_fdmi_port(obj.get('port-name')), obj, uri)


def _switch_port_case(objx, obj, uri):
    """Parses port data into the switch object

    :param objx: Switch object
    :type objx: brcddb.classes.switch.SwitchObj
    :param obj: Object returned from the API
    :type obj: dict
    """
    tl = brcdapi_util.split_uri(uri, run_op_out=True)
    leaf = tl[len(tl)-1]
    for port in gen_util.convert_to_list(obj.get(leaf)):
        port_obj = _port_case_case[leaf](objx, port)
        if port_obj is not None:
            d = port_obj.r_get(leaf)
            if d is None:
                port_obj.s_new_key(leaf, dict())
                d = port_obj.r_get(leaf)
            for k, v in port.items():
                d.update({k: v})


def _fru_blade_case(objx, obj, uri):
    global _ip_list

    new_obj = dict()
    for k, v in obj.items():
        if isinstance(v, list) and k == 'blade':
            new_list = list()
            for d in v:
                new_d = dict()
                for k1, v1 in d.items():
                    if k1 in _ip_list:
                        new_d.update({k1: _convert_ip_addr(v1)})
                    else:
                        new_d.update({k1: v1})
                new_list.append(new_d)
            new_obj.update({k: new_list})
        else:  # Up to 9.0, there was nothing else in here but 'blade' so this is just future proofing
            new_obj.update({k: v})
    _update_brcddb_obj(objx, new_obj, uri)


# Normally, all data returned from the API is stored in the object by calling the methods in _rest_methods(). These
# methods are for non-standard handling of URIs.
_custom_rest_methods = {
    # Fabric
    'running/brocade-fabric/fabric-switch': _add_fab_switch_to_chassis_case,
    'running/brocade-fibrechannel-switch/fibrechannel-switch': _switch_from_list_case,
    'running/brocade-fdmi/hba': _fabric_fdmi_hba_case,
    'running/brocade-fdmi/port': _fabric_fdmi_port_case,
    'running/brocade-name-server/fibrechannel-name-server': _fabric_ns_case,
    'running/brocade-zone/defined-configuration': _defined_zonecfg_case,
    'running/brocade-zone/effective-configuration': _effective_zonecfg_case,
    'running/brocade-fru/blade': _fru_blade_case,
    'running/brocade-ficon/switch-rnid': _switch_from_list_match_case,
}

_rest_methods = {
    # No action - Note that this is a work in progress. Everything that wasn't in _custom_rest_methods called
    # _update_brcddb_obj(). Anything I haven't created a generic rest method for is still in _custom_rest_methods.
    brcdapi_util.NULL_OBJ: _null_case,
    brcdapi_util.SESSION_OBJ: _null_case,

    # Chassis
    brcdapi_util.CHASSIS_OBJ: _update_brcddb_obj,
    brcdapi_util.CHASSIS_SWITCH_OBJ: _add_ls_switch_to_chassis_case,

    # Switch
    brcdapi_util.SWITCH_OBJ: _update_brcddb_obj,
    brcdapi_util.SWITCH_PORT_OBJ: _switch_port_case,

    # Fabric
    brcdapi_util.FABRIC_OBJ: _fabric_case,
    brcdapi_util.FABRIC_SWITCH_OBJ: _fabric_switch_case,
    brcdapi_util.FABRIC_ZONE_OBJ: _fabric_case,
}


def _mask_ip_addr(obj, keep_last):
    """Copies an object and replaces all dictionary elements with an IP key with xxx

    :param obj: Dictionary to copy
    :type obj: dict, list, int, float, bool, None
    :param keep_last: If True, keeps the last octet of the IP address.
    :type keep_last: bool
    :return: Copy of obj with all IP addresses masked off
    :rtype: dict, list, int, float, bool, None
    """
    global _ip_list

    if obj is None:
        return None
    if isinstance(obj, (int, float, str)):  # bool is a form of int
        return obj
    if isinstance(obj, (list, tuple)):
        return [_mask_ip_addr(v, keep_last) for v in obj]
    if isinstance(obj, dict):
        rd = dict()
        for k, v in obj.items():
            if isinstance(v, str):
                rd.update({k: _convert_ip_addr(v) if k in _ip_list else v})
            elif isinstance(v, (list, dict)):
                rd.update({k: _mask_ip_addr(v, keep_last)})
            else:
                rd.update({k: v})
        return rd

    brcdapi_log.exception('Unknown object type: ' + str(type(obj)), echo=True)
    return None


def results_action(session, brcddb_obj, fos_obj, kpi):
    """Updates the brcddb database for an API request response. Typically only called by get_rest() and get_batch()

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param brcddb_obj: brcddb class library object
    :type brcddb_obj: brcddb.classes.*
    :param fos_obj: Object returned from the API
    :type fos_obj: dict
    :param kpi: KPI associated with fos_obj
    :type kpi: str
    """
    global _custom_rest_methods, _rest_methods

    if not fos_auth.is_error(fos_obj):
        try:
            if kpi in _custom_rest_methods:
                _custom_rest_methods[kpi](brcddb_obj, fos_obj, kpi)
            else:
                _rest_methods[brcdapi_util.uri_d(session, kpi)['area']](brcddb_obj, fos_obj, kpi)
        except (TypeError, ValueError, KeyError):
            buf = 'Could not add ' + kpi + ' to ' + str(type(brcddb_obj)) + '. This typically occurs when something '
            buf += 'for the fabric was polled but the fabric WWN is unknown.'
            brcdapi_log.log(buf, echo=True)


def get_batch(session, proj_obj, uri_l, fid=None, no_mask=False):
    """Processes a batch API requests and adds responses to the associated object. All chassis request are performed
    first, followed by processing of logical switch requests.

    If any warnings or errors are encountered, the log is updated and the appropriate flag bits for the proj_obj are
    set. Search for _project_warn in brcddb_common.py for additional information. Again, search for _project_warn in
    brcddb.classes for object methods to set and check these bits.

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.ProjectObj
    :param uri_l: List of URIs to request from the switches and chassis
    :type uri_l: list, str
    :param fid: FID, or list of FIDs for logical switch level requests. If None, execute requests for all FIDs.
    :type fid: int, list, tuple, None
    :param no_mask: If True, do not mask off IP addresses.
    :type no_mask: bool
    :return: True if no errors encountered, otherwise False
    :rtype: bool
    """
    global _ip_list, _default_ip_list

    _ip_list = list() if no_mask else _default_ip_list

    # Get the chassis object
    chassis_obj = get_chassis(session, proj_obj)
    if chassis_obj is None:
        brcdapi_log.log(brcdapi_util.mask_ip_addr(session.get('ip_addr')) + ' Chassis not found.', echo=True)
        return False

    # Sort out which KPIs are for the chassis: which are for a logical switch, which are for CLI
    fos_cli_l, chassis_uri_l, switch_uri_l = list(), list(), list()
    for uri in gen_util.convert_to_list(uri_l):
        fos_command = fos_cli.parse_cli(uri)
        if isinstance(fos_command, str):
            fos_cli_l.append(fos_command)
        else:
            d = brcdapi_util.uri_d(session, uri)
            if isinstance(d, dict):  # It's None if the URI isn't supported in this version of FOS
                if d['fid']:
                    switch_uri_l.append(uri)
                else:
                    chassis_uri_l.append(uri)

    # Get all the chassis data
    for uri in chassis_uri_l:
        obj = get_rest(session, uri, chassis_obj)
        results_action(session, chassis_obj, obj, uri)

    # Figure out which logical switches to poll switch level data from.
    if chassis_obj.r_is_vf_enabled() and fid is not None:
        switch_list = list()
        for fab_id in gen_util.convert_to_list(fid):
            switch_obj = chassis_obj.r_switch_obj_for_fid(fab_id)
            if switch_obj is None:
                brcdapi_log.log('FID ' + str(fab_id) + ' not found', echo=True)
            else:
                switch_list.append(switch_obj)
    else:
        switch_list = chassis_obj.r_switch_objects()

    # Now process all the switch (FID) level commands.
    for switch_obj in switch_list:
        for uri in switch_uri_l:
            obj = get_rest(session, uri, switch_obj, brcddb_switch.switch_fid(switch_obj))
            results_action(session, switch_obj, obj, uri)

    # Process any CLI commands. $ToDo - I'm assuming all these commands are switch level, but it could be chassis
    for switch_obj in chassis_obj.r_switch_objects():
        for full_cmd in fos_cli_l:
            raw_l = fos_cli.send_command(session, brcddb_switch.switch_fid(switch_obj), full_cmd)
            if len(raw_l) > 0:
                cmd = full_cmd.split(' ')[0]
                brcddb_class_util.get_or_add(switch_obj, 'fos_cli/' + cmd, raw_l)
                try:
                    _parse_cli_ref[cmd](switch_obj, raw_l)
                except KeyError:
                    brcdapi_log.exception('Unknown FOS CLI command: ' + cmd, echo=True)

    return True
