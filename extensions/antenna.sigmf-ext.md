# Antenna Extension v1.0.0

The `antenna` namespace extension defines static antenna parameters extending the `global` and `annotations` objects in SigMF Recordings, and the `collection` object in a SigMF Collection.

# SigMF Recordings

The following fields are specified for SigMF Recordings.

## 1 Global

The following names are specified in the `antenna` namespace and should be used in the `global` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`model`|true|string|N/A|Antenna make and model number. E.g. `"ARA CSB-16"`, `"L-com HG3512UP-NF"`.|
|`type`|false|string|N/A|Antenna type. E.g. `"dipole"`, `"biconical"`, `"monopole"`, `"conical monopole"`.|
|`low_frequency`|false|float|Hz|Low frequency of operational range.|
|`high_frequency`|false|float|Hz|High frequency of operational range.|
|`gain`|false|float|dBi|Antenna gain in direction of maximum radiation or reception.|
|`horizontal_gain_pattern`|false|float array|dBi|Antenna gain pattern in horizontal plane from 0 to 359 degrees in 1 degree steps.|
|`vertical_gain_pattern`|false|float array|dBi|Antenna gain pattern in vertical plane from -90 to +90 degrees in 1 degree steps.|
|`horizontal_beam_width`|false|float|degrees|Horizontal 3-dB beamwidth.|
|`vertical_beam_width`|false|float|degrees|Vertical 3-dB beamwidth.|
|`cross_polar_discrimination`|false|float|N/A|Cross-polarization discrimination.|
|`voltage_standing_wave_ratio`|false|float|volts|Voltage standing wave ratio.|
|`cable_loss`|false|float|dB|Cable loss for cable connecting antenna and preselector.|
|`steerable`|false|boolean|N/A|Defines if the antenna is steerable or not.|
|`mobile`|false|boolean|N/A|Defines if the antenna is mobile or not.|
|`hagl`|false|double|meters|Antenna phase center height above ground level.|

## 2 Captures

`antenna` does not extend [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array).

## 3 Annotations

The following names are specified in the `antenna` namespace and should be used in the `annotations` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`azimuth_angle`|false|float|degrees|Angle of main beam in azimuthal plane from North.|
|`elevation_angle`|false|float|degrees|Angle of main beam in elevation plane from horizontal.|
|`polarization`|false|float|string|E.g. `"vertical"`, `"horizontal"`, `"slant-45"`, `"left-hand circular"`, `"right-hand circular"`.|

## 4 Collection

The following fields are specificed in SigMF Collections.

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`azimuth_angle`|false|float|degrees|Angle of main beam in azimuthal plane from North.|
|`elevation_angle`|false|float|degrees|Angle of main beam in elevation plane from horizontal.|
|`hagl`|false|SigMF Recording Tuple|Antenna height above ground level (in meters).|

## 5 Examples

No `antenna` examples.

