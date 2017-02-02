# Signal Metadata Format Specification v0.0.1

## Abstract

## Status of this Document

This document is currently under active development as part of the [DARPA
Brussels Hackfest](http://www.darpahackfest.com/).

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
                - [The `core` Namespace](#the-core-namespace)
            - [Global Object](#global-object)
            - [Capture Object](#capture-object)
            - [Annotation Object](#annotation-object)
        - [Dataset Licensing](#dataset-licensing)
        - [application requirements](#application-requirements)
    - [Example](#example)
- [Acknowledgements](#acknowledgements)

<!-- markdown-toc end -->

## Introduction

Why this is needed

portability of datasets

ensure datasets remain useful after capture

ability to share datasets

enable scientific rigor / reproduction

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
2. A metadata file MUST only describe one dataset file.
3. The metadata file MUST have a `.meta` filename extension.
4. The dataset file MUST have a `.data` filename extension.

### Dataset Format

The samples in the dataset file must be in a SigMF-supported format. There are
four orthogonal characteristics of sample data: complex or real, floating-point
or fixed-point, bit-width, and endianness. All of these must be explicitly
specified, except for endianness which is assumed to be `little-endian` unless
specified otherwise.

SigMF sample formats are specified by strings that indicate the type for each of
the four different characteristics. The types are specified with the following
characters / strings:

* ` ` (empty): real-valued data
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

`<c|(empty)>``<f|i|u>``<8|16|32>``[<_le|_be>]`

So, for example, the string `"cf32"` specifies `complex 32-bit floating-point
samples stored in little-endian`, and the string `u16_be` specifies `real
unsigned 16-bit samples stored in big-endian`.

The samples should be written to the dataset file without separation, and the
dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, `EOF` characters, etc.,).

### Metadata Format

SigMF is written in JSON, and takes the form of JSON name/value pairs
which are contained within JSON `objects`. There are three types top-level
objects: `global`, `capture`, and `annotations`. The `global` object is composed
of name/value pairs. The `capture` and `annotations` objects contain an array of
sorted objects, which are called `capture segments` and `annotation segments`,
respectively. These `segments` are composed of name/value pairs. The names of
the name/value pairs can be namespaced for further structure.

The format of the name/value pairs is:

```
"<namespace:>name": value,
```

Where the `namespace` string should be replaced with the name of the namespace
in use, or omitted entirely (including the colon).

1. The metadata MUST be written in [JSON](http://www.json.org/), as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf),
   composed of ASCII text.
2. The entire contents of the metadata file MUST be contained within a single
   JSON object (i.e., the first character of the file MUST be '{' and the last
   character of the file MUST be '}'. This object is hereafter called the
   `top-level object`.
3. The top-level object MUST contain three objects named `global`, `capture`,
   and `annotations`.
   
#### Datatypes

The values in each name/value pair must be one of the following datatypes:

|type|long-form name|description|
|----|----|-----------|
|int16|short|Signed 16-bit integer.|
|int32|integer|Signed 32-bit integer.|
|int64|long|Signed 64-bit integer.|
|uint16|unsigned short|Unsigned 16-bit integer.|
|uint32|unsigned integer|Unsigned 32-bit integer.|
|uint64|unsigned long|Unsigned 64-bit integer.|
|float|single-precision floating-point number|A 32-bit float as defined by IEEE 754.|
|double|double-precision floating-point number|A 64-bit float as defined by IEEE 754.|
|string|string|A string of ASCII characters, as defined by the JSON standard.|
|boolean|boolean|Either `true` or `false`, as defined by the JSON standard.|
|null|null|`null`, as defined by the JSON standard.|
   
#### Namespaces

Namespaces provide a way to further classify name/value pairs within metadata
objects. This specification defines the `core` namespace, which contains
commonly used name/value pairs for describing signal data.

Other namespaces may be defined by the user as needed.

##### The `core` Namespace

The following names are specified in the `core` namespace:

|name|valid segments|default|description|
|----|--------------|-------|-----------|
|`core:type` |`global`|null|The `type` name describes the format of the stored samples in the dataset file. Its value must be a valid SigMF dataset format type string.|
|`core:type` |`global`|null|The `type` name describes the format of the stored samples in the dataset file. Its value must be a valid SigMF dataset format type string.|
|`core:type` |`global`|null|The `type` name describes the format of the stored samples in the dataset file. Its value must be a valid SigMF dataset format type string.|
|`core:type` |`global`|null|The `type` name describes the format of the stored samples in the dataset file. Its value must be a valid SigMF dataset format type string.|



|namespace|name|datatype|required|description|default|
|---------|----|--------|--------|-----------|-------|
|core|datatype|string|true|A valid SigMF dataset format type string.|null|
|core|url|string|true|Location of the dataset file.|null|
|core|version|string|true|Version of SigMF Specification used for the recording.|null|
|core|sha512|string|true|The SHA512 hash of the dataset file.|null|
|core|offset|uint64|false|Index offset of the first sample.|0|
|core|description|string|false|Textual description of the dataset.|null|
|core|author|string|false|Name and optionally email address of the author.|null|
|core|date|string|false|ISO 8601-formatted date.|null|
|core|license|string|false|License of the SigMF recording.|null|
|core|hw|string|false|Description that |null|

#### Global Object

The global object provides information that applies to the entire dataset.

1. It is RECOMMENDED that the global object be the first object in the top-level
   object.
2. The global object MUST contain `core:datatype`.
3. `core:license`
4. `core:date`
5. `core:url`
6. `core:hash`
7. `core:version`

optional: `offset`, `description`, `author`, `hw`

#### Capture Object

#### Annotation Object

### Dataset Licensing

### application requirements
segments referring to non-existent samples should be ignored

applications should be able to ignore any sections not specified in this document

## Example
example of metadata file contents

# Acknowledgements
DARPA
