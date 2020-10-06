# The `signal` SigMF Extension Namespace v0.0.2

## Description

This document defines the `signal` extension namespace for the Signal
Metadata Format (SigMF) specification. This extension namespace defines how to
describe the attributes of wireless communications systems.

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

This specification defines an extension `signal` namespace
that can be used in SigMF `annotations` to describe wireless communications
systems and their emitters.

### Annotations

This extension adds the following field to the `annotations` global SigMF object:

|name|required|type|description|
|----|--------------|-------|-----------|
|`emission`|false|object|Describes the communications system of a signal emission and its emitter.|

The field of communications is vast, and there may be communications systems that cannot be described using the names and fields described in this extension. If you need additional or different fields to describe a system, create a new extension that adds the necessary fields to the `signal` namespace and/or submit the new fields to be upstreamed into this specification.

#### The `emission` Object

`emission` objects contain name/value pairs that describe the modulations of communications systems. These objects MAY contain the following pairs:

|name|required|type|description|
|----|--------------|-------|----------|
|`label`|false|string|e.g., wifi|
|`detail`|false|[Detail](signal.sigmf-ext.md#the-detail-object)|Emission details (standard, modulation, etc.)|
|`emitter`|false|[Emitter](signal.sigmf-ext.md#the-emitter-object)|Emitter details (manufacturer, geo coordinates, etc.)|

##### The Emitter Object

|name|required|type|description|
|----|--------|----|-----------|
|`seid`|false|uint|Unique ID of the emitter|
|`manufacturer`|false|string|Manufacterer of the hardware used to emit the signal|
|`latitude`|false|float|Latitude|
|`longitude`|false|float|longitude|

##### The Detail Object

|name|required|type|description|
|----|--------|----|-----------|
|`type`|false|string|[type](signal.sigmf-ext.md#the-type-field)|
|`class`|false|string|[class](signal.sigmf-ext.md#the-class-field)|
|`standard`|false|string|Communication standard (e.g., 802.11ac)|
|`carrier_variant`|false|string|[carrier variant](signal.sigmf-ext.md#the-carrier_variant-field)|
|`symbol_variant`|false|string|[symbol variant](signal.sigmf-ext.md#the-symbol_variant-field)|
|`order`|false|uint|[order](signal.sigmf-ext.md#the-order-field)|
|`duplexing`|false|string|[duplexing](signal.sigmf-ext.md#the-duplexing-field)|
|`multiplexing`|false|string|[multiplexing](signal.sigmf-ext.md#the-multiplexing-field)|
|`multiple_access`|false|string|[multiple access](signal.sigmf-ext.md#the-multiple_access-field)|
|`spreading`|false|string|[spreading](signal.sigmf-ext.md#the-spreading-field)|
|`bandwidth`|false|float|[bandwidth](signal.sigmf-ext.md#the-bandwidth-field)|
|`channel`|false|uint|[channel](signal.sigmf-ext.md#the-channel-field)|
|`class_variant`|false|string|[class variant](signal.sigmf-ext.md#the-class_variant-field)|

###### The `type` Field

The `type` field can have the following values:

|value|description|
|----|-------|
|`analog`|analog modulation scheme|
|`digital`|digital modulation scheme|

###### The `class` Field

The `class` field can have the following values:

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

###### The `carrier_variant` Field

The `carrier_variant` field can have the following values:

|value|type|description|
|----|----|-------|
|`with_carrier`|(analog) with-carrier modulation|
|`suppressed_carrier`|(analog) suppressed-carrier modulation|
|`reduced_carrier`|(analog) reduced-carrier modulation|
|`single_carrier`|(digital) single-carrier modulation|
|`multi_carrier`|(digital) multi-carrier modulation|

###### The `symbol_variant` Field

The `symbol_variant` field can have the following values:

|value|type|description|
|----|----|-------|
|`differential`|differential modulation|
|`offset`|offset modulation (sometimes called 'staggered')|

###### The `order` Field

The `order` field has an unsigned integer value that describes the modulation order, which typically refers to the number of symbols or states in a digital modulation (e.g., QAM64 has 64 symbols, QPSK has 4 symbols).

###### The `duplexing` Field

The `duplexing` field can have the following values:

|value|description|
|----|-------|
|`tdd`|time-division duplexing|
|`fdd`|frequency-division duplexing|

###### The `multiplexing` Field

The `multiplexing` field can have the following values:

|value|description|
|----|-------|
|`tdm`|time-division multiplexing|
|`fdm`|frequency-division multiplexing|
|`cdm`|code-division multiplexing|
|`ofdm`|orthogonal frequency-division multiplexing|
|`sdm`|space-division multiplexing|
|`pdm`|polarization-division multiplexing|

###### The `multiple_access` Field

The `multiple_access` field can have the following values:

|value|description|
|----|-------|
|`fdma`|frequency-division multiple access|
|`ofdma`|orthogonal frequency-division multiple access|
|`tdma`|time-division multiple access|
|`cdma`|code-division multiple access|
|`sdma`|space-division multiple access|
|`pdma`|power-division multiple access|

###### The `spreading` Field

The `spreading` field can have the following values:

|value|description|
|----|-------|
|`fhss`|frequency-hopping spread spectrum|
|`thss`|time-hopping spread spectrum|
|`dsss`|direct-sequence spread spectrum|
|`css`|chirp spread spectrum|

###### The `bandwidth` Field

The `bandwidth` field has a float value that describes the channel bandwidth of the signal. Note that this is different from what is reported in the `core` namespace within an annotation, describing the occupied spectrum of a signal, which may or may not be comparable to the actual channel bandwidth of the communications system.

###### The `channel` Field

The `channel` field has an unsigned integer value that describes the channel number of the signal within the communication system.

###### The `class_variant` Field

The `class_variant` field describes any modifier to the modulation class not covered by any of the other fields. Examples include pi/4-DQPSK and GMSK.

## Examples

Here is an example of a relatively simple modulation label, which describes a 10 kHz FM signal using time-division duplexing:
```json
{
    [...]
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 500000,
        "signal:emission": {
            "label": "FM TDD",
            "detail": {
                "type": "analog",
                "class": "fm",
                "duplexing": "tdd",
                "bandwidth": 10000.0
            }
        }
    }]
}
```

Another simple example, this time with an emitter object:
```json
{
    [...]
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 1000000,
        "signal:emission": {
            "label": "wifi",
            "detail": {
                "type": "digital",
                "standard": "802.11ac",
                "channel": 8
            },
            "emitter": {
                "seid": 1,
                "manufacturer": "linksys",
                "latitude": 0.000,
                "longitude": 0.000
            }
        }
    }]
}
```
Here is a more complex example that describes an LTE 5 MHz SC-OFDMA downlink:
```json
{
    [...]
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 2500000,
        "signal:emission": {
            "label": "LTE 12",
            "detail": {
                "type": "digital",
                "class": "qam",
                "carrier_variant": "single_carrier",
                "order": 16,
                "multiple_access": "ofdma",
                "bandwidth": 5000000.0,
                "system": "LTE Release 12"
            }
        }
    }]
}
```
A class variant example describing a pi/4-DQPSK signal
```json
{
    [...]
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 1000000,
        "signal:emission": {
            "label": "pi/4-DQPSK",
            "detail": {
                "type": "digital",
                "class": "psk",
                "order": 4,
                "symbol_variant": "differential",
                "class_variant": "pi/4"
            }
        }
    }]
}
```
