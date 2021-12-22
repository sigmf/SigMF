# Capture Details Extension v1.0.0

The `capture_details` namespace extension defines static IQ capture parameters
extending `captures` and dynamic IQ capture parameters extending `annotations`.

## 1 Global

`capture_details` does not extend [Global](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#global-object).

## 2 Captures

The following names are specified in the `capture_details` namespace and should
be used in the `captures` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`acq_scale_factor`|true|float|N/A|Scale factor of IQ collection from the spectrum analyzer used to convert back to real power.|
|`attentuation`|true|float|dB|Input attenuation on the spectrum analyzer.|
|`acquisition_bandwidth`|true|float|Hz|Frequency range of the IQ recording.|
|`start_capture`|true|string|N/A|Time of the first sample of IQ recording. The time is UTC with the format of `yyyy-mm-ddTHH:MM:SSZ`.|
|`stop_capture`|true|string|N/A|Time of the last sample of IQ recording. The time is UTC with the format of `yyyy-mm-ddTHH:MM:SSZ`.|
|`source_file`|true|string|N/A|RF IQ recording filename that was used to create the file `N.sigmf-data`.  The file `N.sigmf-data` may be the same or an edited versions of the `source_file`.|
|`gain`|false|float|dB|Input gain.|

## 3 Annotations

The following names are specified in the `capture_details` namespace and should be used in the `annotations` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`SNRdB`|true|float|dB|Root mean square (RMS) calculation of signal to noise ratio (SNR). The calculation is over windows of known signal and no known signal.|
|`signal_reference_number`|true|string|N/A|Sequential reference labels for the elements that form the sequence of signals identified in a SigMF dataset file. The format of the string is the filename followed by an index that increases with each decoded signal.  An example is a recording dataset file named `N.sigmf-data` would have signal numbers starting with `N-1`, `N-2`, `N-3`...|

## 4 Examples

No `capture_details` examples.
