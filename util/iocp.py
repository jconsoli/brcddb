"""
Copyright 2023, 2024 Consoli Solutions, LLC.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may also obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.

The license is free for single customer use (internal applications). Use of this module in the production,
redistribution, or service delivery for commerce requires an additional license. Contact jack@consoli-solutions.com for
details.

:mod:`brcddb.util.iocp` - Utility functions for the brcddb libraries

**Important Notes**

There is a little error checking but most error checking was done to assist with debugging the script, not the IOCP. It
is assumed that the IOCP compiled on the host without error.

This initial incarnation of this routine used the built in PERL features for manipulating strings and text but I kept
coming across nuances and syntax that I didn't expect. Keep in mind I'm not an expert at building an IOCP by hand. Most
customers today aren't either, they use HCD. What I ended up with here is a C like parser that is built on a state
machine. It's not very efficient but we don't need efficiency here. What I needed was tha ability to quickly and easily
identify a mistake in the script or something unexpected in the syntax.

Note that an IOCP is in old punch card format where certain characters in certain positions mean something. Rather than
re-invent the wheel, this was taken from an old Perl script and converted to Python. It certainly isn't elegant but it
is functional.

Public Methods & Data::

    +-----------------------+---------------------------------------------------------------------------------------+
    | Method                | Description                                                                           |
    +=======================+=======================================================================================+
    | full_cpc_sn           | Prepends a CPC SN with 0 such that it is padded to a full 12 character serial number  |
    |                       | to match RNID sequence.                                                               |
    +-----------------------+---------------------------------------------------------------------------------------+
    | dev_type_desc         | Converts the RNID type to a human-readable device type                                |
    +-----------------------+---------------------------------------------------------------------------------------+
    | css_to_tag            | Parses a list of CSS into the first byte for the tag                                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | css_chpid_to_tag      | Parses a CSS(x,y)chpid into the equivalent tag                                        |
    +-----------------------+---------------------------------------------------------------------------------------+
    | tag_to_css_list       | Converts a tag to a list of CSS bits                                                  |
    +-----------------------+---------------------------------------------------------------------------------------+
    | tag_to_text           | Converts a CHPID tag to human-readable format (as displayed in the IOCP)              |
    +-----------------------+---------------------------------------------------------------------------------------+
    | tag_to_ind_tag_list   | Returns a list of individual tags for a tag. For example: 'C0' is returned as a list  |
    |                       | of '80', '40'                                                                         |
    +-----------------------+---------------------------------------------------------------------------------------+
    | rnid_flag_to_text     | Converts the RNID flag to human-readable text                                         |
    +-----------------------+---------------------------------------------------------------------------------------+
    | parse_iocp            | Parses an IOCP and adds the IOCP to the proj_obj                                      |
    +-----------------------+---------------------------------------------------------------------------------------+
    | link_addr_to_fc_addr  | Converts a link address to a fibre channel address.                                   |
    +-----------------------+---------------------------------------------------------------------------------------+

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 4.0.1     | 06 Mar 2024   | Documentation updates only.                                                       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023, 2024 Consoli Solutions, LLC'
__date__ = '06 Mar 2024'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack@consoli-solutions.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.1'

import collections
import brcdapi.log as brcdapi_log
import brcdapi.gen_util as gen_util
import brcdapi.file as brcdapi_file

# Converts IBM device type to user-friendly name, 'd', and the generic type, 't'
# Note: These are the types as ordered from IBM. CECs log in to the fabric with the types in this table but devices log
# in with generic RNID data. Although all types I knew of at the time I wrote this are in this table, I've only used it
# to convert RNID log in data. Comments indicate the generic types.
_ibm_type = {
    # CECs
    '9672': dict(d='G5 & G6', t='CPU'),
    '2066': dict(d='z800', t='CPU'),
    '2064': dict(d='z900', t='CPU'),
    '2084': dict(d='z990', t='CPU'),
    '2086': dict(d='z890', t='CPU'),
    '2094': dict(d='z9 EC (z9-109)', t='CPU'),
    '2096': dict(d='z9 BC', t='CPU'),
    '2097': dict(d='z10 EC', t='CPU'),
    '2098': dict(d='z10 BC', t='CPU'),
    '2817': dict(d='z196', t='CPU'),
    '2818': dict(d='z114', t='CPU'),
    '2827': dict(d='EC12', t='CPU'),
    '2828': dict(d='BC12', t='CPU'),
    '2964': dict(d='z13', t='CPU'),
    '2965': dict(d='z13s', t='CPU'),
    '3906': dict(d='z14', t='CPU'),
    '3907': dict(d='z14s', t='CPU'),  # I guess. z14s not announced at the time I wrote this.
    '8561': dict(d='z15 T01', t='CPU'),
    '8562': dict(d='z15 T02', t='CPU'),
    '3931': dict(d='z16', t='CPU'),

    # CTC
    'FCTC': dict(d='CTC', t='CTC'),

    # DASD - RNID log in is generic
    '1750': dict(d='DS6800', t='DASD'),
    '3990': dict(d='3990', t='DASD'),
    '2105': dict(d='Model 800 DASD', t='DASD'),  # Generic
    '2107': dict(d='DASD', t='DASD'),  # Generic DS8000 but RNID data for all 8xxxx DASD is 2107
    '2396': dict(d='DS8870', t='DASD'),
    '2397': dict(d='DS8870', t='DASD'),
    '2398': dict(d='S8870', t='DASD'),
    '2399': dict(d='DS8870', t='DASD'),
    '2421': dict(d='DS8870', t='DASD'),
    '2422': dict(d='DS8870', t='DASD'),
    '2423': dict(d='DS8870', t='DASD'),
    '2424': dict(d='DS8870', t='DASD'),
    '5332': dict(d='DS8900F', t='DASD'),

    # Tape - I think the RNID login is as represented in this table
    '3480': dict(d='3480', t='Tape'),
    '4': dict(d='BTI Tape', t='Tape'),
    '3490': dict(d='3490 Tape', t='Tape'),
    '3494': dict(d='3494 Tape', t='Tape'),
    '3590': dict(d='3590 Tape', t='Tape'),
    '3592': dict(d='3592 Tape', t='Tape'),
    '3957': dict(d='TS77xx', t='Tape'),

    # Switches - RNID login is the generic 2499 but 2032 is in the IOCP for CUP
    '2005': dict(d='Brocade Gen2', t='Switch'),
    '2031': dict(d='6064', t='Switch'),
    '2032': dict(d='Switch', t='CUP'),
    '2053': dict(d='Cisco', t='Switch'),
    '2054': dict(d='Cisco', t='Switch'),
    '2061': dict(d='Cisco', t='Switch'),
    '2062': dict(d='Cisco', t='Switch'),
    '2109': dict(d='Brocade Gen3', t='Switch'),  # 2400, 2800, 48000
    '2498': dict(d='Brocade Gen5 Switch', t='Switch'),  # Fixed port switch
    '2499': dict(d='Brocade Gen5 Director', t='Switch'),  # Generic. Bladed (8510-8, 8510-4)
    '8960': dict(d='Brocade Gen6/7 Switch', t='Switch'),  # Fixed port (G720, G730, G630, G620, G610)
    '8961': dict(d='Brocade Gen6/7 Director', t='Switch'),  # Bladed (X7-8, X7-4, X6-8, X6-4)

    # Other
    '9074': dict(d='Secure Controller', t='IDG'),

    # Test
    'XTV': dict(d='XTV', t='Test'),  # Generic Switch. DCX, DCX-4S, 8510-8, 8510-4
    '3868': dict(d='3868', t='Test'),  # Generic Switch. DCX, DCX-4S, 8510-8, 8510-4
}
_rnid_flag = {
    0x00: 'Storage - Current',
    0x10: 'Channel - Current',
    0x20: 'Storage - Stale',
    0x30: 'Channel - Stale',
    0x40: 'Storage - Invalid',
    0x50: 'Channel - Invalid',
}
_sn_pad = (
    '000000000000',  # len(sn) is 0
    '00000000000',  # len(sn) is 1
    '0000000000',  # len(sn) is 2
    '000000000',  # len(sn) is 3
    '00000000',  # len(sn) is 4
    '0000000',  # len(sn) is 5
    '000000',  # len(sn) is 6
    '00000',  # len(sn) is 7
    '0000',  # len(sn) is 8
    '000',  # len(sn) is 9
    '00',  # len(sn) is 10
    '0'  # len(sn) is 11
)


def full_cpc_sn(sn):
    """Prepends a CPC SN with 0 such that it is padded to a full 12 character serial number to match RNID sequence.

    :param sn: Serial number
    :type sn: str
    :return: Padded serial number
    :rtype: str
    """
    return sn if len(sn) >= len(_sn_pad) else _sn_pad[len(sn)] + sn


def dev_type_desc(dev_type, inc_dev_type=True, inc_generic=True, inc_desc=True, prepend_text='', append_text=''):
    """Converts the RNID type to a human-readable device type

    :param dev_type: Device type. If None, '' is returned
    :type dev_type: int, str, None
    :param inc_dev_type: If True, include the device type
    :type inc_dev_type: bool
    :param inc_generic: If True, include the generic type, 't' in _ibm_type
    :type inc_generic: bool
    :param inc_desc: If True, include the generic description, 'd' in _ibm_type
    :type inc_desc: bool
    :param prepend_text: Text to prepend to the description. Typically, ' (' when inc_dev_type is True
    :type prepend_text: str
    :param append_text: Text to append to the description. Typically, ')' when inc_dev_type is True
    :return: Device type followed by description
    :rtype: str
    """
    global _ibm_type

    if dev_type is None:
        return ''

    # Sometimes the device type has leading '0' or it is hyphenated with additional detail that is not in _ibm_type
    generic_device_type = device_type = str(dev_type)
    while len(generic_device_type) > 4 and generic_device_type not in _ibm_type:
        x = generic_device_type.find('-')
        if x > 0:  # See if the hyphen messing things up
            generic_device_type = generic_device_type[0:x]
        elif generic_device_type[0] == '0':
            generic_device_type = generic_device_type[1:]
        else:
            break

    # Format the return string
    r_buf = device_type + prepend_text if inc_dev_type else prepend_text
    d = _ibm_type.get(generic_device_type)
    if d is None:
        brcdapi_log.log('RNID Type unknown: ' + device_type, False)
    if inc_desc or inc_generic:
        if d is None:
            r_buf += 'Unknown'
        else:
            if inc_generic:
                r_buf += d['t'] + ': ' if inc_desc else d['t']
            if inc_desc:
                r_buf += d['d']
    r_buf += append_text

    return r_buf


def dev_type_to_name(dev_type):
    """Converts the RNID type to a human-readable device type - Deprecated. Use dev_type_desc()

    :param dev_type: Device type
    :type dev_type: int, str
    :return: Device type
    :rtype: str
    """
    device_type = str(dev_type)
    device_type = device_type[0:4] if len(device_type) > 4 else device_type
    return _ibm_type[device_type]['d'] if device_type in _ibm_type else str(dev_type) + ' Unknown'


def _condition_iocp(iocp):
    """Puts all commands on a single line, strips out comments, extraneous white space, and any macro that is not CHPID
    or CNTLUNIT

    :param iocp: IOCP file read into a list
    :type iocp: list
    :return chpids: List of CHPID macros with everything after 'CHPID PATH='
    :rtype chpids: list
    :return cntlunits: List CNTLUNIT macros with everything after 'CNTLUNIT CUNUMBR='
    :rtype cntlunits: list
    """
    comment_flag = False  # When True, the next line is a continuation of a comment
    line_continue = False  # When True, the next line is a continuation of the previous line
    chpids = list()  # List of CHPID macros
    cntlunits = list()  # List of CNTLUNIT macros
    working_buf = ''  # The conditioned line
    cntlunit_flag = False  # In process of reading in a CNTLUNIT macro
    chpid_flag = False  # In process of reading a CHPID macro

    for buf in iocp:
        if not line_continue:
            working_buf = ''

        # Ignore comments
        # An '*' in the first position means the line is a comment. The comment may continue to the next line by putting
        # an '*' in column 72.
        if comment_flag:
            if not (len(buf) > 71 and buf[72] != ' '):
                comment_flag = False
            continue
        if len(buf) > 0 and buf[0] == '*':
            if len(buf) > 71 and buf[72] != ' ':
                comment_flag = True
            continue

        # If it's a line continuation, keep building the line and see if we're done
        if line_continue:
            working_buf += buf[0: 71]
            if len(buf) > 71 and buf[71] != ' ':
                continue
            working_buf = working_buf.strip().replace(' ', '')
            line_continue = False
            if chpid_flag:
                if 'TYPE=FC' in working_buf and 'SWITCH=' in working_buf:
                    # "PARTITION" is the only keyword I know of that is sometimes abreviated.
                    chpids.append(working_buf.replace('PART=', 'PARTITION='))
                chpid_flag = False
            elif cntlunit_flag:
                cntlunits.append(working_buf)
                cntlunit_flag = False
            else:
                brcdapi_log.exception('Programming error', True)
            continue

        temp_buf = buf.lstrip()
        if temp_buf[0: min(len('CHPID'), len(temp_buf))] == 'CHPID':
            working_buf += buf[0: 71]
            if len(buf) > 70 and buf[71] != ' ':
                line_continue = True
                chpid_flag = True
            elif 'TYPE=FC' in working_buf and 'SWITCH=' in working_buf:
                chpids.append(working_buf.strip().replace(' ', ''))
            continue

        x = buf.find('CNTLUNIT CUNUMBR=')
        if x >= 0:
            working_buf = ''.join(buf[0: 71][x + len('CNTLUNIT CUNUMBR='):].split())
            if len(buf) > 70 and buf[71] != ' ':
                line_continue = True
                cntlunit_flag = True
            else:
                cntlunits.append(working_buf.strip().replace(' ', ''))
            continue

    return chpids, cntlunits


def css_to_tag(css_list):
    """Parses a list of CSS into the first byte for the tag

    :param css_list: List of CSSs (list is of int)
    :type css_list: list
    :return tag: CSS formatted as the upper byte of the tag
    :rtype tag: str
    """
    css = 0  # The tag is a bit flag starting highest to lowest so CSS 0 is 0x80, CSS 1, 0x40, etc.
    for x in css_list:
        css |= 0x80 >> x
    tag = str(hex(css)).split('x')[1].upper()
    return '0' + tag if len(tag) == 1 else tag


def css_chpid_to_tag(chpid):
    """Parses a CSS(x,y)chpid into the equivalent tag

    :param chpid: CSS and CHPID, something like: (CSS(0,1),50, 60) or ((CSS(0),50, 60),(CSS(1),50, 60))
    :type chpid: str
    :return tag_list: List of CHPID and CSS formatted as tag
    :rtype tag_list: list
    :return buf: Remainder of anything in chpid that wasn't part of the CSS & CHPIDs
    :rtype buf: str
    """
    # The caller should have parsed everything up to the PATH= before calling this method so what we want is just the
    # portion of the chipid statements that contains the CSS and the CHPIDs. The first thing to do is figure out what
    # is CSS & CHPID and what is everything else

    # Get the tag - a 2 byte hex number where the CSS flags are the most significant byte followed by the CHPID
    working_buf, r_buf = gen_util.paren_content(chpid, True)
    # d is used to sort out what CSS goes with which CHPID. The same CHPIDs do not have to follow each CSS(x). It is
    # ordered because the control unit macro must match link addresses to the CHPIDs associated with these CSS in the
    # order of CHPIDs and LINK addresses in the control unit macro
    d = collections.OrderedDict()
    while 'CSS(' in working_buf:
        t_buf, working_buf = gen_util.paren_content(working_buf[working_buf.find('CSS(') + len('CSS'):], True)
        css_list = [int(c) for c in t_buf.split(',')]
        temp_l = working_buf[0: working_buf.find(')')].split(',') if ')' in working_buf else working_buf.split(',')
        for c in [c.upper() for c in temp_l if len(c) > 1]:
            cl = d.get(c)
            if cl is None:
                cl = list()
                d.update({c: cl})
            cl.extend(css_list)

    return [css_to_tag(v) + str(k).upper() for k, v in d.items()], r_buf


def tag_to_css_list(tag):
    """Converts a tag to a list of CSS bits

    :param tag: Tag from RNID data
    :type tag: str
    :return: List of CSS as integers
    :rtype: list
    """
    try:
        css = int(tag[0:2], 16)
    except ValueError:
        brcdapi_log.exception('Invalid tag. First byte of tag must be hex. Tag was: ' + tag)
        return list()
    except TypeError:
        brcdapi_log.exception('Invalid tag type. Tag must be str. Tag type was: ' + str(type(tag)))
        return list()

    css_list = list()
    i = 0x80
    for x in range(0, 8):
        if css & i:
            css_list.append(x)
        i >>= 1

    return css_list


def tag_to_text(tag):
    """Converts a CHPID tag to human-readable format (as displayed in the IOCP)

    :param tag: CHPID RNID tag
    :type tag: str
    :return: Text representing the CSS & CHPID. Example: CSS(0),50
    :rtype: str
    """
    return 'CSS(' + ','.join([str(i) for i in tag_to_css_list(tag)]) + '),' + tag[2:]


def tag_to_ind_tag_list(tag):
    """Returns a list of individual tags for a tag. For example: 'C0' is returned as a list of '80', '40'

    :param tag: CHPID RNID tag
    :type tag: str
    :return: List of tags. Example: tag == 'C0' is returned as a list of '80', '40'
    :rtype: list
    """
    return [css_to_tag([css]) for css in tag_to_css_list(tag)]


def rnid_flag_to_text(rnid_flag, flag=False):
    """Converts the RNID flag to human-readable text

    :param rnid_flag: RNID data flag (from: brocade-ficon/rnid/flags)
    :type rnid_flag: str, int
    :param flag: If True, includes the actual flag in parentheses
    :return: List of CSS
    :rtype: list
    """
    r_flag = int(rnid_flag, 16) if isinstance(rnid_flag, str) else rnid_flag
    buf = _rnid_flag[r_flag] if r_flag in _rnid_flag else 'Unkonwn'
    return buf + ' (' + hex(r_flag) + ')' if flag else buf


def _chpid_path(buf):
    tag_l, null_buf = css_chpid_to_tag(buf)
    return tag_l


def _chpid_true(buf):
    return True


def _chpid_null(buf):
    return


def _chpid_partition(buf):
    # All I care about with anything I parse the IOCP for a list of LPARs. The CSS doesn't have to be quite right
    buf_l = buf.replace('(', '').replace(')', '').replace('CSS', '').replace('=', '').split(',')
    return [b for b in buf_l if not b.isnumeric() and len(b) > 0]


def _chpid_simple(buf):
    return buf


def _chpid_pchid(buf):
    return buf


_key_word_action_l = dict(
    CHPID=_chpid_true,
    PATH=_chpid_path,
    SHARED=_chpid_true,
    PARTITION=_chpid_partition,
    SWITCH=_chpid_simple,
    NOTPART=_chpid_null,
    TYPE=_chpid_simple,
    PCHID=_chpid_pchid,
)


def _parse_chpid(chpid_macro):
    """Parses a CHPID macro

    :param chpid_macro: CHPID PATH macro
    :type chpid_macro: str
    :return tag: CHPID and CSS formatted as tag
    :rtype tag: list
    :return partition: List of partitions sharing this CHPID
    :rtype partition: list
    :return pchid: PCHID
    :rtype pchid: str
    :return switch: Switch ID
    :rtype switch: str
    """
    # Figure out where everything starts for each keyword
    keyword_l = list()  # List of dictionaries
    for key in _key_word_action_l.keys():
        i = chpid_macro.find(key)
        if i >= 0:
            keyword_l.append(dict(key=key, s=i))

    # Get the text associated with each key word
    keyword_l = sorted(keyword_l, key=lambda i: i['s'])  # Sort on the starting place for each keyword
    rd = dict()  # Using this to store the data to be returned
    x = len(keyword_l) - 1
    for i in range(0, x+1):
        d = keyword_l[i]
        buf = chpid_macro[d['s']+len(d['key']): keyword_l[i+1]['s'] if i < x else len(chpid_macro)]
        # Get rid of the leading '=' and trailing ','
        if len(buf) > 0 and buf[0] == '=':
            buf = buf[1:]
        if len(buf) > 0 and buf[len(buf)-1] == ',':
            buf = buf[0: len(buf)-1]
        rd.update({d['key']: _key_word_action_l[d['key']](buf)})

    return rd['PATH'], list() if rd.get('PARTITION') is None else rd.get('PARTITION'), rd['PCHID'], rd['SWITCH']


def _parse_cntlunit(cntlunit):
    """Parses a Control Unit macro

    Sample Control Unit Macro:
             CNTLUNIT CUNUMBR=0300,
               PATH=((CSS(0),F3,C7,C9),(CSS(1),F3,C7,C9)),
               UNITADD=((00,016)),
               LINK=((CSS(0),6304,0122,0122),(CSS(1),6304,0122,0122)),
               CUADD=0,UNIT=NOCHECK

    Returned dict:

    {
        cunumber: {         # CNTLUNIT CUNUMBR
            path: {}        # The keys are the CHPID tags and the values are the link address
            unitadd: []     # Intended for UNITADD. Not filled in this version - TBD
            cuadd: []       # Intended for CUADD. Not filled in this version - TBD
            unit: unit_type # unit_type is a str. Not filled in this version - TBD
            }
        ...
    }

    :param cntlunit: CNTLUNIT macro
    :type cntlunit: list
    :return: List of dict as defined above
    :rtype: dict
    """
    r = dict()
    for temp_cntl_macro in cntlunit:
        cntl_macro = temp_cntl_macro.upper()  # Not that I've ever seen lower case, but just in case.
        link_addr = dict()
        if 'LINK' in cntl_macro:

            """HCD allows link addresses to be on a subset of the CSS defined for a CHPID. Below assumes all link
            addresses are available to all CSS the CHPID is defined for. This means that if a report displays the
            CHPID along with the CSS, the CSS will be inaccurate but the CHPID will be correct. Only physical
            connectivity matters for zoning so getting the specific CSS doesn't matter.

            Each IOCP is added to the project using it's S/N as the key which contains dictionaries of CHPIDs whose
            key is tag defined in the CHPID macro. To create a list of CHPIDs that access a certain link address, all
            I have to do is look up the CHPIDs by the tag (which contains all CSS defined for the CHPID). If I didn't
            take this short cut, determining which CHPIDs had a path to which physical port would have been a more
            complex coding algorithm. The only benefit of a more complex approach would be that in the rare instance
            when link addresses where not shared across all CSS the CHPID spans would be the accuracy of the CSS in
            a report that no one uses for anything other than physical connectivity anyway.

            BTW - Mainframe people typically look at tags, CHPIDs, and link address all in upper case. Python keys are
            case sensitive. This is why I convert everything to upper case.

            If you don't understand what you just read, it's either a level of detail regarding the mainframe channel
            subsystem you don't need to know or you need to get help from someone who does. If you do understand this
            and are reading in earnest, its either because I overlooked something when I decided this short cut was
            good enough or you are trying to use these libraries for something they weren't intended to be used for."""

            cntl_unit = cntl_macro.split(',')[0]
            # Get the tag - a 2 byte hex number where the CSS flags are the most significant byte followed by the CHPID
            chpid_tag_list, working_buf = css_chpid_to_tag(cntl_macro[cntl_macro.find('PATH=') + len('PATH='):])
            links, working_buf = gen_util.paren_content(cntl_macro[cntl_macro.find('LINK=') + len('LINK='):], True)
            d = collections.OrderedDict()
            for k in chpid_tag_list:
                d.update({k: list()})  # List of link addresses associated with each CHPID

            """If a link address isn't associated with a CSS, it will just have a ,. For example, in link address 6304
            is only associated with CSS(1), it will look like:
            LINK=((CSS(0),,0122,0122),(CSS(1),6304,0122,0122))
            so despite all the commentary above about not associated link addresses with a CSS, I have to figure it out
            anyway because, as you can see in the above example, I could miss a path. It's just that I don't make this
            distinction when adding them to d (dict of CHPIDs by tag) which is what gets added to brcddb data base."""

            while 'CSS' in links:
                links = links[links.find('CSS') + len('CSS(x),'):]
                x = links.find(')')
                t_buf = links[0: x] if x >= 0 else links
                link_list = [c for c in t_buf.split(',')]
                for i in range(0, len(link_list)):
                    if link_list[i] not in d[chpid_tag_list[i]]:
                        d[chpid_tag_list[i]].append(link_list[i])

            # Fill out the dictionary for this control unit
            path = dict()
            for k, v in d.items():
                if len(v) > 0:
                    """I don't think HCD allows multiple link addresses to the same CU on the same CHPID so I expect
                    v to always be a list of 1 but for the little extra coding it takes to check, I figured I may as
                    well check. Although HCD doesn't permit it, if someone hand built an IOCP (some old timers still
                    do it and then import into HCD) with a CHPID defined to a control unit with no link addresses v
                    would be len 0. In days gone by, that was typically done as a place holder while someone was
                    building an IOCP. Basically WIP."""
                    path.update({k: v[0]})
            unitadd = list()  # WIP - Intent is to fill this out in the loop below
            cuadd = list()  # WIP
            unit = ''
            for buf in cntl_macro.split(','):
                cl = buf.split('=')
                if len(cl) > 1 and cl[0] == 'UNIT':
                    unit = cl[1]
                    break
            r.update({cntl_unit: {'path': path, 'unitadd': unitadd, 'cuadd': cuadd, 'unit': unit}})

    return r


def parse_iocp(proj_obj, iocp):
    """Parses an IOCP and adds the IOCP to the proj_obj

    :param proj_obj: Project object where collected data is to be added
    :type proj_obj: brcddb.classes.project.ProjectObj
    :param iocp: Name of the IOCP file to parse
    :type iocp: str
    """
    brcdapi_log.log('Parsing: ' + iocp, True)

    # Read in the IOCP definition file and get an IOCP object
    iocp_list = brcdapi_file.read_file(iocp, False, False)
    iocp_obj = proj_obj.s_add_iocp(iocp.split('/').pop().split('_')[0])

    # Parse the CHPID and CNTLUNIT macros
    chpid_l, cntlunit_l = _condition_iocp(iocp_list)

    # Create all the CHPID objects
    for chpid in chpid_l:
        tag_l, partition, pchid, switch_id = _parse_chpid(chpid)
        for chpid_tag in tag_l:
            iocp_obj.s_add_chpid(chpid_tag, partition, pchid, switch_id)

    # Parse and add all the control units to the CHPID paths
    control_units = _parse_cntlunit(cntlunit_l)
    # Figure out what the paths are and add them to the IOCP object
    for k, v in control_units.items():  # k is the CU number, v is a dict of the parsed CONTLUNIT macro
        for tag, link_addr in v['path'].items():
            try:
                iocp_obj.r_path_obj(tag, exact_match=False).s_add_path(link_addr, k, v['unit'])
            except AttributeError:
                # Every once in a while, someone gives me an IOCP that doesn't compile
                brcdapi_log.log('tag in CNTLUNIT macro, ' + tag + ', for link address ' + link_addr +
                                ' does not match any defined CHPIDs in ' + iocp, True)

    return


def link_addr_to_fc_addr(link_addr, switch_id=None, did=None, leading_0x=False):
    """Converts a link address to a fibre channel address.

    :param link_addr: FICON link address
    :type link_addr: str
    :param switch_id: Switch ID from IOCP - Only used with a single byte link address
    :param switch_id: str
    :param did: Only used if switch_id is None and link_addr is a single byte link address.
    :param leading_0x: If True, prepends '0x'
    :type leading_0x: bool
    """
    prefix = '0x' if leading_0x else ''
    if len(link_addr) == 2:
        prefix += hex(did)[2:] if switch_id is None else switch_id.lower()

    return prefix + link_addr.lower() + '00'
