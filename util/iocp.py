#!/usr/bin/python
# Copyright 2020, 2021 Jack Consoli.  All rights reserved.
#
# NOT BROADCOM SUPPORTED
#
# Licensed under the Apahche License, Version 2.0 (the "License");
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
:mod:`brcddb.util.iocp` - Utility functions for the brcddb libraries

**Important Notes**

There is a little error checking but most error checking was done to assist with debugging the script, not the IOCP. It
is assumed that the IOCP compiled on the host without error.

This initial incarnation of this routine used the built in PERL features for manuipulating strings and text but I kept
comming across nuances and syntax that I didn't expect. Keep in mind I'm not an expert at building an IOCP by hand. Most
customers today aren't either, they use HCD. What I ended up with here is a C like parser that is built on a state
machine. It's not very efficient but we don't need effeciency here. What I needed was tha ability to quickly and easily
identify a mistake in the script or something unexpected in the syntax.

Note that an IOCP is in old punch card format where certain characters in certain positions mean something. Rather than
re-invent the wheel, this was taken from an old Perl script and converted to Python. It certainly isn't elegant but it
is functional.

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch - 3.x to be consistent with other library version convention       |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 22 Aug 2020   | Fixed missing link addresses and added UNIT.                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.3     | 02 Sep 2020   | Handled condition whan CHPID is not immediately followed by PATH                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.4     | 26 Jan 2021   | Miscellaneous cleanup. No functional changes                                      |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020, 2021 Jack Consoli'
__date__ = '26 Jan 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.4'

import collections
import brcddb.brcddb_common as brcddb_common
import brcdapi.log as brcdapi_log
import brcddb.util.util as brcddb_util
import brcddb.util.file as brcddb_file

# Converts IBM device type to user friendly name, 'd', and the generic type, 't'
# Note: These are the types as ordered from IBM. CECs log in to the fabric with the types in this table but devices log
# in with generic RNID data. Although all types I knew of at the time I wrote this are in this table, I've only used it
# to convert RNID log in data. Comments indicate the generic types.
_ibm_type = {
    # CECs
    '9672': {'d': 'G5 & G6', 't': 'CPU'},
    '2066': {'d': 'z800', 't': 'CPU'},
    '2064': {'d': 'z900', 't': 'CPU'},
    '2084': {'d': 'z990', 't': 'CPU'},
    '2086': {'d': 'z890', 't': 'CPU'},
    '2094': {'d': 'z9 EC (z9-109)', 't': 'CPU'},
    '2096': {'d': 'z9 BC', 't': 'CPU'},
    '2097': {'d': 'z10 EC', 't': 'CPU'},
    '2098': {'d': 'z10 BC', 't': 'CPU'},
    '2817': {'d': 'z196', 't': 'CPU'},
    '2818': {'d': 'z114', 't': 'CPU'},
    '2827': {'d': 'EC12', 't': 'CPU'},
    '2828': {'d': 'BC12', 't': 'CPU'},
    '2964': {'d': 'z13', 't': 'CPU'},
    '2965': {'d': 'z13s', 't': 'CPU'},
    '3906': {'d': 'z14', 't': 'CPU'},
    '3907': {'d': 'z14s', 't': 'CPU'},	# I guess. z14s not announced at the time I wrote this.
    '8561': {'d': 'z15 T01', 't': 'CPU'},
    '8562': {'d': 'z15 T02', 't': 'CPU'},

    # CTC
    'FCTC': {'d': 'CTC', 't': 'CTC'},

    # DASD - RNID log in is generic
    '1750': {'d': 'DS6800', 't': 'DASD'},
    '3990': {'d': '3990', 't': 'DASD'},
    '2105': {'d': 'Model 800 DASD', 't': 'DASD'},  # Generic
    '2107': {'d': 'DS88xx DASD', 't': 'DASD'},  # Generic DS8000 but RNID data for all 8xxxx DASD is 2107
    '2396': {'d': 'DS8870', 't': 'DASD'},
    '2397': {'d': 'DS8870', 't': 'DASD'},
    '2398': {'d': 'S8870', 't': 'DASD'},
    '2399': {'d': 'DS8870', 't': 'DASD'},
    '2421': {'d': 'DS8870', 't': 'DASD'},
    '2422': {'d': 'DS8870', 't': 'DASD'},
    '2423': {'d': 'DS8870', 't': 'DASD'},
    '2424': {'d': 'DS8870', 't': 'DASD'},
    '5332': {'d': 'DS8900F', 't': 'DASD'},

    # Tape - I think the RNID login is as represented in this table
    '3480': {'d': '3480', 't': 'Tape'},
    '4': {'d': 'BTI Tape', 't': 'Tape'},
    '3490': {'d': '3480 Tape', 't': 'Tape'},
    '3494': {'d': '3480 Tape', 't': 'Tape'},
    '3590': {'d': '3590 Tape', 't': 'Tape'},
    '3592': {'d': '3592 Tape', 't': 'Tape'},
    '3957': {'d': 'TS77xx', 't': 'Tape'},

    # Switches - RNID login is the generic 2499
    '2005': {'d': 'Brocade Gen2', 't': 'Switch'},
    '2031': {'d': '6064', 't': 'Switch'},
    '2032': {'d': 'McData', 't': 'Switch'},  # This is all switch types in the IOCP. 6140 or i10K. Also old generic type
    '2053': {'d': 'Cisco', 't': 'Switch'},
    '2054': {'d': 'Cisco', 't': 'Switch'},
    '2061': {'d': 'Cisco', 't': 'Switch'},
    '2062': {'d': 'Cisco', 't': 'Switch'},
    '2109': {'d': 'Brocade Gen3', 't': 'Switch'},  # 2400, 2800, 48000
    '2498': {'d': 'Brocade Gen5 Switch', 't': 'Switch'},  # Fixed port (7800, 300, 5100, 5300, 6506, 6510, 6520 & Encyp Switch)
    '2499': {'d': 'Brocade Gen5 Director', 't': 'Switch'},  # Generic. Bladed (8510-8, 8510-4)
    '8960': {'d': 'Brocade Gen6 Switch', 't': 'Switch'},  # Fixed port (G630, G620, G610)
    '8961': {'d': 'Brocade Gen6 Director', 't': 'Switch'},  # Bladed (X6-8, X6-4)

    # Test
    'XTV': {'d': 'XTV', 't': 'Test'},  # Generic Switch. DCX, DCX-4S, 8510-8, 8510-4
    '3868': {'d': '3868', 't': 'Test'},  # Generic Switch. DCX, DCX-4S, 8510-8, 8510-4
}
_rnid_flag = {
    0x00: 'Storage - Current',
    0x10: 'Channel - Current',
    0x20: 'Storage - Stale',
    0x30: 'Channel - Stale',
    0x40: 'Storage - Invalid',
    0x50: 'Channel - Invalid',
}


def dev_type_to_name(dev_type):
    """Converts the RNID type to a human readable device type

    :param dev_type: Device type
    :type dev_type: int, str
    :return: Version
    :rtype: str
    """
    device_type = str(dev_type)
    device_type = device_type[0:4] if len(device_type) > 4 else device_type
    return _ibm_type[device_type]['d'] if device_type in _ibm_type else str(dev_type) + ' Unknown'

    return __version__


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
    line_continue = False  # When True, the next line is a contunuation of the previous line
    chpids = list()  # List of CHPID macros
    cntlunits = list()  # List of CNTLUNIT macros
    working_buf = ''  # The conditioned line
    cntlunit_flag = False  # In process of reading in a CNTLUNIT macro
    chpid_flag = False  # In process of reading a CHPID macro
    for buf in iocp:

        # Ignore comments
        if comment_flag:
            if not (len(buf) > 71 and buf[72] != ' '):
                comment_flag = False
            continue
        # An '*' in the first position means the line is a comment. The comment may continue to the next line by putting
        # an '*' in column 72.
        if len(buf) > 0 and buf[0] == '*':
            if len(buf) > 71 and buf[72] != ' ':
                comment_flag = True
            continue

        # If it's a line contiuation, keep building the line and see if we're done
        if line_continue:
            working_buf += buf[0: 71]
            if len(buf) > 71 and buf[71] != ' ':
                continue
            line_continue = False
            if chpid_flag:
                if 'TYPE=FC' in working_buf and 'SWITCH=' in working_buf:
                    chpids.append(brcddb_util.remove_duplicate_space(working_buf.strip()))
                chpid_flag = False
            elif cntlunit_flag:
                cntlunits.append(brcddb_util.remove_duplicate_space(working_buf.strip()))
                cntlunit_flag = False
            else:
                brcdapi_log.exception('Programming error', True)
            working_buf = ''
            continue

        temp_buf = buf.lstrip()
        if temp_buf[0: min(len('CHPID'), len(temp_buf))] == 'CHPID':
            working_buf += buf[0: 71]
            if (len(buf) > 70 and buf[71] != ' '):
                line_continue = True
                chpid_flag = True
            elif 'TYPE=FC' in working_buf and 'SWITCH=' in working_buf:
                chpids.append(brcddb_util.remove_duplicate_space(working_buf.strip()))
            continue

        x = buf.find('CNTLUNIT CUNUMBR=')
        if x >= 0:
            working_buf = ''.join(buf[0: 71][x + len('CNTLUNIT CUNUMBR='):].split())
            if (len(buf) > 70 and buf[71] != ' '):
                line_continue = True
                cntlunit_flag = True
            else:
                cntlunits.append(brcddb_util.remove_duplicate_space(working_buf.strip()))
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
    return str(hex(css)).split('x')[1].upper()


def css_chpid_to_tag(chpid):
    """Parses a CSS(x,y)chpid into the equivelent tag

    :param chpid: CSS and CHPID, something like: (CSS(0,1),50, 60) or ((CSS(0),50, 60),(CSS(1),50, 60))
    :type chpid: str
    :return tag_list: List of CHPID and CSS formatted as tag
    :rtype tag_list: list
    :return buf: Index to first character in buf past the CHPID/tag definitions
    :rtype buf: Remainder of anything in chpid that wasn't part of the CSS & CHPIDs
    """
    # The caller should have parsed everything up to the PATH= before calling this method so what we want is just the
    # portion of the chipid statements that contains the CSS and the CHPIDs. The first thing to do is figure out what
    # is CSS & CHPID and what is everything else

    # Get the tag - a 2 byte hex number where the CSS flags are the most significant byte followed by the CHPID
    working_buf, r_buf = brcddb_util.paren_content(chpid, True)
    # d is used to sort out what CSS goes with which CHPID. The same CHPIDs do not have to follow each CSS(x). It is
    # ordered because the control unit macro must match link addresses to the CHPIDs associated with these CSS in the
    # order of CHPIDs and LINK addresses in the control unit macro
    d = collections.OrderedDict()
    css_list = list()
    while 'CSS(' in working_buf:
        t_buf, working_buf = brcddb_util.paren_content(working_buf[working_buf.find('CSS(') + len('CSS'):], True)
        css_list = [int(c) for c in t_buf.split(',')]
        l = working_buf[0: working_buf.find(')')].split(',') if ')' in working_buf else working_buf.split(',')
        for c in [c.upper() for c in l if len(c) > 1]:
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
    :return: List of CSS
    :rtype: list
    """
    try:
        css = int(tag[0:2], 16)
    except:
        return list()

    css_list = list()
    i = 0x80
    for x in range(0, 8):
        if css & i:
            css_list.append(x)
        i >>= 1

    return css_list


def rnid_flag_to_text(rnid_flag, flag=False):
    """Converts a tag to a list of CSS bits

    :param rnid_flag: RNID data flag (from: brocade-ficon/rnid/flags)
    :type rnid_flag: str, int
    :param flag: If True, includes the actual flag in parenthesis
    :return: List of CSS
    :rtype: list
    """
    r_flag = int(rnid_flag, 16) if isinstance(rnid_flag, str) else rnid_flag
    buf = _rnid_flag[r_flag] if r_flag in _rnid_flag else 'Unkonwn'
    return buf + ' (' + hex(r_flag) + ')' if flag else buf


def _parse_chpid(chpid):
    """Parses a CHPID macro

    :param chpid: CHPID PATH macro
    :type chpid: str
    :return tag: CHPID and CSS formatted as tag
    :rtype tag: str
    :return partition: List of partitions sharing this CHPID
    :rtype partition: list
    :return pchid: PCHID
    :rtype pchid: str
    :return switch: Switch ID
    :rtype switch: str
    """
    tag = ''
    partition = list()
    pchid = ''
    switch = ''

    # Sample CHPID macro: CHPID PATH=(CSS(0),50),SHARED,PARTITION=((SYJ3,SYJ4),(=)),SWITCH=F4,PCHID=168,TYPE=FC
    # Note that 'CHPID PATH=' is already stripped off so we just have: (CSS(0),4D),SHARED,PARTITION...
    try:

        # Tack on 'xxx=xxx' so I don't have handle any elements at the end as a special case.
        # Get the SWITCH, PARTITION and PCHID
        x = 0
        temp_l = (chpid + ',xxx=xxx').split('=')
        for buf in temp_l:
            if x + 1 >= len(temp_l):
                break
            next_buf = temp_l[x+1]

            if 'PATH' in buf:
                l, dummy_buf = css_chpid_to_tag(next_buf)
                tag = l[0]

            if 'PARTITION' in buf:
                i = 0  # I've seen anywhwere from 0 to 2 '(' so just skip through them all
                for chr in next_buf:
                    if chr != '(':
                        break
                    i += 1
                partition = next_buf[i: next_buf.find(')')].split(',')
            elif 'PCHID' in buf:
                pchid = next_buf.split(',')[0]
            elif 'SWITCH' in buf:
                switch = next_buf.split(',')[0]
            x += 1

    except:
        brcdapi_log.exception('Unknown CHPID macro format:\n' + chpid, True)

    return tag, partition, pchid, switch


def _parse_cntlunit(cntlunit):
    """Parses a Control Unit macro

    Sample Control Unit Macro:
             CNTLUNIT CUNUMBR=0300,
               PATH=((CSS(0),F3,C7,C9),(CSS(1),F3,C7,C9)),
               UNITADD=((00,016)),
               LINK=((CSS(0),6304,0122,0122),(CSS(1),6304,0122,0122)),
               CUADD=0,UNIT=NOCHECK

    Retruned dict:

    {
        cunumber: {         # CNTLUNIT CUNUMBR
            path: {}        # The keys are the CHPID tags and the values are the link address
            unitadd: []     # Intended for UNITADD. Not filled in in this version - TBD
            cuadd: []       # Intended for CUADD. Not filled in in this version - TBD
            unit: unit_type # unit_type is a str. Not filled in in this version - TBD
            }
        ...
    }

    :param cntlunit: CNTLUNIT macro
    :type cntlunit: str
    :return: List of dict as defined above
    :rtype: dict
    """
    r = dict()
    for temp_cntl_macro in (cntlunit):
        cntl_macro = temp_cntl_macro.upper()  # Not that I've ever seen lower case, but just in case.
        link_addr = dict()
        if 'LINK' in cntl_macro:
            # HCD allows link addresses to be on a subset of the CSS defined for a CHPID. Below assumes all link
            # addresses are available to all CSS the CHPID is defined for. This means that if a report displays the
            # CHPID along with the CSS, the CSS will be inaccurate but the CHPID will be correct. Only physical
            # connectivity matters for zoning so getting the specific CSS doesn't matter.
            #
            # Each IOCP is added to the project using it's S/N as the key which contains dictionaries of CHPIDs whose
            # key is tag defined in the CHPID macro. To create a list of CHPIDs that access a certain link address, all
            # I have to do is look up the CHPIDs by the tag (which contains all CSS defined for the CHPID). If I didn't
            # take this short cut, determining which CHPIDs had a path to which physical port would have been a more
            # complex coding algorithm. The only benefit of a more complex approach would be that in the rare instance
            # when link addresses where not sharred across all CSS the CHPID spans would be the accuracy of the CSS in
            # a report that no one uses for anything other than physical connectivity anyway.

            # BTW - Mainframe people typically look at tags, CHPIDs, and link address all in upper case. Python keys are
            # case sensitive. This is why I convert everything to upper case.
            #
            # If you don't understand what you just read, it's either a level of detail regarding the mainframe channel
            # subsystem you don't need to know or you need to get help from soneone who does. If you do understand this
            # and are reading in earnest, its either because I overlooked something when I decided this short cut was
            # good enough or you are trying to use these libraries for something they weren't intended to be used for.

            cntl_unit = cntl_macro.split(',')[0]
            # Get the tag - a 2 byte hex number where the CSS flags are the most significant byte followed by the CHPID
            chpid_tag_list, working_buf = css_chpid_to_tag(cntl_macro[cntl_macro.find('PATH=') + len('PATH='):])
            links, working_buf = brcddb_util.paren_content(cntl_macro[cntl_macro.find('LINK=') + len('LINK='):], True)
            d = collections.OrderedDict()
            for k in chpid_tag_list:
                d.update({k: list()})  # List of link addresses associated with each CHPID
            # If a link address isn't associated with a CSS, it will just have a ,. For example, in link address 6304 is
            # only associated with CSS(1), it will look like:
            # LINK=((CSS(0),,0122,0122),(CSS(1),6304,0122,0122))
            # so despite al the commentary above about not associated link addresses with a CSS, I have to figure it out
            # anyway because, as you can see in the above example, I could miss a path. It's just that I don't make this
            # distinction when adding them to d (dict of CHPIDs by tag) which is what gets added to brcddb data base.
            while 'CSS' in links:
                links = links[links.find('CSS') + len('CSS(x),'):]
                t_buf = links[0: links.find(')')]
                link_list = [c for c in t_buf.split(',')]
                for i in range(0, len(link_list)):
                    if link_list[i] not in d[chpid_tag_list[i]]:
                        d[chpid_tag_list[i]].append(link_list[i])

            # Fill out the dict for this control unit
            path = dict()
            for k, v in d.items():
                if len(v) > 0:
                    # I don't think HCD allows multiple link addresses to the same CU on the same CHPID so I expect
                    # v to always be a list of 1 but for the little extra coding it takes to check, I figured I may as
                    # well check. Although HCD doesn't permit it, if someone hand built an IOCP (some old timers still
                    # do it and then import into HCD) with a CHPID defined to a control unit with no link addresses v
                    # would be len 0. In days gone by, that was typically done as a place holder while someone was
                    # builing an IOCP. Basically WIP just as I've done below.
                    path.update({k: v[0]})
            cl = working_buf.split(',')
            unitadd = list()  # WIP
            cuadd = list()  # WIP
            unit = ''
            for i in range(0, len(cl)):
                if 'UNIT=' in cl[i] and len(cl) > i:
                    unit = cl[i].split('=')[1]
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
    # Read in the IOCP definition file and get an IOCP object
    iocp_list = brcddb_file.read_file(iocp, False, False)
    iocp_obj = proj_obj.s_add_iocp(iocp.split('/').pop().split('_')[0])

    # Parse the CHPID and CNTLUNIT macros
    chpids, cntlunits = _condition_iocp(iocp_list)
    control_units = _parse_cntlunit(cntlunits)

    # Add the control unit definitions to the IOCP object
    for k, v in control_units.items():
        iocp_obj.s_add_cu(k, v)

    # Figure out what the paths are and add them to the IOCP object
    path_d = dict()
    for chpid in chpids:
        chpid_path = dict()
        tag, chpid_path['partition'], chpid_path['pchid'], chpid_path['switch'] = _parse_chpid(chpid)
        link_addr = list()
        cu = list()
        for k, v in control_units.items():  # k is the control unit number, v is a dict of the parsed CONTLUNIT macro
            path = v.get('path')
            if path is not None:  # I don't know why it would ever be None but just in case:
                if tag in path:
                    if path[tag] not in link_addr:
                        # Think of a control unit as a LUN. You can have multiple CUs behind the same address
                        link_addr.append(path[tag])
                    cu.append(k)
        chpid_path['link'] = link_addr
        iocp_obj.s_add_path(tag, chpid_path)
