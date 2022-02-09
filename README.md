<p align="center">
<img src="https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/logo/sigmf_logo.png" width="30%" />
</p>

# Signal Metadata Format (SigMF)

Welcome to the SigMF project! The [SigMF specification document](sigmf-spec.md) is the
`sigmf-spec.md` file in this repository.  Below we discuss why and how you might use SigMF in your projects.

## Introduction

Sharing sets of recorded signal data is an important part of science and
engineering. It enables multiple parties to collaborate, is often a necessary
part of reproducing scientific results (a requirement of scientific rigor), and
enables sharing data with those who do not have direct access to the equipment
required to capture it.

Unfortunately, these datasets have historically not been very portable, and
there is not an agreed upon method of sharing metadata descriptions of the
recorded data itself. This is the problem that SigMF solves.

By providing a standard way to describe data recordings, SigMF facilitates the
sharing of data, prevents the "bitrot" of datasets wherein details of the
capture are lost over time, and makes it possible for different tools to operate
on the same dataset, thus enabling data portability between tools and workflows.

SigMF signal recordings typically involve a data file (e.g., a binary file of IQ
or RF samples) and a metadata file containing plain text that describes the data.
Together these files represent one recording, such as `example.sigmf-data` and
`example.sigmf-meta`.  Here is a minimal example of a SigMF `.sigmf-meta` file:

```json
{
    "global": {
        "core:datatype": "cf32_le",
        "core:sample_rate": 1000000,
        "core:hw": "PlutoSDR with 915 MHz whip antenna",
        "core:author": "Art Vandelay",
        "core:version": "1.0.0",
    },
    "captures": [
        {
            "core:sample_start": 0,
            "core:frequency": 915000000,
        }
    ],
    "annotations": []
}
```

## Using SigMF

There are at least four ways you can use SigMF today, thanks to the community-supported projects:

1. Within **Python**, using the Python package included in this repo and discussed below
2. Within **C++** using the [header-only C++ library **libsigmf**](https://github.com/deepsig/libsigmf) maintained by DeepSig
3. Within **GNU Radio** using the [out-of-tree module **gr-sigmf**](https://github.com/skysafe/gr-sigmf) maintained by SkySafe
4. Manually, using our examples and the [spec itself](sigmf-spec.md), even if it's simply editing a text file


## Contributing

The SigMF standards effort is organized entirely within this Github repository.
Questions, suggestions, bug reports, etc., are discussed in [the issue
tracker](https://github.com/gnuradio/SigMF/issues). Changes to the specification
only occur through [Pull Requests](https://github.com/gnuradio/SigMF/pulls).

This ensures that the history and background of all discussions and changes are
maintained for posterity.

Anyone is welcome to get involved - indeed, the more people involved in the
discussions, the more useful the standard is likely to be.

## SigMF Python Package

If you are interested in using SigMF within Python, we recommend using our Python package which lives within this repo.

### Installation

This module can be installed the typical way:

```bash
pip install .
```

To run the included QA tests:
```bash
pytest
```

### Use Cases

#### Load a SigMF archive; read all samples & metadata

```python
import sigmf
handle = sigmf.sigmffile.fromfile('example.sigmf')
handle.read_samples() # returns all timeseries data
handle.get_global_info() # returns 'global' dictionary
handle.get_captures() # returns list of 'captures' dictionaries
handle.get_annotations() # returns list of all annotations
```

#### Verify SigMF dataset integrity & compliance

```bash
sigmf_validate example.sigmf 
```

#### Load a SigMF dataset; read its annotation, metadata, and samples

```python
from sigmf import SigMFFile, sigmffile

# Load a dataset
filename = 'logo/sigmf_logo' # extension is optional
signal = sigmffile.fromfile(filename)

# Get some metadata and all annotations
sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
sample_count = signal.sample_count
signal_duration = sample_count / sample_rate
annotations = signal.get_annotations()

# Iterate over annotations
for adx, annotation in enumerate(annotations):
    annotation_start_idx = annotation[SigMFFile.START_INDEX_KEY]
    annotation_length = annotation[SigMFFile.LENGTH_INDEX_KEY]
    annotation_comment = annotation.get(SigMFFile.COMMENT_KEY, "[annotation {}]".format(adx))

    # Get capture info associated with the start of annotation
    capture = signal.get_capture_info(annotation_start_idx)
    freq_center = capture.get(SigMFFile.FREQUENCY_KEY, 0)
    freq_min = freq_center - 0.5*sample_rate
    freq_max = freq_center + 0.5*sample_rate

    # Get frequency edges of annotation (default to edges of capture)
    freq_start = annotation.get(SigMFFile.FLO_KEY)
    freq_stop = annotation.get(SigMFFile.FHI_KEY)

    # Get the samples corresponding to annotation
    samples = signal.read_samples(annotation_start_idx, annotation_length)
```

#### Write a SigMF file from a numpy array

```python
import datetime as dt
from sigmf import SigMFFile
from sigmf.utils import get_data_type_str

# suppose we have an complex timeseries signal
data = np.zeros(1024, dtype=np.complex64)

# write those samples to file in cf32_le
data.tofile('example.sigmf-data')

# create the metadata
meta = SigMFFile(
    data_file='example.sigmf-data', # extension is optional
    global_info = {
        SigMFFile.DATATYPE_KEY: get_data_type_str(data),  # in this case, 'cf32_le'
        SigMFFile.SAMPLE_RATE_KEY: 48000,
        SigMFFile.AUTHOR_KEY: 'jane.doe@domain.org',
        SigMFFile.DESCRIPTION_KEY: 'All zero example file.',
        SigMFFile.VERSION_KEY: sigmf.__version__,
    }
)

# create a capture key at time index 0
meta.add_capture(0, metadata={
    SigMFFile.FREQUENCY_KEY: 915000000,
    SigMFFile.DATETIME_KEY: dt.datetime.utcnow().isoformat()+'Z',
})

# add an annotation at sample 100 with length 200 & 10 KHz width
meta.add_annotation(100, 200, metadata = {
    SigMFFile.FLO_KEY: 914995000.0,
    SigMFFile.FHI_KEY: 915005000.0,
    SigMFFile.COMMENT_KEY: 'example annotation',
})

# check for mistakes & write to disk
assert meta.validate()
meta.tofile('example.sigmf-meta') # extension is optional
```

## Frequently Asked Questions

### Is this a GNU Radio effort?

*No*, this is not a GNU Radio-specific effort. It is hosted under the GNU Radio
Github account because this effort first emerged from a group of GNU Radio core
developers, but the goal of the project to provide a standard that will be
useful to anyone and everyone, regardless of tool or workflow.

### Is this specific to wireless communications?

*No*, similar to the response, above, the goal is to create something that is
generally applicable to _signal processing_, regardless of whether or not the
application is communications related.

### It seems like some issues take a long time to resolve?

Yes, and in most cases this is by design. Since the goal of this project is
create a broadly useful standards document, it is in our best interest to make
sure we gather and consider as many opinions as possible, and produce the
clearest and most exact language possible. This necessarily requires extreme
attention to detail and diligence.
