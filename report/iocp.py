#!/usr/bin/python
# Copyright 2019 Jack Consoli.  All rights reserved.
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
:mod:`report.iocp` - Creates an iocp page to be added to an Excel Workbook

VVersion Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 02 Aug 2020   | Initial Launch - 3.x to be consistent with older class objects                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '02 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.0'

import openpyxl.utils.cell as xl
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.report.utils as report_utils
import brcddb.util.search as brcddb_search
import brcddb.util.iocp as brcddb_iocp

##################################################################
#
#              Case methods for _iocp_case
#
##################################################################


def _null_case(id, port_obj, chpid=None):
    """Returns ''
    
    :param id: Idendifier. For CHIPIDs this is the tag and for control units this is the link address
    :type id: str
    :param port_obj: Port object associated with the CHPID or Control Unit
    :type port_obj: brcddb.classes.port.PortObj
    :param chpid: CHPID definition as filled in by brcddb.util.iocp.parse_iocp()
    :type chpid: dict
    """
    return ''


def _comment_case(id, port_obj, chpid=None):
    """Returns the comments associated with the port. See _null_case() for parameter definitions"""
    return report_utils.comments_for_alerts(port_obj)


def _pchid_case(id, port_obj, chpid=None):
    """Returns the PCHID. See _null_case() for parameter definitions"""
    return chpid.get('pchid')


def _css_case(id, port_obj, chpid=None):
    """Returns the CSS for the id (tag). See _null_case() for parameter definitions"""
    return ','.join([str(css) for css in brcddb_iocp.tag_to_css_list(id)])


def _chpid_case(id, port_obj, chpid=None):
    """Returns the CHIPID for the id (tag). See _null_case() for parameter definitions"""
    return id[2:]


def _switch_id_case(id, port_obj, chpid=None):
    """Returns the Switch ID. See _null_case() for parameter definitions"""
    return "'" + chpid.get('switch')


def _chpid_link_addr_case(id, port_obj, chpid=None):
    """Returns the link address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    link_addr = port_obj.r_get('fibrechannel/fcid-hex')
    return link_addr[2:6] if isinstance(link_addr, str) else ''


def _unit_type_case(id, port_obj, chpid=None):
    """Returns the unit type associated with the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    unit_type = port_obj.r_get('rnid/type-number')
    return '' if unit_type is None else unit_type


def _switch_case(id, port_obj, chpid=None):
    """Returns the switch name associated with the port. See _null_case() for parameter definitions"""
    return '' if port_obj is None else brcddb_switch.best_switch_name(port_obj.r_switch_obj())


def _index_case(id, port_obj, chpid=None):
    """Returns the port index. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    port_index = port_obj.r_get('fibrechannel/index')
    return '' if port_index is None else port_index


def _port_case(id, port_obj, chpid=None):
    """Returns the port number. See _null_case() for parameter definitions"""
    return '' if port_obj is None else port_obj.r_obj_key()


def _speed_case(id, port_obj, chpid=None):
    """Returns the login speed. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    speed = port_obj.r_get('_search/speed')
    return '' if speed is None else speed


def _status_case(id, port_obj, chpid=None):
    """Returns port status. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    status = port_obj.r_get('fibrechannel/operational-status')
    return '' if status is None else status


def _fc_addr_case(id, port_obj, chpid=None):
    """Returns the FC address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    addr = port_obj.r_get('fibrechannel/fcid-hex')
    return '' if addr is None else addr.replace('0x', '')


def _rnid_case(id, port_obj, chpid=None):
    """Returns the RNID flag associated with the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    rnid_flag = port_obj.r_get('rnid/flags')
    return '' if rnid_flag is None else brcddb_iocp.rnid_flag_to_text(rnid_flag, True)


def _type_case(id, port_obj, chpid=None):
    """Returns the port type. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    port_type = port_obj.r_get('fibrechannel/port-type')
    return '' if port_type is None else port_type


def _mfg_case(id, port_obj, chpid=None):
    """Returns the manufacturer from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    mfg = port_obj.r_get('rnid/manufacturer')
    return '' if mfg is None else mfg


def _seq_case(id, port_obj, chpid=None):
    """Returns the sequence (S/N) from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    seq = port_obj.r_get('rnid/manufacturer')
    return '' if seq is None else seq


def _tag_case(id, port_obj, chpid=None):
    """Returns the tag from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    tag = port_obj.r_get('rnid/manufacturer')
    return '' if tag is None else tag


def _zone_case(id, port_obj, chpid=None):
    return ''


def _cu_link_addr_case(id, port_obj, chpid=None):
    """Returns the link address. See _null_case() for parameter definitions"""
    return id


_chpid_hdr = {
    # Key   Column header
    # 'c'   Column width
    # 'm'   Method to call to fill in the cell data
    'Comments': {'c': 30, 'm': _comment_case},
    'PCHID': {'c': 7, 'm': _pchid_case},
    'CSS': {'c': 10, 'm': _css_case},
    'CHPID': {'c': 7, 'm': _chpid_case},
    'Switch ID': {'c': 7, 'm': _switch_id_case},
    'Link Addr': {'c': 7, 'm': _chpid_link_addr_case},
    'Unit Type': {'c': 8, 'm': _unit_type_case},
    'Switch': {'c': 22, 'm': _switch_case},
    'Index': {'c': 7, 'm': _index_case},
    'Port': {'c':  7, 'm': _port_case},
    'Speed (Gbps)': {'c': 7, 'm': _speed_case},
    'Status': {'c': 8, 'm': _status_case},
    'FC Addr': {'c': 8, 'm': _fc_addr_case},
    'RNID': {'c': 8, 'm': _rnid_case},
    'Type': {'c': 8, 'm': _type_case},
    'Mfg': {'c': 8, 'm': _mfg_case},
    'Sequence': {'c': 15, 'm': _seq_case},
    'Tag': {'c': 7, 'm': _seq_case},
#    'Zone': {'c': 22, 'm': _zone_case},
}
_cu_hdr = {
    # Key is the column header. Value is the method to call to fill in the cell data
    'Comments': _comment_case,
    'CSS': _null_case,
    'CHPID': _null_case,
    'Switch ID': _null_case,
    'Link Addr': _cu_link_addr_case,
    'Unit Type': _unit_type_case,
    'Switch': _switch_case,
    'Index': _index_case,
    'Port': _port_case,
    'Speed': _speed_case,
    'Status': _status_case,
    'FC Addr': _fc_addr_case,
    'RNID': _rnid_case,
    'Type': _type_case,
    'Mfg': _mfg_case,
    'Sequence': _seq_case,
    'Tag': _seq_case,
    'Zone': _zone_case,
}


def _port_obj_for_chpid(proj_obj, seq, tag):
    """Creates a zone detail worksheet for the Excel report.

    :param proj_obj: Project object where collected data is to be added
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param seq: Serial number (sequence number) for CEC
    :type seq: str
    :param tag: CHPID tag
    :type tag: str
    :rturn: Port object where this CHPID is connected. None if not found
    :rtype: brcddb.classes.port.PortObj, None
    """
    port_list = brcddb_search.match_test(
        proj_obj.r_port_objects(),
        {
            'l': (
                {'k': 'rnid/sequence-number', 't': '==', 'v': seq},
                {'k': 'rnid/tag', 't': '==', 'v': tag},
                {'k': 'rnid/flags', 't': '==', 'v': '0x10'},  # Indicates the RNID data is valid for a channel
            ),
            'logic': 'and'  # 'and' is the default logic so this is just for clarity for the reader
        }
    )
    return port_list[0] if len(port_list) > 0 else None


def _port_obj_for_link_addr(fab_obj, link_addr):
    """Creates a zone detail worksheet for the Excel report.

    :param fab_obj: Fabric object to look for port in
    :type fab_obj: brcddb.classes.fabric.FabricObj
    :param link_addr: Channel path link address
    :type link_addr: str
    :rturn: Port object matching the link address
    :rtype: brcddb.classes.port.PortObj, None
    """
    port_list = brcddb_search.match_test(
        fab_obj.r_port_objects(),
        {
            'l': (
                {'k': 'brocade-interface/sequence-number', 't': '==', 'v': seq},
                {'k': 'rnid/tag', 't': '==', 'v': tag},
                {'k': 'rnid/flags', 't': '==', 'v': '0x10'},  # Indicates the RNID data is valid for a channel
            ),
            'logic': 'and'  # 'and' is the default logic so this is just for clarity for the reader
        }
    )
    return port_list[0] if len(port_list) > 0 else None


def iocp_page(iocp_obj, tc, wb, sheet_name, sheet_i, sheet_title):
    """Creates a zone detail worksheet for the Excel report.

    :param iocp_obj: IOCP object
    :type iocp_obj: brcddb.classes.iocp.IOCPObj
    :param tc: Table of context page. A link to this page is place in cell A1
    :type tc: str, None
    :param wb: Workbook object
    :type wb: class
    :param sheet_name: Sheet (tab) name
    :type sheet_name: str
    :param sheet_i: Sheet index where page is to be placed.
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global _chpid_hdr, _cu_hdr

    proj_obj = iocp_obj.r_project_obj()

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    col = 1
    row = 1
    if isinstance(tc, str):
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].hyperlink = '#' + tc + '!A1'
        sheet[cell].font = report_fonts.font_type('link')
        sheet[cell] = 'Contents'
        col += 1
    cell = xl.get_column_letter(col) + str(row)
    sheet[cell].font = report_fonts.font_type('hdr_1')
    sheet[cell] = sheet_title
    row += 2
    col = 1
    sheet.freeze_panes = sheet['A4']
    font = report_fonts.font_type('hdr_2')
    border = report_fonts.border_type('thin')
    for k in _chpid_hdr:
        sheet.column_dimensions[xl.get_column_letter(col)].width = _chpid_hdr[k]['c']
        cell = xl.get_column_letter(col) + str(row)
        sheet[cell].font = font
        sheet[cell].border = border
        if 'v' in _chpid_hdr[k] and _chpid_hdr[k]['v']:
            sheet[cell].alignment = report_fonts.align_type('wrap_vert_center')
        else:
            sheet[cell].alignment = report_fonts.align_type('wrap')
        sheet[cell] = k
        col += 1

    # Fill out all the CHPID information
    cec_sn = iocp_obj.r_obj_key()
    for i in range(len(cec_sn), 12):
        cec_sn = '0' + cec_sn  # The sequence number is always returned as a 12 charater str with leading '0'
    d = iocp_obj.r_path_objects()
    if isinstance(d, dict):
        for tag, chpid in d.items():

            # Display the CHPID information
            pchid = chpid.get('pchid')
            row += 1
            col = 1
            chpid_port_obj = _port_obj_for_chpid(proj_obj, cec_sn, tag)
            for k in _chpid_hdr.keys():
                cell = xl.get_column_letter(col) + str(row)
                if k == 'Comments' and chpid_port_obj is not None:
                    sheet[cell].font = report_utils.font_type(chpid_port_obj.r_alert_objects())
                else:
                    sheet[cell].font = report_fonts.font_type('std')
                sheet[cell].border = border
                sheet[cell].alignment = report_fonts.align_type('wrap')
                sheet[cell] =  _chpid_hdr[k]['m'](tag, chpid_port_obj, chpid)
                col += 1

            # Display the link addresses
            if chpid_port_obj is not None:
                row += 1
                col = 1
                for link_addr in chpid.get('link'):
                    port_obj = _port_obj_for_link_addr(chpid_port_obj.r_fabric_obj(), link_addr)
                    cell = xl.get_column_letter(col) + str(row)
                    for k in _cu_hdr.keys():
                        if k == 'Comments' and port_obj is not None:
                            sheet[cell].font = report_utils.font_type(port_obj.r_alert_objects())
                        else:
                            sheet[cell].font = report_fonts.font_type('std')
                        sheet[cell].border = border
                        sheet[cell].alignment = report_fonts.align_type('wrap')
                        if k in _cu_hdr:
                            sheet[cell] = _cu_hdr[k](link_addr, port_obj)
                        else:
                            sheet[cell] = ''
                        col += 1
    return

