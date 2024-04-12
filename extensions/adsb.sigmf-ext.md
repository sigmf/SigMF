# ADS-B Extension v1.0.0

The Automatic Dependent Surveillance-Broadcast (`adsb`) namespace extension
defines dynamic properties of ADS-B signals extending `annotations`.

## 1 Global

`adsb` does not extend [Global](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#global-object).

## 2 Captures

`signal` does not extend [Captures](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#captures-array).

## 3 Annotations

The following names are specified in the `adsb` namespace and should be used in
the `annotations` object:

|name|required|type|unit|description|
|----|--------|----|----|-----------|
|`downlink_format`|true|int|N/A|Indicates if an ADS-B signal is a Mode S Short (11) or a Mode S Extended (17) signal.|
|`message_type`|true|int|N/A|Indicates the type of data in a Mode S Extended signal.  The message type code range is from 0 to 31. The type of messages are aircraft identification (1-4), surface position (5-8), airborne position with barometric (9-18), airborne velocities (19), airborne position with GNSS (20-22), testing (23), reserved (24-27, 30), Emergency/Airborne Collision Avoidance System (ACAS) status (28), trajectory change (29), and aircraft operational status (31).  A signal with a Mode S Short downlink format does not contains a message and is represented by 0.
|`ICA_address`|true|double|N/A|The International Civil Aviation Organization (ICAO) address of the ADS-B signal.|
|`binary`|true|string|N/A|The binary signal, either 56 bits (Mode S Short) or 112 bits (Mode S Extended).|

## 4 Examples

No `adsb` examples.
