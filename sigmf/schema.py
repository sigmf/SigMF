# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

'''Schema IO'''

import os
import json

from . import utils

SCHEMA_META = 'schema-meta.json'
SCHEMA_COLLECTION = 'schema-collection.json'


def get_schema(version=None, schema_file=SCHEMA_META):
    '''
    Load JSON Schema to for either a `sigmf-meta` or `sigmf-collection`.

    TODO: In the future load specific schema versions.
    '''
    schema_path = os.path.join(
        utils.get_schema_path(os.path.dirname(utils.__file__)),
        schema_file
    )
    with open(schema_path, 'rb') as handle:
        schema = json.load(handle)
    return schema
