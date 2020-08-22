#!/usr/bin/python
# Copyright 2019, 2020 Jack Consoli.  All rights reserved.
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
:mod:`brcddb.util.file` - File operation methods

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 1.x.x     | 03 Jul 2019   | Experimental                                                                      |
    | 2.x.x     |               |                                                                                   |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1     | 02 Aug 2020   | PEP8 Clean up                                                                     |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.2     | 22 Aug 2020   | Stripped non-ascii characters and added blank line option in read_file()          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2019, 2020 Jack Consoli'
__date__ = '22 Aug 2020'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.2'

import brcdapi.log as brcdapi_log
import json
from os import listdir
from os.path import isfile, join


def write_dump(obj, file):
    """Creates a file using json.dumps. Typical use is to convert a project object with brcddb_to_plain_copy to a plain
    Python dict.
    :param obj: Dictionary to write to file
    :type obj: dict
    :param file: Name of file to write to
    :type file: str
    :rtype: None
    """
    # Debug
    with open(file, 'w') as f:
        f.write(json.dumps(obj, sort_keys=True))
    f.close()
    return

    brcdapi_log.log('CALL: brcddb_util.write_dump. File: ' + file)
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(obj, sort_keys=True))
        f.close()
    except:
        brcdapi_log.log('Unable to open file: ' + file, True)


def read_dump(file):
    """Reads in a file using json.load. Typical use is to read back in a project object file writen with write_dump and
    then convert back to a project object with plain_copy_to_brcddb_copy
    Python dict.
    :param file: Name of file to write to
    :type file: str
    :return:
    :rtype: dict, None
    """
    brcdapi_log.log('CALL: brcddb_util.read_dump. File: ' + file)
    try:
        f = open(file, 'r')
        obj = json.load(f)
        f.close()
        return obj
    except:
        brcdapi_log.log('Unable to open file: ' + file, True)
        return None


def read_director(folder):
    """Reads in the contents of a folder (directory) and return the list of files only (no directories) in that folder
    
    :param folder: Name of the folder
    :type folder: str
    :return: List of file names in the folder. List is empty if the folder doesn't exist
    :rtype: str
    """
    try:
        # Filtering out '~$' is to remove left over junk from Windows that is not actually in the directory
        return [file for file in [f for f in listdir(folder) if isfile(join(folder, f))] if '~$' not in file]
    except:
        return []


def read_file(file, remove_blank=True, rc=True):
    """Reads a file, comments and blank lines removed, and trailing white space removed into a list

    :param file: Name of file to read
    :type file: str
    :param remove_blank: If True, blank lines are removed
    :type remove_blank: bool
    :param remove_comments: If True, remove anything begining with # to the end of line
    :type rc: bool
    :return: List of file file contents.
    :rtype: list
    """
    # Apparently Putty puts some weird characters in the file. Looks like there is a Python bug with the line below. I
    # get "NameError: name 'open' is not defined.
    # f = oepn(file, 'r', encoding='utf-8', errors='ignore')
    #  So I read as bytes, decoded using utf-8 and then had to ignore errors.
    f = open(file, 'rb')
    data = f.read().decode('utf-8', errors='ignore')
    f.close()
    content = data.replace('\r', '').split('\n')
    rl = [buf[:buf.find('#')].rstrip() if buf.find('#') >= 0 else buf.rstrip() for buf in content] if rc else content
    return [buf for buf in rl if len(buf) > 0] if remove_blank else rl
