#!/usr/bin/env python
" foo "

from __future__ import print_function
import re
import json

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
        print("In Section `{sec}', an entry is missing required key `{key}'.".format(
            sec=section,
            key=key
        ))
        return False
    if not match_type(data_value, ref_dict["type"]):
        # print(match_type(data_value, ref_dict["type"]))
        print("In Section `{sec}', entry `{key}={value}' is not of type `{type}'.".format(
            sec=section,
            value=data_value,
            key=key,
            type=ref_dict["type"]))
        return False
    if "py_re" in ref_dict and not re.match(ref_dict["py_re"], data_value):
        print("regex fail")
        return False
    return True

def validate_section(data_section, ref_section, section):
    """
    Validates a section (e.g. global, capture, etc.).
    """
    if ref_section["required"] and data_section is None:
        print("Required section `{sec}' not found.".format(sec=section))
        return False
    if ref_section["type"] == "dict":
        if not isinstance(data_section, dict):
            print("Section `{sec}' exists, but is not a dict.".format(sec=section))
            return False
        return all((
            validate_key(
                data_section.get(key),
                ref_section["keys"].get(key),
                section, key) for key in ref_section["keys"]))
    if ref_section["type"] == "dict_list":
        if not isinstance(data_section, list):
            print("Section `{sec}' exists, but is not a list of dicts.".format(sec=section))
            return False
        if not all((isinstance(x, dict) for x in data_section)):
            return False
        for chunk in data_section:
            if not all((
                    validate_key(
                        chunk.get(key),
                        ref_section["keys"].get(key),
                        section, key) for key in ref_section["keys"])):
                return False
    return True

def validate(data, ref=None):
    """
    docstring for validate

    data, ref: dicts
    """
    if ref is None:
        ref = json.load(open('schema.json'))
    return all((validate_section(data.get(key), ref.get(key), key) for key in ref))

if __name__ == "__main__":
    data_dict_ = json.load(open("../example_metadata_clean.json"))
    ref_dict_ = json.load(open("schema.json"))
    print(validate(data_dict_, ref_dict_))

				# "py_re": "^(?:[1-9]\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:Z|[+-][01]\d:[0-5]\d)$"

				# "py_re": "\d+\.\d+\.\d+"
