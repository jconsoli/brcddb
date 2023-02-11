#!/usr/bin/python
# -*- coding: utf-8 -*-
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
:mod:`switch_config.py` -

$ToDo running/brocade-fibrechannel-switch/fibrechannel-switch/principal (0 for no, 1 for yes)

To set it:

PATCH running/brocade-fibrechannel-configuration/fabric

principal-selection-enabled - boolean
principal-priority - hex value. See options for fabricprincipal -priority

Look for insistent-domain-id-enabled

**Description**

    Although FOS doesn't care what order the port bind commands are in, humans like to see them in port order. I'm not
    using the brcddb.class objects for anything but since there is a utility to sort the port objects by port number,
    I'm leveraging that to sort the ports. Note that you can't just do a .sort() on the list because it does an ASCII
    sort which isn't how you expect the numerical values in s/p to be sorted.

    Adding the ports to the logical switch in sorted order will also result in the default addresses being in order.
    This is useful if you are not going to force the address by binding specified addresses to the ports. The fabric
    only cares that the port addresses are unique but again, humans like to see everything in order.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.0.0     | 31 Dec 2020   | Initial launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.1     | 09 Jan 2021   | Open log file.                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.2     | 13 Feb 2021   | Added # -*- coding: utf-8 -*-                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.3     | 16 Nov 2021   | Fixed call to brcdapi.port.enable_ports()                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.4     | 31 Dec 2021   | Use brcddb.util.file.full_file_name()                                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.5     | 28 Apr 2022   | Used full URI                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.6     | 26 May 2022   | Disabled debug mode (_DEBUG)                                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.7     | 22 Jun 2022   | Replaced CLI port address binding with API based port address binding introduced  |
    |           |               | in FOS 9.1.                                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.8     | 25 Jul 2022   | Added module version number to output.                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.0.9     | 14 Oct 2022   | Fixed case when there is no chassis configuration worksheet.                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.1.0     | 01 Jan 2023   | Added POD license reserve for ports added to fixed port switches. Used revised    |
    |           |               | keys returned from brcddb.report.utils.parse_switch_file                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.1.1     | 14 Jan 2023   | Made port moves more efficient when configuring multiple logical switches.        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 1.1.2     | 11 Feb 2023   | Added port naming configuration                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022, 2023 Jack Consoli'
__date__ = '11 Feb 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '1.1.2'

import argparse
import sys
import datetime
import os
import pprint
import brcdapi.log as brcdapi_log
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.switch as brcdapi_switch
import brcdapi.fos_auth as fos_auth
import brcdapi.port as brcdapi_port
import brcdapi.util as brcdapi_util
import brcdapi.file as brcdapi_file
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.report.utils as report_utils
import brcddb.api.interface as api_int
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_port as brcddb_port
import brcddb.brcddb_switch as brcddb_switch

_DOC_STRING = False  # Should always be False. Prohibits any code execution. Only useful for building documentation
_DEBUG = False  # When True, use _DEBUG_xxx instead of passed arguments
_DEBUG_ip = 'xx.xxx.xx.xx'
_DEBUG_id = 'admin'
_DEBUG_pw = 'password'
_DEBUG_s = 'self'
_DEBUG_i = 'test/gsh'
_DEBUG_force = False
_DEBUG_sup = False
_DEBUG_echo = True
_DEBUG_d = False
_DEBUG_log = '_logs'
_DEBUG_nl = False

_fc_switch = 'running/brocade-fibrechannel-switch/fibrechannel-switch'
_fc_switch_config = 'running/brocade-fibrechannel-configuration/switch-configuration'
_fc_switch_port = 'running/brocade-fibrechannel-configuration/port-configuration'
_fc_ficon_cup = 'running/brocade-ficon/cup'
_basic_capture_kpi_l = [
    # 'running/brocade-fabric/fabric-switch',  Done automatically in brcddb.api.interface.get_chassis()
    _fc_switch,
    _fc_switch_config,
    _fc_switch_port,
    _fc_ficon_cup,
    'running/brocade-interface/fibrechannel',
]


def _configuration_checks(switch_d_list):
    """Some basic chassis configuration checks.

    :param switch_d_list: List of switch object as returned from report_utils.parse_switch_file()
    :type switch_d_list: list
    :return: List of error messages. List is empty if no errors found
    :rtype: list
    """
    rl, base_l = list(), list()

    # Note: duplicate FID checking is done in brcddb.report.utils.parse_switch_file() so there is no need to do it here.
    for switch_d in switch_d_list:
        switch_did = gen_util.get_key_val(switch_d, _fc_switch+'/domain-id')

        if switch_d['switch_info']['switch_type'] == 'base':
            base_l.append(switch_d)  # Used to check for, and report if necessary, duplicate base switches

        # Does the domain ID in the switch definition match the domain ID in the port worksheets?
        # When written, rl_index will always be 0 here. This was setup so that message could be added to rl prior to
        # getting here.
        rl_index = len(rl)
        for port_d in switch_d['port_d'].values():
            port_did = port_d.get('did')
            if isinstance(port_did, int) and port_did != switch_did:
                rl.append('  ' + port_d['port'] + ' DID: ' + str(port_did))
        if len(rl) > rl_index:
            buf = 'The switch DID, ' + str(switch_did) + ', for ' + switch_d['switch_info']['sheet_name'] + \
                  ' does not match the DID for the following ports:'
            rl.insert(rl_index, buf)

        # Does the banner contain any invalid characters?
        banner = gen_util.get_key_val(switch_d, _fc_switch+'/banner')
        if banner is not None:
            v_banner = gen_util.valid_banner.sub('-', banner)
            if banner != v_banner:
                # Fix and report the issue. Note that by appending the error to switch_d rather than rl allows the
                # script to continue running. This isn't a big enough problem to halt processing.
                gen_util.add_to_obj(switch_d, _fc_switch+'/banner', v_banner)
                buf = 'Invalid characters in banner for FID on ' + switch_d['switch_info']['sheet_name'] +\
                      '. Replaced invalid characters with "-"'
                switch_d['err_msgs'].append(buf)

    # Check for > 1 base switch
    if len(base_l) > 1:
        rl.append('Multiple base switches defined:')
        rl.extend(['  ' + switch_d['switch_info']['sheet_name'] for switch_d in base_l])

    return rl


def _configure_chassis(session, chassis_d):
    """Configure, create if necessary, a logical switch

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_d: Switch object as returned from report_utils.parse_switch_file()
    :type chassis_d: dict
    :return: Completion code - see brcddb.common
    :rtype: int
    """
    if chassis_d is None:
        return brcddb_common.EXIT_STATUS_OK  # No chassis level changes to make
    for kpi, content in chassis_d.items():
        tl = kpi.split('/')
        content_d = {tl[len(tl)-1]: content} if tl[0] == 'running' else content
        obj = brcdapi_rest.send_request(session, kpi, 'PATCH', content_d)
        if fos_auth.is_error(obj):
            brcdapi_log.exception(['Error processing ' + kpi + 'Error is: ',
                                   fos_auth.formatted_error_msg(obj),
                                   'chassis_d:',
                                   pprint.pformat(chassis_d)],
                                  echo=True)
            return brcddb_common.EXIT_STATUS_API_ERROR

    return brcddb_common.EXIT_STATUS_OK


def _ports_to_move(switch_obj, switch_d, force):
    """Determine what ports are where and where they should be moved to and add the following to switch_d:

    +-------------------+-------------------------------------------------------------------------------------------|
    | Key               |                                                                                           |
    +===================+===========================================================================================|
    | not_found_port_l  | List of ports in s/p notation do not exist in the chassis.                                |
    +-------------------+-------------------------------------------------------------------------------------------|
    | online_port_l     | List of ports in s/p notation that were not moved because they were online                |
    +-------------------+-------------------------------------------------------------------------------------------|
    | remove_port_l     | List of ports in s/p notation that need to be removed from the switch                     |
    +-------------------+-------------------------------------------------------------------------------------------|
    | remove_ge_port_l  | Not Yet Implemented. Intended for: List of GE ports in s/p notation that need to be       |
    |                   | removed from the switch                                                                   |
    +-------------------+-------------------------------------------------------------------------------------------|
    | add_port_l        | List of ports in s/p notation that need to be added to the switch                         |
    +-------------------+-------------------------------------------------------------------------------------------|
    | add_ge_port_l     | Not Yet Implemented. Intended for: List of GE ports in s/p notation that need to be added |
    |                   | to the switch                                                                             |
    +-------------------+-------------------------------------------------------------------------------------------|
    | already_present_l | List of ports in s/p notation to add but were already in the switch                       |
    +-------------------+-------------------------------------------------------------------------------------------|

    :param switch_obj: Switch object of the switch being configured
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param switch_d: Switch object as returned from report_utils.parse_switch_file()
    :type switch_d: dict
    :param force: Move the port whether it's online or not.
    :type force: bool
    """
    switch_d.update(not_found_port_l=list(), online_port_l=list(), remove_port_l=list(), remove_ge_port_l=list(),
                    add_port_l=list(), add_ge_port_l=list(), already_present_l=list())
    chassis_obj = switch_obj.r_chassis_obj()
    switch_pl = switch_obj.r_port_keys()

    for port_type in [k for k in ('port_d', 'ge_port_d') if k in switch_d]:
        
        # Figure out which ports to remove
        for port in [p for p in switch_pl if p not in switch_d[port_type]]:
            port_obj = chassis_obj.r_port_obj(port)
            if port_obj is None:
                switch_d['not_found_port_l'].append(port)
            elif not force and port_obj.r_is_online():
                switch_d['online_port_l'].append(brcddb_port.best_port_name(port_obj, True) + ', ' +
                                                brcddb_port.port_best_desc(port_obj))
            else:
                switch_d['remove_port_l'].append(port)

        # Figure out what ports to add
        for port in switch_d[port_type]:
            if port in switch_pl:
                switch_d['already_present_l'].append(port)
                continue
            port_obj = chassis_obj.r_port_obj(port)  # Make sure the port is present in the chassis
            if port_obj is None:
                switch_d['not_found_port_l'].append(port)
            elif port_obj.r_is_online():
                switch_d['online_port_l'].append(port)
            elif switch_obj.r_port_obj(port) is None:  # Make sure the port isn't already in the switch
                switch_d['add_port_l'].append(port)


def _create_switch(session, chassis_obj, switch_d, echo):
    """Creates a logical switch

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d: Switch object as returned from report_utils.parse_switch_file()
    :type switch_d: dict
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    """
    global _basic_capture_kpi_l

    fid = switch_d['switch_info']['fid']
    if chassis_obj.r_switch_obj_for_fid(fid) is not None:
        return brcddb_common.EXIT_STATUS_OK  # The switch already exists
    buf = 'Creating FID ' + str(fid) + '. This will take about 20 sec per switch + 25 sec per group of 32 ports.'
    brcdapi_log.log(buf, echo=True)
    base = True if switch_d['switch_info']['switch_type'] == 'base' else False
    ficon = True if switch_d['switch_info']['switch_type'] == 'ficon' else False
    obj = brcdapi_switch.create_switch(session, fid, base, ficon, echo=echo)
    if fos_auth.is_error(obj):
        switch_d['err_msgs'].append('Error creating FID ' + str(fid))
        brcdapi_log.exception([switch_d['err_msgs'][len(switch_d['err_msgs']) - 1],
                               fos_auth.formatted_error_msg(obj),
                               'switch_d:',
                               pprint.pformat(switch_d)],
                              echo=True)
        return brcddb_common.EXIT_STATUS_API_ERROR

    return brcddb_common.EXIT_STATUS_OK


def _fiberchannel_switch(session, switch_obj, switch_d, echo):
    """Set switch configuration parameters for brocade-fibrechannel-switch/fibrechannel-switch.

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param switch_d: Switch object as returned from report_utils.parse_switch_file()
    :type switch_d: dict
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    :return: Status code. See brcddb.common.EXIT_STATUS_*
    :rtype: int
    """
    global _fc_switch

    # Load common use stuff into local variables
    ec = brcddb_common.EXIT_STATUS_OK
    fid = switch_d['switch_info']['fid']

    # Set switch configuration parameters for brocade-fibrechannel-switch/fibrechannel-switch.
    sub_content = dict()
    prefix = _fc_switch.replace('running/', '') + '/'
    api_d = gen_util.get_key_val(switch_d, _fc_switch)
    if isinstance(api_d, dict):
        for k, v in api_d.items():
            current_v = switch_obj.r_get(prefix+k)
            if v is not None:
                if type(current_v) != type(v) or current_v != v:  # We're only sending changes (PATCH)
                    sub_content.update({k: v})
    if len(sub_content) > 0:
        obj = brcdapi_switch.fibrechannel_switch(session, fid, sub_content, wwn=switch_obj.r_obj_key(), echo=echo)
        if fos_auth.is_error(obj):
            buf = 'Failed to configure fibrechannel-switch parameters for FID ' + str(fid)
            switch_d['err_msgs'].append(buf)
            brcdapi_log.exception([buf,
                                   fos_auth.formatted_error_msg(obj),
                                   'switch_d:',
                                   pprint.pformat(switch_d)],
                                  echo=True)
            ec = brcddb_common.EXIT_STATUS_API_ERROR

    return ec


def _switch_config(session, switch_obj, switch_d, echo):
    """Set the fabric parameters: brocade-fibrechannel-configuration/switch-configuration. See _fiberchannel_switch()
    for input and output parameter definitions."""
    global _fc_switch_config, _fc_switch_port

    # Load common use stuff into local variables
    ec = brcddb_common.EXIT_STATUS_OK
    fid = switch_d['switch_info']['fid']
    brcdapi_log.log('Configuring FID: ' + str(fid), echo=echo)

    # Set the fabric parameters: brocade-fibrechannel-configuration/switch-configuration
    sub_content = dict()
    for url in (_fc_switch_config, _fc_switch_port):
        prefix = url.replace('running/', '') + '/'
        api_d = gen_util.get_key_val(switch_d, url)
        if isinstance(api_d, dict):
            for k, v in api_d.items():
                current_v = switch_obj.r_get(prefix+k)
                if v is not None:
                    if type(current_v) != type(v) or current_v != v:  # We're only sending changes (PATCH)
                        sub_content.update({k: v})
        if len(sub_content) > 0:
            obj = brcdapi_rest.send_request(session,
                                            url,
                                            'PATCH',
                                            {url.split('/').pop(): sub_content},
                                            fid)
            if fos_auth.is_error(obj):
                buf = 'Failed to configure switch-configuration parameters for FID ' + str(fid)
                switch_d['err_msgs'].append(buf)
                brcdapi_log.exception([buf,
                                       'Sheet: ' + switch_d['switch_info']['sheet_name'],
                                       fos_auth.formatted_error_msg(obj),
                                       'switch_d:',
                                       pprint.pformat(switch_d)],
                                      echo=True)
                ec = brcddb_common.EXIT_STATUS_API_ERROR

    return ec


def _ficon_config(session, switch_obj, switch_d, echo):
    """Set the fabric parameters: brocade-fibrechannel-configuration/switch-configuration. See _fiberchannel_switch()
    for input and output parameter definitions."""
    global _fc_ficon_cup

    # Load common use stuff into local variables
    ec = brcddb_common.EXIT_STATUS_OK
    fid = switch_d['switch_info']['fid']
    brcdapi_log.log('Configuring FICON parameters for FID: ' + str(fid), echo=echo)

    # Set the fabric parameters: brocade-fibrechannel-configuration/switch-configuration
    sub_content = dict()
    prefix = _fc_ficon_cup.replace('running/', '') + '/'
    api_d = gen_util.get_key_val(switch_d, _fc_ficon_cup)
    if isinstance(api_d, dict):
        for k, v in api_d.items():
            current_v = switch_obj.r_get(prefix+k)
            if v is not None:
                if type(current_v) != type(v) or current_v != v:  # We're only sending changes (PATCH)
                    sub_content.update({k: v})
    if len(sub_content) > 0:
        obj = brcdapi_rest.send_request(session, _fc_ficon_cup, 'PATCH', dict(cup=sub_content), fid)
        if fos_auth.is_error(obj):
            buf = 'Failed to configure FICON parameters for FID ' + str(fid)
            switch_d['err_msgs'].append(buf)
            brcdapi_log.exception([buf,
                                   'Sheet: ' + switch_d['switch_info']['sheet_name'],
                                   fos_auth.formatted_error_msg(obj),
                                   'switch_d:',
                                   pprint.pformat(switch_d)],
                                  echo=True)
            ec = brcddb_common.EXIT_STATUS_API_ERROR

    return ec


def _add_ports(session, chassis_obj, switch_d_l, echo):
    """Add and remove ports from a logical switch

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d_l: List of switch object as returned from report_utils.parse_switch_file()
    :type switch_d_l: list
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    :return: Ending status. See brcddb.common
    :rtype: int
    """
    ec = brcddb_common.EXIT_STATUS_OK

    for switch_d in switch_d_l:
        fid = switch_d['switch_info']['fid']
        switch_obj = chassis_obj.r_switch_obj_for_fid(fid)

        # Figure out what FID all the port to move are in so they can be moved by groups for each FID
        from_fid_d = dict()
        for port in switch_d['add_port_l']:
            from_fid = brcddb_switch.switch_fid(chassis_obj.r_port_obj(port).r_switch_obj())
            port_l = from_fid_d.get(from_fid)
            if port_l is None:
                port_l = list()
                from_fid_d.update({from_fid: port_l})
            port_l.append(port)

        # Add ports
        for from_fid, port_l in from_fid_d.items():
            obj = brcdapi_switch.add_ports(session, fid, from_fid, i_ports=port_l, echo=echo)
            if fos_auth.is_error(obj):
                buf = 'Error moving ports from FID ' + str(from_fid) + ' to ' + str(fid)
                switch_d['err_msgs'].append(buf)
                brcdapi_log.exception(['switch_d:',
                                       pprint.pformat(switch_d),
                                       buf,
                                       fos_auth.formatted_error_msg(obj)],
                                      echo=True)
                ec = brcddb_common.EXIT_STATUS_ERROR

    return ec


def _remove_ports(session, chassis_obj, switch_d_l, echo):
    """Add and remove ports from a logical switch

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d_l: List of switch object as returned from report_utils.parse_switch_file()
    :type switch_d_l: list
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    :return: Ending status. See brcddb.common
    :rtype: int
    """
    ec = brcddb_common.EXIT_STATUS_OK
    default_fid = chassis_obj.r_default_switch_fid()

    for switch_d in switch_d_l:
        fid = switch_d['switch_info']['fid']
        switch_obj = chassis_obj.r_switch_obj_for_fid(fid)

        # Remove ports - $ToDo brcdapi_switch.add_ports() doesn't remove GE ports
        port_l = [p for p in switch_d['remove_port_l'] if switch_obj.r_port_obj(p) is not None]
        obj = brcdapi_switch.add_ports(session, default_fid, fid, i_ports=port_l, echo=echo)
        if fos_auth.is_error(obj):
            buf = 'Error moving ports from FID ' + str('fid') + ' to ' + str(default_fid)
            switch_d['err_msgs'].append(buf)
            brcdapi_log.exception(['switch_d:',
                                   pprint.pformat(switch_d),
                                   buf,
                                   fos_auth.formatted_error_msg(obj)],
                                  echo=True)
            ec = brcddb_common.EXIT_STATUS_ERROR

    return ec


def _configure_ports(session, chassis_obj, switch_d_l, echo):
    """Configure the ports. In this version, only bind, port name, and reserve is supported.

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d_l: List of switch object as returned from report_utils.parse_switch_file()
    :type switch_d_l: list
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    :return: Ending status. See brcddb.common
    :rtype: int
    """
    ec = brcddb_common.EXIT_STATUS_OK

    for switch_d in switch_d_l:
        fid = switch_d['switch_info']['fid']
        port_d = switch_d['port_d']
        switch_obj = chassis_obj.r_switch_obj_for_fid(fid)

        # Reserve the ports
        port_l = list()
        for port in [str(p) for p in port_d.keys()]:  # Figure out which ports need to be reserved
            if '0/' not in port:
                break  # Port POD licenses only need to be reserved on fixed port switches
            port_obj = switch_obj.r_port_obj(port)
            if port_obj is not None and \
                    port_obj.r_get('') != 'running/brocade-interface/fibrechannel/pod-license-state' != 'reserved':
                # If the port doesn't exist in the chassis, it is reported in switch_d['not_found_port_l']. If the port
                # was already in the logical switch it may not have been reserved.
                port_l.append(port)
        if len(port_l) > 0:  # Reserve the POD licenses for the ports
            obj = brcdapi_port.reserve_pod(session, fid, port_l)
            if fos_auth.is_error(obj):
                buf = 'Error reserving ports for FID ' + str(fid)
                switch_d['err_msgs'].append(buf)
                ml = [buf,
                      fos_auth.formatted_error_msg(obj),
                      'port_d:',
                      pprint.pformat(port_d)]
                brcdapi_log.exception(ml, echo=True)

        # Bind the addresses (PIDs)
        if switch_d['switch_info']['bind']:
            bind_d = dict()
            for port, d in port_d.items():
                bind_d.update({port: '0x' + d['port_addr'] + '00'})
            if len(bind_d) > 0:
                obj = brcdapi_switch.bind_addresses(session, fid, bind_d, echo)
                if fos_auth.is_error(obj):
                    ml = ['port_d:',
                          pprint.pformat(port_d),
                          'Errors encountered binding port address for FID ' + str(fid),
                          fos_auth.formatted_error_msg(obj)]
                    brcdapi_log.exception(ml, echo=True)
                    ec = brcddb_common.EXIT_STATUS_ERROR

        # Name the ports
        content = [{'name': d1['port'], 'user-friendly-name': d1['port_name']} for d1 in
                   [d0 for d0 in port_d.values() if isinstance(d0.get('port_name'), str)]]
        if len(content) > 0:
            brcdapi_log.log('Naming ' + str(len(content)) + ' ports.', echo)
            obj = brcdapi_rest.send_request(session,
                                            'running/brocade-interface/fibrechannel',
                                            'PATCH',
                                            {'fibrechannel': content},
                                            fid)
            if fos_auth.is_error(obj):
                buf = 'Error naming ports for FID ' + str(fid)
                switch_d['err_msgs'].append(buf)
                ml = [buf,
                      fos_auth.formatted_error_msg(obj),
                      'port_d:',
                      pprint.pformat(port_d)]
                brcdapi_log.exception(ml, echo=True)

    return ec


def _enable_switch_and_ports(session, chassis_obj, switch_d_l, echo):
    """Enable the logical switches and ports

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d_l: List of switch object as returned from report_utils.parse_switch_file()
    :type switch_d_l: list
    :param echo: If True, echo switch configuration details to STD_OUT
    :type echo: bool
    :return: Ending status. See brcddb.common
    :rtype: int
    """
    global _basic_capture_kpi_l

    ec = brcddb_common.EXIT_STATUS_OK

    for switch_d in switch_d_l:
        fid = switch_d['switch_info']['fid']

        # Enable switch
        if switch_d['switch_info']['enable_switch']:
            obj = brcdapi_switch.fibrechannel_switch(session, fid, {'is-enabled-state': True}, None, echo)
            if fos_auth.is_error(obj):
                buf = 'Failed to enable FID ' + str(fid)
                switch_d['err_msgs'].append(buf)
                brcdapi_log.exception([buf, fos_auth.formatted_error_msg(obj)], echo=True)
                ec = brcddb_common.EXIT_STATUS_API_ERROR

    return ec


def _print_summary(chassis_obj, switch_d_list):
    """Enable switch

    :param chassis_obj: Chassis object
    :type chassis_obj: brcddb.classes.chassis.ChassisObj
    :param switch_d_list: List of switch dictionaries
    :type switch_d_list: list
    """
    ml = ['', 'Summary', '_______', '']
    for switch_d in switch_d_list:
        switch_obj = chassis_obj.r_switch_obj_for_fid(switch_d['switch_info']['fid'])
        try:
            ml.append('FID: ' + str(switch_d['switch_info']['fid']))
            ml.append('  Switch Name:             ' + brcddb_switch.best_switch_name(switch_obj, wwn=True))
            ml.append('  Ports Added:             ' + str(len(switch_d['add_port_l'])))
            ml.append('  Ports Removed:           ' + str(len(switch_d['remove_port_l'])))
            ml.append('  Online Ports Not Moved:  ' + str(len(switch_d['online_port_l'])))
            ml.append('  Ports Not Found:         ' + str(len(switch_d['not_found_port_l'])))
            ml.append('  Ports Already in Switch: ' + str(len(switch_d['already_present_l'])))
            if len(switch_d['err_msgs']) > 0:
                ml.append('  Error Messages:         ')
                ml.extend(['    ' + buf for buf in switch_d['err_msgs']])
        except:
            brcdapi_log.exception(['Malformed "switch_d":', pprint.pformat(switch_d)], echo=True)
    brcdapi_log.log(ml, echo=True)


def _get_input():
    """Retrieves the command line input, minimally validates the input, and sets up logging

    :return args_ip: IP address
    :rtype args_ip: str
    :return args_id: User ID
    :rtype args_id: str
    :return args_pw: Password
    :rtype args_pw: str
    :return args_f: Name of output file
    :rtype args_f: str
    :return args_s: Type of HTTP security. Should be 'none' or 'self'
    :rtype args_s: str
    :return args_i: Name of switch configuratyion workbook
    :rtype args_i: str
    :return args_f: If True, move ports even if they are online
    :rtype args_f: bool
    :return args_echo: If True, echo switch configuration details to STD_OUT
    :rtype args_echo: bool
    """
    global _DEBUG, _DEBUG_ip, _DEBUG_id, _DEBUG_pw, _DEBUG_s, _DEBUG_i, _DEBUG_force, _DEBUG_sup, _DEBUG_echo,\
        _DEBUG_d, _DEBUG_log, _DEBUG_nl

    if _DEBUG:
        args_ip, args_id, args_pw, args_s, args_i, args_force, args_sup, args_echo, args_d, args_log, args_nl = \
            _DEBUG_ip, _DEBUG_id, _DEBUG_pw, _DEBUG_s, _DEBUG_i, _DEBUG_force, _DEBUG_sup, _DEBUG_echo, \
            _DEBUG_d, _DEBUG_log, _DEBUG_nl
    else:
        buf = 'Reads a switch configuration workbook and configures each logical switch accordingly.'
        parser = argparse.ArgumentParser(description=buf)
        parser.add_argument('-ip', help='(Required) IP address', required=True)
        parser.add_argument('-id', help='(Required) User ID', required=True)
        parser.add_argument('-pw', help='(Required) Password', required=True)
        buf = '(Optional) "self" for HTTPS mode. "none", for HTTP, is the default.'
        parser.add_argument('-s', help=buf, required=False,)
        parser.add_argument('-i', help='(Required) File name of Excel Workbook to read.', required=True)
        buf = '(Optional) No parameters. If specified, move ports even if they are online.'
        parser.add_argument('-force', help=buf, action='store_true', required=False)
        buf = '(Optional) Suppress all library generated output to STD_IO except the exit code. Useful with batch ' \
              'processing'
        parser.add_argument('-sup', help=buf, action='store_true', required=False)
        buf = '(Optional) Echoes activity detail to STD_OUT. Recommended because there are multiple operations that ' \
              'can be very time consuming.'
        parser.add_argument('-echo', help=buf, action='store_true', required=False)
        parser.add_argument('-d', help='Enable debug logging', action='store_true', required=False)
        buf = '(Optional) Directory where log file is to be created. Default is to use the current directory. The log '\
              'file name will always be "Log_xxxx" where xxxx is a time and date stamp.'
        parser.add_argument('-log', help=buf, required=False,)
        buf = '(Optional) No parameters. When set, a log file is not created. The default is to create a log file.'
        parser.add_argument('-nl', help=buf, action='store_true', required=False)
        args = parser.parse_args()
        args_ip, args_id, args_pw, args_s, args_i, args_force, args_sup, args_echo, args_d, args_log, args_nl = \
            args.ip, args.id, args.pw, args.s, args.i, args.force, args.sup, args.echo, args.d, args.log, args.nl

    # Set up the logging options
    if args_sup:
        brcdapi_log.set_suppress_all()
    if not args_nl:
        brcdapi_log.open_log(args_log)
    if args_d:
        brcdapi_rest.verbose_debug = True

    # User feedback
    ml = ['switch_config.py: ' + __version__,
          'File, -i:         ' + args_i,
          'IP address, -ip:  ' + brcdapi_util.mask_ip_addr(args_ip),
          'ID, -id:          ' + str(args_id),
          's, -s:            ' + args_s,
          'force, -force     ' + str(args_force),
          'echo, -echo       ' + str(args_echo)]
    if _DEBUG:
        ml.insert(0, 'WARNING!!! Debug is enabled')
    brcdapi_log.log(ml, echo=True)

    return args_ip, args_id, args_pw, args_s if args_s else 'none', brcdapi_file.full_file_name(args_i, '.xlsx'), \
           args_force, args_echo


def pseudo_main():
    """Basically the main().

    :return: Exit code
    :rtype: int
    """
    # Get and validate command line input.
    ec_l = [brcddb_common.EXIT_STATUS_OK]
    ip, user_id, pw, sec, file, force, echo = _get_input()

    # Read in the switch configuration Workbook
    brcdapi_log.log('Reading ' + file, echo=True)
    error_l, chassis_d, switch_d_list = report_utils.parse_switch_file(file)
    if chassis_d is None and len(switch_d_list) == 0:
        error_l.append('Nothing to configure')

    # Pre-flight switch checks
    error_l.extend(_configuration_checks(switch_d_list))

    # Bail out if any errors were encountered
    if len(error_l) > 0:
        brcdapi_log.log(error_l, echo=True)
        return brcddb_common.EXIT_STATUS_INPUT_ERROR

    # Get a project object
    proj_obj = brcddb_project.new('Create_LS', datetime.datetime.now().strftime('%d %b %Y %H:%M:%S'))
    proj_obj.s_python_version(sys.version)
    proj_obj.s_description('Creating logical switches from ' + os.path.basename(__file__))

    # Login
    session = api_int.login(user_id, pw, ip, sec, proj_obj)
    if fos_auth.is_error(session):  # Errors are sent to the log in api_int.login()
        return brcddb_common.EXIT_STATUS_API_ERROR

    try:

        # Read some basic chassis information. Primarily to see if defined switches and ports already exist
        api_int.get_batch(session, proj_obj, _basic_capture_kpi_l, None)
        if proj_obj.r_is_any_error():  # Error details are logged in api_int.get_batch()
            return brcddb_common.EXIT_STATUS_API_ERROR
        chassis_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn'))

        # Make chassis updates
        ec_l.append(_configure_chassis(session, chassis_d))

        # Create the logical switches
        for switch_d in switch_d_list:
            ec_l.append(_create_switch(session, chassis_obj, switch_d, echo))

        # re-read the chassis and logical switch data to pick up the switch(es) we just created.
        session.pop('chassis_wwn', None)
        api_int.get_batch(session, proj_obj, _basic_capture_kpi_l, None)
        chassis_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn'))

        # Configure the switches and fabric parameters
        for method in (_fiberchannel_switch, _switch_config, _ficon_config):
            for switch_d in switch_d_list:
                switch_obj = chassis_obj.r_switch_obj_for_fid(switch_d['switch_info']['fid'])
                if switch_obj is not None:  # Alert was posted during switch creation time if the switch wasn't created
                    ec_l.append(method(session, switch_obj, switch_d, echo))

        """ NOTE: _add_ports() must be called first. This was done for efficiency. Moving ports is time consuming. When
        configuring multiple switches, if a port is needed in another logical switch there is no point in moving it from
        the switch being worked on to the default switch only to later have to move it to another logical switch. Ports
        are added by moving them from whatever logical switch they are in to the one where they are needed. By adding
        ports to all logical switches first, only ports not used in any of the logical switches being created are moved
        to the default switch.
        
        I didn't think of this until after the code was written. To minimize changes to working code, I just built a
        list of all ports that will be added to a logical switch, all_add_l, and removed them from the remove_port_l."""
        all_add_l = list()
        for switch_d in switch_d_list:
            _ports_to_move(chassis_obj.r_switch_obj_for_fid(switch_d['switch_info']['fid']), switch_d, force)
            all_add_l.extend(switch_d['add_port_l'])
        for switch_d in switch_d_list:
            switch_d['remove_port_l'] = [p for p in switch_d['remove_port_l'] if p not in all_add_l]

        # Add ports, re-read chassis to pick up the changes, then do it again for ports to move to the default switch

        for method in (_add_ports, _remove_ports):
            ec_l.append(method(session, chassis_obj, switch_d_list, echo))
            session.pop('chassis_wwn', None)
            api_int.get_batch(session, proj_obj, _basic_capture_kpi_l, None)
            chassis_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn'))

        # Configure the ports, then enable the switch and ports
        for method in (_configure_ports, _enable_switch_and_ports):
            ec_l.append(method(session, chassis_obj, switch_d_list, echo))

    except BaseException as e:
        buf = 'Programming error encountered. Exception: '
        buf += str(e, errors='ignore') if isinstance(e, (bytes, str)) else str(type(e))
        if isinstance(switch_d, dict):
            switch_d['err_msgs'].append(buf)
        brcdapi_log.log(buf, echo=True)
        ec_l.append(brcddb_common.EXIT_STATUS_ERROR)

    # Logout and display a summary report
    if session is not None:
        obj = brcdapi_rest.logout(session)
        if fos_auth.is_error(obj):
            brcdapi_log.exception(fos_auth.formatted_error_msg(obj), echo=True)
            ec_l.append(brcddb_common.EXIT_STATUS_API_ERROR)
    if ip is not None:
        _print_summary(chassis_obj, switch_d_list)

    # Return the first error code, if there was an error
    for ec in ec_l:
        if ec != brcddb_common.EXIT_STATUS_OK:
            break
    return ec


###################################################################
#
#                    Main Entry Point
#
###################################################################
if _DOC_STRING:
    print('_DOC_STRING is True. No processing')
    exit(brcddb_common.EXIT_STATUS_OK)

_ec = pseudo_main()
brcdapi_log.close_log('Processing complete. Exit status: ' + str(_ec))
exit(_ec)
