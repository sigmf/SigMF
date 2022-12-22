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
        "core:version": "1.0.0"
    },
    "captures": [
        {
            "core:sample_start": 0,
            "core:frequency": 915000000
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
tracker](https://github.com/gnuradio/SigMF/issues), feel free to create
a new issue and provide your input, even if it's not a traditional issue.
Changes to the specification only occur through [Pull Requests](https://github.com/gnuradio/SigMF/pulls).
This ensures that the history and background of all discussions and changes are maintained for posterity.

There is also a SigMF chat room on [GNU Radio's Matrix chat server](https://wiki.gnuradio.org/index.php/Chat)
where you can ask SigMF-related questions, or participate in various discussions.
Lastly, there are monthly SigMF calls covering a variety of topics, on the third Monday of each month
at 11:30AM Eastern/New York Time, please email marc@gnuradio.org for an invite and Zoom link.

Anyone is welcome to get involved - indeed, the more people involved in the
discussions, the more useful the standard is likely to be!

## Extensions

The "Core" SigMF standard is intentionally kept limited in scope, additional metadata fields can be added through [SigMF Extensions](https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/sigmf-spec.md#extension-namespaces). For example, the [signal extension](https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/extensions/signal.sigmf-ext.md) provides a standard way to specify modulation schemes and other attributes of wireless comms signals. Several general purpose canonical extensions live within this repository directly in the [extensions directory](https://github.com/gnuradio/SigMF/tree/sigmf-v1.x/extensions), while others are maintained by third parties. Below we include a listing of some popular, compliant SigMF extensions. To have your extension reviewed for inclusion on this list, please open a PR adding the repository to the list below:

* [NTIA's series of extensions](https://github.com/NTIA/sigmf-ns-ntia)

## SigMF Python Package

If you are interested in using SigMF within Python, we recommend using our Python package which lives within this repo, and works with Python 3.6 and higher.

### Installation

To install the latest released version of the SigMF package, install it from pip:

```bash
pip install sigmf
```

To install the latest development version, build the package from source:

```bash
git clone https://github.com/gnuradio/SigMF.git
cd SigMF
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
import numpy as np
import sigmf
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
meta.tofile('example.sigmf-meta') # extension is optional
```

#### Load a SigMF Archive and slice its data without untaring it

Since an *archive* is merely a tarball (uncompressed), and since there any many
excellent tools for manipulating tar files, it's fairly straightforward to
access the *data* part of a SigMF archive without untaring it.
This is a compelling feature because 1) archives make it harder for the `-data`
and the `-meta` to get separated, and 2) some datasets are so large that it can
be impractical (due to available disk space, or slow network speeds if the
archive file resides on a network file share) or simply obnoxious to untar it
first.

```python
In [1]: import sigmf

In [2]: arc = sigmf.SigMFArchiveReader('/src/LTE.sigmf')

In [3]: arc.shape
Out[3]: (15379532,)

In [4]: arc.ndim
Out[4]: 1

In [5]: arc[:10]
Out[5]: 
array([-20.+11.j, -21. -6.j, -17.-20.j, -13.-52.j,   0.-75.j,  22.-58.j,
        48.-44.j,  49.-60.j,  31.-56.j,  23.-47.j], dtype=complex64)
```

The preceeding example exhibits another feature of this approach; the archive
`LTE.sigmf` is actually `complex-int16`'s on disk, for which there is no
corresponding type in `numpy`.
However, the `.sigmffile` member keeps track of this, and converts the data
to `numpy.complex64` *after* slicing it, that is, after reading it from disk.

```python
In [6]: arc.sigmffile.get_global_field(sigmf.SigMFFile.DATATYPE_KEY)
Out[6]: 'ci16_le'

In [7]: arc.sigmffile._memmap.dtype
Out[7]: dtype('int16')

In [8]: arc.sigmffile._return_type
Out[8]: '<c8'
```

Another supported mode is the case where you might have an archive that *is not
on disk* but instead is simply `bytes` in a python variable.
Instead of needing to write this out to a temporary file before being able to
read it, this can be done "in mid air" or "without touching the ground (disk)".

```python
In [1]: import sigmf, io

In [2]: sigmf_bytes = io.BytesIO(open('/src/LTE.sigmf', 'rb').read())

In [3]: arc = sigmf.SigMFArchiveReader(archive_buffer=sigmf_bytes)

In [4]: arc[:10]
Out[4]: 
array([-20.+11.j, -21. -6.j, -17.-20.j, -13.-52.j,   0.-75.j,  22.-58.j,
        48.-44.j,  49.-60.j,  31.-56.j,  23.-47.j], dtype=complex64)
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
