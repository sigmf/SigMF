# DVB-S2 Extension v1.0.0

## Abstract

This document defines the `dvbs2` extension namespace for the Signal Metadata Format (SigMF) specification. This extension namespace defines new datatypes and properties of DVB-S2/S2X signals extending the `global` object in SigMF Recordings.

## Table of Contents
- [DVB-S2 Extension v1.0.0](#dvb-s2-extension-v100)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Acronyms and Terms](#acronyms-and-terms)
  - [Datatypes](#datatypes)
  - [Global Object](#global-object)
    - [The `modcod` Union](#the-modcod-union)
    - [The `rolloff` Enum](#the-rolloff-enum)
    - [The `fecframe_size` Enum](#the-fecframe_size-enum)
  - [Captures Array](#captures-array)
  - [Annotations Array](#annotations-array)
  - [Collections](#collections)
  - [Examples](#examples)
    - [CCM Recording](#ccm-recording)
    - [VCM Recording](#vcm-recording)


## Acronyms and Terms

| Acronym | Description                            |
| ------- | -------------------------------------- |
| ACM     | Adaptive coding and modulation         |
| CCM     | Constant coding and modulation         |
| GS      | Generic stream                         |
| ISSYI   | Input stream synchronization indicator |
| MIS     | Multiple input stream                  |
| MODCOD  | Modulation and coding scheme           |
| PL      | Physical layer                         |
| SIS     | Single input stream                    |
| TS      | Transport stream                       |
| VCM     | Variable coding and modulation         |

## Datatypes

The `dvbs2` namespace defines the following datatypes:

| type  | long-form name  | description                                                                                                                                               |
| ----- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| union | Union type      | Union type accepting values represented by two or more [core datatypes](https://github.com/sigmf/SigMF/blob/sigmf-v1.x/sigmf-spec.md#datatypes).          |
| enum  | Enumerated type | Enumeration accepting a defined set of elements represented by a [core datatype](https://github.com/sigmf/SigMF/blob/sigmf-v1.x/sigmf-spec.md#datatypes). |



## Global Object

The following names are specified in the `dvbs2` namespace and should be used in the `global` object:

| name            | required | type               | description                                                                                                                                                                                                                                                                                                                                     |
| --------------- | -------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `symbol_rate`   | true     | double             | The symbol rate of the signal in symbols per second (or bauds).                                                                                                                                                                                                                                                                                 |
| `gs`            | false    | boolean            | Whether the signal carries a continuous GS. False when the signal carries a packetized TS. If omitted, defaults to false (TS).                                                                                                                                                                                                                  |
| `mis`           | false    | boolean            | Whether the signal has MIS configuration. False when the signal has SIS configuration. If omitted, defaults to false (SIS).                                                                                                                                                                                                                     |
| `acm_vcm`       | false    | boolean            | Whether the signal has ACM or VCM. False when the signal consists of CCM. If omitted, defaults to false (CCM).                                                                                                                                                                                                                                  |
| `issyi`         | false    | boolean            | Whether the signal has ISSYI active. If omitted, defaults to false (inactive).                                                                                                                                                                                                                                                                  |
| `npd`           | false    | boolean            | Whether the signal has null-packet deletion active. If omitted, defaults to false (inactive).                                                                                                                                                                                                                                                   |
| `rolloff`       | false    | [enum](#datatypes) | Signal's baseband shaping roll-off factor given by the [rolloff enum](#the-rolloff-enum).                                                                                                                                                                                                                                                       |
| `modcod`        | false    | array              | Array of MODCODs present in the signal, each represented by a [`modcod` union](#the-modcod-union) value. Should contain a single element in CCM mode (when `acm_vcm` is `false` or omitted). When omitted, it is implied the MODCODs are unknown or dynamically changing and should be discovered by the demodulator.                           |
| `fecframe_size` | false    | array              | Array of FECFRAME sizes present in the signal, each represented by a [`fecframe_size` enum](#the-fecframe_size-enum) value. Should contain a single element in CCM mode (when `acm_vcm` is `false` or omitted). When omitted, it is implied the FECFRAME sizes are unknown or dynamically changing and should be discovered by the demodulator. |
| `pilots`        | false    | boolean            | Whether the signal contains PL pilots. When omitted, it is implied the presence or absence of pilots is unknown or dynamically changing and should be discovered by the demodulator.                                                                                                                                                            |
| `gold_code`     | false    | uint               | n-th Gold code for PL descrambling. If omitted, defaults to code 0.                                                                                                                                                                                                                                                                             |

### The `modcod` Union

A `modcod` union value takes one of the following types:

| type   | description                                                                                                                                                                             |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| string | Canonical name of the signal's MODCOD with the constellation in upper case, followed by a space and the code rate. For example, "QPSK 1/4" or "32APSK 9/10".                            |
| uint   | PLS code decimal value representing the MODCOD as given by EN 302 307-1, Table 12 (DVB-S2), or EN 302 307-2, Table 17 (DVB-S2X). For example, `1` for QPSK 1/4 or `28` for 32APSK 9/10. |

### The `rolloff` Enum

The `rolloff` double-typed [enum](#datatypes) can have one of the following values:

| value | description        |
| ----- | ------------------ |
| 0.35  | DVB-S2 and DVB-S2X |
| 0.25  | DVB-S2 and DVB-S2X |
| 0.2   | DVB-S2 and DVB-S2X |
| 0.15  | DVB-S2X            |
| 0.1   | DVB-S2X            |
| 0.05  | DVB-S2X            |


### The `fecframe_size` Enum

The `fecframe_size` string-typed [enum](#datatypes) can have one of the following values:

| value    | description                                      |
| -------- | ------------------------------------------------ |
| `normal` | Normal FECFRAME size (64800 bits).               |
| `short`  | Short FECFRAME size (16200 bits).                |
| `medium` | Medium FECFRAME size (32400 bits), DVB-S2X only. |

## Captures Array

`dvbs2` does not extend [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array).

## Annotations Array

`dvbs2` does not extend [Annotations](https://github.com/sigmf/SigMF/blob/sigmf-v1.x/sigmf-spec.md#annotations-array).

## Collections

`dvbs2` does not extend SigMF [Collections](https://github.com/sigmf/SigMF/blob/sigmf-v1.x/sigmf-spec.md#sigmf-collection-format).

## Examples

The following SigMF `.sigmf-meta` examples illustrate CCM and VCM IQ recordings:

### CCM Recording

The following example is a baseband CCM DVB-S2 signal collected with a sample rate of 2 Msamples/sec and consisting of a 1 Mbaud QPSK 3/5 MODCOD, pulse-shaped with 0.2 roll-off factor, with normal FECFRAME size, and PL pilots enabled:

```json
{
    "global": {
        "core:datatype": "cu8",
        "core:sample_rate": 2000000,
        "core:version": "1.0.0",
        "dvbs2:symbol_rate": 1000000,
        "dvbs2:rolloff": 0.2,
        "dvbs2:modcod": [
            "QPSK 3/5"
        ],
        "dvbs2:fecframe_size": [
            "normal"
        ],
        "dvbs2:pilots": true
    },
    "captures": [
        {
            "core:sample_start": 0
        }
    ],
    "annotations": []
}
```

> NOTE: The MODCOD and FECFRAME size arrays have a single element, given that this is a CCM recording.

### VCM Recording

The following example is also a 1 Mbaud baseband DVB-S2 signal collected with a sample rate of 2 Msamples/sec. However, in contrast to the previous example, this recording carries two MODCODs simultaneously in VCM mode, QPSK 1/4 and 8PSK 3/5, while flagging `dvbs2:acm_vcm` to `true`:

```json
{
    "global": {
        "core:datatype": "cu8",
        "core:sample_rate": 2000000,
        "core:version": "1.0.0",
        "dvbs2:symbol_rate": 1000000,
        "dvbs2:rolloff": 0.2,
        "dvbs2:acm_vcm": true,
        "dvbs2:modcod": [
            "QPSK 1/4",
            "8PSK 3/5"
        ],
        "dvbs2:fecframe_size": [
            "normal"
        ],
        "dvbs2:pilots": true
    },
    "captures": [
        {
            "core:sample_start": 0
        }
    ],
    "annotations": []
}
```