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

## Specification

This specification fundamentally describes two types of information: datasets,
and metadata associated with those datasets.

### Dataset

Datasets, for purposes of this specification, are recordings of digital samples.
The samples may be created by digital synthesis (i.e., simulation) or by an
actual Analog-to-Digital Converter (ADC) that is sampling an analog signal.


### Metadata

Metadata describes the dataset with which it is associated. The metadata
includes information meant for the human users of the dataset, such as a title and
description, and information meant for computer applications (tools) that
operate on the dataset.

### Files

1. The metadata and dataset MUST be separate files.
2. A metadata file MUST only describe one dataset file.

#### Dataset File & Format

1. The dataset file MUST have a `.data` filename extension.
2. The dataset file MUST be a 'flat' file that is composed only of sample data
   and MUST NOT contain any other characters (e.g., delimiters, whitespace,
   line-endings, `EOF` characters, etc.,).

#### Metadata File & Format

1. The metadata file MUST have a `.meta` filename extension.
2. The metadata file MUST be a [JSON](http://www.json.org/) file, as specified
   by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf),
   composed of ASCII text.

### Metadata Format

#### Types of Segments
global, capture_info, annotations


### Dataset Format

### application requirements
segments referring to non-existent samples should be ignored

## Example
example of metadata file contents

# Acknowledgements
DARPA
