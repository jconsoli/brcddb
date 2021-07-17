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
    | 3.0.5     | 17 Jul 2021   | Referenced brcddb_chassis for all chassis specific stuff.                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '17 Jul 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.5'

import brcddb.util.copy as brcddb_copy
import brcddb.util.util as brcddb_util
import brcddb.brcddb_chassis as brcddb_chassis  # To support deprecated methods
import time

area_mode = {
    0: ' 10-bit addressing mode',
    1: ' Zero-based area assignment',
    2: ' Port-based area assignment',
}


def _chassis_d(switch):
    """Returns the dictionary associated with this switch number from brcddb_chassis.chassis_type_d

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Chassis dicrionary
    :rtype: dict
    """
    d = brcddb_chassis.chassis_type_d.get(int(float(switch)))
    return brcddb_chassis.chassis_type_d[0] if d is None else d



def eos(switch):
    """Deprecated. Use brcddb.brcddb_chassis.eos()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: EOS_date
    :rtype: str
    """
    d = _chassis_d(switch)
    return 'EOS not announced' if d['eos'] is None else time.strftime('%Y-%m-%d', d['eos'])


def gen(switch):
    """Deprecated. Use brcddb.brcddb_chassis.gen()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Generation
    :rtype: str
    """
    return _chassis_d(switch)['gen']


def slots(switch):
    """Deprecated. Use brcddb.brcddb_chassis.slots()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Num slots
    :rtype: int
    """
    cfg = _chassis_d(switch)['cfg']
    return 4 if cfg == brcddb_chassis.cfg_4_slot else 8 if cfg == brcddb_chassis.cfg_8_slot else 0


def ibm_machine_type(switch):
    """Deprecated. Use brcddb.brcddb_chassis.ibm_machine_type()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: machine_type
    :rtype: str
    """
    return _chassis_d(switch)['ibm_t']


def sys_z_supported(switch):
    """Deprecated. Use brcddb.brcddb_chassis.sys_z_supported()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: True if z Systems supported
    :rtype: bool
    """
    return _chassis_d(switch)['z']


def switch_speed(switch):
    """Deprecated. Use brcddb.brcddb_chassis.chassis_speed()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Maximum speed switch is capable of
    :rtype: int
    """
    return _chassis_d(switch)['spd']


def model_broadcom(switch):
    """Deprecated. Use brcddb.brcddb_chassis.chassis_type()

    :param switch: fibrechannel-switch/model
    :type switch: str
    :return: Switch model
    :rtype: str
    """
    return _chassis_d(switch)['brcd']


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
