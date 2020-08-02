#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcddb_chassis` - Methods and tables to support the class ChassisObj.

Primary Methods::

    +-----------------------------+----------------------------------------------------------------------------------+
    | Method                      | Description                                                                      |
    +=============================+==================================================================================+
    | blade_name()                | Converts the brocade-fru/blade/blade-id number to a user freindly blade type     |
    +-----------------------------+----------------------------------------------------------------------------------+
    | best_chassis_name()         | Returns the chassis name, if available. Otherwise, the WWN for the chassis       |
    +-----------------------------+----------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
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

import brcddb.brcddb_switch as brcddb_switch

_MIN_SYMB_LEN = 10

blade_id_name = {
    1: 'CP1',
    2: 'FC_16',
    4: 'FC2-16',
    5: 'CP2',
    16: 'CP4',
    17: 'FC4-16',
    18: 'FC4-32',
    24: 'FR4-18i',
    31: 'FC4-16IP',
    33: 'FA4-18',
    36: 'FC4-48',
    37: 'FC8-16',
    39: 'FC10-6',
    43: 'FS8-18',
    46: 'CR4S-8',
    50: 'CP8',
    51: 'FC8-48',
    52: 'Core8',
    55: 'FC8-32',
    74: 'FCOE10-24',
    75: 'FX8-24',
    77: 'FC8-64',
    96: 'FC16-48',
    97: 'FC16-32',
    98: 'CR16-8',
    99: 'CR16-4',
    125: 'FC8-32E',
    126: 'FC8-48E',
    153: 'FC16-64',
    154: '7840',
    171: 'G620',
    175: 'CPX6',
    177: 'CR32-8',
    176: 'CR32-4',
    178: 'FC32-48',
    186: 'SX6',
    202: 'G630',
    204: 'FC32-64',
}


def blade_name(blade_id):
    """Converts the brocade-fru/blade/blade-id number to a user freindly blade type

    :param blade_id: brocade-fru/blade/blade-id
    :type blade_id: int
    :return: Human readable blade ID
    :rtype: str
    """
    return blade_id_name[blade_id] if blade_id in blade_id_name else 'Unknown'


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
    buf = chassis_obj.r_get('brocade-chassis/chassis/chassis-user-friendly-name')
    if buf is None:
        return chassis_obj.r_obj_key()
    return buf + ' (' + chassis_obj.r_obj_key() + ')' if wwn else buf


def chassis_type(chassis_obj, type_num=False):
    """Returns the chassis type, if available. Otherwise ''

    :param chassis_obj: Chassis Object
    :type chassis_obj: brcddb_classes.chassis.ChassisObj
    :param type_num: If True, append (type number) to the chassis name
    :type type_num: bool
    :return: Chassis type
    :rtype: str
    """
    for switch_obj in chassis_obj.r_switch_objects():  # Chassis type is embedded with the switch data
        switch_type = switch_obj.c_switch_model()
        if switch_type > 0:
            buf = brcddb_switch.model_broadcom(switch_type)
            return buf + ' (' + str(switch_type) + ')' if type_num else buf
    return ''
