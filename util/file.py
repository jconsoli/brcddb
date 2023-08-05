# Copyright 2023 Consoli Solutions, LLC.  All rights reserved.
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
    | 4.0.0     | 04 Aug 2023   | Re-Launch                                                                         |
    +-----------+---------------+-----------------------------------------------------------------------------------+
"""

__author__ = 'Jack Consoli'
__copyright__ = 'Copyright 2023 Consoli Solutions, LLC'
__date__ = '04 August 2023'
__license__ = 'Apache License, Version 2.0'
__email__ = 'jack_consoli@yahoo.com'
__maintainer__ = 'Jack Consoli'
__status__ = 'Released'
__version__ = '4.0.0'

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
