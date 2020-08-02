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
:mod:`brcddb.api.interface` - Single interface to brcdapi. Intended for all applications include brcddb apps

Primary Methods::

    +---------------------------+-----------------------------------------------------------------------------------+
    | Method                    | Description                                                                       |
    +===========================+===================================================================================+
    | login()                   | Wrapper around login of a Rest API session using brcdapi.brcdapi_rest.login()     |
    +---------------------------+-----------------------------------------------------------------------------------+
    | get_rest()                | Wraps loging around a call to brcdapi.brcdapi_rest.get_request()                  |
    +---------------------------------------------------------------------------------------------------------------+
    | get_batch()               | Processes a batch API requests by making iterative calls to get_rest()            |
    +---------------------------+-----------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '02 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.pyfos_auth as pyfos_auth
import brcdapi.util as brcdapi_util
import brcdapi.log as brcdapi_log
import brcddb.util.util as brcddb_util
import brcddb.brcddb_chassis as brcddb_chassis
import brcddb.brcddb_switch as brcddb_switch
import brcddb.app_data.alert_tables as al
import brcddb.classes.util as brcddb_class_util

_GEN_CASE_ERROR_MSG = '. A request for was made for something that needs to be added to an object that does not exist'
_MAX_CHASSIS_BATCH = 15  # Somewhat arbitrary number chassis requests to batch. Used in get_all()
_MAX_SWITCH_BATCH = 1  # Somewhat arbitrary number FID level requests to batch. Used in get_all()

_ip_list = (  # List of keys that are IP addresses. Used to determine if all but the last byte should be masked
    'ip-address',
    'ip-address-list',
    'ip-static-gateway-list',
    'ip-gateway-list',
    'dns-servers',
)


def _process_errors(session, uri, obj, wobj):
    """Checks for errors in the API response and adds alerts to the object if there is an error

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param uri: URI, less the prefix
    :type uri: str
    :param obj: FOS API object
    :type obj: dict
    :param wobj: The brcddb class object we were working when the error occured
    :type wobj: brcddb.classes.project.ProjectObj, brcddb.classes.chassis.ChassisObj, brcddb.classes.switch.SwitchObj,\
        None
    """
    if not pyfos_auth.is_error(obj):
        return
    ip_addr = brcdapi_util.mask_ip_addr(session.get('ip_addr'))
    p1 = pyfos_auth.formatted_error_msg(obj)
    brcdapi_log.log(ip_addr + " Request FAILED:\n" + p1, True)
    if wobj is None:
        return
    proj_obj = wobj.r_project_obj()
    proj_obj.s_api_error_flag()
    error_table = {
        'ProjectObj': {
            'p0': ip_addr,
            'al_num': al.ALERT_NUM.PROJ_FAILED_LOGIN if '/rest/login' in uri else al.ALERT_NUM.PROJ_CHASSIS_API_ERROR
        },
        'ChassisObj': {'p0': brcddb_chassis.best_chassis_name(wobj), 'al_num': al.ALERT_NUM.PROJ_CHASSIS_API_ERROR},
        'SwitchObj': {'p0': brcddb_switch.best_switch_name(wobj), 'al_num': al.ALERT_NUM.PROJ_SWITCH_API_ERROR}
    }
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

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param proj_obj: The project object
    :type: brcddb.classes.project.ProjectObj
    :return: Chassis object
    :rtype: brcddb.classes.ChassisObj
    """
    # See if we already got it
    if 'chassis_wwn' in session:
        chassis_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn'))
        if chassis_obj is not None:
            return chassis_obj

    # Go get it
    uri = 'brocade-chassis/chassis'
    obj = brcdapi_rest.get_request(session, uri, None)
    if pyfos_auth.is_error(obj):
        return None
    try:
        wwn = obj.get('chassis').get('chassis-wwn')
        chassis_obj = proj_obj.s_add_chassis(wwn)
        results_action(chassis_obj, obj, uri)
        session.update({'chassis_wwn': wwn})
        # Get all the switches in this chassis
        if chassis_obj.r_is_vf_enabled():  # Get all the logical switches in this chassis
            uri = 'brocade-fibrechannel-logical-switch/fibrechannel-logical-switch'
            obj = brcdapi_rest.get_request(session, uri, None)
            if pyfos_auth.is_error(obj):
                _process_errors(session, uri, obj, chassis_obj)
                fid_l = []
            else:
                results_action(chassis_obj, obj, uri)
                fid_l = [d.get('fabric-id') for d in obj.get('fibrechannel-logical-switch')]
        else:
            fid_l = [None]
        for fid in fid_l:
            uri = 'brocade-fabric/fabric-switch'
            obj = brcdapi_rest.get_request(session, uri, fid)
            _process_errors(session, uri, obj, chassis_obj)
            results_action(chassis_obj, obj, uri)
        return chassis_obj
    except:
        _process_errors(session, uri, session, proj_obj)
        return None


def login(user_id, pw, ip_addr, https='none', proj_obj=None):
    """Log in and capture a list of supported modules.

    :param user_id: User ID
    :param pw: Password
    :param ip_addr: IP address
    :param https: If 'CA' or 'self', uses https to login. Otherwise, http.
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.project.ProjectObj, None
    :type user_id: str
    :type pw: str
    :type ip_addr: str
    :type https: str
    :return: flag, session
    :rtype: dict
    """
    # Attempt to log in
    tip = brcdapi_util.mask_ip_addr(ip_addr, True)
    session = brcdapi_rest.login(user_id, pw, ip_addr, https)
    if pyfos_auth.is_error(session):
        brcdapi_log.log(tip + ' Login failed', True)
        _process_errors(session, '/rest/login', session, proj_obj)
        return session
    else:
        brcdapi_log.log(tip + ' Login succeeded', True)

    # Figure out what modules this FOS version supports
    # Step 1: Read all the module information from FOS
    uri = 'brocade-module-version'
    obj = brcdapi_rest.get_request(session, uri)
    if pyfos_auth.is_error(obj):
        brcdapi_log.log(tip + ' ERROR: ' + uri + '\n' + pyfos_auth.formatted_error_msg(obj), True)
        return session

    # Step 2: Parse the module information and add it to the session object
    kpi_list = []
    for mod_obj in obj.get(uri).get('module'):
        name = mod_obj.get('name')
        if name is None:
            brcdapi_log.exception("'name' mising in brocade-module-version", True)
            continue
        kpi_list.append(name)
        try:  # I think 'object' will always be there, just empty when there are no objects. Try/Except just in case.
            for mod_object in mod_obj.get('objects').get('object'):
                kpi_list.append(name + '/' + mod_object)
        except:
            pass
    session.update({'supported_uris': kpi_list})

    return session


def get_rest(session, uri, wobj=None, fid=None):
    """Wraps loging around a call to brcdapi_rest.get_request()

    :param session: Session object returned from brcdapi.pyfos_auth.login()
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
    brcdapi_log.log('GET: ' + uri + brcdapi_rest.vfid_to_str(fid), True)
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
    # RNID data is matched to a port by the link address. A GET request for brocade-fibrechannel/fibrechannel must be
    # done first to find the port object.
    fc_addr = port.get('link-address') + '00'
    for port_obj in objx.r_port_objects():
        port_addr = port_obj.r_get('fibrechannel/fcid-hex')
        if port_addr is not None and port_addr == fc_addr:
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
# All of the case methods add to brcddb.classes objects


def _convert_ip_addr(obj):
    if isinstance(obj, dict):
        d = {}
        for k, v in obj.items():
            d.update({k: _convert_ip_addr(v)})
        return d
    elif isinstance(obj, (list, tuple)):
        return [_convert_ip_addr(v) for v in obj]
    else:
        return brcdapi_util.mask_ip_addr(obj)


def _update_brcddb_obj_from_list(objx, obj, uri, sl=[]):
    """Adds a FOS API request response that is a list. Each item in the list is added to a brcddb class object

    All parameters as in comments above except:
    :param sl: Skip list. List of elements to not add to objx
    :type sl: list, tuple
    """
    global _GEN_CASE_ERROR_MSG

    try:
        tl = uri.split('/')
        d = objx.r_get(tl[0])
        if d is None:
            d = {}
            objx.s_new_key(tl[0], d)
        d1 = d.get(tl[1])
        if d1 is None:
            d1 = {}
            d.update({tl[1]: d1})
        for k in obj:
            if k not in sl:
                v1 = obj.get(k)
                if k in _ip_list:
                    d1.update({k: _convert_ip_addr(v1)})
                else:
                    d1.update({k: v1})
    except:
        brcdapi_log.exception(_GEN_CASE_ERROR_MSG, True)
        objx.r_project_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_PROGRAM_ERROR, None,
                                         _GEN_CASE_ERROR_MSG, '')
        try:
            objx.r_project_obj().s_warn_flag()
        except:
            try:
                objx.s_warn_flag()
            except:
                pass


# Case methods for rest_methods
def _update_brcddb_obj(objx, obj, uri):
    global _GEN_CASE_ERROR_MSG

    if objx is None:
        return  # This happens when fabric information is polled from a switch but the principal fabric switch wasn't
                # polled and we don't know what the principal fabric switch WWN is.

    try:
        tl = uri.split('/')
        d = objx.r_get(tl[0])
        if d is None:
            d = {}
            objx.s_new_key(tl[0], d)
        for k in obj:
            v1 = obj.get(k)
            if k in _ip_list:
                d.update({k: _convert_ip_addr(v1)})
            else:
                d.update({k: v1})
    except:
        brcdapi_log.exception(_GEN_CASE_ERROR_MSG, True)
        objx.r_project_obj().s_add_alert(al.AlertTable.alertTbl, al.ALERT_NUM.PROJ_PROGRAM_ERROR, None,
                                         _GEN_CASE_ERROR_MSG, '')
        try:
            objx.r_project_obj().s_warn_flag()
        except:
            try:
                objx.s_warn_flag()
            except:
                pass


def _null_case(objx, obj, uri):
    return


def _fabric_case(objx, obj, uri):
    _update_brcddb_obj(objx.r_fabric_obj(), obj, uri)


def _defined_zonecfg_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    if fab_obj is None:
        return  # The switch is not in a fabric if it's disabled. We also get here if the principal switch is unkonwn
    dobj = obj.get('defined-configuration')
    if dobj is not None:
        for zobj in brcddb_util.convert_to_list(dobj.get('cfg')):
            zonecfg_obj = fab_obj.s_add_zonecfg(zobj.get('cfg-name'), zobj.get('member-zone').get('zone-name'))
            _update_brcddb_obj(zonecfg_obj, zobj, uri)
        for zobj in brcddb_util.convert_to_list(dobj.get('zone')):
            if 'member-entry' in zobj:
                mem_list = zobj.get('member-entry').get('entry-name')
                pmem_list = zobj.get('member-entry').get('principal-entry-name')
            else:
                mem_list = None
                pmem_list = None
            zone_obj = fab_obj.s_add_zone(zobj.get('zone-name'), zobj.get('zone-type'), mem_list, pmem_list)
        for zobj in brcddb_util.convert_to_list(dobj.get('alias')):
            mem_list = zobj.get('member-entry').get('alias-entry-name') if 'member-entry' in zobj else None
            alais_obj = fab_obj.s_add_alias(zobj.get('alias-name'), mem_list)


def _effective_zonecfg_case(objx, obj, uri):
    if 'effective-configuration' in obj:  # None when there is no zone configuration enabled
        fab_obj = objx.r_fabric_obj()
        if fab_obj is None:
            return  # This happens when the principal switch in the fabric is unknown.
        dobj = obj.get('effective-configuration')
        if not isinstance(dobj, dict):
            return
        _update_brcddb_obj_from_list(fab_obj, dobj, uri, ['enabled-zone'])
        for zobj in brcddb_util.convert_to_list(dobj.get('enabled-zone')):
            if 'member-entry' in zobj:
                zone_obj = fab_obj.s_add_eff_zone(zobj.get('zone-name'), zobj.get('zone-type'),
                            zobj.get('member-entry').get('entry-name'),
                            zobj.get('member-entry').get('principal-entry-name'))
            else:  # I don't know how there can be items in the enabled-zone without a 'member-entry'. Just in case ...
                zone_obj = fab_obj.s_add_eff_zone(zobj.get('zone-name'))
            _update_brcddb_obj(zone_obj, zobj, uri)
        fab_obj.s_add_eff_zonecfg(fab_obj.r_eff_zone_keys())


def _add_switch_to_chassis_int(chassis_obj, switch, uri, switch_wwn):
    switch_obj = chassis_obj.s_add_switch(switch_wwn)
    _update_brcddb_obj_from_list(switch_obj, switch, uri)

    # Add the ports
    try:
        for port in brcddb_util.convert_to_list(switch.get('port-member-list').get('port-member')):
            switch_obj.s_add_port(port)
    except:
        pass

    # Add the GE ports
    try:
        for port in brcddb_util.convert_to_list(switch.get('ge-port-member-list').get('port-member')):
            switch_obj.s_add_ge_port(port)
    except:
        pass


def _add_fab_switch_to_chassis_case(chassis_obj, obj, uri):
    proj_obj = chassis_obj.r_project_obj()
    fab_obj = None
    sl = []
    for switch in brcddb_util.convert_to_list(obj.get(uri.split('/').pop())):
        c_obj = proj_obj.s_add_chassis(switch.get('chassis-wwn'))
        s_wwn = switch.get('name')
        switch_obj = c_obj.s_add_switch(s_wwn)
        sl.append(switch_obj)
        _update_brcddb_obj_from_list(switch_obj, switch, uri)
        if switch.get('principal'):
            fab_obj = proj_obj.s_add_fabric(s_wwn)
    if fab_obj is not None:
        for switch_obj in sl:
            switch_obj.s_fabric_key(fab_obj.r_obj_key())
            fab_obj.s_add_switch(switch_obj.r_obj_key())


def _add_ls_switch_to_chassis_case(chassis_obj, obj, uri):
    existing_switch_wwns = chassis_obj.r_switch_keys()
    for switch in brcddb_util.convert_to_list(obj.get(uri.split('/').pop())):
        wwn = switch.get('switch-wwn')
        if wwn in existing_switch_wwns:
            continue  # The switch is already there. This method is not intended to modify an existing switch object
        switch_obj = chassis_obj.s_add_switch(wwn)
        _update_brcddb_obj_from_list(switch_obj, switch, uri)
        try:
            for port in brcddb_util.convert_to_list(switch.get('port-member-list').get('port-member')):
                switch_obj.s_add_port(port)
        except:
            pass
        try:
            for port in brcddb_util.convert_to_list(switch.get('ge-port-member-list').get('port-member')):
                switch_obj.s_add_ge_port(port)
        except:
            pass


def _fabric_switch_case(switch_obj, obj, uri):
    proj_obj = switch_obj.r_project_obj()
    tl = uri.split('/')
    leaf = tl[len(tl)-1]
    wwn_ref = 'switch-wwn' if leaf == 'fibrechannel-logical-switch' else 'name'
    for switch in brcddb_util.convert_to_list(obj.get('fibrechannel-switch')):
        wwn = switch.get(wwn_ref)
        if brcddb_util.is_wwn(wwn):  # Yes, got bit by a bad WWN once
            s_obj = proj_obj.s_add_switch(wwn)
            if switch.get('principal'):
                fab_obj = proj_obj.s_add_fabric(wwn)
            _update_brcddb_obj_from_list(switch_obj, switch, uri)
        else:
            brcdapi_log.log('Bad switch WWN, , returned from ' + uri + ' for switch ' +
                            brcddb_switch.best_switch_name(switch_obj), True)


def _switch_from_list_case(switch_obj, obj, uri):
    try:
        _update_brcddb_obj_from_list(switch_obj, brcddb_util.convert_to_list(obj.get(uri.split('/').pop()))[0], uri)
        if switch_obj.r_is_principal():
            switch_obj.r_project_obj().s_add_fabric(switch_obj.r_obj_key())
    except:
        pass


def _fabric_ns_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for ns_obj in brcddb_util.convert_to_list(obj.get('fibrechannel-name-server')):
        login_obj = fab_obj.s_add_login(ns_obj.get('port-name'))
        _update_brcddb_obj(login_obj, ns_obj, uri)


def _fabric_fdmi_hba_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for obj in brcddb_util.convert_to_list(obj.get('hba')):
        try:
            for wwn in obj.get('hba-port-list').get('wwn'):
                fab_obj.s_add_fdmi_port(wwn)
        except:
            pass
        _update_brcddb_obj(fab_obj.s_add_fdmi_node(obj.get('hba-id')), obj, uri)


def _fabric_fdmi_port_case(objx, obj, uri):
    fab_obj = objx.r_fabric_obj()
    for obj in brcddb_util.convert_to_list(obj.get('port')):
        _update_brcddb_obj(fab_obj.s_add_fdmi_port(obj.get('port-name')), obj, uri)


def _switch_port_case(objx, obj, uri):
    """Parses port data into the switch object

    :param objx: Switch object
    :type objx: brcddb.classes.switch.SwitchObj
    :param obj: Object returned from the API
    :type obj: dict
    """
    tl = uri.split('/')
    leaf = tl[len(tl)-1]
    for port in brcddb_util.convert_to_list(obj.get(leaf)):
        port_obj = _port_case_case[leaf](objx, port)
        if port_obj is not None:
            d = port_obj.r_get(leaf)
            if d is None:
                port_obj.s_new_key(leaf, {})
                d = port_obj.r_get(leaf)
            for k, v in port.items():
                d.update({k: v})


def _fru_blade_case(objx, obj, uri):
    global _ip_list

    new_obj = {}
    for k, v in obj.items():
        if isinstance(v, list) and k == 'blade':
            new_list = []
            for d in v:
                new_d = {}
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


_custom_rest_methods = {  # Normally, all data returned from the API is stored in the object by calling the methods in
                # _rest_methods. These methods are for non-standard handling of URIs.
    # Fabric
    'brocade-fabric/fabric-switch': _add_fab_switch_to_chassis_case,
    'brocade-fibrechannel-switch/fibrechannel-switch': _switch_from_list_case,
    'brocade-fdmi/hba': _fabric_fdmi_hba_case,
    'brocade-fdmi/port': _fabric_fdmi_port_case,
    'brocade-name-server/fibrechannel-name-server': _fabric_ns_case,
    'brocade-zone/defined-configuration': _defined_zonecfg_case,
    'brocade-zone/effective-configuration': _effective_zonecfg_case,
    'brocade-fru/blade': _fru_blade_case,
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


def results_action(brcddb_obj, fos_obj, kpi):
    """Updates the brcddb database for an API request response.

    :param brcddb_obj: brcddb class librairy object
    :type brcddb_obj: brcddb.classes.*
    :param fos_obj: Object returned from the API
    :type fos_obj: dict
    :param kpi: KPI associated with fos_obj
    :type kpi: str
    """
    global _custom_rest_methods, _rest_methods

    if not pyfos_auth.is_error(fos_obj):
        try:
            if kpi in _custom_rest_methods:
                _custom_rest_methods[kpi](brcddb_obj, fos_obj, kpi)
            else:
                _rest_methods[brcdapi_util.uri_map[kpi]['area']](brcddb_obj, fos_obj, kpi)
        except:
            buf = 'Could not add ' + kpi + ' to ' + str(type(brcddb_obj)) + '. This typially occurs when something '
            buf += 'for the fabric was polled but the fabric WWN is unkonwn.'
            brcdapi_log.log(buf, True)


def get_batch(session, proj_obj, kpi_list, fid=None):
    """Processes a batch API requests. All chassis request are performed first, followed by processing of fid_rest_data

    If any warnings or errors are encountered, the log is updated and the appropriate flag bits for the proj_obj are
    set. Search for _project_warn in brcddb_common.py for additional information. Again, search for _project_warn in
    brcddb.classes for object methods to set and check these bits.
    :param session: Session object, or list of session objects, returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param proj_obj: Project object
    :type proj_obj: brcddb.classes.ProjectObj
    :param kpi_list: List of KPIs to request from the switches and chassis
    :type kpi_list: list
    :param fid: FID, or list of FIDs for logical switch level requests. If None, execute requests for all FIDs.
    :type fid: int, list, tuple, None
    :rtype: None
    """
    # Get the chassis object
    chassis_obj = get_chassis(session, proj_obj)
    if chassis_obj is None:
        brcdapi_log.log(brcdapi_util.mask_ip_addr(session.get('ip_addr')) + 'Chassis not found.', True)
        return

    kl = brcddb_util.convert_to_list(kpi_list)

    # Get all the chassis data
    for kpi in [kpi for kpi in kl if not brcdapi_util.uri_map[kpi]['fid']]:
        results_action(chassis_obj, get_rest(session, kpi, chassis_obj), kpi)

    # Figure out which logical switches to poll switch level data from.
    if chassis_obj.r_is_vf_enabled() and fid is not None:
        fid_list = brcddb_util.convert_to_list(fid)
        switch_list = [obj for obj in chassis_obj.r_switch_objects() if brcddb_switch.switch_fid(obj) in fid_list]
    else:
        switch_list = chassis_obj.r_switch_objects()

    # Now process all the switch (FID) level commands.
    for switch_obj in switch_list:
        for kpi in [kpi for kpi in kl if brcdapi_util.uri_map[kpi]['fid']]:
            results_action(switch_obj,
                           get_rest(session, kpi, switch_obj, brcddb_switch.switch_fid(switch_obj)), kpi)
