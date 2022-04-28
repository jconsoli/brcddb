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
:mod:`brcddb.util.file` - Moved to brcdapi.file

Version Control::

    +-----------+---------------+-----------------------------------------------------------------------------------+
    | Version   | Last Edit     | Description                                                                       |
    +===========+===============+===================================================================================+
    | 3.0.0     | 19 Jul 2020   | Initial Launch                                                                    |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.1-6   | 17 Apr 2021   | Miscellaneous bug fixes.                                                          |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.7     | 14 May 2021   | Added permissions to read_full_directory()                                        |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.8     | 31 Dec 2021   | Added full_file_name()                                                            |
    +-----------+---------------+-----------------------------------------------------------------------------------+
    | 3.0.9     | 28 Apr 2022   | Moved to brcdapi                                                                  |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""
__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2020, 2021, 2022 Jack Consoli'
__date__ = '28 Apr 2022'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack.consoli@broadcom.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '3.0.9'

import json
import os
import brcdapi.log as brcdapi_log
import brcdapi.file as brcdapi_file


def write_dump(obj, file):
    return brcdapi_file.write_dump(obj, file)


def read_dump(file):
    return brcdapi_file.read_dump(file)


def read_directory(folder):
    return brcdapi_file.read_directory(folder)


def read_director(folder):
    """To support old misspelled method name."""
    return brcdapi_file.read_directory(folder)


def read_file(file, remove_blank=True, rc=True):
    return brcdapi_file.read_file(file, remove_blank, rc)


def file_properties(folder, file):
    return brcdapi_file.file_properties(folder, file)


def read_full_directory(folder, skip_sys=False):
    return brcdapi_file.read_full_directory(folder, skip_sys)


def full_file_name(file, extension, prefix=None):
    return brcdapi_file.full_file_name(file, extension, prefix)
