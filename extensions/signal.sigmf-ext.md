# The `signal` SigMF Extension Namespace v1.0.0

This document defines the `signal` extension namespace for the Signal Metadata
Format (SigMF) specification. This extension namespace defines how to describe
the attributes of wireless communications signals and their emitters.

## 1 Global

`signal` does not extend [Global](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#global-object).

## 2 Captures

`signal` does not extend [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array).


## 3 Annotations

This extension adds the following optional field to the `annotations` global SigMF object:

|name|required|type|description|
|----|--------------|-------|----------|
|`detail`|false|[Detail](signal.sigmf-ext.md#the-detail-object)|Emission details (standard, modulation, etc.)|
|`emitter`|false|[Emitter](signal.sigmf-ext.md#the-emitter-object)|Emitter details (manufacturer, geo coordinates, etc.)|

The field of communications is vast, and there may be communications systems
that cannot be described using the names and fields described in this extension.
If you need additional or different fields to describe a system, create a new
extension that adds the necessary fields to the `signal` namespace and/or submit
the new fields to be upstreamed into this canonical extension.

### 3.1 The Detail Object

|name|required|type|description|
|----|--------|----|-----------|
|`type`|false|string|[type](signal.sigmf-ext.md#the-type-field)|
|`mod_class`|false|string|[mod_class](signal.sigmf-ext.md#the-mod_class-field)|
|`standard`|false|string|Communication standard (e.g., 802.11ac)|
|`carrier_variant`|false|string|[carrier variant](signal.sigmf-ext.md#the-carrier_variant-field)|
|`symbol_variant`|false|string|[symbol variant](signal.sigmf-ext.md#the-symbol_variant-field)|
|`order`|false|uint|[order](signal.sigmf-ext.md#the-order-field)|
|`duplexing`|false|string|[duplexing](signal.sigmf-ext.md#the-duplexing-field)|
|`multiplexing`|false|string|[multiplexing](signal.sigmf-ext.md#the-multiplexing-field)|
|`multiple_access`|false|string|[multiple access](signal.sigmf-ext.md#the-multiple_access-field)|
|`spreading`|false|string|[spreading](signal.sigmf-ext.md#the-spreading-field)|
|`channel_bw`|false|float|[bandwidth](signal.sigmf-ext.md#the-bandwidth-field)|
|`channel`|false|uint|[channel](signal.sigmf-ext.md#the-channel-field)|
|`class_variant`|false|string|[class variant](signal.sigmf-ext.md#the-class_variant-field)|

#### 3.1.1 The `type` Field

The `type` field can have the following values:

|value|description|
|----|-------|
|`analog`|analog modulation scheme|
|`digital`|digital modulation scheme|

#### 3.1.2 The `mod_class` Field

The `mod_class` field can have the following values:

|value|description|
|----|-------|
|`am`|(analog) amplitude modulation|
|`fm`|(analog) frequency modulation|
|`pm`|(analog) phase modulation|
|`ssb`|single side-band|
|`dsb`|dual side-band|
|`vsb`|vestigial side-band|
|`ask`|amplitude-shift keying|
|`fsk`|frequency-shift keying|
|`psk`|phase-shift keying|
|`qam`|quadrature-amplitude modulation|
|`ook`|on-off keying|
|`cpm`|continuous phase modulation|
|`msk`|minimum-shift keying|

#### 3.1.3 The `carrier_variant` Field

The `carrier_variant` field can have the following values:

|value|description|
|----|----|-------|
|`with_carrier`|with-carrier modulation|
|`suppressed_carrier`|suppressed-carrier modulation|
|`reduced_carrier`|reduced-carrier modulation|
|`single_carrier`|single-carrier modulation|
|`multi_carrier`|multi-carrier modulation|

#### 3.1.4 The `symbol_variant` Field

The `symbol_variant` field can have the following values:

|value|description|
|----|----|-------|
|`differential`|differential modulation|
|`offset`|offset modulation (sometimes called 'staggered')|

#### 3.1.5 The `order` Field

The `order` field has an unsigned integer value that describes the modulation
order, which typically refers to the number of symbols or states in a digital
modulation (e.g., QAM64 has 64 symbols, QPSK has 4 symbols).

#### 3.1.6 The `duplexing` Field

The `duplexing` field can have the following values:

|value|description|
|----|-------|
|`tdd`|time-division duplexing|
|`fdd`|frequency-division duplexing|

#### 3.1.7 The `multiplexing` Field

The `multiplexing` field can have the following values:

|value|description|
|----|-------|
|`tdm`|time-division multiplexing|
|`fdm`|frequency-division multiplexing|
|`cdm`|code-division multiplexing|
|`ofdm`|orthogonal frequency-division multiplexing|
|`sdm`|space-division multiplexing|
|`pdm`|polarization-division multiplexing|

#### 3.1.8 The `multiple_access` Field

The `multiple_access` field can have the following values:

|value|description|
|----|-------|
|`fdma`|frequency-division multiple access|
|`ofdma`|orthogonal frequency-division multiple access|
|`tdma`|time-division multiple access|
|`cdma`|code-division multiple access|
|`sdma`|space-division multiple access|
|`pdma`|power-division multiple access|

#### 3.1.9 The `spreading` Field

The `spreading` field can have the following values:

|value|description|
|----|-------|
|`fhss`|frequency-hopping spread spectrum|
|`thss`|time-hopping spread spectrum|
|`dsss`|direct-sequence spread spectrum|
|`css`|chirp spread spectrum|

#### 3.1.10 The `bandwidth` Field

The `channel_bw` field has a float value that describes the channel bandwidth of
the signal. Note that this is different from what may be reported in the `core`
namespace within an annotation which describes the occupied spectrum of a
signal, which may or may not be comparable to the actual channel bandwidth of
the communications system.

#### 3.1.11 The `channel` Field

The `channel` field has an unsigned integer value that describes the channel
number of the signal within the communication system.

#### 3.1.12 The `class_variant` Field

The `class_variant` field describes any modifier to the modulation class not
covered by any of the other fields. Examples include pi/4-DQPSK and GMSK.

### 3.2 The Emitter Object

|name|required|type|description|
|----|--------|----|-----------|
|`seid`|false|uint|Unique ID of the emitter|
|`manufacturer`|false|string|Manufacturer of the hardware used to emit the signal|
|`power_tx`|false|double|Total transmitted power by the emitter (dBm)|
|`power_eirp`|false|double|Effective Isotropic Radiated Power in the direction of the receiver (dBm)|
|`geolocation`|false|GeoJSON|Location of the emitter hardware|

## 4 Examples

Here is an example of a relatively simple modulation label, which describes a
10 kHz FM signal using time-division duplexing:
```json
{
    ...
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 500000,
        "core:label": "FM TDD",
        "signal:detail": {
            "type": "analog",
            "mod_class": "fm",
            "duplexing": "tdd",
            "bandwidth": 10000.0
        }
    }]
}
```

Another simple example, this time with an emitter object:
```json
{
    ...
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 1000000,
        "core:label": "WIFI",
        "signal:detail": {
            "type": "digital",
            "standard": "802.11ac",
            "channel": 8
        },
        "signal:emitter": {
            "seid": 1,
            "manufacturer": "linksys",
            "power_tx": 27.0
        }
    }]
}
```
Here is a more complex example that describes an LTE 5 MHz SC-OFDMA downlink:
```json
{
    ...
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 2500000,
        "core:label": "LTE 12",
        "signal:detail": {
            "type": "digital",
            "mod_class": "qam",
            "carrier_variant": "single_carrier",
            "order": 16,
            "multiple_access": "ofdma",
            "bandwidth": 5000000.0,
            "system": "LTE Release 12"
        }
    }]
}
```
A class variant example describing a pi/4-DQPSK signal:
```json
{
    ...
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 1000000,
        "core:label": "pi/4-DQPSK",
        "signal:detail": {
            "type": "digital",
            "mod_class": "psk",
            "order": 4,
            "symbol_variant": "differential",
            "class_variant": "pi/4"
        }
    }]
}
```
An example describing just the ID, power, and location of an emitter:
```json
{
    ...
    "annotations": [{
        "core:sample_start": 0,
        "core:sample_count": 1000000,
        "core:label": "5G-NR",
        "signal:emitter": {
            "seid": 5428604929,
            "power_eirp": 43.0,
            "geolocation": {
                "type": "point",
                "coordinates": [-77.071651, 38.897397]
            }
        }
    }]
}
```
