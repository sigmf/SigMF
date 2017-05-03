# Signal Metadata Format Specification v0.0.1

## Abstract

The Signal Metadata Format (SigMF) specifies a way to describe sets of recorded
digital signal samples with metadata written in JSON. SigMF can be used to
describe general information about a collection of samples, the characteristics
of the system that generated the samples, and features of the signal itself.

## Status of this Document

This document is currently under active development and is not stable. We
encourage anyone and everyone interested in this effort to participate. We are
using the Issue Tracker for the repository as the medium for discussion, and
changes are submitted as Pull Requests.

This effort was kicked off at
the [DARPA Brussels Hackfest](http://www.darpahackfest.com/) in early February
2017, and first announced at FOSDEM'17.

## Copyright Notice

This document is Copyright of The GNU Radio Foundation, Inc. 

This document is available under the [CC-BY-SA License](http://creativecommons.org/licenses/by-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

## Table of Contents

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Signal Metadata Format Specification v0.0.1](#signal-metadata-format-specification-v001)
    - [Abstract](#abstract)
    - [Status of this Document](#status-of-this-document)
    - [Copyright Notice](#copyright-notice)
    - [Table of Contents](#table-of-contents)
    - [Introduction](#introduction)
    - [Conventions Used in this Document](#conventions-used-in-this-document)
    - [Specification](#specification)
        - [Files](#files)
        - [Dataset Format](#dataset-format)
        - [Metadata Format](#metadata-format)
            - [Datatypes](#datatypes)
            - [Namespaces](#namespaces)
            - [Global Object](#global-object)
            - [Capture Object](#capture-object)
            - [Annotation Object](#annotation-object)
        - [Dataset Licensing](#dataset-licensing)
        - [SigMF Compliance by Applications](#sigmf-compliance-by-applications)
    - [Example](#example)
- [Acknowledgements](#acknowledgements)

<!-- markdown-toc end -->

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

## Conventions Used in this Document

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

JSON keywords are used as defined in [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

## Specification

The SigMF specification fundamentally describes two types of information:
datasets, and metadata associated with those datasets. Taken together, a dataset
with its SigMF metadata is a `SigMF recording`.

Datasets, for purposes of this specification, are sets of digital samples.
The samples may be created by digital synthesis (i.e., simulation) or by an
actual Analog-to-Digital Converter (ADC) that is sampling an analog signal.

Metadata describes the dataset with which it is associated. The metadata
includes information meant for the human users of the dataset, such as a title and
description, and information meant for computer applications (tools) that
operate on the dataset.

### Files

A SigMF recording consists of two files: a SigMF `metadata` file and a
`dataset` file. The dataset file is a binary file of samples, and the metadata
file contains information that describes the dataset.

1. The metadata and dataset MUST be in separate files.
2. The metadata file MUST only describe one dataset file.
3. The metadata file MUST be stored in UTF-8 encoding.
3. The metadata file MUST have a `.meta` filename extension.
4. The dataset file MUST have a `.data` filename extension.
5. The names of the metadata and dataset files must be identical (excepting
   their extensions).

### Dataset Format

The samples in the dataset file must be in a SigMF-supported format. There are
four orthogonal characteristics of sample data: complex or real, floating-point
or fixed-point, bit-width, and endianness. All of these must be explicitly
specified.

SigMF sample formats are specified by strings that indicate the type for each of
the four different characteristics. The types are specified with the following
characters / strings:

* `r`: real-valued data
* `c`: complex (quadrature) data
* `f`: floating-point data
* `i`: signed fixed-point data
* `u`: unsigned fixed-point data
* `8`: 8-bit samples
* `16`: 16-bit samples
* `32`: 32-bit samples
* `_le`: little-endian data
* `_be`: big-endian data

The above strings must be joined in a specific order to create a type string:

`<r|c><f|i|u><8|16|32><_le|_be>`

So, for example, the string `"cf32_le"` specifies `complex 32-bit floating-point
samples stored in little-endian`, and the string `ru16_be` specifies `real
unsigned 16-bit samples stored in big-endian`.

The samples should be written to the dataset file without separation, and the
dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, `EOF` characters, etc.,).

### Metadata Format

SigMF is written in JSON and takes the form of JSON name/value pairs which are
contained within JSON `objects`. There are three types of top-level objects:
`global`, `capture`, and `annotations`. The names of the name/value pairs must
be namespaced.

The format of the name/value pairs is:

```
"namespace:name": value,
```

1. The metadata MUST be written in [JSON](http://www.json.org/), as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).
2. The entire contents of the metadata file MUST be contained within a single
   JSON object (i.e., the first character of the file MUST be '{' and the last
   character of the file MUST be '}'. This object is hereafter called the
   `top-level object`.
3. The top-level object MUST contain three values named `global`, `capture`,
   and `annotations`.
4. Metadata name/value pairs SHALL NOT be assumed to have carried over between
   segments. If a name/value pair applies to a particular segment, then it must
   appear in that segment, even if the value is unchanged relative to the
   previous segment.

#### Datatypes

The values in each name/value pair must be one of the following datatypes:

|type|long-form name|description|
|----|----|-----------|
|int|integer|Signed 64-bit integer.|
|uint|unsigned long|Unsigned 64-bit integer.|
|double|double-precision floating-point number|A 64-bit float as defined by IEEE 754.|
|string|string|A string of characters, as defined by the JSON standard.|
|boolean|boolean|Either `true` or `false`, as defined by the JSON standard.|
|null|null|`null`, as defined by the JSON standard.|
   
#### Namespaces

Namespaces provide a way to further classify name/value pairs within metadata
objects. This specification defines the `core` namespace, which contains
commonly used name/value pairs for describing signal data.

Some keys within the `core` namespace are optional, and others are required. The
fields that are required are those that are minimally necessary to parse &
process the dataset, or that have obvious defaults that are valid. Other fields
are 'optional', even if they are highly encouraged.

Other namespaces may be defined by the user as needed.

#### Global Object

The `global` object consists of name/value pairs that provide information
applicable to the entire dataset. It contains the information that is minimally
necessary to open and parse the dataset file, as well as general information
about the recording itself.

The following names are specified in the `core` namespace and should be used in
the `global` object:

|name|required|type|description|
|----|--------------|-------|-----------|
|`datatype`|true|string|The format of the stored samples in the dataset file. Its value must be a valid SigMF dataset format type string.|
|`sample_rate`|false|double|The sample rate of the signal in samples per second.|
|`version`|true|string|The version of the SigMF specification used to create the metadata file.|
|`sha512`|false|string|The SHA512 hash of the dataset file associated with the SigMF file.|
|`offset`|false|uint64|The index number of the first sample in the dataset. This value defaults to zero. Typically used when a recording is split over multiple files.|
|`description`|false|string|A text description of the SigMF recording.|
|`author`|false |string|The author's name (and optionally e-mail address).|
|`date`|false|string|An ISO-8601 formatted string of the capture date of the recording.|
|`license`|false|string|The license under which the recording is offered.|
|`hw`|false |string|A text description of the hardware used to make the recording.|

#### Capture Array

The `capture` value is an array of _capture segment objects_ that describe the
parameters of the signal capture. It MUST be sorted by the value of each
segment's `core:sample_start` key, ascending.

##### Capture Segment Objects

Capture segment objects are composed of name/value pairs.

Each capture segment object must contain a `core:sample_start` name/value pair,
which indicates the first index at which the rest of the segment's name/value
pairs apply.

The following names are specified in the `core` namespace and should be used in
capture segment objects:

|name|required|type|description|
|----|--------------|-------|-----------|
|`sample_start`|true|uint|The sample index at which this segment takes effect.|
|`frequency`|false|double|The center frequency of the signal in Hz.|
|`time`|false|string|An ISO-8601 formatted string indicating the timestamp of the sample index specified by `sample_start`.|

#### Annotation Array

The `annotation` value is an array of _annotation segment objects_ that
describe anything regarding the signal data not part of the `capture` and
`global` objects. It MUST be sorted by the value of each segment's
`core:sample_start` key, ascending.

##### Annotation Segment Objects

Annotation segment objects contain name/value pairs.

Each annotation segment object must contain a `core:sample_start` name/value
pair, which indicates the first index at which the rest of the segment's
name/value pairs apply.

The following names are specified in the `core` namespace and should be used in
annotation segment objects:

|name|required|type|description|
|----|--------------|-------|-----------|
|`sample_start`|true|uint|The sample index at which this segment takes effect.|
|`sample_count`|true|uint|The number of samples that this segment applies to. |
|`generator`|false|string|Human-readable name of the entity that created this annotation.|
|`comment`|false|string|A human-readable comment.|
|`freq_lower_edge`|false|double|The lower edge of the frequency band of a signal feature that this annotation describes.|
|`freq_upper_edge`|false|double|The upper edge of the frequency band of a signal feature that this annotation describes. |
|`latitude`|false|need a standard?| |
|`longitude`|false|need a standard?| |

### Dataset Licensing

You may specify any license of your choosing. Recommended licenses for SigMF
recordings are:

* [CC0 1.0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/)
* [CC-BY Attrition 2.0 Generic](https://creativecommons.org/licenses/by/2.0/)

### SigMF Compliance by Applications

In order to be `SigMF Compliant`, an application must meet the following
requirements:

1. Adheres to and supports for the file rules, dataset formats, `objects`,
   `namespaces`, and `names` specified by this document.
2. Must be able to ignore any `object` or `namespace` not specified by this
   document and still function normally.
3. `Capture` segments referring to non-existent samples should be ignored.
4. Must treat consecutive capture segments whose metadata is equivalent for
   purposes of that application (i.e., it may be different in values ignored by
   the application such as optional values or unknown extensions) as it would
   a single segment.

## Example

[TODO] Provide an example of metadata file contents.

# Acknowledgements

This specification originated at the DARPA Brussels Hackfest 2017.

