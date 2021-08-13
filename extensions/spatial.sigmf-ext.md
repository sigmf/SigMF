# The `spatial` SigMF Extension Namespace v0.0.1

This document defines the `spatial` extension namespace for the Signal Metadata
Format (SigMF) specification. This extension namespace contains objects to help
store information about spatially diverse data, specifically information applied
to multichannel phase-coherent datasets used for signal direction of arrival and
beamforming.

This extension uses the objects defined in the `multichannel` extension to
provide mangement for the separate recordings for phase coherent channels. The
use of this extension is required.

The `spatial` extension makes use of cartesian coordinates to define array
geometry, and spherical coordinates for reporting bearings. This, coupled with
the various methods for defining boresights and bearing references can become
complicated rapidly so the union of these two cordinate reference systems (CRS)
is illustrated in Figure 1 below. The ISO 80000-2:2019 compliant cartesian and
spherical systems have a specific relationship with the reported azimuth and
elevation, which use the conventional geospatial definitions (degrees east of
north, and degrees above horizon).

![SigMF Spatial Coordinate Reference System](spatial_crs.png)

**Figure 1 - Spatial Coordinate Reference Systems**

As shown in Figure 1, the boresight of the aperture is defined as being in the
direction of the positive X-axis. Based on this, as an example, a horizontal
uniform linear array aperture would be defined along the Y-axis (see examples
section below).

## 0 Datatypes

This extension defines the following datatypes:

|type|long-form name|description|
|----|--------------|-----------|
|bearing|signal direction bearing|Quantitative representation of a direction|

The `bearing` field is used to describe relative one or two dimensional signal
directions. The units are always in degrees; while it is legal for this field to
have any value it is recommended that it be between 0 and 360 or +/- 180. This
type has several possible representations:

- If this object is scalar, it represents an azimuth in degrees as a single
floating point value.
- Otherwise the object must be of the `bearing` type:

```json
  "bearing_object": {
    "azimuth": 211.2,
    "elevation": 15.0,
    "az_error": 0.1,
    "el_error": 0.1
  }
```

### 0.1 The Bearing Object

|name|required|type|units|description|
|----|--------|----|-----|-----------|
|`azimuth`|false|float|degrees|Azimuth component of the direction in degrees increasing clockwise.|
|`elevation`|false|float|degrees|Elevation component of the direction in degrees above horizon.|
|`az_error`|false|float|degrees|Error or uncertainty in the azimuth component.|
|`el_error`|false|float|degrees|Error or uncertainty in the azimuth component.|

The `az_error` and `el_error` fields must only be used if `azimuth` or
`elevation` respectively are specified.

## 1 Global

The `spatial` extension adds the following fields to the `global` SigMF object:

|name|required|type|units|description|
|----|--------|----|-----|-----------|
|`num_elements`|true|int|N/A|Defines the number of channels collected in the coherent dataset.|

The number of elements must be directly specified here and is constant for a
given dataset. It may be tempting to use the `core:num_channels` field however
that has a specific purpose related to interleaved data and is not a substitute.

## 2 Captures

The `spatial` extension adds the following fields to `captures` segment objects:

|name|required|type|units|description|
|----|--------|----|-----|-----------|
|`element_geometry`|true|array|meters|Defines the relative arrangement of the array.|
|`aperture_bearing`|false|bearing|degrees|Bearing of aperture boresight in this segment.|
|`emitter_bearing`|false|bearing|degrees|Bearing of signals in this segment.|

The `element_geometry` object must be included in each `captures` segment if the
`spatial` extension is used, and defines the position of the phase centers of
the array elements relative to the electrical phase center of the overall array.
The value must be an array, usually of length `num_elements` with each element
of this array being a three-element array representing an X, Y, Z cartesian
coordinate. Because the element phase centers can change with frequency, this
value is defined specifically for each segment in the `captures` object.

There are two special cases for the `element_geometry` field. If data contained
only references a single single phase center aperture, as may be the case with
a normal directional antenna, this value should be [[0,0,0]]. If the element
geometry is unknown, this value may be defined as an empty array [] - this is a
very niche use case and generally this field should be defined. 

The `aperture_bearing` field within a `captures` segment can be used to specify
a fixed aperture boresight bearing. For single element or uniform planar array
apertures, the boresight is defined as the direction of peak gain when fed with
a uniform phase signal; for more complicated arrays this value is determined by
antenna mechanical or electrical geometry and will be specific to the design.
The azimuth is specified in degrees east of true north and if provided elevation
is in degrees above the horizon.

The `emitter_bearing` field within a `captures` segment can be used to specify
the ground truth bearing of all signals contained within a multichannel dataset
relative to the `aperture_bearing`. This is useful for reference data which is
well controlled, but is not well suited for arbitrary signals or data with more
than one emitter location.

## 3 Annotations

This extension adds the following optional fields to the `annotations` SigMF
object:

|name|required|type|description|
|----|--------|----|-----------|
|`signal_bearing`|false|bearing|Bearing associated with the specific annotation.|

The `signal_bearing` field represents the bearing of a specific signal relative
to the `aperture_bearing`, and can be utilized when the `captures` segment
`bearing` field is insufficient to define a dataset such as when signals
contained originate from a variety of bearings.

## 4 Examples

Here is an example of how the `global` and captures fields can be specified for
a 4 element uniform linear array with element spacing of 20cm pointed due west.
```json
{
  "global": {
    "core:datatype": "ci16_le",
    "core:sample_rate": 40000000,
    "antenna:gain": 0,
    "spatial:num_elements": 4
  },
  "captures": [
    {
      "core:sample_start": 0,
      "core:frequency": 740000000.0,
      "spatial:element_geometry": [[0,0.3,0],[0,0.1,0],[0,-0.1,0],[0,-0.3,0]],
      "spatial:aperture_bearing": 270
    }
  ],
  ...
}
```

This is an example of how to report the observed direction of annotations, in
this case they are originating from the 4 o'clock position:
```json
{
  ...
  "annotations": [
    {
      "core:sample_start": 0,
      "core:sample_count": 50944,
      "core:freq_upper_edge": 2401000000,
      "core:freq_lower_edge": 2402000000,
      "core:description": "burst",
      "spatial:signal_bearing": {
        "azimuth": 120.2,
        "az_error": 0.5
      }
    },
    ...
  ]
}
```

Here is an example of a 6 element uniform planar array pointed approximately due
north that is detecting emissions from an emitter located east north-east from
the aperture (see figure above for reference).
```json
{
  "global": {
    "core:datatype": "ci16_le",
    "core:sample_rate": 40000000,
    "antenna:gain": 6,
    "spatial:num_elements": 6
  },
  "captures": [
    {
      "core:sample_start": 0,
      "core:frequency": 1260000000.0,
      "spatial:element_geometry": [[0,0.1,0.05],[0,0,0.05],[0,-0.1,0.05],[0,0.1,-0.05],[0,0,-0.05],[0,-0.1,-0.05]],
      "spatial:aperture_bearing": 1.13124
    }
  ],
  "annotations": [
    {
      "core:sample_start": 8424351,
      "core:sample_count": 88741,
      "core:freq_upper_edge": 1248111918.0,
      "core:freq_lower_edge": 1245718776.0,
      "core:description": "burst",
      "spatial:signal_bearing": {
        "azimuth": 59.431,
        "elevation": 13.681,
        "az_error": 1.3421,
        "el_error": 4.1192
      }
    },
    {
      "core:sample_start": 13843284,
      "core:sample_count": 96438,
      "core:freq_upper_edge": 1271283241.0,
      "core:freq_lower_edge": 1268532007.0,
      "core:description": "burst",
      "spatial:signal_bearing": {
        "azimuth": 60.994,
        "elevation": 17.324,
        "az_error": 0.9694,
        "el_error": 3.8474
      }
    },
    ...
  ]
}
```

Here is an example of a 4 element aperture with square geometry in the XY plane:
```json
{
  "global": {
    "core:datatype": "ci16_le",
    "core:sample_rate": 40000000,
    "antenna:gain": 6,
    "spatial:num_elements": 6
  },
  "captures": [
    {
      "core:sample_start": 0,
      "core:frequency": 160000000.0,
      "spatial:element_geometry": [[0.25,0.25,0],[0.25,-0.25,0],[-0.25,-0.25,0],[-0.25,0.25,0]],
    }
  ],
  "annotations": [
    {
      "core:sample_start": 38012637,
      "core:sample_count": 100991,
      "core:freq_upper_edge": 165125034.0,
      "core:freq_lower_edge": 165112388.0,
      "spatial:signal_bearing": 202.812,
    },
    {
      "core:sample_start": 780208811,
      "core:sample_count": 100018,
      "core:freq_upper_edge": 165125018.0,
      "core:freq_lower_edge": 165112371.0,
      "spatial:signal_bearing": 200.142,
    },
    {
      "core:sample_start": 118009143,
      "core:sample_count": 99841,
      "core:freq_upper_edge": 165125041.0,
      "core:freq_lower_edge": 165112369.0,
      "spatial:signal_bearing": 197.681,
    },
    {
      "core:sample_start": 158007123,
      "core:sample_count": 101041,
      "core:freq_upper_edge": 165125023.0,
      "core:freq_lower_edge": 165112401.0,
      "spatial:signal_bearing": 195.017,
    },
    ...
  ]
}
```
