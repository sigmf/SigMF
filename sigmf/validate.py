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

'''SigMF Validator'''

from . import schema

import json


class ValidationResult(object):
    '''Amends a validation result (True, False) with an error string.'''
    def __init__(self, value=False, error=None):
        self.error = error
        self.value = value

    def __bool__(self):
        return self.value
    __nonzero__ = __bool__

    def __str__(self):
        if self.value or self.error is None:
            return str(self.value)
        return str(self.error)


def match_type(value, our_type):
    '''Checks if value matches our_type'''
    return value is None or {
        'string': lambda x: isinstance(x, str),
        'uint': lambda x: isinstance(x, int) and x >= 0,
        'double': lambda x: isinstance(x, float) or isinstance(x, int),
    }[our_type](value)


def validate_key(data_value, ref_dict, section, key):
    '''
    Validates a key/value pair entry in a chunk.

    Parameters
    ----------
    data_value
        Valid or invaid entry in metadata for validation.
    ref_dict: dict
        A dictionary containing reference information.
    section: str
        The section in which this key/value pair is stored ("global", etc.).
        This is for better error reporting only.
    key: str
        The key of this key/value pair ("core:Version", etc.). This is for better error reporting only.

    Returns
    -------
    True or ValidationResult
    '''
    if ref_dict.get('required') and data_value is None:
        return ValidationResult(
            False,
            f'In Section `{section}`, an entry is missing required key `{key}`'
            )
    if 'type' in ref_dict and not match_type(data_value, ref_dict["type"]):
        return ValidationResult(
            False,
            f'In Section `{section}`, entry `{key}={data_value}` is not of type `{ref_dict["type"]}`'
            )
    # if "py_re" in ref_dict and not re.match(ref_dict["py_re"], data_value):
        # return ValidationResult(False, "regex fail")
    return True


def validate_key_throw(*args):
    """
    Like validate_key, but throws a ValueError when invalid.
    """
    validation_result = validate_key(*args)
    if not validation_result:
        raise ValueError(str(validation_result))
    return validation_result


def validate_section_dict(data_section, ref_section, section):
    if not isinstance(data_section, dict):
        return ValidationResult(False, f'Section `{section}` exists, but is not a dict.')
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
    return True


def validate_section_dict_list(data_section, ref_section, section):
    if not isinstance(data_section, list) or \
            not all((isinstance(x, dict) for x in data_section)):
        return ValidationResult(False, f'Section `{section}` exists, but is not a list of dicts.')
    sort_key = ref_section.get('sort')
    last_index = (data_section[0].get(sort_key, 0) if len(data_section) else 0) - 1
    for chunk in data_section:
        key_validation_results = (
            validate_key(
                chunk.get(key),
                ref_section['keys'].get(key),
                section, key
            ) for key in ref_section['keys']
        )
        for result in key_validation_results:
            if not bool(result):
                return result
        this_index = chunk.get(sort_key, 0)
        if this_index <= last_index:
            return ValidationResult(
                False,
                f'In Section `{section}`, chunk starting at index {this_index} is ahead of previous section.'
                )
        last_index = this_index
    return True


def validate_section(data_section, ref_section, section):
    '''Validates a section (e.g. global, capture, etc.).'''
    if ref_section["required"] and data_section is None:
        return ValidationResult(False, f'Required section `{section}` not found.')
    return {
        'dict': validate_section_dict,
        'dict_list': validate_section_dict_list,
    }[ref_section['type']](data_section, ref_section, section)


def validate(data, ref=None):
    if ref is None:
        ref = schema.get_schema()
    for result in (validate_section(data.get(key), ref.get(key), key) for key in ref):
        if not result:
            return result
    return True


def main():
    import argparse
    import logging

    from . import sigmffile
    from . import error

    parser = argparse.ArgumentParser(description='Validate SigMF Archive or file pair against JSON schema.')
    parser.add_argument('filename', help='SigMF path (extension optional).')
    parser.add_argument('--skip-checksum', action='store_true', help='Skip reading dataset to validate checksum.')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    level_lut = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    log = logging.getLogger()
    logging.basicConfig(level=level_lut[min(args.verbose, 2)])

    try:
        signal = sigmffile.fromfile(args.filename, skip_checksum=args.skip_checksum)
    except error.SigMFFileError as err:
        # this happens if checksum fails
        log.error(err)
        exit(1)
    except IOError as err:
        log.error(err)
        log.error('Unable to read SigMF, bad path?')
        exit(1)
    except json.decoder.JSONDecodeError as err:
        log.error(err)
        log.error('Unable to decode malformed JSON.')
        exit(1)
    result = signal.validate()
    if result:
        log.info('Validation OK!')
    else:
        log.error(result)
        exit(1)


if __name__ == '__main__':
    main()
