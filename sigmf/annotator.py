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
Formatter Object
"""

import os
import json
from six import iteritems
from .utils import dict_merge, insert_sorted_dict_list
# from .validate import v

def get_default_metadata(schema):
    """
    Return a valid annotation object based on defaults.
    """
    def get_default_dict(keys_dict):
        " Return a dict with all default values from keys_dict "
        return {
            key: desc.get("default")
            for key, desc in iteritems(keys_dict)
            if "default" in desc
        }
    def default_category_data(cat_type, defaults):
        " Return a valid data type for a category "
        return {
            'dict': lambda x: x,
            'dict_list': lambda x: [x],
        }[cat_type](defaults)
    return {
        category: default_category_data(desc["type"], get_default_dict(desc["keys"]))
        for category, desc in iteritems(schema)
    }

class SigMF(object):
    """
    API to manipulate annotation files.

    Parameters:
    metadata_file -- Path to an annotation file (required). If it does not
                     exist, it will be created. If it can't be read or accessed,
                     an error will be thrown.
    data_file     -- Path to the corresponding data file (optional).
    global_info   -- Dictionary containing global header info.
    """
    START_INDEX_KEY = "core:sample_start"
    LENGTH_INDEX_KEY = "core:sample_length"

    def __init__(
            self,
            metadata_file,
            data_file=None,
            global_info=None,
    ):
        self.metadata_file = metadata_file
        if os.path.isfile(self.metadata_file):
            self._metadata = json.load(open(self.metadata_file))
        else:
            # FIXME no hardcodery
            default_schema = json.load(open("caf/schema.json"))
            self._metadata = get_default_metadata(default_schema)
        if global_info is not None:
            self.set_global_info(global_info)
        self.data_file = data_file

    def set_global_info(self, new_global):
        """
        Overwrite the global info with a new dictionary.

        TODO: Validate
        """
        self._metadata["global"] = new_global

    def add_global_field(self, key, value):
        """
        Inserts a value into the global fields.

        TODO: Validate
        """
        self._metadata["global"][key] = value

    def add_capture(self, start_index, metadata=None):
        """
        Insert capture info

        TODO: fail if index already exists
        TODO: Validate metadata
        """
        assert start_index >= self._metadata.get("global", {}).get("core:offset", 0)
        metadata[self.START_INDEX_KEY] = start_index
        self._metadata["capture"] = insert_sorted_dict_list(
            self._metadata.get("capture", []),
            metadata,
            self.START_INDEX_KEY,
        )

    def add_annotation(self, start_index, length, metadata):
        """
        Insert annotation

        TODO: Validate
        """
        assert start_index >= self._metadata.get("global", {}).get("core:offset", 0)
        assert length > 1
        metadata[self.START_INDEX_KEY] = start_index
        metadata[self.LENGTH_INDEX_KEY] = length
        self._metadata["annotation"] = insert_sorted_dict_list(
            self._metadata.get("annotation", []),
            metadata,
            self.START_INDEX_KEY,
        )

    def get_global_info(self):
        """
        Returns a dictionary with all the global info.
        """
        return self._metadata.get("global", {})

    def get_capture_info(self, index):
        """
        Returns a dictionary containing all the capture information at sample
        'index'.
        """
        start_offset = self._metadata.get("global", {}).get("core:offset", 0)
        assert index >= start_offset
        captures = self._metadata.get("capture", [])
        assert len(captures) > 0
        cap_info = captures[0]
        for capture in captures:
            if capture[self.START_INDEX_KEY] > index:
                break
            cap_info = dict_merge(cap_info, capture)
        return cap_info

    def get_annotations(self, index):
        """
        Returns a list of dictionaries.
        Every dictionary contains one annotation for the sample at 'index'.
        """
        return [
            x for x in self._metadata.get("annotation", [])
            if x[self.START_INDEX_KEY] <= index
            and x[self.START_INDEX_KEY] + x[self.LENGTH_INDEX_KEY] > index
        ]

    def validate(self):
        """
        Return True if this is valid.
        """
        return True

