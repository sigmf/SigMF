# The `modulation` SigMF Extension Namespace v0.0.1

## Description

This document defines the `modulation` extension namespace for the Signal
Metadata Format (SigMF) specification. This extension namespace defines how to
describe the modulations of wireless communications systems.

## Copyright Notice

This document is Copyright of The GNU Radio Foundation, Inc.

This document is available under the [CC-BY-SA License](http://creativecommons.org/licenses/by-sa/4.0/).

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

## Conventions Used in this Document

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

JSON keywords are used as defined in [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

Augmented Backus-Naur form (ABNF) is used as defined by [RFC
5234](https://tools.ietf.org/html/rfc5234) and updated by [RFC
7405](https://tools.ietf.org/html/rfc7405).

Fields defined as "human-readable", a "string", or simply as "text" shall be
treated as plaintext where whitespace is significant, unless otherwise
specified.

## Specification

This specification defines new name/value fields in the `modulation` namespace
that can be used in SigMF `annotations` to describe wireless communications
systems.

### Annotations

|name|required|type|description|
|----|--------------|-------|-----------|
|modulation|false|string|Describes a communications modulation.|
|system|false|string|Describes the communications system at a higher-level.|

##### The `modulation` Field

The following initialisms and acronyms are used in the ABNF form of this
metadata field:

* `analog-type`:
    * **am**: amplitude modulation
    * **fm**: frequency modulation
    * **pm**: phase modulation
    * **ssb**: single side-band
    * **dsb**: dual side-band
    * **vsb**: vestigial side-band
* `analog-carrier-variant`:
    * **wc**: with-carrier
    * **sc**: suppressed-carrier
    * **rc**: reduced-carrier
* `digital-type`:
    * **ask**: amplitude-shift keying
    * **fsk**: frequency-shift keying
    * **psk**: phase-shift keying
    * **qam**: quadrature-amplitude modulation
    * **ook**: on-off keying
    * **cpm**: continuous phase modulation
    * **msk**: minimum-shift keying
* `common-psk`:
    * **b**: binary
    * **q**: quadrature
* `digital-type-variants`:
    * **d**: differential
    * **o**: offset
    * **s**: staggered
* `digital-shared-type`:
    * **m**: multiplexing
    * **ma**: multiple-access
* `digital-multi-type`:
    * **fd**: frequency-division
    * **ofd**: orthogonal frequency-division
    * **td**: time-division
    * **pd**: phase-division
    * **cd**: code-division
* `spread-spectrum`:
    * **dsss**: direct-sequence spread spectrum
    * **css**: chirp spread spectrum
    * **fhss**: frequency-hopping spread spectrum

The `modulation` field must be defined according to these rules:

```abnf
modulation = analog / digital

new-type = 1*32(DIGIT / ALPHA)

analog = analog-type ["-" analog-carrier-variant]

analog-type = amplitude-modulation / "FM" / "PM" / new-type
amplitude-modulation = "AM" / "DSB" / "SSB" / "VSB"
analog-carrier-variant = "WC" / "SC" / "RC"

digital = [digital-multi-type "-"] [digital-symbols "-"] digital-type ["-" spread-spectrum]

digital-multi-type = (("FD / "OFD") / "TD" / "PD" / "CD" / new-type) [digital-shared-type]
digital-shared-type = "M" / "MA" / new-type

digital-symbols = "2" / "4" / "8" / "16" / "32" / "64" / "128" / "256" / new-type

digital-type = [digital-type-variant] ("QAM" / "ASK" / "FSK" / [common-psk] "PSK" / "OOK" / "CPM" / "MSK" / new-type)
common-psk = ["B" / "Q"]
digital-type-variant = "D" / "O" / "S" / new-type

spread-spectrum = "DSSS" / "CSS" / "FHSS" / new-type
```

Note: The `common-psk` structure is necessary because the "BPSK" and "QPSK"
nomenclature is inconsistent with other PSK-modulations when combined with type
variants. For example, you would write either `4-OPSK` or `OQPSK` - note that
the symbol count and type variant indicators swap places and there is no hyphen.

##### The `system` Field

TODO 
describes `802.11ac` or `Wireless Webcam`
