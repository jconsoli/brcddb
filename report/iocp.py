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
:mod:`report.iocp` - Creates an iocp page to be added to an Excel Workbook

VVersion Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 02 Aug 2020   | Initial Launch - 3.x to be consistent with older class objects                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 22 Aug 2020   | Fixed link address reporting.                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 02 Sep 2020   | Fixed missing paths in IOCP report                                                |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 13 Feb 2021   | Removed the shebang line                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 17 Jul 2021   | Added 'Comment' column. Used libraries in brcddb_port.                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '17 Jul 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import openpyxl.utils.cell as xl
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.fonts as report_fonts
import brcddb.report.utils as report_utils
import brcddb.util.search as brcddb_search
import brcddb.util.iocp as brcddb_iocp
import brcddb.brcddb_port as brcddb_port

_cu_lookup = dict()


##################################################################
#
#              Case methods for _iocp_case
#
##################################################################
def _null_case(id, port_obj, chpid, link_addr=None):
    """Returns ''
    
    :param id: Idendifier. This is the CHPID tag
    :type id: str
    :param port_obj: Port object associated with the CHPID or Control Unit
    :type port_obj: brcddb.classes.port.PortObj
    :param chpid: This is the dict as filled in by brcddb.util.iocp.parse_iocp().
    :type chpid: dict
    :param link_addr: Link address.
    :type link_addr: str
    :return: Data for table
    :rtype: str
    """
    return ''


def _comment_case(id, port_obj, chpid, link_addr=None):
    """Returns the comments associated with the port. See _null_case() for parameter definitions"""
    return report_utils.comments_for_alerts(port_obj)


def _pchid_case(id, port_obj, chpid, link_addr=None):
    """Returns the PCHID. See _null_case() for parameter definitions"""
    return chpid.get('pchid')


def _css_case(id, port_obj, chpid, link_addr=None):
    """Returns the CSS for the id (tag). See _null_case() for parameter definitions"""
    return ','.join([str(css) for css in brcddb_iocp.tag_to_css_list(id)])


def _chpid_case(id, port_obj, chpid, link_addr=None):
    """Returns the CHIPID for the id (tag). See _null_case() for parameter definitions"""
    return id[2:]


def _defined_tag_case(id, port_obj, chpid, link_addr=None):
    """Returns the CHIPID for the id (tag). See _null_case() for parameter definitions"""
    return id.replace('0x', '')


def _switch_id_case(id, port_obj, chpid, link_addr=None):
    """Returns the Switch ID. See _null_case() for parameter definitions"""
    return "'" + chpid.get('switch')


def _chpid_link_addr_case(id, port_obj, chpid, link_addr=None):
    """Returns the link address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    link_addr = port_obj.r_get('fibrechannel/fcid-hex')
    return link_addr[2:6] if isinstance(link_addr, str) else ''


def _unit_type_case(id, port_obj, chpid, link_addr=None):
    """Returns the unit type associated with the defined path. See _null_case() for parameter definitions"""
    global _cu_lookup

    cu = _cu_lookup.get(id + '_' + link_addr)
    return '' if cu is None else cu['unit']


def _cu_number(id, port_obj, chpid, link_addr=None):
    """Returns the CU number for the defined path. See _null_case() for parameter definitions"""
    global _cu_lookup

    cu = _cu_lookup.get(id + '_' + link_addr)
    return '' if cu is None else cu['_cu_num']


def _switch_case(id, port_obj, chpid, link_addr=None):
    """Returns the switch name associated with the port. See _null_case() for parameter definitions"""
    return '' if port_obj is None else brcddb_switch.best_switch_name(port_obj.r_switch_obj())


def _index_case(id, port_obj, chpid, link_addr=None):
    """Returns the port index. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    port_index = port_obj.r_get('fibrechannel/index')
    return '' if port_index is None else port_index


def _port_case(id, port_obj, chpid, link_addr=None):
    """Returns the port number. See _null_case() for parameter definitions"""
    return '' if port_obj is None else port_obj.r_obj_key()


def _speed_case(id, port_obj, chpid, link_addr=None):
    """Returns the login speed. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    speed = port_obj.r_get('_search/speed')
    return '' if speed is None else speed


def _status_case(id, port_obj, chpid, link_addr=None):
    """Returns port status. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    status = port_obj.r_get('fibrechannel/operational-status')
    return '' if status is None else status


def _fc_addr_case(id, port_obj, chpid, link_addr=None):
    """Returns the FC address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    addr = port_obj.r_get('fibrechannel/fcid-hex')
    return '' if addr is None else addr.replace('0x', '')


def _rnid_case(id, port_obj, chpid, link_addr=None):
    """Returns the RNID flag associated with the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    rnid_flag = port_obj.r_get('rnid/flags')
    return '' if rnid_flag is None else brcddb_iocp.rnid_flag_to_text(rnid_flag, True)


def _type_case(id, port_obj, chpid, link_addr=None):
    """Returns the port type. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    port_type = port_obj.r_get('rnid/type-number')
    return '' if port_type is None else port_type


def _mfg_case(id, port_obj, chpid, link_addr=None):
    """Returns the manufacturer from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    mfg = port_obj.r_get('rnid/manufacturer')
    return '' if mfg is None else mfg


def _seq_case(id, port_obj, chpid, link_addr=None):
    """Returns the sequence (S/N) from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    seq = port_obj.r_get('rnid/sequence-number')
    return '' if seq is None else seq


def _tag_case(id, port_obj, chpid, link_addr=None):
    """Returns the tag from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    tag = port_obj.r_get('rnid/tag')
    return '' if tag is None else tag.replace('0x', '')


def _zone_case(id, port_obj, chpid, link_addr=None):
    return ''


def _link_addr_case(id, port_obj, chpid, link_addr=None):
    """Returns the link address. See _null_case() for parameter definitions"""
    return link_addr


_chpid_hdr = {
    # Key   Column header
    # 'c'   Column width
    # 'm'   Method to call to fill in the cell data
    'Comments': dict(c=30, m=_comment_case),
    'PCHID': dict(c=7, m=_pchid_case),
    'CSS': dict(c=10, m=_css_case),
    'CHPID': dict(c=7, m=_chpid_case),
    'Defined Tag': dict(c=8, m=_defined_tag_case),
    'Switch ID': dict(c=7, m=_switch_id_case),
    'Link Addr': dict(c=7, m=_chpid_link_addr_case),
    'Unit Type': dict(c=9, m=_null_case),
    'CU Number': dict(c=9, m=_null_case),
    'Switch': dict(c=22, m=_switch_case),
    'Index': dict(c=7, m=_index_case),
    'Port': dict(c= 7, m=_port_case),
    'Speed (Gbps)': dict(c=7, m=_speed_case),
    'Status': dict(c=8, m=_status_case),
    'FC Addr': dict(c=8, m=_fc_addr_case),
    'RNID': dict(c=22, m=_rnid_case),
    'Type': dict(c=8, m=_type_case),
    'Mfg': dict(c=8, m=_mfg_case),
    'Sequence': dict(c=15, m=_seq_case),
    'Tag': dict(c=7, m=_tag_case),
    # 'Zone': dict(c=22, m=_zone_case),
}
_cu_hdr = {
    # Key is the column header. Value is the method to call to fill in the cell data. Keys must match _chpid_hdr keys
    'Comments': _comment_case,
    'Link Addr': _link_addr_case,
    'Unit Type': _unit_type_case,
    'CU Number': _cu_number,
    'Switch': _switch_case,
    'Index': _index_case,
    'Port': _port_case,
    'Speed (Gbps)': _speed_case,
    'Status': _status_case,
    'FC Addr': _fc_addr_case,
    'RNID': _rnid_case,
    'Type': _type_case,
    'Mfg': _mfg_case,
    'Sequence': _seq_case,
    'Tag': _tag_case,
    # 'Zone': _zone_case,
}


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
    global _chpid_hdr, _cu_hdr, _cu_lookup

    proj_obj = iocp_obj.r_project_obj()

    # Just in case the columns ever get moved around, figure them out dynamically
    key_to_col = dict()
    i = 1
    for k in _chpid_hdr.keys():
        key_to_col.update({k: i})
        i += 1

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
    cec_sn = brcddb_iocp.full_cpc_sn(iocp_obj.r_obj_key())
    d = iocp_obj.r_path_objects()
    if isinstance(d, dict):

        # Build a table to look up the control unit by a hash of CHPID tag + '_' + link address
        cu_list = iocp_obj.r_cu_objects()
        for tag, chpid in d.items():
            for k, v in cu_list.items():  # K is the CU Number
                cu_addr = v['path'].get(tag)
                if cu_addr is not None and cu_addr in chpid['link']:
                    v.update(dict(_cu_num=k))
                    _cu_lookup.update({tag + '_' + cu_addr: v})

        # Add the CHPID and Control Units to the report
        for tag, chpid in d.items():

            # Display the CHPID information
            pchid = chpid.get('pchid')
            row += 1
            chpid_port_obj = brcddb_port.port_obj_for_chpid(proj_obj, cec_sn, tag)
            fabric_obj = None if chpid_port_obj is None else chpid_port_obj.r_fabric_obj()
            for k in _chpid_hdr.keys():
                cell = xl.get_column_letter(key_to_col[k]) + str(row)
                if k == 'Comments' and chpid_port_obj is not None:
                    sheet[cell].font = report_utils.font_type(chpid_port_obj.r_alert_objects())
                else:
                    sheet[cell].font = report_fonts.font_type('std')
                sheet[cell].border = border
                sheet[cell].alignment = report_fonts.align_type('wrap')
                sheet[cell] =  _chpid_hdr[k]['m'](tag, chpid_port_obj, chpid)

            # Display the link addresses
            row += 1
            for link_addr in chpid.get('link'):
                port_obj = None if fabric_obj is None else \
                    brcddb_port.port_obj_for_addr(fabric_obj, '0x' + link_addr + '00')
                for k in _cu_hdr.keys():
                    cell = xl.get_column_letter(key_to_col[k]) + str(row)
                    if k == 'Comments' and port_obj is not None:
                        sheet[cell].font = report_utils.font_type(port_obj.r_alert_objects())
                    else:
                        sheet[cell].font = report_fonts.font_type('std')
                    sheet[cell].border = border
                    sheet[cell].alignment = report_fonts.align_type('wrap')
                    sheet[cell] = _cu_hdr[k](tag, port_obj, chpid, link_addr)
                row += 1

    return
