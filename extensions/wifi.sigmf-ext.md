## Wi-Fi Extension v1.0.0

The `wifi`namespace extension defines dynamic Wi-Fi burst parameters extending
`annotations`.

## 1 Global

`wifi` does not extend [Global](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#global-object).

## 2 Captures

`wifi` does not extend [Captures](https://github.com/sigmf/SigMF/blob/main/sigmf-spec.md#captures-array).

## 3 Annotations

The following names are specified in the `wifi` namespace and should be used in the `annotations` object:

|name|required|type|unit|description|
|----|--------|----|----|-----------|
|`standard`|true|string|N/A|Wireless standard of captured signal e.g. 802.11a/g.|
|`frame_type_phy`|true|string|N/A|Physical layer specification e.g. non-high throughput or very-high throughput.|
|`channel`|true|int|N/A|Wi-Fi channel of captured signal|
|`start_time_s`|true|double|seconds|Start time of RF burst (relative time to start time of main capture file).|
|`stop_time_s`|true|double|seconds|Stop time of RF burst (relative time to start time of main capture file).|
|`frame_duration_s`|true|double|seconds|Duration of RF burst (`stop_time_s` - `start_time_s`).|
|`MCS`|true|int|N/A|Wi-Fi signal Modulation and Coding Scheme (MCS).|
|`MAC_frame_type`|true|string|N/A|Wi-Fi MAC frame type.|
|`MAC_ta`|true|string|N/A|Wi-Fi transmitter MAC address.|
|`MAC_ra`|true|string|N/A|Wi-Fi receiver MAC address.|
|`manufacturer_ta`|true|string|N/A|Manufacturer of the Wi-Fi transmitter.|
|`MAC_frame`|true|string|N/A|Wi-Fi MAC frame data without CRC.|
|`CRC`|true|string|N/A|Wi-Fi MAC frame CRC.|
|`start_of_packet`|true|double|samples|Starting sample of captured Wi-Fi burst.|
|`stop_of_packet`|true|double|samples|Stopping sample of captured Wi-Fi burst.|
|`number_of_samples_in_packet`|true|double|samples|Number of downsampled IQ samples in Wi-Fi burst.|

## 4 Examples

No `wifi` examples.
