# The `modulation` SigMF Extension Namespace v0.0.2

## Description

This document defines the `modulation` extension namespace for the Signal
Metadata Format (SigMF) specification. This extension namespace defines how to
describe the modulations of wireless communications systems.

## Copyright Notice

This document is Copyright of The GNU Radio Foundation, Inc.

This document is available under the [CC-BY-SA License](http://creativecommons.org/licenses/by-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

## Conventions Used in this Document

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

JSON keywords are used as defined in [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

Augmented Backus-Naur form (ABNF) is used as defined by [RFC
5234](https://tools.ietf.org/html/rfc5234) and updated by [RFC
7405](https://tools.ietf.org/html/rfc7405).

Fields defined as "human-readable", a "string", or simply as "text" shall be
treated as plaintext where whitespace is significant, unless otherwise
specified.

## Specification

This specification defines an extension `modulation` namespace
that can be used in SigMF `annotations` to describe wireless communications
systems.

### Annotations

This extension adds the following field to the `annotations` global SigMF object:

|name|required|type|description|
|----|--------------|-------|-----------|
|modulation|false|object|Describes a communications system.|

The field of communications is vast, and there may be communications systems that cannot be described using the names and fields described in this extension. If you need additional or different fields to describe a system, create a new extension that adds the necessary fields to the `modulation` namespace and/or submit the new fields to be upstreamed into this specification.

#### The `modulation` Object

`modulation` objects contain name/value pairs that describe the modulations of communications systems. These objects MAY contain the following pairs:

|name|required|type|
|----|--------------|-------|
|`type`|false|string|
|`class`|false|string|
|`carrier_variant`|false|string|
|`symbol_variant`|false|string|
|`order`|false|uint|
|`duplexing`|false|string|
|`multiplexing`|false|string|
|`multiple_access`|false|string|
|`spreading`|false|string|
|`bandwidth`|false|float|
|`system`|false|string|

###### The `type` Pair

The `type` name can have the following values:

|value|description|
|----|-------|
|`analog`|analog modulation scheme|
|`digital`|digital modulation scheme|

###### The `class` Pair

The `class` name can have the following values:

|value|description|
|----|-------|
|`am`|(analog) amplitude modulation|
|`fm`|(analog) frequency modulation|
|`pm`|(analog) phase modulation|
|`ssb`|(analog) single side-band|
|`dsb`|(analog) dual side-band|
|`vsb`|(analog) vestigal side-band|
|`ask`|(analog) amplitude-shift keying|
|`fsk`|(digital) frequency-shift keying|
|`psk`|(digital) phase-shift keying|
|`qam`|(digital) quadrature-amplitude modulation|
|`ook`|(digital) on-off keying|
|`cpm`|(digital) continuous phase modulation|
|`msk`|(digital) minimum-shift keying|

###### The `carrier_variant` pair

The `carrier_variant` name can have the following values:

|value|type|description|
|----|----|-------|
|`with_carrier`|(analog) with-carrier modulation|
|`suppressed_carrier`|(analog) suppressed-carrier modulation|
|`reduced_carrier`|(analog) reduced-carrier modulation|
|`single_carrier`|(digital) single-carrier modulation|
|`multi_carrier`|(digital) multi-carrier modulation|

###### The `carrier_variant` pair

The `symbol_variant` name can have the following values:

|value|type|description|
|----|----|-------|
|`differential`|differential modulation|
|`offset`|offset modulation (sometimes called 'staggered')|

###### The `order` Pair

The `order` name has an unsigned integer value that describes the modulation order, which typically refers to the number of symbols or states in a digital modulation (e.g., QAM64 has 64 symbols, QPSK has 4 symbols).

###### The `duplexing` Pair

The `duplexing` name can have the following values:

|value|description|
|----|-------|
|`tdd`|time-division duplexing|
|`fdd`|frequency-division duplexing|

###### The `multiplexing` Pair

The `multiplexing` name can have the following values:

|value|description|
|----|-------|
|`tdm`|time-division multiplexing|
|`fdm`|frequency-division multiplexing|
|`cdm`|code-division multiplexing|
|`ofdm`|orthogonal frequency-division multiplexing|
|`sdm`|space-division multiplexing|
|`pdm`|polarization-division multiplexing|

###### The `multiple_access` Pair

The `multiple_access` name can have the following values:

|value|description|
|----|-------|
|`fdma`|frequency-division multiple access|
|`ofdma`|orthogonal frequency-division multiple access|
|`tdma`|time-division multiple access|
|`cdma`|code-division multiple access|
|`sdma`|space-division multiple access|
|`pdma`|power-division multiple access|

###### The `spreading` Pair

The `spreading` name can have the following values:

|value|description|
|----|-------|
|`fhss`|frequency-hopping spread spectrum|
|`thss`|time-hopping spread spectrum|
|`dsss`|direct-sequence spread spectrum|
|`css`|chirp spread spectrum|

###### The `bandwidth` Pair

The `bandwidth` name has a float value that describes the channel bandwidth of the signal. Note that this is different from what is reported in the `core` namespace within an annotation, describing the occupied spectrum of a signal, which may or may not be comparable to the actual channel bandwidth of the communications system.

###### The `system` Pair

The `system` name is meant to provide a way to describe the higher-level system. For example, "802.11ac", "BlueTooth", or "LTE Release 12".

## Examples

Here is an example of a relatively simple modulation label, which describes a 10 kHz FM signal using time-division duplexing:

    "modulation": {
        "type": "analog",
        "class": "fm",
        "duplexing": "tdd",
        "bandwidth": 10000.0
    }

Here is a more complex example that describes an LTE 5 MHz SC-OFDMA downlink:

    "modulation": {
        "type": "digital",
        "class": "qam",
        "carrier_variant": "single_carrier",
        "order": 16,
        "multiple_access": "ofdma",
        "bandwidth": 5000000.0,
        "system": "LTE Release 12"
    }
