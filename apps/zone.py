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
:mod:`zone` - Applies zoning changes to a fabric.

**Overview**

Performs zoning transactions on a per transaction basis or in bulk. Originally intended for use with a script written
to support an Ansible Playbook. Ansible Playbooks are usually expected to have a test mode so that the Playbook can
validate the actions before executing the Playbook. Due to Ansible container library restrictions in most shops, it
morphed into an example on how to zone via the API. Since there is a test mode, it also serves as an example on how to
use the brcddb database to validate the zoning. In fact, most of the code herein is dedicated to validating the zoning.

CLI was used because the CLI is most familiar to system administrators. It was also the most convenient to test the
zone library with since there is an abundance of CLI test scripts to use.

Error messages with FOS often provided limited information so one of the goals of the test mode was to provide more
detailed information when an error occurs.

When not in bulk mode, there are certainly ways to make the individual zoning more efficient. The intent was to keep
individual zoning simple and one for one so it can be used as an example. I'm assuming customers using CLI scripting
already have a script to execute those commands via an SSH session. This method does add more error checking with
verbose messages which could be useful but I suspect anyone using this method in a production environment would only do
so as an interim step towards a fully automated zoning solution.

These methods could be smarter as follows:

    * Bunch alias additions into a single request
    * Bunch zone create with zone add into a single request
    * Bunch zone configurations and the additions into a single request
    * When the force options is set, check to see if the object being updated is the same. Currently, with force set,
      when a zone exists it is deleted and then added back without checking to see if the object isn't changing.

**Important Zone Object Rename Notes**

There is no API equivalent to "zoneobjectrename". Renaming is accomplished by copying the object, modifying all zone
objects where used, and then deleting it. Note that more zone DB space is required with this approach.

Renaming the effective configuration is prohibited unless force is set. This is because in order to rename the effective
configuration in this manner, the defined configuration must be copied to a new configuration and then enabled before
deleting it. Since there may be other pending changes, this may have unintended consequences.

**Important Timing Notes**

Read (GET) happens very quickly but zone changes usually take around 400 msec per change. The delay is due to the need
to update the flash. It is the flash update operation, not the number of updates that take time. There is no significant
difference between making on zone change vs. 1000 zone changes in a single request. There is also about 2 seconds for
of additional overhead in this module for operations such as reading and saving the zone database.

Bulk zoning operations happen within a few seconds but, depending on the number of changes, a large batch of zone
changes can take significantly longer. If you are invoking this module from another module with a timeout, such as would
be the case with modules called from an Ansible Playbook, you need to be cognizant of how long the changes will take.

**Input**

    Data is input is a dictionary as follows:

    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | leaf      | Sub-leaf  | Type  | Description                                                                   |
    +===========+===========+=======+===============================================================================+
    | fid       |           | int   | Required. Fabric ID of switch in chassis where zoning changes are to be       |
    |           |           |       | applied                                                                       |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | ip-addr   |           | str   | Required. IP address of chassis                                               |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | id        |           | str   | Required. User ID                                                             |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | pw        |           | str   | Required. Password                                                            |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | sec       |           | str   | 'CA' or 'self' for HTTPS. If 'none', HTTP is used. Default: 'none'.           |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | force     |           | bool  | True - ignore warnings and overwrite existing objects. Default: True          |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | test      |           | bool  | True - ignores cfg-save. Only reads the zone database for validation          |
    |           |           |       | purposes. No zone changes are sent to the switch. Useful for validating       |
    |           |           |       | changes before applying them. Default: False                                  |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | changes   | list      |       | List of dictionaries as noted below. Unless file is specified, the baseline   |
    |           |           |       |zone DB is read from the switch matching fid.                                  |
    |           |           |       |                                                                               |
    |           |           |       | This should be set to the list returned from brcddb.util.util.parse_cli()     |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | c-type    | str   | Change type. Must be one of the keys in _change_type_func                     |
    |           |           |       |                                                                               |
    |           |           |       | Note that None is allowed. his was done to support a script that front ended  |
    |           |           |       | this with a simple CLI parser where the CLI file may have comments or blank   |
    |           |           |       | lines. This was done so that the index of commands matches the index of the   |
    |           |           |       | responses                                                                     |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | operand   | str   | Name associated with the operation specified in c-type. Zone name, alias      |
    |           |           |       | name, etc.                                                                    |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | p0        | list  | Parameters. For all zone operations, these are the members. For peer zones,   |
    |           |           |       | these are the non-principal members.                                          |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | p1        | list  | Similar to p0. Only used for peer zones. These are the principal members      |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | peer      | bool  | If true, zone is a peer zone.                                                 |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+

**Return**

    Data is returned in a dictionary as follows:

    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | leaf      | Sub-leaf  | Type  | Description                                                                   |
    +===========+===========+=======+===============================================================================+
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | summary   |           |       |                                                                               |
    |           | warnings  | int   | Summary number of warnings                                                    |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | errors    | int   | Summary number of errors                                                      |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | save      | bool  | True - the equivalent of cfgsave was done.                                    |
    |           |           |       | False - Zoning changes were not saved to the switch                           |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    | commands  |           | list  | This list matches the input list 'changes'. It is a list of dict with the     |
    |           |           |       | following members:                                                            |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | changed   | bool  | True - a change was made                                                      |
    |           |           |       | False - no change was made                                                    |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | fail      | bool  | True - encountered an error                                                   |
    |           |           |       | Fail - No errors encountered.                                                 |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | io        | bool  | True - Operation completed by performing an API request.                      |
    |           |           |       | False - No API request was made. This occurs when test is True or force is    |
    |           |           |       | True but no switch operation was                                              |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | status    | int   | Status, if any, returned from from the switch if a request was actually made. |
    |           |           |       | There will always be a status if the request failed but status is not always  |
    |           |           |       | returned for success. If io is False, the status is made up.                  |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | reason    | str   | Reason, if provided, returned from FOS. If io is False, the reason is made up.|
    +-----------+-----------+-------+-------------------------------------------------------------------------------+
    |           | err_msg   | list  | List of detailed error messages returned from FOS. If io is False, the        |
    |           |           |       | detailed messages are made up. Not always present with errors.                |
    +-----------+-----------+-------+-------------------------------------------------------------------------------+

**Public Methods**

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | refresh_zoning        | Deletes all zoning information from the fabric object and refreshes with new zoning   |
    |                       | data                                                                                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | send_zoning           | Entry point. Parses and dispatches all zoning operations                              |
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

import sys
import datetime
import copy
import brcdapi.util as brcdapi_util
import brcdapi.zone as brcdapi_zone
import brcdapi.fos_auth as fos_auth
import brcdapi.log as brcdapi_log
import brcdapi.brcdapi_rest as brcdapi_rest
import brcdapi.gen_util as gen_util
import brcddb.brcddb_project as brcddb_project
import brcddb.brcddb_common as brcddb_common
import brcddb.api.zone as api_zone
import brcddb.api.interface as api_int

_DEBUG_FICON = True

# Global arguments that get overwritten
_t_flag = False  # True - Test mode only - no changes actually sent to the switch
_f_flag = False  # True - over ride existing zone database
_b_flag = False  # True - perform bulk zoning
_fab_obj = None  # TODO- Make this a passed parameter
_checksum = None
_skip_pend_flag = False
_pending = list()    # List of pending zoning actions in the FOS zone transaction buffer
_good_test_return = dict(status=brcdapi_util.HTTP_OK, io=False, changed=True, fail=False)
_good_force_nop_return = dict(status=brcdapi_util.HTTP_OK, io=False, changed=False, fail=False)
_def_zone_access_tbl = {
    '--noaccess': brcddb_common.DEF_ZONE_NOACCESS,
    '--allaccess': brcddb_common.DEF_ZONE_ALLACCESS,
    '--show': -1,
}
# Zone URIs
_zone_uris = (
    'running/brocade-zone/defined-configuration',
    'running/brocade-zone/effective-configuration',
)


def _format_api_error(obj):
    """Formats an API response into the return dict

    :param obj: Returned object from an API call
    :type obj: dict
    """
    return dict(status=fos_auth.obj_status(obj),
                reason=fos_auth.obj_reason(obj),
                err_msg=fos_auth.obj_error_detail(obj),
                io=False,
                changed=False,
                fail=True)


def _format_cmd_for_brcdapi(cmd):
    """Convert the cmd dict structure used herein to the dict that the brcdapi zone library wants to see

    :param cmd: Dictionary element as described in **Input** -> changes
    :type cmd: dict
    :return: brcdapi.zone library data structure
    :rtype: dict
    """
    return dict(
        name=cmd['operand'],
        members=cmd['p0'],
        pmembers=cmd['p1'],
        type=brcddb_common.ZONE_USER_PEER if cmd['peer'] else brcddb_common.ZONE_STANDARD_ZONE,
    )


def _format_return(obj):
    """Creates the return dictionary

    :param obj: FOS API object
    :type obj: dict
    :return: Per command dictionary as defined in commands (See **Return** -> commands)
    :rtype: dict
    """
    if fos_auth.is_error(obj):
        return _format_api_error(obj)
    else:
        try:
            status = obj['_raw_data']['status']
        except KeyError:
            status = brcdapi_util.HTTP_OK
        try:
            reason = obj['_raw_data']['reason']
        except KeyError:
            reason = None
        return dict(status=status, reason=reason, io=True, changed=True, fail=False)


def _no_operand_check(cmd, strict=False):
    """Validates the operand

    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :param strict: When True, will generate an error if there is an operand or additional parameters
    :type strict: bool
    :return obj: If an error is found, dictionary as defined in 'commands' in the response. Otherwise None
    :rtype obj: dict, None
    :return operand: The operand from cmd
    :rtype: str
    :return p0: Parameter p0 converted to a list
    :rtype p0: list
    :return p1: Parameter p1 converted to a list
    :rtype p1: list
    """
    operand = cmd.get('operand')
    p0 = gen_util.convert_to_list(cmd.get('p0'))
    p1 = gen_util.convert_to_list(cmd.get('p1'))
    if strict:
        err_msg = list()
        if operand is not None:
            err_msg.append('operand: ' + str(operand))
        if len(p0) > 0:
            err_msg.append('p0:\n  ' + '  \n'.join(p0))
        if len(p1) > 0:
            err_msg.append('p1:\n  ' + '  \n'.join(p1))
        if len(err_msg) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='Unsupported parameters',
                        err_msg=err_msg,
                        io=False,
                        changed=False,
                        fail=True), p0, p1
    return None, operand, p0, p1


def _operand_check(cmd, strict=False):
    """Validates the operand

    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :param strict: When True, will generate an error if there are additional parameters
    :type strict: bool
    :return obj: If an error is found, dictionary as defined in 'commands' in the response. Otherwise None
    :rtype obj: dict, None
    :return operand: The operand from cmd
    :rtype: str
    :return p0: Parameter p0 converted to a list
    :rtype p0: list
    :return p1: Parameter p1 converted to a list
    :rtype p1: list
    """
    global _def_zone_access_tbl

    operand = cmd.get('operand')
    if _DEBUG_FICON and 'ficon' in operand:
        operand = operand.replace(',', '')
    p0 = gen_util.convert_to_list(cmd.get('p0'))
    p1 = gen_util.convert_to_list(cmd.get('p1'))
    if operand is None:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason=brcdapi_util.HTTP_REASON_MISSING_OPERAND,
                    io=False,
                    changed=False,
                    fail=True), operand, p0, p1
    if cmd.get('c-type') == 'defzone':
        if operand not in _def_zone_access_tbl:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='Invalid option for defzone',
                        err_msg=[str(operand)],
                        io=False,
                        changed=False,
                        fail=True), operand, p0, p1
    elif not gen_util.is_valid_zone_name(operand):
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid zone object name',
                    err_msg=[str(operand)],
                    io=False,
                    changed=False,
                    fail=True), operand, p0, p1
    if strict:
        err_msg = list()
        if len(p0) > 0:
            err_msg.append('p0:\n  ' + '  \n'.join(p0))
        if len(p1) > 0:
            err_msg.append('p1:\n  ' + '  \n'.join(p1))
        if len(err_msg) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='Unsupported parameters',
                        err_msg=err_msg,
                        io=False,
                        changed=False,
                        fail=True), operand, p0, p1
    return None, operand, p0, p1


def _p0_check(cmd, strict=False):
    """Validates the operand and one parameter (p0)

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand and p0 only
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if len(p0) == 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason=str(operand) + ' missing members',
                    err_msg=['p0'],
                    io=False,
                    changed=False,
                    fail=True), operand, p0, p1
    if strict:
        if len(p1) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason=str(operand) + ' has unsupported parameters (p1)',
                        err_msg=p1,
                        io=False,
                        changed=False,
                        fail=True), operand, p0, p1

    return None, operand, p0, p1


def _p1_check(cmd, strict=False):
    """Validates the operand and p1.

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand and only p1
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if len(p1) == 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason=str(operand) + ' missing members',
                    err_msg=['principal members: p1'],
                    io=False,
                    changed=False,
                    fail=True), operand, p0, p1
    if strict:
        if len(p0) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason=str(operand) + ' has unsupported parameters',
                        err_msg=['p0:\n  ' + '  \n'.join(p1)],
                        io=False,
                        changed=False,
                        fail=True), p0, p1

    return None, operand, p0, p1


def _p0_p1_check(cmd, strict=False):
    """Validates the operand and two parameters, p0 and p1

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand, p0, and p1.
    When False, must contain at least one of p0 or p1
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if strict:
        err_msg = list()
        if len(p0) == 0:
            err_msg.append('members: p0')
        if len(p1) == 0:
            err_msg.append('principal members: p1')
        if len(err_msg) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason=str(operand) + ' missing members',
                        err_msg=err_msg,
                        io=False,
                        changed=False,
                        fail=True), operand, p0, p1
    elif len(p0) + len(p1) == 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason=str(operand) + ' requires p0 or p1',
                    err_msg=list(),
                    io=False,
                    changed=False,
                    fail=True), operand, p0, p1
    
    return None, operand, p0, p1


def _p0_f_ok(cmd, strict=False):
    """Validates the operand. p0 is only OK if it's -f or -force

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand and p0 only
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if len(p0) == 1:
        if p0[0] == '-f' or p0[0] == '-force':
            return None, operand, p0, p1
    if strict:
        if len(p1) + len(p0) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason=str(operand) + ' has unsupported parameters (p1)',
                        err_msg=p0 + p1,
                        io=False,
                        changed=False,
                        fail=True), operand, p0, p1

    return None, operand, p0, p1


def refresh_zoning(session, fid, fabric_obj):
    """Deletes all zoning information from the fabric object and refreshes with new zoning data

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param fid: Fabric ID
    :type fid: int
    :param fabric_obj: Fabric object. Not using global _fab_obj because this method can be called externally.
    :return: List of error message encountered.
    :rtype: list
    """
    global _zone_uris

    # Just wipe out the fabric object and create a new one
    proj_obj = fabric_obj.r_project_obj()
    fab_key = fabric_obj.r_obj_key()
    switch_list = fabric_obj.r_switch_keys()
    proj_obj.s_del_fabric(fab_key)
    fabric_obj = proj_obj.s_add_fabric(fab_key)
    for wwn in switch_list:
        fabric_obj.s_add_switch(wwn)

    # Capture the current zoning information
    api_int.get_batch(session, proj_obj, _zone_uris, fid)

    return [alert_obj.fmt_msg() for alert_obj in fabric_obj.r_project_obj().r_alert_objects()]


##################################################################
#
#      Methods used in _change_type_func
#
###################################################################
def _alias_add(session, cmd, fid):
    """Add members to an existing alias. If force is set and the alias doesn't exist, it will be created

    :param session: Session object, or list of session objects, returned from brcdapi.fos_auth.login()
    :type session: dict
    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :param fid: Fabric ID
    :type fid: int
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command
    obj, alias, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    ali_obj = _fab_obj.r_alias_obj(alias)
    if ali_obj is None:
        if _f_flag:
            return _alias_create(session, cmd, fid)  # The alias doesn't exist so create it.
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    err_msg=[alias],
                    io=False,
                    changed=False,
                    fail=True)

    # If we got this far, the alias already existed so add the member to it.
    members = ali_obj.r_members()
    p0 = [mem for mem in tp0 if mem in members]  # List of members to add that are already members
    if len(p0) > 0 and not _f_flag:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason=alias + ' member already exists',
                    err_msg=p0, 
                    io=False,
                    changed=False,
                    fail=True)
    p0 = [mem for mem in tp0 if mem not in members]  # List of members to add that are not already members
    err_msg = [mem for mem in p0 if ',' not in mem and not gen_util.is_wwn(mem)]  # List of invalid members
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid WWN',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    ali_obj.s_add_member(p0)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))


def _alias_create(session, cmd, fid):
    """Create an alias. If force is set and the alias exists, it will be overwritten

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not gen_util.is_valid_zone_name(alias):  # Make sure it's a valid alias name
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid alias name',
                    err_msg=[alias],
                    io=False,
                    changed=False,
                    fail=True)
    err_msg = [mem for mem in p0 if ',' not in mem and not gen_util.is_wwn(mem)]  # Make sure its a valid d,i or WWN
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid WWN',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    if _fab_obj.r_alias_obj(alias) is None:
        _fab_obj.s_add_alias(alias, p0)
        if _t_flag or _b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    # If we got this far, the alias already exists
    if _f_flag:  # Overwrite the alias if _f_flag is True by deleting it and then creating this one
        _fab_obj.s_del_alias(alias)
        _fab_obj.s_add_alias(alias, p0)
        if _t_flag or _b_flag:
            return _good_test_return
        obj = _alias_delete(session, dict(operand=cmd.get('operand'), p0=list(), p1=list(), peer=cmd.get('peer')), fid)
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    else:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Alias already exists',
                    err_msg=[alias],
                    io=False,
                    changed=False,
                    fail=True)


def _alias_delete(session, cmd, fid):
    """Delete an alias. If force is set and the alias doesn't exist, no action is taken and good status is returned

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    ali_obj = _fab_obj.r_alias_obj(alias)
    if ali_obj is None:
        if _f_flag:
            return _good_force_nop_return
        else:
            return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                        reason='Alias not found',
                        err_msg=[alias],
                        io=False,
                        changed=False,
                        fail=True)
    zl = [obj.r_obj_key() for obj in ali_obj.r_zone_objects()]  # List of zones where alias is used
    if len(zl) > 0:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Alias in use',
                    err_msg=zl,
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    _fab_obj.s_del_alias(alias)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))


def _alias_remove(session, cmd, fid):
    """Remove alias members. If force is set and the alias doesn't exist, no action is taken and good status is returned

    See _alias_add() for a description of input and return values."""
    global _f_flag, _t_flag, _fab_obj, _b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    alias_obj = _fab_obj.r_alias_obj(alias)
    if alias_obj is None:
        if _f_flag:
            return _good_force_nop_return
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=alias + ' does not exist',
                    err_msg=list(),
                    io=False,
                    changed=False,
                    fail=True)
    members = alias_obj.r_members()
    if not _f_flag:
        t_members = [mem for mem in p0 if mem not in members]  # Get a list of members to remove that don't exist
        if len(t_members) > 0:
            return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                        reason='Members not in ' + alias,
                        err_msg=t_members,
                        io=False,
                        changed=False,
                        fail=True)

    # Execute the command. The only way to remove a member via the API is to delete and re-create it
    if _t_flag or _b_flag:
        return _good_test_return
    obj = _alias_delete(session, dict(operand=cmd.get('operand'), p0=list(), p1=list(), peer=cmd.get('peer')), fid)
    if obj['fail']:
        return obj
    new_cmd = copy.deepcopy(cmd)
    new_cmd.update(p0=[mem for mem in members if mem not in p0])  # Replace p0 with members to keep
    return _alias_create(session, new_cmd, fid)


def _cfg_add(session, cmd, fid):
    """Add zone members to an existing configuration. If force is set and the zone configuration doesn't exist, it will
    be created

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command
    obj, zonecfg, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj

    # Make sure the zone configuration exists
    zonecfg_obj = _fab_obj.r_zonecfg_obj(zonecfg)
    if zonecfg_obj is None:
        if _f_flag:
            return _cfg_create(session, cmd, fid)  # The zonecfg doesn't exist so create it.
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    rr_msg=[zonecfg],
                    io=False,
                    changed=False,
                    fail=True)

    # If we got this far, the zonecfg already existed so add the member(s) to it.
    members = zonecfg_obj.r_members()
    existing_members = [mem for mem in tp0 if mem in members]  # List of members to add that are already members
    if len(existing_members) > 0 and not _f_flag:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Member already exists',
                    err_msg=existing_members,
                    io=False,
                    changed=False,
                    fail=True)
    p0 = [mem for mem in tp0 if mem not in members]  # List of members to add that are not already members
    err_msg = [mem for mem in p0 if _fab_obj.r_zone_obj(mem) is None]  # Make sure members exist
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Zone member(s) do not exist',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)
    if len(p0) == 0:  # Make sure there is something to add
        if _f_flag:
            return _good_force_nop_return
        else:
            reason = 'No member(s) to add to ' + zonecfg + '. Members removed because they already were members, if '\
                                                           'any, are in the err_msg detail'
            return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                        reason=reason,
                        err_msg=existing_members,
                        io=False,
                        changed=False,
                        fail=True)

    # Execute the command
    zonecfg_obj.s_add_member(p0)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.zonecfg_add(session, fid, zonecfg, p0))


def _cfg_create(session, cmd, fid):
    """Create a zone configuration. If force is set and the configuration exists, it will be overwritten

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not gen_util.is_valid_zone_name(zonecfg):  # Make sure it's a valid zone configuration name
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid zone configuration name',
                    err_msg=[zonecfg],
                    io=False,
                    changed=False,
                    fail=True)
    err_msg = [mem for mem in p0 if _fab_obj.r_zone_obj(mem) is None]  # Make sure members exist
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Zone member(s) do not exist',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    if _fab_obj.r_zonecfg_obj(zonecfg) is None:
        _fab_obj.s_add_zonecfg(zonecfg, p0)
        if _t_flag or _b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_zonecfg(session, fid, zonecfg, p0))

    # If we got this far, the zone configuration already exists
    if _f_flag:  # Overwrite the zone configuration if _f_flag is True by deleting it and then creating this one
        _fab_obj.s_del_zonecfg(zonecfg)
        _fab_obj.s_add_zonecfg(zonecfg, p0)
        if _t_flag or _b_flag:
            return _good_test_return
        obj = _cfg_delete(session, dict(operand=cmd.get('operand'), p0=list(), p1=list(), peer=cmd.get('peer')), fid)
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_zonecfg(session, fid, cmd.get('operand'), p0))
    else:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Zone configuration already exists',
                    err_msg=[zonecfg],
                    io=False,
                    changed=False,
                    fail=True)


def _cfg_delete(session, cmd, fid):
    """Delete a zone configuration. If force is set and the configuration doesn't exist, good status is returned

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    if _fab_obj.r_zonecfg_obj(zonecfg) is None:
        if _f_flag:
            return _good_force_nop_return
        else:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Zone configuration not found',
                    'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    _fab_obj.s_del_zonecfg(zonecfg)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_zonecfg(session, fid, zonecfg))


def _cfg_enable(session, cmd, fid):
    """Enable a zone configuration. The force flag, _f_flag, does nothing.

    See _alias_add() for a description of input and return values"""
    global _fab_obj, _t_flag, _checksum, _pending, _skip_pend_flag, _b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _p0_f_ok(cmd, True)
    if obj is not None:
        return obj
    # It would be nice to see if the defined zone configuration is already the effective zone configuration and if so,
    # check to see if any of the members changed but that's for another revision. The only thing being checked for is
    # to make sure the zone configuration exists.
    if _fab_obj.r_zonecfg_obj(zonecfg) is None:
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    err_msg=[zonecfg],
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    if _t_flag or _b_flag:
        # WARNING: The effective zone database in the fabric object, _fab_obj, is now out of date. There is no software
        # utility to simulate the zoning response and since we are in test mode, we can't just refresh the zoning
        # database from the switch. Writing a software utility to update it wouldn't be hard but as a practical matter,
        # I don't know of anyone who makes zoning changes, enables a zone configuration, and then continues to make
        # zoning changes all in the same activity so I didn't bother. This is only a problem in test mode.
        return _good_test_return
    zobj = brcdapi_zone.enable_zonecfg(session, _checksum, fid, zonecfg)
    if not fos_auth.is_error(zobj):
        msg_l = refresh_zoning(session, fid, _fab_obj)
        if len(msg_l) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='API error occurred while refreshing the zone DB',
                        err_msg=msg_l,
                        io=False,
                        changed=False,
                        fail=True)
        _pending = list()  # A cfgsave is inherent when a zone configuration is enabled.
        _skip_pend_flag = True
        _checksum, obj = brcdapi_zone.checksum(session, fid)  # Need a new checksum in case there are additional changes
        if fos_auth.is_error(obj):
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='Successfully enabled ' + zonecfg + ', but could not refresh the _checksum',
                        err_msg=['Check the log for details'],
                        io=False,
                        changed=False,
                        fail=True)
    return _format_return(zobj)


def _cfg_remove(session, cmd, fid):
    """Remove a zone from an existing zone configuration. If force is set and the zone is not in the configuraiton of
    configuraiton doesn't exist, good status is returned.

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, zonecfg, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    zonecfg_obj = _fab_obj.r_zonecfg_obj(zonecfg)
    # Does the zone configuration exist?
    if zonecfg_obj is None:
        if _f_flag:
            return _good_force_nop_return
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    err_msg=[zonecfg],
                    io=False,
                    changed=False,
                    fail=True)
    # Do the members exist?
    no_exist = [mem for mem in tp0 if not zonecfg_obj.r_has_member(mem)]
    if len(no_exist) > 0 and not _f_flag:
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    err_msg=[no_exist], 
                    io=False,
                    changed=False,
                    fail=True)
    p0 = [mem for mem in tp0 if mem not in no_exist]
    if len(p0) == 0:
        if _f_flag:
            return _good_force_nop_return
        else:
            reason = 'No members to remove. Requested members to remove that were not in ' + zonecfg + ', if any, '
            reason += 'are in the err_msg detail'
            return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                        reason=reason,
                        err_msg=[no_exist],
                        io=False,
                        changed=False,
                        fail=True)

    # Execute the request to delete the members
    zonecfg_obj.s_del_member([mem for mem in tp0 if not zonecfg_obj.r_has_member(mem)])
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.zonecfg_remove(session, fid, zonecfg, p0))


def _cfg_save(session, cmd, fid):
    """Causes the zone database to be pushed to the fabric. The force flag is only relevant in test mode. In test mode,
    if force is not set and there are pending transactions, an error is returned. Otherwise, the action is always
    sent to the switch

    See _alias_add() for a description of input and return values"""
    global _f_flag, _t_flag, _fab_obj, _pending, _checksum, _skip_pend_flag, _b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _no_operand_check(cmd)
    if obj is not None:
        return obj
    _skip_pend_flag = True
    if _t_flag or _b_flag:
        if not _f_flag and len(_pending) == 0:
            obj = fos_auth.create_error(brcdapi_util.HTTP_NO_CONTENT, 'No pending zone transactions', '')
            return _format_api_error(obj)
        return _good_test_return
    obj = brcdapi_zone.save(session, fid, _checksum)
    if fos_auth.is_error(obj):
        return _format_api_error(obj)
    _pending = list()
    _checksum, obj = brcdapi_zone.checksum(session, fid)  # Need a new _checksum in case there are additional changes
    return _format_return(obj)


def _defzone(session, cmd, fid):
    """Set the default zone. The force flag, _f_flag, does nothing

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _def_zone_access_tbl, _b_flag, _skip_pend_flag

    # Validate the command and operands
    obj, action, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    try:
        access = _def_zone_access_tbl[action]
        if access < 0:  # --show is -1 in _def_zone_access_tbl
            return _good_force_nop_return
    except BaseException as e:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid operand',
                    err_msg=[action, 'Exception code: ' + str(e) if isinstance(e, (bytes, str)) else str(type(e))],
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    _skip_pend_flag = True
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.default_zone(session, fid, access))


def _zone_add(session, cmd, fid):
    """Add members to an existing zone. If force is set and zone doesn't exist, it will be created.

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command
    obj, zone, p0, p1 = _p0_p1_check(cmd)
    if obj is not None:
        return obj
    zone_obj = _fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if _f_flag:
            return _zone_create(session, cmd, fid)  # The zone doesn't exist so create it.

        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                    err_msg=[zone],
                    io=False,
                    changed=False,
                    fail=True)

    # If we got this far, the zone already existed. Validate and figure out which members to add.
    for buf in ('member', 'principal'):
        members = zone_obj.r_members() if buf == 'member' else zone_obj.r_pmembers()
        test_p = p0 if buf == 'member' else p1
        px = [mem for mem in test_p if mem in members]  # List of members to add that are already members
        if len(px) > 0 and not _f_flag:
            return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                        reason=zone + ' ' + buf + ' already exists',
                        err_msg=px,
                        io=False,
                        changed=False,
                        fail=True)
        px = [mem for mem in test_p if mem not in members]  # List of members to add that are not already members
        err_msg = [mem for mem in test_p if ',' not in mem and not gen_util.is_wwn(mem) and
                   not gen_util.is_valid_zone_name(mem)]  # List of invalid zone members
        if len(err_msg) > 0:
            return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                        reason='Invalid zone member(s)',
                        err_msg=err_msg,
                        io=False,
                        changed=False,
                        fail=True)
        if buf == 'member':  # If forcing changes, only send the added members to the switch
            new_p0 = px
        else:
            new_p1 = px
    err_msg = [mem for mem in new_p0 if mem in new_p1 + zone_obj.r_pmembers()]  # Members that are also principals
    err_msg.extend([mem for mem in new_p1 if mem in new_p0 + zone_obj.r_members()])  # Principals that are also members
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Members and principal members must be exclusive',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)
    new_cmd = dict()
    for k in cmd.keys():
        v = new_p0 if k == 'p0' else new_p1 if k == 'p1' else cmd.get(k)
        new_cmd.update({k: v})

    # Execute the command
    zone_obj.s_add_member(new_p0)
    zone_obj.s_add_pmember(new_p1)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.create_zones(session, fid, [_format_cmd_for_brcdapi(new_cmd)]))


def _zone_create(session, cmd, fid):
    """Create a zone. If force is set and the zone already exists, it is overwritten

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    if cmd['peer']:
        zone_type = brcddb_common.ZONE_USER_PEER
        obj, zone, p0, p1 = _p1_check(cmd)
    else:
        zone_type = brcddb_common.ZONE_STANDARD_ZONE
        obj, zone, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not gen_util.is_valid_zone_name(zone):  # Make sure it's a valid zone name
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid zone name',
                    err_msg=[zone],
                    io=False,
                    changed=False,
                    fail=True)
    err_msg = [mem for mem in p0 if ',' not in mem and not gen_util.is_wwn(mem) and
               not gen_util.is_valid_zone_name(mem)]  # List of invalid zone members
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Invalid zone member(s)',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)
    err_msg = [mem for mem in p0 if mem in p1]  # Members in p0 that are also in p1
    err_msg.extend(([mem for mem in p1 if mem in p0]))  # Add members in p1 that are also in p0
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Members and principal members must be exclusive',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)
    # Figure out if there are any duplicate members after resolving the aliases. The previous check just checked to make
    # sure there were no duplicates as defined. Zone are usually defined with aliases. Below resolves the aliases into
    # WWNs and checks for duplicates in the resolved list of members.
    # often is with aliases. If two different aliases have the same member, a duplicate member error is returned from
    # FOS but you have no idea which one. The above check would be covered in this check but by doing two separate
    # checks, the error message(s) can articulate the error.
    err_msg = list()
    resolved = [list(), list()]  # Members in d,i or WWN - 0: members in p0, 1: members in p1
    desc = ['p0', 'p1']
    px = [p0, p1]
    for i in range(0, 2):
        for mem in px[i]:  # This loop builds the resolved list
            if ',' not in mem and not gen_util.is_wwn(mem):
                alias_obj = _fab_obj.r_alias_obj(mem)
                if alias_obj is None:
                    err_msg.append('Alias ' + mem + ' does not exist')
                else:
                    resolved.extend(alias_obj.r_members())
            else:
                resolved.append(mem)
    # Now check for duplicates
    found = [list(), list()]
    for i in range(0, 2):
        for mem in resolved[i]:
            x = 0 if i == 1 else 1
            if mem in found[i]:
                err_msg.append('Duplicate member ' + mem + ' in ' + desc[i] + '. Alias(es): ' +
                               ', '.join(_fab_obj.r_alias_for_wwn(mem)))
            if mem in found[x]:
                err_msg.append('Duplicate member ' + mem + ' in ' + desc[i] + '. Alias(es): ' +
                               ', '.join(_fab_obj.r_alias_for_wwn(mem)))

    err_msg = list()
    resolved = list()
    for mem in p0 + p1:
        if ',' not in mem and not gen_util.is_wwn(mem):
            alias_obj = _fab_obj.r_alias_obj(mem)
            if alias_obj is None:
                err_msg.append('Alias ' + mem + ' does not exist')
            else:
                for ali_mem in alias_obj.r_members():
                    if ali_mem in resolved:
                        err_msg.append('Duplicate member: ' + ali_mem + ' appears in: '
                                       + ', '.join(_fab_obj.r_alias_for_wwn(ali_mem)))
                    resolved.append(ali_mem)
        else:
            resolved.append(mem)
    if len(err_msg) > 0:
        return dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                    reason='Zone: ' + zone + ' contains invalid members',
                    err_msg=err_msg,
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    if _fab_obj.r_zone_obj(zone) is None:
        _fab_obj.s_add_zone(zone, zone_type, p0, p1)
        if _t_flag or _b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_zones(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    # If we got this far, the zone already exists
    if _f_flag:  # Overwrite the zone if _f_flag is True by deleting it and then creating this one
        _fab_obj.s_del_zone(zone)
        _fab_obj.s_add_zone(zone, zone_type, p0, p1)
        if _t_flag or _b_flag:
            return _good_test_return
        obj = _zone_delete(session, dict(operand=cmd.get('operand'), p0=list(), p1=list(), peer=cmd.get('peer')), fid)
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_zones(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    else:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Alias already exists',
                    err_msg=[zone],
                    io=False,
                    changed=False,
                    fail=True)


def _zone_delete(session, cmd, fid):
    """Delete a zone. If force is set and the zone does not exist, good status is returned

    See _alias_add() for a description of input and return values"""
    global _f_flag, _fab_obj, _t_flag, _b_flag

    # Validate the command and operands
    obj, zone, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    zone_obj = _fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if _f_flag:
            return _good_force_nop_return
        else:
            return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                        reason='Zone not found',
                        err_msg=[zone],
                        io=False,
                        changed=False,
                        fail=True)
    zl = [obj.r_obj_key() for obj in zone_obj.r_zonecfg_objects()]  # List of zone configurations where zone is used
    if len(zl) > 0:
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Zone in use',
                    err_msg=zl,
                    io=False,
                    changed=False,
                    fail=True)

    # Execute the command
    _fab_obj.s_del_zone(zone)
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_zones(session, fid, [_format_cmd_for_brcdapi(cmd)]))


##################################################################
#
#      Methods used in _change_type_func
#
###################################################################
def _alias_copy_int(session, obj, fid):
    """Used by _zone_object_copy() and _zone_object_rename() to copy an alias

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param obj: Alias object to create
    :type obj: brcddb.classes.AliasObj
    :param fid: Fabric ID
    :type fid: int
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    return brcdapi_zone.create_aliases(session, fid, [dict(name=obj.r_obj_key(), members=obj.r_members())])


def _zone_copy_int(session, obj, fid):
    """Used by _zone_object_copy() and _zone_object_rename() to copy a zone

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param obj: Zone object to create
    :type obj: brcddb.classes.ZoneObj
    :param fid: Fabric ID
    :type fid: int
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    send_obj = dict(name=obj.r_obj_key(), members=obj.r_members(), pmembers=obj.r_pmembers(), type=obj.r_type())
    return brcdapi_zone.create_zones(session, fid, [send_obj])


def _zonecfg_copy_int(session, obj, fid):
    """Used by _zone_object_copy() and _zone_object_rename() to copy a zone configuration

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param obj: Zone configuration object to create
    :type obj: brcddb.classes.ZoneCfgObj
    :param fid: Fabric ID
    :type fid: int
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    return brcdapi_zone.create_zonecfg(session, fid, obj.r_obj_key(), obj.r_members())


def _alias_replace_int(session, old_obj, fid, new_obj):
    """Replace an alias in all zones with a new alias name.

    :param session: Session object returned from brcdapi.fos_auth.login()
    :type session: dict
    :param old_obj: Zone object to be replaced
    :type old_obj: brcddb.classes.AliasObj
    :param fid: Fabric ID
    :type fid: int
    :param new_obj: New zone object
    :type new_obj: AliasObj, ZoneObj, ZoneCfgObj
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
"""
    global _fab_obj

    return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST, 'Replace aliases not yet implemented', list())

    """
    r_obj = brcdapi_util.GOOD_STATUS_OBJ
    old_alias, new_alias = old_obj.r_obj_key(), new_obj.r_obj_key()
    zone_update_d = dict()  # Use zone_update_d to keep track of which zones need to be modified

    # This could have been a little more efficient but for as often as it's used, this is good enough
    for zone in _fab_obj.r_zones_for_alias(old_alias):
        zone_obj = _fab_obj.r_zone_object(zone)
        zone_update_d.update({zone: dict(del_member=old_alias if old_alias in zone_obj.r_members() else None,
                                         del_pmember=old_alias if old_alias in zone_obj.r_pmembers() else None,
                                         add_member=new_alias if old_alias in zone_obj.r_members() else None,
                                         add_pmember=new_alias if old_alias in zone_obj.r_pmembers() else None)})
    # Modify the zones
    for zone, d in zone_update_d.items():
        r_obj = brcdapi_zone.modify_zone(session,
                                         fid,
                                         zone,
                                         d['add_member'],
                                         d['del_member'],
                                         d['add_pmember'],
                                         d['del_pmember'])
        if fos_auth.is_error(r_obj):
            return r_obj  # Just bail out if there is an error

    # Delete the old alias and add the new one
    r_obj = brcdapi_zone.del_aliases(session, fid, old_alias)
    # TODO - Add alias with brcdapi_zone.create_aliases

    return r_obj
    """


def _zone_replace_int(session, old, new):
    """Replace a zone in all zone configurations with a new zone name. See _alias_copy_int() for parameters"""
    global _fab_obj

    return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST, 'Replace zone not yet implemented', list())


def _zonecfg_replace_int(session, old, fid):
    """Delete a zone configuration. See _alias_copy_int() for parameters"""
    return fos_auth.create_error(brcdapi_util.HTTP_BAD_REQUEST, 'Replace Zone config not yet implemented', list())


_zone_copy_action = dict(
    alias=dict(copy=_alias_copy_int, replace=_alias_replace_int),
    zone=dict(copy=_zone_copy_int, replace=_zone_replace_int),
    zonecfg=dict(copy=_zonecfg_copy_int, replace=_zonecfg_replace_int)
)


def _zone_copy_rename_param(cmd):
    """Used by _zone_object_copy() and _zone_object_rename() to validate parameters and determine the zone object type

    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :return obj: Dictionary as defined in 'commands' in the response if an error was encountered. Otherwise None
    :rtype obj: dict, None
    :return zoneobj: The zone object to be copied or renamed. None if the zone object was not found
    :rtype zoneobj: brcddb.classes.AliasObj, brcddb.classes.ZoneObj, brcddb.classes.ZoneCfgObj, None
    :return new_obj: Name of the new zone object (copy of zoneobj). None if an error occured
    :rtype new_obj: str, None
    :return type: 'alias', 'zone', or 'zonecfg'. May be '' if an error was encountered
    :rtype type: str
    """
    global _f_flag, _t_flag, _fab_obj, _b_flag

    # Validate the command and operands
    obj, zoneobj_name, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj, None, None, ''
    if len(p0) != 1:  # It can't be 0 because _p0_check() would have caught that case
        err_obj = dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                       reason='Too many parameters',
                       err_msg=p0,
                       io=False,
                       changed=False,
                       fail=True)
        return err_obj, None, p0[0], ''

    # Find the zone object to copy and make the copy in brcddb
    zone_obj_types = dict(zonecfg=_fab_obj.r_zonecfg_obj, zone=_fab_obj.r_zone_obj, alias=_fab_obj.r_alias_obj)
    for buf in zone_obj_types.keys():
        obj = zone_obj_types[buf](zoneobj_name)
        if obj is not None:
            copied_obj = obj.s_copy(p0[0])
            if copied_obj is None:
                err_obj = dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                               reason=buf + ' ' + p0[0] + ' already exists',
                               err_msg=list(),
                               io=False,
                               changed=False,
                               fail=True)
                return err_obj, None, None, buf
            else:
                return None, obj, copied_obj, buf

    err_obj = dict(status=brcdapi_util.HTTP_NOT_FOUND,
                   reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                   err_msg=[zoneobj_name],
                   io=False,
                   changed=False,
                   fail=True)
    return err_obj, None, None, ''


def _zone_object_copy(session, cmd, fid):
    """Copies a zone object. Force is ignored. The destination zone object will not be over written if it already exists

    See _alias_add() for a description of input and return values"""
    global _f_flag, _t_flag, _fab_obj, _b_flag

    # Validate the command and operands
    obj, zoneobj, copy_obj, zone_type = _zone_copy_rename_param(cmd)
    if obj is not None:
        return obj

    # Make the copy
    if _t_flag or _b_flag:
        return _good_test_return
    return _format_return(_zone_copy_action[zone_type]['copy'](session, copy_obj, fid))


def _zone_object_rename(session, cmd, fid):
    """Renames a zone object and iteratively updates all zone objects where used. Force does nothing. You cannot rename
    an object over an existing object. You cannot rename the effective zone configuration.

    See _alias_add() for a description of input and return values"""
    global _f_flag, _t_flag, _fab_obj, _b_flag

    eff_zone_name = _fab_obj.r_defined_eff_zonecfg_key()
    if isinstance(cmd['operand'], str) and cmd['operand'] == eff_zone_name:
        # Renaming the defined zone configuration when it's also the effective zone configuration is not permitted.
        # Back out the copy and return an error
        return dict(status=brcdapi_util.HTTP_REQUEST_CONFLICT,
                    reason='Renaming the effective zone configuration is not permitted',
                    err_msg=[eff_zone_name],
                    io=False,
                    changed=False,
                    fail=True)

    obj, zoneobj, copy_obj, zone_type = _zone_copy_rename_param(cmd)
    if obj is not None:
        return obj

    # Make the copy
    if _t_flag or _b_flag:
        return _good_test_return
    obj = _zone_copy_action[zone_type]['copy'](session, copy_obj, fid)
    if fos_auth.is_error(obj):
        return _format_return(obj)

    # Replace everywhere this zone object was used and replace it with the copy
    return _format_return(_zone_copy_action[zone_type]['replace'](session, copy_obj.r_obj_key(), fid))


def _zone_remove(session, cmd, fid):
    """Remove zone members. If force is set and the zone or member does not exist, good status is returned.

    See _alias_add() for a description of input and return values"""
    global _f_flag, _t_flag, _fab_obj, _b_flag

    # Validate the command and operands
    obj, zone, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    zone_obj = _fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if _f_flag:
            return _good_force_nop_return
        return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                    reason=zone + ' does not exist',
                    err_msg=list(),
                    io=False,
                    changed=False,
                    fail=True)
    members = zone_obj.r_members()
    pmembers = zone_obj.r_pmembers()
    if not _f_flag:
        # Get a list of members to remove that don't exist
        t_members = [mem for mem in p0 if mem not in members] + [mem for mem in p1 if mem not in pmembers]
        # Note that if the zone was created with an alias and the remove is by d,i or WWN, not only am I not going to
        # catch it here, neither will FOS.
        if len(t_members) > 0:
            return dict(status=brcdapi_util.HTTP_NOT_FOUND,
                        reason='Members not in ' + zone,
                        err_msg=t_members,
                        io=False,
                        changed=False,
                        fail=True)

    # Execute the command. The only way to remove a member via the API is to delete and create it
    if _t_flag or _b_flag:
        return _good_test_return
    obj = _zone_delete(session, dict(operand=cmd.get('operand'), p0=list(), p1=list(), peer=cmd.get('peer')), fid)
    if obj['fail']:
        return obj
    new_cmd = copy.deepcopy(cmd)
    new_cmd.update(p0=[mem for mem in members if mem not in p0])  # Replace p0 with members to keep
    new_cmd.update(p1=[mem for mem in pmembers if mem not in p1])  # Replace p1 with peer members to keep
    return _zone_create(session, cmd, fid)


# Table _change_type_func is the C like case statement
_change_type_func = {
    'alias-add': _alias_add,
    'alias-create': _alias_create,
    'alias-delete': _alias_delete,
    'alias-remove': _alias_remove,
    'cfg-add': _cfg_add,
    'cfg-create': _cfg_create,
    'cfg-delete': _cfg_delete,
    'cfg-enable': _cfg_enable,
    'cfg-remove': _cfg_remove,
    'cfg-save': _cfg_save,
    'defzone': _defzone,
    'zone-add': _zone_add,
    'zone-create': _zone_create,
    'zone-delete': _zone_delete,
    'zone-object-copy': _zone_object_copy,
    'zone-object-rename': _zone_object_rename,
    'zone-remove': _zone_remove,
}


##################################################################
#
#               Process the changes
#
###################################################################
def send_zoning(content, cur_session=None):
    """Entry point. Parses and dispatches all zoning operations

    :param content: List of zone changes as described in Inputs - see module header.
    :type content: list
    :param cur_session: Session object. If None, a login is performed and a new session captured
    :type cur_session: dict
    :return: Formatted response as described in Return - see module header
    :rtype: dict
    """
    global _t_flag, _f_flag, _pending, _change_type_func, _fab_obj, _checksum, _skip_pend_flag, _zone_uris, _b_flag

    # Initialize application control and validate request
    response = list()
    must_have = {
        'ip-addr': content.get('ip-addr'),
        'id': content.get('id'),
        'pw': content.get('pw'),
        'fid': content.get('fid'),
    }
    for k, v in must_have.items():
        if not isinstance(k, (str, int)):
            response.append(dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                                 reason=brcdapi_util.HTTP_REASON_MISSING_PARAM,
                                 err_msg=['Missing ' + k, 'All processing halted'],
                                 io=False,
                                 changed=False,
                                 fail=True))
    fid = content.get('fid')  # We use the fid often, so get a local copy
    sec = 'none' if content.get('sec') is None else content.get('sec')
    if content.get('force') is not None and content.get('force'):
        _f_flag = True  # Global flag initialized to False
    if content.get('test') is not None and content.get('test'):
        _t_flag = True  # Global flag initialized to False
    if content.get('bulk') is not None and content.get('bulk'):
        _b_flag = True  # Global flag initialized to False
    if len(response) > 0:
        return response

    # Set up the project container
    proj_obj = brcddb_project.new("Captured_data", datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    proj_obj.s_python_version(sys.version)
    proj_obj.s_description('Temporary project for zoning changes')

    # Login and prime the project object (proj_obj) with basic fabric info.
    if cur_session is None:
        session = api_int.login(content.get('id'), content.get('pw'), content.get('ip-addr'), sec, proj_obj)
        if fos_auth.is_error(session):
            response.append(_format_api_error(session))
            return response
        # We'll need some basic information about the chassis, switch, fabric, and current zoning
        api_int.get_batch(session, proj_obj, _zone_uris, fid)
        if proj_obj.r_is_api_error():
            response.append(dict(status=brcdapi_util.HTTP_BAD_REQUEST,
                                 reason='Error processing the commands in err_msg',
                                 err_msg=_zone_uris,
                                 io=False,
                                 changed=False,
                                 fail=True))
            obj = brcdapi_rest.logout(session)
            if fos_auth.is_error(obj):
                response.append(_format_api_error(obj))
    else:
        session = cur_session

    # Make sure we have a switch and fabric
    switch_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn')).r_switch_obj_for_fid(fid)
    if switch_obj is None:
        response.append(dict(status=brcdapi_util.HTTP_NOT_FOUND,
                             reason='Switch matching FID ' + str(fid),
                             err_msg=list(),
                             io=False,
                             changed=False,
                             fail=True))
    _fab_obj = switch_obj.r_fabric_obj()
    if _fab_obj is None:
        response.append(dict(status=brcdapi_util.HTTP_NOT_FOUND,
                             reason='Fabric object for FID ' + str(fid),
                             err_msg=list(),
                             io=False,
                             changed=False,
                             fail=True))
    if len(response) > 0:
        obj = brcdapi_rest.logout(session)
        if fos_auth.is_error(obj):
            response.append(_format_api_error(obj))
        return response

    # Get a checksum - we'll need this for cfgsave operation
    _checksum = _fab_obj.r_get('brocade-zone/effective-configuration/checksum')
    if _checksum is None:
        response.append(dict(status=brcdapi_util.HTTP_INT_SERVER_ERROR,
                             reason=brcdapi_util.HTTP_REASON_UNEXPECTED_RESP,
                             err_msg=['Missing: brocade-zone/effective-configuration/checksum'],
                             io=False,
                             changed=False,
                             fail=True))
        return response

    # Process the requests
    i = 0
    tl = content.get('changes')
    fail_flag = False
    for change_req in tl:
        _skip_pend_flag = False
        c_type = change_req.get('c-type')
        if c_type is not None:
            if isinstance(c_type, str) and c_type in _change_type_func:
                try:
                    obj = _change_type_func[c_type](session, change_req, fid)
                    response.append(obj)
                    if not _t_flag:
                        if obj['io'] and obj['changed'] and not _skip_pend_flag:
                            _pending.append(change_req)
                        if obj['fail']:
                            fail_flag = True
                            break
                except BaseException as e:
                    e_buf = 'Exception: ' + str(e) if isinstance(e, (bytes, str)) else str(type(e))
                    ml = ['Programming error processing ' + c_type,
                          'Operand: str(change_req.get("operand"))',
                          'Line: ' + str(i),
                          e_buf]
                    brcdapi_log.exception(ml, echo=True)
                    response.append(dict(status=brcdapi_util.HTTP_INT_SERVER_ERROR,
                                         reason=e_buf,
                                         err_msg=ml,
                                         io=False,
                                         changed=False,
                                         fail=True))
                    fail_flag = True
                    break
            else:
                response.append(dict(status=brcdapi_util.HTTP_NOT_FOUND,
                                     reason=brcdapi_util.HTTP_REASON_NOT_FOUND,
                                     err_msg=['Unknown change request: ' + str(c_type)],
                                     io=False,
                                     changed=False,
                                     fail=True))
                fail_flag = True
                break
        else:
            response.append(dict(status=brcdapi_util.HTTP_OK, io=False, changed=False, fail=False))
        i += 1

    # If bulk zoning was specified, send the updates.
    if _b_flag and not _t_flag and not fail_flag:
        try:
            obj = api_zone.replace_zoning(session, _fab_obj, fid)
            if fos_auth.is_error(obj):
                response.append(_format_return(obj))
        except BaseException as e:
            buf = 'Programming error in api_zone.replace_zoning()'
            e_buf = str(e) if isinstance(e, (bytes, str)) else str(type(e))
            brcdapi_log.exception([buf, 'Exception: ' + e_buf], echo=True)
            response.append(dict(status=brcdapi_util.HTTP_INT_SERVER_ERROR,
                                 reason=buf,
                                 err_msg=['Exception: ' + e_buf],
                                 io=False,
                                 changed=False,
                                 fail=True))

    # Wrap up
    if len(_pending) > 0:
        response.append(dict(status=brcdapi_util.HTTP_PRECONDITION_REQUIRED,
                             reason=brcdapi_util.HTTP_REASON_PENDING_UPDATES,
                             err_msg=['Request: ' + str(change_req.get('c-type')) + ' Operand: ' +
                                      str(change_req.get('operand')) for change_req in _pending],
                             io=False,
                             changed=False,
                             fail=True))
    # There is no harm in aborting a transaction when there are no pending transactions so instead of only aborting the
    # transactions when there are pending transactions, I always abort just in case there is a code bug
    obj = brcdapi_zone.abort(session, fid)
    if fos_auth.is_error(obj):
        response.append(_format_return(obj))

    # Log out
    if session is not None and cur_session is None:
        obj = brcdapi_rest.logout(session)
        if fos_auth.is_error(obj):
            brcdapi_log.log(fos_auth.formatted_error_msg(obj), echo=True)

    return response
