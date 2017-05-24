# Signal Metadata Format (SigMF)

Welcome to the SigMF project! The SigMF specification document is the
`sigmf-spec.md` file in this repository:

SigMF: [Signal Metadata Format Specification](sigmf-spec.md)

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

(Taken from the
[Introduction](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#introduction)
of the specification document.)

## Contributing

The SigMF standards effort is organized entirely within this Github repository.
Questions, suggestions, bug reports, etc., are discussed in [the issue
tracker](https://github.com/gnuradio/SigMF/issues). Changes to the specification
only occur through [Pull Requests](https://github.com/gnuradio/SigMF/pulls).

This ensures that the history and background of all discussions and changes are
maintained for posterity.

Anyone is welcome to get involved - indeed, the more people involved in the
discussions, the more useful the standard is likely to be.

## Frequently Asked Questions

#### Is this a GNU Radio effort?

*No*, this is not a GNU Radio-specific effort. It is hosted under the GNU Radio
Github account because this effort first emerged from a group of GNU Radio core
developers, but the goal of the project to provide a standard that will be
useful to anyone and everyone, regardless of tool or workflow.

#### Is this specific to wireless communications?

*No*, similar to the response, above, the goal is to create something that is
generally applicable to _signal processing_, regardless of whether or not the
application is communications related.

#### It seems like some issues take a long time to resolve?

Yes, and in most cases this is by design. Since the goal of this project is
create a broadly useful standards document, it is in our best interest to make
sure we gather and consider as many opinions as possible, and produce the
clearest and most exact language possible. This necessarily requires extreme
attention to detail and diligence.
