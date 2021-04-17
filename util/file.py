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
:mod:`brcddb.util.file` - File operation methods

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-6   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021 Jack Consoli'
__date__ = '17 Apr 2021'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.6'

import brcdapi.log as brcdapi_log
import json
from os import listdir
from os.path import isfile, join
from os import stat
from pathlib import Path

def write_dump(obj, file):
    """Creates a file using json.dumps. Typical use is to convert a project object with brcddb_to_plain_copy to a plain
    Python dict.
    :param obj: Dictionary to write to file
    :type obj: dict, list
    :param file: Name of file to write to
    :type file: str
    :rtype: None
    """
    brcdapi_log.log('CALL: brcddb_util.write_dump. File: ' + file)
    with open(file, 'w') as f:
        f.write(json.dumps(obj, sort_keys=True))
    f.close()


def read_dump(file):
    """Reads in a file using json.load. Typical use is to read back in a project object file writen with write_dump and
    then convert back to a project object with plain_copy_to_brcddb_copy
    Python dict.
    :param file: Name of file to write to
    :type file: str
    :return:
    :rtype: dict, list, None
    """
    brcdapi_log.log('CALL: brcddb_util.read_dump. File: ' + file)
    f = open(file, 'r')
    obj = json.load(f)
    f.close()
    return obj


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
        return list()


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
    return [buf for buf in rl if len(buf) > 0] if remove_blank else [buf for buf in rl]


def read_full_directory(folder):
    """Beginning with file, reads the full content of a folder and puts all file names and stats in a list of dict

    Structure for returned dict is:

    +-----------+-------+-----------------------------------------------+
    | key       | type  | Description                                   |
    +===========+=======+===============================================+
    | name      | str   | File name                                     |
    +-----------+-------+-----------------------------------------------+
    | folder    | str   | Folder name, relative to passed param folder  |
    +-----------+-------+-----------------------------------------------+
    | st_atime  | float | Last access time (epoch time)                 |
    +-----------+-------+-----------------------------------------------+
    | st_ctime  | float | Creation time (epoch time)                    |
    +-----------+-------+-----------------------------------------------+
    | st_mtime  | float | Last time modified (epoch time)               |
    +-----------+-------+-----------------------------------------------+
    | st_size   | int   | File size in bytes                            |
    +-----------+-------+-----------------------------------------------+
    | st_mode   | int   | File mode, see os.stat()                      |
    +-----------+-------+-----------------------------------------------+
    | st_ino    | int   | File mode, see os.stat()                      |
    +-----------+-------+-----------------------------------------------+
    | st_dev    | int   | File mode, see os.stat()                      |
    +-----------+-------+-----------------------------------------------+
    | st_nlink  | int   | File mode, see os.stat()                      |
    +-----------+-------+-----------------------------------------------+
    | st_uid    | int   | File mode, see os.stat()                      |
    +-----------+-------+-----------------------------------------------+
    | st_gid    | int   | See os.stat()                                 |
    +-----------+-------+-----------------------------------------------+

    :param folder: Name of the directory to read
    :type folder: str
    :return: List of files.
    :rtype: list
    """

    rl = list()
    try:
        for file in read_director(folder):
            stats = stat(folder + '/' + file)
            rl.append(dict(
                name=file,
                folder=folder,
                st_atime=stats.st_atime,
                st_ctime=stats.st_ctime,
                st_mtime=stats.st_mtime,
                st_size=stats.st_size,
                st_mode=stats.st_mode,
                st_ino=stats.st_ino,
                st_dev=stats.st_dev,
                st_nlink=stats.st_nlink,
                st_uid=stats.st_uid,
                st_gid=stats.st_gid
            ))
        for new_dir in [file for file in [f for f in listdir(folder) if listdir(join(folder, f))] if '~$' not in file]:
            rl.extend(read_full_directory(folder + '/' + new_dir))
    except:
        pass

    return rl
