# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

'''Utilities'''

from copy import deepcopy
from datetime import datetime
import sys
import numpy as np

from . import error

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
    for key, value in b_dict.items():
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def get_schema_path(module_path):
    """
    """
    return module_path


def get_endian_str(ray):
    if not isinstance(ray, np.ndarray):
        raise error.SigMFError('Argument must be a numpy array')
    atype = ray.dtype

    if atype.byteorder == '<':
        return '_le'
    elif atype.byteorder == '>':
        return '_be'
    else:
        # endianness must be either '=' (native) or '|' (doesn't matter)
        return '_le' if sys.byteorder == 'little' else '_be'


def get_data_type_str(ray):
    """
    Return the SigMF datatype string for the datatype of numpy array `ray`.

    NOTE: this function only supports native numpy types so interleaved complex
    integer types are not supported.
    """
    if not isinstance(ray, np.ndarray):
        raise error.SigMFError('Argument must be a numpy array')
    atype = ray.dtype
    if atype.kind not in ('u', 'i', 'f', 'c'):
        raise error.SigMFError('Unsupported data type:', atype)
    data_type_str = ''
    if atype.kind == 'c':
        data_type_str += 'cf'
        # units are component bits, numpy complex types len(I)+len(Q)
        data_type_str += str(atype.itemsize * 8 // 2)
    elif atype.kind == 'f':
        data_type_str += 'rf'
        data_type_str += str(atype.itemsize * 8)  # units are bits
    elif atype.kind in ('u', 'i'):
        data_type_str += 'r' + atype.kind
        data_type_str += str(atype.itemsize * 8)  # units are bits
    if (atype.itemsize > 1):
        # only append endianness for types over 8 bits
        data_type_str += get_endian_str(ray)
    return data_type_str
