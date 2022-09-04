# Copyright 2020, 2021, 2022 Jack Consoli.  All rights reserved.
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

:mod:`report.graph` - Creates a worksheet with a graph

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | graph                 | Inserts a worksheet into a workbook with a graph of specified ports and statistics.   |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 29 Sep 2020   | Initial. Started with 3.0 for consistency with other libraries                    |
    +-----------+----------------+----------------------------------------------------------------------------------+
    | 3.0.1     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 28 Apr 2022   | Updated documentation.                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 04 Sep 2022   | Fixed table of contents hyper link                                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2022 Jack Consoli'
__date__ = '04 Sep 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.3'

from openpyxl.chart import AreaChart, AreaChart3D, BarChart, BarChart3D, LineChart, LineChart3D, Reference
from openpyxl.chart.axis import DateAxis
import brcdapi.excel_util as excel_util
import brcdapi.excel_fonts as excel_fonts

_link_font = excel_fonts.font_type('link')

chart_types = {
    'area': AreaChart,
    'area_3d': AreaChart3D,
    'bar': BarChart,
    'bar_3d': BarChart3D,
    'line': LineChart,
    'line_3d': LineChart3D,
}


def graph(wb, tc, sheet_name, sheet_i, data_ref):
    """Inserts a worksheet into a workbook with a graph of specified ports and statistics.

    data_ref: The graph assumes that the first row of the data are the data labels

    +-----------+-----------+-------------------------------------------+
    | Member    | type      | Description                               |
    +===========+===========+===========================================+
    | title     | str       | Chart title                               |
    +-----------+-----------+-------------------------------------------+
    | sheet     | pointer   | Pointer to worksheet object returned from |
    |           |           | create_sheet()                            |
    +-----------+-----------+-------------------------------------------+
    | type      | str       | Chart type. See chart_types.              |
    +-----------+-----------+-------------------------------------------+
    | x         | dict      | See Axis dictionary below.                |
    +-----------+-----------+-------------------------------------------+
    | y         | dict      | Same as x but for the y axis.             |
    +-----------+-----------+-------------------------------------------+

    Axis dictionary

    +-----------+-----------+-------------------------------------------+
    | Member    | type      | Description                               |
    +===========+===========+===========================================+
    | title     | str       | Axis title.                               |
    +-----------+-----------+-------------------------------------------+
    | min_col   | int       | Starting column.                          |
    +-----------+-----------+-------------------------------------------+
    | max_col   | int       | Last column. Not used for the x axis.     |
    +-----------+-----------+-------------------------------------------+
    | min_row   | int       | Starting row. Should include the labels.  |
    +-----------+-----------+-------------------------------------------+
    | max_row   | int       | Row number for the last sample.           |
    +-----------+-----------+-------------------------------------------+

    :param wb: Workbook object
    :type wb: Workbook object
    :param tc: Link to table of context page.
    :type tc: str, None
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param data_ref: Chart type. See chart_types
    :type data_ref: dict
    :rtype: None
    """
    global _link_font

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    ref_sheet = data_ref['sheet']
    y, x = data_ref['y'], data_ref['x']
    if isinstance(tc, str):
        excel_util.cell_update(sheet, 1, 1, 'Contents', link=tc, font=_link_font)

    data = Reference(ref_sheet, min_col=y['min_col'], min_row=y['min_row'], max_col=y['max_col'], max_row=y['max_row'])
    # Chart with date axis
    chart = LineChart()
    chart.title = data_ref['title']
    chart.y_axis.title = y['title']
    chart.y_axis.crossAx = 500
    chart.x_axis = DateAxis(crossAx=100)
    chart.x_axis.title = x['title']

    chart.add_data(data, titles_from_data=True)
    dates = Reference(ref_sheet, min_col=x['min_col'], min_row=x['min_row'], max_row=x['max_row'])
    chart.set_categories(dates)

    sheet.add_chart(chart, 'A2')
