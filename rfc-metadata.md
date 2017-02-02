# RFC Metadata

cool title pending beer consumption

## Abstract

## Status of this Document

This document is currently under active development as part of the [DARPA
Brussels Hackfest](http://www.darpahackfest.com/).

## Copyright Notice

This document is Copyright of The GNU Radio Foundation, Inc. 

This document is available under the [CC-BY-SA License](http://creativecommons.org/licenses/by-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

## Table of Contents

auto-generate this

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

JSON key words are used as defined in [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

## Specification

This specification fundamentally describes two types of information: datasets,
and metadata associated with those datasets.

Datasets, for purposes of this specification, are recordings of digital samples.
The samples may be created by digital synthesis (i.e., simulation) or by an
actual Analog-to-Digital Converter (ADC) that is sampling an analog signal.

Metadata describes the dataset with which it is associated. The metadata
includes information meant for the human users of the dataset, such as a title and
description, and information meant for computer applications (tools) that
operate on the dataset.

### Files

One complete [NAME] consists of two files: a `metadata` file and a `dataset`
file. The dataset file is a binary file for storing samples, and the metadata
file contains information that describes the dataset.

1. The metadata and dataset MUST be separate files.
2. A metadata file MUST only describe one dataset file.
3. The metadata file MUST have a `.meta` filename extension.
4. The dataset file MUST have a `.data` filename extension.
5. The dataset file MUST be a 'flat' file that is composed only of sample data
   and MUST NOT contain any other characters (e.g., delimiters, whitespace,
   line-endings, `EOF` characters, etc.,).

### Sample Format

The samples in the dataset file must be in a supported format. There are four
orthogonal characteristics of sample data: complex or real, floating-point or
fixed-point, bit-width, and endianness. All of these must be explicitly
specified, except for endianness which is assumed to be `little endian` unless
specified otherwise.

Sample formats are specified by strings that indicate the type for each of the
four different characteristics. The types must be specified in the following
order:

```
<complex or real> <floating or fixed> <bit-width> <endianness>
```

Where the following strings specify types:

` ` or `c`: `<nothing>` for real data, and `c` for complex (quadrature) data.
`f` or `i` or `u`: `f` for floating-point, `i` for signed fixed-point, and `u`
for unsigned fixed-point.
`8` or `16` or `32`: `8` for 8-bit samples, `16` for 16-bit samples, `32` for
32-bit samples.
`_le` or `_be`: `_le` for little-endian, `_be` for big-endian.



The tables below detail how to specify each type.

**Complex or Real:**


|type string|description|
|-----------|-----------|
|"cf32"|complex 32-bit floating-point
|"ci32"|complex 32-bit integer
|"ci16"|complex 16-bit integer
|"ci8"|real signed 8-bit integer
|"f32"|real 32-bit floating-point
|"i32"|real 32-bit integer
|"i16"|real 16-bit integer
|"i8"|real signed 8-bit integer
|"u8"|real unsigned 8-bit integer

int8
uint8
int16
uint16
float

In order to specify an endianness, an extension is added to the above type
strings: `_le` for little-endian or `_be` for big-endian (e.g., `cf32_be` is
complex 32-bit floats in big-endian).

### Metadata Format

Metadata is written in JSON, and takes the form of JSON name/value pairs which
are contained within JSON `objects`. There are three types top-level objects:
`global`, `capture`, and `annotations`. The `global` object is composed of
name/value pairs. The `capture` and `annotations` objects contain an array of
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

|type|name|description|
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

**core:datatype**

|namespace|name|datatype|required|description|default|
|---------|----|--------|--------|-----------|-------|
|core|datatype|string|true|Format of the sample data|nil|
|core|offset|uint64|false|Index offset of the first sample.|0|
|core|description|string|false|Textual description of the dataset.|nil|
|core|author|string|false|Name and optionally email address of the author.|nil|
|core|license|string|true|License of the [NAME].|CC0|
|core|date|string|true|ISO 8601-formatted date.|nil|
|core|url|string|true|Location of the dataset file.|nil|
|core|sha512|string|true||
core:version true
core:hw




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
