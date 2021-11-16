# Signal Metadata Format Specification v1.0.0

## Abstract

The Signal Metadata Format (SigMF) specifies a way to describe sets of recorded
digital signal samples with metadata written in JSON. SigMF can be used to
describe general information about a collection of samples, the characteristics
of the system that generated the samples, features of signals themselves, and the
relationship between different recordings.

## Copyright Notice

This document is available under the [CC-BY-SA License](http://creativecommons.org/licenses/by-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

Copyright of contributions to SigMF are retained by their original authors. All contributions under these terms are welcome.

## Table of Contents

**Table of Contents**

- [Signal Metadata Format Specification v1.0.0](#signal-metadata-format-specification-v100)
  - [Abstract](#abstract)
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

Specific keywords with semantic meaning in the context of this specification 
are capitalized after being introduced (e.g., Recording).

## Specification

The SigMF specification fundamentally describes two types of information:
datasets, and metadata associated with those datasets. Taken together, a dataset
with its SigMF metadata is a SigMF `Recording`.

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

This specification defines a schema for metadata using a `core` namespace that 
is a reserved name and can only be defined by this specification. Other metadata
may be described by extension namespaces. This specification also defines a 
model and format for how SigMF data should be stored at-rest (on-disk) using JSON.

### Files

There are two fundamental filetypes defined by this specification: files with 
metadata, and the files that contain the datasets described by the metadata. There
are two types of files containining metadata, a SigMF `Metadata` file, and a SigMF
`Collection` file. There are also two types of datasets, a SigMF `Dataset` file, 
and a `Non-Conforming Dataset` file, abbreviated as `NCD`.

The primary unit of SigMF is a SigMF `Recording`, which comprises a Metadata file
and the dataset file it describes. Collections are an optional feature that are 
used to describe the relationships between multiple Recordings. 

Collections and multiple Recordings can be packaged for easy storage and 
distribution in a SigMF `Archive`.

             ┌────────────────────┐
             │                    │
             │  SigMF Collection  │
             │                    ├──┐
             │   (optional file)  │  │
             └──────────┬─────────┘  │
                        │            │            ┌─────────────────────┐
                        │            │  stored in │                     │
                        │ links      ├────────────►    SigMF Archive    │
                        │            │            │                     │
                        │            │            │   (optional file)   │
              ┌─────────▼─────────┐  │            └─────────────────────┘
              │                   │  │
              │  SigMF Recording  ├──┘
              │                   │
              └─────────┬─────────┘
                        │
                        │ comprises
                        │
          ┌─────────────┴──────────────┐
          │                            │
 ┌────────▼───────┐                    │
 │                │               ┌────▼────┐
 │ SigMF Metadata ├───────────────► dataset │
 │                │   describes   └────┬────┘
 │     (file)     │                    │
 └────────────────┘                    │
                             ┌─────────┴────────────┐
                             │     is either        │
                             │                      │
                    ┌────────▼────────┐    ┌────────▼─────────┐
                    │                 │    │                  │
                    │  SigMF Dataset  │    │  Non-Conforming  │
                    │                 │    │     Dataset      │
                    │      (file)     │    │                  │
                    └─────────────────┘    │      (file)      │
                                           └──────────────────┘


Rules for all files:
1. All filetypes MUST be stored in separate files on-disk.
1. It is RECOMMENDED that filenames use hyphens to separate 
   words rather than whitespace or underscores.

Rules for SigMF Metadata files:
1. A Metadata file MUST only describe one dataset file.
1. A Metadata file MUST be stored in UTF-8 encoding.
1. A Metadata file MUST have a `.sigmf-meta` filename extension.
1. A Metadata file MUST be in the same directory as the dataset file
   it describes.
1. It is RECOMMENDED that the base filenames (not including file extension) of 
   a Recording's Metadata and dataset files be identical.

Rules for SigMF Dataset files:
1. The Dataset file MUST have a `.sigmf-data` filename extension.

Rules for SigMF Non-Conforming Dataset files:
1. The NCD file MUST NOT have a `.sigmf-data` filename extension.

Rules for SigMF Collection files:
1. The Collection file MUST be stored in UTF-8 encoding.
1. The Collection file MUST have a `.sigmf-collection` filename extension.
1. The `sigmf-collection` file MUST be EITHER in the same directory as the 
   Recordings that it references, or in the top-level directory of an Archive 
   (described in later section).

Rules for SigMF Archive files:
1. The Archive MUST use the `tar` archive format, as specified by POSIX.1-2001.
1. The Archive file's filename extension MUST be `.sigmf`.
1. The Archive MUST contain the following files: for each contained Recording
   with some name given here meta-syntactically as `N`, files named `N` (a
   directory), `N/N.sigmf-meta`, and `N/N.sigmf-data`.
1. The Archive MAY contain a `.sigmf-collection` file at the top-level directory.
1. It is RECOMMENDED that if Recordings in an archive represent continuous
   data that has been split into separate Recordings, that their filenames
   reflect the order of the series by appending a hyphenated zero-based index
   (e.g., `N-0`, `N-1`, `N-2`, etc.,).

### SigMF Dataset Format

There are four orthogonal characteristics of sample data: complex or real, 
floating-point or integer, bit-width, and endianness. The following ABNF 
rules specify the dataset formats defined in the Core namespace. Additional
dataset formats may be added through extensions.

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

So, for example, the string `"cf32_le"` specifies "complex 32-bit floating-point
samples stored in little-endian", the string `"ru16_be"` specifies "real
unsigned 16-bit samples stored in big-endian", and the string `"cu8"` specifies
"complex unsigned byte".

Note that only IEEE-754 single-precision floating-point is supported by the
SigMF Core namespace.

The samples should be written to the Dataset file without separation, and the
Dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, EOF characters).

Complex samples should be interleaved, with the in-phase component first (i.e.,
`I[0]` `Q[0]` `I[1]` `Q[1]` ... `I[n]` `Q[n]`). When `core:num_channels` in the
Global object (described below) indicates that the Recording contains more than one channel,
samples from those channels should be interleaved in the same manner, with
the same index from each channel's sample serially in the recording. For
example, a Recording with two channels of `ri16_le` representing real-valued
audio data from a stereo recording and here labeled `L` for left and `R` for
right, the data should appear as `L[0]` `R[0]` `L[1]` `R[1]` ... `L[n]` `R[n]`.
The data type specified by `core:data_type` applies to all channels of data
both real and imaginary parts.

### SigMF Metadata Format

SigMF metadata fundamentally takes the form of key/value pairs:

```JSON
"namespace:name": value,
```

When stored on-disk (at-rest), these rules apply:
1. The Metadata file MUST be written in [JSON](http://www.json.org/), as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).
1. The entire contents of the Metadata file MUST be contained within a single
   top-level JSON Object.
2. The top-level Object MUST contain three JSON Objects named `global`, `captures`,
   and `annotations`.
1. Metadata key/value pairs SHALL NOT be assumed to have carried over between
   capture or annotation segments. If a name/value pair applies to a particular
   segment, then it must appear in that segment, even if the value is unchanged
   relative to the previous segment.

All SigMF metadata is defined using the structural concepts of JSON, and when 
stored on-disk, metadata MUST be proper JSON to be SigMF compliant.

#### Datatypes

The values in each key/value pair must be one of the following datatypes.

| type    | long-form name                         | description                                                   |
| ------- | -------------------------------------- | ------------------------------------------------------------- |
| int     | integer                                | Signed 64-bit integer.                                        |
| uint    | unsigned long                          | Unsigned 64-bit integer.                                      |
| double  | double-precision floating-point number | A 64-bit float as defined by IEEE 754.                        |
| string  | string                                 | A string of characters, as defined by the JSON standard.      |
| boolean | boolean                                | Either `true` or `false`, as defined by the JSON standard.    |
| null    | null                                   | `null`, as defined by the JSON standard.                      |
| array   | JSON `array`                           | An `array` of other values, as defined by the JSON standard.  |
| object  | JSON `object`                          | An `object` of other values, as defined by the JSON standard. |
| GeoJSON | GeoJSON `point` object                 | A single GeoJSON `point` object as defined by RFC 7946.       |

#### Namespaces

Namespaces provide a way to further classify key/value pairs in metadata.
This specification defines the `core` namespace. Only this specification
may add fields to the Core namespace.

The goal of the Core namespace is to capture the foundational metadata 
necessary to work with SigMF data. Some keys within the Core namespace 
are optional, and others are required. The fields that are required are those 
that are minimally necessary to parse and process the Dataset, or that have 
obvious defaults that are valid. Other fields are 'optional', even if they 
are highly encouraged.

##### Extension Namespaces

Fields not defined in the Core namespace may be defined in extension
namespaces. The SigMF specification defines some extension namespaces to
provide canonical definitions for commonly needed metadata fields that do not
belong in Core. These canonical extension namespaces can be found in the
`extensions/` directory of the official SigMF repository. Other extension
namespaces may be defined by the user as needed.

1. An extension namespace MUST be defined in a single file, named
   meta-syntactically as `N.sigmf-ext.md`, where `N` is the name of the extension.
1. A `N.sigmf-ext.md` file MUST be a Github-Flavored Markdown file stored in UTF-8
   encoding.
1. Extensions MUST have version numbers. It is RECOMMENDED that extensions use
   [Semantic Versioning](https://semver.org/).
1. An extension namespace MAY define new top-level SigMF Objects, key/value
   pairs, new files, new dataset formats, or new datatypes.
1. New key/value pairs defined by an extension namespace MUST be defined in
   the context of a specific SigMF top-level object - i.e., `global`,
   `captures`, `annotations`, or a new user-defined object.
1. It is RECOMMENDED that an extension namespace file follow the structure of
   the canonical extension namespaces.

#### Global Object

The `global` object consists of key/value pairs that provide information
applicable to the entire Dataset. It contains the information that is minimally
necessary to open and parse the Dataset file, as well as general information
about the Recording itself.

The following names are specified in the Core namespace and should be used in
the Global object:

| name           | required | type    | description      |
| -------------- | -------- | --------| -----------------|
| `datatype`     | true     | string  | The SigMF Dataset format of the stored samples in the dataset file.|
| `sample_rate`  | false    | double  | The sample rate of the signal in samples per second.|
| `version`      | true     | string  | The version of the SigMF specification used to create the Metadata file.|
| `num_channels` | false    | uint    | Total number of interleaved channels in the dataset file. If omitted, this defaults to one.|
| `sha512`       | false    | string  | The SHA512 hash of the Dataset file associated with the SigMF file.|
| `offset`       | false    | uint    | The index number of the first sample in the Dataset. If not provided, this value defaults to zero. Typically used when a Recording is split over multiple files. All sample indices in SigMF are absolute, and so all other indices referenced in metadata for this recording should be greater than or equal to this value.|
| `description`  | false    | string  | A text description of the SigMF Recording.|
| `author`       | false    | string  | The author's name (and optionally e-mail address) of the form "Bruce Wayne <wayne@example.com>".|
| `meta_doi`     | false    | string  | The registered DOI (ISO 26324) for a Recording's Metadata file.|
| `data_doi`     | false    | string  | The registered DOI (ISO 26324) for a Recording's Dataset file.|
| `recorder`     | false    | string  | The name of the software used to make this SigMF Recording.|
| `license`      | false    | string  | A URL for the license document under which the Recording is offered.|
| `hw`           | false    | string  | A text description of the hardware used to make the Recording.|
| `dataset`      | false    | string  | The full filename of the dataset file this Metadata file describes.|
| `trailing_bytes` | false | uint | The number of bytes to ignore at the end of a Non-Conforming Dataset file.|
| `geolocation`  | false    | GeoJSON `point` object | The location of the Recording system.|
| `extensions`   | false    | array   | A list of JSON Objects describing extensions used by this Recording.|
| `collection`   | false    | string  | The base filename of a `collection` with which this Recording is associated.|

##### The `dataset` Field
The `core:dataset` field in the Global Object is used to specify the dataset file that
this Metadata describes. If provided, this string MUST BE the complete filename of the
dataset file, including the extension. The dataset file must be in the local directory,
and this string MUST NOT include any aspects of filepath other than the filename.

If this field is omitted, the dataset file MUST BE a SigMF Dataset file (NOT a
Non-Conforming Dataset), and MUST have the same base filename as the Metadata file and
use the `.sigmf-data` extension.

##### The `trailing_bytes` Field
This field is used with Non-Conforming Datasets to indicate some number of bytes that
trail the sample data in the NCD file that should be ignored for processing. This can
be used to ignore footer data in non-SigMF filetypes.

##### The `geolocation` Field
The `core:geolocation` field in the Global Object is used to store the
location of the recording system. The location is stored as a single
[RFC 7946](https://www.rfc-editor.org/rfc/rfc7946.txt) GeoJSON `point` object
using the convention defined by [RFC 5870](https://www.rfc-editor.org/rfc/rfc5870.txt).
Per the GeoJSON specification, the point coordinates use the WGS84 coordinate
reference system and are `longitude`, `latitude` (required, in decimal degrees),
and `altitude` (optional, in meters above the WGS84 ellipsoid) - in that order. An
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

GeoJSON permits the use of *Foreign Members* in GeoJSON documents per RFC 7946
Section 6.1. Because the SigMF requirement for the `geolocation` field is to be
a valid GeoJSON `point` object, users MAY include *Foreign Member* fields here
for user-defined purposes (position valid indication, GNSS SV counts, dillution
of precision, accuracy, etc). It is strongly RECOMMENDED that all fields be
documented in a SigMF Extension document.

*Note:* Objects named `geometry` or `properties` are **not** permitted Foreign
Members, as specified in RFC 7946 Section 7.1.

##### The `extensions` Field

The `core:extensions` field in the Global Object is an array of `extension objects`
that describe SigMF extensions. Extension Objects MUST contain the three key/value 
pairs defined below, and MUST NOT contain any other fields.

| name       | required | type    | description                                                                 |
| ---------- | -------- | ------- | --------------------------------------------------------------------------- |
| `name`     | true     | string  | The name of the SigMF extension namespace.                                  |
| `version`  | true     | string  | The version of the extension namespace specification used.                  |
| `optional` | true     | boolean | If this field is `true`, the extension is required to parse this recording. |

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
This field is used to indicate that this Recording is part of a SigMF Collection 
(described later in this document). It is RECOMMENDED that if you are 
building a Collection, that each Recording referenced by that Collection use this 
field to associate up to the relevant `sigmf-collection` file.

#### Captures Array

The `captures` value is an array of `capture segment objects` that describe how to
understand the samples from a signal capture and map them into digital memory. 
It MUST be sorted by the value of each capture segment's `core:sample_start` key, 
ascending.

#### Capture Segment Objects

Capture Segment Objects are composed of key/value pairs, and each Segment describes
a chunk of samples that can be mapped into memory for processing. Each Segment
must contain a `core:sample_start` key/value pair, which indicates the sample index
relative to the dataset where this Segment's metadata applies. The fields that are 
described within a Capture Segment are scoped to that Segment only and must be 
declared again if they are valid in subsequent Segments.

The following names are specified in the Core namespace and should be used in
Capture Segment Objects:

| name            | required | type   | description                                                                                 |
| ----------------| -------- | ------ | --------------------------------------------------------------------------------------------|
| `sample_start`  | true     | uint   | The sample index in the dataset file at which this Segment takes effect.                    |
| `global_index`  | false    | uint   | The index of the sample referenced by `sample_start` relative to an original sample stream. |
| `header_bytes`  | false    | uint   | The number of bytes preceeding a chunk of samples that should be ignored, used for NCDs.    |
| `frequency`     | false    | double | The center frequency of the signal in Hz.                                                   |
| `datetime`      | false    | string | An ISO-8601 string indicating the timestamp of the sample index specified by `sample_start`.|

##### The `sample_start` Field

This field specifies the sample index where this Segment takes effect relative
to the recorded dataset file. If the dataset is a SigMF Dataset file, this 
field can be immediately mapped to physical disk location since conforming
Datasets only contain sample data.

##### The `global_index` Field

This field describes the index of the sample referenced by the `sample_start`
field relative to an original sample stream, the entirety of which may not
have been captured in a recorded dataset. If ommitted, this value SHOULD
be treated as equal to `sample_start`.

For example, some hardware devices are capable of 'counting' samples at
the point of data conversion. This sample count is commonly used to indicate 
a discontinuity in the datastream between the hardware device and processing.

For example, in the below Captures array, there are two Segments describing
samples in a SigMF Dataset file. The first Segment begins at the start of the 
Dataset file. The second segment begins at sample index 500 relative to the
recorded samples (and since this is a conforming SigMF Dataset, is physically
located on-disk at location `sample_start * sizeof(sample)`), but the 
`global_index` reports this was actually sample number 1000 in the original
datastream, indicating that 500 samples were lost before they could be recorded.

```json
   ...
   "captures": [
      {
         "core:sample_start": 0,
         "core:global_index": 0
      },
      {
         "core:sample_start": 500,
         "core:global_index": 1000
      }
   ],
   ...
```

##### The `header_bytes` Field

This field specifies a number of bytes that are not valid sample data that 
are physically located at the start of where the chunk of samples referenced 
by this Segment would otherwise begin. If omitted, this value SHOULD
be treated as equal zero. If included, the Dataset is by definition a
Non-Conforming Dataset.

For example, the below Metadata for a Non-Conforming Dataset contains
two segments describing chunks of 8-bit complex samples (2 bytes per sample) 
recorded to disk with 4-byte headers that are not valid for 
processing. Thus, to map these two chunks of samples into memory, a reader
application would map the `500 samples` (equal to `1000 bytes`) in the first 
Segment, starting at a file offset of `4 bytes`, and then the remainder of the 
file through EOF starting at a file offset of `1008 bytes` (equal to the size 
of the previous Segment of samples plus two headers).

```json
{
   "global": {
      "core:datatype": "cu8",
      "core:version": "1.0.0",
      "core:dataset": "non-conforming-dataset-01.dat"
   },
   "captures": [
      {
         "core:sample_start": 0,
         "core:header_bytes": 4,
      },
      {
         "core:sample_start": 500,
         "core:header_bytes": 4,
      }
   ],
   "annotations": []
}
```

##### The `datetime` Field

This key/value pair must be an ISO-8601 string, as defined by 
[RFC 3339](https://www.ietf.org/rfc/rfc3339.txt), where the only allowed 
`time-offset` is `Z`, indicating the UTC/Zulu timezone. The ABNF description is:

```abnf
   date-fullyear   = 4DIGIT
   date-month      = 2DIGIT  ; 01-12
   date-mday       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based on month/year
                             
   time-hour       = 2DIGIT  ; 00-23
   time-minute     = 2DIGIT  ; 00-59
   time-second     = 2DIGIT  ; 00-58, 00-59, 00-60 based on leap second rules
                            
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

The `annotations` value is an array of `annotation segment objects` that
describe anything regarding the signal data not part of the Captures and
Global objects. It MUST be sorted by the value of each Annotation Segment's
`core:sample_start` key, ascending.

##### Annotation Segment Objects

Annotation segment objects contain key/value pairs and MUST contain a 
`core:sample_start` key/value pair, which indicates the first index 
at which the rest of the Segment's key/value pairs apply.

The following names are specified in the Core namespace and should be used in
Annotation Segment Objects:

| name              | required | type   | description                                                                         |
| ----------------- | -------- | ------ | ----------------------------------------------------------------------------------- |
| `sample_start`    | true     | uint   | The sample index at which this Segment takes effect.                                |
| `sample_count`    | false    | uint   | The number of samples that this Segment applies to.                                 |
| `generator`       | false    | string | Human-readable name of the entity that created this annotation.                     |
| `label`           | false    | string | A short form human/machine-readable label for the annotation.                       |
| `comment`         | false    | string | A human-readable comment.                                                           |
| `freq_lower_edge` | false    | double | The frequency (Hz) of the lower edge of the feature described by this annotation.   |
| `freq_upper_edge` | false    | double | The frequency (Hz) of the upper edge of the feature described by this annotation.   |
| `latitude`        | false    |        | The latitude corresponding to the annotation (DEPRECATED, use `core:geolocation`).  |
| `longitude`       | false    |        | The longitude corresponding to the annotation (DEPRECATED, use `core:geolocation`). |

There is no limit to the number of annotations that can apply to the same group
of samples. If two annotations have the same `sample_start`, there is no
defined ordering between them. If `sample_count` is not provided, it should
be assumed that the annotation applies from `sample_start` through the end of
the dataset, in all other cases `sample_count` should be provided.

The `freq_lower_edge` and `freq_upper_edge` fields should be at RF if the
feature is at a known RF frequency. If there is no known center frequency (as
defined by the `frequency` field in the relevant Capture Segment Object), or
the center frequency is at baseband, the `freq_lower_edge` and `freq_upper_edge`
fields may be relative to baseband. It is REQUIRED that both `freq_lower_edge`
and `freq_upper_edge` be provided, or neither; the use of just one field is not
allowed.

The `label` field may be used for any purpose, but it is RECOMMENDED that it be
limited to no more than 20 characters as a common use is a short form GUI
indicator. Similarly, it is RECOMMENDED that any user interface making use of 
this field be capable of displaying up to 20 characters.

### Collection Format

The `sigmf-collection` file contains metadata in a single top-level object 
called a `collection`. The Collection Object contains key/value pairs that 
describe relationships between SigMF Recordings.

The Collection object points to specific recordings via a `SigMF Recording tuple`,
which references the base-name of the Recording and the SHA512 hash of the 
Metadata file. Tuples may be the singular value in a key/value pair, or provided
in an ordered list via a JSON array.

1. The Collection Object MUST be the only top-level object in the file.
1. The Collection Object MUST only contain SigMF key/value pairs.
1. Keys in the Collection Object MUST use SigMF Recording Tuples to reference 
   Recordings.
1. SigMF Recording Tuples MUST take the form of `["N", "hash"]`, where `N` is the 
   base-name of a SigMF Recording and `hash` is the SHA512 hash of the Recording's 
   Metadata file `N.sigmf-meta`.
1. If a value contains multiple SigMF Recording Tuples, they MUST appear in a JSON array.  

The following names are specified in the `core` namespace for use in the `collection` object.

| name             | required | type                  | description |
| -----------------| ---------| ----------------------| ------------|
| `version`        | true     | string                | The version of the SigMF specification used to create the Collection file.|
| `description`    | false    | string                | A text description of the SigMF Collection.|
| `author`         | false    | string                | The author's name (and optionally e-mail address) of the form "Bruce Wayne <wayne@example.com>".|
| `collection_doi` | false    | string                | The registered DOI (ISO 26324) for a Collection.|
| `license`        | false    | string                | A URL for the license document under which this Collection metadata is offered.|
| `extensions`     | false    | array                 | A list of objects describing extensions used by this Collection.|
| `streams`        | false    | array                 | An ordered array of SigMF Recording Tuples, indicating multiple recorded streams of data (e.g., phased array collections).|

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

        "antenna:hagl": ["hagl-basename", "hash"],

        "antenna:azimuth_angle": ["azimuth-angle-basename", "hash"],

        "core:streams": [
            ["example-channel-0-basename", "hash"],
            ["example-channel-1-basename", "hash"]
        ]
    }
}
```

## Licensing

Open licenses are recommended but you can specify any license. You can refer to 
resources provided by the [Open Data Commons](https://opendatacommons.org/) when 
deciding which open license fits your needs best. Cornell University has also 
created [a guide](https://data.research.cornell.edu/content/intellectual-property#data-licensing) 
to help you make these choices.

## SigMF Compliance by Applications

In order to be `SigMF Compliant`, an application must meet the following
requirements:

1. Adheres to and supports the file rules, dataset formats, `objects`,
   `namespaces`, and `names` specified by this document.
2. Must be able to ignore any `object` or `namespace` not specified by this
   document and still function normally.
3. Capture Segments referring to non-existent samples should be ignored.
4. Must treat consecutive Capture Segments whose metadata is equivalent for
   purposes of that application (i.e., it may be different in values ignored by
   the application such as optional values or unknown extensions) as it would
   a single segment.
5. Supports all fields in the `core` namespace.

## Citing SigMF

To cite the SigMF specification, we recommend the following format:

```txt
The Signal Metadata Format (SigMF), <release>, <date of release>, https://sigmf.org
```

## Acknowledgements

This specification originated at the DARPA Brussels Hackfest 2017.
