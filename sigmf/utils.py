# Copyright 2016 GNU Radio Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Utilities
"""

from copy import deepcopy
from datetime import datetime

from six import iteritems


SIGMF_DATETIME_ISO8601_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def get_sigmf_iso8601_datetime_now():
    return datetime.isoformat(datetime.utcnow()) + 'Z'


def parse_iso8601_datetime(datestr):
    return datetime.strptime(datestr, SIGMF_DATETIME_ISO8601_FMT)


def dict_merge(a_dict, b_dict):
    """
    Recursively merge b_dict into a_dict. b_dict[key] will overwrite a_dict[key] if it exists.
    """
    if not isinstance(b_dict, dict):
        return b_dict
    result = deepcopy(a_dict)
    for key, value in iteritems(b_dict):
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

def insert_sorted_dict_list(dict_list, new_entry, key, force_insertion=False):
    """
    Insert new_entry (which must be a dict) into a sorted list of other dicts.
    If force_insertion is True, new_entry will NOT overwrite an existing entry
    with the same key.
    Returns the new list, which is still sorted.
    """
    for index, entry in enumerate(dict_list):
        if not entry:
            continue
        if entry[key] == new_entry[key] and not force_insertion:
            dict_list[index] = dict_merge(entry, new_entry)
            return dict_list
        if entry[key] > new_entry[key]:
            dict_list.insert(index, new_entry)
            return dict_list
    dict_list = dict_list + [new_entry]
    return dict_list

def get_schema_path(module_path):
    """
    """
    return module_path
