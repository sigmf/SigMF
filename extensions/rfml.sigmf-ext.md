# RFML Extension v1.0.0
The radio frequency machine learning (`rfml`) namespace extension defines the protocol, manufacturer, and device labeling scheme for RF bursts.

## Global

The following names are specified in the `rfml` namespace and should be used in the `global` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`label_hierarchy`|true|array|N/A|Defines hierarchy of the fields in the label array.|
|`version`|true|string|N/A|The version of the `rfml` extension used to create the metadata file.|


## Annotations

The following names are specified in the `rfml` namespace and should be used in the `annotations` object:

|name|required|type|unit|description|
|----|--------------|-------|-------|-----------|
|`label`|true|array|N/A|An array of hierarchical labels that describe this annotation. The label `device_type` is the type of RF transmitter or signal source.  The label `manufacturer_ID` is the manufacturer of the transmitter. The label `device_ID` is the source of the RF signal.|