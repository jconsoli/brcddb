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
:mod:`zone` - Applies zoning changes to a fabric.

**Overview**

Performs zoning transactions on a per transaction basis or in bulk. Origionally intended for use with a script written
to support an Ansible Playbook. Ansible Playbooks are usually expected to have a test mode so that the Playbook can
validate the actions before executing the Playbook. Due to Ansible container library restrictions in most shops, it
morphed into an example on how to zone via the API. Since there is a test mode, it also serves as an eample on how to
use the brcddb database to validate the zoning. In fact, most of the code herein is dedicated to validating the zoning.

CLI was used because the CLI is most familiar to system administrators. It was also the most convenient to test the
zone library with since there is an abundance of CLI test scripts to use.

Error messages with FOS often provided limited information so one of the goals of the test mode was to provide more
detailed information when an error occurs.

When not in bulk mode, there are certainly ways to make the individual zoning more effecient. The intent was to keep
intdividual zoning simple and one for one so it can be used as an example. I'm assuming customers using CLI scripting
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
configuration in this maner, the defined configuration must be copied to a new configuration and then enabled before
deleting it. Since there may be other pending changes, this may have unintended consequences.

**Important Timing Notes**

Read (GET) happens very quickly but zone changes usually take around 400 msec per change. The delay is due to the need
to update the flash. It is the flash update operation, not the number of updates that take time. There is no significant
difference between making on zone change vs. 1000 zone changes in a single request. There is also about 2 seconds for
of additional overhead in this module for operations such as reading and saving the zone database.

Bulk zoning operations happen within a few seconds but, depending on the number of changes, a large batch of zone
changes can take signifiantly longer. If you are invoking this module from another module with a timeout, such as would
be the case with modules called from an Ansible Playbook, you need to be cognizant of how long the changes will take.

**Input**

    Data is input is a dictionary as follows:

    +-----------+-----------+-------+-------------------------------+
    | leaf      | Sub-leaf  | Type  | Description                   |
    +===========+===========+=======+===============================+
    | fid       |           | int   | Fabric ID of switch in        |
    |           |           |       | chassis where zoning changes  |
    |           |           |       | are to be applied             |
    |           |           |       | Required                      |
    +-----------+-----------+-------+-------------------------------+
    | ip-addr   |           | str   | IP address of chassis         |
    |           |           |       | Required                      |
    +-----------+-----------+-------+-------------------------------+
    | id        |           | str   | User ID                       |
    |           |           |       | Required                      |
    +-----------+-----------+-------+-------------------------------+
    | pw        |           | str   | Password                      |
    |           |           |       | Required                      |
    +-----------+-----------+-------+-------------------------------+
    | sec       |           | str   | 'CA' or 'self' for HTTPS. If  |
    |           |           |       | 'none', HTTP is used.         |
    |           |           |       | Default: 'none'               |
    +-----------+-----------+-------+-------------------------------+
    | force     |           | bool  | True - ignore warnings and    |
    |           |           |       | overwrite existing objects.   |
    |           |           |       | Default: True                 |
    +-----------+-----------+-------+-------------------------------+
    | test      |           | bool  | True - ignores cfg-save. Only |
    |           |           |       | reads the zone database for   |
    |           |           |       | validation purposes. No zone  |
    |           |           |       | changes are sent to the       |
    |           |           |       | switch. Useful for validating |
    |           |           |       | changes before applying them. |
    |           |           |       | Degfault: False               |
    +-----------+-----------+-------+-------------------------------+
    | changes   | list      |       | List of dictionaries as noted |
    |           |           |       | below. Unless file is         |
    |           |           |       | specified, the baseline zone  |
    |           |           |       | DB is read from the switch    |
    |           |           |       | matching fid.                 |
    |           |           |       |                               |
    |           |           |       | This should be set to the     |
    |           |           |       | list returned from            |
    |           |           |       | brcddb.util.util.parse_cli()  |
    +-----------+-----------+-------+-------------------------------+
    |           | c-type    | str   | Change type. Must be one of   |
    |           |           |       | the keys in change_type_func  |
    |           |           |       |                               |
    |           |           |       | Note that None is allowed.    |
    |           |           |       | This was done to support a    |
    |           |           |       | script that front ended this  |
    |           |           |       | with a simple CLI parser      |
    |           |           |       | where the CLI file may have   |
    |           |           |       | comments or blank lines. This |
    |           |           |       | was done so that the index of |
    |           |           |       | commands matches the index of |
    |           |           |       | the responses                 |
    +-----------+-----------+-------+-------------------------------+
    |           | operand   | str   | Name associated with the      |
    |           |           |       | operation specified in c-type.|
    |           |           |       | Zone name, alias name, etc.   |
    +-----------+-----------+-------+-------------------------------+
    |           | p0        | list  | Parameters. For all zone      |
    |           |           |       | operations, these are the     |
    |           |           |       | members. For peer zones,      |
    |           |           |       | these are the non-principal   |
    |           |           |       | members.                      |
    +-----------+-----------+-------+-------------------------------+
    |           | p1        | list  | Similar to p0. Only used for  |
    |           |           |       | peer zones. These are the     |
    |           |           |       | principal members             |
    +-----------+-----------+-------+-------------------------------+
    |           | peer      | bool  | If true, zone is a peer zone. |
    +-----------+-----------+-------+-------------------------------+

**Return**

    Data is returned in a dictionary as follows:

    +-----------+-----------+-------+-------------------------------+
    | leaf      | Sub-leaf  | Type  | Description                   |
    +===========+===========+=======+===============================+
    | summary   |           |                                       |
    |           | warnings  | int   | Summary number of warnings    |
    +-----------+-----------+-------+-------------------------------+
    |           | errors    | int   | Summary number of errors      |
    +-----------+-----------+-------+-------------------------------+
    |           | save      | bool  | True - the equivalent of      |
    |           |           |       | cfgsave was done.             |
    |           |           |       | False - Zoning changes were   |
    |           |           |       | not saved to the switch       |
    +-----------+-----------+-------+-------------------------------+
    | commands  |           | list  | This list matches the input   |
    |           |           |       | list 'changes'. It is a list  |
    |           |           |       | of dict with the following    |
    |           |           |       | members:                      |
    +-----------+-----------+-------+-------------------------------+
    |           | changed   | bool  | True - a change was made      |
    |           |           |       | False - no change was made    |
    +-----------+-----------+-------+-------------------------------+
    |           | fail      | bool  | True - encountered an error   |
    |           |           |       | Fail - No errors encountered. |
    +-----------+-----------+-------+-------------------------------+
    |           | io        | bool  | True - Opertion completed by  |
    |           |           |       | performing an API request.    |
    |           |           |       | False - No API request was    |
    |           |           |       | made. This occurs when test   |
    |           |           |       | is True or force is True but  |
    |           |           |       | no switch operation was       |
    |           |           |       | required.                     |
    +-----------+-----------+-------+-------------------------------+
    |           | status    | int   | Status, if any, returned from |
    |           |           |       | from the switch if a request  |
    |           |           |       | was actually made. There will |
    |           |           |       | always be a status if the     |
    |           |           |       | request failed but status is  |
    |           |           |       | not always returned for       |
    |           |           |       | success. If io is False, the  |
    |           |           |       | status is made up.            |
    +-----------+-----------+-------+-------------------------------+
    |           | reason    | str   | Reason, if provided, returned |
    |           |           |       | from FOS. If io is False, the |
    |           |           |       | reason is made up.            |
    +-----------+-----------+-------+-------------------------------+
    |           | err_msg   | list  | List of detailed error        |
    |           |           |       | messages returned from FOS.   |
    |           |           |       | If io is False, the detailed  |
    |           |           |       | messages are made up. Not     |
    |           |           |       | always present with errors.   |
    +-----------+-----------+-------+-------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 01 Nov 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '13 Feb 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.1'

import sys
import datetime
import itertools

import brcdapi.util as brcdapi_util
import brcdapi.zone as brcdapi_zone
import brcdapi.pyfos_auth as pyfos_auth
import brcdapi.log as brcdapi_log
import brcdapi.brcdapi_rest as brcdapi_rest
import brcddb.brcddb_project as brcddb_project
import brcddb.util.copy as brcddb_copy
import brcddb.util.file as brcddb_file
import brcddb.util.util as brcddb_util
import brcddb.brcddb_common as brcddb_common
import brcddb.api.zone as api_zone
import brcddb.api.interface as api_int
import brcddb.brcddb_fabric as brcddb_fabric
import brcddb.app_data.alert_tables as al

_DEBUG_FICON = True

# Global arguments that get overwritten
ip = None
user_id = None
pw = None
sec = 'none'
fid = 128
t_flag = False  # True - Test mode only - no changes actually sent to the switch
f_flag = False  # True - overide existing zone database
b_flag = False  # True - perform bulk zoning
fab_obj = None
checksum = None
skip_pend_flag = False
pending = []    # List of pending zoning actions in the FOS zone transaction buffer
_good_test_return = {'status': brcdapi_util.HTTP_OK, 'io': False, 'changed': True, 'fail': False}
_good_force_nop_return = {'status': brcdapi_util.HTTP_OK, 'io': False, 'changed': False, 'fail': False}
_def_zone_access_tbl = {
    '--noaccess': brcddb_common.DEF_ZONE_NOACCESS,
    '--allaccess': brcddb_common.DEF_ZONE_ALLACCESS,
    '--show': -1,
}
# Zone URIs
zone_uris = (
    'brocade-zone/defined-configuration',
    'brocade-zone/effective-configuration',
)


def version():
    """Returns the module version number

    :return: Version
    :rtype: str
    """
    return __version__


def _format_api_error(obj, io, changed, fail):
    """Formats an API response into the return dict

    :param obj: Returned object from an API call
    :type obj: dict
    :param io: True - a request was sent to and processed by the switch. False - this is a made up error
    :type io: bool
    :param changed: True - A change was made on the switch, False - no change was made
    :type changed: bool
    :param fail: True - The request failed. False - the request did not fail
    :type fail: bool
    """
    return {'status': pyfos_auth.obj_status(obj),
                     'reason': pyfos_auth.obj_reason(obj),
                     'err_msg': pyfos_auth.obj_error_detail(obj),
                     'io': False,
                     'changed': False,
                     'fail': True}


def _format_cmd_for_brcdapi(cmd):
    """Convert the cmd dict structure used herein to the dict that the brcdapi zone library wants to see

    :param cmd: Dictionary element as described in **Input** -> changes
    :type cmd: dict
    :return: brcdapi.zone library data structure
    :rtype: dict
    """
    return {
        'name': cmd['operand'],
        'members': cmd['p0'],
        'pmembers': cmd['p1'],
        'type': brcddb_common.ZONE_USER_PEER if cmd['peer'] else brcddb_common.ZONE_STANDARD_ZONE,
    }


def _format_return(obj):
    """Creates the return dictionary

    :param obj: FOS API object
    :type obj: dict
    :return: Per command dictionary as defined in commands (See **Return** -> commands)
    :rtype: dict
    """
    if pyfos_auth.is_error(obj):
        return _format_api_error(obj, True, False, True)
    else:
        try:
            status = obj['_raw_data']['status']
        except:
            status = brcdapi_util.HTTP_OK
        try:
            return {'status': brcdapi_util.HTTP_OK, 'reason': obj['_raw_data']['reason'], 'io': True,
                    'changed': True, 'fail': False}
        except:
            return {'status': brcdapi_util.HTTP_OK, 'io': True, 'changed': True, 'fail': False}


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
    p0 = brcddb_util.convert_to_list(cmd.get('p0'))
    p1 = brcddb_util.convert_to_list(cmd.get('p1'))
    if strict:
        err_msg = []
        if operand is not None:
            err_msg.append('operand: ' + str(operand) )
        if len(p0) > 0:
            err_msg.append('p0:\n  ' + '  \n'.join(p0))
        if len(p1) > 0:
            err_msg.append('p1:\n  ' + '  \n'.join(p1))
        if len(err_msg) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Unsupported parameters', 'err_msg': err_msg,
                    'io': False, 'changed': False, 'fail': True}, p0, p1
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
    p0 = brcddb_util.convert_to_list(cmd.get('p0'))
    p1 = brcddb_util.convert_to_list(cmd.get('p1'))
    if operand is None:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': brcdapi_util.HTTP_REASON_MISSING_OPERAND,
                'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    if cmd.get('c-type') == 'defzone':
        if operand not in _def_zone_access_tbl:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid option for defzone',
                    'err_msg': [str(operand)], 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    elif not brcddb_util.is_valid_zone_name(operand):
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid zone object name',
                'err_msg': [str(operand)], 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    if strict:
        err_msg = []
        if len(p0) > 0:
            err_msg.append('p0:\n  ' + '  \n'.join(p0))
        if len(p1) > 0:
            err_msg.append('p1:\n  ' + '  \n'.join(p1))
        if len(err_msg) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Unsupported parameters', 'err_msg': err_msg,
                    'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    return None, operand, p0, p1


def _p0_check(cmd, strict=False):
    """Validates the operand and one parameter (p0)

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand and p0 only
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if len(p0) == 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': str(operand) + ' missing members',
                'err_msg': ['p0'], 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    if strict:
        if len(p1) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST,
                    'reason': str(operand) + ' has unsupported parameters (p1)',
                    'err_msg': p1, 'io': False, 'changed': False, 'fail': True}, operand, p0, p1

    return None, operand, p0, p1


def _p1_check(cmd, strict=False):
    """Validates the operand and p1.

    Same input parameters and returns as _operand_check(). When strict is True, must contain an operand and only p1
    """
    obj, operand, p0, p1 = _operand_check(cmd)
    if obj is not None:
        return obj, operand, p0, p1
    if len(p1) == 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': str(operand) + ' missing members',
                'err_msg': ['principal members: p1'], 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    if strict:
        if len(p0) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': str(operand) +  ' has unsupported parameters',
                    'err_msg': ['p0:\n  ' + '  \n'.join(p1)], 'io': False, 'changed': False, 'fail': True}, p0, p1

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
        err_msg = []
        if len(p0) == 0:
            err_msg.append('members: p0')
        if len(p1) == 0:
            err_msg.append('principal members: p1')
        if len(err_msg) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': str(operand) +  ' missing members',
                    'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    elif len(p0) + len(p1) == 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': str(operand) + ' requires p0 or p1',
                'err_msg': [], 'io': False, 'changed': False, 'fail': True}, operand, p0, p1
    return None, operand, p0, p1


def _p0_f_OK(cmd, strict=False):
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
            return {'status': brcdapi_util.HTTP_BAD_REQUEST,
                    'reason': str(operand) + ' has unsupported parameters (p1)',
                    'err_msg': p0 + p1, 'io': False, 'changed': False, 'fail': True}, operand, p0, p1

    return None, operand, p0, p1


def refresh_zoning(session, fab_id, fabric_obj):
    """Deletes all zoning information from the fabric object and refreshes with new zoning data

    :param session: Session object, or list of session objects, returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param fab_id: Fabric ID. Not using global fid because this method can be called externally.
    :type fab_id: int
    :param fabric_obj: Fabric object. Not using global fab_obj because this method can be called externally.
    :return: Error message. If no errors, None
    :rtype: str, None
    """
    global zone_uris

    # Just wipe out the fabric object and create a new one
    proj_obj = fabric_obj.r_project_obj()
    fab_key = fabric_obj.r_obj_key()
    switch_list = fabric_obj.r_switch_keys()
    proj_obj.s_del_fabric(fab_key)
    fabric_obj = proj_obj.s_add_fabric(fab_key)
    for wwn in switch_list:
        fabric_obj.s_add_switch(wwn)

    # Capture the current zoning information
    api_int.get_batch(session, proj_obj, [], zone_uris, fid)
    if len(fabric_obj.r_project_obj().r_alert_objects()) > 0:
        return _API_ERROR
    return None




##################################################################
#
#      Methods used in change_type_func
#
###################################################################
def _alias_add(session, cmd):
    """Add members to an existing alias. If force is set and the alais doesn't exist, it will be created

    :param session: Session object, or list of session objects, returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command
    obj, alias, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    ali_obj = fab_obj.r_alias_obj(alias)
    if ali_obj is None:
        if f_flag:
            return _alias_create(session, cmd)  # The alias doesn't exist so create it.
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                'err_msg': [alias], 'io': False, 'changed': False, 'fail': True}

    # If we got this far, the alias already existed so add the member to it.
    members = ali_obj.r_members()
    p0 = [mem for mem in tp0 if mem in members]  # List of members to add that are already members
    if len(p0) > 0 and not f_flag:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': alias + ' member already exists',
                'err_msg': p0, 'io': False, 'changed': False, 'fail': True}
    p0 = [mem for mem in tp0 if mem not in members]  # List of members to add that are not already members
    err_msg = [mem for mem in p0 if ',' not in mem and not brcddb_util.is_wwn(mem)]  # List of invalid members
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid WWN',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    ali_obj.s_add_member(p0)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))


def _alias_create(session, cmd):
    """Create an alias. If force is set and the alais exists, it will be overwritten

    See _alias_add() for a description of input and return values"""
    global fid, f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not brcddb_util.is_valid_zone_name(alias):  # Make sure it's a valid alias name
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid alias name',
                'err_msg': [alias], 'io': False, 'changed': False, 'fail': True}
    err_msg = [mem for mem in p0 if ',' not in mem and not brcddb_util.is_wwn(mem)]  # Make sure its a valid d,i or WWN
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid WWN',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    if fab_obj.r_alias_obj(alias) is None:
        fab_obj.s_add_alias(alias, p0)
        if t_flag or b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    # If we got this far, the alias already exists
    if f_flag:  # Overwrite the alias if f_flag is True by deleting it and then creating this one
        fab_obj.s_del_alias(alias)
        fab_obj.s_add_alias(alias, p0)
        if t_flag or b_flag:
            return _good_test_return
        obj = _alias_delete(session, {'operand': cmd.get('operand'), 'p0': [], 'p1': [], 'peer': cmd.get('peer')})
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    else:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Alias already exists',
                'err_msg': [alias], 'io': False, 'changed': False, 'fail': True}


def _alias_delete(session, cmd):
    """Delete an alias. If force is set and the alais doesn't exist, no action is takend and good status is returned

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    ali_obj = fab_obj.r_alias_obj(alias)
    if ali_obj is None:
        if f_flag:
            return _good_force_nop_return
        else:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Alias not found',
                    'err_msg': [alias], 'io': False, 'changed': False, 'fail': True}
    zl = [obj.r_obj_key() for obj in ali_obj.r_zone_objects()]  # List of zones where alias is used
    if len(zl) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Alias in use',
                'err_msg': zl, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    fab_obj.s_del_alias(alias)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_aliases(session, fid, [_format_cmd_for_brcdapi(cmd)]))


def _alias_remove(session, cmd):
    """Remove alias members. If force is set and the alais doesn't exist, no action is taken and good status is returned

    See _alias_add() for a description of input and return values."""
    global f_flag, t_flag, fab_obj, b_flag

    # Validate the command and operands
    obj, alias, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    alias_obj = fab_obj.r_alias_obj(alias)
    if alias_obj is None:
        if f_flag:
            return _good_force_nop_return
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': alias + ' does not exist',
                'err_msg': [], 'io': False, 'changed': False, 'fail': True}
    members = alias_obj.r_members()
    if not f_flag:
        t_members = [mem for mem in p0 if mem not in members]  # Get a list of members to remove that don't exist
        if len(t_members) > 0:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Members not in ' + alias,
                    'err_msg': t_members, 'io': False, 'changed': False, 'fail': True}
    t_member = [mem for mem in members if mem not in p0]  # Members to keep

    # Execute the command. The only way to remove a member via the API is to delete and create it
    if t_flag or b_flag:
        return _good_test_return
    obj = _alias_delete(session, {'operand': cmd.get('operand'), 'p0': [], 'p1': [], 'peer': cmd.get('peer')})
    if obj['fail']:
        return obj
    return _alias_create(session, cmd)


def _cfg_add(session, cmd):
    """Add zone members to an existing configuration. If force is set and the zone configuration doesn't exist, it will
    be created

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command
    obj, zonecfg, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj

    # Make sure the zone configuration exists
    zonecfg_obj = fab_obj.r_zonecfg_obj(zonecfg)
    if zonecfg_obj is None:
        if f_flag:
            return _cfg_create(session, cmd)  # The zonecfg doesn't exist so create it.
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}

    # If we got this far, the zonecfg already existed so add the member(s) to it.
    members = zonecfg_obj.r_members()
    existing_members = [mem for mem in tp0 if mem in members]  # List of members to add that are already members
    if len(existing_members) > 0 and not f_flag:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': alias + ' member already exists',
                'err_msg': existing_members, 'io': False, 'changed': False, 'fail': True}
    p0 = [mem for mem in tp0 if mem not in members]  # List of members to add that are not already members
    err_msg = [mem for mem in p0 if fab_obj.r_zone_obj(mem) is None]  # Make sure members exist
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Zone member(s) do not exist',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}
    if len(p0) == 0:  # Make sure there is something to add
        if f_flag:
            return _good_force_nop_return
        else:
            reason = 'No member(s) to add to ' + zonecfg + '. Members removed because they arleady were members, if '\
                                                           'any, are in the err_msg detail'
            return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': reason,
                    'err_msg': existing_members, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    zonecfg_obj.s_add_member(p0)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.zonecfg_add(session, fid, zonecfg, p0))


def _cfg_create(session, cmd):
    """Create a zone configuration. If force is set and the configuration exists, it will be overwritten

    See _alias_add() for a description of input and return values"""
    global fid, f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not brcddb_util.is_valid_zone_name(zonecfg):  # Make sure it's a valid zone configuration name
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid zone configuration name',
                'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}
    err_msg = [mem for mem in p0 if fab_obj.r_zone_obj(mem) is None]  # Make sure members exist
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Zone member(s) do not exist',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    if fab_obj.r_zonecfg_obj(zonecfg) is None:
        fab_obj.s_add_zonecfg(zonecfg, p0)
        if t_flag or b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_zonecfg(session, fid, zonecfg, p0))

    # If we got this far, the zone configuration already exists
    if f_flag:  # Overwrite the zone configuration if f_flag is True by deleting it and then creating this one
        fab_obj.s_del_zonecfg(zonecfg)
        fab_obj.s_add_zonecfg(zonecfg, p0)
        if t_flag or b_flag:
            return _good_test_return
        obj = _cfg_delete(session, {'operand': cmd.get('operand'), 'p0': [], 'p1': [], 'peer': cmd.get('peer')})
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_zonecfg(session, fid, [_format_cmd_for_brcdapi(cmd)]))
    else:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Zone configuration already exists',
                'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}


def _cfg_delete(session, cmd):
    """Delete a zone configuration. If force is set and the configuration doesn't exist, good status is returned

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    if fab_obj.r_zonecfg_obj(zonecfg) is None:
        if f_flag:
            return _good_force_nop_return
        else:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Zone configuration not found',
                    'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    fab_obj.s_del_zonecfg(zonecfg)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_zonecfg(session, fid, zonecfg))


def _cfg_enable(session, cmd):
    """Enable a zone configuration. The force flag, f_flag, does nothing.

    See _alias_add() for a description of input and return values"""
    global fab_obj, t_flag, checksum, pending, skip_pend_flag, b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _p0_f_OK(cmd, True)
    if obj is not None:
        return obj
    # It would be nice to see if the defined zone configuration is already the effective zone configuration and if so,
    # check to see if any of the members changed but that's for another revision. The only thing being checked for is
    # to make sure the zone configuration exists.
    if fab_obj.r_zonecfg_obj(zonecfg) is None:
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    if t_flag or b_flag:
        # WARNING: The effective zone database in the fabric object, fab_obj, is now out of date. There is no software
        # utility to simulate the zoning response and since we are in test mode, we can't just refresh the zoning
        # database from the switch. Writting a software utility to update it wouldn't be hard but as a practical matter,
        # I don't know of anyone who makes zoning changes, enables a zone configuration, and then continues to make
        # zoning changes all in the same activity so I didn't bother. This is only a problem in test mode.
        return _good_test_return
    zobj = brcdapi_zone.enable_zonecfg(session, checksum, fid, zonecfg)
    if not pyfos_auth.is_error(zobj):
        msg = refresh_zoning(session, fid, fab_obj)
        if msg is not None:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST,
                    'reason': 'API error occured while refreshing the zone DB',
                    'err_msg': [msg], 'io': False, 'changed': False, 'fail': True}
        pending = []  # A cfgsave is inherent when a zone configuration is enabled.
        skip_pend_flag = True
        checksum, obj = brcdapi_zone.checksum(session, fid)  # Need a new checksum in case there are additional changes
        if pyfos_auth.is_error(obj):
            return {'status': brcdapi_util.HTTP_BAD_REQUEST,
                    'reason': 'Sucessfully enabled ' + zonecfg + ', but could not refresh the checksum',
                    'err_msg': ['Check the log for details'], 'io': False, 'changed': False, 'fail': True}
    return _format_return(zobj)


def _cfg_remove(session, cmd):
    """Remove a zone from an existing zone configuration. If force is set and the zone is not in the configuraiton of
    configuraiton doesn't exist, good status is returned.

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    obj, zonecfg, tp0, tp1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    zonecfg_obj = fab_obj.r_zonecfg_obj(zonecfg)
    # Does the zone configuration exist?
    if zonecfg_obj is None:
        if f_flag:
            return _good_force_nop_return
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                    'err_msg': [zonecfg], 'io': False, 'changed': False, 'fail': True}
    # Do the members exist?
    no_exist = [mem for mem in tp0 if not zonecfg_obj.r_has_member(mem)]
    if len(no_exist) > 0 and not f_flag:
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                    'err_msg': [no_exist], 'io': False, 'changed': False, 'fail': True}
    p0 = [mem for mem in tp0 if mem not in no_exist]
    if len(p0) == 0:
        if f_flag:
            return _good_force_nop_return
        else:
            reason = 'No members to remove. Requested memebrs to remove that were not in ' + zonecfg + ', if any, '
            reason += 'are in the err_msg detail'
            return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': reason,
                    'err_msg': [no_exist], 'io': False, 'changed': False, 'fail': True}

    # Execute the request to delete the members
    zonecfg_obj.s_del_member([mem for mem in tp0 if not zonecfg_obj.r_has_member(mem)])
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.zonecfg_remove(session, fid, zonecfg, p0))


def _cfg_save(session, cmd):
    """Causes the zone database to be pushed to the fabric. The force flag is only relevant in test mode. In test mode,
    if force is not set and there are pending transansactions, an error is returned. Otherwise, the action is always
    sent to the switch

    See _alias_add() for a description of input and return values"""
    global fid, f_flag, t_flag, fab_obj, pending, checksum, skip_pend_flag, b_flag

    # Validate the command and operands
    obj, zonecfg, p0, p1 = _no_operand_check(cmd)
    if obj is not None:
        return obj
    skip_pend_flag = True
    if t_flag or b_flag:
        if not f_flag and len(pending) == 0:
            obj = pyfos_auth.create_error(brcdapi_util.HTTP_NO_CONTENT, 'No pending zone transactions', '')
            return (_format_api_error(obj, False, False, True))
        return _good_test_return
    obj = brcdapi_zone.save(session, fid, checksum)
    if pyfos_auth.is_error(obj):
        return _format_api_error(obj, True, False, True)
    pending = []
    checksum, obj = brcdapi_zone.checksum(session, fid)  # Need a new checksum in case there are additional changes
    return _format_return(obj)


def _defzone(session, cmd):
    """Set the default zone. The force flag, f_flag, does nothing

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, _def_zone_access_tbl, b_flag

    # Validate the command and operands
    obj, action, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    try:
        access = _def_zone_access_tbl[action]
        if access < 0:  # --show is -1 in _def_zone_access_tbl
            return _good_force_nop_return
    except:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid operand',
                'err_msg': action, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    skip_pend_flag = True
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.default_zone(session, fid, access))


def _zone_add(session, cmd):
    """Add members to an existing zone. If force is set and zone doesn't exist, it will be created.

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, b_flag

    # Validate the command
    obj, zone, p0, p1 = _p0_p1_check(cmd)
    if obj is not None:
        return obj
    zone_obj = fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if f_flag:
            return _zone_create(session, cmd)  # The zone doesn't exist so create it.

        # Debug
        debug_status = brcdapi_util.HTTP_NOT_FOUND
        debug_reason = brcdapi_util.HTTP_REASON_NOT_FOUND
        debug_err_msg = [zone]
        debug_io = False
        debug_changed = False
        debug_fail = True
        debug_obj = {'status': debug_status, 'reason': debug_reason,
                'err_msg': debug_err_msg, 'io': debug_io, 'changed': debug_changed, 'fail': debug_fail}
        print(str(len(debug_obj)))

        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                'err_msg': [zone], 'io': False, 'changed': False, 'fail': True}

    # If we got this far, the zone already existed. Validate and figure out which members to add.
    for buf in ('member', 'principal'):
        members = zone_obj.r_members() if buf == 'member' else zone_obj.r_pmembers()
        test_p = p0 if buf == 'member' else p1
        px = [mem for mem in test_p if mem in members]  # List of members to add that are already members
        if len(px) > 0 and not f_flag:
            return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': zone + ' ' + buf + ' already exists',
                    'err_msg': px, 'io': False, 'changed': False, 'fail': True}
        px = [mem for mem in test_p if mem not in members]  # List of members to add that are not already members
        err_msg = [mem for mem in test_p if ',' not in mem and not brcddb_util.is_wwn(mem) and
                   not brcddb_util.is_valid_zone_name(mem)]  # List of invalid zone members
        if len(err_msg) > 0:
            return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid zone member(s)',
                    'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}
        if buf == 'member':  # If forcing changes, only send the added members to the switch
            new_p0 = px
        else:
            new_p1 = px
    err_msg = [mem for mem in new_p0 if mem in new_p1 + zone_obj.r_pmembers()]  # Members that are also principals
    err_msg.extend([mem for mem in new_p1 if mem in new_p0 + zone_obj.r_members()])  # Prinipals that are also members
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT,
                'reason': 'Members and principal members must be exclusive',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}
    new_cmd = {}
    for k in cmd.keys():
        v = new_p0 if k == 'p0' else new_p1 if k == 'p1' else cmd.get(k)
        new_cmd.update({k: v})

    # Execute the command
    zone_obj.s_add_member(new_p0)
    zone_obj.s_add_pmember(new_p1)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.create_zones(session, fid, [_format_cmd_for_brcdapi(new_cmd)]))


def _zone_create(session, cmd):
    """Create a zone. If force is set and the zone already exists, it is overwritten

    See _alias_add() for a description of input and return values"""
    global fid, f_flag, fab_obj, t_flag, b_flag

    # Validate the command and operands
    if cmd['peer']:
        zone_type = brcddb_common.ZONE_USER_PEER
        obj, zone, p0, p1 = _p1_check(cmd)
    else:
        zone_type = brcddb_common.ZONE_STANDARD_ZONE
        obj, zone, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    if not brcddb_util.is_valid_zone_name(zone):  # Make sure it's a valid zone name
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid zone name',
                'err_msg': [zone], 'io': False, 'changed': False, 'fail': True}
    err_msg = [mem for mem in p0 if ',' not in mem and not brcddb_util.is_wwn(mem) and
               not brcddb_util.is_valid_zone_name(mem)]  # List of invalid zone members
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Invalid zone member(s)',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}
    err_msg = [mem for mem in p0 if mem in p1]  # Members in p0 that are also in p1
    err_msg.extend(([mem for mem in p1 if mem in p0]))  # Add members in p1 that are also in p0
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT,
                'reason': 'Members and principal members must be exclusive',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}
    # Figure out if there are any dupicate members after resolving the aliases. The previous check just checked to make
    # sure there were no duplicates as defined. Zone are usually defined with aliases. Below resolves the aliases into
    # WWNs and checks for duplicates in the resolved list of members.
    # often is with aliases. If two different aliases have the same member, a duplicate member error is returned from
    # FOS but you have no idea which one. The above check would be covered in this check but by doing two seperate
    # checks, the error message(s) can articulate the error.
    err_msg = []
    resolved = [[], []]  # Members in d,i or WWN - 0: members in p0, 1: members in p1
    desc = ['p0', 'p1']
    px = [p0, p1]
    for i in range(0, 2):
        for mem in px[i]:  # This loop builds the resolved list
            if ',' not in mem and not brcddb_util.is_wwn(mem):
                alias_obj = fab_obj.r_alias_obj(mem)
                if alias_obj is None:
                    err_msg.append('Alias ' + mem + ' does not exist')
                else:
                    resolved.extend(alias_obj.r_members())
            else:
                resolved.append(mem)
    # Now check for duplicates
    found = [[], []]
    for i in range(0, 2):
        for mem in resolved[i]:
            x = 0 if i == 1 else 1
            if mem in found[i]:
                err_msg.append('Duplicate member ' + mem + ' in ' + desc[i] + '. Ailas(es): ' +
                               ', '.join(fab_obj.r_alias_for_wwn(mem)))
            if mem in found[x]:
                err_msg.append('Duplicate member ' + mem + ' in ' + desc[i] + '. Ailas(es): ' +
                               ', '.join(fab_obj.r_alias_for_wwn(mem)))

    err_msg = []
    resolved = []
    for mem in p0 + p1:
        if ',' not in mem and not brcddb_util.is_wwn(mem):
            alias_obj = fab_obj.r_alias_obj(mem)
            if alias_obj is None:
                err_msg.append('Alias ' + mem + ' does not exist')
            else:
                for ali_mem in alias_obj.r_members():
                    if ali_mem in resolved:
                        err_msg.append('Duplicate member: ' + ali_mem + ' appears in: '
                                       + ', '.join(fab_obj.r_alias_for_wwn(ali_mem)))
                    resolved.append(ali_mem)
        else:
            resolved.append(mem)
    if len(err_msg) > 0:
        return {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Zone: ' + zone + ' contains invalid members',
                'err_msg': err_msg, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    if fab_obj.r_zone_obj(zone) is None:
        fab_obj.s_add_zone(zone, zone_type, p0, p1)
        if t_flag or b_flag:
            return _good_test_return
        return _format_return(brcdapi_zone.create_zones(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    # If we got this far, the zone already exists
    if f_flag:  # Overwrite the zone if f_flag is True by deleting it and then creating this one
        fab_obj.s_del_zone(zone)
        fab_obj.s_add_zone(zone, zone_type, p0, p1)
        if t_flag or b_flag:
            return _good_test_return
        obj = _zone_delete(session, {'operand': cmd.get('operand'), 'p0': [], 'p1': [], 'peer': cmd.get('peer')})
        if obj['fail']:
            return obj
        return _format_return(brcdapi_zone.create_zonees(session, fid, [_format_cmd_for_brcdapi(cmd)]))

    else:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Alias already exists',
                'err_msg': [zone], 'io': False, 'changed': False, 'fail': True}


def _zone_delete(session, cmd):
    """Delete a zone. If force is set and the zone does not exist, good status is returned

    See _alias_add() for a description of input and return values"""
    global f_flag, fab_obj, t_flag, fid, b_flag

    # Validate the command and operands
    obj, zone, p0, p1 = _operand_check(cmd, True)
    if obj is not None:
        return obj
    zone_obj = fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if f_flag:
            return _good_force_nop_return
        else:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Zone not found',
                    'err_msg': [zone], 'io': False, 'changed': False, 'fail': True}
    zl = [obj.r_obj_key() for obj in zone_obj.r_zonecfg_objects()]  # List of zone configurations where zone is used
    if len(zl) > 0:
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT, 'reason': 'Zone in use',
                'err_msg': zl, 'io': False, 'changed': False, 'fail': True}

    # Execute the command
    fab_obj.s_del_zone(zone)
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(brcdapi_zone.del_zones(session, fid, [_format_cmd_for_brcdapi(cmd)]))


def _alias_copy_int(session, obj):
    """Used by _zone_object_copy() and _zone_object_rename() to copy an alias

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param obj: Alias object to create
    :type obj: brcddb.classes.AliasObj
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    global fid

    return brcdapi_zone.create_aliases(session, fid, [{'name': obj.r_obj_key(), 'members': obj.r_members()}])


def _zone_copy_int(session, obj):
    """Used by _zone_object_copy() and _zone_object_rename() to copy a zone

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param obj: Zone object to create
    :type obj: brcddb.classes.ZoneObj
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    send_obj = {
        'name': obj.r_obj_key(),
        'members': obj.r_members(),
        'pmembers': obj.r_pmembers(),
        'type': obj.r_type(),
    }
    return brcdapi_zone.create_zones(session, fid, [send_obj])


def _zonecfg_copy_int(session, obj):
    """Used by _zone_object_copy() and _zone_object_rename() to copy a zone configuration

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param obj: Zone configuration object to create
    :type obj: brcddb.classes.ZoneCfgObj
    :return obj: Dictionary as defined in 'commands' in the response
    :rtype obj: dict
    """
    return brcdapi_zone.create_zonecfg(session, fid, obj.r_obj_key(), obj.r_members())


def _alias_replace_int(session, old, new):
    """Used by _zone_object_rename() to replace an alias in all zones with a new alias name

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param old: Name of alias to be replaced
    :type old: str
    :return new: Name of new replacement alias
    :rtype new: str
    """
    global fid, fab_obj

    zone_l = fab_obj.r_zones_for_alias(old)
    if len(zone_l) > 0:  # Don't forget, the alias may not be used in any zones.
        for zone in zone_l:
            zone_obj = fab_obj.r_zone_obj(zone)
            if old in zone_obj.r_members():
                del_members = [old]
                del_pmembers = []
                add_members = [new]
                add_pmembers = []
            else:   # If it's not a member so it must be a pmember
                del_members = []
                del_pmembers = [old]
                add_members = []
                add_pmembers = [new]
            obj = brcdapi_zone.modify_zone(session, fid, zone, add_members, del_members, add_pmembers, del_pmembers)
            if pyfos_auth.is_error(obj):
                return obj
        obj = brcdapi_zone.del_aliases(session, fid, [{'name': old}])
        if not pyfos_auth.is_error(obj):
            fab_obj.s_del_alias(old)
        return obj
    else:  # The alias isn't used if we get here
        return {}  # I only check for bad status. No status is not "good", but it's not "bad" so this is good enough

def _zone_replace_int(session, old, new):
    """Used by _zone_object_rename() to replace a zone in all zone configurations with a new zone name

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param old: Name of zone to be replaced with new and deleted
    :type old: str
    :return new: Name of replacement zone
    :rtype new: str
    """
    global fab_obj

    # Find every zone configuration where the old zone is used and replace with the new zone
    zonecfg_l = fab_obj.r_zonecfgs_for_zone(old)
    if len(zonecfg_l) > 0:  # Don't forget, the zone may not be used in any zone configurations.
        for zonecfg in zonecfg_l:
            obj = brcdapi_zone.zonecfg_remove(session, fid, zonecfg, [old])  # Remove old zone from the configuration
            if pyfos_auth.is_error(obj):
                return obj
            obj = brcdapi_zone.zonecfg_add(session, fid, zonecfg, [new])  # Add new zone to the configuraiton
            if pyfos_auth.is_error(obj):
                return obj
        obj = brcdapi_zone.del_zones(session, fid, [old])  # Delete the old zone
        if pyfos_auth.is_error(obj):
            return obj
        fab_obj.s_del_zone(old)  # Delete the zone from the database

    return {}  # I only check for bad status. No status is not "good", but it's not "bad" so this is good enough


def _zonecfg_replace_int(session, old, new):
    """Used by _zone_object_rename() to delete a zone configuration

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param old: Name of zone configuration to delete
    :type old: str
    :return new: Not used
    :rtype new: str
    """
    return brcdapi_zone.del_zonecfg(session, fid, old)


_zone_copy_action = {
    'alias': {'copy': _alias_copy_int, 'replace': _alias_replace_int},
    'zone': {'copy': _zone_copy_int, 'replace': _zone_replace_int},
    'zonecfg': {'copy': _zonecfg_copy_int, 'replace': _zonecfg_replace_int}
}


def _zone_copy_rename_param(session, cmd):
    """Used by _zone_object_copy() and _zone_object_rename() to validate parameters and determine the zone object type

    :param session: Session object returned from brcdapi.pyfos_auth.login()
    :type session: dict
    :param cmd: Dictionary as returned in the list from 'changes' in the input
    :type cmd: dict
    :return obj: Dictionary as defined in 'commands' in the response if an error was encounted. Otherwise None
    :rtype obj: dict, None
    :return zoneobj: The zone object to be copied or renamed. None if the zone object was not found
    :rtype zoneobj: brcddb.classes.AliasObj, brcddb.classes.ZoneObj, brcddb.classes.ZoneCfgObj, None
    :return new_obj: Name of the new zone object (copy of zoneobj). None if an error occured
    :rtype new_obj: str, None
    :return type: 'alias', 'zone', or 'zonecfg'. May be '' if an error was encountered
    :rtype type: str
    """
    global f_flag, t_flag, fab_obj, b_flag

    # Validate the command and operands
    obj, zoneobj_name, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj, p0, zone_obj_type
    if len(p0) != 1:  # It can't be 0 because _p0_check() would have caught that case
        err_obj = {'status': brcdapi_util.HTTP_BAD_REQUEST, 'reason': 'Too many parameters',
                'err_msg': p0, 'io': False, 'changed': False, 'fail': True}
        return err_obj, None, p0[0], ''

    # Find the zone object to copy and make the copy in brcddb
    zone_obj_types = {
        'zonecfg': fab_obj.r_zonecfg_obj,
        'zone': fab_obj.r_zone_obj,
        'alias': fab_obj.r_alias_obj,
    }
    for buf in zone_obj_types.keys():
        obj = zone_obj_types[buf](zoneobj_name)
        if obj is not None:
            copied_obj = obj.s_copy(p0[0])
            if copied_obj is None:
                err_obj = {'status': brcdapi_util.HTTP_REQUEST_CONFLICT,
                           'reason': buf + ' ' + p0[0] + ' already exists',
                           'err_msg': [], 'io': False, 'changed': False, 'fail': True}
                return err_obj, None, None, buf
            else:
                return None, obj, copied_obj, buf

    err_obj = {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
               'err_msg': [zoneobj_name], 'io': False, 'changed': False, 'fail': True}
    return err_obj, None, None, ''


def _zone_object_copy(session, cmd):
    """Copies a zone object. Force is ignored. The destination zone object will not be over written if it already exists

    See _alias_add() for a description of input and return values"""
    global f_flag, t_flag, fab_obj, b_flag

    # Validate the command and operands
    obj, zoneobj, copy_obj, zone_type = _zone_copy_rename_param(session, cmd)
    if obj is not None:
        return obj

    # Make the copy
    if t_flag or b_flag:
        return _good_test_return
    return _format_return(_zone_copy_action[zone_type]['copy'](session, copy_obj))


def _zone_object_rename(session, cmd):
    """Renames a zone object and iteratively updates all zone objects where used. Force does nothing. You cannot rename
    an object over an existing object. You cannot rename the effective zone configuration.

    See _alias_add() for a description of input and return values"""
    global f_flag, t_flag, fab_obj, b_flag

    eff_zone_name = fab_obj.r_defined_eff_zonecfg_key()
    if isinstance(cmd['operand'], str) and cmd['operand'] == eff_zone_name:
        # Renaming the defined zone configuration when it's also the effective zone configuration is not permitted.
        # Back out the copy and return an error
        return {'status': brcdapi_util.HTTP_REQUEST_CONFLICT,
                'reason': 'Renaming the effective zone configuration is not permitted',
                'err_msg': [eff_zone_name], 'io': False, 'changed': False, 'fail': True}

    obj, zoneobj, copy_obj, zone_type = _zone_copy_rename_param(session, cmd)
    if obj is not None:
        return obj

    # Make the copy
    if t_flag or b_flag:
        return _good_test_return
    obj = _zone_copy_action[zone_type]['copy'](session, copy_obj)
    if pyfos_auth.is_error(obj):
        return _format_return(obj)

    # Replace everywhere this zone object was used and replace it with the copy
    return _format_return(_zone_copy_action[zone_type]['replace'](session, zoneobj.r_obj_key(), copy_obj.r_obj_key()))

def _zone_remove(session, cmd):
    """Remove zone members. If force is set and the zone or member does not exist, good status is retruned.

    See _alias_add() for a description of input and return values"""
    global f_flag, t_flag, fab_obj, b_flag

    # Validate the command and operands
    obj, zone, p0, p1 = _p0_check(cmd, True)
    if obj is not None:
        return obj
    zone_obj = fab_obj.r_zone_obj(zone)
    if zone_obj is None:
        if f_flag:
            return _good_force_nop_return
        return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': zone + ' does not exist',
                'err_msg': [], 'io': False, 'changed': False, 'fail': True}
    members = zone_obj.r_members()
    if not f_flag:
        t_members = [mem for mem in p0 if mem not in members]  # Get a list of members to remove that don't exist
        # Note that if the zone was created with an alias and the remove is by d,i or WWN, not only am I not going to
        # catch it here, neither will FOS.
        if len(t_members) > 0:
            return {'status': brcdapi_util.HTTP_NOT_FOUND, 'reason': 'Members not in ' + zone,
                    'err_msg': t_members, 'io': False, 'changed': False, 'fail': True}
    t_member = [mem for mem in p0 if mem not in members]  # Members to remove

    # Execute the command. The only way to remove a member via the API is to delete and create it
    if t_flag or b_flag:
        return _good_test_return
    obj = _zone_delete(session, {'operand': cmd.get('operand'), 'p0': [], 'p1': [], 'peer': cmd.get('peer')})
    if obj['fail']:
        return obj
    return _zone_create(session, cmd)


# Table cmd_func is the C like case statement
change_type_func = {
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
    global error_count, warn_count, t_flag, user_id, pw, ip, sec, f_flag, pending, fid, change_type_func,\
        _RESPONSE_ERROR, _RESPONSE_WARN, fab_obj, checksum, skip_pend_flag, zone_uris, b_flag

    # Initialize application control and validate request
    response = []
    must_have = {
        'ip-addr': content.get('ip-addr'),
        'id': content.get('id'),
        'pw': content.get('pw'),
        'fid': content.get('fid'),
    }
    for k, v in must_have.items():
        if not isinstance(k, (str, int)):
            response.append({'status': brcdapi_util.HTTP_BAD_REQUEST,
                             'reason': brcdapi_util.HTTP_REASON_MISSING_PARAM,
                             'err_msg': ['Missing ' + k, 'All processing halted'],
                             'io': False,
                             'changed': False,
                             'fail': True})
    fid = content.get('fid')  # We use the fid often, so get a local copy
    sec = 'none' if content.get('sec') is None else content.get('sec')
    if content.get('force') is not None and content.get('force'):
        f_flag = True  # Global flag initialized to False
    if content.get('test') is not None and content.get('test'):
        t_flag = True  # Global flag initialized to False
    if content.get('bulk') is not None and content.get('builk'):
        b_flag = True  # Global flag initialized to False
    if len(response) > 0:
        return response

    # Set up the project container
    proj_obj = brcddb_project.new("Captured_data", datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    proj_obj.s_python_version(sys.version)
    proj_obj.s_description('Temporary project for zoning changes')

    # Login and prime the project object (proj_obj) with basic fabric info.
    if cur_session is None:
        session = api_int.login(content.get('id'), content.get('pw'), content.get('ip-addr'), sec, proj_obj)
        if pyfos_auth.is_error(session):
            response.append(_format_api_error(session, False, False, True))
            return response
        # We'll need some basic information about the chassis, switch, fabric, and current zoning
        api_int.get_batch(session, proj_obj, [], zone_uris, fid)
        if proj_obj.r_is_api_error():
            response.append({'status': brcdapi_util.HTTP_BAD_REQUEST,
                             'reason': 'Error processing the commands in err_msg',
                             'err_msg': zone_uris,
                             'io': False,
                             'changed': False,
                             'fail': True})
            obj = brcdapi_rest.logout(session)
            if pyfos_auth.is_error(obj):
                response.append(_format_api_error(obj, False, False, True))
    else:
        session = cur_session

    # Make sure we have a switch and fabric
    switch_obj = proj_obj.r_chassis_obj(session.get('chassis_wwn')).r_switch_obj_for_fid(fid)
    if switch_obj is None:
        response.append({'status': brcdapi_util.HTTP_NOT_FOUND,
                         'reason': 'Switch matching FID ' + str(fid),
                         'err_msg': [],
                         'io': False,
                         'changed': False,
                         'fail': True})
    fab_obj = switch_obj.r_fabric_obj()
    if fab_obj is None:
        response.append({'status': brcdapi_util.HTTP_NOT_FOUND,
                         'reason': 'Fabric object for FID ' + str(fid),
                         'err_msg': [],
                         'io': False,
                         'changed': False,
                         'fail': True})
    if len(response) > 0:
        obj = brcdapi_rest.logout(session)
        if pyfos_auth.is_error(obj):
            response.append(_format_api_error(obj, False, False, True))
        return response

    # Get a checksum - we'll need this for cfgsave operation
    checksum = fab_obj.r_get('brocade-zone/effective-configuration/checksum')
    if checksum is None:
        response.append({'status': brcdapi_util.HTTP_INT_SERVER_ERROR,
                         'reason': brcdapi_util.HTTP_REASON_UNEXPECTED_RESP,
                         'err_msg': ['Missing: brocade-zone/effective-configuration/checksum'],
                         'io': False,
                         'changed': False,
                         'fail': True})
        return response

    # Process the requests
    i = 0
    tl = content.get('changes')
    fail_flag = False
    for change_req in tl:
        skip_pend_flag = False
        c_type = change_req.get('c-type')
        if c_type is not None:
            if isinstance(c_type, str) and c_type in change_type_func:
                try:
                    obj = change_type_func[c_type](session, change_req)
                    response.append(obj)
                    if not t_flag:
                        if obj['io'] and obj['changed'] and not skip_pend_flag:
                            pending.append(change_req)
                        if obj['fail']:
                            fail_flag = True
                            break
                except:
                    brcdapi_log.exception('Programming error processing ' + c_type + ', ' +
                                          str(change_req.get('operand')) + ', line ' + str(i), True)
                    response.append({'status': brcdapi_util.HTTP_INT_SERVER_ERROR,
                                     'reason': 'Unknown',
                                     'err_msg': ['Error processing: ' + str(c_type)],
                                     'io': False,
                                     'changed': False,
                                     'fail': True})
                    fail_flag = True
                    break
            else:
                response.append({'status': brcdapi_util.HTTP_NOT_FOUND,
                                 'reason': brcdapi_util.HTTP_REASON_NOT_FOUND,
                                 'err_msg': ['Unknown change request: ' + str(c_type)],
                                 'io': False,
                                 'changed': False,
                                 'fail': True})
                fail_flag = True
                break
        else:
            response.append({'status': brcdapi_util.HTTP_OK, 'io': False, 'changed': False, 'fail': False})
        i += 1

    # If bulk zoning was specified, send the updates.
    if b_flag and not t_flagand and not fail_flag:
        try:
            obj = api_zone.replace_zoning(session, fab_obj, fid)
            if pyfos_auth.is_error(obj):
                response.append(_format_return(obj))
#            else:
#                eff_zone = fab_obj.r_defined_eff_zonecfg_key()
#                if eff_zone is not None:
#                    checksum, obj = brcdapi_zone.checksum(session, fid)
#                    if pyfos_auth.is_error(obj):
#                        response.append(_format_return(obj))
#                    else:
#                        obj = brcdapi_zone.enable_zonecfg(session, checksum, fid, eff_zone)
#                        if pyfos_auth.is_error(obj):
#                            response.append(_format_return(obj))
        except:
            buf = 'Programming error in api_zone.replace_zoning()'
            brcdapi_log.exception(buf, True)
            response.append({'status': brcdapi_util.HTTP_INT_SERVER_ERROR, 'reason': buf, 'err_msg': [], 'io': False,
                             'changed': False, 'fail': True})

    # Wrap up
    if len(pending) > 0:
        response.append({'status': brcdapi_util.HTTP_PRECONDITION_REQUIRED,
                         'reason': brcdapi_util.HTTP_REASON_PENDING_UPDATES,
                         'err_msg': ['Request: ' + str(change_req.get('c-type')) + ' Operand: ' +
                                     str(change_req.get('operand')) for change_req in pending],
                         'io': False,
                         'changed': False,
                         'fail': True})
    # There is no harm in aborting a transaction when there are no pending transactions so instead of only aborting the
    # transactions when there are pending transactions, I always abort just in case there is a code bug
    obj = brcdapi_zone.abort(session, fid)
    if pyfos_auth.is_error(obj):
        response.append(_format_return(obj))

    # Log out
    if session is not None and cur_session is None:
        obj = brcdapi_rest.logout(session)
        if pyfos_auth.is_error(obj):
            brcdapi_log.log(pyfos_auth.formatted_error_msg(obj), True)

    return response
