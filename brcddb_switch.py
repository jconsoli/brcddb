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
:mod:`brcddb.brcddb_switch` - Methods and tables to support the class SwitchObj.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '19 Jul 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import brcdapi.log as brcdapi_log
import brcddb.util.copy as brcddb_copy
import brcddb.util.util as brcddb_util
import brcddb.app_data.alert_tables as al
import brcddb.brcddb_login as brcddb_login
import brcddb.brcddb_common as brcddb_common

# This is <model> in switch/fibrechannel-switch. Note that it is returned as a string (str) representing a floating
# point numbers. Anything after the decimal point represents a version change. Only the integer portion is useful for
# determing a switch type. Switch types used herein are the integer portion only so your code should do something like:
# switch_type = int(float( <model> returned from switch/fibrechannel-switch))
class SWITCH_TYPE:
    UNKNOWN     =   0
    S_1000		=	1
    S_2800		=	2
    S_2100_2400	=	3
    S_20x0		=	4
    S_22x0		=	5
    S_2800		=	6
    S_2000		=	7
    S_3800		=	9
    S_12000		=	10
    S_3900		=	12
    S_3200		=	16
    S_3800VL	=	17
    S_3000		=	18
    S_24000		=	21
    S_3016		=	22
    S_3850		=	26
    S_3250		=	27
    S_4012		=	29
    S_4100		=	32
    S_3014		=	33
    S_200E		=	34
    S_4020		=	37
    S_7420		=	38
    S_FCR_Front	=	40
    S_FCR_Xlate	=	41
    S_48000		=	42
    S_4024		=	43
    S_4900		=	44
    S_4016		=	45
    S_7500		=	46
    S_4018		=	51
    S_7600		=	55
    S_5000		=	58
    S_DCX		=	62
    S_5300		=	64
    S_5100		=	66
    S_Encryp	=	67
    S_5410		=	69
    S_300		=	71
    S_5480		=	72
    S_5470		=	73
    S_5424		=	75
    S_8000		=	76
    S_DCX_4S	=	77
    S_7800		=	83
    S_5450		=	86
    S_5460		=	87
    S_8470		=	90
    S_VA_40FC	=	92
    S_6720_24	=	95
    S_6730_32	=	96
    S_6720_60	=	97
    S_6730_76	=	98
    S_M8428		=	108
    S_6510		=	109
    S_6746		=	112
    S_6710		=	116
    S_6547		=	117
    S_6505		=	118
    S_8510_8	=	120
    S_8510_4	=	121
    S_5430		=	124
    S_5431		=	125
    S_6548		=	129
    S_6505		=	130
    S_6740		=	131
    S_6520		=	133
    S_5432		=	134
    S_6746		=	138
    S_7840		=	148
    S_6740T_1G	=	151
    S_6940T_1G	=	153
    S_G610		=	170
    S_G620		=	162
    S_G630		=	173
    S_X6_4		=	165
    S_X6_8		=	166
    S_AMP_2_0	=	171
    S_7810      =   178
    S_8770_4	=	1000
    S_8770_8	=	1001

class SWITCH_BRAND:  # The custom index in FOS. Not yet implemented in the API as of 8.2.1b
	Brocade			=	0
	IBM				=	1
	HPE				=	2
	EMC				=	3
	HDS				=	4

st_name = {
    SWITCH_TYPE.UNKNOWN: {
        SWITCH_BRAND.Brocade : 'Unknown',
        SWITCH_BRAND.IBM : 'Unknown',
        SWITCH_BRAND.HPE : 'Unknown',
        SWITCH_BRAND.EMC : 'Unknown',
        SWITCH_BRAND.HDS : 'Unknown'},
    SWITCH_TYPE.S_1000 		: {
        SWITCH_BRAND.Brocade : '1000',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '1000',
        SWITCH_BRAND.EMC : '1000',
        SWITCH_BRAND.HDS : '1000'},
    SWITCH_TYPE.S_2800 		: {
        SWITCH_BRAND.Brocade : '2800',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '2800',
        SWITCH_BRAND.EMC : 'DS-16B',
        SWITCH_BRAND.HDS : '2800'},
    SWITCH_TYPE.S_2100_2400 : {
        SWITCH_BRAND.Brocade : '2100/2400',
        SWITCH_BRAND.IBM : 'S08',
        SWITCH_BRAND.HPE : '2100/2400',
        SWITCH_BRAND.EMC : 'DS-8B',
        SWITCH_BRAND.HDS : '2100/2400'},
    SWITCH_TYPE.S_20x0 		: {
        SWITCH_BRAND.Brocade : '20x0',
        SWITCH_BRAND.IBM : 'Managed Hub',
        SWITCH_BRAND.HPE : '20x0',
        SWITCH_BRAND.EMC : '20x0',
        SWITCH_BRAND.HDS : '20x0'},
    SWITCH_TYPE.S_22x0 		: {
        SWITCH_BRAND.Brocade : '22x0',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '22x0',
        SWITCH_BRAND.EMC : '22x0',
        SWITCH_BRAND.HDS : '22x0'},
    SWITCH_TYPE.S_2800 		: {
        SWITCH_BRAND.Brocade : '2800',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '2800',
        SWITCH_BRAND.EMC : 'DS-16b',
        SWITCH_BRAND.HDS : '2800'},
    SWITCH_TYPE.S_2000 		: {
        SWITCH_BRAND.Brocade : '2000',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '2000',
        SWITCH_BRAND.EMC : 'DS-SCB',
        SWITCH_BRAND.HDS : '2000'},
    SWITCH_TYPE.S_3800 		: {
        SWITCH_BRAND.Brocade : '3800',
        SWITCH_BRAND.IBM : 'F16',
        SWITCH_BRAND.HPE : '3800',
        SWITCH_BRAND.EMC : 'DS-16B2',
        SWITCH_BRAND.HDS : '3800'},
    SWITCH_TYPE.S_12000		: {
        SWITCH_BRAND.Brocade : '12000',
        SWITCH_BRAND.IBM : 'M12',
        SWITCH_BRAND.HPE : 'StorageWorks 2/64',
        SWITCH_BRAND.EMC : 'ED-12000B',
        SWITCH_BRAND.HDS : '12000'},
    SWITCH_TYPE.S_3900 		: {
        SWITCH_BRAND.Brocade : '3900',
        SWITCH_BRAND.IBM : 'F32',
        SWITCH_BRAND.HPE : 'StorageWorks 2/32',
        SWITCH_BRAND.EMC : 'DS-8B2',
        SWITCH_BRAND.HDS : '3900'},
    SWITCH_TYPE.S_3200 		: {
        SWITCH_BRAND.Brocade : '3200',
        SWITCH_BRAND.IBM : 'F08',
        SWITCH_BRAND.HPE : 'StorageWorks 2/8-EL',
        SWITCH_BRAND.EMC : '1000',
        SWITCH_BRAND.HDS : '3200'},
    SWITCH_TYPE.S_3800VL	: {
        SWITCH_BRAND.Brocade : '3800VL',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'StorageWorks 3800VL',
        SWITCH_BRAND.EMC : '3800VL',
        SWITCH_BRAND.HDS : '3800VL'},
    SWITCH_TYPE.S_3000 		: {
        SWITCH_BRAND.Brocade : '3000',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '3000',
        SWITCH_BRAND.EMC : '3000',
        SWITCH_BRAND.HDS : '3000'},
    SWITCH_TYPE.S_24000 	: {
        SWITCH_BRAND.Brocade : '24000',
        SWITCH_BRAND.IBM : 'M14',
        SWITCH_BRAND.HPE : 'StorageWorks 2/128',
        SWITCH_BRAND.EMC : 'ED-24000B',
        SWITCH_BRAND.HDS : '24000'},
    SWITCH_TYPE.S_3016 		: {
        SWITCH_BRAND.Brocade : '3016',
        SWITCH_BRAND.IBM : '2G Entry SAN Switch Module',
        SWITCH_BRAND.HPE : '24000',
        SWITCH_BRAND.EMC : '24000',
        SWITCH_BRAND.HDS : '24000'},
    SWITCH_TYPE.S_3850 		: {
        SWITCH_BRAND.Brocade : '3850',
        SWITCH_BRAND.IBM : 'H16',
        SWITCH_BRAND.HPE : 'StorageWorks 2/16V',
        SWITCH_BRAND.EMC : 'DS-16B3',
        SWITCH_BRAND.HDS : '1000'},
    SWITCH_TYPE.S_3250 		: {
        SWITCH_BRAND.Brocade : '3250',
        SWITCH_BRAND.IBM : 'H08',
        SWITCH_BRAND.HPE : 'StorageWorks 2/8V',
        SWITCH_BRAND.EMC : '3250',
        SWITCH_BRAND.HDS : '3250'},
    SWITCH_TYPE.S_4012 		: {
        SWITCH_BRAND.Brocade : '4012',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'bladeSystem 4Gb SAN switch',
        SWITCH_BRAND.EMC : '4012',
        SWITCH_BRAND.HDS : '4012'},
    SWITCH_TYPE.S_4100 		: {
        SWITCH_BRAND.Brocade : '4100',
        SWITCH_BRAND.IBM : 'SAN16B-2',
        SWITCH_BRAND.HPE : 'StorageWorks 4/32',
        SWITCH_BRAND.EMC : 'DS-4100B',
        SWITCH_BRAND.HDS : '4100'},
    SWITCH_TYPE.S_3014 		: {
        SWITCH_BRAND.Brocade : '3014',
        SWITCH_BRAND.IBM : '3014',
        SWITCH_BRAND.HPE : '3014',
        SWITCH_BRAND.EMC : '3014',
        SWITCH_BRAND.HDS : '3014'},
    SWITCH_TYPE.S_200E 		: {
        SWITCH_BRAND.Brocade : '200E',
        SWITCH_BRAND.IBM : 'SAN16B-2',
        SWITCH_BRAND.HPE : 'StorageWorks 4/8 or 4/16',
        SWITCH_BRAND.EMC : 'DS-220B',
        SWITCH_BRAND.HDS : '200E'},
    SWITCH_TYPE.S_4020 		: {
        SWITCH_BRAND.Brocade : '4020',
        SWITCH_BRAND.IBM : '4Gb SAN Switch Module',
        SWITCH_BRAND.HPE : '4020',
        SWITCH_BRAND.EMC : '4020',
        SWITCH_BRAND.HDS : '4020'},
    SWITCH_TYPE.S_7420 		: {
        SWITCH_BRAND.Brocade : '7420',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'StorageWorks 200',
        SWITCH_BRAND.EMC : '7420',
        SWITCH_BRAND.HDS : '7420'},
    SWITCH_TYPE.S_FCR_Front	: {
        SWITCH_BRAND.Brocade : 'FCR Front Domain',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'FCR Front Domain',
        SWITCH_BRAND.EMC : 'FCR Front Domain',
        SWITCH_BRAND.HDS : 'FCR Front Domain'},
    SWITCH_TYPE.S_FCR_Xlate	: {
        SWITCH_BRAND.Brocade : 'FCR Xlate Domain',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'FCR Xlate Domain',
        SWITCH_BRAND.EMC : 'FCR Xlate Domain',
        SWITCH_BRAND.HDS : 'FCR Xlate Domain'},
    SWITCH_TYPE.S_48000 	: {
        SWITCH_BRAND.Brocade : '48000',
        SWITCH_BRAND.IBM : 'SAN256B',
        SWITCH_BRAND.HPE : 'StorageWorks 4/256',
        SWITCH_BRAND.EMC : 'ED-48000B',
        SWITCH_BRAND.HDS : '48000'},
    SWITCH_TYPE.S_4024 		: {
        SWITCH_BRAND.Brocade : '4024',
        SWITCH_BRAND.IBM : '4024',
        SWITCH_BRAND.HPE : 'bladeSystem 4Gb SAN switch',
        SWITCH_BRAND.EMC : '4024',
        SWITCH_BRAND.HDS : '4024'},
    SWITCH_TYPE.S_4900 		: {
        SWITCH_BRAND.Brocade : '4900',
        SWITCH_BRAND.IBM : 'SAN64B-2',
        SWITCH_BRAND.HPE : '4/64',
        SWITCH_BRAND.EMC : 'DS-4900B',
        SWITCH_BRAND.HDS : '4900'},
    SWITCH_TYPE.S_4016 		: {
        SWITCH_BRAND.Brocade : '4016',
        SWITCH_BRAND.IBM : '4016',
        SWITCH_BRAND.HPE : '4016',
        SWITCH_BRAND.EMC : '4016',
        SWITCH_BRAND.HDS : '4016'},
    SWITCH_TYPE.S_7500 		: {
        SWITCH_BRAND.Brocade : '7500',
        SWITCH_BRAND.IBM : '2005-R18',
        SWITCH_BRAND.HPE : 'StorageWorks 400',
        SWITCH_BRAND.EMC : 'MP-7500B',
        SWITCH_BRAND.HDS : '7500'},
    SWITCH_TYPE.S_4018 		: {
        SWITCH_BRAND.Brocade : '4018',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '4018',
        SWITCH_BRAND.EMC : '4018',
        SWITCH_BRAND.HDS : '4018'},
    SWITCH_TYPE.S_4018 		: {
        SWITCH_BRAND.Brocade : '7600',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '7600',
        SWITCH_BRAND.EMC : '7600',
        SWITCH_BRAND.HDS : '7600'},
    SWITCH_TYPE.S_5000 		: {
        SWITCH_BRAND.Brocade : '5000',
        SWITCH_BRAND.IBM : '2005-B5K',
        SWITCH_BRAND.HPE : 'StorageWorks 4/32B',
        SWITCH_BRAND.EMC : 'DS-5000B',
        SWITCH_BRAND.HDS : '5000'},
    SWITCH_TYPE.S_DCX 		: {
        SWITCH_BRAND.Brocade : 'DCX',
        SWITCH_BRAND.IBM : 'SAN768B',
        SWITCH_BRAND.HPE : 'StorageWorks DC SAN backbone director',
        SWITCH_BRAND.EMC : 'ED-DCX-B',
        SWITCH_BRAND.HDS : 'DCX'},
    SWITCH_TYPE.S_5300 		: {
        SWITCH_BRAND.Brocade : '5300',
        SWITCH_BRAND.IBM : 'SAN80B-4',
        SWITCH_BRAND.HPE : 'StorageWorks 8/80',
        SWITCH_BRAND.EMC : 'DS-5300B',
        SWITCH_BRAND.HDS : '5300'},
    SWITCH_TYPE.S_5100 		: {
        SWITCH_BRAND.Brocade : '5100',
        SWITCH_BRAND.IBM : 'SAN40B-4',
        SWITCH_BRAND.HPE : 'StorageWorks 8/40',
        SWITCH_BRAND.EMC : 'DS-5100B',
        SWITCH_BRAND.HDS : '10051000'},
    SWITCH_TYPE.S_Encryp	: {
        SWITCH_BRAND.Brocade : 'Encryption',
        SWITCH_BRAND.IBM : 'SAN32B-E4',
        SWITCH_BRAND.HPE : 'AR944A',
        SWITCH_BRAND.EMC : 'ES-5832B',
        SWITCH_BRAND.HDS : 'Encryption'},
    SWITCH_TYPE.S_5410 		: {
        SWITCH_BRAND.Brocade : '5410',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'EVA 4400',
        SWITCH_BRAND.EMC : '5410',
        SWITCH_BRAND.HDS : '5410'},
    SWITCH_TYPE.S_300 		: {
        SWITCH_BRAND.Brocade : '300',
        SWITCH_BRAND.IBM : 'SAN24B-4',
        SWITCH_BRAND.HPE : 'StorageWorks 8/24',
        SWITCH_BRAND.EMC : 'DS-300B',
        SWITCH_BRAND.HDS : '300'},
    SWITCH_TYPE.S_5480 		: {
        SWITCH_BRAND.Brocade : 'S_5480',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '8Gb SAN module for HP bladeSystem',
        SWITCH_BRAND.EMC : '5480',
        SWITCH_BRAND.HDS : '5480'},
    SWITCH_TYPE.S_5470 		: {
        SWITCH_BRAND.Brocade : '5470',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5470',
        SWITCH_BRAND.EMC : '5470',
        SWITCH_BRAND.HDS : '5470'},
    SWITCH_TYPE.S_5424 		: {
        SWITCH_BRAND.Brocade : '5424',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5424',
        SWITCH_BRAND.EMC : '5424',
        SWITCH_BRAND.HDS : '5424'},
    SWITCH_TYPE.S_8000 		: {
        SWITCH_BRAND.Brocade : '8000',
        SWITCH_BRAND.IBM : 'Converged Switch L32',
        SWITCH_BRAND.HPE : 'StorageWorks FC over ethernet',
        SWITCH_BRAND.EMC : 'MP-8000B',
        SWITCH_BRAND.HDS : '8000'},
    SWITCH_TYPE.S_DCX_4S	: {
        SWITCH_BRAND.Brocade : 'DCX-4S',
        SWITCH_BRAND.IBM : 'SAN384B',
        SWITCH_BRAND.HPE : 'StorageWorks DC04 SAN director',
        SWITCH_BRAND.EMC : 'ED-DCX-4S-B',
        SWITCH_BRAND.HDS : 'DCX-4S'},
    SWITCH_TYPE.S_7800 		: {
        SWITCH_BRAND.Brocade : '7800',
        SWITCH_BRAND.IBM : 'SAN06B-R',
        SWITCH_BRAND.HPE : '1606',
        SWITCH_BRAND.EMC : 'MP-7800B',
        SWITCH_BRAND.HDS : '7800'},
    SWITCH_TYPE.S_5450 		: {
        SWITCH_BRAND.Brocade : '5450',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5450',
        SWITCH_BRAND.EMC : '5450',
        SWITCH_BRAND.HDS : '5450'},
    SWITCH_TYPE.S_5460 		: {
        SWITCH_BRAND.Brocade : '5460',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5460',
        SWITCH_BRAND.EMC : '5460',
        SWITCH_BRAND.HDS : '5460'},
    SWITCH_TYPE.S_8470 		: {
        SWITCH_BRAND.Brocade : '8470',
        SWITCH_BRAND.IBM : 'Converged 10GbE Switch Module',
        SWITCH_BRAND.HPE : '8470',
        SWITCH_BRAND.EMC : '8470',
        SWITCH_BRAND.HDS : '8470'},
    SWITCH_TYPE.S_VA_40FC	: {
        SWITCH_BRAND.Brocade : 'VA-40FC',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VA-40FC',
        SWITCH_BRAND.EMC : 'VA-40FC',
        SWITCH_BRAND.HDS : 'VA-40FC'},
    SWITCH_TYPE.S_6720_24	: {
        SWITCH_BRAND.Brocade : 'VDX 6720-24',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VDX 6720-24',
        SWITCH_BRAND.EMC : 'VDX 6720-24',
        SWITCH_BRAND.HDS : 'VDX 6720-24'},
    SWITCH_TYPE.S_6730_32	: {
        SWITCH_BRAND.Brocade : 'VDX 6730-32',
        SWITCH_BRAND.IBM : 'VDX 6730-32',
        SWITCH_BRAND.HPE : 'VDX 6730-32',
        SWITCH_BRAND.EMC : 'VDX 6730-32',
        SWITCH_BRAND.HDS : 'VDX 6730-32'},
    SWITCH_TYPE.S_6720_60	: {
        SWITCH_BRAND.Brocade : 'VDX 6720-60',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VDX 6720-60',
        SWITCH_BRAND.EMC : 'VDX 6720-60',
        SWITCH_BRAND.HDS : 'VDX 6720-60'},
    SWITCH_TYPE.S_6730_76	: {
        SWITCH_BRAND.Brocade : 'VDX 6730-76',
        SWITCH_BRAND.IBM : 'VDX 6730-76',
        SWITCH_BRAND.HPE : 'VDX 6730-76',
        SWITCH_BRAND.EMC : 'VDX 6730-76',
        SWITCH_BRAND.HDS : 'VDX 6730-76'},
    SWITCH_TYPE.S_M8428		: {
        SWITCH_BRAND.Brocade : 'M8428-k FCoE',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'M8428-k FCoE',
        SWITCH_BRAND.EMC : 'M8428-k FCoE',
        SWITCH_BRAND.HDS : 'M8428-k FCoE'},
    SWITCH_TYPE.S_6510 		: {
        SWITCH_BRAND.Brocade : '6510',
        SWITCH_BRAND.IBM : 'SAN48B-5',
        SWITCH_BRAND.HPE : 'SN6000B',
        SWITCH_BRAND.EMC : 'DS-6510B'
        ,SWITCH_BRAND.HDS : '6510'},
    SWITCH_TYPE.S_6746 		: {
        SWITCH_BRAND.Brocade : 'VDX 6746',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '100VDX 67460',
        SWITCH_BRAND.EMC : 'VDX 6746',
        SWITCH_BRAND.HDS : 'VDX 6746'},
    SWITCH_TYPE.S_6710 		: {
        SWITCH_BRAND.Brocade : 'VDX 6710',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VDX 6710',
        SWITCH_BRAND.EMC : 'VDX 6710',
        SWITCH_BRAND.HDS : 'VDX 6710'},
    SWITCH_TYPE.S_6547 		: {
        SWITCH_BRAND.Brocade : '6547',
        SWITCH_BRAND.IBM : 'FC5022 SAN Switch',
        SWITCH_BRAND.HPE : '6547',
        SWITCH_BRAND.EMC : '6547',
        SWITCH_BRAND.HDS : '6547'},
    SWITCH_TYPE.S_6505 		: {
        SWITCH_BRAND.Brocade : '6505',
        SWITCH_BRAND.IBM : 'SAN24B-5',
        SWITCH_BRAND.HPE : '6505',
        SWITCH_BRAND.EMC : 'DS-6505B',
        SWITCH_BRAND.HDS : '6505'},
    SWITCH_TYPE.S_8510_8	: {
        SWITCH_BRAND.Brocade : 'DCX8510-8',
        SWITCH_BRAND.IBM : 'SAN768B-2',
        SWITCH_BRAND.HPE : 'SN8000B 8-slot',
        SWITCH_BRAND.EMC : 'ED-DCX8510-8B',
        SWITCH_BRAND.HDS : 'DCX8510-8'},
    SWITCH_TYPE.S_8510_4	: {
        SWITCH_BRAND.Brocade : 'DCX8510-4',
        SWITCH_BRAND.IBM : 'SAN384B-2',
        SWITCH_BRAND.HPE : 'SN8000B 4-slot',
        SWITCH_BRAND.EMC : '1ED-DCX8510-4B000',
        SWITCH_BRAND.HDS : 'DCX8510-4'},
    SWITCH_TYPE.S_5430 		: {
        SWITCH_BRAND.Brocade : '5430',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5430',
        SWITCH_BRAND.EMC : '5430',
        SWITCH_BRAND.HDS : '5430'},
    SWITCH_TYPE.S_5431 		: {
        SWITCH_BRAND.Brocade : '5431',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5431',
        SWITCH_BRAND.EMC : '5431',
        SWITCH_BRAND.HDS : '5431'},
    SWITCH_TYPE.S_6548 		: {
        SWITCH_BRAND.Brocade : '6548',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '16Gb SAN switch for HP BladeSystem',
        SWITCH_BRAND.EMC : '6548',
        SWITCH_BRAND.HDS : '6548'},
    SWITCH_TYPE.S_6505 		: {
        SWITCH_BRAND.Brocade : 'M6505',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'M6505',
        SWITCH_BRAND.EMC : 'M6505',
        SWITCH_BRAND.HDS : 'M6505'},
    SWITCH_TYPE.S_6520 		: {
        SWITCH_BRAND.Brocade : '6520',
        SWITCH_BRAND.IBM : 'SAN96B-5',
        SWITCH_BRAND.HPE : 'SN6500B',
        SWITCH_BRAND.EMC : 'DS-6520B',
        SWITCH_BRAND.HDS : '6520'},
    SWITCH_TYPE.S_5432 		: {
        SWITCH_BRAND.Brocade : '5432',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '5432',
        SWITCH_BRAND.EMC : '5432',
        SWITCH_BRAND.HDS : '5432'},
    SWITCH_TYPE.S_6746 		: {
        SWITCH_BRAND.Brocade : 'VDX 6746',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '',
        SWITCH_BRAND.EMC : '',
        SWITCH_BRAND.HDS : ''},
    SWITCH_TYPE.S_7840 		: {
        SWITCH_BRAND.Brocade : '7840',
        SWITCH_BRAND.IBM : 'SAN42B-R',
        SWITCH_BRAND.HPE : '7840',
        SWITCH_BRAND.EMC : 'MP-7840B',
        SWITCH_BRAND.HDS : '7840'},
    SWITCH_TYPE.S_6740T_1G	: {
        SWITCH_BRAND.Brocade : 'VDX 6740T-1G',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '',
        SWITCH_BRAND.EMC : '',
        SWITCH_BRAND.HDS : ''},
    SWITCH_TYPE.S_6940T_1G	: {
        SWITCH_BRAND.Brocade : 'VDX 6940T-1G',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '',
        SWITCH_BRAND.EMC : '',
        SWITCH_BRAND.HDS : ''},
    SWITCH_TYPE.S_G610 		: {
        SWITCH_BRAND.Brocade : 'G610',
        SWITCH_BRAND.IBM : 'SAN24B-6',
        SWITCH_BRAND.HPE : 'SN3600B',
        SWITCH_BRAND.EMC : 'DS-6610B'
        ,SWITCH_BRAND.HDS : 'G610'},
    SWITCH_TYPE.S_G620 		: {
        SWITCH_BRAND.Brocade : 'G620',
        SWITCH_BRAND.IBM : 'SAN64B-6',
        SWITCH_BRAND.HPE : 'SN6600B',
        SWITCH_BRAND.EMC : 'DS-6620',
        SWITCH_BRAND.HDS : 'G620'},
    SWITCH_TYPE.S_G630 		: {
        SWITCH_BRAND.Brocade : 'G630',
        SWITCH_BRAND.IBM : 'SAN96B-6',
        SWITCH_BRAND.HPE : 'SN6650B',
        SWITCH_BRAND.EMC : 'G630',
        SWITCH_BRAND.HDS : 'G630'},
    SWITCH_TYPE.S_X6_8 		: {
        SWITCH_BRAND.Brocade : 'X6-8',
        SWITCH_BRAND.IBM : 'SAN512B-6',
        SWITCH_BRAND.HPE : 'SN8600B 8-Slot',
        SWITCH_BRAND.EMC : 'ED-DCX6-8B',
        SWITCH_BRAND.HDS : 'X6-8'},
    SWITCH_TYPE.S_X6_4 		: {
        SWITCH_BRAND.Brocade : 'X6-4',
        SWITCH_BRAND.IBM : 'SAN256B-6',
        SWITCH_BRAND.HPE : 'SN8600B 4-Slot',
        SWITCH_BRAND.EMC : 'ED-DCX6-4B',
        SWITCH_BRAND.HDS : 'X6-4'},
    SWITCH_TYPE.S_AMP_2_0 	: {
        SWITCH_BRAND.Brocade : 'AMP_2_0',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : '',
        SWITCH_BRAND.EMC : '',
        SWITCH_BRAND.HDS : ''},
    SWITCH_TYPE.S_7810 		: {
        SWITCH_BRAND.Brocade : '7810',
        SWITCH_BRAND.IBM : 'Unknwon',
        SWITCH_BRAND.HPE : '7810',
        SWITCH_BRAND.EMC : 'MP-7810B',
        SWITCH_BRAND.HDS : '7810'},
    SWITCH_TYPE.S_8770_4	: {
        SWITCH_BRAND.Brocade : 'VDX 8770-4',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VDX 8770-4',
        SWITCH_BRAND.EMC : 'VDX 8770-4',
        SWITCH_BRAND.HDS : 'VDX 8770-4'},
    SWITCH_TYPE.S_8770_8	: {
        SWITCH_BRAND.Brocade : 'VDX 8770-8',
        SWITCH_BRAND.IBM : '',
        SWITCH_BRAND.HPE : 'VDX 8770-8',
        SWITCH_BRAND.EMC : 'VDX 8770-8',
        SWITCH_BRAND.HDS : 'VDX 8770-8'},
}

st_type = {
    SWITCH_TYPE.S_2800		:	'2109-S08',
    SWITCH_TYPE.S_20x0		:	'3534-1RU',
    SWITCH_TYPE.S_3800		:	'2109-F16',
    SWITCH_TYPE.S_12000		:	'2109-M12',
    SWITCH_TYPE.S_3900		:	'2109-F32',
    SWITCH_TYPE.S_3200		:	'3534-F08',
    SWITCH_TYPE.S_24000		:	'2109-M14',
    SWITCH_TYPE.S_3016		:	'26K5601 / 90P0165',
    SWITCH_TYPE.S_3850		:	'2005-H16',
    SWITCH_TYPE.S_3250		:	'2005-H08',
    SWITCH_TYPE.S_4100		:	'2005-B32',
    SWITCH_TYPE.S_200E		:	'2005-B16',
    SWITCH_TYPE.S_4020		:	'32R1812',
    SWITCH_TYPE.S_48000		:	'2109-M48',
    SWITCH_TYPE.S_4900		:	'2005-B64',
    SWITCH_TYPE.S_7500		:	'2005-R18',
    SWITCH_TYPE.S_5000		:	'2005-B5K',
    SWITCH_TYPE.S_DCX		:	'2499-384',
    SWITCH_TYPE.S_5300		:	'2498-B80',
    SWITCH_TYPE.S_5100		:	'2498-B40',
    SWITCH_TYPE.S_Encryp	:	'2498-E32',
    SWITCH_TYPE.S_300		:	'2498-B24',
    SWITCH_TYPE.S_8000		:	'3758-B32',
    SWITCH_TYPE.S_DCX_4S	:	'2499-192',
    SWITCH_TYPE.S_7800		:	'2498-R06',
    SWITCH_TYPE.S_VA_40FC	:	'69Y1909',
    SWITCH_TYPE.S_6730_32	:	'3759-C32 / 8553-AF6 / 8553-AR5',
    SWITCH_TYPE.S_6730_76	:	'3759-C76 / 8553-BF8 / 8553-BR7',
    SWITCH_TYPE.S_6510		:	'2498-F48',
    SWITCH_TYPE.S_6547		:	'90Y9356 / 00Y3324 / 88Y6374',
    SWITCH_TYPE.S_6505		:	'2498-F24',
    SWITCH_TYPE.S_8510_8	:	'2499-816',
    SWITCH_TYPE.S_8510_4	:	'2499-416',
    SWITCH_TYPE.S_6520		:	'2498-F96 / N96',
    SWITCH_TYPE.S_7840		:	'2498-R42',
    SWITCH_TYPE.S_G610		:	'8960-F24/N24',
    SWITCH_TYPE.S_G620		:	'8960-F64/N64',
    SWITCH_TYPE.S_G630		:	'8960-F128/N128',
    SWITCH_TYPE.S_X6_8		:	'8961-F08',
    SWITCH_TYPE.S_X6_4		:	'8961-F04',
}


st_speed = {
    SWITCH_TYPE.S_1000			:	1,
    SWITCH_TYPE.S_2800			:	1,
    SWITCH_TYPE.S_2100_2400		:	1,
    SWITCH_TYPE.S_20x0			:	1,
    SWITCH_TYPE.S_22x0			:	1,
    SWITCH_TYPE.S_2800			:	1,
    SWITCH_TYPE.S_2000			:	1,
    SWITCH_TYPE.S_3800			:	2,
    SWITCH_TYPE.S_12000			:	2,
    SWITCH_TYPE.S_3900			:	2,
    SWITCH_TYPE.S_3200			:	2,
    SWITCH_TYPE.S_3800VL		:	2,
    SWITCH_TYPE.S_3000			:	2,
    SWITCH_TYPE.S_24000			:	2,
    SWITCH_TYPE.S_3016			:	2,
    SWITCH_TYPE.S_3850			:	2,
    SWITCH_TYPE.S_3250			:	2,
    SWITCH_TYPE.S_4012			:	2,
    SWITCH_TYPE.S_4100			:	4,
    SWITCH_TYPE.S_3014			:	4,
    SWITCH_TYPE.S_200E			:	4,
    SWITCH_TYPE.S_4020			:	4,
    SWITCH_TYPE.S_7420			:	4,
    SWITCH_TYPE.S_FCR_Front		:	4,
    SWITCH_TYPE.S_FCR_Xlate		:	4,
    SWITCH_TYPE.S_48000			:	4,
    SWITCH_TYPE.S_4024			:	4,
    SWITCH_TYPE.S_4900			:	4,
    SWITCH_TYPE.S_4016			:	4,
    SWITCH_TYPE.S_7500			:	4,
    SWITCH_TYPE.S_4018			:	4,
    SWITCH_TYPE.S_7600			:	4,
    SWITCH_TYPE.S_5000			:	4,
    SWITCH_TYPE.S_DCX			:	8,
    SWITCH_TYPE.S_5300			:	8,
    SWITCH_TYPE.S_5100			:	8,
    SWITCH_TYPE.S_Encryp		:	8,
    SWITCH_TYPE.S_5410			:	8,
    SWITCH_TYPE.S_300			:	8,
    SWITCH_TYPE.S_5480			:	8,
    SWITCH_TYPE.S_5470			:	8,
    SWITCH_TYPE.S_5424			:	8,
    SWITCH_TYPE.S_8000			:	8,
    SWITCH_TYPE.S_DCX_4S		:	8,
    SWITCH_TYPE.S_7800			:	8,
    SWITCH_TYPE.S_5450			:	8,
    SWITCH_TYPE.S_5460			:	8,
    SWITCH_TYPE.S_8470			:	8,
    SWITCH_TYPE.S_6510			:	16,
    SWITCH_TYPE.S_6547			:	16,
    SWITCH_TYPE.S_6505			:	16,
    SWITCH_TYPE.S_8510_8		:	16,
    SWITCH_TYPE.S_8510_4		:	16,
    SWITCH_TYPE.S_5430			:	8,
    SWITCH_TYPE.S_5431			:	8,
    SWITCH_TYPE.S_6548			:	16,
    SWITCH_TYPE.S_6505			:	16,
    SWITCH_TYPE.S_6520			:	16,
    SWITCH_TYPE.S_5432			:	8,
    SWITCH_TYPE.S_7840			:	16,
    SWITCH_TYPE.S_G610			:	32,
    SWITCH_TYPE.S_G620			:	32,
    SWITCH_TYPE.S_G630	        :	32,
    SWITCH_TYPE.S_X6_8			:	32,
    SWITCH_TYPE.S_X6_4			:	32,
    SWITCH_TYPE.S_7810			:	32,
    SWITCH_TYPE.S_AMP_2_0		:	32,
}

st_sys_z = {
    SWITCH_TYPE.S_1000		:	False,
    SWITCH_TYPE.S_2800		:	False,
    SWITCH_TYPE.S_2100_2400	:	False,
    SWITCH_TYPE.S_3800		:	True,
    SWITCH_TYPE.S_12000		:	True,
    SWITCH_TYPE.S_3900		:	True,
    SWITCH_TYPE.S_24000		:	True,
    SWITCH_TYPE.S_4100		:	False,
    SWITCH_TYPE.S_3014		:	False,
    SWITCH_TYPE.S_48000		:	True,
    SWITCH_TYPE.S_4900		:	False,
    SWITCH_TYPE.S_7500		:	True,
    SWITCH_TYPE.S_DCX		:	True,
    SWITCH_TYPE.S_5300		:	True,
    SWITCH_TYPE.S_5100		:	True,
    SWITCH_TYPE.S_Encryp	:	False,
    SWITCH_TYPE.S_8000		:	False,
    SWITCH_TYPE.S_DCX_4S	:	True,
    SWITCH_TYPE.S_7800		:	True,
    SWITCH_TYPE.S_6720_24	:	False,
    SWITCH_TYPE.S_6730_32	:	False,
    SWITCH_TYPE.S_6720_60	:	False,
    SWITCH_TYPE.S_6730_76	:	False,
    SWITCH_TYPE.S_6510		:	True,
    SWITCH_TYPE.S_6746		:	False,
    SWITCH_TYPE.S_6710		:	False,
    SWITCH_TYPE.S_8510_8	:	True,
    SWITCH_TYPE.S_8510_4	:	True,
    SWITCH_TYPE.S_6740		:	False,
    SWITCH_TYPE.S_6520		:	False,
    SWITCH_TYPE.S_6746		:	False,
    SWITCH_TYPE.S_7840		:	True,
    SWITCH_TYPE.S_6740T_1G	:	False,
    SWITCH_TYPE.S_6940T_1G	:	False,
    SWITCH_TYPE.S_G630		:	False,
    SWITCH_TYPE.S_X6_8		:	True,
    SWITCH_TYPE.S_X6_4		:	True,
    SWITCH_TYPE.S_AMP_2_0	:	True,
    SWITCH_TYPE.S_7810		:	False,
    SWITCH_TYPE.S_8770_4	:	False,
    SWITCH_TYPE.S_8770_8	:	False,
}

st_slots = {
    SWITCH_TYPE.S_1000		:	0,
    SWITCH_TYPE.S_2800		:	0,
    SWITCH_TYPE.S_2100_2400	:	0,
    SWITCH_TYPE.S_20x0		:	0,
    SWITCH_TYPE.S_22x0		:	0,
    SWITCH_TYPE.S_2800		:	0,
    SWITCH_TYPE.S_2000		:	0,
    SWITCH_TYPE.S_3800		:	0,
    SWITCH_TYPE.S_12000		:	8,
    SWITCH_TYPE.S_3900		:	0,
    SWITCH_TYPE.S_3200		:	0,
    SWITCH_TYPE.S_3800VL	:	0,
    SWITCH_TYPE.S_3000		:	0,
    SWITCH_TYPE.S_24000		:	8,
    SWITCH_TYPE.S_3016		:	0,
    SWITCH_TYPE.S_3850		:	0,
    SWITCH_TYPE.S_3250		:	0,
    SWITCH_TYPE.S_4012		:	0,
    SWITCH_TYPE.S_4100		:	0,
    SWITCH_TYPE.S_3014		:	0,
    SWITCH_TYPE.S_200E		:	0,
    SWITCH_TYPE.S_4020		:	0,
    SWITCH_TYPE.S_7420		:	0,
    SWITCH_TYPE.S_FCR_Front	:	0,
    SWITCH_TYPE.S_FCR_Xlate	:	0,
    SWITCH_TYPE.S_48000		:	8,
    SWITCH_TYPE.S_4024		:	0,
    SWITCH_TYPE.S_4900		:	0,
    SWITCH_TYPE.S_4016		:	0,
    SWITCH_TYPE.S_7500		:	0,
    SWITCH_TYPE.S_4018		:	0,
    SWITCH_TYPE.S_7600		:	0,
    SWITCH_TYPE.S_5000		:	0,
    SWITCH_TYPE.S_DCX		:	8,
    SWITCH_TYPE.S_5300		:	0,
    SWITCH_TYPE.S_5100		:	0,
    SWITCH_TYPE.S_Encryp	:	0,
    SWITCH_TYPE.S_5410		:	0,
    SWITCH_TYPE.S_300		:	0,
    SWITCH_TYPE.S_5480		:	0,
    SWITCH_TYPE.S_5470		:	0,
    SWITCH_TYPE.S_5424		:	0,
    SWITCH_TYPE.S_8000		:	0,
    SWITCH_TYPE.S_DCX_4S	:	4,
    SWITCH_TYPE.S_7800		:	0,
    SWITCH_TYPE.S_5450		:	0,
    SWITCH_TYPE.S_5460		:	0,
    SWITCH_TYPE.S_8470		:	0,
    SWITCH_TYPE.S_VA_40FC	:	0,
    SWITCH_TYPE.S_6720_24	:	0,
    SWITCH_TYPE.S_6730_32	:	0,
    SWITCH_TYPE.S_6720_60	:	0,
    SWITCH_TYPE.S_6730_76	:	0,
    SWITCH_TYPE.S_M8428		:	0,
    SWITCH_TYPE.S_6510		:	0,
    SWITCH_TYPE.S_6746		:	0,
    SWITCH_TYPE.S_6710		:	0,
    SWITCH_TYPE.S_6547		:	0,
    SWITCH_TYPE.S_6505		:	0,
    SWITCH_TYPE.S_8510_8	:	8,
    SWITCH_TYPE.S_8510_4	:	4,
    SWITCH_TYPE.S_5430		:	0,
    SWITCH_TYPE.S_5431		:	0,
    SWITCH_TYPE.S_6548		:	0,
    SWITCH_TYPE.S_6505		:	0,
    SWITCH_TYPE.S_6740		:	0,
    SWITCH_TYPE.S_6520		:	0,
    SWITCH_TYPE.S_5432		:	0,
    SWITCH_TYPE.S_6746		:	0,
    SWITCH_TYPE.S_7840		:	0,
    SWITCH_TYPE.S_6740T_1G	:	0,
    SWITCH_TYPE.S_6940T_1G	:	0,
    SWITCH_TYPE.S_G610		:	0,
    SWITCH_TYPE.S_G620		:	0,
    SWITCH_TYPE.S_G630		:	0,
    SWITCH_TYPE.S_X6_8		:	8,
    SWITCH_TYPE.S_X6_4		:	4,
    SWITCH_TYPE.S_AMP_2_0	:	0,
    SWITCH_TYPE.S_7810		:	0,
    SWITCH_TYPE.S_8770_4	:	8,
    SWITCH_TYPE.S_8770_8	:	8,
}

st_gen = {
    SWITCH_TYPE.S_1000		:	'1G',
    SWITCH_TYPE.S_2800		:	'1G',
    SWITCH_TYPE.S_2100_2400	:	'2G',
    SWITCH_TYPE.S_20x0		:	'1G',
    SWITCH_TYPE.S_22x0		:	'1G',
    SWITCH_TYPE.S_2800		:	'1G',
    SWITCH_TYPE.S_2000		:	'1G',
    SWITCH_TYPE.S_3800		:	'2G',
    SWITCH_TYPE.S_12000		:	'2G',
    SWITCH_TYPE.S_3900		:	'2G',
    SWITCH_TYPE.S_3200		:	'2G',
    SWITCH_TYPE.S_3800VL	:	'2G',
    SWITCH_TYPE.S_3000		:	'2G',
    SWITCH_TYPE.S_24000		:	'2G',
    SWITCH_TYPE.S_3016		:	'2G',
    SWITCH_TYPE.S_3850		:	'2G',
    SWITCH_TYPE.S_3250		:	'2G',
    SWITCH_TYPE.S_4012		:	'2G',
    SWITCH_TYPE.S_4100		:	'2G',
    SWITCH_TYPE.S_3014		:	'2G',
    SWITCH_TYPE.S_200E		:	'Gen3',
    SWITCH_TYPE.S_4020		:	'Gen3',
    SWITCH_TYPE.S_7420		:	'Gen3',
    SWITCH_TYPE.S_FCR_Front	:	'Gen3',
    SWITCH_TYPE.S_FCR_Xlate	:	'Gen3',
    SWITCH_TYPE.S_48000		:	'Gen3',
    SWITCH_TYPE.S_4024		:	'Gen3',
    SWITCH_TYPE.S_4900		:	'Gen3',
    SWITCH_TYPE.S_4016		:	'Gen3',
    SWITCH_TYPE.S_7500		:	'Gen3',
    SWITCH_TYPE.S_4018		:	'Gen3',
    SWITCH_TYPE.S_7600		:	'Gen3',
    SWITCH_TYPE.S_5000		:	'Gen3',
    SWITCH_TYPE.S_DCX		:	'Gen4',
    SWITCH_TYPE.S_5300		:	'Gen4',
    SWITCH_TYPE.S_5100		:	'Gen4',
    SWITCH_TYPE.S_Encryp	:	'Gen4',
    SWITCH_TYPE.S_5410		:	'Gen4',
    SWITCH_TYPE.S_300		:	'Gen4',
    SWITCH_TYPE.S_5480		:	'Gen4',
    SWITCH_TYPE.S_5470		:	'Gen4',
    SWITCH_TYPE.S_5424		:	'Gen4',
    SWITCH_TYPE.S_8000		:	'Gen4',
    SWITCH_TYPE.S_DCX_4S	:	'Gen5',
    SWITCH_TYPE.S_7800		:	'Gen5',
    SWITCH_TYPE.S_5450		:	'Gen4',
    SWITCH_TYPE.S_5460		:	'Gen4',
    SWITCH_TYPE.S_8470		:	'Gen4',
    SWITCH_TYPE.S_6510		:	'Gen5',
    SWITCH_TYPE.S_6547		:	'Gen5',
    SWITCH_TYPE.S_6505		:	'Gen5',
    SWITCH_TYPE.S_8510_8	:	'Gen5',
    SWITCH_TYPE.S_8510_4	:	'Gen5',
    SWITCH_TYPE.S_5430		:	'Gen4',
    SWITCH_TYPE.S_5431		:	'Gen4',
    SWITCH_TYPE.S_6548		:	'Gen4',
    SWITCH_TYPE.S_6505		:	'Gen4',
    SWITCH_TYPE.S_6520		:	'Gen5',
    SWITCH_TYPE.S_5432		:	'Gen4',
    SWITCH_TYPE.S_7840		:	'Gen5',
    SWITCH_TYPE.S_G610		:	'Gen6',
    SWITCH_TYPE.S_G620		:	'Gen6',
    SWITCH_TYPE.S_G630		:	'Gen6',
    SWITCH_TYPE.S_X6_8		:	'Gen6',
    SWITCH_TYPE.S_X6_4		:	'Gen6',
    SWITCH_TYPE.S_AMP_2_0	:	'Gen6',
    SWITCH_TYPE.S_7810	    :	'Gen6',
}

st_eos = {
    SWITCH_TYPE.S_1000		:	'1990/01/01',
    SWITCH_TYPE.S_2800		:	'2007/12/15',
    SWITCH_TYPE.S_2100_2400	:	'2007/12/15',
    SWITCH_TYPE.S_20x0		:	'1990/01/01',
    SWITCH_TYPE.S_22x0		:	'1990/01/01',
    SWITCH_TYPE.S_2800		:	'2007/12/15',
    SWITCH_TYPE.S_2000		:	'1990/01/01',
    SWITCH_TYPE.S_3800		:	'2010/04/30',
    SWITCH_TYPE.S_12000		:	'2010/03/31',
    SWITCH_TYPE.S_3900		:	'2010/08/01',
    SWITCH_TYPE.S_3200		:	'2009/12/15',
    SWITCH_TYPE.S_3800VL	:	'2010/04/30',
    SWITCH_TYPE.S_3000		:	'2013/02/02',
    SWITCH_TYPE.S_24000		:	'2011/04/28',
    SWITCH_TYPE.S_3016		:	'2011/05/22',
    SWITCH_TYPE.S_3850		:	'2011/02/28',
    SWITCH_TYPE.S_3250		:	'2011/02/28',
    SWITCH_TYPE.S_4012		:	'2013/02/28',
    SWITCH_TYPE.S_4100		:	'2012/10/31',
    SWITCH_TYPE.S_3014		:	'2011/06/30',
    SWITCH_TYPE.S_200E		:	'2014/02/28',
    SWITCH_TYPE.S_4020		:	'1990/01/01',
    SWITCH_TYPE.S_7420		:	'2012/10/31',
    SWITCH_TYPE.S_FCR_Front	:	'Current',
    SWITCH_TYPE.S_FCR_Xlate	:	'Current',
    SWITCH_TYPE.S_48000		:	'2016/02/17',
    SWITCH_TYPE.S_4024		:	'2014/09/05',
    SWITCH_TYPE.S_4900		:	'2014/02/28',
    SWITCH_TYPE.S_4016		:	'1990/01/01',
    SWITCH_TYPE.S_7500		:	'2016/08/15',
    SWITCH_TYPE.S_4018		:	'1990/01/01',
    SWITCH_TYPE.S_7600		:	'1990/01/01',
    SWITCH_TYPE.S_5000		:	'2014/02/28',
    SWITCH_TYPE.S_DCX		:	'2019/11/14',
    SWITCH_TYPE.S_5300		:	'2019/08/22',
    SWITCH_TYPE.S_5100		:	'2018/06/14',
    SWITCH_TYPE.S_Encryp	:	'2019/12/31',
    SWITCH_TYPE.S_5410		:	'1990/01/01',
    SWITCH_TYPE.S_300		:	'2019/08/22',
    SWITCH_TYPE.S_5480		:	'Current',
    SWITCH_TYPE.S_5470		:	'1990/01/01',
    SWITCH_TYPE.S_5424		:	'1990/01/01',
    SWITCH_TYPE.S_8000		:	'2018/04/02',
    SWITCH_TYPE.S_DCX_4S	:	'2019/11/14',
    SWITCH_TYPE.S_7800		:	'2021/07/21',
    SWITCH_TYPE.S_5450		:	'1990/01/01',
    SWITCH_TYPE.S_5460		:	'1990/01/01',
    SWITCH_TYPE.S_8470		:	'1990/01/01',
    SWITCH_TYPE.S_VA_40FC	:	'2019/01/25',
    SWITCH_TYPE.S_6720_24	:	'2019/09/03',
    SWITCH_TYPE.S_6730_32	:	'2020/05/24',
    SWITCH_TYPE.S_6720_60	:	'1990/01/01',
    SWITCH_TYPE.S_6730_76	:	'2020/05/24',
    SWITCH_TYPE.S_M8428		:	'1990/01/01',
    SWITCH_TYPE.S_6510		:	'Current',
    SWITCH_TYPE.S_6746		:	'Current',
    SWITCH_TYPE.S_6710		:	'2020/05/24',
    SWITCH_TYPE.S_6547		:	'1990/01/01',
    SWITCH_TYPE.S_6505		:	'Current',
    SWITCH_TYPE.S_8510_8	:	'Current',
    SWITCH_TYPE.S_8510_4	:	'Current',
    SWITCH_TYPE.S_5430		:	'2017/08/20',
    SWITCH_TYPE.S_5431		:	'2017/08/20',
    SWITCH_TYPE.S_6548		:	'Current',
    SWITCH_TYPE.S_6505		:	'Current',
    SWITCH_TYPE.S_6740		:	'Current',
    SWITCH_TYPE.S_6520		:	'Current',
    SWITCH_TYPE.S_5432		:	'1990/01/01',
    SWITCH_TYPE.S_6746		:	'1990/01/01',
    SWITCH_TYPE.S_7840		:	'Current',
    SWITCH_TYPE.S_6740T_1G	:	'Current',
    SWITCH_TYPE.S_6940T_1G	:	'Current',
    SWITCH_TYPE.S_G610		:	'Current',
    SWITCH_TYPE.S_G620		:	'Current',
    SWITCH_TYPE.S_G630		:	'Current',
    SWITCH_TYPE.S_X6_8		:	'Current',
    SWITCH_TYPE.S_X6_4		:	'Current',
    SWITCH_TYPE.S_AMP_2_0	:	'Current',
    SWITCH_TYPE.S_7810		:	'Current',
    SWITCH_TYPE.S_8770_4	:	'2014/05/09',
    SWITCH_TYPE.S_8770_8	:	'2014/05/09',
	}

area_mode = {
    0: ' 10-bit addressing mode',
    1: ' Zero-based area assignment',
    2: ' Port-based area assignment',
}


def eos(switch_type):
    """Returns the End of Support (EOS) date

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: EOS_date
    :rtype: str
    """
    try:
        return st_eos[int(float(switch_type))]
    except:
        return ''


def gen(switch_type):
    """Returns the gen type

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: Generation
    :rtype: str
    """
    try:
        return st_gen[int(float(switch_type))]
    except:
        return ''


def slots(switch_type):
    """Returns the number of slots for the switch

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: Num slots
    :rtype: int
    """
    try:
        return st_slots[int(float(switch_type))]
    except:
        return 0


def ibm_machine_type(switch_type):
    """Returns the IBM machine type for the switch

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: machine_type
    :rtype: str
    """
    try:
        return st_type[int(float(switch_type))]
    except:
        return ''


def sys_z_supported(switch_type):
    """Returns True if z systems supported

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: True if z Systems supported
    :rtype: bool
    """
    try:
        return st_sys_z[int(float(switch_type))]
    except:
        return False


def switch_speed(switch_type):
    """Converts the switch type number to the max speed the switch is capable of

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: Maximum speed switch is capable of
    :rtype: int
    """
    try:
        return st_speed[int(float(switch_type))]
    except:
        return 0


def model_oem(switch_type, oem):
    """Returns the OEM branded switch model type.

    Note: As of FOS 8.2.1b, the custom-index was not yet available
    :param switch_type: fibrechannel-switch/model
    :type switch_type: float, int, str
    :param oem: Custom index - I'm assuming this will be 'custom-index' in fibrechannel-switch
    :return: OEM branded witch model
    :rtype: str
    """
    global st_name

    try:
        return st_name[int(switch_type)][oem]
    except:
        return 'Unknown'


def model_broadcom(switch_type):
    """Returns the Broadcom  branded switch model type

    :param switch_type: fibrechannel-switch/model
    :type switch_type: str
    :return: Switch model
    :rtype: str
    """
    return model_oem(switch_type, SWITCH_BRAND.Brocade)


def add_rest_port_data(switch_obj, pobj, flag_obj=None, skip_list=[]):
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
                # is created for the port object in the switch object. I can't think of a reason why just stripping off the
                # type won't work but, if you're in here debugging code, I may have overlooked something
                port_obj = switch_obj.s_add_port('/'.join(pdict.get('name').split('/')[1:]))
            else:
                port_obj = switch_obj.s_add_port(pdict.get('name'))
            v = {}
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
    :rtype: (str, None)
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
