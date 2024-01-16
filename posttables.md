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
