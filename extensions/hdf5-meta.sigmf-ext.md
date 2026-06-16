# The `hdf5-meta` SigMF Extension Namespace v1.0.0

This document defines the `hdf5-meta` extension namespace for the Signal
Metadata Format (SigMF) specification. This extension defines an OPTIONAL HDF5
sidecar file that stores a performance-optimized, columnar duplicate of a
Recording's SigMF metadata. The sidecar enables substantially faster load times
and smaller on-disk metadata for Recordings with large numbers of `captures` or
`annotations`, while preserving full backwards compatibility with tools that do
not implement this extension.

The `.sigmf-meta` JSON file remains the complete, authoritative, and SigMF
Compliant source of truth. The HDF5 sidecar is a derived cache: it MUST contain
content equivalent to the JSON Metadata file, and it MUST NOT be required in
order to read a Recording. Tools that do not understand `hdf5-meta` ignore the
extension fields and read the JSON exactly as they do today.

## 0 Motivation

SigMF Metadata is stored as JSON, which is human-readable and portable but does
not scale efficiently to Recordings with very large `annotations` or `captures`
arrays (common in some RF survey, machine-learning, and signal-detection
workflows). JSON repeats every field name in every object, is parsed serially,
and is row-oriented, which prevents columnar access.

This extension addresses that by writing the `captures` and `annotations`
arrays as columnar HDF5 datasets (one column per field) and the `global` object
as HDF5 attributes. Field names are stored once per column rather than once per
object, the data is stored in native binary types, and datasets MAY be
compressed. Tools that implement this extension MAY read the sidecar instead of
parsing the JSON arrays, then fall back to the JSON file whenever the sidecar is
absent, unreadable, or stale.

### 0.1 Scope and Non-Goals

This extension is deliberately scoped to **metadata only**. To avoid confusion
with the several other roles HDF5 commonly plays in RF and array workflows, the
following are explicit non-goals:

1. **It is not a sample-data container.** The sidecar duplicates only the
   `global`, `captures`, and `annotations` Metadata. It does not store, replace,
   or reference IQ/sample data, and it has no relationship to the
   `.sigmf-data` Dataset file. Sample data continues to live in the SigMF
   Dataset exactly as specified by Core.
2. **It does not represent multiple channels or arrays.** SigMF already handles
   multichannel data two ways — interleaved samples in a single Recording via
   `core:num_channels`, and multiple channels of IQ data (e.g., array
   processing) via [SigMF Collections](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#sigmf-collection-format),
   where each channel is a separate Recording tied together by a
   `.sigmf-collection` file. This extension changes neither mechanism. A
   `core:num_channels` value is carried through as an ordinary `global` field,
   and because the cache is per-Recording-metadata it composes with Collections
   without modification: each member Recording MAY carry its own sidecar, and
   the Collection file itself needs none.
3. **It does not change the SigMF data model or add Metadata fields.** No fields
   are added to `captures` or `annotations`, and the JSON Metadata file remains
   the complete, authoritative, SigMF Compliant source of truth.

In short, `hdf5-meta` is a performance cache for metadata-heavy Recordings, not
a data format, an array format, or an alternative to Collections. Using HDF5 as
a container for the sample data of an array is a separate concern that would
warrant its own proposal.

## 1 Global

`hdf5-meta` extends the [Global](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#global-object) object.

The following names are specified in the `hdf5-meta` namespace and should be
used in the `global` object:

|name|required|type|description|
|----|--------|----|-----------|
|`file`|true|string|Filename of the HDF5 sidecar file, relative to the directory containing the `.sigmf-meta` file. It is RECOMMENDED that this be the Metadata filename with an `.h5` suffix appended (e.g., `recording.sigmf-meta.h5`).|
|`version`|false|string|Version of the `hdf5-meta` extension that the sidecar conforms to, using [Semantic Versioning](https://semver.org). Defaults to the version declared for `hdf5-meta` in `core:extensions` when omitted.|

A Recording using this extension MUST list `hdf5-meta` in the `core:extensions`
array. Because the sidecar is OPTIONAL by design, the extension entry SHOULD be
marked `"optional": true` so that the absence of the sidecar (or of HDF5 support
in a reading tool) does not render the Recording non-compliant.

## 2 Captures

`hdf5-meta` does not add any fields to the [Captures](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#captures-array) array in the JSON Metadata file.

The contents of the `captures` array are duplicated into the HDF5 sidecar as
described in [Section 4](#4-hdf5-sidecar-structure).

## 3 Annotations

`hdf5-meta` does not add any fields to the [Annotations](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#annotations-object) array in the JSON Metadata file.

The contents of the `annotations` array are duplicated into the HDF5 sidecar as
described in [Section 4](#4-hdf5-sidecar-structure).

## 4 HDF5 Sidecar Structure

The HDF5 sidecar file mirrors the three top-level SigMF Objects. A reader that
loads the sidecar MUST be able to reconstruct a Metadata Object equivalent to
the JSON Metadata file from the structure below.

```
recording.sigmf-meta.h5
│
├── Attributes (root group "/")
│   ├── sigmf_version     : core:version of the Recording (string)
│   └── hdf5_meta_version : version of this extension (string)
│
├── /global  (group)
│   └── Attributes: one per global key/value pair (see 4.1)
│       ├── core.datatype     : "cf32_le"
│       ├── core.sample_rate  : 1000000.0
│       ├── core.version      : "1.2.0"
│       └── <namespace.field> : <value>
│
├── /captures  (dataset, columnar structured array, present iff captures exist)
│       columns: core.sample_start (int64), core.frequency (float64), ...
│
└── /annotations  (dataset, columnar structured array, present iff annotations exist)
        columns: core.sample_start (int64), core.sample_count (int64),
                 core.label (string), core.freq_lower_edge (float64), ...
```

Requirements:

1. The sidecar MUST be a valid HDF5 file written with HDF5 library version
   1.10 or later.
2. The root group MUST contain the `sigmf_version` and `hdf5_meta_version`
   string attributes.
3. The sidecar MUST contain a `/global` group whose attributes represent every
   key/value pair in the JSON `global` object.
4. The sidecar MUST contain a `/captures` dataset if and only if the JSON
   `captures` array is non-empty.
5. The sidecar MUST contain an `/annotations` dataset if and only if the JSON
   `annotations` array is non-empty.
6. Datasets SHOULD be stored with `gzip` compression.
7. Namespaced field names MUST use dot notation in the sidecar (e.g.,
   `core.sample_start`), not the colon notation used in JSON
   (`core:sample_start`). The colon has reserved meaning in some HDF5 tooling;
   the dot is broadly portable. Readers MUST reverse this mapping (replace the
   first `.` after the namespace with `:`) when reconstructing JSON field names.

### 4.1 Global Object Mapping

Each key/value pair in the JSON `global` object is stored as one attribute on
the `/global` group, with the field name converted to dot notation. Scalar
values (string, integer, number, boolean) are stored as native HDF5 attribute
types per [Section 4.3](#43-datatype-mapping). Values that are JSON arrays or
objects (for example `core:extensions`, or any GeoJSON value) MUST be stored as
a JSON-encoded string attribute and decoded by the reader. Keys whose value is
`null` are omitted.

### 4.2 Captures and Annotations Mapping

The `captures` and `annotations` arrays are each stored as a one-dimensional
HDF5 dataset of a compound (structured) type, i.e. columnar layout: each field
that appears in any element of the array becomes one named column.

1. The set of columns MUST be the union of all field names present across all
   elements of the array. SigMF permits each segment to carry a different set
   of fields, so readers MUST NOT assume every element populates every column.
2. Rows MUST be stored in the same order as the corresponding JSON array so
   that array indices are preserved.
3. The column datatype is determined per [Section 4.3](#43-datatype-mapping).
   When a field is absent from a given element, or its value is `null`, that
   row's cell MUST carry a sentinel that the reader interprets as "field not
   present": `NaN` for floating-point columns, and an empty string for string
   columns. Readers MUST omit such fields when reconstructing the JSON element
   rather than emitting the sentinel value.
4. Object- or array-valued fields (for example a `signal:detail` object) MUST
   be stored as a JSON-encoded string column and decoded by the reader.

Because the sentinel-based reconstruction in rule 3 is lossy for some types
(e.g. it cannot distinguish an absent integer from a present one), writers MAY
promote a column that mixes present and absent values to a JSON-encoded string
column to guarantee an exact round-trip. Readers MUST support both encodings.

### 4.3 Datatype Mapping

| SigMF JSON Type | HDF5 Representation |
|-----------------|--------------------|
| string | Variable-length UTF-8 string, or fixed-length UTF-8 bytes |
| integer (`int`/`uint`) | 64-bit signed integer (`<i8`) |
| number (`double`) | 64-bit IEEE-754 float (`<f8`) |
| boolean | 8-bit integer (`0` = false, `1` = true) |
| null | Field omitted (global) or sentinel cell (captures/annotations) |
| array | JSON-encoded UTF-8 string |
| object | JSON-encoded UTF-8 string |
| GeoJSON | JSON-encoded UTF-8 string |

## 5 Reading and Writing

### 5.1 Reader Behavior

A tool that implements `hdf5-meta` SHOULD use the following algorithm:

1. Read and parse the `.sigmf-meta` JSON file (REQUIRED for compatibility).
2. If `hdf5-meta:file` is present, resolve it relative to the Metadata file's
   directory.
3. If the sidecar exists, is readable, and the tool supports HDF5, the tool MAY
   load `global`, `captures`, and `annotations` from the sidecar instead of
   from the JSON arrays.
4. Otherwise, the tool MUST fall back to the JSON Metadata file. A missing or
   unreadable sidecar is NOT an error.

Because the JSON file is authoritative, a reader that detects a conflict between
the JSON file and the sidecar SHOULD prefer the JSON file and SHOULD warn the
user that the sidecar is stale.

### 5.2 Writer Behavior

A tool that writes the sidecar MUST:

1. Write the complete, SigMF Compliant `.sigmf-meta` JSON file as usual.
2. Add `hdf5-meta` to `core:extensions` (RECOMMENDED `"optional": true`) and set
   `hdf5-meta:file` in the `global` object to the sidecar filename.
3. Write the sidecar containing content equivalent to the JSON file.

Writers SHOULD treat the JSON file as authoritative and regenerate the sidecar
whenever the JSON Metadata changes, so that the two never diverge.

## 6 Archives

In a SigMF Archive (`.sigmf` tarball), the sidecar is an additional file placed
alongside the Recording's Metadata and Dataset files:

```
recording.sigmf
└── recording/
    ├── recording.sigmf-meta      (JSON Metadata, REQUIRED)
    ├── recording.sigmf-meta.h5   (HDF5 sidecar, OPTIONAL)
    └── recording.sigmf-data      (Dataset, REQUIRED)
```

SigMF Archives MAY contain additional files, so legacy tools ignore the sidecar
when extracting the Archive.

## 7 Compliance

A Recording using the `hdf5-meta` extension is compliant when:

1. The `.sigmf-meta` JSON file is a complete, valid SigMF Recording without
   reference to the sidecar (i.e., removing the sidecar leaves a compliant
   Recording).
2. `hdf5-meta` is listed in `core:extensions` and `hdf5-meta:file` is set in the
   `global` object.
3. If the sidecar file referenced by `hdf5-meta:file` is present, it conforms to
   the structure in [Section 4](#4-hdf5-sidecar-structure) and contains content
   equivalent to the JSON Metadata file.

Because the JSON file is authoritative and complete, a Recording remains SigMF
Compliant even if the sidecar is absent.

## 8 Examples

A `.sigmf-meta` file that references an HDF5 sidecar:

```json
{
    "global": {
        "core:datatype": "cf32_le",
        "core:sample_rate": 1000000,
        "core:version": "1.2.0",
        "core:extensions": [
            {
                "name": "hdf5-meta",
                "version": "1.0.0",
                "optional": true
            }
        ],
        "hdf5-meta:file": "recording.sigmf-meta.h5",
        "hdf5-meta:version": "1.0.0"
    },
    "captures": [
        {
            "core:sample_start": 0,
            "core:frequency": 915000000
        }
    ],
    "annotations": [
        {"core:sample_start": 0, "core:sample_count": 100, "core:label": "burst_0"},
        {"core:sample_start": 1000, "core:sample_count": 100, "core:label": "burst_1"}
    ]
}
```

The corresponding `recording.sigmf-meta.h5` sidecar would contain:

- Root attributes `sigmf_version = "1.2.0"` and `hdf5_meta_version = "1.0.0"`.
- A `/global` group with attributes `core.datatype = "cf32_le"`,
  `core.sample_rate = 1000000.0`, `core.version = "1.2.0"`,
  `core.extensions = "[{\"name\": \"hdf5-meta\", ...}]"` (JSON-encoded),
  `hdf5-meta.file = "recording.sigmf-meta.h5"`, and
  `hdf5-meta.version = "1.0.0"`.
- A `/captures` dataset with columns `core.sample_start` (int64) and
  `core.frequency` (float64), and one row `(0, 915000000.0)`.
- An `/annotations` dataset with columns `core.sample_start` (int64),
  `core.sample_count` (int64), and `core.label` (string), and two rows
  `(0, 100, "burst_0")` and `(1000, 100, "burst_1")`.
</content>
</invoke>
