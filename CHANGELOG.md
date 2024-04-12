# Changelog

All notable changes will be documented here for easy reference.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CHANGELOG

## [1.2.0] - 2024-01-13

### Added

- Core specification
    - Optional `uuid` in `annotations` object
- SVG version of logo

### Changed

- Clarify optional Extensions
- Spatial extension
    - Add range-rate to bearing object
    - Add aperture_rotation field

### Removed

- Python module moved to separate repository [sigmf-python](https://github.com/sigmf/sigmf-python).

## [1.1.0] - 2023-01-12

### Changed

- Core specification
    - Deprecate tuples in favor of JSON objects
    - Clarify rules related to SigMF archives
    - Fix table of contents errors
    - Application compliance language clarification

## [1.0.1] - 2022-12-03

### Added

- Specifically point to the [NTIA extensions](https://github.com/NTIA/sigmf-ns-ntia) as good references.
- Spatial extension

### Changed

- Core specification
    - Add examples
    - Clarification of field types
    - Conforming / compliant language

### Removed

- Undocumented & incomplete RFML extension

## [1.0.0] - 2022-01-05

### Added

- Core Specification
    - Definition of Dataset
    - GeoJSON to store locations in `geolocation` field
    - New `header_bytes` and `trailing_bytes` field
    - New `metadata_only` field
    - Define SigMF compliance
- Add Collection Format
- Official logo & example `.sigmf` files
- Extensions
    - ADS-B
    - Antenna
    - Capture Details
    - RFML
    - Signal
    - WiFi
- Code of conduct

### Changed

- Core specification rewrite
    - Descriptions for all fields
    - Inclusion of block diagrams
    - Clarification of data types
    - Formalize extension definitions & versioning
- Formal license inclusion

## [0.0.1] - 2018-01-05

### Added

Initial release.

- Core specification
- Citation information
- CC-BY-SA-4.0 License
- Modulation extension
- Volatile extension


[unreleased]: https://github.com/sigmf/SigMF/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/sigmf/SigMF/compare/v1.2.0...v1.1.0
[1.1.0]: https://github.com/sigmf/SigMF/compare/v1.1.0...v1.0.1
[1.1.0]: https://github.com/sigmf/SigMF/compare/v1.1.0...v1.0.1
[1.0.1]: https://github.com/sigmf/SigMF/compare/v1.0.1...v0.0.1
[0.0.1]: https://github.com/sigmf/SigMF/tree/v0.0.1