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

Parses CLI output.

**Public Methods & Data**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| cfgshow               | Parse cfgshow output                                                                      |
+-----------------------+-------------------------------------------------------------------------------------------+
| chassisshow           | Adds a chassis object to a project object from chassisshow output                         |
+-----------------------+-------------------------------------------------------------------------------------------+
| defzone               | Parse defzone output                                                                      |
+-----------------------+-------------------------------------------------------------------------------------------+
| fabricshow            | Adds a fabric object to a project object from fabricshow output                           |
+-----------------------+-------------------------------------------------------------------------------------------+
| ficonshow             | Parse ficonshow output                                                                    |
+-----------------------+-------------------------------------------------------------------------------------------+
| nsshow                | Parse nsshow outpu                                                                        |
+-----------------------+-------------------------------------------------------------------------------------------+
| portbuffershow        | Adds the portbuffershow output to the ports in a switch object                            |
+-----------------------+-------------------------------------------------------------------------------------------+
| portcfgshow           | Adds the portcfgshow output to the ports in a switch object                               |
+-----------------------+-------------------------------------------------------------------------------------------+
| portstatsshow         | Parse portstatsshow and add to the port objects                                           |
+-----------------------+-------------------------------------------------------------------------------------------+
| portstats64show       | Parse portstats64show and add to the port objects                                         |
+-----------------------+-------------------------------------------------------------------------------------------+
| sfpshow               | Parse sfpshow output                                                                      |
+-----------------------+-------------------------------------------------------------------------------------------+
| slotshow_d576         | Parse slotshow_d576 output                                                                |
+-----------------------+-------------------------------------------------------------------------------------------+
| switchshow            | Adds a switch object to a project object from switchshow output                           |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Fixed address mode. Added portcfgshow()                                               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 03 Apr 2024   | Fixed missed FID change in sfpshow. Fixed missing NPIV logins in nsshow()             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 15 May 2024   | Fixed missed effective zone configuration.                                            |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.4     | 20 Oct 2024   | Typos in error messages.                                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.5     | 06 Dec 2024   | Added portname_range()                                                                |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.6     | 26 Dec 2024   | Fixed error when switchshow output is empty or missing.                               |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.7     | 25 Aug 2025   | Updated email address in __email__ only.                                              |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.8     | 19 Oct 2025   | In cfgshow output, newer versions of FOS do not have a space between the ':' after a  |
|           |               | key word and the operand. Fixed this by stuffing a space after ':'.                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.9     | 20 Feb 2026   | Changed from fibrechannel/port-type to fibrechannel/port-type-string                  |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025, 2026 Jack Consoli'
__date__ = '20 Feb 2026'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.9'

import re
import time
import collections
import copy
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcddb.brcddb_common as brcddb_common
import brcddb.util.util as brcddb_util
import brcddb.brcddb_port as brcddb_port
import brcddb.classes.util as brcddb_class_util


def _conv_to_int(buf):
    """
    :param buf: Value to convert to an integer
    :type buf: str
    :return: None if non-integer, otherwise the value in buf converted to an integer
    :rtype: None, int
    """
    return int(buf) if buf.isnumeric() else None


def _conv_to_lower(buf):
    """
    :param buf: Value to convert to lower case
    :type buf: str
    :return: Value as passed if buf is not a string. Otherwise, buf is converted to lower case
    :rtype: str
    """
    return buf.lower() if isinstance(buf, str) else buf


_switchshow_tbl = {
    'switchName': brcdapi_util.bfs_sw_user_name,
    'switchType': brcdapi_util.bfs_model,
    'switchDomain': brcdapi_util.bfs_did,
    'switchId': brcdapi_util.bfs_fcid_hex,
    'switchWwn': brcdapi_util.bfs_name,
    'Fabric Name': brcdapi_util.bfs_fab_user_name,
}
_switch_0_1_boolean_off_on = {
    # 'Base Switch': brcdapi_util.bfls_base_sw_en,
    # 'Default Switch': brcdapi_util.bfls_def_sw_status,
    # 'Ficon Switch': brcdapi_util.bfls_ficon_mode_en,
}
_switch_0_1_boolean_yes_no = {
    'HIF Mode': brcdapi_util.bfls_ficon_mode_en,
    'Base Switch': brcdapi_util.bfls_base_sw_en,
    'Default Switch': brcdapi_util.bfls_def_sw_status,
    'Ficon Switch': brcdapi_util.bfls_ficon_mode_en,
}
_switch_attributes_T_F = {
    'Allow XISL Use': brcdapi_util.bfc_xisl_en,
}
_physical_port_state = {
    'No_Light': 'no_light',
    'No_Module': 'no_module',
    'Mod_Val': 'mod_val',
    'Mod_Inv': 'mod_inv',
    'Mod_Uns': 'no_port',
    'No_SigDet': 'no_sigdet',
    'No_Sync': 'no_sync',
    'In_Sync': 'in_sync',
    'Laser_Flt': 'laser_flt',
    'Port_Flt': 'port_flt',
    'Hard_Flt': 'hard_flt',
    'Lock_Ref': 'lock_ref',
    'Testing': 'testing',
    'Offline': 'offline',
    'Online': 'online',
    'Transient': 'unknown'
}
_skip_in_switch = ('port-member-list', 'ge-port-member-list', 'fibrechannel', 'media-rdp', '_neighbor', 'rnid')

# Port conversion tables. Used in portstats64show().
_portstats_to_api = {
    # 'xxx': 'address-errors', In portcamshow
    'er64_bad_eof': 'bad-eofs-received',
    'er_bad_eof': 'bad-eofs-received',
    'tim64_txcrd_z': 'bb-credit-zero',
    'tim_txcrd_z': 'bb-credit-zero',
    # 'xxx': 'class-1-frames',
    'stat64_c2_frx': 'class-2-frames',
    'stat_c2_frx': 'class-2-frames',
    'er64_disc_c3': 'class-3-discards',
    'er_disc_c3': 'class-3-discards',
    'er64_tx_c3_timeout': 'class3-out-discards',
    'er_tx_c3_timeout': 'class3-out-discards',
    'stat64_c3_frx': 'class-3-frames',
    'stat_c3_frx': 'class-3-frames',
    'er64_rx_c3_timeout': 'class3-in-discards',
    'er_rx_c3_timeout': 'class3-in-discards',
    'er64_crc': 'crc-errors',
    'er_crc': 'crc-errors',
    # 'xxx': 'delimiter-errors', In portcamshow
    # 'xxx': 'encoding-disparity-errors', In portcamshow
    'er64_enc_out': 'encoding-errors-outside-frame',
    'er_enc_out': 'encoding-errors-outside-frame',
    # 'xxx': 'f-busy-frames',
    # 'xxx': 'f-rjt-frames',
    # 'xxx': 'frames-processing-required', In portcamshow
    # 'xxx': 'frames-timed-out',
    'er64_toolong': 'frames-too-long',
    'er_toolong': 'frames-too-long',
    # 'xxx': 'frames-transmitter-unavailable-errors', In portcamshow
    'Invalid_CRC': 'in-crc-errors',
    'er_crc_good_eof': 'in-crc-errors',
    'stat64_rateRxFrame': 'in-frame-rate',
    'stat64_frx': 'in-frames',
    'stat_frx': 'in-frames',
    'stat64_lc_rx': 'in-lcs',
    'stat_lc_rx': 'in-lcs',
    'Lr_in': 'in-link-resets',
    # 'xxx': 'in-max-frame-rate',
    'stat64_mc_rx': 'in-multicast-pkts',
    'stat_mc_rx': 'in-multicast-pkts',
    'stat64_wrx': 'in-octets',
    'stat_wrx': 'in-octets',
    'Ols_in': 'in-offline-sequences',
    'stat64_rateRxPeakFrame': 'in-peak-rate',
    # 'xxx': 'in-rate',
    'stat64_inputBuffersFull': 'input-buffer-full',
    'er_bad_os': 'invalid-ordered-sets',
    'Invalid_word': 'invalid-transmission-words',
    'Link_failure': 'link-failures',
    'lli64': 'link-level-interrupts',
    'Loss_of_sig': 'loss-of-signal',
    'Loss_of_sync': 'loss-of-sync',
    'stat64_mc_to': 'multicast-timeouts',
    'stat_mc_to': 'multicast-timeouts',
    'stat64_rateTxFrame': 'out-frame-rate',
    'stat64_ftx': 'out-frames',
    'stat_ftx': 'out-frames',
    'Lr_out': 'out-link-resets',
    # 'xx': 'out-max-frame-rate',
    'stat64_mc_tx': 'out-multicast-pkts',
    'stat_mc_tx': 'out-multicast-pkts',
    'stat64_wtx': 'out-octets',
    'stat_wtx': 'out-octets',
    'Ols_out': 'out-offline-sequences',
    'stat64_rateTxPeakFrame': 'out-peak-rate',
    # 'xxx': 'out-rate',
    'Fbsy': 'p-busy-frames',
    'Frjt': 'p-rjt-frames',
    'er64_pcs_blk': 'pcs-block-errors',
    'er_pcs_blk': 'pcs-block-errors',
    'Protocol_err': 'primitive-sequence-protocol-error',
    'er64_trunc': 'truncated-frames',
    'er_trunc': 'truncated-frames',
}
# SFP (media-rdp) used in sfpshow()
_sfp_to_api_1 = {
    'Connector': dict(p=2, id='media-rdp/connector', type='str'),
    'Current': dict(p=1, id=brcdapi_util.sfp_current, type='float'),
    'Date Code': dict(p=2, id='media-rdp/date-code', type='str'),
    'Encoding': dict(p=2, id='media-rdp/encoding', type='str'),
    'Identifier': dict(p=2, id='media-rdp/identifier', type='str'),
    'Vendor PN': dict(p=2, id=brcdapi_util.sfp_pn, type='str'),
    'Pwr On Time:': dict(p=5, id=brcdapi_util.sfp_power_on, type='int'),
    'RX Power': dict(p=4, id=brcdapi_util.sfp_rx_pwr, type='float'),
    'Serial No': dict(p=2, id=brcdapi_util.sfp_sn, type='str'),
    'Temperature': dict(p=1, id=brcdapi_util.sfp_temp, type='int'),
    'TX Power': dict(p=4, id=brcdapi_util.sfp_tx_pwr, type='float'),
    'Vendor Name': dict(p=2, id=brcdapi_util.sfp_vendor, type='str'),
    'Vendor OUI': dict(p=2, id=brcdapi_util.sfp_oui, type='str'),
    'Vendor Rev': dict(p=2, id='media-rdp/vendor-revision', type='str'),
    'Voltage': dict(p=1, id=brcdapi_util.sfp_volt, type='float'),
    'Wavelength': dict(p=1, id=brcdapi_util.sfp_wave, type='int'),
}
# Used in _pbs_port_type() to interpret the Port Type in portbuffershow output
_pbs_port_types = dict(
    E=brcddb_common.PORT_TYPE_E,
    F=brcddb_common.PORT_TYPE_F,
)
# Used in xxx to interpret "Avg Buffer Usage & FrameSize"
_pbs_avg_buf_conv = (
    'average-transmit-buffer-usage',
    'average-transmit-frame-size',
    'average-receive-buffer-usage',
    'average-receive-frame-size')

# Build a reverse port type lookup table
_physical_pbs_port_type = dict()
for _key, _v in brcddb_common.port_conversion_tbl[brcdapi_util.fc_port_type].items():
    if _key != brcddb_common.PORT_TYPE_UNKONWN:
        _physical_pbs_port_type.update({_v: _key})

# Used in _slotshow_d576(), _chassishow_wwn, _chassishow_blade(), _chassishow_ps() & _chassishow_ps
_unit_conv_tbl = {
    'AP_BLADE': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled', b=True),
    'CP_BLADE': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled', b=True),
    'CP BLADE Slot': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled',
                          b=True),
    'SW_BLADE': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled', b=True),
    'SW BLADE Slot': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled',
                          b=True),
    'CORE_BLADE': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled',
                       b=True),
    'CORE BLADE Slot': dict(key=brcdapi_util.fru_blade, unit='slot-number', status='blade-state', ok_status='enabled',
                            b=True),
    'PWR_SUPP': dict(key=brcdapi_util.fru_ps, unit='unit-number', status='operational-state', ok_status='ok', b=False),
    'POWER SUPPLY Unit': dict(key=brcdapi_util.fru_ps, unit='unit-number', status='operational-state',
                              ok_status='ok', b=False),
    'BLOWER': dict(key=brcdapi_util.fru_fan, unit='unit-number', status='operational-state', ok_status='ok', b=False),
    'FAN Unit': dict(key=brcdapi_util.fru_fan, unit='unit-number', status='operational-state', ok_status='ok', b=False),
    'WWN_CARD': dict(key=brcdapi_util.fru_wwn, unit='unit-number', status='operational-state', ok_status='ok', b=False),
    'WWN Unit': dict(key=brcdapi_util.fru_wwn, unit='unit-number', status='operational-state', ok_status='ok', b=False),
    'UNKNOWN': dict(key=None, unit=None, status=None, ok_status=None, b=False),
}
""" _slotshow_d576_tbl
key     API leaf
api     i:      position in in command line after conditioning with xxx and split on ' '
        c:      If present, the conversion between the command output and the value for the API
        int:    If True, convert to an integer. The default is False
"""
_slotshow_fru_id = {brcdapi_util.fru_blade: 'blade-id',
                    brcdapi_util.fru_ps: 'unit-number',
                    brcdapi_util.fru_fan: 'unit-number',
                    brcdapi_util.fru_wwn: 'unit-number'}
_slotshow_state = dict(ON='enabled',
                       ENABLED='enabled',
                       OFF='disabled',
                       DISABLED='disabled',
                       OUT='vacant',
                       FLTY='faulty')
_slotshow_ps = {'unit-number': dict(i=0, int=True), 'operational-state': dict(i=2, c=dict(ON='ok', FLTY='faulty'))}
_slotshow_d576_tbl = dict(
    AP_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=3, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(AP_BLADE='ap blade'))},),
    CP_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=3, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(CP_BLADE='cp blade'))},),
    SW_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=3, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(SW_BLADE='sw blade'))},),
    CORE_BLADE=dict(key=brcdapi_util.fru_blade,
                    api={'blade-id': dict(i=2, int=True),
                         'slot-number': dict(i=0, int=True),
                         'blade-state': dict(i=3, c=_slotshow_state),
                         'blade-type': dict(i=1, c=dict(CORE_BLADE='core blade'))},),
    UNKNOWN=dict(key=brcdapi_util.fru_blade,
                 api={'slot-number': dict(i=0, int=True),
                      'blade-state': dict(i=2, c=_slotshow_state),
                      'blade-type': dict(i=1, c=dict(UNKNOWN='unknown'))},),
    PWR_SUPP=dict(key=brcdapi_util.fru_ps, api=_slotshow_ps),
    BLOWER=dict(key=brcdapi_util.fru_fan, api=_slotshow_ps),
    WWN_CARD=dict(key=brcdapi_util.fru_wwn, api={'unit-number': dict(i=0)})
)
_slotshow_m_tbl = dict(
    AP_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=4, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(AP_BLADE='ap blade'))},),
    CP_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=4, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(CP_BLADE='cp blade'))},),
    SW_BLADE=dict(key=brcdapi_util.fru_blade,
                  api={'blade-id': dict(i=2, int=True),
                       'slot-number': dict(i=0, int=True),
                       'blade-state': dict(i=4, c=_slotshow_state),
                       'blade-type': dict(i=1, c=dict(SW_BLADE='sw blade'))},),
    CORE_BLADE=dict(key=brcdapi_util.fru_blade,
                    api={'blade-id': dict(i=2, int=True),
                         'slot-number': dict(i=0, int=True),
                         'blade-state': dict(i=4, c=_slotshow_state),
                         'blade-type': dict(i=1, c=dict(CORE_BLADE='core blade'))},),
    UNKNOWN=dict(key=brcdapi_util.fru_blade,
                 api={'slot-number': dict(i=0, int=True),
                      'blade-state': dict(i=2, c=_slotshow_state),
                      'blade-type': dict(i=1, c=dict(UNKNOWN='unknown'))},),
    PWR_SUPP=dict(key=brcdapi_util.fru_ps, api=_slotshow_ps),
    BLOWER=dict(key=brcdapi_util.fru_fan, api=_slotshow_ps),
    WWN_CARD=dict(key=brcdapi_util.fru_wwn, api={'unit-number': dict(i=0)})
)


def _split_parm(buf):
    """Splits lines with param: value. Returns value less any leading/trailing space

    :param buf: Line from CLI output to split
    :type buf: str
    :return k: Parameter key. '' if ':' not in buf
    :return v: Value - input str, buf, less the parameter key. '' if ':' not in buf
    :rtype v: str, None
    """
    if isinstance(buf, str):
        tl = buf.split(':')
        if len(tl) > 1:
            tl[1] = tl[1].lstrip()
            return tl[0], ':'.join(tl[1:]).rstrip()

    return '', ''


def switchshow(obj, content, append_buf=''):
    """Adds a switch object to a project object from switchshow output

    :param obj: Project object or object with a project object associated with it
    :type obj: brcddb.classes.project.ProjectObj
    :param content: Beginning of switchshow output text
    :type content: list
    :param append_buf: Text to append to the WWN when creating a key
    :type append_buf: str
    :return switch_obj: Switch object
    :rtype switch_obj: brcddb.classes.switch.SwitchObj
    :return i: Index into content where we left off
    :rtype i: int
    """
    global _physical_pbs_port_type

    buf, switch_obj, proj_obj = '', None, obj.r_project_obj()

    for buf in content:
        if 'switchWwn:' in buf:
            k, v = _split_parm(buf)
            switch_obj = proj_obj.s_add_switch(v + append_buf)
            break
    if switch_obj is None:
        brcdapi_log.exception('Could not find switchWwn in', echo=True)
        return switch_obj

    # Get the basic switch information
    i = 0
    while len(content) > i:
        buf = content[i]
        if len(buf) > len('Index') and buf[0: len('Index')] == 'Index' or 'LS Attributes:' in buf:
            break
        k, v = _split_parm(buf)
        if k == 'switchId':
            v = '0x' + v
        elif k == 'switchDomain':
            v = int(v.replace(' (unconfirmed)', ''))
        if k in _switchshow_tbl:
            brcddb_util.add_to_obj(switch_obj, _switchshow_tbl[k], v)
        elif k == 'switchRole':
            brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_principal, 1 if 'Principal' in v else 0)
        elif k == 'switchState':
            if v == 'Online':
                brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_op_status, 2)
                brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_enabled_state, True)
            else:
                brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_op_status, 3)
                brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_enabled_state, False)
        elif k in _switch_attributes_T_F.keys():
            brcddb_util.add_to_obj(switch_obj, _switch_attributes_T_F[k], False if 'OFF' in v.upper() else True)
        elif k in _switch_0_1_boolean_off_on.keys():
            brcddb_util.add_to_obj(switch_obj, _switch_0_1_boolean_off_on[k], 0 if 'OFF' in v.upper() else 1)
        elif k in _switch_0_1_boolean_yes_no.keys():
            brcddb_util.add_to_obj(switch_obj, _switch_0_1_boolean_yes_no[k], 0 if 'NO' in v.upper() else 1)
        elif k == 'Address Mode':
            brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfc_area_mode, int(v))
        i += 1
    brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_sw_user_name, switch_obj.r_get(brcdapi_util.bfs_sw_user_name))
    brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfs_did, switch_obj.r_get(brcdapi_util.bfs_did))

    # Get the logical switch attributes. Note that these are formated on a single line rather than in a list as the
    # other switch attributes are displayed when VF is enabled
    if 'LS Attributes:' in buf:
        for t_buf in buf[len('LS Attributes:'):].replace('[', '').replace(']', '').replace('\t', '').strip().split(','):
            cl = [c.strip() for c in t_buf.split(':')]
            if len(cl) == 1 and 'Address Mode' in cl[0]:
                brcddb_util.add_to_obj(switch_obj, brcdapi_util.bfc_area_mode, int(cl[0].split(' ')[2]))
            elif len(cl) == 2 and cl[0] in _switch_0_1_boolean_off_on.keys():
                brcddb_util.add_to_obj(switch_obj,
                                       _switch_0_1_boolean_off_on[cl[0]],
                                       0 if 'OFF' in cl[1].upper() else 1)
            elif len(cl) == 2 and cl[0] in _switch_0_1_boolean_yes_no.keys():
                brcddb_util.add_to_obj(switch_obj, _switch_0_1_boolean_yes_no[cl[0]], 0 if 'NO' in cl[1].upper() else 1)
        i += 1

    # Figure out where the indices are for the port parameters. Note that they are different for bladed vs. fixed port
    # switches and ge ports do not have an index
    port_index = dict()
    while len(content) > i:
        buf = content[i]
        if 'Index' in buf and 'Media' in buf:
            cl = gen_util.remove_duplicate_char(buf, ' ').strip().split(' ')
            for x in range(0, len(cl)):
                port_index.update({cl[x]: x})
            break
        i += 1

    # Now get the port information
    i += 2  # Skip the line just below it that has ================ in it
    while len(content) > i:
        buf = content[i].replace('\t', ' ').strip()
        cl = gen_util.remove_duplicate_char(buf, ' ').split(' ')
        if len(cl) < 6:
            break
        if 'ge' in cl[0]:
            cl.insert(1, None)  # It's a fixed port switch. ge ports do not have an FC address
            cl.insert(0, None)  # ge ports do not have an index
        elif 'ge' in cl[1]:
            cl.insert(2, None)  # It's a director. ge ports do not have an FC address
            cl.insert(0, None)  # ge ports do not have an index or an FC address
        else:
            cl[port_index['Index']] = int(cl[port_index['Index']])
            cl[port_index['Address']] = '0x' + cl[port_index['Address']]

        proto = cl[port_index['Proto']]
        if proto == 'FC' or proto == 'VE' or proto == 'FCIP':
            port_desc = ' '.join(cl[port_index['Proto']:])
            port_num = '0' if port_index.get('Slot') is None else cl[port_index.get('Slot')]
            port_num += '/' + cl[port_index['Port']]
            physical_state = _physical_port_state.get(cl[port_index['State']])
            try:
                speed = int(gen_util.non_decimal.sub('', cl[port_index['Speed']])) * 1000000000
            except ValueError:
                speed = 32000000000
            port_d = {
                'name': port_num,
                'index': cl[port_index['Index']],
                'fcid-hex': cl[port_index['Address']],
                'auto-negotiate': 1 if 'N' in cl[port_index['Speed']] else 0,
                'speed': speed,
                'operational-status': 2 if 'Online' in cl[port_index['State']] else 3,
                'is-enabled-state': False if 'Disabled' in port_desc or 'license not assigned' in port_desc else True,
                'physical-state': 'unknown' if physical_state is None else physical_state,
                'neighbor': dict(wwn=list()),
            }
            port_type = 'unknown-port'  # A port type should always be found below, but just in case ...
            for k, v in _physical_pbs_port_type.items():
                if k in port_desc:
                    port_type = v
                    break
            port_d.update(({'port-type-string': v}))
            port_obj = switch_obj.s_add_port(port_num) if proto == 'FC' \
                else switch_obj.s_add_ve_port(port_num) if proto == 'VE' \
                else switch_obj.s_add_ge_port(port_num) if proto == 'FCIP' \
                else None
            if port_obj is None:
                brcdapi_log.exception('Unexpected error in: ' + buf, echo=True)
            port_obj.s_new_key('fibrechannel', port_d)
        i += 1

    return switch_obj, i


# Case statement methods in portbuffershow()
def _pbs_user_port(port_obj, v):
    brcddb_util.add_to_obj(port_obj, brcdapi_util.fc_index, int(v) if v.isnumeric() else 0)


def _pbs_port_type(port_obj, v):
    port_type = _pbs_port_types.get(v)
    brcddb_util.add_to_obj(port_obj,
                           brcdapi_util.fc_port_type,
                           brcddb_common.PORT_TYPE_UNKONWN if port_type is None else port_type)


def _pbs_lx_mode(port_obj, v):
    brcddb_util.add_to_obj(port_obj, 'fos_cli/portbuffershow/lx_mode', v)


def _pbs_max_resv(port_obj, v):
    brcddb_util.add_to_obj(port_obj, 'fos_cli/portbuffershow/max_resv', int(v)) if v.isnumeric() else 0


def _pbs_avg_buffer_usage(port_obj, v):
    tl = v.replace('-', '0').replace(' ', '').replace(')', '(').split('(')
    for i in range(0, len(_pbs_avg_buf_conv)):
        try:
            val = int(tl[i])
        except (IndexError, ValueError):
            val = 0
        brcddb_util.add_to_obj(port_obj, 'fibrechannel/' + _pbs_avg_buf_conv[i], val)


def _pbs_buffer_usage(port_obj, v):
    brcddb_util.add_to_obj(port_obj, 'fibrechannel/current-buffer-usage', int(v) if v.isnumeric() else 0)


def _pbs_needed_buffers(port_obj, v):
    return  # $ToDo: _pbs_needed_buffers() - is this 'reserved-buffers'? I don't think so but what?


def _pbs_link_distance(port_obj, v):
    return  # $ToDo: _pbs_link_distance() - Finish


def _pbs_remaining_buffers(port_obj, v):
    return  # $ToDo: Finish _pbs_remaining_buffers()


# The starting alignment for the header denoted with ---- doesn't always align with the values. This is to correct it.
_portbuffer_show_adj_d = dict(max_resv=-2)


def portbuffershow(obj, content):
    """Adds the portbuffershow output to the ports in a switch object

    :param obj: Switch object or object with a switch object associated with it
    :type obj: brcddb.classes.switch.SwitchObj
    :param content: List of portbuffershow output text
    :type content: list
    """
    global _portbuffer_show_adj_d

    switch_obj = obj.r_switch_obj()

    # The output is formatted for a human, so we have to figure out the beginning and end of each item
    # Create a dictionary to put the start and end indices in. The starting alignment for the header denoted with ----
    # doesn't always align with the values. 's' is to correct it.
    port_buf_d = collections.OrderedDict()
    port_buf_d['user_port'] = dict(a=_pbs_user_port, s=0)
    port_buf_d['port_type'] = dict(a=_pbs_port_type, s=0)
    port_buf_d['lx_mode'] = dict(a=_pbs_lx_mode, s=-2)
    port_buf_d['max_resv'] = dict(a=_pbs_max_resv, s=-2)
    port_buf_d['avg_pbs_buffer_usage'] = dict(a=_pbs_avg_buffer_usage, s=0)
    port_buf_d['buffer_usage'] = dict(a=_pbs_buffer_usage, s=0)
    port_buf_d['needed_buffers'] = dict(a=_pbs_needed_buffers, s=0)
    port_buf_d['link_distance'] = dict(a=_pbs_link_distance, s=0)
    port_buf_d['remaining_buffers'] = dict(a=_pbs_remaining_buffers, s=0)

    # Figure out where everything aligns. $ToDo - Parse Remaining Buffers
    buf_l = [content.pop(0) for i in range(0, 3)]
    key_l = list(port_buf_d.keys())
    active_d = port_buf_d[key_l.pop(0)]
    last_d, state, i = None, 0, 0
    for char in buf_l[2]:
        if state == 0:
            if char == '-':
                if isinstance(last_d, dict):
                    last_d.update(e=i - 1 + active_d['s'])
                active_d.update(s=i + active_d['s'])
                if len(key_l) > 0:
                    last_d = active_d
                    active_d = port_buf_d[key_l.pop(0)]
                else:
                    break
                state = 1
        elif char == ' ':
            state = 0
        i += 1
    active_d.update(e=len(buf_l[2])-1)

    # Now parse the portbuffershow output
    for buf in [b.rstrip() for b in content]:
        if len(buf) == 0:
            break
        for k, d in port_buf_d.items():
            v = buf[port_buf_d[k]['s']:port_buf_d[k]['e']].strip()
            if k == 'user_port':
                port_obj = brcddb_port.port_obj_for_index(switch_obj, int(v))
                d['a'](port_obj, v)

    return


def portcfgshow(obj, content):
    """Adds the portcfgshow output to the port objects in a switch object

    :param obj: Switch object or object with a switch object associated with it
    :type obj: brcddb.classes.switch.SwitchObj
    :param content: List of portcfgshow output text
    :type content: list
    """
    i, slot, separator_index, ports, buf, state, port_l = 0, '0', 1, '', '', 'idle', list() 
    switch_obj = obj.r_switch_obj()

    for i in range(0, len(content)):
        buf = content[i].rstrip()
        if 'where AE:QoSAutoEnable' in buf:
            break
        if state == 'idle':
            if 'No ports found' in buf:
                break
            if 'Ports of Slot' in buf:
                temp_l = buf.split(' ')
                if len(temp_l) > 3:
                    slot = temp_l[3]
                    ports = buf
                    state = 'separator'
        elif state == 'separator':
            separator_index = buf.index('+')
            port_l = gen_util.remove_duplicate_char(ports[separator_index:].strip(), ' ').split(' ')
            state = 'values'
        elif state == 'values':
            if len(buf) == 0:
                state = 'idle'
            else:
                clean_buf = buf.lstrip().lower()
                if len(clean_buf) >= len('where') and clean_buf[0: len('where')] == 'where':
                    break
                key = 'fos_cli/portcfgshow/' + buf[0: separator_index-1].rstrip().replace('/', '_')
                vl = [b.strip() for b in gen_util.remove_duplicate_char(buf[separator_index:].strip(), ' ').split(' ')]
                for x in range(0, len(vl)):
                    port = slot + '/' + port_l[x]
                    port_obj = switch_obj.r_port_obj(port)
                    if port_obj is None:
                        brcdapi_log.exception('Could not find port ' + port, echo=True)
                    else:
                        brcddb_class_util.get_or_add(port_obj, key, vl[x])

    return i + 1


# Case methods used in _portstatsshow_special
def _stats_tim_txcrd_z_vc(port_obj):
    return


def _stats_phy_stats_clear_ts(port_obj):
    return


def _stats_lgc_stats_clear_ts(port_obj):
    return


def _stats_latency_dma_ts(port_obj):
    return


_portstatsshow_special = dict(
    tim_txcrd_z_vc=_stats_tim_txcrd_z_vc,
    phy_stats_clear_ts=_stats_phy_stats_clear_ts,
    lgc_stats_clear_ts=_stats_lgc_stats_clear_ts,
    latency_dma_ts=_stats_latency_dma_ts,
)


def portstatsshow(obj, content):
    """Parse portstatsshow and add to the port objects

    :param obj: Switch object or object with a switch object associated with it
    :type obj: brcddb.classes.switch.SwitchObj
    :param content: List of portstatsshow output text
    :type content: list
    """
    global _portstats_to_api

    port_obj, port_stats_d, switch_obj = None, None, obj.r_switch_obj()

    for buf in content:
        buf = buf.replace('er_single_credit_loss', 'er_single_credit_loss ')
        buf = buf.replace('er_multi_credit_loss', 'er_multi_credit_loss ')
        buf = buf.replace('fec_corrected_rate', 'fec_corrected_rate ')
        buf = buf.replace('latency_dma_ts', 'latency_dma_ts ')
        tl = gen_util.remove_duplicate_char(buf.replace('\t', ' '), ' ').split(' ')
        if len(tl) < 2:
            continue

        if tl[0] == 'port:':
            port_obj = brcddb_port.port_obj_for_index(switch_obj, int(tl[1].strip()))
            if port_obj is None:
                brcdapi_log.exception('Could not find port matching: ' + buf, echo=False)  # Just so it gets in the log
                raise Exception('Could not find port matching: ' + buf)
            port_stats_d = port_obj.r_get(brcdapi_util.stats_uri)
            if port_stats_d is None:
                port_stats_d = dict(name=port_obj.r_obj_key())
                port_obj.s_new_key(brcdapi_util.stats_uri, port_stats_d)

        elif tl[0] in _portstatsshow_special:
            _portstatsshow_special[tl[0]](port_obj)

        else:
            key = _portstats_to_api.get(tl[0])
            if key is not None:
                port_stats_d.update({key: int(tl[1])})


def portstats64show(obj, content):
    """Parse portstats64show and add to the port objects

    :param obj: Chassis object or object with a chassis object associated with it
    :type obj: brcddb.classes.chassis.ChassisObj
    :param content: List of portstats64show output text
    :type content: list
    :return i: Index into content where we left off
    :rtype i: int
    """
    global _portstats_to_api

    i, x, chassis_obj = 0, len('portstats64show'), obj.r_chassis_obj()
    while len(content) > i:

        # Get the port object
        buf = gen_util.remove_duplicate_char(content[i].replace('\t', ' '), ' ')
        if len(buf) == 0:
            i += 1
            continue
        if len(buf) < x or buf[0:x] != 'portstats64show':
            break
        index = int(buf.split(' ')[1])
        port_obj = brcddb_port.port_obj_for_index(chassis_obj, int(buf.split(' ')[1]))
        if port_obj is None:
            brcdapi_log.exception('Could not find port matching: ' + buf, echo=False)  # Just so it gets in the log
            raise Exception('Could not find port matching: ' + buf)
        port_stats_d = port_obj.r_get(brcdapi_util.stats_uri)
        if port_stats_d is None:
            port_stats_d = dict()
            port_obj.s_new_key(brcdapi_util.stats_uri, port_stats_d)

        # Parse the port statistics
        i += 1
        while len(content) > i and len(content[i]) > 0:
            buf = gen_util.remove_duplicate_char(content[i].replace('\t', ' '), ' ')
            cl = buf.split(' ')
            key = _portstats_to_api.get(cl[0])
            if key is not None:
                if 'top_int :' in buf:
                    i += 1
                    lv = int(gen_util.remove_duplicate_char(content[i].replace('\t', ' ').strip().split(' ')[0], ' '))
                    v = int('{:x}'.format(int(cl[1])) + '{:08x}'.format(lv), 16)
                else:
                    v = int(cl[1])
                port_stats_d.update({key: v})
            i += 1

    return i


"""Cases for chassisshow. All parameters are as follows:
chassis_obj The chassis object in _parsed_ss
cl          Current line parsed into a list, .split(':)
i           Index into content for the current line
n           If not None, the API branch & leaf associated with the value
return      Index into content for the next line to be processed"""

_chassis_to_api = {  # supportshow names converted to API names
    'System AirFlow': 'airflow-direction',
    'Power Consume Factor': 'power-usage',
    'Factory Part Num': 'part-number',
    'Factory Serial Num': 'serial-number',
    'Generation Num': 'generation-number',
    'Time Alive': 'time-alive',
    'Time Awake': 'time-awake',
}


def _chassishow_unit_parse(chassis_obj, content, cl, i, n, d):
    x = i
    while len(cl) > 1:
        if cl[0] in _chassis_to_api:
            if cl[0] in ('Time Alive', 'Time Awake', 'Power Consume Factor', 'Generation Num'):
                d.update({_chassis_to_api[cl[0]]: int(gen_util.non_decimal.sub('', cl[1]))})
            else:
                d.update({_chassis_to_api[cl[0]]: cl[1]})
        x += 1
        cl = [p.strip() for p in gen_util.remove_duplicate_char(content[x].replace('\t', ' '), ' ').split(':')]

    return x


def _chassisshow_add(chassis_obj, content, cl, i, n):
    brcddb_util.add_to_obj(chassis_obj, n, cl[1])
    return i + 1


def _chassisshow_add_int(chassis_obj, content, cl, i, n):
    brcddb_util.add_to_obj(chassis_obj, n, int(gen_util.non_decimal.sub('', cl[1])))
    return i + 1


def _chassishow_unit(chassis_obj, content, cl, i, key):
    # Get this object entry - we may have captured this blade already with slotshow
    try:
        obj = _chassis_unit_obj(chassis_obj, key, _unit_conv_tbl[cl[0]]['unit'], int(cl[1]))
        return _chassishow_unit_parse(chassis_obj, content, cl, i, key, obj)
    except ValueError:
        return i + 1  # This happens when there is an * by the unit number which is typical of faulty components


_chassisshow_actions = {
    'Chassis Family': dict(m=_chassisshow_add, n=brcdapi_util.bc_product_name),
    'Chassis Backplane Revision': dict(m=_chassisshow_add, n=brcdapi_util.bc_vendor_rev_num),
    'Chassis Factory Serial Num': dict(m=_chassisshow_add, n=brcdapi_util.bc_serial_num),
    'Time Alive': dict(m=_chassisshow_add_int, n=brcdapi_util.bc_time_alive),
    'Time Awake': dict(m=_chassisshow_add_int, n=brcdapi_util.bc_time_awake),
    'WWN Unit': dict(m=_chassishow_unit, n=brcdapi_util.fru_wwn),
    'SW BLADE Slot': dict(m=_chassishow_unit, n=brcdapi_util.fru_blade),
    'CP BLADE Slot': dict(m=_chassishow_unit, n=brcdapi_util.fru_blade),
    'CORE BLADE Slot': dict(m=_chassishow_unit, n=brcdapi_util.fru_blade),
    'POWER SUPPLY Unit': dict(m=_chassishow_unit, n=brcdapi_util.fru_ps),
    'FAN Unit': dict(m=_chassishow_unit, n=brcdapi_util.fru_fan),
}


def chassisshow(obj, content):
    """Adds a chassis object to a project object from chassisshow output

    :param obj: Project object or object with a project object associated with it
    :type obj: brcddb.classes.project.ProjectObj
    :param content: Beginning of chassisshow output text
    :type content: list
    :return chassis_obj: Chassis object
    :rtype chassis_obj: brcddb.classes.chassis.ChassisObj
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    ri, chassis_obj, proj_obj = 0, None, obj.r_project_obj()

    for buf in content:
        if 'Chassis Factory Serial Num:' in buf:
            chassis_obj = proj_obj.s_add_chassis(buf.split(':')[1].strip())
            break

    if chassis_obj is None:
        # If we haven't found it yet, pick the first WWN card. Get a chassis S/N by first finding "WWN  Unit:", then
        # look for Factory Serial Num:
        for buf in content:
            ri += 1
            if 'WWN  Unit:' in buf:
                break
            elif 'timeout' in buf:
                return chassis_obj, ri

        for buf in content[ri:]:
            ri += 1
            if 'Factory Serial Num:' in buf:
                chassis_obj = proj_obj.s_add_chassis(buf.split(':')[1].strip())
                break
            elif 'timeout' in buf:
                break

    # Parse the chassis data and add to the chassis object
    if chassis_obj is not None:
        tl = content[0:ri]
        i = 1
        while len(tl) > i:
            buf = tl[i]
            cl = [p.strip() for p in gen_util.remove_duplicate_char(buf.replace('\t', ' '), ' ').split(':')]
            if len(cl) > 1:
                if cl[0] in _chassisshow_actions:
                    i = _chassisshow_actions[cl[0]]['m'](chassis_obj, tl, cl, i, _chassisshow_actions[cl[0]]['n'])
                else:
                    i += 1
            else:
                i += 1

    return chassis_obj, ri


def fabricshow(obj, content):
    """Adds a fabric object to a project object from fabricshow output

    :param obj: Project object or object with a project object associated with it
    :type obj: brcddb.classes.project.ProjectObj
    :param content: Beginning of fabricshow output text
    :type content: list
    :return fabric_obj: Fabric object
    :rtype fabric_obj: brcddb.classes.fabric.FabricObj
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    ri, fab_obj, proj_obj = 0, None, obj.r_project_obj()

    # Skip to where the fabric list starts (after the '-----------------------')
    for ri in range(0, len(content)):
        buf = content[ri]
        ri += 1
        if '-version' in buf or 'no fabric' in buf or 'SS CMD END' in buf:
            return fab_obj, ri
        if '-----------------------' in buf:
            break

    brocade_fabric = list()
    while len(content) > ri:
        buf = content[ri]
        ri += 1
        if len(buf) == 0 or 'The Fabric has' in buf or 'Fabric had' in buf or 'SS CMD END' in buf:
            break
        temp_l = gen_util.remove_duplicate_char(buf.strip(), ' ').split(' ')
        if len(temp_l) > 5:
            if temp_l[5][0] == '>':  # It's the principal switch
                fab_obj = proj_obj.s_add_fabric(temp_l[2])
            brocade_fabric.append({
                'domain-id': int(temp_l[0].replace(':', '')),
                'fcid-hex': '0x' + temp_l[1],
                'name': temp_l[2],
                'ip-address': brcdapi_util.mask_ip_addr(temp_l[3]),
                'fcip-address': brcdapi_util.mask_ip_addr(temp_l[4]),
                'principal': 1 if '>' in temp_l[5] else 0,
                'switch-user-friendly-name': temp_l[5].replace('"', '').replace('>', ''),
            })

    if fab_obj is not None:
        brcddb_util.add_to_obj(fab_obj, 'brocade-fabric/fabric-switch', brocade_fabric)
        for d in brocade_fabric:
            fab_obj.s_add_switch(d['name'])

    return fab_obj, ri


"""nsshow CLI output to API map. Used in nsshow() to add data from nsshow output to the login object. The sub-dictionary
is as follow:

+-----------+---------------+---------------------------------------------------------------------------------------+
| Key       | Type          | Description                                                                           |
+===========+===============+=======================================================================================+
| uri       | str           | URI used in the API                                                                   |
+-----------+---------------+---------------------------------------------------------------------------------------+
| conv      | None, dict    | Conversion table or method to convert the values from CLI output to the API value.    |
|           | method        | Note: As of this writting, there were no dictionaries but the mechanics are present   |
|           |               | in the code to use one. The ability to hardcode an int, str, list, or tuple has also  |
|           |               | been coded.                                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
_nsshow_to_api = {
    'SCR': dict(uri=brcdapi_util.bns_scr),
    'PortSymb': dict(uri=brcdapi_util.bns_port_symbol),
    'NodeSymb': dict(uri=brcdapi_util.bns_node_symbol),
    'Fabric Port Name': dict(uri=brcdapi_util.bns_fab_port_name, conv=_conv_to_lower),
    'Permanent Port Name': dict(uri=brcdapi_util.bns_perm_port_name,
                                conv=_conv_to_lower),
    'Port Index': dict(uri=brcdapi_util.bns_port_index, conv=_conv_to_int),
    'Partial': dict(uri=brcdapi_util.bns_partial, conv=_conv_to_lower),
    'LSAN': dict(uri=brcdapi_util.bns_lsan, conv=_conv_to_lower),
    'Slow Drain Device': dict(uri=brcdapi_util.bns_sddq, conv=_conv_to_lower),
    'Device link speed': dict(uri=brcdapi_util.bns_link_speed),
    'Connected through AG': dict(uri=brcdapi_util.bns_connect_ag,  conv=_conv_to_lower),
    'Real device behind AG': dict(uri=brcdapi_util.bns_dev_behind_ag, conv=_conv_to_lower),
    'FCoE': dict(uri=brcdapi_util.bns_fcoe_dev, conv=_conv_to_lower),
}


def nsshow(obj, content):
    """Parse nsshow output

    :param obj: Any object that returns a fabric object, obj.r_fabric_obj(), and switch object, obj.r_switch_obj()
    :type obj: brcddb.classes.switch.SwitchObj, brcddb.classes.port.PortObj
    :param content: Beginning of nsshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    fab_obj, switch_obj, port_obj, ri = obj.r_fabric_obj(), obj.r_switch_obj(), None, 0

    buf = content[ri]
    if 'nsshow' in buf:
        ri += 1
        buf = content[ri]  # Skip past the invocation line
    if len(buf) == 0 or 'There is no entry' in buf:
        return ri + 1

    while len(content) > ri:
        buf = content[ri]
        ri += 1
        # Are we done processing nshsow output?
        if len(buf) == 0 or '}' in buf:
            break

        if len(buf) > 3:
            if buf[0:3] in (' N ', ' U ', ' NL'):  # Is there a new login?
                cl = [b.lower() for b in buf[3:].replace(' ', '').split(';')]
                login_obj = fab_obj.s_add_login(cl[2].lower())
                brcddb_util.add_to_obj(login_obj, brcdapi_util.bns_port_id, '0x' + cl[0])
                brcddb_util.add_to_obj(login_obj, brcdapi_util.bns_node_name, cl[3])
                brcddb_util.add_to_obj(login_obj, brcdapi_util.bns_port_name, cl[2])

            else:
                cl = [b.strip() for b in buf.split(':', 1)]
                cntl_d = _nsshow_to_api.get(cl[0])
                if isinstance(cntl_d, dict):
                    api_k = cntl_d['uri']
                    if api_k is not None:
                        val = cl[1]
                        val_c = cntl_d.get('conv')
                        if callable(val_c):
                            val = val_c(val)
                        elif isinstance(val_c, dict):
                            val = val if val_c.get(val) is None else val_c[val]
                        elif isinstance(val_c, (int, str, list, tuple)):
                            val = val_c
                        if cl[0] == 'Port Index':
                            port_obj = switch_obj.r_port_object_for_index(val)
                            if port_obj is not None:
                                nl = port_obj.r_get(brcdapi_util.fc_neighbor_wwn)
                                if nl is None:
                                    nl = list()
                                    brcddb_util.add_to_obj(port_obj, brcdapi_util.fc_neighbor_wwn, nl)
                                nl.append(login_obj.r_obj_key())
                        brcddb_util.add_to_obj(login_obj, api_k, val)

    return ri


_sfpshow_state_start = 0  # Looking first ============== above port number
_sfpshow_state_1st_sep = _sfpshow_state_start + 1  # Looking subsequent ============== above port number
_sfpshow_state_port = _sfpshow_state_1st_sep + 1  # Next line should be the port
_sfpshow_state_2nd_sep = _sfpshow_state_port + 1  # Next line should be ========= separator after port number
_sfpshow_state_parms = _sfpshow_state_2nd_sep + 1  # Next line should be one of the SFP parameters.
_sfp_sep = '======'
_sfp_sep_len = len(_sfp_sep)
_sfp_start_match = re.compile(r'(sfpshow|Media not installed|does not use)', re.IGNORECASE)
_sfp_skip_match = re.compile(r'(No SFP installed|does not use)', re.IGNORECASE)
_sfp_clean_port = re.compile(r'(Slot|Port|:|\t| )')
_sfp_end_match = re.compile(r'(-tuning|SS CMD END)', re.IGNORECASE)


def sfpshow(obj, content):
    """Parse sfpshow output

    :param obj: Switch object or object with a switch object associated with it
    :type obj: brcddb.classes.switch.SwitchObj
    :param content: Beginning of nsshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    global _sfp_sep, _sfp_sep_len, _sfpshow_state_start, _sfpshow_state_port, _sfpshow_state_1st_sep, _sfp_start_match
    global _sfp_to_api_1

    switch_obj, state, port_num, port_obj, ri = obj.r_switch_obj(), _sfpshow_state_start, None, None, 0

    for buf in content:
        buf = gen_util.remove_duplicate_char(buf.replace('\t', ' '), ' ')

        if _sfp_end_match.search(buf):
            break

        if 'CURRENT CONTEXT' in buf:
            break

        elif state == _sfpshow_state_start:
            # I don't remember why I check for the port seperator, ===== right away. It should always begin with
            # sfpshow -all.
            if len(buf) >= _sfp_sep_len and buf[0:_sfp_sep_len] == _sfp_sep:
                port_num, port_obj, state = None, None, _sfpshow_state_port
            elif len(buf) > 0:  # Ignore blank lines
                if 'sfpshow -all' in buf:
                    state = _sfpshow_state_1st_sep
                else:
                    break  # There are no SFPs in this switch

        elif state == _sfpshow_state_1st_sep:  # Looking for the first line separator before the port number
            port_num = port_obj = None
            if len(buf) >= _sfp_sep_len and buf[0:_sfp_sep_len] == _sfp_sep:
                state = _sfpshow_state_port

        elif state == _sfpshow_state_port:  # This should be the port number
            port_num = _sfp_clean_port.sub('', buf)
            if '/' not in port_num:
                port_num = '0/' + port_num
            port_obj = switch_obj.r_port_obj(port_num)
            if port_obj is None:
                brcdapi_log.exception(port_num + ' not found.', echo=False)  # It's probably an IP port so just log it
            state = _sfpshow_state_2nd_sep

        elif state == _sfpshow_state_2nd_sep:  # Looking for ==== separator after port number
            if len(buf) >= _sfp_sep_len and buf[0:_sfp_sep_len] == _sfp_sep:
                state = _sfpshow_state_parms
            else:
                brcdapi_log.exception('Invalid sfpshow output. Expected "=====", found ' + buf, echo=True)
                state = _sfpshow_state_start

        elif state == _sfpshow_state_parms:  # Parsing parameters. Exit this state on "Last poll time:"
            if len(buf) >= _sfp_sep_len and buf[0:_sfp_sep_len] == _sfp_sep:
                state = _sfpshow_state_port
                ri += 1
                continue
            if _sfp_skip_match.search(buf):
                state = _sfpshow_state_1st_sep
                ri += 1
                continue
            if port_obj.r_get('media-rdp/name') is None:
                brcddb_util.add_to_obj(port_obj, 'media-rdp/name', 'fc/' + port_num)
            cl = gen_util.remove_duplicate_char(buf.replace(':', ': ', 1), ' ').split(' ')
            param = buf.split(':')[0]

            # Transceiver requires special handling
            if param == 'Transceiver':
                try:
                    vl = [int(gen_util.non_decimal.sub('', c)) for c in cl[2].split(',')]
                except ValueError:
                    vl = list()  # Typical of older SFP
                brcddb_util.add_to_obj(port_obj, brcdapi_util.sfp_speed, vl)
                # 'Long_dist' is the most common for LWL optics but there are others such as Smart Optics. I have no
                # idea what they look like in supportshow output and getting it exactly right wasn't important for
                # anything I was working on at the time I wrote this so just 'long' was good enough.
                vl = ['short'] if 'Short_dist' in buf else ['long']
                brcddb_util.add_to_obj(port_obj, brcdapi_util.sfp_distance, vl)

            else:
                # Process normal parameters
                d = _sfp_to_api_1.get(param)
                if d is not None:
                    try:
                        if d['type'] == 'int':
                            v = int(gen_util.non_decimal.sub('', cl[d['p']]))
                        elif d['type'] == 'float':
                            v = float(gen_util.non_decimal.sub('', cl[d['p']]))
                        else:
                            v = cl[d['p']]
                    except ValueError:
                        v = cl[d['p']]  # typically -inf for nothing read
                    brcddb_util.add_to_obj(port_obj, d['id'], v)
                if 'Last poll time' in buf:
                    state = _sfpshow_state_1st_sep

        ri += 1

    return ri


def cfgshow_zone_gen(fab_obj, member_l):
    zone_type, peer_mem_l, pmem_l = brcddb_common.ZONE_STANDARD_ZONE, list(), list()

    if len(member_l) > 0 and gen_util.is_wwn(member_l[0], full_check=False) and member_l[0].split(':')[0] == '00':
        """It's a peer zone. Note that a WWN with a leading '00' is not a valid WWN so this is used to indicate that the
        WWN is a property parameter for a peer zone. This is easiest to explain with a example:
        
        00:02:00:00:00:03:01:02, principal_alias_1, principal_alias_2, member_alias_1, member_alias_2
        
        The only bytes I ever look at are the first byte and the last byte of the WWN. Breaking the WWN down:
        
        00          This indicates it's a peer zone and that this WWN is a peer zone property member (not an actual
                    zone member)
        02:00:00:00 Not relevant
        03:01       I can take a guess but I don't use this. Since I don't use, my example may not be correct.
        02          The last byte is the number of principal WWN members, not the number of aliases that follow. Keep in
                    mind that an alias can have multiple WWNs. Assuming each alias represents a single WWN, this means
                    the next two members are the principal members. All remaining members therefore are the peer members
                    
        Keep in mind that all bytes in a WWN, including the property member described above, are hex values.
        """
        zone_type, p, i, pc = brcddb_common.ZONE_USER_PEER, int(member_l[0].split(':')[7], 16), 1, 0
        while pc < p:
            alias_obj = fab_obj.r_alias_obj(member_l[i])
            pc += 1 if alias_obj is None else len(alias_obj.r_members())
            i += 1
        pmem_l, peer_mem_l = member_l[1:i], member_l[i:]

    else:
        peer_mem_l = member_l

    return zone_type, peer_mem_l, pmem_l


def _cfgshow_def_zone_act(fab_obj, name, mem_l):
    zone_type, sl, pl = cfgshow_zone_gen(fab_obj, mem_l)
    fab_obj.s_add_zone(name, zone_type, sl, pl)


def _cfgshow_alias_act(fab_obj, name, mem_l):
    fab_obj.s_add_alias(name, mem_l)


def _cfgshow_def_cfg_act(fab_obj, name, mem_l):
    fab_obj.s_add_zonecfg(name, mem_l)


def _cfgshow_eff_zone_act(fab_obj, name, mem_l):
    zone_type, sl, pl = cfgshow_zone_gen(fab_obj, mem_l)
    fab_obj.s_add_eff_zone(name, zone_type, sl, pl)


def _cfgshow_eff_cfg_act(fab_obj, name, mem_l):
    fab_obj.s_add_eff_zonecfg(mem_l)
    brcddb_util.add_to_obj(fab_obj, brcdapi_util.bz_eff_cfg, name)


"""A state machine is used to parse the cfgshow output. The state machine is designed to accomplish two objectives:

    * Find the transitions from:
        * Start
        * Defined zone section (note that the actions differ for defined zones and effective zones)
        * Effective zone
        * End
    * The action to take for each item after parsing is complete

The dictionaries used in _cfgshow_operand_tbl are as follows:

state   The next state after processing of the current state is complete
da      The action to take for this item when it is in the defined zone
ea      The action to take for this item when it is in the effective zone
"""
_cfgshow_state_start = 0  # Looking for "Defined configuration:"
_cfgshow_state_def = _cfgshow_state_start + 1  # Found "Defined configuration:"
_cfgshow_state_eff = _cfgshow_state_def + 1  # Found "Effective configuration:"
_cfgshow_state_continue = _cfgshow_state_eff + 1  # Continue processing cfg:, zone:, and alais:
_cfgshow_state_exit = _cfgshow_state_continue + 1  # Finished processing cfgshow output
_cfgshow_operand_tbl = {
    'Defined_configuration:': dict(state=_cfgshow_state_def),
    'Effective_configuration:': dict(state=_cfgshow_state_eff),
    'cfg:': dict(state=_cfgshow_state_continue, da=_cfgshow_def_cfg_act, ea=_cfgshow_eff_cfg_act),
    'zone:': dict(state=_cfgshow_state_continue, da=_cfgshow_def_zone_act, ea=_cfgshow_eff_zone_act),
    'alias:': dict(state=_cfgshow_state_continue, da=_cfgshow_alias_act),
}
_cfgshow_clean_buf = (
    (';', ' '),
    ('\t', ' '),
    ('Defined configuration:', 'Defined_configuration:'),
    ('Effective configuration:', 'Effective_configuration:'),
)


def _cfgshow_process(state, buf):
    """Sorts out parameters in cfgshow() and checks for state changes

    :param state: Current state - one of _cfgshow_state_*
    :type state: int
    :param buf: Current line being processed
    :type buf: str
    :return state: Next state
    :rtype state: int
    :return operand: Operand (name of configuration, zone, or alias). None if not present
    :rtype operand: str, None
    :return rl: List of members associated with the operand
    :rtype rl: list()
    """
    global _cfgshow_state_eff, _cfgshow_state_exit, _cfgshow_operand_tbl, _cfgshow_clean_buf

    operand, rl, next_state, t_buf, key = None, list(), None, buf, None

    # Clean up the line for processing
    for tl in _cfgshow_clean_buf:
        t_buf = t_buf.replace(tl[0], tl[1])
    tl = [b.strip() for b in gen_util.remove_duplicate_char(t_buf.strip(), ' ').split(' ') if len(b.strip()) > 0]

    # Figure out what the key, operand, and content is
    k = tl[0] if len(tl) > 0 else None
    if k is not None and k in _cfgshow_operand_tbl:
        operand = tl[1] if len(tl) > 1 else None
        rl = tl[2:] if len(tl) > 2 else list()
    else:
        k, operand, rl = None, None, tl

    # Figure out what the next state is
    if len(tl) == 0:
        next_state = _cfgshow_state_exit if state == _cfgshow_state_eff else _cfgshow_state_eff
    elif 'no configuration defined' in buf:
        next_state = _cfgshow_state_eff
    elif 'no configuration in effect' in buf:
        next_state = _cfgshow_state_exit
    elif k is not None and k in _cfgshow_operand_tbl:
        next_state = _cfgshow_operand_tbl[k]['state']

    return next_state, k, operand, rl


_cfgshow_template_d = dict(key='null', operand=None, mem_l=list())


def cfgshow(obj, content):
    """Parse cfgshow output

    :param obj: Fabric object or object with a fabric object associated with it
    :type obj: brcddb.classes.fabric.FabricObj
    :param content: Beginning of nsshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    global _cfgshow_state_exit, _cfgshow_state_start

    # Initialize local and return variables
    fab_obj, ri, mem_l, last_key, last_operand = obj.r_fabric_obj(), 0, list(), None, None
    state = _cfgshow_state_start
    active_d, def_l, eff_l = _cfgshow_template_d.copy(), list(), list()
    active_l = def_l

    # Parse the cfgshow output
    for buf in content:

        state, key, operand, mem_l = _cfgshow_process(state, buf)
        if state is not None and state == _cfgshow_state_exit:
            break

        if key is not None:
            active_l.append(active_d)
            active_d = _cfgshow_template_d.copy()
            active_d['key'], active_d['operand'], active_d['mem_l'] = key, operand, mem_l
            if key == 'Defined_configuration:':
                active_l = def_l
            elif key == 'Effective_configuration:':
                active_l = eff_l
        else:
            active_d['mem_l'].extend(mem_l)
        ri += 1
    active_l.append(active_d.copy())  # IDK why I made this a copy, but I'm not fixing working code.

    # Process (add to brcddb objects) the parsed data. Note that an alias must be unbundled, see comments in
    # cfgshow_zone_gen(), before evaluating peer zone. Hence, the order below.
    for action_key, active_l in dict(da=def_l, ea=eff_l).items():
        for cfg_key in ('alias:', 'zone:', 'cfg:'):
            action = _cfgshow_operand_tbl[cfg_key].get(action_key)
            if callable(action):
                for active_d in [d for d in active_l if d['key'] == cfg_key]:
                    action(fab_obj, active_d['operand'], active_d['mem_l'])

    return ri


def ficonshow(obj, content):
    """Parse ficonshow output

    :param obj: Switch object or object with a switch object associated with it
    :type obj: brcddb.classes.switch.SwitchObj
    :param content: Beginning of nsshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    switch_obj, ri = obj.r_switch_obj(), 0

    # Find where the first entry is by searching for 'Sequence#' in the header
    for buf in content:
        ri += 1
        if '}' in buf:
            return ri
        if 'Sequence#' in buf:
            break

    # Process all the entries
    for buf in content[ri:]:
        ri += 1

        if '}' in buf:
            break

        # Process each entry
        cl = gen_util.remove_duplicate_char(buf.replace('\t', ' '), ' ').strip().split(' ')
        if len(cl) > 12:  # It should always be 13
            pid = '0x' + cl[2].lower()
            port_obj = switch_obj.r_port_obj_for_pid(pid)
            if port_obj is None:
                brcdapi_log.exception(['Could not find port matching ' + pid + ' in:', buf], echo=True)
                continue
            ficon_d = {
                'link-address': pid[0:6],
                'format': cl[0],
                'port-type': cl[1],
                'registered-port-wwn': cl[3],
                'registered-node-wwn': cl[4],
                'flags': cl[5],
                'node-parameters': cl[6],
                'type-number': cl[7],
                'model-number': cl[8],
                'manufacturer': cl[9],
                'plant': cl[10],
                'sequence-number': cl[11],
                'tag': '0x' + cl[12],
            }
            port_obj.s_new_key('rnid', ficon_d)
        else:
            brcdapi_log.exception(['Invalid data for ficonshow rnid table:', buf], echo=True)

    return ri


_slotshow_d576_clean = (
    ('\t', ' '),
    (' BLADE', '_BLADE'),
    (' SUPP', '_SUPP'),
    (' CARD', '_CARD'),
)
_slotshow_d576_int = dict(
    CP_BLADE={
        'blade-state': dict(ON='enabled', OFF='disabled', FLTY='faulty')
    }
)


def _chassis_unit_obj(chassis_obj, key, unit, unit_num):
    """Finds a chassis unit (blade, power supply, fan, or WWN) in the chassis. Creates one if not found

    :param chassis_obj: Chassis object as in _parsed_ss['chassis']
    :type chassis_obj: dict
    :param key: API key for the unit
    :type key: str
    :param unit:
    :return: Dictionary for the switch structure
    :rtype: dict
    """
    unit_list = gen_util.convert_to_list(brcddb_util.get_from_obj(chassis_obj, key))
    for obj in unit_list:
        if obj[unit] == unit_num:
            return obj
    obj = dict(unit=unit_num)
    unit_list.append(obj)
    return obj


def _slotshow_get_fru(chassis_obj, api_key):
    rl, rd = chassis_obj.r_get(api_key), None
    if rl is None:
        rl = list()
        brcddb_util.add_to_obj(chassis_obj, api_key, rl)
        return rl, rd
    s_key = _slotshow_fru_id.get(api_key)
    if s_key is None:
        brcdapi_log.exception('Unknown key: ' + api_key, echo=True)
        return rl, rd
    for d in rl:
        if d.get(s_key) is not None and d.get(s_key) == id:
            return rl, d
    return rl, rd


def _slotshow(obj, content, slotshow_d):
    """Parse slotshow -d576 output

    :param obj: Chassis object or object with a switch object associated with it
    :type obj: brcddb.classes.chassis.ChassisObj
    :param content: Beginning of slotshow output text
    :type content: list
    :param slotshow_d: Either _slotshow_d576_tbl or _slotshow_m_tbl
    :type slotshow_d: dict
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    global _slotshow_d576_clean

    chassis_obj, ri = obj.r_chassis_obj(), 0

    # Skip past the header
    for buf in content:
        ri += 1
        if '--------' in buf:
            break

    # Parse the output
    for buf in content[ri:]:
        ri += 1
        for tl in _slotshow_d576_clean:
            buf = buf.replace(tl[0], tl[1])
        cl = gen_util.remove_duplicate_char(buf.strip(), ' ').split(' ')
        if len(cl) < 4:
            break
        if '*' in cl[0]:  # It's a note at the end of the slotshow for one of the FRUs - typically faulty
            break

        # Get the FRU
        unit_d = slotshow_d.get(cl[1])
        if unit_d is None:
            brcdapi_log.exception(['Unkown FRU Type: ' + cl[1] + ' in:', buf], echo=True)
            continue
        fru_l, fru_d = _slotshow_get_fru(chassis_obj, unit_d['key'])
        api_d = unit_d['api']
        val, d = None, dict()
        for k, v in api_d.items():
            val = int(cl[v['i']]) if v.get('int') is not None and v.get('int') else cl[v['i']]
            if v.get('c') is not None and v.get('c').get(val) is not None:
                val = v['c'][val]
            d.update({k: val})
        if fru_d is None:
            fru_l.append(d)
        else:  # We already have this FRU. Just add to the dictionary
            for k, v in d.items():
                if k not in d:  # Only add the leaf if it's not already in the dictionary for this FRU
                    d.update({k: val})

    return ri


def slotshow_d576(obj, content):
    """Parse slotshow -d576 output

    :param obj: Chassis object or object with a switch object associated with it
    :type obj: brcddb.classes.chassis.ChassisObj
    :param content: Beginning of slotshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    global _slotshow_d576_tbl

    return _slotshow(obj, content, _slotshow_d576_tbl)


def slotshow_m(obj, content):
    """Parse slotshow -m output

    :param obj: Chassis object or object with a switch object associated with it
    :type obj: brcddb.classes.chassis.ChassisObj
    :param content: Beginning of slotshow output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    global _slotshow_m_tbl

    return _slotshow(obj, content, _slotshow_m_tbl)


def defzone(obj, content):
    """Parse defzone output

    :param obj: Fabric object or object with a fabric object associated with it
    :type obj: brcddb.classes.fabric.FabricObj
    :param content: Beginning of defzone output text
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    ri, fabric_obj = 0, obj.r_fabric_obj()
    all_access = fabric_obj.r_get(brcdapi_util.bz_eff_default_zone)
    for buf in content:
        ri += 1
        if 'committed' in buf:
            if all_access is None:
                access = brcddb_common.DEF_ZONE_ALLACCESS if 'All Access' in buf else brcddb_common.DEF_ZONE_NOACCESS
                brcddb_util.add_to_obj(fabric_obj, brcdapi_util.bz_eff_default_zone, access)
            break
        elif 'zone --show' in buf and 'defzone' not in buf:
            brcdapi_log.exception(['Could not find in "committed" in:'] + content[0:7], echo=True)
            ri = max(0, ri-1)
            break

    return ri


def portname_range(obj, content):
    """Adds the port name to each associated port object

    :param obj: Object with a chassis object associated with it
    :type obj: brcddb.classes.chassis.ChassisObj, brcddb.classes.port.PortObj, brcddb.classes.switch.SwitchObj
    :param content: List of portname output when a range is selected for the portname command
    :type content: list
    :return ri: Index into content where we left off
    :rtype ri: int
    """
    ri, chassis_obj = 0, obj.r_chassis_obj()

    for buf in content:
        ri += 1
        if 'CURRENT CONTEXT' in buf or 'portname' in buf:
            pass
        elif 'port' in buf:
            try:
                buf_l = buf.split(':')
                port_index = int(gen_util.remove_duplicate_char(buf_l[0], ' ').split(' ')[1])
                port_obj = chassis_obj.r_port_object_for_index(port_index)
                port_obj.rs_key(brcdapi_util.fc_user_name, buf_l[1].strip())
            except (IndexError, TypeError, ValueError):
                brcdapi_log.exception('Invalid format for port name: ' + buf, echo=True)
                break
        else:
            break

    return ri
