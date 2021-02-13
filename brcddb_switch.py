# Copyright 2019, 2020, 2021 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.brcddb_switch` - Methods and tables to support the class SwitchObj.

**Note**

    The chassis types, often refered to as switch type, would make more sense in brcddb_chassis.py. The fact that they
    are in this module is due to some now irrelevant history. I wish I cleaned it up a long time ago but at thie point
    I'm limiting the amount of working code I'm changing so I left it here.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | Updated EOS matrix for Gen5 and AMP                                               |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 01 Nov 2020   | Removed all products past EOS and added Gen7 products                             |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 13 Feb 2021   | Corrected switch types for X7-4 and X7-8.                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '13 Feb 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import brcddb.util.copy as brcddb_copy
import brcddb.util.util as brcddb_util

# This is <model> in switch/fibrechannel-switch. Note that it is returned as a string (str) representing a floating
# point number. Anything after the decimal point represents a version change. Only the integer portion is useful for
# determining a switch type. Switch types used herein are the integer portion only so your code should do something
#  like:
# switch_type = int(float( <model> returned from switch/fibrechannel-switch))
class SWITCH_TYPE:
    S_FCR_Front = 40
    S_FCR_Xlate = 41
    S_6510 = 109
    S_6746 = 112
    S_6710 = 116
    S_6547 = 117
    S_6505 = 118
    S_8510_8 = 120
    S_8510_4 = 121
    S_6548 = 129
    S_6505 = 130
    S_6520 = 133
    S_7840 = 148
    S_G620 = 162
    S_X6_4 = 165
    S_X6_8 = 166
    S_6542 = 167
    S_G610 = 170
    S_G630 = 173
    S_AMP_2_0 = 171
    S_MXG610 = 175
    S_7810 = 178
    S_X7_4 = 179
    S_X7_8 = 180
    S_G720 = 181
    S_G620_2 = 183
    S_G630_2 = 184

class SWITCH_BRAND:  # The custom index in FOS. Not yet implemented in the API as of 8.2.1b
 Brocade = 0
 IBM = 1
 HPE = 2
 EMC = 3
 HDS = 4

st_name = {
    SWITCH_TYPE.S_FCR_Front: {
        SWITCH_TYPE.S_FCR_Front: {
        SWITCH_BRAND.Brocade: 'FCR Front Domain',
        SWITCH_BRAND.IBM: 'SWITCH_BRAND.IBM',
        SWITCH_BRAND.HPE: 'FCR Front Domain',
        SWITCH_BRAND.EMC: 'FCR Front Domain',
        SWITCH_BRAND.HDS: 'FCR Front Domain'}
    },
    SWITCH_TYPE.S_FCR_Xlate: {
        SWITCH_BRAND.Brocade: 'FCR Xlate Domain',
        SWITCH_BRAND.IBM: '',
        SWITCH_BRAND.HPE: 'FCR Xlate Domain',
        SWITCH_BRAND.EMC: 'FCR Xlate Domain',
        SWITCH_BRAND.HDS: 'FCR Xlate Domain'},
    SWITCH_TYPE.S_6510: {
        SWITCH_BRAND.Brocade: '6510',
        SWITCH_BRAND.IBM: 'SAN48B-5',
        SWITCH_BRAND.HPE: 'SN6000B',
        SWITCH_BRAND.EMC: 'DS-6510B',
        SWITCH_BRAND.HDS: '6510'},
    SWITCH_TYPE.S_6505: {
        SWITCH_BRAND.Brocade: '6505',
        SWITCH_BRAND.IBM: 'SAN24B-5',
        SWITCH_BRAND.HPE: '6505',
        SWITCH_BRAND.EMC: 'DS-6505B',
        SWITCH_BRAND.HDS: '6505'},
    SWITCH_TYPE.S_8510_8: {
        SWITCH_BRAND.Brocade: 'DCX8510-8',
        SWITCH_BRAND.IBM: 'SAN768B-2',
        SWITCH_BRAND.HPE: 'SN8000B 8-slot',
        SWITCH_BRAND.EMC: 'ED-DCX8510-8B',
        SWITCH_BRAND.HDS: 'DCX8510-8'},
    SWITCH_TYPE.S_8510_4: {
        SWITCH_BRAND.Brocade: 'DCX8510-4',
        SWITCH_BRAND.IBM: 'SAN384B-2',
        SWITCH_BRAND.HPE: 'SN8000B 4-slot',
        SWITCH_BRAND.EMC: '1ED-DCX8510-4B000',
        SWITCH_BRAND.HDS: 'DCX8510-4'},
    SWITCH_TYPE.S_6548: {
        SWITCH_BRAND.Brocade: '6548',
        SWITCH_BRAND.IBM: '',
        SWITCH_BRAND.HPE: '16Gb SAN switch for HP BladeSystem',
        SWITCH_BRAND.EMC: '6548',
        SWITCH_BRAND.HDS: '6548'},
    SWITCH_TYPE.S_6520: {
        SWITCH_BRAND.Brocade: '6520',
        SWITCH_BRAND.IBM: 'SAN96B-5',
        SWITCH_BRAND.HPE: 'SN6500B',
        SWITCH_BRAND.EMC: 'DS-6520B',
        SWITCH_BRAND.HDS: '6520'},
    SWITCH_TYPE.S_7840: {
        SWITCH_BRAND.Brocade: '7840',
        SWITCH_BRAND.IBM: 'SAN42B-R',
        SWITCH_BRAND.HPE: '7840',
        SWITCH_BRAND.EMC: 'MP-7840B',
        SWITCH_BRAND.HDS: '7840'},
    SWITCH_TYPE.S_6542: {
        SWITCH_BRAND.Brocade: 'Blade_6542',
        SWITCH_BRAND.IBM: 'Blade_6542',
        SWITCH_BRAND.HPE: 'Blade_6542',
        SWITCH_BRAND.EMC: 'Blade_6542'
        ,SWITCH_BRAND.HDS: 'Blade_6542'},
    SWITCH_TYPE.S_G610: {
        SWITCH_BRAND.Brocade: 'G610',
        SWITCH_BRAND.IBM: 'SAN24B-6',
        SWITCH_BRAND.HPE: 'SN3600B',
        SWITCH_BRAND.EMC: 'DS-6610B'
        ,SWITCH_BRAND.HDS: 'G610'},
    SWITCH_TYPE.S_MXG610: {
        SWITCH_BRAND.Brocade: 'MXG610',
        SWITCH_BRAND.IBM: 'MXG610',
        SWITCH_BRAND.HPE: 'MXG610',
        SWITCH_BRAND.EMC: 'MXG610'
        ,SWITCH_BRAND.HDS: 'MXG610'},
    SWITCH_TYPE.S_G620: {
        SWITCH_BRAND.Brocade: 'G620',
        SWITCH_BRAND.IBM: 'SAN64B-6',
        SWITCH_BRAND.HPE: 'SN6600B',
        SWITCH_BRAND.EMC: 'DS-6620B',
        SWITCH_BRAND.HDS: 'G620'},
    SWITCH_TYPE.S_G620_2: {
        SWITCH_BRAND.Brocade: 'G620_C5',
        SWITCH_BRAND.IBM: 'SAN64B-6',
        SWITCH_BRAND.HPE: 'SN6600B',
        SWITCH_BRAND.EMC: 'DS-6620B',
        SWITCH_BRAND.HDS: 'G620'},
    SWITCH_TYPE.S_G630: {
        SWITCH_BRAND.Brocade: 'G630',
        SWITCH_BRAND.IBM: 'SAN96B-6',
        SWITCH_BRAND.HPE: 'SN6650B',
        SWITCH_BRAND.EMC: 'DS-6630B',
        SWITCH_BRAND.HDS: 'G630'},
    SWITCH_TYPE.S_G630_2: {
        SWITCH_BRAND.Brocade: 'G630_C5',
        SWITCH_BRAND.IBM: 'SAN96B-6',
        SWITCH_BRAND.HPE: 'SN6650B',
        SWITCH_BRAND.EMC: 'DS-6630B',
        SWITCH_BRAND.HDS: 'G630'},
    SWITCH_TYPE.S_X6_8: {
        SWITCH_BRAND.Brocade: 'X6-8',
        SWITCH_BRAND.IBM: 'SAN512B-6',
        SWITCH_BRAND.HPE: 'SN8600B 8-Slot',
        SWITCH_BRAND.EMC: 'ED-DCX6-8B',
        SWITCH_BRAND.HDS: 'X6-8'},
    SWITCH_TYPE.S_X6_4: {
        SWITCH_BRAND.Brocade: 'X6-4',
        SWITCH_BRAND.IBM: 'SAN256B-6',
        SWITCH_BRAND.HPE: 'SN8600B 4-Slot',
        SWITCH_BRAND.EMC: 'ED-DCX6-4B',
        SWITCH_BRAND.HDS: 'X6-4'},
    SWITCH_TYPE.S_AMP_2_0: {
        SWITCH_BRAND.Brocade: 'AMP_2_0',
        SWITCH_BRAND.IBM: '',
        SWITCH_BRAND.HPE: '',
        SWITCH_BRAND.EMC: '',
        SWITCH_BRAND.HDS: ''},
    SWITCH_TYPE.S_7810: {
        SWITCH_BRAND.Brocade: '7810',
        SWITCH_BRAND.IBM: 'Unknwon',
        SWITCH_BRAND.HPE: '7810',
        SWITCH_BRAND.EMC: 'MP-7810B',
        SWITCH_BRAND.HDS: '7810'},
    SWITCH_TYPE.S_G720: {
        SWITCH_BRAND.Brocade: 'G720',
        SWITCH_BRAND.IBM: 'SAN64B-7',
        SWITCH_BRAND.HPE: 'G720',
        SWITCH_BRAND.EMC: 'DS-7720B',
        SWITCH_BRAND.HDS: 'HD-G720'},
    SWITCH_TYPE.S_X7_4: {
        SWITCH_BRAND.Brocade: 'X7-4',
        SWITCH_BRAND.IBM: 'SAN512B-7',
        SWITCH_BRAND.HPE: 'X7-4',
        SWITCH_BRAND.EMC: 'ED-DCX7-4B',
        SWITCH_BRAND.HDS: 'HD-X74-0002'},
    SWITCH_TYPE.S_X7_8: {
        SWITCH_BRAND.Brocade: 'X7-8',
        SWITCH_BRAND.IBM: 'SAN256B-7',
        SWITCH_BRAND.HPE: 'X7-8',
        SWITCH_BRAND.EMC: 'ED-DCX7-8B',
        SWITCH_BRAND.HDS: 'HD-X78-0002'},
}

st_type = {
    SWITCH_TYPE.S_6510: '2498-F48',
    SWITCH_TYPE.S_6505: '2498-F24',
    SWITCH_TYPE.S_8510_8: '2499-816',
    SWITCH_TYPE.S_8510_4: '2499-416',
    SWITCH_TYPE.S_6520: '2498-F96 / N96',
    SWITCH_TYPE.S_7840: '2498-R42',
    SWITCH_TYPE.S_G610: '8960-F24/N24',
    SWITCH_TYPE.S_G620: '8960-F64/N64',
    SWITCH_TYPE.S_G620_2: '8960-F65/8960-N65',
    SWITCH_TYPE.S_G630: '8960-F128/N128',
    SWITCH_TYPE.S_G630_2: '8960-F97/8960-N97',
    SWITCH_TYPE.S_X6_8: '8961-F08',
    SWITCH_TYPE.S_X6_4: '8961-F04',
    SWITCH_TYPE.S_G720: '8960-P64/R64',
    SWITCH_TYPE.S_X7_4: '8961-F04',
    SWITCH_TYPE.S_X7_8: '8961-F08',
}

st_speed = {
    SWITCH_TYPE.S_6510: 16,
    SWITCH_TYPE.S_6547: 16,
    SWITCH_TYPE.S_6505: 16,
    SWITCH_TYPE.S_8510_8: 16,
    SWITCH_TYPE.S_8510_4: 16,
    SWITCH_TYPE.S_6548: 16,
    SWITCH_TYPE.S_6505: 16,
    SWITCH_TYPE.S_6520: 16,
    SWITCH_TYPE.S_7840: 16,
    SWITCH_TYPE.S_G610: 32,
    SWITCH_TYPE.S_MXG610: 32,
    SWITCH_TYPE.S_G620: 32,
    SWITCH_TYPE.S_G620_2: 32,
    SWITCH_TYPE.S_G630: 32,
    SWITCH_TYPE.S_G630_2: 32,
    SWITCH_TYPE.S_X6_8: 32,
    SWITCH_TYPE.S_X6_4: 32,
    SWITCH_TYPE.S_7810: 32,
    SWITCH_TYPE.S_AMP_2_0: 32,
    SWITCH_TYPE.S_G720: 64,
    SWITCH_TYPE.S_X7_8: 64,
    SWITCH_TYPE.S_X7_4: 64,
}

st_sys_z = {
    SWITCH_TYPE.S_6510: True,
    SWITCH_TYPE.S_6547: False,
    SWITCH_TYPE.S_8510_8: True,
    SWITCH_TYPE.S_8510_4: True,
    SWITCH_TYPE.S_6520: False,
    SWITCH_TYPE.S_7840: True,
    SWITCH_TYPE.S_G610: False,
    SWITCH_TYPE.S_G620: True,
    SWITCH_TYPE.S_G620_2: True,
    SWITCH_TYPE.S_G630: False,
    SWITCH_TYPE.S_G630_2: False,
    SWITCH_TYPE.S_X6_8: True,
    SWITCH_TYPE.S_X6_4: True,
    SWITCH_TYPE.S_AMP_2_0: True,
    SWITCH_TYPE.S_7810: False,
    SWITCH_TYPE.S_G720: True,
    SWITCH_TYPE.S_X7_8: True,
    SWITCH_TYPE.S_X7_4: True,
}

st_slots = {
    SWITCH_TYPE.S_6510: 0,
    SWITCH_TYPE.S_6710: 0,
    SWITCH_TYPE.S_6547: 0,
    SWITCH_TYPE.S_6505: 0,
    SWITCH_TYPE.S_8510_8: 8,
    SWITCH_TYPE.S_8510_4: 4,
    SWITCH_TYPE.S_6548: 0,
    SWITCH_TYPE.S_6505: 0,
    SWITCH_TYPE.S_6520: 0,
    SWITCH_TYPE.S_7840: 0,
    SWITCH_TYPE.S_G610: 0,
    SWITCH_TYPE.S_MXG610: 0,
    SWITCH_TYPE.S_G620: 0,
    SWITCH_TYPE.S_G620_2: 0,
    SWITCH_TYPE.S_G630: 0,
    SWITCH_TYPE.S_G630_2: 0,
    SWITCH_TYPE.S_X6_8: 8,
    SWITCH_TYPE.S_X6_4: 4,
    SWITCH_TYPE.S_AMP_2_0: 0,
    SWITCH_TYPE.S_7810: 0,
    SWITCH_TYPE.S_G720: 0,
    SWITCH_TYPE.S_X7_8: 8,
    SWITCH_TYPE.S_X7_4: 4,
}

st_gen = {
    SWITCH_TYPE.S_6510: 'Gen5',
    SWITCH_TYPE.S_6547: 'Gen5',
    SWITCH_TYPE.S_6505: 'Gen5',
    SWITCH_TYPE.S_8510_8: 'Gen5',
    SWITCH_TYPE.S_8510_4: 'Gen5',
    SWITCH_TYPE.S_6520: 'Gen5',
    SWITCH_TYPE.S_7840: 'Gen5',
    SWITCH_TYPE.S_G610: 'Gen6',
    SWITCH_TYPE.S_MXG610: 'Gen6',
    SWITCH_TYPE.S_G620: 'Gen6',
    SWITCH_TYPE.S_G620_2: 'Gen6',
    SWITCH_TYPE.S_G630: 'Gen6',
    SWITCH_TYPE.S_G630_2: 'Gen6',
    SWITCH_TYPE.S_X6_4: 'Gen6',
    SWITCH_TYPE.S_X6_8: 'Gen6',
    SWITCH_TYPE.S_AMP_2_0: 'Gen6',
    SWITCH_TYPE.S_7810: 'Gen6',
    SWITCH_TYPE.S_G720: 'Gen7',
    SWITCH_TYPE.S_X7_4: 'Gen7',
    SWITCH_TYPE.S_X7_8: 'Gen7',
}

st_eos = {  # EOS date format is yyyy/mm/dd
    SWITCH_TYPE.S_FCR_Front: 'Current',
    SWITCH_TYPE.S_FCR_Xlate: 'Current',
    SWITCH_TYPE.S_6510: '2025/04/30',
    SWITCH_TYPE.S_6746: 'Current',
    SWITCH_TYPE.S_6505: '2025/04/30',
    SWITCH_TYPE.S_8510_8: '2025/04/30',
    SWITCH_TYPE.S_8510_4: '2025/04/30',
    SWITCH_TYPE.S_6548: 'Current',
    SWITCH_TYPE.S_6505: 'Current',
    SWITCH_TYPE.S_6520: 'Current',
    SWITCH_TYPE.S_7840: 'Current',
    SWITCH_TYPE.S_G610: 'Current',
    SWITCH_TYPE.S_MXG610: 'Current',
    SWITCH_TYPE.S_G620: 'Current',
    SWITCH_TYPE.S_G620_2: 'Current',
    SWITCH_TYPE.S_G630: 'Current',
    SWITCH_TYPE.S_G630_2: 'Current',
    SWITCH_TYPE.S_X6_8: 'Current',
    SWITCH_TYPE.S_X6_4: 'Current',
    SWITCH_TYPE.S_AMP_2_0: '2024/10/31',
    SWITCH_TYPE.S_7810: 'Current',
    SWITCH_TYPE.S_G720: 'Current',
    SWITCH_TYPE.S_X7_8: 'Current',
    SWITCH_TYPE.S_X7_4: 'Current',
}

area_mode = {
    0: ' 10-bit addressing mode',
    1: ' Zero-based area assignment',
    2: ' Port-based area assignment',
}


def eos(switch):
    """Returns the End of Support (EOS) date

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: EOS_date
    :rtype: str
    """
    try:
        return st_eos[int(float(switch))]
    except:
        return ''


def gen(switch):
    """Returns the gen type

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Generation
    :rtype: str
    """
    try:
        return st_gen[int(float(switch))]
    except:
        return ''


def slots(switch):
    """Returns the number of slots for the switch

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Num slots
    :rtype: int
    """
    try:
        return st_slots[int(float(switch))]
    except:
        return 0


def ibm_machine_type(switch):
    """Returns the IBM machine type for the switch

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: machine_type
    :rtype: str
    """
    try:
        return st_type[int(float(switch))]
    except:
        return ''


def sys_z_supported(switch):
    """Returns True if z systems supported

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: True if z Systems supported
    :rtype: bool
    """
    try:
        return st_sys_z[int(float(switch))]
    except:
        return False


def switch_speed(switch):
    """Converts the switch type number to the max speed the switch is capable of

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Maximum speed switch is capable of
    :rtype: int
    """
    try:
        return st_speed[int(float(switch))]
    except:
        return 0


def model_oem(switch, oem):
    """Returns the OEM branded switch model type.

    Note: As of FOS 8.2.1b, the custom-index was not yet available
    :param switch: fibrechannel-switch/model
    :type switch: float, int, str
    :param oem: Custom index - I'm assuming this will be 'custom-index' in fibrechannel-switch
    :return: OEM branded witch model
    :rtype: str
    """
    global st_name

    try:
        return st_name[int(switch)][oem]
    except:
        return 'Unknown'


def model_broadcom(switch):
    """Returns the Broadcom  branded switch model type

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Switch model
    :rtype: str
    """
    return model_oem(switch, SWITCH_BRAND.Brocade)


def add_rest_port_data(switch_obj, pobj, flag_obj=None, skip_list=list()):
    """Adds port statistics from rest request 'brocade-interface/fibrechannel-statistics' to each port object

    :param switch_obj: Switch object
    :type switch_obj: SwitchObj
    :param pobj: Object returned from the FOS Rest API
    :type pobj: dict
    :param flag_obj: Not used. Must be here for methods that call rest add methods from a table.
    :type flag_obj: None
    :param skip_list: Keys to skip
    :type skip_list: (list, tuple)
    :return: None
    :rtype: None
    """
    sl = ['name', 'enabled-state']
    sl.extend(skip_list)
    for k in pobj.keys():
        for pdict in brcddb_util.convert_to_list(pobj.get(k)):
            if k == 'media-rdp':
                # The media name is in the format type/s/p, but for everything else, it's just s/p, which is how the key
                # is created for the port object in the switch object. By splitting on '/', removing the first list
                # element, and joining the rest with '/', I end up with just s/p.
                port_obj = switch_obj.s_add_port('/'.join(pdict.get('name').split('/')[1:]))
            else:
                port_obj = switch_obj.s_add_port(pdict.get('name'))
            v = dict()
            port_obj.s_new_key(k, v)
            brcddb_copy.object_copy(pdict, v, port_obj, sl)
            # Make sure there is a login object for every login found
            fab_obj = switch_obj.r_fabric_obj()
            if fab_obj is not None:
                for wwn in port_obj.r_login_keys():
                    fab_obj.s_add_login(wwn)


def best_switch_name(switch_obj, wwn=False):
    """Returns the user friendly switch name, optionally with the switch WWN in parenthesis. If the swith is not named,
        just the switch WWN is returned

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :param wwn: If True, append (wwn) to the switch name
    :type wwn: bool
    :return: Switch name
    :rtype: str, None
    """
    if switch_obj is None:
        return 'Unknown'
    buf = switch_obj.r_get('brocade-fibrechannel-switch/fibrechannel-switch/user-friendly-name')
    if buf is None:
        buf = switch_obj.r_get('brocade-fabric/fabric-switch/switch-user-friendly-name')
    if buf is None or len(buf) == 0:
        return switch_obj.r_obj_key()
    return buf + ' (' + switch_obj.r_obj_key() + ')' if wwn else buf


def switch_type(switch_obj):
    """Returns the switch type: Default, FICON, Base, FCP

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Switch type
    :rtype: str
    """
    if switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/default-switch-status'):
        return 'Default'
    if switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/ficon-mode-enabled'):
        return 'FICON'
    if switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/base-switch-enabled'):
        return 'Base'
    return 'FCP'


def switch_fid(switch_obj):
    """Returns the switch FID

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: Switch FID. Returns None if non-VF or logical switch data not yet captured
    :rtype: int, None
    """
    return switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/fabric-id')


def switch_ports(switch_obj):
    """Returns the list of ports in the switch

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: List of ports in switch. Empty if no ports but None if not polled
    :rtype: list, None
    """
    return switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/port-member-list')


def switch_ge_ports(switch_obj):
    """Returns the list of GE ports in the switch

    :param switch_obj: Switch object
    :type switch_obj: brcddb.classes.switch.SwitchObj
    :return: List of GE ports in switch. Empty if no ports but None if not polled
    :rtype: list, None
    """
    return switch_obj.r_get('brocade-fibrechannel-logical-switch/fibrechannel-logical-switch/ge-port-member-list')
