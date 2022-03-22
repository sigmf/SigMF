# The `presentation` SigMF Extension Namespace v1.0.0

This document defines the `presentation` extension namespace for the Signal
Metadata Format (SigMF) specification. This extension namespace contains objects
to help define how SigMF metadata should be presented graphically to users.

All fields in the `presentation` extension are optional, thus any SigMF
application using this extension is not required to implement any particular
feature. It is RECOMMENDED that applications adhering to the `presentation`
extension use default values in this document.

## 0 Datatypes

The `presentation` extension defines the following SigMF datatypes:

|type|long-form name|description|
|----|--------------|-----------|
|`color`|Hexadecimal Color String|String representing a 24 bit color (with optional alpha value) in hexadecimal form; either "#RRGGBB" or "#AARRGGBB".|

### 0.1 The `color` datatype

The `color` datatype is a string which MUST be either 6 or 8 hexadecimal
characters long prepended by a "#". It MAY be specified in capital or lower case
characters and applications MUST handle either. The alpha channel is optional,
and while compliant software MUST be able to parse either format presentation of
the alpha channel by visualization software is RECOMMENDED but OPTIONAL. If
software is unable to render the alpha channel then it SHOULD ignore the alpha
value for foreground objects and ignore background objects entirely.

ARGB format was selected over RGBA for compatibility with QColor objects, RGBA
color specification is invalid and will result in incorrect display of content.

For greatest compatibility, it is RECOMMENDED that this value default to
`#00ffffff` (fully opaque white) for foreground features and `#ffffffff` (fully
transparent) for background features.

## 1 Global

The `presentation` extension adds the following fields to the `global` SigMF
object:

|name|required|type|description|
|----|--------|----|-----------|
|`capture_default`|false|`presentation_style`|Default style to be used for captures when a style is not specified.|
|`capture_styles`|false|list of `style_entry`|Color of the fill of the annotation, this is generally used with defined alpha channel.|
|`annotation_default`|false|`presentation_style`|Default style to be used for annotations when a style is not specified.|
|`annotation_styles`|false|list of `style_entry`|Color of the foreground captures segment display features.|

Both `capture_styles` and `annotation_styles` are JSON object containg style
information by short form name. This is a simple mechanism to prevent every
annotation or capture segment from defining these fields repeatedly. These
objects have keys that represent capture segments or annotation `label` fields
they apply to and values consisting of `presentation_style` objects.

In a `capture_styles` object the `key` field MAY be underdetermined if there are
multiple `capture_tags`. The first entry in the `capture_tags` list for which
a `captures_styles` `key` exists SHOULD be used.

Applications implementing this extension will generally parse the `*_styles`
fields into a dictionary for easy reference.

### 1.1 The `style_entry` object

The `presentation_style` object is a JSON dictionary entry and is implemented
for dictionary emulation for efficient serialization:

|name|required|type|description|
|----|--------|----|-----------|
|`key`|true|string|Color of the fill of the annotation, this is generally used with defined alpha channel.|
|`style`|true|`presentation_style`|Color of the fill of the annotation, this is generally used with defined alpha channel.|

### 1.2 The `presentation_style` object

The `presentation_style` object is a JSON object where each value is an object with
the following form:

|name|required|type|default|description|
|----|--------|----|-------|-----------|
|`display_type`|true|`display_type`||Color of the fill of the annotation, this is generally used with defined alpha channel.|
|`line_color`|false|color|`#00ffffff`|Color of the foreground captures segment display features.|
|`line_width`|false|double|1.0|Width of the line (in pixels) surrounding the annotation, fractional values are permitted.|
|`fill_color`|false|color|`#ffffffff`|Color of the background, generally used with significant alpha.|
|`comment`|false|string||User comment field, any string is fine.|

The `key` and `display_type` fields are required for all `presentation_style`
objects. When describing a capture segment, the `key` field refers only to the
first key in the captures list.

### 1.1.1 The `display_type` field

The `display_type` field can have the following values:

|value|description|
|----|-------|
|`none`|Do not apply special presentation to this segment, all other fields are ignored.|
|`box`|Apply a box of `line_color` and `line_width` enclosing defined samples, with background `fill_color` (if defined).|
|`diagonal`|Fill the boxed segment with the specified `fill_color` and apply diagonal `line_color` lines to the foreground.|
|`grayscale`|This captures segment should be rendered completely desaturated, other fields are ignored.|
|`point`|Single circle of diameter `line_width` at the center frequency and first sample position. Valid only for annotations.|
|`impulse`|Line covering the entire spectral range at the first sample position. Valid only for annotations.|

## 2 Captures

The `presentation` extension adds the following fields to the `captures` SigMF
object:

|name|required|type|default|description|
|----|--------|----|-------|-----------|
|`style`|false|[presentation style](presentation.sigmf-ext.md#the-presentation-style-field)|{}|Style to use for the segment.|

## 3 Annotations

The `presentation` extension adds the following fields to the `annotations`
SigMF object:

|name|required|type|default|description|
|----|--------|----|-------|-----------|
|`style`|false|[presentation style](presentation.sigmf-ext.md#the-presentation-style-field)|{}|Style to use for the annotation.|
|`color`|false|`color`|`0x00ffffff`|Simple specification for the annotation box color.|

The `color` and `style` fields SHOULD NOT both be provided. In the event of an
overdetermined specification for color, the first specification found below
should be used to determine the appropriate presentation style:

1. `annotations->presentation:style`
1. `annotations->presentation:color`
1. `global->presentation:annotation_styles`[`annotations->core:label`]
1. default (white box)

## 4 Examples

Example usage of the simple presentation specification, in this case specifying
different box colors (red, then green) in the annotations directly:
```json
  ...
  "annotations": [
    {
      "core:sample_start": 1000,
      "core:sample_count": 100,
      "core:label": "signal1",
      "core:freq_lower_edge": 119000000,
      "core:freq_upper_edge": 120000000,
      "presentation:color": "#00ff0000"
    },
    {
      "core:sample_start": 5000,
      "core:sample_count": 100,
      "core:label": "signal2",
      "core:freq_lower_edge": 119000000,
      "core:freq_upper_edge": 120000000,
      "presentation:color": "#0000ff00"
    },
  ]
```

How to use `capture_styles` or `annotation_styles` to specify the same two
annotations above:
```json
  "global": {
    ...
    "presentation:capture_styles": [
      {
        "key": "VALID",
        "style": {
          "display_type": "none",
          "comment": "Valid capture segments have no unique presentation."
        }
      },
      {
        "key": "INVALID",
        "stye": {
          "display_type": "diagonal"
          "line_color": "#80ffff00",
          "line_width": "3.0",
          "fill_color": "#c0000000",
          "comment": "Invalid sections are shaded slightly grey with yellow diagonal lines."
        }
      }
    ],
    "presentation:annotation_styles": [
      {
        "key": "signal1",
        "style": {
          "display_type": "box",
          "line_color": "#00ff0000",
          "comment": "Box signals labeled 'signal1' in RED."
        }
      },
      {
        "key": "signal2",
        "style": {
          "display_type": "box",
          "line_color": "#0000ff00",
          "comment": "Box signals labeled 'signal1' in GREEN."
        }
      }
    ]
  },
  "captures": [
    {
      "core:sample_start": 0,
      "core:capture_tags": ["VALID"],
      "core:frequency": 100000000.0
    },
    {
      "core:sample_start": 100000,
      "core:capture_tags": ["INVALID","SATURATION"],
      "core:frequency": 100000000.0
    }
    {
      "core:sample_start": 101000,
      "core:capture_tags": ["VALID"],
      "core:frequency": 100000000.0
    }
  ],
  "annotations": [
    {
      "core:sample_start": 1000,
      "core:sample_count": 100,
      "core:label": "signal1",
      "core:freq_lower_edge": 119000000,
      "core:freq_upper_edge": 120000000
    },
    {
      "core:sample_start": 5000,
      "core:sample_count": 100,
      "core:label": "signal2",
      "core:freq_lower_edge": 119000000,
      "core:freq_upper_edge": 120000000
    },
  ]
```

