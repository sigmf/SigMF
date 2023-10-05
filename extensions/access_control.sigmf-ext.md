# Access Control Extension for SigMF v1.0.0

The Access Control Extension is designed to manage access to SigMF files, providing mechanisms for access permissions and control.

## 1 Global
`access_control` extends the [Global](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#global-object) object.

|name|required|type|description|
|----|--------|----|-----------|
|`access_control:owner`|true|string|A text identifier for the owner potentially including name, handle, email, and/or other ID like Amateur Call Sign.|
|`access_control:public`|true|boolean|Determine whether the SigMF dataset is public or only accessible for certain `Accessors`|
|`access_control:accessors`|false|Accessor[]|People/Groups authorized to view. If `public` is set `true`, everyone can access the SigMF Dataset. If `public` is set `false` and not set only `owner` can view.|

### Accessor Object

|name|required|type|description|
|----|--------|----|-----------|
|`accessor`|true|string|A text identifier for the accessor potentially including name, handle, email, and/or other ID like Amateur Call Sign. |
|`group`|true|boolean|Determine whether Accessor is a group|
|`editor`|false|boolean|Determine whether Accessor is allowed to edit|



## 2 Captures

`access_control` does not extend [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array).

## 3 Annotations


`access_control` does not extend [Annotations](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#annotations-array)

## 4 Examples

Here are some examples of using the `access_control` extension:

- Public Dataset but only editable by owner
```json
{
    "global": {
        "access_control:owner": "john.doe@example.com",
        "access_control:public": true
    }
}
```

- Only let cetrain people view and edit

```json
{
    "global": {
        "access_control:owner": "john.doe@example.com",
        "access_control:public": false,
        "access_control:accessors": [
            {
                "accessor": "jane.doe@example.com",
                "group": false,
                "editor": true
            },
            {
                "accessor": "max.mustermann@example.com",
                "group": false
            },
        ],
    }
}
```

- Only people in a certain group are allowed to view, but not to edit.

```json
{
    "global": {
        "access_control:owner": "john.doe@example.com",
        "access_control:public": false,
        "access_control:accessors": [
            {
                "accessor": "group_1",
                "group": true
            }
        ]
    }
}
```