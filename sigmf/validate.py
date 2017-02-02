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
" SigMF Validation routines "

from __future__ import print_function
import re
import json

class ValidationResult(object):
    " Amends a validation result (True, False) with an error string. "
    def __init__(self, value=False, error=None):
        self.error = error
        self.value = value

    def __bool__(self):
        return self.value
    __nonzero__ = __bool__


def match_type(value, our_type):
    " Checks if value matches our_type "
    return value is None or {
        'string': lambda x: isinstance(x, str) or isinstance(x, unicode), # FIXME make py3k compatible
        'uint': lambda x: isinstance(x, int) and x >= 0,
        'double': lambda x: isinstance(x, float) or isinstance(x, int),
    }[our_type](value)


def validate_key(data_value, ref_dict, section, key):
    """
    Validates a data entry in a chunk.
    """
    if ref_dict["required"] and data_value is None:
        return ValidationResult(
            False,
            "In Section `{sec}', an entry is missing required key `{key}'.".format(
                sec=section,
                key=key
            ))
    if not match_type(data_value, ref_dict["type"]):
        return ValidationResult(
            False,
            "In Section `{sec}', entry `{key}={value}' is not of type `{type}'.".format(
                sec=section,
                value=data_value,
                key=key,
                type=ref_dict["type"]
            ))
    if "py_re" in ref_dict and not re.match(ref_dict["py_re"], data_value):
        return ValidationResult(False, "regex fail")
    return True

def validate_section(data_section, ref_section, section):
    """
    Validates a section (e.g. global, capture, etc.).
    """
    if ref_section["required"] and data_section is None:
        return ValidationResult(
            False,
            "Required section `{sec}' not found.".format(sec=section)
        )
    if ref_section["type"] == "dict":
        if not isinstance(data_section, dict):
            return ValidationResult(
                False,
                "Section `{sec}' exists, but is not a dict.".format(sec=section)
            )
        key_validation_results = (
            validate_key(
                data_section.get(key),
                ref_section["keys"].get(key),
                section, key
            ) for key in ref_section["keys"]
        )
        for result in key_validation_results:
            if not bool(result):
                return result
    if ref_section["type"] == "dict_list":
        if not isinstance(data_section, list) or \
                not all((isinstance(x, dict) for x in data_section)):
            return ValidationResult(
                False,
                "Section `{sec}' exists, but is not a list of dicts.".format(sec=section)
            )
        for chunk in data_section:
            if not all((
                    validate_key(
                        chunk.get(key),
                        ref_section["keys"].get(key),
                        section, key) for key in ref_section["keys"])):
                return ValidationResult(False, "missing keys yo")
    return True

def validate(data, ref=None):
    """
    docstring for validate

    data, ref: dicts
    """
    if ref is None:
        from sigmf import default_schema
        ref = default_schema.get_default_schema()
    for result in (validate_section(data.get(key), ref.get(key), key) for key in ref):
        if not result:
            return result
    return True

if __name__ == "__main__":
    data_dict_ = json.load(open("../example_metadata_clean.json"))
    ref_dict_ = json.load(open("schema.json"))
    print(validate(data_dict_, ref_dict_))

				# "py_re": "^(?:[1-9]\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:Z|[+-][01]\d:[0-5]\d)$"

				# "py_re": "\d+\.\d+\.\d+"
