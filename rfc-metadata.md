# RFC Metadata

cool title pending beer consumption

## Abstract

## Status of this Document

## Copyright Notice

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
The metadata MUST be in a separate file from the dataset.

#### Dataset File
IQ
real

#### Metadata File


### Metadata Format

#### Markup
JSON

#### Types of Segments
global, capture_info, annotations


### Dataset Format

## Example
example of metadata file contents

# Acknowledgements
DARPA
