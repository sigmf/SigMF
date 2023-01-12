# Copyright: Multiple Authors
#
# This file is part of SigMF. https://github.com/gnuradio/SigMF
#
# SPDX-License-Identifier: LGPL-3.0-or-later

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
from .archive import SigMFArchive, SIGMF_DATASET_EXT, SIGMF_METADATA_EXT, SIGMF_ARCHIVE_EXT, SIGMF_COLLECTION_EXT
from .utils import dict_merge
from .error import SigMFFileError, SigMFAccessError

class SigMFMetafile():
    VALID_KEYS = {}
    def __init__(self):
        self.version = None
        self.schema = None
        self._metadata = None
        self.shape = None

    def __str__(self):
        return self.dumps()

    def __repr__(self):
        return f'SigMFFile({self})'

    def __iter__(self):
        '''special method to iterate through samples'''
        self.iter_position = 0
        return self

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
        for top_key in self.VALID_KEYS.keys():
            assert top_key in self._metadata
            ordered_meta[top_key] = json.loads(json.dumps(self._metadata[top_key], sort_keys=True))
        # If there are other top-level keys, they go later
        # TODO: sort potential `other` top-level keys
        for oth_key, oth_val in self._metadata.items():
            if oth_key not in self.VALID_KEYS.keys():
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

class SigMFFile(SigMFMetafile):
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
    UUID_KEY = "core:uuid"
    GEOLOCATION_KEY = "core:geolocation"
    COLLECTION_KEY = "core:collection"
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
        COMMENT_KEY, FHI_KEY, FLO_KEY, GENERATOR_KEY, LABEL_KEY, LAT_KEY, LENGTH_INDEX_KEY, LON_KEY, START_INDEX_KEY,
        UUID_KEY
    ]
    VALID_KEYS = {GLOBAL_KEY: VALID_GLOBAL_KEYS, CAPTURE_KEY: VALID_CAPTURE_KEYS, ANNOTATION_KEY: VALID_ANNOTATION_KEYS}

    def __init__(self, metadata=None, data_file=None, global_info=None, skip_checksum=False, map_readonly=True):
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
        map_readonly: bool, default True
            Indicates whether assignments on the numpy.memmap are allowed.
        '''
        super(SigMFFile, self).__init__()
        self.data_file = None
        self.sample_count = 0
        self._memmap = None
        self.is_complex_data = False  # numpy.iscomplexobj(self._memmap) is not adequate for fixed-point complex case

        if metadata is None:
            self._metadata = {self.GLOBAL_KEY:{}, self.CAPTURE_KEY:[], self.ANNOTATION_KEY:[]}
            self._metadata[self.GLOBAL_KEY][self.NUM_CHANNELS_KEY] = 1
            self._metadata[self.GLOBAL_KEY][self.VERSION_KEY] = __version__
        elif isinstance(metadata, dict):
            self._metadata = metadata
        else:
            self._metadata = json.loads(metadata)
        if global_info is not None:
            self.set_global_info(global_info)
        if data_file is not None:
            self.set_data_file(data_file, skip_checksum, map_readonly=map_readonly)

    def __len__(self):
        return self._memmap.shape[0]

    def __next__(self):
        '''get next batch of samples'''
        if self.iter_position < len(self):
            # normal batch
            value = self.read_samples(start_index=self.iter_position, count=1)
            self.iter_position += 1
            return value

        else:
            # no more data
            raise StopIteration

    def __getitem__(self, sli):
        a = self._memmap[sli] # matches behavior of numpy.ndarray.__getitem__()
        if self._return_type is not None:
            # is_fixed_point and is_complex
            if self._memmap.ndim == 2:
                # num_channels==1
                a = a[:,0].astype(self._return_type) + 1.j * a[:,1].astype(self._return_type)
            elif self._memmap.ndim == 3:
                # num_channels>1
                a = a[:,:,0].astype(self._return_type) + 1.j * a[:,:,1].astype(self._return_type)
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
        self._metadata[self.GLOBAL_KEY] = new_global.copy()

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
        Inserts a value into the global field.
        """
        self._metadata[self.GLOBAL_KEY][key] = value

    def get_global_field(self, key, default=None):
        """
        Return a field from the global info, or default if the field is not set.
        """
        return self._metadata[self.GLOBAL_KEY].get(key, default)

    def add_capture(self, start_index, metadata=None):
        """
        Insert capture info for sample starting at start_index.
        If there is already capture info for this index, metadata will be merged
        with the existing metadata, overwriting keys if they were previously set.
        """
        assert start_index >= self._get_start_offset()
        capture_list = self._metadata[self.CAPTURE_KEY]
        new_capture = metadata or {}
        new_capture[self.START_INDEX_KEY] = start_index
        # merge if capture exists
        merged = False
        for existing_capture in self._metadata[self.CAPTURE_KEY]:
            if existing_capture[self.START_INDEX_KEY] == start_index:
                existing_capture = dict_merge(existing_capture, new_capture)
                merged = True
        if not merged:
            capture_list += [new_capture]
        # sort captures by start_index
        self._metadata[self.CAPTURE_KEY] = sorted(
            capture_list,
            key=lambda item: item[self.START_INDEX_KEY]
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
        Insert annotation at start_index with length.
        """
        assert start_index >= self._get_start_offset()
        assert length >= 1
        new_annot = metadata or {}
        new_annot[self.START_INDEX_KEY] = start_index
        new_annot[self.LENGTH_INDEX_KEY] = length

        self._metadata[self.ANNOTATION_KEY] += [new_annot]
        # sort annotations by start_index
        self._metadata[self.ANNOTATION_KEY] = sorted(
            self._metadata[self.ANNOTATION_KEY],
            key=lambda item: item[self.START_INDEX_KEY]
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
            file_size = path.getsize(self.data_file) if self.offset_and_size is None else self.offset_and_size[1]
            file_data_size = file_size - self.get_global_field(self.TRAILING_BYTES_KEY, 0) - header_bytes  # bytes
            sample_size = self.get_sample_size() # size of a sample in bytes
            num_channels = self.get_num_channels()
            sample_count = file_data_size // sample_size // num_channels
            if file_data_size % (sample_size * num_channels) != 0:
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
        if self.data_file is not None:
            new_hash = sigmf_hash.calculate_sha512(self.data_file, offset_and_size=self.offset_and_size)
        else:
            new_hash = sigmf_hash.calculate_sha512(fileobj=self.data_buffer, offset_and_size=self.offset_and_size)
        if old_hash:
            if old_hash != new_hash:
                raise SigMFFileError('Calculated file hash does not match associated metadata.')

        self.set_global_field(self.HASH_KEY, new_hash)
        return new_hash

    def set_data_file(self, data_file=None, data_buffer=None, skip_checksum=False, offset=0, size_bytes=None, map_readonly=True):
        """
        Set the datafile path, then recalculate sample count. If not skipped,
        update the hash and return the hash string.
        """
        if self.get_global_field(self.DATATYPE_KEY) is None:
            raise SigMFFileError("Error setting data file, the DATATYPE_KEY must be set in the global metadata first.")

        self.data_file = data_file
        self.data_buffer = data_buffer
        self.offset_and_size = None if (offset == 0 and size_bytes is None) else (offset, size_bytes)
        self._count_samples()

        dtype = dtype_info(self.get_global_field(self.DATATYPE_KEY))
        self.is_complex_data = dtype['is_complex']
        num_channels = self.get_num_channels()
        self.ndim = 1 if (num_channels < 2) else 2

        complex_int_separates = dtype['is_complex'] and dtype['is_fixedpoint']
        mapped_dtype_size = dtype['component_size'] if complex_int_separates else dtype['sample_size']
        mapped_length = None if size_bytes is None else size_bytes // mapped_dtype_size
        mapped_reshape = (-1,)  # we can't use -1 in mapped_length ...
        if num_channels > 1:
            mapped_reshape = mapped_reshape + (num_channels,)
        if complex_int_separates:
            # There is no corresponding numpy type, so we'll have to add another axis, with length of 2
            mapped_reshape = mapped_reshape + (2,)
        self._return_type = dtype['memmap_convert_type']
        common_args = {'dtype': dtype['memmap_map_type'], 'offset': offset}
        try:
            if self.data_file is not None:
                open_mode = 'r' if map_readonly else 'r+'
                memmap_shape = None if mapped_length is None else (mapped_length,)
                raveled = np.memmap(self.data_file, mode=open_mode, shape=memmap_shape, **common_args)
            elif self.data_buffer is not None:
                buffer_count = -1 if mapped_length is None else mapped_length
                raveled = np.frombuffer(self.data_buffer.getbuffer(), count=buffer_count, **common_args)
            else:
                raise ValueError('In sigmffile.set_data_file(), either data_file or data_buffer must be not None')
        except:  # TODO include likely exceptions here
            warnings.warn('Failed to create data array from memory-map-file or buffer!')
        else:
            self._memmap = raveled.reshape(mapped_reshape)
            self.shape = self._memmap.shape if (self._return_type is None) else self._memmap.shape[:-1]

        if skip_checksum:
            return None
        return self.calculate_hash()

    def validate(self):
        """
        Check schema and throw error if issue.
        """
        version = self.get_global_field(self.VERSION_KEY)
        validate.validate(self._metadata, self.get_schema())

    def archive(self, name=None, fileobj=None):
        """Dump contents to SigMF archive format.

        `name` and `fileobj` are passed to SigMFArchive and are defined there.

        """
        archive = SigMFArchive(self, name, fileobj)
        return archive.path

    def tofile(self, file_path, pretty=True, toarchive=False, skip_validate=False):
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
        if not skip_validate:
            self.validate()
        fns = get_sigmf_filenames(file_path)
        if toarchive:
            self.archive(fns['archive_fn'])
        else:
            with open(fns['meta_fn'], 'w') as fp:
                self.dump(fp, pretty=pretty)
                fp.write('\n')  # text files should end in carriage return

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
        self.is_complex_data = dtype['is_complex']
        is_fixedpoint_data = dtype['is_fixedpoint']
        is_unsigned_data = dtype['is_unsigned']
        data_type_in = dtype['sample_dtype']
        component_type_in = dtype['component_dtype']
        component_size = dtype['component_size']

        data_type_out = np.dtype("f4") if not self.is_complex_data else np.dtype("f4, f4")
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
            if self.is_complex_data:
                data = data.view(np.complex64)
        else:
            data = data.view(component_type_in)

        fp.close()
        return data


class SigMFCollection(SigMFMetafile):
    VERSION_KEY = "core:version"
    DESCRIPTION_KEY = "core:description"
    AUTHOR_KEY = "core:author"
    COLLECTION_DOI_KEY = "core:collection_doi"
    LICENSE_KEY = "core:license"
    EXTENSIONS_KEY = "core:extensions"
    STREAMS_KEY = "core:streams"
    COLLECTION_KEY = "collection"
    VALID_COLLECTION_KEYS = [
        AUTHOR_KEY, COLLECTION_DOI_KEY, DESCRIPTION_KEY, EXTENSIONS_KEY, LICENSE_KEY, STREAMS_KEY, VERSION_KEY
    ]
    VALID_KEYS = {COLLECTION_KEY: VALID_COLLECTION_KEYS}

    def __init__(self, metafiles=None, metadata=None, skip_checksums=False):
        """Create a SigMF Collection object.

        Parameters:

        metafiles -- A list of SigMF metadata filenames objects comprising the Collection,
                    there must be at least one file. If the files do not exist, this will
                    raise a SigMFFileError.

        metadata  -- collection metadata to use, if not provided this will populate a
                    minimal set of default metadata. The core:streams field will be
                    regenerated automatically
        """
        super(SigMFCollection, self).__init__()
        self.skip_checksums = skip_checksums

        if metadata is None:
            self._metadata = {self.COLLECTION_KEY:{}}
            self._metadata[self.COLLECTION_KEY][self.VERSION_KEY] = __version__
            self._metadata[self.COLLECTION_KEY][self.STREAMS_KEY] = []
        else:
            self._metadata = metadata

        if metafiles is None:
            self.metafiles = []
        else:
            self.set_streams(metafiles)

        if not self.skip_checksums:
            self.verify_stream_hashes()

    def __len__(self):
        '''
        the length of a collection is the number of streams
        '''
        return len(self.get_stream_names())

    def verify_stream_hashes(self):
        '''
        compares the stream hashes in the collection metadata to the metadata files
        '''
        streams = self.get_collection_field(self.STREAMS_KEY, [])
        for stream in streams:
            old_hash = stream.get('hash')
            metafile_name = get_sigmf_filenames(stream.get('name'))['meta_fn']
            if path.isfile(metafile_name):
                new_hash = sigmf_hash.calculate_sha512(filename=metafile_name)
                if old_hash != new_hash:
                    raise SigMFFileError(f'Calculated file hash for {metafile_name} does not match collection metadata.')

    def set_streams(self, metafiles):
        '''
        configures the collection `core:streams` field from the specified list of metafiles
        '''
        self.metafiles = metafiles
        streams = []
        for metafile in self.metafiles:
            if metafile.endswith('.sigmf-meta') and path.isfile(metafile):
                stream = {
                    "name": get_sigmf_filenames(metafile)['base_fn'],
                    "hash": sigmf_hash.calculate_sha512(filename=metafile)
                }
                streams.append(stream)
            else:
                raise SigMFFileError(f'Specifed stream file {metafile} is not a valid SigMF Metadata file')
        self.set_collection_field(self.STREAMS_KEY, streams)

    def get_stream_names(self):
        '''
        returns a list of `name` object(s) from the `collection` level `core:streams` metadata
        '''
        return [s.get('name') for s in self.get_collection_field(self.STREAMS_KEY, [])]

    def set_collection_info(self, new_collection):
        """
        Overwrite the collection info with a new dictionary.
        """
        self._metadata[self.COLLECTION_KEY] = new_collection.copy()

    def get_collection_info(self):
        """
        Returns a dictionary with all the collection info.
        """
        try:
            return self._metadata.get(self.COLLECTION_KEY, {})
        except AttributeError:
            return {}

    def set_collection_field(self, key, value):
        """
        Inserts a value into the collection field.
        """
        self._metadata[self.COLLECTION_KEY][key] = value

    def get_collection_field(self, key, default=None):
        """
        Return a field from the collection info, or default if the field is not set.
        """
        return self._metadata[self.COLLECTION_KEY].get(key, default)

    def tofile(self, file_path, pretty=True):
        '''
        Write metadata file

        Parameters
        ----------
        file_path : string
            Location to save.
        pretty : bool, default True
            When True will write more human-readable output, otherwise will be flat JSON.
        '''
        fns = get_sigmf_filenames(file_path)
        with open(fns['collection_fn'], 'w') as fp:
            self.dump(fp, pretty=pretty)
            fp.write('\n')  # text files should end in carriage return

    def get_SigMFFile(self, stream_name=None, stream_index=None):
        '''
        Returns the SigMFFile instance of the specified stream if it exists
        '''
        metafile = None
        if stream_name is not None:
            if stream_name in self.get_stream_names():
                metafile = stream_name + '.sigmf_meta'
        if stream_index is not None and stream_index < self.__len__():
            metafile = self.get_stream_names()[stream_index] + '.sigmf_meta'

        if metafile is not None:
            return fromfile(metafile, skip_checksum=self.skip_checksums)

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

    The `dir` parameter is no longer used as this function has been changed to
    access SigMF archives without extracting them.
    """
    from .archivereader import SigMFArchiveReader
    return SigMFArchiveReader(archive_path).sigmffile


def fromfile(filename, skip_checksum=False):
    '''
    Creates and returns a SigMFFile or SigMFCollection instance with metadata
    loaded from the specified file. The filename may be that of either a
    sigmf-meta file, a sigmf-data file, a sigmf-collection file, or a sigmf
    archive.

    Parameters
    ----------
    filename: str
        Path for SigMF Metadata, Dataset, Archive or Collection (with or without extension).
    skip_checksum: bool, default False
        When True will not read entire dataset to caculate hash.

    Returns
    -------
    object
        SigMFFile object with dataset & metadata or a SigMFCollection depending on the type of file
    '''
    fns = get_sigmf_filenames(filename)
    meta_fn = fns['meta_fn']
    archive_fn = fns['archive_fn']
    collection_fn = fns['collection_fn']

    if (filename.lower().endswith(SIGMF_ARCHIVE_EXT) or not path.isfile(meta_fn)) and path.isfile(archive_fn):
        return fromarchive(archive_fn)

    if (filename.lower().endswith(SIGMF_COLLECTION_EXT) or not path.isfile(meta_fn)) and path.isfile(collection_fn):
        collection_fp = open(collection_fn, "rb")
        bytestream_reader = codecs.getreader("utf-8")
        mdfile_reader = bytestream_reader(collection_fp)
        metadata = json.load(mdfile_reader)
        collection_fp.close()

        return SigMFCollection(metadata=metadata, skip_checksums=skip_checksum)

    else:
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
    return {'base_fn': filename,
            'data_fn': filename+SIGMF_DATASET_EXT,
            'meta_fn': filename+SIGMF_METADATA_EXT,
            'archive_fn': filename+SIGMF_ARCHIVE_EXT,
            'collection_fn': filename+SIGMF_COLLECTION_EXT}
