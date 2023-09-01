# The `traceability` SigMF Extension Namespace v1.0.0

This document proposes a new extension namespace called `traceability` for the Signal Metadata
Format (SigMF) specification. This extension provides traceability information for the metadata.

## 1 Global

`traceability` extends the [Global](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#global-object) object.

The following fields are added to the `global` object:

|name|required|type|description|
|----|--------|----|-----------|
|`traceability:last_modified`|false|[DataChange](#datachange-object)|Captures the author and timestamp of the most recent modification|
|`traceability:last_reviewed`|false|[DataChange](#datachange-object)|Captures the author and timestamp of the most recent review|
|`traceability:revision`|false|integer|Specifies the revision number associated with the metadata|
|`traceability:origin`|false|[Origin](#origin-object)|Provides information about the origin of the data|
|`traceability:sample_length`|false|integer|Specifies the total number of samples of the Dataset|

### DataChange Object

|name|required|type|description|
|----|--------|----|-----------|
|`author`|false|string|Email address of the author who changed the metadata|
|`time`|true|string (date-time)|Timestamp of the modification in ISO 8601 format|

### Origin Object

|name|required|type|description|
|----|--------|----|-----------|
|`account`|false|string|Account name or identifier|
|`container`|false|string|Container or repository name|
|`file_path`|true|string|Path to the file within the container|

## 2 Captures

`traceability` does not extend the [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array) object.

## 3 Annotations

`traceability` extends the [Annotations](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#annotations-object) object.

The following fields are added to each annotation in the `annotations` array:

|name|required|type|description|
|----|--------|----|-----------|
|`traceability:last_modified`|false|[DataChange](#datachange-object)|Captures the author and timestamp of the most recent modification|
|`traceability:last_reviewed`|false|[DataChange](#datachange-object)|Captures the author and timestamp of the most recent review|

## 4 Examples

Here are some examples of using the `traceability` extension:

- Simple traceability information:

```json
{
  "global": {
    "traceability:last_modified": {
      "author": "john.doe@example.com",
      "time": "2023-05-31T12:00:00Z"
    },
    "traceability:last_reviewed": {
      "author": "ben.doe@example.com",
      "time": "2023-05-31T12:30:00Z"
    },
    "traceability:revision": 1,
    "traceability:origin": {
      "file_path": "/data/signal_data.bin"
    }
  },
  "annotations": [
    {
      "traceability:last_modified": {
        "author": "jane.doe@example.com",
        "time": "2023-05-30T10:30:00Z"
      },
      "core:label": "Signal of interest",
      "core:sample_start": 100,
      "core:sample_count": 500
    }
  ],
}
```

- Multiple annotations with traceability information:

```json
{
  "global": {
    "traceability:last_modified": {
      "author": "john.doe@example.com",
      "time": "2023-05-31T12:00:00Z"
    },
    "traceability:last_reviewed": {
      "author": "ben.doe@example.com",
      "time": "2023-05-31T12:30:00Z"
    },
    "traceability:revision": 1,
    "traceability:origin": {
      "file_path": "/data/signal_data.bin"
    }
  },
  "annotations": [
    {
      "traceability:last_modified": {
        "author": "jane.doe@example.com",
        "time": "2023-05-30T10:30:00Z"
      },
      "core:label": "Signal of interest",
      "core:sample_start": 100,
      "core:sample_count": 500
    },
    {
      "traceability:last_modified": {
        "author": "james.smith@example.com",
        "time": "2023-05-30T15:45:00Z"
      },
      "traceability:last_reviewed": {
      "author": "ben.doe@example.com",
      "time": "2023-05-31T12:30:00Z"
    },
    "core:label": "Noise artifact",
      "core:sample_start": 600,
      "core:sample_count": 200
    }
  ]
}
```

- Traceability information with additional origin details:

```json
{
  "global": {
    "traceability:last_modified": {
      "author": "john.doe@example.com",
      "time": "2023-05-31T12:00:00Z"
    },
    "traceability:revision": 1,
    "traceability:origin": {
      "account": "user123",
      "container": "sigmf_data",
      "file_path": "/data/signal_data.bin"
    }
  },
  "annotations": [
    {
      "traceability:last_modified": {
        "author": "jane.doe@example.com",
        "time": "2023-05-30T10:30:00Z"
      },
      "core:label": "Signal of interest",
      "core:sample_start": 100,
      "core:sample_count": 500
    }
  ]
}
```

- Multiple modifications of the metadata:

```json
{
  "global": {
    "traceability:last_modified": {
      "author": "john.doe@example.com",
      "time": "2023-05-31T12:00:00Z"
    },
    "traceability:revision": 2,
    "traceability:origin": {
      "file_path": "/data/signal_data.bin"
    }
  },
  "annotations": [
    {
      "traceability:last_modified": {
        "author": "jane.doe@example.com",
        "time": "2023-05-30T10:30:00Z"
      },
      "traceability:last_reviewed": {
        "author": "ben.doe@example.com",
        "time": "2023-05-31T12:30:00Z"
      },
      "core:label": "Signal of interest",
      "core:sample_start": 100,
      "core:sample_count": 500
    },
    {
      "traceability:last_modified": {
        "author": "jane.doe@example.com",
        "time": "2023-05-31T09:15:00Z"
      },
      "core:label": "Updated signal of interest",
      "core:sample_start": 50,
      "core:sample_count": 700
    }
  ]
}
```
