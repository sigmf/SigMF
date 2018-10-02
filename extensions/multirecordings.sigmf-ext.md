# Multi-Recordings Extension v0.0.1

This extension makes it possible to link multiple SigMF recordings together to
represent a single data-capture event. This is primarily used for two purposes:
representing aspects of one SigMF recording with another recording, and
capturing multi-channel data.

For some recordings, there are fields that are continuously variable. Examples
include the geolocation of a radio receiver that is on a moving vehicle, the
azimuth of a spinning antenna aperture, and the temperature readings of a
thermal sensor. If these were stored as metadata in the "primary" signal
recording, they would bloat and complicate the use of that recording.
Furthermore, it would be difficult to process any aspect of the data without
parsing all of the recorded data. This extension enables you to treat such
fields as *simply another `SigMF Recording`*.

For recordings that digitize multiple streams of information (e.g., a
phased-array receiver with multiple channels), this extension enables you to
capture the multiple streams and link them such that each one can be treated as
a separate `SigMF Recording` or they may be treated together as one.

Per the SigMF specification, all recordings must be independently evaluated and
be able to stand-alone.

## Datatypes

| type      | long-form name        | description                                             |
| --------- | --------------------- | ------------------------------------------------------- |
| recording | string recording name | A string that indicates the name of a `SigMF Recording` |

The `recording` datatype is the primary mechanism by which SigMF Recordings are
linked. This datatype is the name of a SigMF Recording, **without** extensions
(i.e., given a recording comprising `N.sigmf-meta` and `N.sigmf-data`, the
`recording` datatype value would simply be `N`).

The metadata and dataset files of the recording MUST be in the local directory
(i.e., local to the SigMF Recording in which they are referenced, and thus in
the same SigMF Archive).

### `core` Namespace Support

If the `multirecordings` extension is supported, it MAY be used in the following
name/value pairs within the `core` namespace.

#### Capture Segment Objects

The following are existing name/value pairs in capture segment objects in the
`core` namespace:

| name           | required | type      | description  |
| -------------- | -------- | --------- | ------------ |
| `frequency`    | false    | recording | The center frequency of the signal in Hz.|

### `multirecordings` Namespace

This extension adds the following name/value pairs under the `multirecordings`
namespace.

#### Global Object

| name          | required | type      | description                         |
| ------------- | -------- | --------- | ----------------------------------- |
| `master`      | false    | recording | The primary recording this recording is linked to.|

The `multirecordings:master` field in the `global` object allows the user to
indicate another SigMF recording that acts as the 'master' or 'parent' of this
one, effectively providing a mechanism for bi-directional link between SigMF recordings.

#### Capture Segment Objects

| name           | required | type      | description  |
| -------------- | -------- | --------- | ------------ |
| `streams`      | false    | object    | List of SigMF recordings that represent multiple streams.|

The `multirecordings:streams` field in a capture segment object is a JSON array
of `recording` strings, as defined by this extension, that indicate multiple
streams of data that were captured as part of the same event.

An example of using the `streams` field in a recording called `example-channel-0`:

```json
    ...
    "captures": [
        {
            "core:sample_start": 0,
            "core:frequency": 900000000,
            "core:time": "2017-02-01T11:33:17053240428Z",
            "multirecordings:streams": [
                "example-channel-0",
                "example-channel-1",
                "example-channel-2",
                "example-channel-3"
            ]
        }
    ],
    ...
```

In the example above, the metadata in the only `capture segment object`
indicates that the full data capture event consists of four recorded streams,
the first one is "this" recording (`example-channel-0`), and that there are
three other SigMF recordings in the local directory that represent the other
three channels.