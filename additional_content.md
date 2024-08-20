\subsection{Introduction}

Sharing sets of recorded signal data is an important part of science and
engineering. It enables multiple parties to collaborate, is often a necessary
part of reproducing scientific results (a requirement of scientific rigor), and
enables sharing data with those who do not have direct access to the equipment
required to capture it.

Unfortunately, these datasets have historically not been very portable, and
there is not an agreed upon method of sharing metadata descriptions of the
recorded data itself. This is the problem that SigMF solves.

By providing a standard way to describe data recordings, SigMF facilitates the
sharing of data, prevents the "bitrot" of datasets wherein details of the
capture are lost over time, and makes it possible for different tools to operate
on the same dataset, thus enabling data portability between tools and workflows.

\subsection{Conventions Used in this Document}

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be
interpreted as described in \href{https://tools.ietf.org/html/rfc2119}{RFC 2119}.

JSON keywords are used as defined in \href{https://ecma-international.org/publications-and-standards/standards/ecma-404/}{ECMA-404}.

Augmented Backus-Naur form (ABNF) is used as defined by \href{https://tools.ietf.org/html/rfc5234}{RFC 5234}
and updated by \href{https://tools.ietf.org/html/rfc7405}{RFC 7405}.

Fields defined as "human-readable", a "string", or simply as "text" SHALL be
treated as plaintext where whitespace is significant, unless otherwise
specified. Fields defined "human/machine-readable" SHOULD be short, simple
text strings without whitespace that are easily understood by a human and
readily parsed by software.

Specific keywords with semantic meaning in the context of this specification 
are capitalized after being introduced (e.g., Recording).

\subsection{Specification Overview}

The SigMF specification fundamentally describes two types of information:
datasets, and metadata associated with those datasets. Taken together, a Dataset
with its SigMF metadata is a SigMF `Recording`.

Datasets, for purposes of this specification, are sets of digital measurements
generically called `samples` in this document. The samples can represent any
time-varying source of information. They MAY, for example, be digital samples
created by digital synthesis or by an Analog-to-Digital Converter. They could
also be geolocation coordinates from a GNSS receiver, temperature readings
from a thermal sensor, or any other stored digital measurement information.

Metadata describes the Dataset with which it is associated. The metadata
includes information meant for the human users of the Dataset, such as a title
and description, and information meant for computer applications (tools) that
operate on the Dataset.

This specification defines a schema for metadata using a `core` namespace that 
is a reserved name and can only be defined by this specification. Other metadata
MAY be described by extension namespaces. This specification also defines a 
model and format for how SigMF data should be stored at-rest (on-disk) using JSON.

\subsection{SigMF File Types}

There are two fundamental filetypes defined by this specification: files with 
metadata, and the files that contain the Datasets described by the metadata.
There are two types of files containing metadata, a SigMF `Metadata` file, and a
SigMF `Collection` file. There are also two types of Datasets, a SigMF `Dataset`
file, and a `Non-Conforming Dataset` file, abbreviated as `NCD`. NCDs are a
mechanism to support using valid SigMF metadata to describe data that is not
valid SigMF and formatted according to SigMF Dataset requirements.

The primary unit of SigMF is a SigMF `Recording`, which comprises a Metadata file
and the Dataset file it describes. Collections are an optional feature that are 
used to describe the relationships between multiple Recordings. 

Collections and multiple Recordings can be packaged for easy storage and 
distribution in a SigMF `Archive`.

\begin{figure}[t]
\includesvg[width=400px]{images/SigMFobjects.drawio.svg}
\centering
\end{figure}

Rules for all files:
\begin{enumerate}
\item All filetypes MUST be stored in separate files on-disk.
\item It is RECOMMENDED that filenames use hyphens to separate words rather than whitespace or underscores.
\end{enumerate}

Rules for SigMF Metadata files:
\begin{enumerate}
\item A Metadata file MUST only describe one Dataset file.
\item A Metadata file MUST be stored in UTF-8 encoding.
\item A Metadata file MUST have a `.sigmf-meta` filename extension.
\item A Metadata file MUST be in the same directory as the Dataset file it describes.
\item It is RECOMMENDED that the base filenames (not including file extension) of a Recording's Metadata and Dataset files be identical.
\end{enumerate}

Rules for SigMF Dataset files:
\begin{enumerate}
\item The Dataset file MUST have a `.sigmf-data` filename extension.
\end{enumerate}

Rules for SigMF Non-Conforming Dataset files:
\begin{enumerate}
\item The NCD file MUST NOT have a `.sigmf-data` filename extension.
\end{enumerate}

Rules for SigMF Collection files:
\begin{enumerate}
\item The Collection file MUST be stored in UTF-8 encoding.
\item The Collection file MUST have a `.sigmf-collection` filename extension.
\item The `sigmf-collection` file MUST be either in the same directory as the Recordings that it references, or in the top-level directory of an Archive (described in later section).
\end{enumerate}

Rules for SigMF Archive files:
\begin{enumerate}
\item The Archive MUST use the `tar` archive format, as specified by POSIX.1-2001.
\item The Archive file's filename extension MUST be `.sigmf`.
\item The Archive MUST contain at least one SigMF Recording.
\item The Archive MAY contain one `.sigmf-collection` file in the top-level directory.
\item SigMF Archives MAY contain additional files (not specified by SigMF), and arbitrary directory structures, but the SigMF files within the Archive MUST adhere to all rules above when the archive is extracted.
\end{enumerate}

\subsection{SigMF Dataset Format}

There are four orthogonal characteristics of sample data: complex or real, 
floating-point or integer, bit-width, and endianness. The following ABNF 
rules specify the Dataset formats defined in the Core namespace. Additional
Dataset formats MAY be added through extensions.

\begin{verbatim}
    dataset-format = (real / complex) ((type endianness) / byte)

    real = "r"
    complex = "c"

    type = floating-point / signed-integer / unsigned-integer
    floating-point = "f32" / "f64"
    signed-integer = "i32" / "i16"
    unsigned-integer = "u32" / "u16"

    endianness = little-endian / big-endian
    little-endian = "_le"
    big-endian = "_be"

    byte = "i8" / "u8"
\end{verbatim}

So, for example, the string `"cf32_le"` specifies "complex 32-bit floating-point
samples stored in little-endian", the string `"ru16_be"` specifies "real
unsigned 16-bit samples stored in big-endian", and the string `"cu8"` specifies
"complex unsigned byte".

Only IEEE-754 single-precision and double-precision floating-point types are
supported by the SigMF Core namespace. Note that complex data types are
specified by the bit width of the individual I/Q components, and not by the
total complex pair bitwidth (like Numpy).

The samples SHOULD be written to the Dataset file without separation, and the
Dataset file MUST NOT contain any other characters (e.g., delimiters,
whitespace, line-endings, EOF characters).

Complex samples MUST be interleaved, with the in-phase component first (i.e., `I[0]` `Q[0]` `I[1]` `Q[1]` ... `I[n]` `Q[n]`). 

When `core:num_channels` in the Global Object (described below) indicates that the Recording contains more than one channel, samples from those channels MUST be interleaved in the same manner with the same index from each channel's sample serially in the Recording. This is intended for use in situations where the native SigMF datatypes are not appropriate, such as audio or oscilloscope channels. For best compatibility, is RECOMMENDED that native complex type datatypes be used whenever possible (e.g.: RF data).  For multiple channels of IQ data (e.g., array processing), it is RECOMMENDED to use SigMF Collections.

\subsection{SigMF Metadata Format}

SigMF metadata fundamentally takes the form of key/value pairs: `"namespace:name": value,`

Metadata field names in the top level `global` Object, `captures` segment
Objects, or `annotations` Objects MUST be of this form. All fields other than
those at the top level which contain a `:` delimiter SHALL only use letters,
numbers, and the `_` character; all other characters are forbidden. Field names
MUST NOT start with a number and MUST NOT not be C++20 or Python 3.10 keywords.

When stored on-disk (at-rest), these rules apply:
\begin{enumerate}
\item The Metadata file MUST be written in JSON, as specified by \href{https://ecma-international.org/publications-and-standards/standards/ecma-404/}{ECMA-404}.
\item The entire contents of the Metadata file MUST be contained within a single top-level JSON Object.
\item The top-level Object MUST contain three JSON Objects named `global`, `captures`, and `annotations`.
\item Metadata key/value pairs SHALL NOT be assumed to have carried over between capture or annotation segments. If a name/value pair applies to a particular segment, then it MUST appear in that segment, even if the value is unchanged relative to the previous segment.
\end{enumerate}

All SigMF metadata is defined using the structural concepts of JSON, and when 
stored on-disk, metadata MUST be proper JSON to be SigMF compliant.

\subsubsection{Datatypes}

The values in each key/value pair MUST be one of the following datatypes.

\rowcolors{1}{}{lightblue}
\begin{table}[!ht]
    \centering
    \begin{tabular}{lll}
    \toprule
        \textbf{Type} & \textbf{Long-form Name} & \textbf{Description} \\ 
    \midrule
        int & integer & Signed 64-bit integer. \\
        uint & unsigned long & Unsigned 64-bit integer. \\
        double & double-precision floating-point & A 64-bit float as defined by IEEE 754. \\
        string & string & A string of characters, as defined by the JSON standard. \\
        boolean & boolean & Either `true` or `false`, as defined by the JSON standard. \\
        null & null & `null`, as defined by the JSON standard. \\
        array & JSON array & An `array` of other values, as defined by the JSON standard. \\
        object & JSON object & An `object` of other values, as defined by the JSON standard. \\
        GeoJSON & GeoJSON point Object & A single GeoJSON `point` Object as defined by RFC 7946. \\
    \bottomrule
    \end{tabular}
\end{table}

\subsubsection{Namespaces}

Namespaces provide a way to further classify key/value pairs in metadata.
This specification defines the `core` namespace. Only this specification
can add fields to the Core namespace.

The goal of the Core namespace is to capture the foundational metadata 
necessary to work with SigMF data. Some keys within the Core namespace are
OPTIONAL, and others are REQUIRED. The REQUIRED fields are those that are
minimally necessary to parse and process the Dataset, or that have obvious
defaults that are valid. All other fields are OPTIONAL, though they can be
strongly RECOMMENDED.

\subsubsubsection{Extension Namespaces}

Fields not defined in the Core namespace MAY be defined in extension
namespaces. The SigMF specification defines some extension namespaces to
provide canonical definitions for commonly needed metadata fields that do not
belong in Core. These canonical extension namespaces can be found in the
`extensions/` directory of the official SigMF repository. Other extension
namespaces MAY be defined by the user as needed.

\begin{enumerate}
\item An extension namespace MUST be defined in a single file, named meta-syntactically as `N.sigmf-ext.md`, where `N` is the name of the extension.
\item A `N.sigmf-ext.md` file MUST be a Github-Flavored Markdown file stored in UTF-8 encoding.
\item Extensions MUST have version numbers. It is RECOMMENDED that extensions use \href{https://semver.org}{Semantic Versioning}.
\item An extension namespace MAY define new top-level SigMF Objects, key/value pairs, new files, new Dataset formats, or new datatypes.
\item New key/value pairs defined by an extension namespace MUST be defined in the context of a specific SigMF top-level Object - i.e., `global`, `captures`, `annotations`, or a new user-defined Object.
\item It is RECOMMENDED that an extension namespace file follow the structure of the canonical extension namespaces.
\end{enumerate}

<<<<<<<<<<content from JSON schema>>>>>>>>>>>>

\subsection{SigMF Recording Objects}

`SigMF Recording Objects` reference the base-name of the SigMF Recording and the
SHA512 hash of the Metadata file, and SHOULD BE specified as a JSON Object:

\begin{verbatim}
  {
    "name": "example-channel-0-basename",
    "hash": "b4071db26f5c7b0c70f5066eb9..."
  }
\end{verbatim}

Recording Tuples are also permitted and have a similar form. The order of
the tuple: [`name`, `hash`] is REQUIRED when using tuples:

\begin{verbatim}
  ["example-channel-0-basename", "b4071db26f5c7b0c70f5066e..."]
\end{verbatim}

Tuples will be removed in SigMF version 2.0, so JSON Objects are RECOMMENDED.
Additional optional user fields MAY be added to `SigMF Recording Objects` if
they are defined in a compliant SigMF extension. Additional fields are NOT
permitted in tuples.

\subsection{Licensing}

Open licenses are RECOMMENDED but you can specify any license. You can refer to 
resources provided by the \href{https://opendatacommons.org/}{Open Data Commons} when 
deciding which open license fits your needs best. Cornell University has also 
created \href{https://data.research.cornell.edu/content/intellectual-property#data-licensing}{a guide}
to help you make these choices.

\subsection{SigMF Compliance}

The term 'SigMF Compliant' is used throughout this document, which can take on
one of several contextually dependent meanings. In order for a schema,
Recording, or application to be 'SigMF Compliant', specific conditions MUST be
met, outlined in the following sections. Provided the below criteria are met, an
application or Recording can indicate that it is 'SigMF Compliant'.

\subsubsection{SigMF Schema Compliance}

In order to be 'SigMF Compliant', a schema MUST meet the following requirements:

\begin{enumerate}
\item Adheres to and supports the metadata file naming conventions, `objects`,  `namespaces`, and `names` specified by this document.
\item MUST contain all REQUIRED fields with the correct datatype listed the `core` namespace, and any namespace listed in the `extensions` array.
\item MUST NOT contain fields that are not outlined in the `core` or a listed `extensions` namespace.
\end{enumerate}

\subsubsection{SigMF Recording Compliance}

In order to be 'SigMF Compliant', a Recording MUST meet the following
requirements:

\begin{enumerate}
\item The Recording's schema file MUST be SigMF Compliant.
\item Adheres to and supports the file naming conventions and Dataset formats specified in this document.
\item Stores data using the on-disk representation described by the `datatype`.
\end{enumerate}

Recordings with Non-Conforming Datasets MAY have SigMF Compliant schema, but
cannot be SigMF Compliant Recordings.

\subsubsection{SigMF Collection Compliance}

In order to be 'SigMF Compliant', a Collection must meet the following
requirements:

\begin{enumerate}
\item The collection MUST contain only compliant Recordings.
\item The Collection Object MUST only contain SigMF key/value pairs provided by the core specification or a compliant SigMF extension.
\end{enumerate}

\subsubsection{SigMF Application Compliance}

In order to be 'SigMF Compliant', an application MUST meet the following
requirements:

\begin{enumerate}
\item Is capable of parsing and loading SigMF Compliant Recordings. Support for  SigMF Collections and Archives is RECOMMENDED but not REQUIRED.
\item Adheres to and supports the file rules, Dataset formats, `objects`, `namespaces`, and `names` specified by this document.
\item MUST be able to ignore any `object` or `namespace` not specified by this document and still function normally.
\item Capture Segments referring to non-existent samples SHOULD be ignored.
\item MUST treat consecutive Capture Segments whose metadata is equivalent for purposes of that application (i.e., it may be different in values ignored by the application such as optional values or unknown extensions) as it would a single segment.
\item MUST support parsing ALL required fields in the `core` namespace, and defines which optional fields are used by the application.
\item MUST define which extensions are supported, parses ALL required fields in listed extension namespaces, and defines which optional fields are used. This definition can be in user documentation or within the code itself, though explicit documentation is RECOMMENDED.
\item Support for ALL SigMF Datatypes is NOT REQUIRED as certain datatypes may not make sense for a particular application, but Compliant applications MUST define which datatypes are supported, and be capable of loading Compliant Recordings using supported datatypes.
\end{enumerate}

Compliant applications are NOT REQUIRED to support Non-Conforming Datasets or
Metadata Only schema files, but it is RECOMMENDED that they parse the respective
metadata fields in the `global` Object to provide descriptive messages to users
regarding why the files are not supported.

Support for SigMF Collections is OPTIONAL for SigMF Compliant applications,
however it is RECOMMENDED that applications implementing SigMF make use of
Collections when appropriate for interoperability and consistency.

\subsection{Citing SigMF}

To cite the SigMF specification, we recommend the following format:

\begin{verbatim}
The Signal Metadata Format (SigMF), <release>, <date of release>, https://sigmf.org
\end{verbatim}

\subsection{Acknowledgements}

This specification originated at the DARPA Brussels Hackfest 2017.
