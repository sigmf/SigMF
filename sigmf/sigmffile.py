# Copyright 2021 GNU Radio Foundation
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

'''SigMFFile Object'''

from collections import OrderedDict
import codecs
import json
import tarfile
import tempfile
from os import path
import warnings
import numpy as np

from . import __version__, schema, sigmf_hash, validate
from .archive import SigMFArchive, SIGMF_DATASET_EXT, SIGMF_METADATA_EXT, SIGMF_ARCHIVE_EXT
from .utils import dict_merge, insert_sorted_dict_list
from .error import SigMFFileError, SigMFAccessError

class SigMFFileIterator():
    def __init__(self, sigmf_file):
        self.sigmf_file = sigmf_file
        self.pos = 0

    def __next__(self):
        if self.pos >= len(self.sigmf_file):
            raise StopIteration
        a = self.sigmf_file[self.pos]
        self.pos += 1
        return a

class SigMFFile():
    '''
    API for SigMF I/O

    Parameters
    ----------
    metadata: str or dict, optional
        Metadata for associated dataset.
    data_file: str, optional
        Path to associated dataset.
    global_info: dict, optional
        Set global field shortcut if creating new object.
    skip_checksum: bool, default False
        When True will skip calculating hash on data_file (if present) to check against metadata.
    '''
    START_INDEX_KEY = "core:sample_start"
    LENGTH_INDEX_KEY = "core:sample_count"
    GLOBAL_INDEX_KEY = "core:global_index"
    START_OFFSET_KEY = "core:offset"
    NUM_CHANNELS_KEY = "core:num_channels"
    HASH_KEY = "core:sha512"
    VERSION_KEY = "core:version"
    DATATYPE_KEY = "core:datatype"
    FREQUENCY_KEY = "core:frequency"
    HEADER_BYTES_KEY = "core:header_bytes"
    FLO_KEY = "core:freq_lower_edge"
    FHI_KEY = "core:freq_upper_edge"
    SAMPLE_RATE_KEY = "core:sample_rate"
    COMMENT_KEY = "core:comment"
    DESCRIPTION_KEY = "core:description"
    AUTHOR_KEY = "core:author"
    META_DOI_KEY = "core:meta-doi"
    DATA_DOI_KEY = "core:data-doi"
    GENERATOR_KEY = "core:generator"
    LABEL_KEY = "core:label"
    RECORDER_KEY = "core:recorder"
    LICENSE_KEY = "core:license"
    HW_KEY = "core:hw"
    DATASET_KEY = "core:dataset"
    TRAILING_BYTES_KEY = "core:trailing_bytes"
    METADATA_ONLY_KEY = "core:metadata_only"
    EXTENSIONS_KEY = "core:extensions"
    DATETIME_KEY = "core:datetime"
    LAT_KEY = "core:latitude"
    LON_KEY = "core:longitude"
    GEOLOCATION_KEY = "core:geolocation"
    COLLECTION_KEY = "core:collection"
    COLLECTION_DOI_KEY = "core:collection_doi"
    STREAMS_KEY = "core:streams"
    GLOBAL_KEY = "global"
    CAPTURE_KEY = "captures"
    ANNOTATION_KEY = "annotations"
    VALID_GLOBAL_KEYS = [
        AUTHOR_KEY, COLLECTION_KEY, DATASET_KEY, DATATYPE_KEY, DATA_DOI_KEY, DESCRIPTION_KEY, EXTENSIONS_KEY,
        GEOLOCATION_KEY, HASH_KEY, HW_KEY, LICENSE_KEY, META_DOI_KEY, METADATA_ONLY_KEY, NUM_CHANNELS_KEY, RECORDER_KEY,
        SAMPLE_RATE_KEY, START_OFFSET_KEY, TRAILING_BYTES_KEY, VERSION_KEY
    ]
    VALID_CAPTURE_KEYS = [DATETIME_KEY, FREQUENCY_KEY, HEADER_BYTES_KEY, GLOBAL_INDEX_KEY, START_INDEX_KEY]
    VALID_ANNOTATION_KEYS = [
        COMMENT_KEY, FHI_KEY, FLO_KEY, GENERATOR_KEY, LABEL_KEY, LAT_KEY, LENGTH_INDEX_KEY, LON_KEY, START_INDEX_KEY
    ]
    VALID_COLLECTION_KEYS = [
        AUTHOR_KEY, COLLECTION_DOI_KEY, DESCRIPTION_KEY, EXTENSIONS_KEY, LICENSE_KEY, STREAMS_KEY, VERSION_KEY
    ]

    def __init__(self, metadata=None, data_file=None, global_info=None, skip_checksum=False):
        self.version = None
        self.schema = None
        self.data_file = None
        self.sample_count = 0

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
        if data_file is not None:
            self.set_data_file(data_file, skip_checksum=skip_checksum)

    def __str__(self):
        return self.dumps()

    def __repr__(self):
        return f'SigMFFile({self})'

    def __len__(self):
        return self._memmap.shape[0]

    def __iter__(self):
        return SigMFFileIterator(self)

    def __getitem__(self, sli):
        a = self._memmap[sli] # matches behavior of numpy.ndarray.__getitem__()
        if self._return_type is not None:
            # is_fixed_point and is_complex
            if self._memmap.ndim == 2:
                # num_channels==1
                a = a[0].astype(self._return_type) + 1.j * a[1].astype(self._return_type)
            elif self._memmap.ndim == 3:
                # num_channels>1
                a = a[:,0].astype(self._return_type) + 1.j * a[:,1].astype(self._return_type)
            else:
                raise ValueError("unhandled ndim in SigMFFile.__getitem__(); this shouldn't happen")
        return a

    def _get_start_offset(self):
        """
        Return the offset of the first sample.
        """
        return self.get_global_field(self.START_OFFSET_KEY, 0)

    def get_num_channels(self):
        '''Returns integer number of channels if present, otherwise 1'''
        return self.get_global_field(self.NUM_CHANNELS_KEY, 1)

    def _is_conforming_dataset(self):
        """
        Returns `True` if the dataset is conforming to SigMF, `False` otherwise

        The dataset is non-conforming if the datafile contains non-sample bytes
        which means global trailing_bytes field is zero or not set, all captures
        `header_bytes` fields are zero or not set. Because we do not necessarily
        know the filename no means of verifying the meta/data filename roots
        match, but this will also check that a data file exists.
        """
        if self.get_global_field(self.TRAILING_BYTES_KEY, 0):
            return False
        for capture in self.get_captures():
            # check for any non-zero `header_bytes` fields in captures segments
            if capture.get(self.HEADER_BYTES_KEY, 0):
                return False
        if not path.isfile(self.data_file):
            return False
        # if we get here, the file exists and is conforming
        return True

    def _validate_dict_in_section(self, entries, section_key):
        """
        Checks a dictionary for validity.
        Throws if not.
        """
        schema_section = self.get_schema()[section_key]
        for key, value in entries.items():
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
            cap_info = capture
        return cap_info

    def get_capture_start(self, index):
        """
        Returns a the start sample index of a given capture, will raise
        SigMFAccessError if this field is missing.
        """
        start = self.get_captures()[index].get(self.START_INDEX_KEY)
        if start is None:
            raise SigMFAccessError("Capture {} does not have required {} key".format(index, self.START_INDEX_KEY))
        return start

    def get_capture_byte_boundarys(self, index):
        """
        Returns a tuple of the file byte range in a dataset of a given SigMF
        capture of the form [start, stop). This function works on either
        compliant or noncompliant SigMF Recordings.
        """
        if index >= len(self.get_captures()):
            raise SigMFAccessError("Invalid captures index {} (only {} captures in Recording)".format(index, len(self.get_captures())))

        start_byte = 0
        prev_start_sample = 0
        for ii, capture in enumerate(self.get_captures()):
            start_byte += capture.get(self.HEADER_BYTES_KEY, 0)
            start_byte += (self.get_capture_start(ii) - prev_start_sample) * self.get_sample_size() * self.get_num_channels()
            prev_start_sample = self.get_capture_start(ii)
            if ii >= index:
                break

        end_byte = start_byte
        if index == len(self.get_captures())-1:  # last captures...data is the rest of the file
            end_byte = path.getsize(self.data_file) - self.get_global_field(self.TRAILING_BYTES_KEY, 0)
        else:
            end_byte += (self.get_capture_start(index+1) - self.get_capture_start(index)) * self.get_sample_size() * self.get_num_channels()
        return (start_byte, end_byte)

    def add_annotation(self, start_index, length, metadata=None):
        """
        Insert annotation
        """
        assert start_index >= self._get_start_offset()
        assert length >= 1
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
        '''
        Get relevant annotations from metadata.

        Parameters
        ----------
        index : int, default None
            If provided returns all annotations that include this sample index.
            When omitted returns all annotations.

        Returns
        -------
        list of dict
            Each dictionary contains one annotation for the sample at `index`.
        '''
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
            header_bytes = sum([c.get(self.HEADER_BYTES_KEY, 0) for c in self.get_captures()])
            file_size = path.getsize(self.data_file) - self.get_global_field(self.TRAILING_BYTES_KEY, 0) - header_bytes  # bytes
            sample_size = self.get_sample_size() # size of a sample in bytes
            num_channels = self.get_num_channels()
            sample_count = file_size // sample_size // num_channels
            if file_size % (sample_size * num_channels) != 0:
                warnings.warn(f'File `{self.data_file}` does not contain an integer '
                    'number of samples across channels. It may be invalid data.')
            if len(annotations) > 0 and annotations[-1][self.START_INDEX_KEY] + annotations[-1][self.LENGTH_INDEX_KEY] > sample_count:
                warnings.warn(f'File `{self.data_file}` ends before the final annotation '
                    'in the corresponding SigMF metadata.')
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

    def set_data_file(self, data_file, skip_checksum=False):
        """
        Set the datafile path, then recalculate sample count. If not skipped,
        update the hash and return the hash string.
        """
        if self.get_global_field(self.DATATYPE_KEY) is None:
            raise SigMFFileError("Error setting data file, the DATATYPE_KEY must be set in the global metadata first.")

        self.data_file = data_file
        self._count_samples()

        dtype = dtype_info(self.get_global_field(self.DATATYPE_KEY))
        num_channels = self.get_num_channels()
        self.ndim = 1 if (num_channels < 2) else 2
        is_complex_data = dtype['is_complex']
        is_fixedpoint_data = dtype['is_fixedpoint']

        memmap_shape = (-1,)
        if num_channels > 1:
            memmap_shape = memmap_shape + (num_channels,)
        if is_complex_data and is_fixedpoint_data:
            # There is no corresponding numpy type, so we'll have to add another axis, length of 2
            memmap_shape = memmap_shape + (2,)
        self._return_type = dtype['memmap_convert_type']
        #print('memmap()ing', self.get_global_field(self.DATATYPE_KEY), 'with', dtype['memmap_map_type'])
        try:
            self._memmap = np.memmap(self.data_file, offset=0, dtype=dtype['memmap_map_type']).reshape(memmap_shape)
        except:  # TODO include likely exceptions here
            warnings.warn('Failed to memory-map array from file')
            self._memmap = None
            self.shape = None
        else:
            self.shape = self._memmap.shape if (self._return_type is None) else self._memmap.shape[:-1]

        if skip_checksum:
            return None
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
        # TODO: sort potential `other` top-level keys
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
        pretty : bool, default True
            When True will write more human-readable output, otherwise will be flat JSON.
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
        pretty : bool, default True
            When True will write more human-readable output, otherwise will be flat JSON.

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
        '''
        Write metadata file or full archive containing metadata & dataset.

        Parameters
        ----------
        file_path : string
            Location to save.
        pretty : bool, default True
            When True will write more human-readable output, otherwise will be flat JSON.
        toarchive : bool, default False
            If True will write both dataset & metadata into SigMF archive format as a single `tar` file.
            If False will only write metadata to `sigmf-meta`.
        '''
        fns = get_sigmf_filenames(file_path)
        if toarchive:
            self.archive(fns['archive_fn'])
        else:
            with open(fns['meta_fn'], 'w') as fp:
                self.dump(fp, pretty=pretty)

    def read_samples_in_capture(self, index=0, autoscale=True):
        '''
        Reads samples from the specified captures segment in its entirety.

        Parameters
        ----------
        index : int, default 0
            Captures segment to read samples from.
        autoscale : bool, default True
            If dataset is in a fixed-point representation, scale samples from (min, max) to (-1.0, 1.0)

        Returns
        -------
        data : ndarray
            Samples are returned as an array of float or complex, with number of dimensions equal to NUM_CHANNELS_KEY.
        '''
        cb = self.get_capture_byte_boundarys(index)
        if (cb[1] - cb[0]) % (self.get_sample_size() * self.get_num_channels()):
            warnings.warn(f'Capture `{index}` in `{self.data_file}` does not contain '
                    'an integer number of samples across channels. It may be invalid.')

        return self._read_datafile(cb[0], (cb[1] - cb[0]) // self.get_sample_size(), autoscale, False)

    def read_samples(self, start_index=0, count=-1, autoscale=True, raw_components=False):
        '''
        Reads the specified number of samples starting at the specified index from the associated data file.

        Parameters
        ----------
        start_index : int, default 0
            Starting sample index from which to read.
        count : int, default -1
            Number of samples to read. -1 will read whole file.
        autoscale : bool, default True
            If dataset is in a fixed-point representation, scale samples from (min, max) to (-1.0, 1.0)
        raw_components : bool, default False
            If True read and return the sample components (individual I & Q for complex, samples for real)
            with no conversions or interleaved channels.

        Returns
        -------
        data : ndarray
            Samples are returned as an array of float or complex, with number of dimensions equal to NUM_CHANNELS_KEY.
        '''
        if count == 0:
            raise IOError('Number of samples must be greater than zero, or -1 for all samples.')
        elif start_index + count > self.sample_count:
            raise IOError("Cannot read beyond EOF.")
        if self.data_file is None:
            if self.get_global_field(self.METADATA_ONLY_KEY, False):
                # only if data_file is `None` allows access to dynamically generated datsets
                raise SigMFFileError("Cannot read samples from a metadata only distribution.")
            else:
                raise SigMFFileError("No signal data file has bfeen associated with the metadata.")
        first_byte = start_index * self.get_sample_size() * self.get_num_channels()

        if not self._is_conforming_dataset():
            warnings.warn(f'Recording dataset appears non-compliant, resulting data may be erroneous')
        return self._read_datafile(first_byte, count * self.get_num_channels(), autoscale, False)

    def _read_datafile(self, first_byte, nitems, autoscale, raw_components):
        '''
        internal function for reading samples from datafile
        '''
        dtype = dtype_info(self.get_global_field(self.DATATYPE_KEY))
        is_complex_data = dtype['is_complex']
        is_fixedpoint_data = dtype['is_fixedpoint']
        is_unsigned_data = dtype['is_unsigned']
        data_type_in = dtype['sample_dtype']
        component_type_in = dtype['component_dtype']
        component_size = dtype['component_size']

        data_type_out = np.dtype("f4") if not is_complex_data else np.dtype("f4, f4")
        num_channels = self.get_num_channels()

        fp = open(self.data_file, "rb")
        fp.seek(first_byte, 0)
        data = np.fromfile(fp, dtype=data_type_in, count=nitems)
        if num_channels != 1:
            # return reshaped view for num_channels
            # first dimension will be double size if `is_complex_data`
            data = data.reshape(data.shape[0] // num_channels, num_channels)
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
    if datatype is None:
        raise SigMFFileError("Invalid datatype 'None'.")
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
    if "64" in dtype:
        sample_size = 8
    elif "32" in dtype:
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

    memmap_convert_type = None
    if is_complex_data:
        data_type_str = ','.join((data_type_str, data_type_str))
        memmap_map_type = byte_order
        if is_fixedpoint_data:
            memmap_map_type += ("u" if is_unsigned_data else "i") + str(component_size)
            memmap_convert_type = byte_order + "c8"
        else:
            memmap_map_type += "c" + str(sample_size)
    else:
        memmap_map_type = data_type_str

    data_type_in = np.dtype(data_type_str)
    output_info['sample_dtype'] = data_type_in
    output_info['component_dtype'] = data_type_in['f0'] if is_complex_data else data_type_in
    output_info['sample_size'] = sample_size
    output_info['component_size'] = component_size
    output_info['is_complex'] = is_complex_data
    output_info['is_unsigned'] = is_unsigned_data
    output_info['is_fixedpoint'] = is_fixedpoint_data
    output_info['memmap_map_type'] = memmap_map_type
    output_info['memmap_convert_type'] = memmap_convert_type
    return output_info


def get_dataset_filename_from_metadata(meta_fn, metadata=None):
    '''
    Parse provided metadata and return the expected data filename. In the case of
    a metadata only distribution, or if the file does not exist, this will return
    'None'. The priority for conflicting:
      1. The file named <METAFILE_BASENAME>.sigmf-meta if it exists
      2. The file in the `core:dataset` field (Non-Compliant Dataset) if it exists
      3. None (may be a metadata only distribution)
    '''
    compliant_data_fn = get_sigmf_filenames(meta_fn)['data_fn']
    noncompliant_data_fn = metadata['global'].get("core:dataset", None)

    if path.isfile(compliant_data_fn):
        if noncompliant_data_fn:
            warnings.warn(f'Compliant Dataset `{compliant_data_fn}` exists but '
                    f'"core:dataset" is also defined; using `{compliant_data_fn}`')
        return compliant_data_fn

    elif noncompliant_data_fn:
        if path.isfile(noncompliant_data_fn):
            if metadata['global'].get("core:metadata_only", False):
                warnings.warn('Schema defines "core:dataset" but "core:meatadata_only" '
                        f'also exists; using `{noncompliant_data_fn}`')
            return noncompliant_data_fn
        else:
            warnings.warn(f'Non-Compliant Dataset `{noncompliant_data_fn}` is specified '
                    'in "core:dataset" but does not exist!')

    return None


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
            if member.name.endswith(SIGMF_METADATA_EXT):
                bytestream_reader = codecs.getreader("utf-8")  # bytes -> str
                mdfile_reader = bytestream_reader(archive.extractfile(member))
                metadata = json.load(mdfile_reader)
                data_file = get_dataset_filename_from_metadata(member.name, metadata)
            else:
                archive.extractfile(member)
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
    archive_fn = fns['archive_fn']

    if (filename.lower().endswith(SIGMF_ARCHIVE_EXT) or not path.isfile(meta_fn)) and path.isfile(archive_fn):
        return fromarchive(archive_fn)

    meta_fp = open(meta_fn, "rb")
    bytestream_reader = codecs.getreader("utf-8")
    mdfile_reader = bytestream_reader(meta_fp)
    metadata = json.load(mdfile_reader)
    meta_fp.close()

    data_fn = get_dataset_filename_from_metadata(meta_fn, metadata)
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
            for key, desc in keys_dict.items()
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
        for category, desc in schema.items()
    }
