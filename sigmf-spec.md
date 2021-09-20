# Signal Metadata Format Specification v0.0.2

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

**Table of Contents**

- [Signal Metadata Format Specification v0.0.2](#signal-metadata-format-specification-v002)
  - [Abstract](#abstract)
  - [Status of this Document](#status-of-this-document)
  - [Copyright Notice](#copyright-notice)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Conventions Used in this Document](#conventions-used-in-this-document)
  - [Specification](#specification)
    - [Files](#files)
      - [SigMF Archives](#sigmf-archives)
    - [Dataset Format](#dataset-format)
    - [Metadata Format](#metadata-format)
      - [Datatypes](#datatypes)
      - [Namespaces](#namespaces)
        - [Extension Namespaces](#extension-namespaces)
        - [Canonical Extension Namespaces](#canonical-extension-namespaces)
      - [Global Object](#global-object)
        - [The `geolocation` Field](#the-geolocation-field)
        - [The `extensions` Field](#the-extensions-field)
        - [The `collection` Field](#the-collection-field)
      - [Captures Array](#captures-array)
        - [Capture Segment Objects](#capture-segment-objects)
          - [The `global_index` Pair](#the-global_index-pair)
          - [The `datetime` Pair](#the-datetime-pair)
      - [Annotations Array](#annotations-array)
        - [Annotation Segment Objects](#annotation-segment-objects)
    - [Collection Format](#collection-format)
    - [Licensing](#licensing)
    - [SigMF Compliance by Applications](#sigmf-compliance-by-applications)
  - [Examples](#examples)
      - [Example of the `global` `core:offset` field usage:](#example-of-the-global-coreoffset-field-usage)
  - [Citing SigMF](#citing-sigmf)
  - [Acknowledgements](#acknowledgements)

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

Augmented Backus-Naur form (ABNF) is used as defined by [RFC 5234](https://tools.ietf.org/html/rfc5234)
and updated by [RFC 7405](https://tools.ietf.org/html/rfc7405).

Fields defined as "human-readable", a "string", or simply as "text" shall be
treated as plaintext where whitespace is significant, unless otherwise
specified. Fields defined "human/machine-readable" should be short, simple
text strings without whitespace that are easily understood by a human and
readily parsed by software.

## Specification

The SigMF specification fundamentally describes two types of information:
datasets, and metadata associated with those datasets. Taken together, a dataset
with its SigMF metadata is a `SigMF Recording`.

Datasets, for purposes of this specification, are sets of digital measurements
generically called `samples` in this document. The samples can represent any
time-varying source of information. They may, for example, be digital samples
created by digital synthesis or by an Analog-to-Digital Converter. They could
also be geolocation coordinates from a GNSS receiver, temperature readings
from a thermal sensor, or any other stored digital measurement information.

Metadata describes the dataset with which it is associated. The metadata
includes information meant for the human users of the dataset, such as a title
and description, and information meant for computer applications (tools) that
operate on the dataset.

### Files

A `SigMF Recording` is the fundamental unit of SigMF, and consists of two files: a SigMF `metadata` file and
a `dataset` file. The dataset file is a binary file of digital samples, and the
metadata file contains information that describes the dataset. Multiple Recordings MAY be organized in a `SigMF Collection`, which describes relationships between recordings, and is defined in a `collection` file.

`SigMF Recording` Rules:
1. The metadata and dataset MUST be in separate files.
2. The metadata file MUST only describe one dataset file.
3. The metadata file MUST be stored in UTF-8 encoding.
4. The metadata file MUST have a `.sigmf-meta` filename extension.
5. The dataset file MUST have a `.sigmf-data` filename extension.
6. The names of the metadata and dataset files must be identical (excepting
   their extensions).

`SigMF Collection` Rules:
1. The collection MUST be defined in its own file, separate from any Recording's metadata.
2. The collection file MUST be stored in UTF-8 encoding.
3. The collection file MUST have a `.sigmf-collection` filename extension.

#### SigMF Archives

The metadata and dataset files that comprise a `SigMF Recording` may be combined
into a file archive. A `SigMF Archive` may contain multiple `SigMF Recordings`, which may be related by a `SigMF Collection`.

1. The archive MUST use the `tar` archive format, as specified by POSIX.1-2001.
2. The archive file's filename extension MUST be `.sigmf`.
3. The archive MUST contain the following files: for each contained recording
   with some name given here meta-syntactically as `N`, files named `N` (a
   directory), `N/N.sigmf-meta`, and `N/N.sigmf-data`.
4. The archive MAY contain a `.sigmf-collection` file in the top-level directory.
5. It is RECOMMENDED that if recordings in an archive represent a continuous
   dataset that has been split into separate recordings, that their filenames
   reflect the order of the series by appending a hyphenated zero-based index
   (e.g., `N-0`, `N-1`, `N-2`, etc.,).

Each recording in an archive, even if connected to others by being part of
a larger dataset, MUST be evaluated independently for compliance to the SigMF
standard, and thus all metadata MAY be different between the recordings.

### Dataset Format

The samples in the dataset file must be in a SigMF-supported format. There are
four orthogonal characteristics of sample data: complex or real, floating-point
or integer, bit-width, and endianness. The following ABNF rules specify the
dataset formats defined in the SigMF `core` namespace:

```abnf
    dataset-format = (real / complex) ((type endianness) / byte)

    real = "r"
    complex = "c"

    type = floating-point / signed-integer / unsigned-integer
    floating-point = "f32"
    signed-integer = "i32" / "i16"
    unsigned-integer = "u32" / "u16"

    endianness = little-endian / big-endian
    little-endian = "_le"
    big-endian = "_be"

    byte = "i8" / "u8"
```

So, for example, the string `"cf32_le"` specifies `complex 32-bit floating-point
samples stored in little-endian`, the string `"ru16_be"` specifies `real
unsigned 16-bit samples stored in big-endian`, and the string `"cu8"` specifies
`complex unsigned byte`.

Note that only IEEE-754 single-precision floating-point is supported by the
SigMF `core` namespace.

The samples should be written to the dataset file without separation, and the
dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, `EOF` characters, etc.,).

Complex samples should be interleaved, with the in-phase component first (i.e.,
`I[0]` `Q[0]` `I[1]` `Q[1]` ... `I[n]` `Q[n]`). When `core:num_channels` in the
`global` object indicates that the recording contains more than one channel,
samples from those channels should be interleaved in the same manner, with
the same index from each channel's sample serially in the recording. For
example, a recording with two channels of `i16_le` representing real-valued
audio data from a stereo recording and here labeled `L` for left and `R` for
right, the data should appear as `L[0]` `R[0]` `L[1]` `R[1]` ... `L[n]` `R[n]`.
The data type specified by `core:data_type` applies to all channels of data
both real and imaginary parts.

### Metadata Format

SigMF is written in JSON and takes the form of JSON name/value pairs which are
contained within JSON `objects`. There are three types of top-level objects in the metadata file:
`global`, `captures`, and `annotations`. The names of the name/value pairs must
be namespaced.

The format of the name/value pairs is:

```JSON
"namespace:name": value,
```

1. The metadata MUST be written in [JSON](http://www.json.org/), as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).
2. The entire contents of the metadata file MUST be contained within a single
   JSON object. This object is hereafter called the `top-level object`.
3. The top-level object MUST contain three values named `global`, `captures`,
   and `annotations`.
4. Metadata name/value pairs SHALL NOT be assumed to have carried over between
   capture or annotation segments. If a name/value pair applies to a particular
   segment, then it must appear in that segment, even if the value is unchanged
   relative to the previous segment.

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
|array|JSON `array`|An `array` of other values, as defined by the JSON standard.|
|object|JSON `object`|An `object` of other values, as defined by the JSON standard.|
|GeoJSON|GeoJSON `point` object|A single GeoJSON `point` object as defined by RFC 7946.|

#### Namespaces

Namespaces provide a way to further classify name/value pairs within metadata
objects. This specification defines the `core` namespace, which contains
the foundational name/value pairs for describing signal data.

Some keys within the `core` namespace are optional, and others are required. The
fields that are required are those that are minimally necessary to parse &
process the dataset, or that have obvious defaults that are valid. Other fields
are 'optional', even if they are highly encouraged.

##### Extension Namespaces

Fields not defined in the `core` namespace may be defined in extension
namespaces. The SigMF specification defines some extension namespaces to
provide canonical definitions for commonly needed metadata fields that do not
belong in `core`. These canonical extension namespaces can be found in the
`extensions/` directory of the official SigMF repository. Other extension
namespaces may be defined by the user as needed.

1. An extension namespace MUST be defined in a single file, named
   meta-syntactically as `N.sigmf-ext.md`, where `N` is the name of the extension.
2. A `N.sigmf-ext.md` file MUST be a Github-Flavored Markdown file stored in UTF-8
   encoding.
3. Extensions MUST have version numbers. It is RECOMMENDED that extensions use
   [Semantic Versioning](https://semver.org/).
4. An extension namespace MAY define new top-level SigMF objects, name/value
   pairs, new files, new dataset formats, or new datatypes.
5. New name/value pairs defined by an extension namespace MUST be defined in
   the context of a specific SigMF top-level object (i.e., `global`,
   `captures`, `annotations`, or a new user-defined object).
6. It is RECOMMENDED that an extension namespace file follow the structure of
   the canonical extension namespaces.

##### Canonical Extension Namespaces

This is a list of the canonical extension namespaces defined by SigMF:

* `antenna` - Used to describe the antenna(s) used to for the recording.
* `capture_details` - Used to describe features of IQ captures and annotations.
* `signal` - Used to describe modulated signals used in wireless communications systems.

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
|`num_channels`|false|uint|Total number of interleaved channels in the dataset file. If omitted defaults to 1.|
|`sha512`|false|string|The SHA512 hash of the dataset file associated with the SigMF file.|
|`offset`|false|uint|The index number of the first sample in the dataset. If not provided, this value is assumed to be zero. Typically used when a recording is split over multiple files. All sample indices in SigMF are absolute, and so all other indices referenced in metadata for this recording should be greater than or equal to this value.|
|`description`|false|string|A text description of the SigMF recording.|
|`author`|false|string|The author's name (and optionally e-mail address) of the form "Bruce Wayne <wayne@example.com>".|
|`meta_doi`|false|string|The registered DOI (ISO 26324) for a recording's metadata file.|
|`data_doi`|false|string|The registered DOI (ISO 26324) for a recording's dataset file.|
|`recorder`|false|string|The name of the software used to make this SigMF recording.|
|`license`|false|string|A URL for the license document under which the recording is offered; when possible, use the canonical document provided by the license author, or, failing that, a well-known one.|
|`hw`|false |string|A text description of the hardware used to make the recording.|
|`geolocation`|false|GeoJSON `point` object|The location of the recording system.|
|`hagl`|false|double|Antenna height above ground level (in meters).|
|`extensions`|false|array|A list of objects describing extensions used by this recording.|
|`collection`|false|string|The base filename of a `collection` with which this Recording is associated.|

##### The `geolocation` Field
The `core:geolocation` field in the `global` object is used to store the
location of the recording system. The location is stored as a single
[RFC 7946](https://www.rfc-editor.org/rfc/rfc7946.txt) GeoJSON `point` object
using the convention defined by [RFC 5870](https://www.rfc-editor.org/rfc/rfc5870.txt).
Per the GeoJSON specification, the point coordinates use the WGS84 coordinate
reference system and are `longitude`, `latitude` (required, in decimal degrees),
and `altitude` (optional, in meters above the WGS84 ellipsoid) in that order. An
example including the optional third altitude value is shown below:

```JSON
  "global": {
    ...
    "core:geolocation": {
      "type": "Point",
      "coordinates": [-107.6183682, 34.0787916, 2120.0]
    }
    ...
  }
```

##### The `extensions` Field

The `core:extensions` field in the `global` object is a JSON array of _extension objects_
that describe SigMF extensions. `Extension objects` MUST contain the three key/value pairs defined below, and MUST NOT contain any other fields.

|name|required|type|description|
|----|--------------|-------|-----------|
|`name`|true|string|The name of the SigMF extension namespace.|
|`version`|true|string|The version of the extension namespace specification used.|
|`optional`|true|boolean|If this field is `true`, the extension is required to parse this recording.|

In the example below, `extension-01` is used, but not required, and 
`version 1.2.3` of `extension-02` *is* required.

```JSON
  "global": {
    ...
    "core:extensions" : [
        {
        "name": "extension-01",
        "version": "0.0.5",
        "optional": true
        },
        {
        "name": "extension-02",
        "version": "1.2.3",
        "optional": false
        }
    ]
    ...
  }
```

##### The `collection` Field
This field is used to indicated that this Recording is part of a SigMF Collection (described later in this document). It is STRONGLY RECOMMENDED that if you are building a Collection, that each Recording referenced by that Collection use this field to associate up to the `sigmf-collection` file.

#### Captures Array

The `captures` value is an array of _capture segment objects_ that describe the
parameters of the signal capture. It MUST be sorted by the value of each
capture segment's `core:sample_start` key, ascending.

##### Capture Segment Objects

Capture segment objects are composed of name/value pairs.

Each capture segment object must contain a `core:sample_start` name/value pair,
which indicates the first index at which the rest of the segment's name/value
pairs apply. The fields that are described within a `captures` segment are
scoped to that segment only and must be declared again if they are valid in
subsequent segments.

The following names are specified in the `core` namespace and should be used in
capture segment objects:

|name|required|type|description|
|----|--------------|-------|-----------|
|`sample_start`|true|uint|The sample index in the dataset file at which this segment takes effect.|
|`global_index`|false|uint|If the sample source provides a global sample count, this is the global index that maps to `sample_start`.|
|`frequency`|false|double|The center frequency of the signal in Hz.|
|`datetime`|false|string|An ISO-8601 string indicating the timestamp of the sample index specified by `sample_start`. More details, below.|

###### The `global_index` Pair

Some hardware devices are capable of 'counting' samples, or assigning sample
indices relative to the sample stream produced or consumed by the device. Note 
this is different from the sample index used to reference a sample in the SigMF 
dataset file.

These numbers are most commonly used to indicate that data was dropped by the 
hardware device. For example, if the hardware driver provides a packet of data,
labeled with samples 0 to 1000, and the following packet labels its first sample
as number 1500, that indicates that 500 samples were dropped between those two 
packets. This field allows you to indicate such a discontinuity in the recorded
sample stream as seen by the application (e.g., a SigMF writer or reader).

###### The `datetime` Pair

This name/value pair must be an ISO-8601 string, as defined by [RFC 3339](https://www.ietf.org/rfc/rfc3339.txt),
where the only allowed `time-offset` is `Z`, indicating the UTC/Zulu timezone.
The ABNF description is:

```abnf
   date-fullyear   = 4DIGIT
   date-month      = 2DIGIT  ; 01-12
   date-mday       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based on
                             ; month/year
   time-hour       = 2DIGIT  ; 00-23
   time-minute     = 2DIGIT  ; 00-59
   time-second     = 2DIGIT  ; 00-58, 00-59, 00-60 based on leap second
                             ; rules
   time-secfrac    = "." 1*DIGIT
   time-offset     = "Z"

   partial-time    = time-hour ":" time-minute ":" time-second [time-secfrac]
   full-date       = date-fullyear "-" date-month "-" date-mday
   full-time       = partial-time time-offset

   date-time       = full-date "T" full-time
```

Thus, timestamps take the form of `YYYY-MM-DDTHH:MM:SS.SSSZ`, where any number
of digits for fractional seconds is permitted.

#### Annotations Array

The `annotations` value is an array of _annotation segment objects_ that
describe anything regarding the signal data not part of the `captures` and
`global` objects. It MUST be sorted by the value of each annotation segment's
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
|`sample_count`|false|uint|The number of samples that this segment applies to. |
|`generator`|false|string|Human-readable name of the entity that created this annotation.|
|`label`|false|string|A short form human/machine-readable label for the annotation.|
|`comment`|false|string|A human-readable comment.|
|`freq_lower_edge`|false|double|The frequency (Hz) of the lower edge of the feature described by this annotation.|
|`freq_upper_edge`|false|double|The frequency (Hz) of the upper edge of the feature described by this annotation.|
|`latitude`|false||The latitude corresponding to the annotation (deprecated, use `core:geolocation`).|
|`longitude`|false||The longitude corresponding to the annotation (deprecated, use `core:geolocation`).|

There is no limit to the number of annotations that can apply to the same group
of samples. If two annotations have the same `sample_start`, there is no
defined ordering between them. If `sample_count` is not provided, it should
be assumed that the annotation applies from `sample_start` through the end of
the dataset, in all other cases `sample_count` should be provided.

The `freq_lower_edge` and `freq_upper_edge` fields should be at RF if the
feature is at a known RF frequency. If there is no known center frequency (as
defined by the `frequency` field in the relevant `capture segment object`), or
the center frequency is at baseband, the `freq_lower_edge` and `freq_upper_edge`
fields may be relative to baseband. It is required that both `freq_lower_edge`
and `freq_upper_edge` be provided, or neither; the use of just one field is not
allowed.

The `label` field may be used for any purpose, but it is recommended that it be
limited to no more than 20 characters because a common use is a short form GUI
indicator. Similarly, any user interface making use of this field should be
capable of displaying up to 20 characters.

### Collection Format

The `sigmf-collection` file contains JSON-formatted metadata adhering to the SigMF schema, with one top-level object called a `collection`. The `collection` object contains name/value pairs that describe relationships between SigMF Recordings.

The `collection` object points to specific recordings via a _SigMF Recording tuple_, which references the base-name of the recording and the SHA512 hash of the metadata file. Tuples may be the singular value in a key/value pair, or provided in an ordered list via a JSON array.

1. The `collection` object MUST be the only top-level object in the file.
2. It is RECOMMENDED that the `collection` file use hyphens to separate words rather than whitespace or underscores.
3. The `collection` object MUST only contain SigMF key/value pairs.
4. Keys in the `collection` object MUST use SigMF Recording Tuples to reference recordings.
5. SigMF Recording tuples MUST take the form of `["N", "hash"]`, where `N` is the base-name of a SigMF Recording and `hash` is the SHA512 hash of the Recording's metadata file `N.sigmf-meta`.
6. If a value contains multiple SigMF Recording tuples, they MUST appear in a JSON array.  
7. The `sigmf-collection` file MUST be EITHER in the same directory as the Recordings that it references, or in the top-level directory of an Archive.

The following names are specified in the `core` namespace for use in the `collection` object.

|name|required|type|description|
|----|--------------|-------|-----------|
|`version`|true|string|The version of the SigMF specification used to create the metadata file.|
|`description`|false|string|A text description of the SigMF collection.|
|`author`|false|string|The author's name (and optionally e-mail address) of the form "Bruce Wayne <wayne@example.com>".|
|`collection_doi`|false|string|The registered DOI (ISO 26324) for a Collection.|
|`license`|false|string|A URL for the license document under which this Collection metadata is offered; when possible, use the canonical document provided by the license author, or, failing that, a well-known one.|
|`hagl`|false|SigMF Recording Tuple|Antenna height above ground level (in meters).|
|`extensions`|false|array|A list of objects describing extensions used by this recording.|
|`streams`|false|array|An ordered array of SigMF Recording Tuples, indicating multiple recorded streams of data (e.g., phased array collections).|

Example `top-level.sigmf-collection` file:
```JSON
{
    "collection": {
       "core:version": "v1.0.0",

        "core:extensions" : [
            {
            "name": "antenna",
            "version": "1.0.0",
            "optional": false
            }
         ],

        "core:hagl": ["hagl-basename", "hash"],

        "antenna:azimuth_angle": ["azimuth-angle-basename", "hash"],

        "core:streams": [
            ["example-channel-0-basename", "hash"],
            ["example-channel-1-basename", "hash"]
        ]
    }
}
```

### Licensing

You may specify any license of your choosing. Recommended licenses for SigMF
Recordings and Collections are:

* [CC0 1.0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/)
* [CC-BY Attribution 2.0 Generic](https://creativecommons.org/licenses/by/2.0/)

### SigMF Compliance by Applications

In order to be `SigMF Compliant`, an application must meet the following
requirements:

1. Adheres to and supports the file rules, dataset formats, `objects`,
   `namespaces`, and `names` specified by this document.
2. Must be able to ignore any `object` or `namespace` not specified by this
   document and still function normally.
3. Capture segments referring to non-existent samples should be ignored.
4. Must treat consecutive capture segments whose metadata is equivalent for
   purposes of that application (i.e., it may be different in values ignored by
   the application such as optional values or unknown extensions) as it would
   a single segment.
5. Supports all fields in the `core` namespace.

## Examples

#### Example of the `global` `core:offset` field usage:

This is an example metadata file for the second of a series of files split into
5M sample chunks.

```json
{
  "global": {
    "core:datatype": "ci16_le",
    "core:sample_rate": 25000000.0,
    "core:offset": 5000000,
    "core:version": "1.0.0"
  },
  "captures": [{
    "core:frequency": 100000000.0,
    "core:sample_start": 5000000
  }],
  "annotations": [{
    "core:sample_start": 5000000,
    "core:sample_count": 5000000,
    "core:freq_lower_edge": 100190000.0,
    "core:freq_upper_edge": 100410000.0,
  }]
}
```

## Citing SigMF

To cite the SigMF specification, we recommend the following format:

    The Signal Metadata Format (SigMF), <release>, <date of release>, https://sigmf.org

## Acknowledgements

This specification originated at the DARPA Brussels Hackfest 2017.
