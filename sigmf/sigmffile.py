# Copyright 2016 GNU Radio Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from collections import OrderedDict
import codecs
import json
import tarfile
import tempfile
from os import path
import warnings
from six import iteritems
import numpy as np

from . import __version__, schema, sigmf_hash, validate
from .archive import SigMFArchive, SIGMF_DATASET_EXT, SIGMF_METADATA_EXT, SIGMF_ARCHIVE_EXT
from .utils import dict_merge, insert_sorted_dict_list
from .error import SigMFFileError


class SigMFFile(object):
    """API to manipulate SigMF files.

    Parameters:

      metadata    -- Metadata. Either a string, or a dictionary.
      data_file   -- Path to the corresponding data file.
      global_info -- Dictionary containing global header info.

    """
    START_INDEX_KEY = "core:sample_start"
    LENGTH_INDEX_KEY = "core:sample_count"
    START_OFFSET_KEY = "core:offset"
    HASH_KEY = "core:sha512"
    VERSION_KEY = "core:version"
    DATATYPE_KEY = "core:datatype"
    FREQUENCY_KEY = "core:frequency"
    FLO_KEY = "core:freq_lower_edge"
    FHI_KEY = "core:freq_upper_edge"
    SAMPLE_RATE_KEY = "core:sample_rate"
    COMMENT_KEY = "core:comment"
    DESCRIPTION_KEY = "core:description"
    AUTHOR_KEY = "core:author"
    META_DOI_KEY = "core:meta-doi"
    DATA_DOI_KEY = "core:data-doi"
    GENERATOR_KEY = "core:generator"
    RECORDER_KEY = "core:recorder"
    LICENSE_KEY = "core:license"
    HW_KEY = "core:hw"
    EXTENSIONS_KEY = "core:extensions"
    DATETIME_KEY = "core:datetime"
    LAT_KEY = "core:latitude"
    LON_KEY = "core:longitude"
    GLOBAL_KEY = "global"
    CAPTURE_KEY = "captures"
    ANNOTATION_KEY = "annotations"

    def __init__(
            self,
            metadata=None,
            data_file=None,
            global_info=None,
            skip_checksum=False,
    ):
        self.version = None
        self.schema = None
        if metadata is None:
            self._metadata = get_default_metadata(self.get_schema())
            if not self._metadata[self.GLOBAL_KEY][self.VERSION_KEY]:
                self._metadata[self.GLOBAL_KEY][self.VERSION_KEY] = __version__
        elif isinstance(metadata, dict):
            self._metadata = metadata
        else:
            self._metadata = json.loads(metadata)
        if global_info is not None:
            self.set_global_info(global_info)
        self.data_file = data_file
        if self.data_file and not skip_checksum:
            self.calculate_hash()
        self._count_samples()

    def __str__(self):
        return self.dumps()

    def __repr__(self):
        return "SigMFFile(%s)" % self

    def _get_start_offset(self):
        """
        Return the offset of the first sample.
        """
        return self.get_global_field(self.START_OFFSET_KEY, 0)

    def _validate_dict_in_section(self, entries, section_key):
        """
        Checks a dictionary for validity.
        Throws if not.
        """
        schema_section = self.get_schema()[section_key]
        for key, value in iteritems(entries):
            validate.validate_key_throw(
                value, schema_section.get(key, {}), schema_section, key
            )

    def get_schema(self):
        """
        Return a schema object valid for the current metadata
        """
        current_metadata_version = self.get_global_info().get(self.VERSION_KEY)
        if self.version != current_metadata_version or self.schema is None:
            self.version = current_metadata_version
            self.schema = schema.get_schema(self.version)
        assert isinstance(self.schema, dict)
        return self.schema

    def set_global_info(self, new_global):
        """
        Overwrite the global info with a new dictionary.
        """
        self._validate_dict_in_section(new_global, self.GLOBAL_KEY)
        self._metadata[self.GLOBAL_KEY] = new_global

    def get_global_info(self):
        """
        Returns a dictionary with all the global info.
        """
        try:
            return self._metadata.get(self.GLOBAL_KEY, {})
        except AttributeError:
            return {}

    def set_global_field(self, key, value):
        """
        Inserts a value into the global fields.

        Will throw a ValueError if the key/value pair is invalid.
        """
        schema_section = self.get_schema()[self.GLOBAL_KEY].get('keys', {})
        validate.validate_key_throw(
            value,
            schema_section.get(key, {}),
            self.GLOBAL_KEY,
            key
        )
        self._metadata[self.GLOBAL_KEY][key] = value
        return value

    def get_global_field(self, key, default=None):
        """
        Return a field from the global info, or default if the field is not set.
        """
        return self._metadata[self.GLOBAL_KEY].get(key, default)

    def add_capture(self, start_index, metadata=None):
        """
        Insert capture info for sample starting at start_index.
        If there is already capture info for this index, metadata will be merged
        with the existing metadata, overwriting keys if they were previously
        set.
        """
        assert start_index >= self._get_start_offset()
        metadata = metadata or {}
        self._validate_dict_in_section(metadata, self.CAPTURE_KEY)
        metadata[self.START_INDEX_KEY] = start_index
        self._metadata[self.CAPTURE_KEY] = insert_sorted_dict_list(
            self._metadata.get(self.CAPTURE_KEY, []),
            metadata,
            self.START_INDEX_KEY,
        )

    def get_captures(self):
        """
        Returns a list of dictionaries representing all captures.
        """
        return [
            x for x in self._metadata.get(self.CAPTURE_KEY, [])
        ]

    def get_capture_info(self, index):
        """
        Returns a dictionary containing all the capture information at sample
        'index'.
        """
        assert index >= self._get_start_offset()
        captures = self._metadata.get(self.CAPTURE_KEY, [])
        assert len(captures) > 0
        cap_info = captures[0]
        for capture in captures:
            if capture[self.START_INDEX_KEY] > index:
                break
            cap_info = dict_merge(cap_info, capture)
        return cap_info

    def add_annotation(self, start_index, length, metadata=None):
        """
        Insert annotation
        """
        assert start_index >= self._get_start_offset()
        assert length > 1
        metadata = metadata or {}
        metadata[self.START_INDEX_KEY] = start_index
        metadata[self.LENGTH_INDEX_KEY] = length
        self._validate_dict_in_section(metadata, self.ANNOTATION_KEY)
        self._metadata[self.ANNOTATION_KEY] = insert_sorted_dict_list(
            self._metadata.get(self.ANNOTATION_KEY, []),
            metadata,
            self.START_INDEX_KEY,
            force_insertion=True
        )

    def get_annotations(self, index=None):
        """
        Returns a list of dictionaries.
        Every dictionary contains one annotation for the sample at 'index'.
        If no index is specified, all annotations are returned.

        Keyword arguments:
        index -- the criteria for selecting annotations; this sample index must be contained in each annotation that is returned
        """
        return [
            x for x in self._metadata.get(self.ANNOTATION_KEY, [])
            if index is None or (x[self.START_INDEX_KEY] <= index
            and x[self.START_INDEX_KEY] + x[self.LENGTH_INDEX_KEY] > index)
        ]

    def get_sample_size(self):
        """
        Determines the size of a sample, in bytes, from the datatype of this set.
        For complex data, a 'sample' includes both the real and imaginary part.
        """
        return dtype_info(self.get_global_field(self.DATATYPE_KEY))['sample_size']

    def _count_samples(self):
        """
        Count, set, and return the total number of samples in the data file.
        If there is no data file but there are annotations, use the end index
        of the final annotation instead. If there are no annotations, use 0.
        For complex data, a 'sample' includes both the real and imaginary part.
        """
        annotations = self.get_annotations()
        if self.data_file is None:
            if len(annotations) > 0:
                sample_count = annotations[-1][self.START_INDEX_KEY] + annotations[-1][self.LENGTH_INDEX_KEY]
            else:
                sample_count = 0
        else:
            file_size = path.getsize(self.data_file)
            sample_size = self.get_sample_size()
            sample_count = file_size // sample_size
            if file_size % sample_size != 0:
                warnings.warn("File '{}' does not contain an integral number of sample. It might not be valid data.".format(self.data_file))
            if len(annotations) > 0 and annotations[-1][self.START_INDEX_KEY] + annotations[-1][self.LENGTH_INDEX_KEY] > sample_count:
                warnings.warn("File '{}' ends before the final annotation in the corresponding SigMF metadata.".format(self.data_file))
        self.sample_count = sample_count
        return sample_count

    def calculate_hash(self):
        """
        Calculates the hash of the data file and adds it to the global section.
        Also returns a string representation of the hash.
        """
        old_hash = self.get_global_field(self.HASH_KEY)
        new_hash = sigmf_hash.calculate_sha512(self.data_file)
        if old_hash:
            if old_hash != new_hash:
                raise SigMFFileError('Calculated file hash does not match associated metadata.')

        return self.set_global_field(self.HASH_KEY, new_hash)

    def set_data_file(self, data_file):
        """
        Set the datafile path, then recalculate the hash and sample count. Return the hash string.
        """
        self.data_file = data_file
        self._count_samples()
        return self.calculate_hash()

    def validate(self):
        """
        Return True if the metadata is valid.
        """
        schema_version = self.get_global_field(self.VERSION_KEY)
        return validate.validate(
            self._metadata,
            schema.get_schema(schema_version),
        )
    def ordered_metadata(self):
        '''
        Get a nicer representation of _metadata. Will sort keys, but put the
        top-level fields 'global', 'captures', 'annotations' in front.

        Returns
        -------
        ordered_meta : OrderedDict
            Cleaner representation of _metadata with top-level keys correctly
            ordered and the rest of the keys sorted.
        '''
        ordered_meta = OrderedDict()
        top_sort_order = ['global', 'captures', 'annotations']
        for top_key in top_sort_order:
            assert top_key in self._metadata
            ordered_meta[top_key] = json.loads(json.dumps(self._metadata[top_key], sort_keys=True))
        # If there are other top-level keys, they go later
        # TODO: sort these `other` top-level keys
        for oth_key, oth_val in self._metadata.items():
            if oth_key not in top_sort_order:
                ordered_meta[oth_key] = json.loads(json.dumps(oth_val, sort_keys=True))
        return ordered_meta

    def dump(self, filep, pretty=True):
        '''
        Write metadata to a file.

        Parameters
        ----------
        filep : object
            File pointer or something that json.dump() can handle.
        pretty : bool, optional
            Is true by default.
        '''
        json.dump(
            self.ordered_metadata(),
            filep,
            indent=4 if pretty else None,
            separators=(',', ': ') if pretty else None,
        )

    def dumps(self, pretty=True):
        '''
        Get a string representation of the metadata.

        Parameters
        ----------
        pretty : bool, optional
            Is true by default.

        Returns
        -------
        string
            String representation of the metadata using json formatter.
        '''
        return json.dumps(
            self.ordered_metadata(),
            indent=4 if pretty else None,
            separators=(',', ': ') if pretty else None,
        )

    def archive(self, name=None, fileobj=None):
        """Dump contents to SigMF archive format.

        `name` and `fileobj` are passed to SigMFArchive and are defined there.

        """
        archive = SigMFArchive(self, name, fileobj)
        return archive.path

    def tofile(self, file_path, pretty=True, toarchive=False):
        """
        Dump contents to file.
        """
        fns = get_sigmf_filenames(file_path)
        if toarchive:
            self.archive(fns['archive_fn'])
        else:
            with open(fns['meta_fn'], 'w') as fp:
                self.dump(fp, pretty=pretty)

    def read_samples(self, start_index=0, count=1, autoscale=True, raw_components=False):
        """
        Reads the specified number of samples starting at the specified index
        from the associated data file.
        Samples are returned as a NumPy array of type np.float32 (if real data)
        or np.complex64.

        Keyword arguments:
        start_index -- starting sample index from which to read
        count -- number of samples to read
        autoscale -- if dataset is in a fixed-point representation, scale samples from (min, max) to (-1.0, 1.0)
        raw_components -- if True, read and return the sample components (individual I and Q for complex, samples for real) with no conversions
        """

        if count < 1:
            raise IOError("Number of samples must be greater than zero.")

        if start_index + count > self.sample_count:
            raise IOError("Cannot read beyond EOF.")
        if self.data_file is None:
            raise SigMFFileError("No signal data file has been associated with the metadata.")

        dtype = dtype_info(self.get_global_field(self.DATATYPE_KEY))
        is_complex_data = dtype['is_complex']
        is_fixedpoint_data = dtype['is_fixedpoint']
        is_unsigned_data = dtype['is_unsigned']
        data_type_in = dtype['sample_dtype']
        component_type_in = dtype['component_dtype']
        sample_size = dtype['sample_size']
        component_size = dtype['component_size']

        data_type_out = np.dtype("f4") if not is_complex_data else np.dtype("f4,f4")

        fp = open(self.data_file, "rb")
        fp.seek(start_index * sample_size, 0)

        data = np.fromfile(fp, dtype=data_type_in, count=count)
        if not raw_components:
            data = data.astype(data_type_out)
            if autoscale and is_fixedpoint_data:
                data = data.view(np.dtype("f4"))
                if is_unsigned_data:
                    data -= 2**(component_size*8-1)
                data *= 2**-(component_size*8-1)
                data = data.view(data_type_out)
            if is_complex_data:
                data = data.view(np.complex64)
        else:
            data = data.view(component_type_in)

        fp.close()
        return data

def dtype_info(datatype):
    """
    Parses a datatype string conforming to the SigMF spec and returns a dict
    of values describing the format.

    Keyword arguments:
    datatype -- a SigMF-compliant datatype string
    """
    output_info = {}
    dtype = datatype.lower()

    is_unsigned_data = "u" in datatype
    is_complex_data = "c" in datatype
    is_fixedpoint_data = "f" not in datatype

    dtype = datatype.lower().split("_")

    byte_order = ""
    if len(dtype) == 2:
        if dtype[1][0] == "l":
            byte_order = "<"
        elif dtype[1][0] == "b":
            byte_order = ">"
        else:
            raise SigMFFileError("Unrecognized endianness specifier: '{}'".format(dtype[1]))
    dtype = dtype[0]
    if "32" in dtype:
        sample_size = 4
    elif "16" in dtype:
        sample_size = 2
    elif "8" in dtype:
        sample_size = 1
    else:
        raise SigMFFileError("Unrecognized datatype: '{}'".format(dtype))
    component_size = sample_size
    if is_complex_data:
        sample_size *= 2
    sample_size = int(sample_size)

    data_type_str = byte_order
    data_type_str += "f" if not is_fixedpoint_data else "u" if is_unsigned_data else "i"
    data_type_str += str(component_size)

    if is_complex_data:
        data_type_str = ','.join((data_type_str, data_type_str))

    data_type_in = np.dtype(data_type_str)
    output_info['sample_dtype'] = data_type_in
    output_info['component_dtype'] = data_type_in['f0'] if is_complex_data else data_type_in
    output_info['sample_size'] = sample_size
    output_info['component_size'] = component_size
    output_info['is_complex'] = is_complex_data
    output_info['is_unsigned'] = is_unsigned_data
    output_info['is_fixedpoint'] = is_fixedpoint_data
    return output_info

def fromarchive(archive_path, dir=None):
    """Extract an archive and return a SigMFFile.

    If `dir` is given, extract the archive to that directory. Otherwise,
    the archive will be extracted to a temporary directory. For example,
    `dir` == "." will extract the archive into the current working
    directory.

    """
    if not dir:
        dir = tempfile.mkdtemp()

    archive = tarfile.open(archive_path, mode="r", format=tarfile.PAX_FORMAT)
    members = archive.getmembers()

    try:
        archive.extractall(path=dir)

        data_file = None
        metadata = None

        for member in members:
            if member.name.endswith(SIGMF_DATASET_EXT):
                data_file = path.join(dir, member.name)
            elif member.name.endswith(SIGMF_METADATA_EXT):
                bytestream_reader = codecs.getreader("utf-8")  # bytes -> str
                mdfile_reader = bytestream_reader(archive.extractfile(member))
                metadata = json.load(mdfile_reader)
    finally:
        archive.close()

    return SigMFFile(metadata=metadata, data_file=data_file)

def fromfile(filename, skip_checksum=False):
    '''
    Creates and returns a returns a SigMFFile instance with metadata loaded from the specified file.
    The filename may be that of either a sigmf-meta file, a sigmf-data file, or a sigmf archive.

    Parameters
    ----------
    filename: str
        Path for SigMF dataset with or without extension.
    skip_checksum: bool, default False
        When True will not read entire dataset to caculate hash.

    Returns
    -------
    object
        SigMFFile object with dataset & metadata.
    '''
    fns = get_sigmf_filenames(filename)
    meta_fn = fns['meta_fn']
    data_fn = fns['data_fn']
    archive_fn = fns['archive_fn']

    if (filename.lower().endswith(SIGMF_ARCHIVE_EXT) or not path.isfile(meta_fn)) and path.isfile(archive_fn):
        return fromarchive(archive_fn)
    if not path.isfile(data_fn):
        data_fn = None

    meta_fp = open(meta_fn, "rb")
    bytestream_reader = codecs.getreader("utf-8")
    mdfile_reader = bytestream_reader(meta_fp)
    metadata = json.load(mdfile_reader)
    meta_fp.close()
    return SigMFFile(metadata=metadata, data_file=data_fn, skip_checksum=skip_checksum)

def get_sigmf_filenames(filename):
    """
    Safely returns a set of SigMF file paths given an input filename.
    Returned as dict with 'data_fn', 'meta_fn', and 'archive_fn' as keys.

    Keyword arguments:
    filename -- the SigMF filename
    """
    filename = path.splitext(filename)[0]
    return {'data_fn': filename+SIGMF_DATASET_EXT, 'meta_fn': filename+SIGMF_METADATA_EXT, 'archive_fn': filename+SIGMF_ARCHIVE_EXT}


def get_default_metadata(schema):
    """Return the minimal metadata that will pass the validator."""
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
            'dict_list': lambda x: [x] if x else [],
        }[cat_type](defaults)

    return {
        category: default_category_data(desc["type"], get_default_dict(desc["keys"]))
        for category, desc in iteritems(schema)
    }
