# Copyright 2021 GNU Radio Foundation
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
