<p align="center">
<img src="https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/logo/sigmf_logo.png" width="30%" />
</p>

# Signal Metadata Format (SigMF)

Welcome to the SigMF project! The [SigMF specification document](sigmf-spec.md)
is the `sigmf-spec.md` file in this repository. Below we discuss why and how
you might use SigMF in your projects.

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

1. Within **Python**, using the [official SigMF Python package **sigmf**](https://github.com/sigmf/sigmf-python) available from pip: `pip install sigmf`
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

Software that seeks to perform validation on metadata can open a metafile, parse which extensions are used (if any), then pull the core JSON schema plus the JSON schemas for each extension being used (and optionally, an application-specific schema), then merge the global/captures/annotations objects between all schemas, and disable `additionalProperties` for all three so that typos can be detected.

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
