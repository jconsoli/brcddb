"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

**Description**

Creates an iocp page to be added to an Excel Workbook

**Public Methods & Data**

+-----------------------+-------------------------------------------------------------------------------------------+
| Method                | Description                                                                               |
+=======================+===========================================================================================+
| iocp_page             | Creates a zone detail worksheet for the Excel report.                                     |
+-----------------------+-------------------------------------------------------------------------------------------+

**Version Control**

+-----------+---------------+---------------------------------------------------------------------------------------+
| Version   | Last Edit     | Description                                                                           |
+===========+===============+=======================================================================================+
| 4.0.0     | 04 Aug 2023   | Re-Launch                                                                             |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.2     | 06 Dec 2024   | Fixed references to cell_update() and added port and switch links to iocp page.       |
+-----------+---------------+---------------------------------------------------------------------------------------+
| 4.0.3     | 26 Dec 2024   | Documentation updates only.                                                           |
+-----------+---------------+---------------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '26 Dec 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.3'

import collections
import openpyxl.utils.cell as xl
import brcdapi.log as brcdapi_log
import brcdapi.util as brcdapi_util
import brcdapi.gen_util as gen_util
import brcdapi.excel_fonts as excel_fonts
import brcdapi.excel_util as excel_util
import brcddb.brcddb_switch as brcddb_switch
import brcddb.report.utils as report_utils
import brcddb.util.iocp as brcddb_iocp
import brcddb.brcddb_port as brcddb_port

_cu_lookup = dict()
_std_font = excel_fonts.font_type('std')
_bold_font = excel_fonts.font_type('bold')
_link_font = excel_fonts.font_type('link')
_hdr2_font = excel_fonts.font_type('hdr_2')
_hdr1_font = excel_fonts.font_type('hdr_1')
_align_wrap = excel_fonts.align_type('wrap')
_align_wrap_vc = excel_fonts.align_type('wrap_vert_center')
_align_wrap_c = excel_fonts.align_type('wrap_center')
_border_thin = excel_fonts.border_type('thin')


##################################################################
#
#              Case methods for _iocp_case
#
##################################################################
def _null_case(port_obj, chpid_obj, link_addr=None):
    """Returns ''
    
    :param port_obj: Port object associated with the CHPID or Control Unit
    :type port_obj: brcddb.classes.port.PortObj
    :param chpid_obj: This is the CHPID object as determined by brcddb.util.iocp.parse_iocp().
    :type chpid_obj: brcddb.classes.iocp.ChpidObj
    :param link_addr: Link address.
    :type link_addr: str
    :return: Data for table
    :rtype: str
    """
    return ''


def _comment_case(port_obj, chpid_obj, link_addr=None):
    """Returns the comments associated with the port. See _null_case() for parameter definitions"""
    return report_utils.comments_for_alerts(port_obj)


def _pchid_case(port_obj, chpid_obj, link_addr=None):
    """Returns the PCHID. See _null_case() for parameter definitions"""
    return chpid_obj.r_pchid()


def _css_case(port_obj, chpid_obj, link_addr=None):
    """Returns the CSS for the id (tag). See _null_case() for parameter definitions"""
    return ','.join([str(css) for css in brcddb_iocp.tag_to_css_list(chpid_obj.r_obj_key())])


def _chpid_case(port_obj, chpid_obj, link_addr=None):
    """Returns the CHIPID for the id (tag). See _null_case() for parameter definitions"""
    return chpid_obj.r_obj_key()[2:]


def _defined_tag_case(port_obj, chpid_obj, link_addr=None):
    """Returns the CHIPID for the id (tag). See _null_case() for parameter definitions"""
    return chpid_obj.r_obj_key()


def _switch_id_case(port_obj, chpid_obj, link_addr=None):
    """Returns the Switch ID. See _null_case() for parameter definitions"""
    return "'" + chpid_obj.r_switch_id()


def _chpid_link_addr_case(port_obj, chpid_obj, link_addr=None):
    """Returns the link address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    link_addr = port_obj.r_get('fibrechannel/fcid-hex').upper()
    return link_addr[2:6] if isinstance(link_addr, str) else ''


def _unit_type_case(port_obj, chpid_obj, link_addr=None):
    """Returns the unit type associated with the defined path. See _null_case() for parameter definitions"""
    link_d = chpid_obj.r_link_addr(link_addr)
    return '' if link_d is None else ', '.join(gen_util.remove_duplicates(link_d.values()))


def _cu_number(port_obj, chpid_obj, link_addr=None):
    """Returns the CU number for the defined path. See _null_case() for parameter definitions"""
    link_d = chpid_obj.r_link_addr(link_addr)
    return '' if link_d is None else ', '.join(gen_util.remove_duplicates([str(k) for k in link_d.keys()]))


def _switch_case(port_obj, chpid_obj, link_addr=None):
    """Returns the switch name associated with the port. See _null_case() for parameter definitions"""
    return '' if port_obj is None else brcddb_switch.best_switch_name(port_obj.r_switch_obj())


def _index_case(port_obj, chpid_obj, link_addr=None):
    """Returns the port index. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    port_index = port_obj.r_index()
    return '' if port_index is None else port_index


def _port_case(port_obj, chpid_obj, link_addr=None):
    """Returns the port number. See _null_case() for parameter definitions"""
    return '' if port_obj is None else port_obj.r_obj_key()


def _speed_case(port_obj, chpid_obj, link_addr=None):
    """Returns the login speed. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    speed = port_obj.r_get('cs_search/speed')
    return '' if speed is None else speed


def _tx_case(port_obj, chpid_obj, link_addr=None):
    """Returns the number of in-frames. See _null_case() for parameter definitions"""
    return '' if port_obj is None else port_obj.r_get(brcdapi_util.stats_out_frames)


def _rx_case(port_obj, chpid_obj, link_addr=None):
    """Returns the number or out-frames. See _null_case() for parameter definitions"""
    return '' if port_obj is None else port_obj.r_get(brcdapi_util.stats_in_frames)


def _status_case(port_obj, chpid_obj, link_addr=None):
    """Returns port status. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    return port_obj.r_status().replace('Unknown', '')


def _fc_addr_case(port_obj, chpid_obj, link_addr=None):
    """Returns the FC address for the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    return port_obj.r_addr().replace('0x', '')


def _rnid_case(port_obj, chpid_obj, link_addr=None):
    """Returns the RNID flag associated with the port. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    rnid_flag = port_obj.r_get('rnid/flags')
    return '' if rnid_flag is None else brcddb_iocp.rnid_flag_to_text(rnid_flag, True)


def _type_case(port_obj, chpid_obj, link_addr=None):
    """Returns the port type and type description. See _null_case() for parameter definitions"""
    return '' if port_obj is None else \
        brcddb_iocp.dev_type_desc(port_obj.r_get('rnid/type-number'), True, True, True, ' (', ')')


def _mfg_case(port_obj, chpid_obj, link_addr=None):
    """Returns the manufacturer from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    mfg = port_obj.r_get('rnid/manufacturer')
    return '' if mfg is None else mfg


def _seq_case(port_obj, chpid_obj, link_addr=None):
    """Returns the sequence (S/N) from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    seq = port_obj.r_get('rnid/sequence-number')
    return '' if seq is None else seq


def _tag_case(port_obj, chpid_obj, link_addr=None):
    """Returns the tag from the RNID data. See _null_case() for parameter definitions"""
    if port_obj is None:
        return ''
    tag = port_obj.r_get('rnid/tag')
    return '' if tag is None else tag.replace('0x', '')


def _zone_case(port_obj, chpid_obj, link_addr=None):
    return ''


def _link_addr_case(port_obj, chpid_obj, link_addr=None):
    """Returns the link address. See _null_case() for parameter definitions"""
    return link_addr


_chpid_hdr = collections.OrderedDict({
    # Key   Column header. Value is dict: 'c' - Column width, 'm' - Method to call to fill in the cell data
    'Comments': dict(c=30, m=_comment_case),
    'PCHID': dict(c=7, m=_pchid_case),
    'CSS': dict(c=10, m=_css_case),
    'CHPID': dict(c=7, m=_chpid_case),
    'Defined Tag': dict(c=9, m=_defined_tag_case),
    'Switch ID': dict(c=8, m=_switch_id_case),
    'Link Addr': dict(c=7, m=_chpid_link_addr_case),
    'Unit Type': dict(c=10, m=_null_case),
    'CU Number': dict(c=22, m=_null_case),
    'Switch': dict(c=22, m=_switch_case),
    'Index': dict(c=7, m=_index_case),
    'Port': dict(c=7, m=_port_case),
    'Speed (Gbps)': dict(c=7, m=_speed_case),
    'Tx Frames': dict(c=15, m=_tx_case, f='#,###'),
    'Rx Frames': dict(c=15, m=_rx_case, f='#,###'),
    'Status': dict(c=8, m=_status_case),
    'FC Addr': dict(c=8, m=_fc_addr_case),
    'RNID': dict(c=23, m=_rnid_case),
    'Type': dict(c=28, m=_type_case),
    'Mfg': dict(c=8, m=_mfg_case),
    'Sequence': dict(c=15, m=_seq_case),
    'Tag': dict(c=7, m=_tag_case),
    # 'Zone': dict(c=22, m=_zone_case),
})
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
    'Tx Frames': _tx_case,
    'Rx Frames': _rx_case,
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
    :param sheet_i: Sheet index where page is to be placed. Default is 0
    :type sheet_i: int
    :param sheet_title: Title to be displayed in large font, hdr_1, at the top of the sheet
    :type sheet_title: str
    :rtype: None
    """
    global _chpid_hdr, _cu_hdr, _cu_lookup, _align_wrap_vc, _hdr2_font, _border_thin, _std_font

    proj_obj = iocp_obj.r_project_obj()

    # Just in case the columns ever get moved around, figure them out dynamically
    key_to_col_d = excel_util.find_headers([str(k) for k in _chpid_hdr.keys()], plus_one=True)

    # Create the worksheet, add the headers, and set up the column widths
    sheet = wb.create_sheet(index=0 if sheet_i is None else sheet_i, title=sheet_name)
    sheet.page_setup.paperSize = sheet.PAPERSIZE_LETTER
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    row = col = 1
    if isinstance(tc, str):
        excel_util.cell_update(sheet, row, col, 'Contents', font=_link_font, link=tc)
        col += 1
    excel_util.cell_update(sheet, row, col, sheet_title, font=_hdr1_font)
    row, col = row+2, 1
    sheet.freeze_panes = sheet['A4']
    for k, d in _chpid_hdr.items():
        sheet.column_dimensions[xl.get_column_letter(col)].width = d['c']
        alignment = _align_wrap_vc if 'v' in d and d['v'] else _align_wrap
        excel_util.cell_update(sheet, row, col, k, font=_hdr2_font, align=alignment, border=_border_thin)
        col += 1

    # Sort the CHPIDs by PCHID in the report.
    chpid_d = dict()
    for chpid_obj in iocp_obj.r_path_objects():
        # In case two CHPIDs share the same PCHID, make it unique by appending the CHPID tag
        chpid_d.update({chpid_obj.r_pchid() + '_' + chpid_obj.r_obj_key(): chpid_obj})
    chpid_l = [str(k) for k in chpid_d.keys()]
    chpid_l.sort()

    # Fill out all the CHPID information
    cec_sn = brcddb_iocp.full_cpc_sn(iocp_obj.r_obj_key())
    for chpid_obj in [chpid_d[chpid_k] for chpid_k in chpid_l]:
        row += 1
        chpid_port_obj = brcddb_port.port_obj_for_chpid(proj_obj, cec_sn, chpid_obj.r_obj_key())
        fabric_obj = None if chpid_port_obj is None else chpid_port_obj.r_fabric_obj()
        for k, d in _chpid_hdr.items():
            font, link = _std_font, None
            if chpid_port_obj is not None:
                if k == 'Switch':
                    try:
                        link = chpid_port_obj.r_switch_obj().r_get('report_app/hyperlink/switch')
                        if link is not None:
                            font = _link_font
                    except AttributeError:
                        pass  # This can happen when there is a partial data collection
                elif k == 'Port':
                    link = chpid_port_obj.r_get('report_app/hyperlink/pl')
                    if link is not None:
                        font = _link_font
                elif k == 'Comments':
                    font = report_utils.font_type(chpid_port_obj.r_alert_objects())
            excel_util.cell_update(sheet,
                                   row,
                                   key_to_col_d[k],
                                   d['m'](chpid_port_obj, chpid_obj),
                                   font=font,
                                   align=_align_wrap,
                                   border=_border_thin,
                                   number_format=d.get('f'),
                                   link=link)

        # Display the link addresses
        row += 1
        for link_addr in chpid_obj.r_link_addresses():

            # Get the port object
            port_obj = None
            if fabric_obj is not None:
                did = fabric_obj.r_switch_objects()[0].r_did() if len(fabric_obj.r_switch_keys()) == 1 else None
                port_obj = brcddb_port.port_obj_for_addr(
                    fabric_obj,
                    brcddb_iocp.link_addr_to_fc_addr(
                        link_addr,
                        switch_id=chpid_obj.r_switch_id() if did is None else None,
                        did=did,
                        leading_0x=True
                    )
                )

            # Display the corresponding port information
            for k, d in _chpid_hdr.items():
                font, link = _std_font, None
                if port_obj is not None:
                    if k == 'Port':
                        link = port_obj.r_get('report_app/hyperlink/pl')
                        if link is not None:
                            font = _link_font
                    if k == 'Switch':
                        try:
                            link = port_obj.r_switch_obj().r_get('report_app/hyperlink/switch')
                            if link is not None:
                                font = _link_font
                        except AttributeError:
                            pass  # This can happen when there is a partial data collection
                    elif k == 'Comments':
                        font = report_utils.font_type(port_obj.r_alert_objects())
                excel_util.cell_update(sheet,
                                       row,
                                       key_to_col_d[k],
                                       _cu_hdr.get(k)(port_obj, chpid_obj, link_addr) if k in _cu_hdr else None,
                                       font=font,
                                       align=_align_wrap,
                                       border=_border_thin,
                                       number_format=d.get('f'),
                                       link=link)
            row += 1

    return
