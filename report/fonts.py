# Copyright 2019, 2020, 2021, 2022 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.report.fonts` - Depracated

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | Fixed typo in align_type() exception case                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 14 Nov 2021   | Added configuration workbook fill types                                           |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.5     | 31 Dec 2021   | Added more configuration workbook fill types and bold white text font.            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.6     | 28 Apr 2022   | Depracated.                                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021, 2022 Jack Consoli'
__date__ = '28 Apr 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import openpyxl.styles as xl_styles
import brcdapi.log as brcdapi_log
import brcdapi.excel_fonts as excel_fonts
#################################################################
#   Font Types                                                  #
#                                                               #
#   If you add a font type, remember to add it to font_tbl      #
#################################################################
std_font = excel_fonts.std_font
h1_font = excel_fonts.h1_font
h2_font = excel_fonts.h2_font
bold_font = excel_fonts.bold_font
italic_font = excel_fonts.italic_font
warn_font = excel_fonts.warn_font
error_font = excel_fonts.error_font
link_font = excel_fonts.link_font
font_tbl = excel_fonts.font_tbl
thin_border = excel_fonts.thin_border
border_tbl = excel_fonts.border_tbl
wrap_center_alignment = excel_fonts.wrap_center_alignment
wrap_right_alignment = excel_fonts.wrap_right_alignment
wrap_alignment = excel_fonts.wrap_alignment
wrap_vert_center_alignment = excel_fonts.wrap_vert_center_alignment
align_tbl = excel_fonts.align_tbl


def font_type(x):
    return excel_fonts.font_type(x)


def fill_type(x):
    return excel_fonts.fill_type(x)


def border_type(x):
    return excel_fonts.border_type(x)


def align_type(x):
    return excel_fonts.align_type(x)
