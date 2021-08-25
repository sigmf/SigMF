# The `multirecordings` SigMF Extension Namespace v0.1.0

This extension makes it possible to link multiple SigMF recordings together to
represent a single data-capture event. This is primarily used for two purposes:
representing dynamic aspects of one SigMF recording and
capturing multi-channel data.

For recordings that digitize multiple streams of information (e.g., a
phased-array receiver with multiple channels), this extension enables you to
capture the multiple streams and link them such that each one can be treated as
a separate `SigMF Recording` or they may be treated together as one.

For some recordings, there are fields that are continuously variable. Examples
include the geolocation of a radio receiver that is on a moving vehicle, the
azimuth of a spinning antenna aperture, and the temperature readings of a
thermal sensor. If these were stored as metadata in the "primary" signal
recording, they would bloat and complicate the use of that recording.
Furthermore, it would be difficult to process any aspect of the data without
parsing all of the recorded data. This extension enables you to treat such
fields as *simply another `SigMF Recording`*.

Per the SigMF specification, all recordings must be independently evaluated and
be able to stand-alone as compliant recordings.

## 0 Datatypes

| type      | long-form name        | description                                             |
| --------- | --------------------- | ------------------------------------------------------- |
| recording | string recording name | A string that indicates the name of a `SigMF Recording` |

The `recording` datatype is the primary mechanism by which SigMF Recordings are
linked. This datatype is the string name of a SigMF Recording, **without** filename extensions
(i.e., given a recording comprising `N.sigmf-meta` and `N.sigmf-data`, the
`recording` datatype value would simply be `N`).

This datatype may take the place of any non-string datatype in a metadata file. The presence of string filename then indicates that particular field in the recording is described by another recording with the base name in the string.

The second recording (both metadata and dataset files) MUST be in the same directory
(i.e., local to the SigMF Recording in which they are referenced, and thus in
the same SigMF Archive).

## 1 Global

This extension adds the following optional fields to the `Global` object.

| name          | required | type      | description                         |
| ------------- | -------- | --------- | ----------------------------------- |
| `primary`     | false    | recording | The primary recording this recording is linked to.|
| `channel`     | false    | uint      | The channel index of this recording.|
| `streams`     | false    | object    | List of SigMF recordings that represent multiple streams.|

### The `primary` field

The `multirecordings:primary` field in the `global` object allows the user to
indicate another SigMF recording that acts as the 'primary' or 'parent' of this
one, effectively providing a mechanism for bi-directional link between SigMF recordings.

If omitted, it is assumed that this file is the primary.

### The `channel` field

In recordings with multiple channels (e.g., phased arrays), this field is used to indicate the channel number of this specific recording.

### The `streams` field

The `multirecordings:streams` field is a JSON array
of `recording` strings, as defined by this extension, that indicate multiple
streams of data that were captured as part of the same event.

This field MUST only appear in the `primary` recording's metadata file.

## 2 Captures

This extension does not extend `captures`.

## 3 Annotations

This extension does not extend `annotations`.

## 4 Examples


### 4.1 Example of a 2-channel MIMO archive

File: `example-0.sigmf-meta`
```json
{
    "global": {
        "core:datatype": "i16_le",
        "core:version": "1.0.0",
        "core:extensions" : {
            "multirecordings": "v0.1.0"
        },
        "multirecordings:streams": [
            "example-channel-0",
            "example-channel-1",
        ],
        "multirecordings:channel": 0
    },
    "captures": [
        {
            "core:sample_start": 0
        }
    ],
    "annotations": []
}
```

File: `example-1.sigmf-meta`
```json
{
    "global": {
        "core:datatype": "i16_le",
        "core:version": "1.0.0",
        "core:extensions" : {
            "multirecordings": "v0.1.0"
        },
        "multirecordings:channel": 1,
        "multirecordings:primary": "example-0"
    },
    "captures": [
        {
            "core:sample_start": 0
        }
    ],
    "annotations": []
}
```