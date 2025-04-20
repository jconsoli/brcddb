"""
Copyright 2023, 2024, 2025 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Methods and tables to support the class ChassisObj.

**Public Methods**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| blade_name            | Converts the brocade-fru/blade/blade-id number to a user friendly blade type              |
+-----------------------+-------------------------------------------------------------------------------------------+
| best_chassis_name     | Returns the chassis name, if available. Otherwise, the WWN for the chassis                |
+-----------------------+-------------------------------------------------------------------------------------------+
| chassis_type          | Returns the chassis type (ie: G720)                                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| eos_epoch             | Returns the End of Support (EOS) date in epoch time                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| eos                   | Returns the End of Support (EOS) date in human readable format                            |
+-----------------------+-------------------------------------------------------------------------------------------+
| firmware_version      | Returns the firmware version as text.                                                     |
+-----------------------+-------------------------------------------------------------------------------------------+
| gen                   | Returns the gen type as an integer                                                        |
+-----------------------+-------------------------------------------------------------------------------------------+
| slots                 | Returns the number of slots for a switch or chassis                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| ibm_machine_type      | Returns the IBM machine type for the switch                                               |
+-----------------------+-------------------------------------------------------------------------------------------+
| sys_z_supported       | Returns True if z systems supported                                                       |
+-----------------------+-------------------------------------------------------------------------------------------+
| chassis_speed         | Converts the switch type number to the max speed the switch is capable of as an int in    |
|                       | Gbps.                                                                                     |
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
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024, 2025 Consoli Solutions, LLC'
__date__ = '12 Apr 2025'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.6'

import time
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util

_MIN_SYMB_LEN = 10

blade_id_name = {  # ToDo - Add G720 and G730
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
    214: 'CR64-4',
    215: 'CR64-8',
    216: 'FC64-48',
    218: 'FC32-X7-48',
    220: 'CPX7',
    232: 'FC64-64',
}
cfg_unknown = 0
cfg_fixed = 1
cfg_fcip = 2
cfg_4_slot = 3
cfg_8_slot = 4
"""chassis_type_d: key is the switch type, value is a dictionary as follows:
    +-------+-------+---------------------------------------------------------------------------------------+
    | brcd  | str   | Brocade brand name                                                                    |
    +=======+=======+=======================================================================================+
    | ibm   | str   | IBM brand name                                                                        |
    +-------+-------+---------------------------------------------------------------------------------------+
    | hpe   | str   | HPE brand name                                                                        |
    +-------+-------+---------------------------------------------------------------------------------------+
    | dell  | str   | Dell-EMC brand name                                                                   |
    +-------+-------+---------------------------------------------------------------------------------------+
    | hv    | str   | Hitachi Vantara brand name                                                            |
    +-------+-------+---------------------------------------------------------------------------------------+
    | netapp| str   | NetApp brand name                                                                     |
    +-------+-------+---------------------------------------------------------------------------------------+
    | pure  | str   | Pure brand name                                                                       |
    +-------+-------+---------------------------------------------------------------------------------------+
    | ibm_t | str   | IBM machine type                                                                      |
    +-------+-------+---------------------------------------------------------------------------------------+
    | spd   | int   | Maximum speed capability in Gbps                                                      |
    +-------+-------+---------------------------------------------------------------------------------------+
    | cfg   | int   | 0 (cfg_unknown) - Unknown                                                             |
    |       | int   | 1 (cfg_fixed) - fixed port FC switch                                                  |
    |       | int   | 2 (cfg_fcip) - FCIP switch                                                            |
    |       | int   | 3 (cfg_4_slot) - 4 slot chassis                                                       |
    |       | int   | 4 (cfg_8_slot) - 8 slot chssis                                                        |
    +-------+-------+---------------------------------------------------------------------------------------+
    | gen   | int   | Arbitrarily picked 1 for 1G, 2 for 2G, and 3 for 4G. All else standard Gen notation   |
    +-------+-------+---------------------------------------------------------------------------------------+
    | z     | bool  | True if supported for zSystems                                                        |
    +-------+-------+---------------------------------------------------------------------------------------+
    | eos   | int   | Epoch date/time for last day of support                                               |
    +-------+-------+---------------------------------------------------------------------------------------+
"""
chassis_type_d = {
    0: dict(brcd='Unknown', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
            pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_unknown,
            gen=0, z=False, eos=0.0),
    2: dict(brcd='2800', ibm='Unknown', hpe='2800', dell='DS-16B', hv='2800',
            pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=1, cfg=cfg_fixed,
            gen=1, z=False, eos=1197781199.0),
    3: dict(brcd='2100/2400', ibm='S08', hpe='2100/2400', dell='DS-8B', hv='2100/2400',
            pure='Unknown', netapp='Unknown', ibm_t='2109-S08', spd=1, cfg=cfg_fixed,
            gen=2, z=False, eos=1197781199.0),
    4: dict(brcd='20x0', ibm='ManagedHub', hpe='20x0', dell='20x0', hv='20x0',
            pure='Unknown', netapp='Unknown', ibm_t='3534-1RU', spd=1, cfg=cfg_fixed,
            gen=1, z=False, eos=631256399.0),
    5: dict(brcd='22x0', ibm='Unknown', hpe='22x0', dell='22x0', hv='22x0',
            pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=1, cfg=cfg_fixed,
            gen=1, z=False, eos=631256399.0),
    6: dict(brcd='2800', ibm='Unknown', hpe='2800', dell='DS-16b', hv='2800',
            pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=1, cfg=cfg_fixed,
            gen=1, z=False, eos=1197781199.0),
    7: dict(brcd='2000', ibm='Unknown', hpe='2000', dell='DS-SCB', hv='2000',
            pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=1, cfg=cfg_fixed,
            gen=1, z=False, eos=631256399.0),
    9: dict(brcd='3800', ibm='F16', hpe='3800', dell='DS-16B2', hv='3800',
            pure='Unknown', netapp='Unknown', ibm_t='2109-F16', spd=2, cfg=cfg_fixed,
            gen=2, z=True, eos=1272686399.0),
    10: dict(brcd='12000', ibm='M12', hpe='StorageWorks2/64', dell='ED-12000B', hv='12000',
             pure='Unknown', netapp='Unknown', ibm_t='2109-M12', spd=2, cfg=cfg_fcip,
             gen=2, z=True, eos=1270094399.0),
    12: dict(brcd='3900', ibm='F32', hpe='StorageWorks2/32', dell='DS-32B2', hv='3900',
             pure='Unknown', netapp='Unknown', ibm_t='2109-F32', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1280721599.0),
    16: dict(brcd='3200', ibm='F08', hpe='StorageWorks2/8-EL', dell='DS-8B2', hv='3200',
             pure='Unknown', netapp='Unknown', ibm_t='3534-F08', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1260939599.0),
    17: dict(brcd='3800VL', ibm='Unknown', hpe='StorageWorks3800VL', dell='3800VL', hv='3800VL',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1272686399.0),
    18: dict(brcd='3000', ibm='Unknown', hpe='3000', dell='3000', hv='3000',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1359867599.0),
    21: dict(brcd='24000', ibm='M14', hpe='StorageWorks2/128', dell='ED-24000B', hv='24000',
             pure='Unknown', netapp='Unknown', ibm_t='2109-M14', spd=2, cfg=cfg_fcip,
             gen=2, z=True, eos=1304049599.0),
    22: dict(brcd='3016', ibm='2GEntrySANSwitchModule', hpe='24000', dell='24000', hv='24000',
             pure='Unknown', netapp='Unknown', ibm_t='26K5601/90P0165', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1306123199.0),
    26: dict(brcd='False', ibm='H16', hpe='StorageWorks2/16V', dell='DS-16B3', hv='3850',
             pure='Unknown', netapp='Unknown', ibm_t='2005-H16', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1298955599.0),
    27: dict(brcd='3250', ibm='H08', hpe='StorageWorks2/8V', dell='3250', hv='3250',
             pure='Unknown', netapp='Unknown', ibm_t='2005-H08', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1298955599.0),
    29: dict(brcd='4012', ibm='Unknown', hpe='bladeSystem4GbSANswitch', dell='4012', hv='4012',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=2, cfg=cfg_fixed,
             gen=2, z=False, eos=1362113999.0),
    32: dict(brcd='4100', ibm='SAN16B-2', hpe='StorageWorks4/32', dell='DS-4100B', hv='4100',
             pure='Unknown', netapp='Unknown', ibm_t='2005-B32', spd=4, cfg=cfg_fixed,
             gen=2, z=False, eos=1351742399.0),
    33: dict(brcd='3014', ibm='3014', hpe='3014', dell='3014', hv='3014',
             pure='Unknown', netapp='Unknown', ibm_t='3014', spd=4, cfg=cfg_fixed,
             gen=2, z=False, eos=1309492799.0),
    34: dict(brcd='200E', ibm='SAN16B-2', hpe='StorageWorks4/8or4/16', dell='DS-220B', hv='200E',
             pure='Unknown', netapp='Unknown', ibm_t='2005-B16', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=1393649999.0),
    37: dict(brcd='4020', ibm='4GbSANSwitchModule', hpe='4020', dell='4020', hv='4020',
             pure='Unknown', netapp='Unknown', ibm_t='32R1812', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=631256399.0),
    38: dict(brcd='7420', ibm='Unknown', hpe='StorageWorks200', dell='7420', hv='7420',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=1351742399.0),
    40: dict(brcd='FCRFrontDomain', ibm='Unknown', hpe='FCRFrontDomain', dell='FCRFrontDomain', hv='FCRFrontDomain',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=4102549199.0),
    41: dict(brcd='FCRXlateDomain', ibm='Unknown', hpe='FCRXlateDomain', dell='FCRXlateDomain', hv='FCRXlateDomain',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=4102549199.0),
    42: dict(brcd='48000', ibm='SAN256B', hpe='StorageWorks4/256', dell='ED-48000B', hv='48000',
             pure='Unknown', netapp='Unknown', ibm_t='2109-M48', spd=4, cfg=cfg_fcip,
             gen=3, z=True, eos=1455771599.0),
    43: dict(brcd='4024', ibm='4024', hpe='bladeSystem4GbSANswitch', dell='4024', hv='4024',
             pure='Unknown', netapp='Unknown', ibm_t='4024', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=1409975999.0),
    44: dict(brcd='4900', ibm='SAN64B-2', hpe='4/64', dell='DS-4900B', hv='4900',
             pure='Unknown', netapp='Unknown', ibm_t='2005-B64', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=1393649999.0),
    45: dict(brcd='4016', ibm='4016', hpe='4016', dell='4016', hv='4016',
             pure='Unknown', netapp='Unknown', ibm_t='4016', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=631256399.0),
    46: dict(brcd='7500', ibm='2005-R18', hpe='StorageWorks400', dell='MP-7500B', hv='7500',
             pure='Unknown', netapp='Unknown', ibm_t='2005-R18', spd=4, cfg=cfg_fixed,
             gen=3, z=True, eos=1471319999.0),
    51: dict(brcd='4018', ibm='Unknown', hpe='4018', dell='4018', hv='4018',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=631256399.0),
    55: dict(brcd='7600', ibm='Unknown', hpe='7600', dell='7600', hv='7600',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=631256399.0),
    58: dict(brcd='5000', ibm='2005-B5K', hpe='StorageWorks4/32B', dell='DS-5000B', hv='5000',
             pure='Unknown', netapp='Unknown', ibm_t='2005-B5K', spd=4, cfg=cfg_fixed,
             gen=3, z=False, eos=1393649999.0),
    62: dict(brcd='DCX-8', ibm='SAN768B', hpe='StorageWorksDCSANbackbonedirector', dell='ED-DCX-B', hv='DCX',
             pure='Unknown', netapp='Unknown', ibm_t='2499-384', spd=8, cfg=cfg_8_slot,
             gen=4, z=True, eos=1573793999.0),
    64: dict(brcd='5300', ibm='SAN80B-4', hpe='StorageWorks8/80', dell='DS-5300B', hv='5300',
             pure='Unknown', netapp='Unknown', ibm_t='2498-B80', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=1566532799.0),
    66: dict(brcd='5100', ibm='SAN40B-4', hpe='StorageWorks8/40', dell='DS-5100B', hv='5100',
             pure='Unknown', netapp='Unknown', ibm_t='2498-B40', spd=8, cfg=cfg_fixed,
             gen=4, z=True, eos=1529035199.0),
    67: dict(brcd='Encryption', ibm='SAN32B-E4', hpe='AR944A', dell='ES-5832B', hv='Encryption',
             pure='Unknown', netapp='Unknown', ibm_t='2498-E32', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=1577854799.0),
    69: dict(brcd='5410', ibm='Unknown', hpe='EVA4400', dell='5410', hv='5410',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=631256399.0),
    71: dict(brcd='300', ibm='SAN24B-4', hpe='StorageWorks8/24', dell='DS-300B', hv='300',
             pure='Unknown', netapp='Unknown', ibm_t='2498-B24', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=1566532799.0),
    72: dict(brcd='5480', ibm='Unknown', hpe='8GbSANmoduleforHPbladeSystem', dell='5480', hv='5480',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=4102549199.0),
    73: dict(brcd='5470', ibm='Unknown', hpe='5470', dell='5470', hv='5470',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=631256399.0),
    75: dict(brcd='5424', ibm='Unknown', hpe='5424', dell='5424', hv='5424',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=True, eos=631256399.0),
    76: dict(brcd='8000', ibm='ConvergedSwitchL32', hpe='StorageWorksFCoverethernet', dell='MP-8000B', hv='8000',
             pure='Unknown', netapp='Unknown', ibm_t='3758-B32', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=1522727999.0),
    77: dict(brcd='DCX-4S', ibm='SAN384B', hpe='StorageWorksDC04SANdirector', dell='ED-DCX-4S-B', hv='DCX-4S',
             pure='Unknown', netapp='Unknown', ibm_t='2499-192', spd=8, cfg=cfg_4_slot,
             gen=5, z=True, eos=1573793999.0),
    83: dict(brcd='7800', ibm='SAN06B-R', hpe='1606', dell='MP-7800B', hv='7800',
             pure='Unknown', netapp='Unknown', ibm_t='2498-R06', spd=8, cfg=cfg_fixed,
             gen=5, z=True, eos=1626926399.0),
    86: dict(brcd='5450', ibm='Unknown', hpe='5450', dell='5450', hv='5450',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=631256399.0),
    87: dict(brcd='5460', ibm='Unknown', hpe='5460', dell='5460', hv='5460',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=631256399.0),
    90: dict(brcd='8470', ibm='Converged10GbESwitchModule', hpe='8470', dell='8470', hv='8470',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
             gen=4, z=False, eos=631256399.0),
    92: dict(brcd='VA-40FC', ibm='Unknown', hpe='VA-40FC', dell='VA-40FC', hv='VA-40FC',
             pure='Unknown', netapp='Unknown', ibm_t='69Y1909', spd=0, cfg=cfg_fixed,
             gen=0, z=False, eos=1548421199.0),
    95: dict(brcd='VDX6720-24', ibm='Unknown', hpe='VDX6720-24', dell='VDX6720-24', hv='VDX6720-24',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
             gen=0, z=False, eos=1567569599.0),
    96: dict(brcd='VDX6730-32', ibm='VDX6730-32', hpe='VDX6730-32', dell='VDX6730-32', hv='VDX6730-32',
             pure='Unknown', netapp='Unknown', ibm_t='3759-C32/8553-AF6/8553-AR5', spd=0, cfg=cfg_fixed,
             gen=0, z=False, eos=1590379199.0),
    97: dict(brcd='VDX6720-60', ibm='Unknown', hpe='VDX6720-60', dell='VDX6720-60', hv='VDX6720-60',
             pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
             gen=0, z=False, eos=631256399.0),
    98: dict(brcd='VDX6730-76', ibm='VDX6730-76', hpe='VDX6730-76', dell='VDX6730-76', hv='VDX6730-76',
             pure='Unknown', netapp='Unknown', ibm_t='3759-C76/8553-BF8/8553-BR7', spd=0, cfg=cfg_fixed,
             gen=0, z=False, eos=1590379199.0),
    108: dict(brcd='M8428-kFCoE', ibm='Unknown', hpe='M8428-kFCoE', dell='M8428-kFCoE', hv='M8428-kFCoE',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=631256399.0),
    109: dict(brcd='6510', ibm='SAN48B-5', hpe='SN6000B', dell='DS-6510B', hv='6510',
              pure='Unknown', netapp='Unknown', ibm_t='2498-F48', spd=16, cfg=cfg_fixed,
              gen=5, z=True, eos=1750165199.0),
    112: dict(brcd='VDX6746', ibm='Unknown', hpe='VDX6746', dell='VDX6746', hv='VDX6746',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=4102549199.0),
    116: dict(brcd='VDX6710', ibm='Unknown', hpe='VDX6710', dell='VDX6710', hv='VDX6710',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=1590379199.0),
    117: dict(brcd='6547', ibm='FC5022SANSwitch', hpe='6547', dell='6547', hv='6547',
              pure='Unknown', netapp='Unknown', ibm_t='90Y9356/00Y3324/88Y6374', spd=16, cfg=cfg_fixed,
              gen=5, z=False, eos=4102549199.0),
    118: dict(brcd='6505', ibm='SAN24B-5', hpe='6505', dell='DS-6505B', hv='6505',
              pure='Unknown', netapp='Unknown', ibm_t='2498-F24', spd=16, cfg=cfg_fixed,
              gen=5, z=True, eos=1746071999.0),
    120: dict(brcd='DCX8510-8', ibm='SAN768B-2', hpe='SN8000B8-slot', dell='ED-DCX8510-8B', hv='DCX8510-8',
              pure='Unknown', netapp='Unknown', ibm_t='2499-816', spd=16, cfg=cfg_8_slot,
              gen=5, z=True, eos=1746017999.0),
    121: dict(brcd='DCX8510-4', ibm='SAN384B-2', hpe='SN8000B4-slot', dell='ED-DCX8510-4B', hv='DCX8510-4',
              pure='Unknown', netapp='Unknown', ibm_t='2499-416', spd=16, cfg=cfg_4_slot,
              gen=5, z=True, eos=1746017999.0),
    124: dict(brcd='5430', ibm='Unknown', hpe='5430', dell='5430', hv='5430',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
              gen=4, z=False, eos=1503287999.0),
    125: dict(brcd='5431', ibm='Unknown', hpe='5431', dell='5431', hv='5431',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
              gen=4, z=False, eos=1503287999.0),
    129: dict(brcd='6548', ibm='Unknown', hpe='16GbSANswitchforHPBladeSystem', dell='6548', hv='6548',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=16, cfg=cfg_fixed,
              gen=4, z=False, eos=4102549199.0),
    130: dict(brcd='M6505', ibm='Unknown', hpe='M6505', dell='M6505', hv='M6505',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=16, cfg=cfg_fixed,
              gen=4, z=False, eos=1746017999.0),
    131: dict(brcd='VDX6740', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=4102549199.0),
    133: dict(brcd='6520', ibm='SAN96B-5', hpe='SN6500B', dell='DS-6520B', hv='6520',
              pure='Unknown', netapp='Unknown', ibm_t='2498-F96/N96', spd=16, cfg=cfg_fixed,
              gen=5, z=False, eos=1821484800.0),
    134: dict(brcd='5432', ibm='Unknown', hpe='5432', dell='5432', hv='5432',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=8, cfg=cfg_fixed,
              gen=4, z=False, eos=631256399.0),
    138: dict(brcd='VDX6746', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=631256399.0),
    148: dict(brcd='7840', ibm='SAN42B-R', hpe='SN4000B', dell='MP-7840B', hv='7840',
              pure='Unknown', netapp='Unknown', ibm_t='2498-R42', spd=16, cfg=cfg_fixed,
              gen=5, z=True, eos=None),
    151: dict(brcd='VDX6740T-1G', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=True, eos=4102549199.0),
    153: dict(brcd='VDX6940T-1G', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
              gen=0, z=False, eos=4102549199.0),
    162: dict(brcd='G620', ibm='SAN64B-6', hpe='SN6600B', dell='DS-6620B', hv='G620',
              pure='G620', netapp='Unknown', ibm_t='8960-F64/N64', spd=32, cfg=cfg_fixed,
              gen=6, z=True, eos=None),
    165: dict(brcd='X6-4', ibm='SAN256B-6', hpe='SN8600B-4', dell='ED-DCX6-4B', hv='X6-4',
              pure='X6-4', netapp='Unknown', ibm_t='8961-F04', spd=32, cfg=cfg_4_slot,
              gen=6, z=True, eos=None),
    166: dict(brcd='X6-8', ibm='SAN512B-6', hpe='SN8600B-8', dell='ED-DCX6-8B', hv='X6-8',
              pure='X6-8', netapp='Unknown', ibm_t='8961-F08', spd=32, cfg=cfg_8_slot,
              gen=6, z=True, eos=None),
    170: dict(brcd='G610', ibm='SAN64B-6', hpe='SN3600B', dell='DS-6610B', hv='G610',
              pure='G610', netapp='Unknown', ibm_t='8960-F64/N64', spd=32, cfg=cfg_fixed,
              gen=6, z=False, eos=None),
    171: dict(brcd='AMP_2_0', ibm='AMP_2_0', hpe='AMP_2_0', dell='AMP_2_0', hv='AMP_2_0',
              pure='Unknown', netapp='Unknown', ibm_t='AMP_2_0', spd=32, cfg=cfg_fixed,
              gen=6, z=False, eos=1572526799.0),
    173: dict(brcd='G630', ibm='SAN128B-6', hpe='SN6650B', dell='DS-6630', hv='G630',
              pure='G630', netapp='Unknown', ibm_t='8960-F128/N64', spd=32, cfg=cfg_fixed,
              gen=6, z=False, eos=None),
    178: dict(brcd='7810', ibm='SAN18B-6', hpe='SN2600B', dell='MP-7810B', hv='7810',
              pure='7810', netapp='Unknown', ibm_t='8960-R18', spd=32, cfg=cfg_fixed,
              gen=7, z=False, eos=None),
    179: dict(brcd='X7-4', ibm='SAN256B-7', hpe='SN8700B-4', dell='ED-DCX7-4B', hv='X7-4',
              pure='X7-4', netapp='Unknown', ibm_t='8960-F128/N64', spd=64, cfg=cfg_4_slot,
              gen=7, z=True, eos=None),
    180: dict(brcd='X7-8', ibm='SAN512B-7', hpe='SN8700B-8', dell='ED-DCX7-8B', hv='X7-8',
              pure='X7-8', netapp='Unknown', ibm_t='8961-F78', spd=64, cfg=cfg_8_slot,
              gen=7, z=True, eos=None),
    181: dict(brcd='G720', ibm='SAN64B-7', hpe='SN6700B', dell='DS-7720', hv='HD-720',
              pure='G720', netapp='Unknown', ibm_t='8960-R64/P64', spd=64, cfg=cfg_fixed,
              gen=7, z=True, eos=None),
    183: dict(brcd='G620', ibm='SAN64B-6', hpe='SN6600B', dell='DS-6620', hv='HD-620',
              pure='G620', netapp='Unknown', ibm_t='8960-F64/N64', spd=32, cfg=cfg_fixed,
              gen=6, z=True, eos=None),
    184: dict(brcd='G630', ibm='SAN64B-6', hpe='SN6650B', dell='DS-6630', hv='HD-630',
              pure='G630', netapp='Unknown', ibm_t='8960-F64/N64', spd=32, cfg=cfg_fixed,
              gen=6, z=False, eos=None),
    189: dict(brcd='G730', ibm='SAN128B-7', hpe='SN6700B', dell='DS-7730', hv='HD-730',
              pure='G730', netapp='Unknown', ibm_t='8960-R64/P64', spd=64, cfg=cfg_fixed,
              gen=7, z=False, eos=None),
    190: dict(brcd='7850', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=64, cfg=cfg_fixed,
              gen=7, z=True, eos=None),
    191: dict(brcd='G710', ibm='Unknown', hpe='Unknown', dell='Unknown', hv='Unknown',
              pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=64, cfg=cfg_fixed,
              gen=7, z=False, eos=None),
    1000: dict(brcd='VDX8770-4', ibm='Unknown', hpe='VDX8770-4', dell='VDX8770-4', hv='VDX8770-4',
               pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
               gen=0, z=True, eos=1399694399.0),
    1001: dict(brcd='VDX8770-8', ibm='Unknown', hpe='VDX8770-8', dell='VDX8770-8', hv='VDX8770-8',
               pure='Unknown', netapp='Unknown', ibm_t='Unknown', spd=0, cfg=cfg_fixed,
               gen=0, z=True, eos=1399694399.0),
}


def _chassis_type(chassis_obj):
    """Returns the switch type ID. This is an integer. See key into chassis_type_d

    :param chassis_obj: Chassis Object
    :type chassis_obj: brcddb_classes.chassis.ChassisObj
    :return: Chassis type. 0 if unknown
    :rtype: int
    """
    global chassis_type_d

    if chassis_obj is not None:
        for switch_obj in chassis_obj.r_switch_objects():  # Chassis type is embedded with the switch data
            switch_type = switch_obj.c_switch_model()
            if isinstance(switch_type, int):
                return switch_type if switch_type in chassis_type_d else 0
    return 0


def blade_name(blade_id):
    """Converts the brocade-fru/blade/blade-id number to a user friendly blade type

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
    buf = chassis_obj.r_get(brcdapi_util.bc_user_name)
    return chassis_obj.r_obj_key() if buf is None else buf + ' (' + chassis_obj.r_obj_key() + ')' if wwn else buf


def chassis_type(chassis_obj, type_num=False, oem='brcd'):
    """Returns the chassis type by brand name (ie: G720).

    Notes:

    'brocade-chassis/chassis/product-name', was introduced in 9.1. It returns the product name. Previously, in
    FOS 8.x, OEM product names were supported. I don't recall any formal announcement about support for vendor, OEM,
    names being dropped, but I haven't seen vendor names displayed in quite some time. I'm assuming this is why
    'brocade-chassis/chassis' doesn't contain something like 'vendor-product-name'. In case it was an omission in FOS
    9.1 and 9.2, I try 'brocade-chassis/chassis/vendor-product-name' first. If it's not present, I just return the
    Brocade product name, 'brocade-chassis/chassis/product-name'. This means the oem parameter is ignored in FOS 9.1
    and above. Furthermore, it means that until 'brocade-chassis/chassis/vendor-product-name' is introduced in FOS 9.1,
    vendor product names are unavailable.

    Brocade branding is always uppercase. The FOS API, however, returns the Brocade brand name in lowercase. The
    Brocade brand name therefore is always converted to uppercase. I'm not certain that OEMs always use uppercase, so I
    don't change it. I'm assuming that if a vendor product name is introduced in future versions of FOS, it will be with
    the correct case.

    :param chassis_obj: Chassis Object
    :type chassis_obj: brcddb_classes.chassis.ChassisObj
    :param type_num: If True, append (type number) to the chassis name
    :type type_num: bool
    :param oem: 'brcd', 'ibm', 'hpe', 'dell', 'hv', 'netapp', or 'pure'. See notes in function description.
    :type oem: str
    :return: Chassis type in upper case unless unknown in which just 'U' is uppercase, 'Unknown'
    :rtype: str
    """
    global chassis_type_d

    type_str = ' (' + str(_chassis_type(chassis_obj)) + ')' if type_num else ''
    try:  # See notes in function description.
        brand_name = chassis_obj.r_get(brcdapi_util.bc_product_name).upper()
    except (TypeError, AttributeError):  # Try getting the name from the chassis ID which has been in FOS since 8.2
        try:
            brand_name = chassis_type_d.get(_chassis_type(chassis_obj))[oem.lower()]
        except KeyError:
            brcdapi_log.exception('Invalid oem parameter. Type: ' + str(type(oem)) + ', Value: ' + str(oem), echo=True)
            brand_name = chassis_type_d.get(_chassis_type(chassis_obj))['brcd']

    return brand_name + type_str


def eos_epoch(obj):
    """Returns the End of Support (EOS) date in epoch time

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: EOS date in epoch time. None if EOS not yet announced.
    :rtype: int, None
    """
    return chassis_type_d[_chassis_type(obj.r_chassis_obj())]['eos']


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


def eos(obj):
    """Returns the End of Support (EOS) date in human-readable format

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: EOS_date
    :rtype: str
    """
    epoch_eos = eos_epoch(obj)
    return 'EOS not announced' if epoch_eos is None else time.strftime('%Y-%m-%d', epoch_eos)


def gen(obj):
    """Returns the gen type as an integer

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: Generation
    :rtype: int
    """
    return chassis_type_d[_chassis_type(obj.r_chassis_obj())]['gen']


def slots(obj):
    """Returns the number of slots for a switch or chassis

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: Num slots
    :rtype: int
    """
    cfg = chassis_type_d[_chassis_type(obj.r_chassis_obj())]['cfg']
    return 4 if cfg == cfg_4_slot else 8 if cfg == cfg_8_slot else 0


def ibm_machine_type(obj):
    """Returns the IBM machine type for the switch

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: machine_type
    :rtype: str
    """
    return chassis_type_d[_chassis_type(obj.r_chassis_obj())]['ibm_t']


def sys_z_supported(obj):
    """Returns True if z systems supported

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: True if z Systems supported
    :rtype: bool
    """
    return chassis_type_d[_chassis_type(obj.r_chassis_obj())]['z']


def chassis_speed(obj):
    """Converts the switch type number to the max speed the switch is capable of as an int in Gbps

    :param obj: Chassis or switch object
    :type obj: brcddb.class.chassis.ChassisObj, brcddb.class.switch.SwitchObj
    :return: Maximum speed switch is capable of
    :rtype: int
    """
    return chassis_type_d[_chassis_type(obj.r_chassis_obj())]['spd']
