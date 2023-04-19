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
    - [SigMF File Types](#sigmf-file-types)
    - [SigMF Dataset Format](#sigmf-dataset-format)
    - [SigMF Metadata Format](#sigmf-metadata-format)
      - [Datatypes](#datatypes)
      - [Namespaces](#namespaces)
        - [Extension Namespaces](#extension-namespaces)
      - [Global Object](#global-object)
      - [Captures Array](#captures-array)
        - [Capture Segment Objects](#capture-segment-objects)
      - [Annotations Array](#annotations-array)
        - [Annotation Segment Objects](#annotation-segment-objects)
    - [SigMF Collection Format](#sigmf-collection-format)
      - [SigMF Recording Objects](#sigmf-recording-objects)
  - [Licensing](#licensing)
  - [SigMF Compliance](#sigmf-compliance)
    - [SigMF Schema Compliance](#sigmf-schema-compliance)
    - [SigMF Recording Compliance](#sigmf-recording-compliance)
    - [SigMF Collection Compliance](#sigmf-collection-compliance)
    - [SigMF Application Compliance](#sigmf-application-compliance)
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

Fields defined as "human-readable", a "string", or simply as "text" SHALL be
treated as plaintext where whitespace is significant, unless otherwise
specified. Fields defined "human/machine-readable" SHOULD be short, simple
text strings without whitespace that are easily understood by a human and
readily parsed by software.

Specific keywords with semantic meaning in the context of this specification 
are capitalized after being introduced (e.g., Recording).

## Specification

The SigMF specification fundamentally describes two types of information:
datasets, and metadata associated with those datasets. Taken together, a Dataset
with its SigMF metadata is a SigMF `Recording`.

Datasets, for purposes of this specification, are sets of digital measurements
generically called `samples` in this document. The samples can represent any
time-varying source of information. They MAY, for example, be digital samples
created by digital synthesis or by an Analog-to-Digital Converter. They could
also be geolocation coordinates from a GNSS receiver, temperature readings
from a thermal sensor, or any other stored digital measurement information.

Metadata describes the Dataset with which it is associated. The metadata
includes information meant for the human users of the Dataset, such as a title
and description, and information meant for computer applications (tools) that
operate on the Dataset.

This specification defines a schema for metadata using a `core` namespace that 
is a reserved name and can only be defined by this specification. Other metadata
MAY be described by extension namespaces. This specification also defines a 
model and format for how SigMF data should be stored at-rest (on-disk) using JSON.

### SigMF File Types

There are two fundamental filetypes defined by this specification: files with 
metadata, and the files that contain the Datasets described by the metadata. There
are two types of files containing metadata, a SigMF `Metadata` file, and a SigMF
`Collection` file. There are also two types of Datasets, a SigMF `Dataset` file, 
and a `Non-Conforming Dataset` file, abbreviated as `NCD`.

The primary unit of SigMF is a SigMF `Recording`, which comprises a Metadata file
and the Dataset file it describes. Collections are an optional feature that are 
used to describe the relationships between multiple Recordings. 

Collections and multiple Recordings can be packaged for easy storage and 
distribution in a SigMF `Archive`.

```
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
                 ╔══════════▼══════════╗ │            └─────────────────────┘
                 ║                     ║ │
                 ║   SigMF Recording   ╟─┘
                 ║                     ║
                 ║ (base SigMF Object) ║
                 ╚══════════╤══════════╝
                            │
                            │ comprises
                            │
              ┌─────────────┴──────────────┐
              │                            │
     ┌────────▼───────┐                    │
     │                │               ┌────▼────┐
     │ SigMF Metadata ├───────────────► Dataset │
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
```

Rules for all files:
1. All filetypes MUST be stored in separate files on-disk.
1. It is RECOMMENDED that filenames use hyphens to separate words rather than
   whitespace or underscores.

Rules for SigMF Metadata files:
1. A Metadata file MUST only describe one Dataset file.
1. A Metadata file MUST be stored in UTF-8 encoding.
1. A Metadata file MUST have a `.sigmf-meta` filename extension.
1. A Metadata file MUST be in the same directory as the Dataset file it
   describes.
1. It is RECOMMENDED that the base filenames (not including file extension) of
   a Recording's Metadata and Dataset files be identical.

Rules for SigMF Dataset files:
1. The Dataset file MUST have a `.sigmf-data` filename extension.

Rules for SigMF Non-Conforming Dataset files:
1. The NCD file MUST NOT have a `.sigmf-data` filename extension.

Rules for SigMF Collection files:
1. The Collection file MUST be stored in UTF-8 encoding.
1. The Collection file MUST have a `.sigmf-collection` filename extension.
1. The `sigmf-collection` file MUST be either in the same directory as the
   Recordings that it references, or in the top-level directory of an Archive
   (described in later section).

Rules for SigMF Archive files:
1. The Archive MUST use the `tar` archive format, as specified by POSIX.1-2001.
1. The Archive file's filename extension MUST be `.sigmf`.
1. The Archive MUST contain at least one SigMF Recording.
1. The Archive MAY contain one `.sigmf-collection` file in the top-level
   directory.
1. SigMF Archives MAY contain additional files (not specified by SigMF), and
   arbitrary directory structures, but the SigMF files within the Archive MUST
   adhere to all rules above when the archive is extracted.

### SigMF Dataset Format

There are four orthogonal characteristics of sample data: complex or real, 
floating-point or integer, bit-width, and endianness. The following ABNF 
rules specify the Dataset formats defined in the Core namespace. Additional
Dataset formats MAY be added through extensions.

```abnf
    dataset-format = (real / complex) ((type endianness) / byte)

    real = "r"
    complex = "c"

    type = floating-point / signed-integer / unsigned-integer
    floating-point = "f32" / "f64"
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

Only IEEE-754 single-precision and double-precision floating-point types are
supported by the SigMF Core namespace. Note that complex data types are
specified by the bit width of the individual I/Q components, and not by the
total complex pair bitwidth (like Numpy).

The samples SHOULD be written to the Dataset file without separation, and the
Dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, EOF characters).

Complex samples MUST be interleaved, with the in-phase component first (i.e.,
`I[0]` `Q[0]` `I[1]` `Q[1]` ... `I[n]` `Q[n]`). When `core:num_channels` in the
Global Object (described below) indicates that the Recording contains more than one channel,
samples from those channels MUST be interleaved in the same manner, with
the same index from each channel's sample serially in the Recording. For
example, a Recording with two channels of `ri16_le` representing real-valued
audio data from a stereo Recording and here labeled `L` for left and `R` for
right, the data MUST appear as `L[0]` `R[0]` `L[1]` `R[1]` ... `L[n]` `R[n]`.
The data type specified by `core:data_type` applies to all channels of data
both real and imaginary parts.

### SigMF Metadata Format

SigMF metadata fundamentally takes the form of key/value pairs:

```JSON
"namespace:name": value,
```

Metadata field names in the top level `global` Object, `captures` segment
Objects, or `annotations` Objects MUST be of this form. All fields other than
those at the top level which contain a `:` delimiter SHALL only use letters,
numbers, and the `_` character; all other characters are forbidden. Field names
MUST NOT start with a number and MUST NOT not be C++20 or Python 3.10 keywords.

When stored on-disk (at-rest), these rules apply:
1. The Metadata file MUST be written in [JSON](http://www.json.org/), as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).
1. The entire contents of the Metadata file MUST be contained within a single
   top-level JSON Object.
1. The top-level Object MUST contain three JSON Objects named `global`, `captures`,
   and `annotations`.
1. Metadata key/value pairs SHALL NOT be assumed to have carried over between
   capture or annotation segments. If a name/value pair applies to a particular
   segment, then it MUST appear in that segment, even if the value is unchanged
   relative to the previous segment.

All SigMF metadata is defined using the structural concepts of JSON, and when 
stored on-disk, metadata MUST be proper JSON to be SigMF compliant.

#### Datatypes

The values in each key/value pair MUST be one of the following datatypes.

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
| GeoJSON | GeoJSON `point` Object                 | A single GeoJSON `point` Object as defined by RFC 7946.       |

#### Namespaces

Namespaces provide a way to further classify key/value pairs in metadata.
This specification defines the `core` namespace. Only this specification
can add fields to the Core namespace.

The goal of the Core namespace is to capture the foundational metadata 
necessary to work with SigMF data. Some keys within the Core namespace are
OPTIONAL, and others are REQUIRED. The REQUIRED fields are those that are
minimally necessary to parse and process the Dataset, or that have obvious
defaults that are valid. All other fields are OPTIONAL, though they can be
strongly RECOMMENDED.

##### Extension Namespaces

Fields not defined in the Core namespace MAY be defined in extension
namespaces. The SigMF specification defines some extension namespaces to
provide canonical definitions for commonly needed metadata fields that do not
belong in Core. These canonical extension namespaces can be found in the
`extensions/` directory of the official SigMF repository. Other extension
namespaces MAY be defined by the user as needed.

1. An extension namespace MUST be defined in a single file, named
   meta-syntactically as `N.sigmf-ext.md`, where `N` is the name of the extension.
1. A `N.sigmf-ext.md` file MUST be a Github-Flavored Markdown file stored in UTF-8
   encoding.
1. Extensions MUST have version numbers. It is RECOMMENDED that extensions use
   [Semantic Versioning](https://semver.org/).
1. An extension namespace MAY define new top-level SigMF Objects, key/value
   pairs, new files, new Dataset formats, or new datatypes.
1. New key/value pairs defined by an extension namespace MUST be defined in
   the context of a specific SigMF top-level Object - i.e., `global`,
   `captures`, `annotations`, or a new user-defined Object.
1. It is RECOMMENDED that an extension namespace file follow the structure of
   the canonical extension namespaces.

#### Global Object

The `global` Object consists of key/value pairs that provide information
applicable to the entire Dataset. It contains the information that is minimally
necessary to open and parse the Dataset file, as well as general information
about the Recording itself.

The following names are specified in the Core namespace for use in the Global
Object:

| name            | required | type    | description      |
| --------------- | -------- | --------| -----------------|
| `datatype`      | true     | string  | The SigMF Dataset format of the stored samples in the Dataset file.|
| `sample_rate`   | false    | double  | The sample rate of the signal in samples per second.|
| `version`       | true     | string  | The version of the SigMF specification used to create the Metadata file.|
| `num_channels`  | false    | uint    | Total number of interleaved channels in the Dataset file. If omitted, this defaults to one.|
| `sha512`        | false    | string  | The SHA512 hash of the Dataset file associated with the SigMF file.|
| `offset`        | false    | uint    | The index number of the first sample in the Dataset. If not provided, this value defaults to zero. Typically used when a Recording is split over multiple files. All sample indices in SigMF are absolute, and so all other indices referenced in metadata for this recording SHOULD be greater than or equal to this value.|
| `description`   | false    | string  | A text description of the SigMF Recording.|
| `author`        | false    | string  | A text identifier for the author potentially including name, handle, email, and/or other ID like Amateur Call Sign. For example "Bruce Wayne <bruce@waynetech.com>" or "Bruce (K3X)".|
| `meta_doi`      | false    | string  | The registered DOI (ISO 26324) for a Recording's Metadata file.|
| `data_doi`      | false    | string  | The registered DOI (ISO 26324) for a Recording's Dataset file.|
| `recorder`      | false    | string  | The name of the software used to make this SigMF Recording.|
| `license`       | false    | string  | A URL for the license document under which the Recording is offered.|
| `hw`            | false    | string  | A text description of the hardware used to make the Recording.|
| `dataset`       | false    | string  | The full filename of the Dataset file this Metadata file describes.|
| `trailing_bytes`| false    | uint    | The number of bytes to ignore at the end of a Non-Conforming Dataset file.|
| `metadata_only` | false    | bool    | Indicates the Metadata file is intentionally distributed without the Dataset.|
| `geolocation`   | false    | GeoJSON `point` Object | The location of the Recording system.  Using geolocation within Captures is preferred |
| `extensions`    | false    | array   | A list of JSON Objects describing extensions used by this Recording.|
| `collection`    | false    | string  | The base filename of a `collection` with which this Recording is associated.|

**The `dataset` Field**

The `core:dataset` field in the Global Object is used to specify the Dataset file that
this Metadata describes. If provided, this string MUST be the complete filename of the
Dataset file, including the extension. The Dataset file must be in the local directory,
and this string MUST NOT include any aspects of filepath other than the filename.

If a Recording does not have this field, it MUST have a compliant SigMF Dataset (NOT
a Non-Conforming Dataset) which MUST use the same base filename as the Metadata file
and use the `.sigmf-data` extension. If a SigMF Recording or Archive is renamed this
field MUST also be updated, because of this it is RECOMMENDED that Compliant SigMF
Recordings avoid use of this field.

This field SHOULD NOT be used in conjunction the `core:metadata_only` field. If both
fields exist and the file specified by `core:dataset` exists, then `core:metadata_only`
SHOULD be ignored by the application.

**The `trailing_bytes` Field**

This field is used with Non-Conforming Datasets to indicate some number of bytes that
trail the sample data in the NCD file that should be ignored for processing. This can
be used to ignore footer data in non-SigMF filetypes.

 **The `metadata_only` Field**

This field should be defined and set to `true` to indicate that the Metadata
file is being distributed without a corresponding `.sigmf-data` file. This may
be done when the Dataset will be generated dynamically from information in the
schema, or because just the schema is sufficient for the intended application. A
metadata only distribution is not a SigMF Recording.

If a Compliant SigMF Recording uses this field, it MAY indicate that the Dataset
was dynamically generated from the metadata. This field MAY NOT be used in
conjunction with Non-Conforming Datasets or the `core:dataset` field.

**The `geolocation` Field**

See the `geolocation` field within `Captures`.  While it can also be provided within Global, Captures is preferred.

**The `extensions` Field**

The `core:extensions` field in the Global Object is an array of `extension` Objects
that describe SigMF extensions. Extension Objects MUST contain the three key/value 
pairs defined below, and MUST NOT contain any other fields.

| name       | required | type    | description                                                                 |
| ---------- | -------- | ------- | --------------------------------------------------------------------------- |
| `name`     | true     | string  | The name of the SigMF extension namespace.                                  |
| `version`  | true     | string  | The version of the extension namespace specification used.                  |
| `optional` | true     | boolean | If this field is `true`, the extension is REQUIRED to parse this Recording. |

In the example below, `extension-01` is used, but not necessary, and
`version 1.2.3` of `extension-02` *is* necessary.

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

**The `collection` Field**

This field is used to indicate that this Recording is part of a SigMF Collection 
(described later in this document). It is strongly RECOMMENDED that if you are 
building a Collection, that each Recording referenced by that Collection use this 
field to associate up to the relevant `sigmf-collection` file.

#### Captures Array

The `captures` value is an array of `capture segment` Objects that describe the
parameters of the signal capture. It MUST be sorted by the value of each
capture segment's `core:sample_start` key, ascending.

##### Capture Segment Objects

Capture Segment Objects are composed of key/value pairs, and each Segment describes
a chunk of samples that can be mapped into memory for processing. Each Segment
MUST contain a `core:sample_start` key/value pair, which indicates the sample index
relative to the Dataset where this Segment's metadata applies. The fields that are
described within a Capture Segment are scoped to that Segment only and need to be
explicitly declared again if they are valid in subsequent Segments.

The following names are specified in the Core namespace for use in Capture
Segment Objects:

| name            | required | type   | description                                                                                 |
| ----------------| -------- | ------ | --------------------------------------------------------------------------------------------|
| `sample_start`  | true     | uint   | The sample index in the Dataset file at which this Segment takes effect.                    |
| `global_index`  | false    | uint   | The index of the sample referenced by `sample_start` relative to an original sample stream. |
| `header_bytes`  | false    | uint   | The number of bytes preceding a chunk of samples that are not sample data, used for NCDs.  |
| `frequency`     | false    | double | The center frequency of the signal in Hz.                                                   |
| `datetime`      | false    | string | An ISO-8601 string indicating the timestamp of the sample index specified by `sample_start`.|
| `geolocation`   | false    | GeoJSON `point` Object | The location of the Recording system. |

**The `sample_start` Field**

This field specifies the sample index where this Segment takes effect relative
to the recorded Dataset file. If the Dataset is a SigMF Dataset file, this 
field can be immediately mapped to physical disk location since conforming
Datasets only contain sample data.

**The `global_index` Field**

This field describes the index of the sample referenced by the `sample_start`
field relative to an original sample stream, the entirety of which may not
have been captured in a recorded Dataset. If omitted, this value SHOULD
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

**The `header_bytes` Field**

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

**The `datetime` Field**

This key/value pair MUST be an ISO-8601 string, as defined by [RFC 3339](https://www.ietf.org/rfc/rfc3339.txt),
where the only allowed `time-offset` is `Z`, indicating the UTC/Zulu timezone.
The ABNF description is:

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

**The `geolocation` Field**

The `core:geolocation` field in the Captures or Global Object (Captures is preferred) is used to store the
location of the recording system. The location is stored as a single
[RFC 7946](https://www.rfc-editor.org/rfc/rfc7946.txt) GeoJSON `point` Object
using the convention defined by [RFC 5870](https://www.rfc-editor.org/rfc/rfc5870.txt).
Per the GeoJSON specification, the point coordinates use the WGS84 coordinate
reference system and are `longitude`, `latitude` (REQUIRED, in decimal degrees),
and `altitude` (OPTIONAL, in meters above the WGS84 ellipsoid) - in that order. An
example including the altitude field is shown below:

```JSON
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
a valid GeoJSON `point` Object, users MAY include *Foreign Member* fields here
for user-defined purposes (position valid indication, GNSS SV counts, dillution
of precision, accuracy, etc). It is strongly RECOMMENDED that all fields be
documented in a SigMF Extension document.

*Note:* Objects named `geometry` or `properties` are prohibited Foreign Members
as specified in RFC 7946 Section 7.1.

#### Annotations Array

The `annotations` value is an array of `annotation` Objects that describe
anything regarding the signal data not part of the Captures and Global
Objects. It MUST be sorted by the value of each Annotation Segment's
`core:sample_start` key, ascending.

##### Annotation Segment Objects

Annotation segment Objects contain key/value pairs and MUST contain a 
`core:sample_start` key/value pair, which indicates the first index 
at which the rest of the Segment's key/value pairs apply.

The following names are specified in the Core namespace for use in Annotation
Segment Objects:

| name              | required | type   | description                                                                         |
| ----------------- | -------- | ------ | ----------------------------------------------------------------------------------- |
| `sample_start`    | true     | uint   | The sample index at which this Segment takes effect.                                |
| `sample_count`    | false    | uint   | The number of samples that this Segment applies to.                                 |
| `generator`       | false    | string | Human-readable name of the entity that created this annotation.                     |
| `label`           | false    | string | A short form human/machine-readable label for the annotation.                       |
| `comment`         | false    | string | A human-readable comment.                                                           |
| `freq_lower_edge` | false    | double | The frequency (Hz) of the lower edge of the feature described by this annotation.   |
| `freq_upper_edge` | false    | double | The frequency (Hz) of the upper edge of the feature described by this annotation.   |
| `uuid`            | false    | string | A RFC-4122 compliant UUID string of the form `xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx`.|
| `latitude`        | false    |        | The latitude corresponding to the annotation (DEPRECATED, use `core:geolocation`).  |
| `longitude`       | false    |        | The longitude corresponding to the annotation (DEPRECATED, use `core:geolocation`). |

**The Sample Index Fields**

There is no limit to the number of annotations that can apply to the same group
of samples. If two annotations have the same `sample_start`, there is no
defined ordering between them. If `sample_count` is not provided, it SHOULD
be assumed that the annotation applies from `sample_start` through the end of
the Dataset, in all other cases `sample_count` MUST be provided.

**The `freq_*_edge` Fields**

The `freq_lower_edge` and `freq_upper_edge` fields SHOULD be at RF if the
feature is at a known RF frequency. If there is no known center frequency (as
defined by the `frequency` field in the relevant Capture Segment Object), or
the center frequency is at baseband, the `freq_lower_edge` and `freq_upper_edge`
fields SHOULD be relative to baseband. It is REQUIRED that both `freq_lower_edge`
and `freq_upper_edge` be provided, or neither; the use of just one field is not
allowed.

**The `label` Field**

The `label` field MAY be used for any purpose, but it is RECOMMENDED that it be
limited to no more than 20 characters as a common use is a short form GUI
indicator. Similarly, it is RECOMMENDED that any user interface making use of 
this field be capable of displaying up to 20 characters.

### SigMF Collection Format

The `sigmf-collection` file contains metadata in a single top-level Object 
called a `collection`. The Collection Object contains key/value pairs that 
describe relationships between SigMF Recordings.

The Collection Object associates SigMF Recordings together by specifying
`SigMF Recording Objects` in the `core:streams` JSON array. Each Object
describes a specific associated SigMF Recording.

The following rules apply to SigMF Collections:

1. The Collection Object MUST be the only top-level Object in the file.
1. Keys in the Collection Object SHOULD use SigMF Recording Objects when
   referencing SigMF Recordings.
1. SigMF Recording Objects MUST contain both a `name` field, which is the
   base-name of a SigMF Recording, and a `hash` which is the SHA512 hash of
   the Recording Metadata file `[base-name].sigmf-meta`.
1. SigMF Recording Objects MUST appear in a JSON array.

The following names are specified in the `core` namespace for use in the `collection`
Object.

| name             | required | type                  | description |
| -----------------| ---------| ----------------------| ------------|
| `version`        | true     | string                | The version of the SigMF specification used to create the Collection file.|
| `description`    | false    | string                | A text description of the SigMF Collection.|
| `author`         | false    | string                | A text identifier for the author potentially including name, handle, email, and/or other ID like Amateur Call Sign. For example "Bruce Wayne <bruce@waynetech.com>" or "Bruce (K3X)".|
| `collection_doi` | false    | string                | The registered DOI (ISO 26324) for a Collection.|
| `license`        | false    | string                | A URL for the license document under which this Collection metadata is offered.|
| `extensions`     | false    | array                 | A list of Objects describing extensions used by this Collection.|
| `streams`        | false    | array                 | An ordered array of SigMF Recording Tuples, indicating multiple recorded streams of data (e.g., channels from a phased array).|

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
        "antenna:hagl": {
            "name": "hagl-basename",
            "hash": "9c1ab7285c13644cef5d910dc774ca63d1921f91318417cfadc71c4d7f3acf85ec3c5b05e9335e9cc310b1557de517519c76da540b08886a0e440d71e1271fd0"
        },
        "antenna:azimuth_angle": {
            "name": "azimuth-angle-basename",
            "hash": "6eb7f16cf7afcabe9bdea88bdab0469a7937eb715ada9dfd8f428d9d38d86133945f5f2f2688ddd96062223a39b5d47f07afc3c48d9db1d5ee3f41c8d274dccf"
        },
        "core:streams": [
            {
               "name": "example-channel-0-basename",
               "hash": "b4071db26f5c7b0c70f5066eb9bc3a8b506df0f5af09991ba481f63f97f7f48e9396584bc1c296650cd3d47bc4ad2c5b72d2561078fb6eb16151d2898c9f84c4"
            },
            {
               "name": "example-channel-1-basename",
               "hash": "7132aa240e4d8505471cded716073141ae190f763bfca3c27edd8484348d6693d0e8d3427d0bf1990e687a6a40242d514e5d1995642bc39384e9a37a211655d7"
            }
        ]
    }
}
```

#### SigMF Recording Objects

`SigMF Recording Objects` reference the base-name of the SigMF Recording and the
SHA512 hash of the Metadata file, and SHOULD BE specified as a JSON Object:

```JSON
  {
    "name": "example-channel-0-basename",
    "hash": "b4071db26f5c7b0c70f5066eb9bc3a8b506df0f5af09991ba481f63f97f7f48e9396584bc1c296650cd3d47bc4ad2c5b72d2561078fb6eb16151d2898c9f84c4"
  }
```

Recording Tuples are also permitted and have a similar form. The order of
the tuple: [`name`, `hash`] is REQUIRED when using tuples:

```JSON
  ["example-channel-0-basename", "b4071db26f5c7b0c70f5066eb9bc3a8b506df0f5af09991ba481f63f97f7f48e9396584bc1c296650cd3d47bc4ad2c5b72d2561078fb6eb16151d2898c9f84c4"]
```

Tuples will be removed in SigMF version 2.0, so JSON Objects are RECOMMENDED.
Additional optional user fields MAY be added to `SigMF Recording Objects` if
they are defined in a compliant SigMF extension. Additional fields are NOT
permitted in tuples.

## Licensing

Open licenses are RECOMMENDED but you can specify any license. You can refer to 
resources provided by the [Open Data Commons](https://opendatacommons.org/) when 
deciding which open license fits your needs best. Cornell University has also 
created [a guide](https://data.research.cornell.edu/content/intellectual-property#data-licensing) 
to help you make these choices.

## SigMF Compliance

The term 'SigMF Compliant' is used throughout this document, which can take on
one of several contextually dependent meanings. In order for a schema,
Recording, or application to be 'SigMF Compliant', specific conditions MUST be
met, outlined in the following sections. Provided the below criteria are met, an
application or Recording can indicate that it is 'SigMF Compliant'.

### SigMF Schema Compliance

In order to be 'SigMF Compliant', a schema MUST meet the following requirements:

1. Adheres to and supports the metadata file naming conventions, `objects`,
   `namespaces`, and `names` specified by this document.
1. MUST contain all REQUIRED fields with the correct datatype listed the `core`
   namespace, and any namespace listed in the `extensions` array.
1. MUST NOT contain fields that are not outlined in the `core` or a listed
   `extensions` namespace.

### SigMF Recording Compliance

In order to be 'SigMF Compliant', a Recording MUST meet the following
requirements:

1. The Recording's schema file MUST be SigMF Compliant.
1. Adheres to and supports the file naming conventions and Dataset formats
   specified in this document.
1. Stores data using the on-disk representation described by the `datatype`.

Recordings with Non-Conforming Datasets MAY have SigMF Compliant schema, but
cannot be SigMF Compliant Recordings.

### SigMF Collection Compliance

In order to be 'SigMF Compliant', a Collection must meet the following
requirements:

1. The collection MUST contain only compliant Recordings.
1. The Collection Object MUST only contain SigMF key/value pairs provided by
   the core specification or a compliant SigMF extension.

### SigMF Application Compliance

In order to be 'SigMF Compliant', an application MUST meet the following
requirements:

1. Is capable of parsing and loading SigMF Compliant Recordings. Support for
   SigMF Collections and Archives is RECOMMENDED but not REQUIRED.
1. Adheres to and supports the file rules, Dataset formats, `objects`,
   `namespaces`, and `names` specified by this document.
1. MUST be able to ignore any `object` or `namespace` not specified by this
   document and still function normally.
1. Capture Segments referring to non-existent samples SHOULD be ignored.
1. MUST treat consecutive Capture Segments whose metadata is equivalent for
   purposes of that application (i.e., it may be different in values ignored by
   the application such as optional values or unknown extensions) as it would
   a single segment.
1. MUST support parsing ALL required fields in the `core` namespace, and defines
   which optional fields are used by the application.
1. MUST define which extensions are supported, parses ALL required fields in
   listed extension namespaces, and defines which optional fields are used. This
   definition can be in user documentation or within the code itself, though
   explicit documentation is RECOMMENDED.
1. Support for ALL SigMF Datatypes is NOT REQUIRED as certain datatypes may not
   make sense for a particular application, but Compliant applications MUST
   define which datatypes are supported, and be capable of loading Compliant
   Recordings using supported datatypes.

Compliant applications are NOT REQUIRED to support Non-Conforming Datasets or
Metadata Only schema files, but it is RECOMMENDED that they parse the respective
metadata fields in the `global` Object to provide descriptive messages to users
regarding why the files are not supported.

Support for SigMF Collections is OPTIONAL for SigMF Compliant applications,
however it is RECOMMENDED that applications implementing SigMF make use of
Collections when appropriate for interoperability and consistency.

## Citing SigMF

To cite the SigMF specification, we recommend the following format:

```txt
The Signal Metadata Format (SigMF), <release>, <date of release>, https://sigmf.org
```

## Acknowledgements

This specification originated at the DARPA Brussels Hackfest 2017.
