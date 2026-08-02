"""
Copyright 2023, 2024, 2025, 2026 Jack Consoli.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack_consoli@yahoo.com for
details.

**Description**

Methods and tables to support the class ChassisObj.

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| best_chassis_name     | Returns the chassis name, if available. Otherwise, the WWN for the chassis                |
+-----------------------+-------------------------------------------------------------------------------------------+
| gen                   | Returns the generation level as an int.                                                   |
+-----------------------+-------------------------------------------------------------------------------------------+
| firmware_version      | Returns the firmware version as text.                                                     |
+-----------------------+-------------------------------------------------------------------------------------------+
| static_mgmt_addr      | Returns the static management IP address, subnet mask, and gateway.                       |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Added FC64-48 to blade_id_name                                                        |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 26 Jun 2024   | Added firmware_version()                                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 20 Oct 2024   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 06 Dec 2024   | Fixed configuration types for X7-4 and X7-8                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 26 Dec 2024   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 12 Apr 2025   | FOS 9.2 updates.                                                                      |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.7     | 25 Aug 2025   | Added static_mgmt_addr()                                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.8     | 19 Oct 2025   | Updated comments only.                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.9     | 20 Feb 2026   | Updated copyright notice.                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.1.0     | 01 Aug 2026   | Removed obsolete functions.                                                            |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2024, 2025, 2026 Jack Consoli'
__date__ = '01 Aug 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.1.0'

import time
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util


class Found(Exception):
    pass


def best_chassis_name(chassis_obj, wwn=False):
    """Returns the chassis name, if available. Otherwise, the WWN for the chassis

    :param chassis_obj: Chassis Object
    :type chassis_obj: brcddb_classes.chassis.ChassisObj
    :param wwn: If True, append (wwn) to the chassis name
    :type wwn: bool
    :return: Chassis name
    :rtype: str
    """
    if chassis_obj is None:
        return 'Unknown'
    buf = chassis_obj.r_get(brcdapi_util.bc_user_name)
    return chassis_obj.r_obj_key() if buf is None else buf + ' (' + chassis_obj.r_obj_key() + ')' if wwn else buf


def firmware_version(obj):
    """Returns the firmware version as text.

    :param obj: Any object that contains a chassis object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj, brcddb.class.port.PortObj
    :return: Firmware version as plain text.
    :rtype: str
    """
    # FOS 9.2 and above
    firmware = obj.r_chassis_obj().r_get(brcdapi_util.bc_version_fos)
    if isinstance(firmware, str):
        kernal = obj.r_chassis_obj().r_get(brcdapi_util.bc_version_kernal, 'Unknown')
        return firmware + ' (Kernal: ' + kernal + ')'

    # Pre-FOS 9.2
    firmware_l = obj.r_chassis_obj().r_get('brocade-firmware/firmware-history')
    try:
        return firmware_l[len(firmware_l)-1]['firmware-version'].replace('Fabos Version ', '')
    except (IndexError, TypeError, KeyError):
        pass

    # Pre-FOS before firmware-history was added
    return obj.r_chassis_obj().r_get('brocade-fru/blade/firmware-version', 'Unknown')


def static_mgmt_addr(obj, default_ip=None, default_subnet_mask=None, default_gateway=None):
    """Returns the static management IP address, subnet mask, and gateway.

    $ToDo - Fishout the gateway.

    :param obj: Any object that returns a chassis object: Chassis, switch, port, or login object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :param default_ip: The value to return if the management IP address cannot be found
    :type default_ip: str, None
    :param default_subnet_mask: The value to return if the management subnet mask cannot be found
    :type default_subnet_mask: str, None
    :param default_gateway: The value to return if the gateway address cannot be found
    :type default_gateway: str, None
    :return ip_addr: Management IP address
    :rtype ip_addr: str, None
    :return subnet_mask: Subnet mask
    :rtype subnet_mask: str, None
    :return gateway: The gateway address
    """
    ip_d = dict()
    try:
        chassis_obj = obj.r_chassis_obj()
        for ip_d in chassis_obj.r_get('brocade-chassis/management-ethernet-interface', list()):
            for flag in ip_d['ethernet-status-flags']['flag']:
                if flag == 'master':
                    raise Found
    except TypeError:
        brcdapi_log.exception('Invalid object parameter: ')
    except (TypeError, KeyError, Found):
        # A TypeError occurs when the chassis_obj couldn't be resolved.
        pass

    return ip_d.get('inet-address', default_ip), ip_d.get('subnet-mask', default_subnet_mask), default_gateway


def gen(obj):
    """Returns the generation level as an int.

    :param obj: Any object that contains a chassis object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj, brcddb.class.port.PortObj
    :return: Generation level. 0 if unknown
    :rtype: int
    """
    product_name = obj.r_chassis_obj().r_get(brcdapi_util.bc_product_name)
    if product_name is None:
        return 0
    product_name = product_name.lower()  # It should be lower, but just to be sure.
    if 'g6' or 'x6' in product_name:
        return 6
    if 'g7' or 'x7' in product_name:
        return 7
    if 'g8' or 'x8' in product_name:
        return 8
    if 'g9' or 'x9' in product_name:  # Future proofing
        return 9
    return 5  # The only other generation that supported the API was gen 5

