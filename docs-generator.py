from __future__ import annotations

"""
Generate SigMF specification documentation (PDF + HTML) directly from the
JSON-Schema source files.
"""

from pathlib import Path
import json
import re
import subprocess
from typing import Any, Dict, Set

from pylatex import (
    Command,
    Document,
    Figure,
    Package,
    Section,
    Subsection,
    Subsubsection,

)
from pylatex.utils import NoEscape, bold

# ---------------------------------------------------------------------------
# Configuration – change these when the repository layout changes
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
SCHEMA_PATHS = {
    "core": REPO_ROOT / "sigmf-schema.json",
    "collection": REPO_ROOT / "collection-schema.json",
    "antenna": REPO_ROOT / "extensions" / "antenna-schema.json",
    "capture_detail": REPO_ROOT / "extensions" / "capture-detail-schema.json",
    "signal": REPO_ROOT / "extensions" / "signal-schema.json",
    "spatial": REPO_ROOT / "extensions" / "spatial-schema.json",
    "traceability": REPO_ROOT / "extensions" / "traceability-schema.json",
}
ADDITIONAL_CONTENT_MD = REPO_ROOT / "additional_content.md"
LOGO_PATH = REPO_ROOT / "logo" / "sigmf_logo.png"
OUTPUT_BASENAME = "sigmf-spec"

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> Dict[str, Any]:
    """Load *and* validate that *path* exists."""
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as f:
        return json.load(f)


def _normalise_key(key: str, *prefixes_to_strip: str) -> str:
    """Return a human-oriented variant of *key*.

    Prefixes like ``core:`` or ``signal:`` are stripped, duplicate underscores
    collapsed, and we keep colons intact so that the SigMF namespace remains
    visible in the PDF.
    """
    for p in prefixes_to_strip:
        key = key.replace(p, "")
    # Collapse accidental repeated underscores introduced by replacements
    key = re.sub(r"__+", "_", key)
    return key


def _add_code_tags(text: str) -> str:
    """
    Convert markdown-ish text to LaTeX, keeping code blocks intact.
    """
    # ------------------------------------------------------------------
    # 1) protect code blocks first
    # ------------------------------------------------------------------
    CODE_RE = re.compile(
        r"(```.*?```)|"                 # triple-back-tick markdown blocks
        r"(\\begin{verbatim}.*?\\end{verbatim})",
        re.DOTALL
    )

    code_store: list[str] = []

    def _stash(m: re.Match) -> str:
        code = m.group(0)
        if code.startswith("```"):
            code = code[3:-3]
            code = code.strip("\n")
            code = f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}"
        code_store.append(code)
        return f"§§CODEBLOCK{len(code_store)-1}§§"

    text = CODE_RE.sub(_stash, text)

    # ------------------------------------------------------------------
    # 2) Clean up problematic sequences from JSON schema descriptions
    # ------------------------------------------------------------------
    text = text.replace("_", r"\_")

    # Remove ALL line break commands that appear in schema descriptions
    text = text.replace("\\newline", " ")
    # This appears in collection-schema.json
    text = text.replace("\\nn", " ")
    text = text.replace("\\\\", " ")

    # Remove embedded LaTeX table commands that appear in schema descriptions
    text = re.sub(r"\\rowcolors\{[^}]*\}\{[^}]*\}\{[^}]*\}", "", text)
    text = re.sub(r"\\begin\{center\}.*?\\end\{center\}",
                  "", text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}",
                  "", text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{samepage\}.*?\\end\{samepage\}",
                  "", text, flags=re.DOTALL)
    text = re.sub(r"\\toprule|\\midrule|\\bottomrule", "", text)

    # Clean up paragraph breaks
    text = re.sub(r"\n{2,}", r"\\par\\vspace{2mm}", text)
    text = text.replace("\n", " ")

    # Handle inline code
    text = re.sub(r"(?<!`)`([^`]+)`(?!`)", r"\\code{\1}", text)

    # ------------------------------------------------------------------
    # 3) restore the verbatim/code chunks
    # ------------------------------------------------------------------
    for i, block in enumerate(code_store):
        text = text.replace(f"§§CODEBLOCK{i}§§", block)

    return text


def _plain_short_description(field: Dict[str, Any]) -> str:
    """Return short description up to first period or whole string."""
    desc = field.get("description", "").replace("\n", " ")
    dot = desc.find(".")
    return desc if dot == -1 else desc[:dot]

# ---------------------------------------------------------------------------
# Main generator class
# ---------------------------------------------------------------------------


class SigMFDocGenerator:
    """Create SigMF LaTeX (and afterwards HTML) documentation from schemas."""

    def __init__(self, schema_paths: dict[str, Path], logo_path: Path, extra_md: Path) -> None:
        self.schemas = {name: _read_json(p)
                        for name, p in schema_paths.items()}
        self.logo_path = logo_path
        self.extra_md_parts = extra_md.read_text().split(
            "<<<<<<<<<<content from JSON schema>>>>>>>>>>>>"
        )
        self.sigmf_version: str = self.schemas["core"]["$id"].split("/")[-2]

        self._labels: Set[str] = set()
        self._current_schema: str = "core"
        self.doc = self._create_document_skeleton()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_pdf_and_html(self) -> None:
        """Generate *OUTPUT_BASENAME*.pdf and *OUTPUT_BASENAME*.html."""
        tex_file = self._populate_document()

        # Try PDF generation
        try:
            self.doc.generate_pdf(OUTPUT_BASENAME, clean_tex=False,
                                  compiler_args=["--shell-escape"])
            print(f"PDF generated successfully: {OUTPUT_BASENAME}.pdf")
        except subprocess.CalledProcessError as e:
            # Check if PDF was actually generated despite errors
            pdf_path = Path(f"{OUTPUT_BASENAME}.pdf")
            if pdf_path.exists():
                print(
                    f"PDF generated with warnings: {OUTPUT_BASENAME}.pdf")
                print(
                    f"LaTeX had some issues but PDF was created (exit code: {e.returncode})")
            else:
                print(f"PDF generation failed: {e}")
        except Exception as e:
            print(f" PDF generation failed: {e}")

        # Generate HTML
        try:
            self._compile_html(tex_file)
            print("HTML generated successfully")
        except Exception as e:
            print(f"HTML generation failed: {e}")
            raise

    # ------------------------------------------------------------------
    # Internal helpers – document structure
    # ------------------------------------------------------------------

    def _create_document_skeleton(self) -> Document:
        geometry_options = {k: "1in" for k in (
            "tmargin", "lmargin", "rmargin", "bmargin")}
        doc = Document(geometry_options=geometry_options)

        # Preamble essentials ------------------------------------------------
        doc.preamble.append(Command("title", "SigMF"))
        for pkg in (
            ("underscore", None),
            ("xcolor", ["table"]),
            ("listings", None),
            ("microtype", None),
            ("fancyhdr", None),
            ("booktabs", None),
            ("longtable", None),
            ("svg", None),
            (
                "hyperref",
                ["hidelinks", "colorlinks=true", "urlcolor=blue", "linkcolor=black"],
            ),
        ):
            name, opts = pkg
            doc.packages.append(Package(name, options=opts))

        # Colours & custom macros -------------------------------------------
        doc.append(NoEscape("\\definecolor{mylightgray}{RGB}{240,240,240}"))
        doc.append(NoEscape("\\definecolor{lightblue}{RGB}{240,240,255}"))
        doc.append(
            NoEscape(
                "\\newcommand{\\code}[1]{\\texttt{\\colorbox{mylightgray}{#1}}}")
        )
        doc.append(
            NoEscape("\\newcommand{\\sectionspacing}[0]{\\par\\vspace{4mm}\\noindent}"))

        # Footer -------------------------------------------------------------
        doc.append(NoEscape("\\pagestyle{fancy}"))
        doc.append(NoEscape("\\fancyhf{}"))
        doc.append(NoEscape("\\renewcommand{\\headrulewidth}{0pt}"))
        doc.append(NoEscape("\\fancyfoot[LE,RO]{\\thepage}"))
        doc.append(
            NoEscape(
                f"\\fancyfoot[LO,CE]{{\\footnotesize SigMF Specification Version {self.sigmf_version}}}"
            )
        )
        doc.append(NoEscape(
            "\\newcommand{\\subsubsubsection}[1]{\\vspace{2mm}\\par\\noindent\\textbf{#1}\\par\\noindent}"))
        # Number down to paragraph level
        doc.append(NoEscape("\\setcounter{secnumdepth}{4}"))
        # Show paragraphs in TOC
        doc.append(NoEscape("\\setcounter{tocdepth}{4}"))

        return doc

    # ------------------------------------------------------------------
    # Content adding helpers
    # ------------------------------------------------------------------

    def _populate_document(self) -> Path:
        """Fill *self.doc* with all sections and return resulting *Path* to TEX."""

        self._add_cover_and_toc()
        self._add_core_sections()
        self._add_extensions()

        tex_path = Path(f"{OUTPUT_BASENAME}.tex")
        self.doc.generate_tex(tex_path.stem)  # Only write .tex; compile later
        return tex_path

    def _add_cover_and_toc(self) -> None:
        with self.doc.create(Figure(position="h!")) as logo:
            self.doc.append(NoEscape("\\vspace{-0.8in}\\centering"))
            logo.add_image(str(self.logo_path), width="120px")
            self.doc.append(NoEscape("\\vspace{-0.3in}"))

        with self.doc.create(Section(f"SigMF Specification Version {self.sigmf_version}")):
            self._add_subsection(
                "Abstract", self.schemas["core"].get("description", ""))
            copyright_md = (
                "This document is available under the "
                "\\href{http://creativecommons.org/licenses/by-sa/4.0/}{CC-BY-SA License}. "
                "Copyright of contributions to SigMF are retained by their original authors. "
                "All contributions under these terms are welcome."
            )
            self._add_subsection("Copyright Notice", copyright_md)

            with self.doc.create(Subsection("Table of Contents")):
                self.doc.append(
                    NoEscape(
                        "\\vspace{-0.4in}\\def\\contentsname{\\empty}\\setcounter{tocdepth}{4}\\tableofcontents")
                )

            # Extra MD before core schema content
            self.doc.append(NoEscape(_add_code_tags(self.extra_md_parts[0])))

    def _add_core_sections(self) -> None:
        self._current_schema = "core"  # Set context for core sections
        core = self.schemas["core"]
        collection = self.schemas["collection"]

        self._schema_object_section(
            "Global Object", core["properties"]["global"])
        self._schema_array_section(
            "Captures Array", core["properties"]["captures"])
        self._schema_array_section(
            "Annotations Array", core["properties"]["annotations"]
        )

        self._current_schema = "collection"  # Change context for collection
        self._schema_object_section(
            "SigMF Collection Format", collection["properties"]["collection"]
        )

        # Extra MD between core and extensions
        self.doc.append(NoEscape(_add_code_tags(self.extra_md_parts[1])))

    def _add_extensions(self) -> None:
        with self.doc.create(Section("Extensions")):
            self._build_antenna_extension()
            self._build_capture_detail_extension()
            self._build_signal_extension()
            self._build_spatial_extension()
            self._build_traceability_extension()

    def _add_subsection(self, title: str, content: str) -> None:
        with self.doc.create(Subsection(title)):
            if content:
                self.doc.append(NoEscape(_add_code_tags(content)))
    # ------------------------------------------------------------------
    # Individual extension builders (each fairly small now!)
    # ------------------------------------------------------------------

    def _build_antenna_extension(self) -> None:
        self._current_schema = "antenna"
        ant = self.schemas["antenna"]
        with self.doc.create(Subsection("Antenna")):
            self._extension_intro(ant)
            self._schema_object_subsubsection(
                "Global", ant["properties"]["global"])
            self._schema_array_subsubsection(
                "Annotations", ant["properties"]["annotations"])
            self._schema_object_subsubsection(
                "Collection", ant["properties"]["collection"])

    def _build_capture_detail_extension(self) -> None:
        self._current_schema = "capture_detail"

        cap = self.schemas["capture_detail"]
        with self.doc.create(Subsection("Capture Detail")):
            self._extension_intro(cap)
            self._schema_array_subsubsection(
                "Captures", cap["properties"]["captures"])
            self._schema_array_subsubsection(
                "Annotations", cap["properties"]["annotations"])

    def _build_signal_extension(self) -> None:
        self._current_schema = "signal"
        sig = self.schemas["signal"]
        with self.doc.create(Subsection("Signal")):
            self._extension_intro(sig)
            annot_props = sig["properties"]["annotations"]["items"]["properties"]
            self._schema_object_subsubsection(
                "Signal Detail", annot_props["signal:detail"])
            self._schema_object_subsubsection(
                "Signal Emitter", annot_props["signal:emitter"])

    def _build_spatial_extension(self) -> None:
        self._current_schema = "spatial"
        spat = self.schemas["spatial"]
        with self.doc.create(Subsection("Spatial")):
            self._extension_intro(spat)

            # Definitions as subsubsection - FIX: Use unique label system
            label = self._unique_label("ssubsec", "Definitions")
            with self.doc.create(Subsubsection("Definitions", label=False)):
                self.doc.append(NoEscape(f"\\label{{{label}}}"))

                self._definition_object(
                    "Bearing Object", spat["$defs"]["bearing"], "bearing")
                self._definition_object(
                    "Cartesian Point Object", spat["$defs"]["cartesian_point"], "cartesian_point")
                self._definition_object(
                    "Calibration Object", spat["$defs"]["calibration"], "calibration")

            # Schema sections as subsubsections
            self._schema_object_subsubsection(
                "Global", spat["properties"]["global"])
            self._schema_array_subsubsection(
                "Captures", spat["properties"]["captures"])
            self._schema_array_subsubsection(
                "Annotations", spat["properties"]["annotations"])
            self._schema_object_subsubsection(
                "Collection", spat["properties"]["collection"])

    def _build_traceability_extension(self) -> None:
        self._current_schema = "traceability"
        tr = self.schemas["traceability"]
        with self.doc.create(Subsection("Traceability")):
            self._extension_intro(tr)

            # Definitions as subsubsection - FIX: Use unique label system
            label = self._unique_label("ssubsec", "Definitions")
            with self.doc.create(Subsubsection("Definitions", label=False)):
                self.doc.append(NoEscape(f"\\label{{{label}}}"))

                self._definition_object(
                    "DataChange Object", tr["$defs"]["DataChange"], "datachange")
                self._definition_object(
                    "Origin Object", tr["$defs"]["Origin"], "origin")

            # Schema sections as subsubsections
            self._schema_object_subsubsection(
                "Global", tr["properties"]["global"])
            self._schema_array_subsubsection(
                "Annotations", tr["properties"]["annotations"])

    # ------------------------------------------------------------------
    # Table / field generation helpers
    # ------------------------------------------------------------------

    def _schema_object_section(self, title: str, schema: Dict[str, Any]) -> None:
        descr = schema.get("description", "")
        with self.doc.create(Subsection(title)):
            if descr:
                self.doc.append(NoEscape(_add_code_tags(descr)))
            # Replace \nn
            self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))
            self._object_table(schema)
            self._field_details(schema)

    def _schema_array_section(self, title: str, schema: Dict[str, Any]) -> None:
        descr = schema.get("description", "")
        with self.doc.create(Subsection(title)):
            if descr:
                self.doc.append(NoEscape(_add_code_tags(descr)))
            items = schema["items"]["anyOf"][0] if "anyOf" in schema["items"] else schema["items"]
            # Replace \nn
            self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))
            self._object_table(items)
            self._field_details(items)

    def _extension_intro(self, schema: Dict[str, Any]) -> None:
        self.doc.append(
            NoEscape(_add_code_tags(schema.get("description", ""))))
        self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))

    def _definition_object(self, title: str, schema: Dict[str, Any], label_name: str) -> None:
        """Add a definition object with proper label and no subsection."""
        self.doc.append(NoEscape("\\vspace{2mm}\\par\\noindent"))
        self.doc.append(NoEscape(f"\\textbf{{{title}}}"))
        self.doc.append(NoEscape(f"\\label{{def:{label_name}}}"))
        self.doc.append(NoEscape("\\vspace{2mm}\\par\\noindent"))
        self._object_table(schema)
        self._field_details_no_subsection(schema)

    def _schema_object_subsubsection(self, title: str, schema: Dict[str, Any]) -> None:
        """Schema object as subsubsection with paragraph field details (for extensions)."""
        descr = schema.get("description", "")
        label = self._unique_label("ssubsec", title)

        with self.doc.create(Subsubsection(title, label=False)):
            self.doc.append(NoEscape(f"\\label{{{label}}}"))

            if descr:
                self.doc.append(NoEscape(_add_code_tags(descr)))
            self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))
            self._object_table(schema)
            # Use paragraph-level field details for extensions
            self._field_details_paragraphs(schema)

    def _schema_array_subsubsection(self, title: str, schema: Dict[str, Any]) -> None:
        """Schema array as subsubsection with paragraph field details (for extensions)."""
        descr = schema.get("description", "")
        label = self._unique_label("ssubsec", title)

        with self.doc.create(Subsubsection(title, label=False)):
            self.doc.append(NoEscape(f"\\label{{{label}}}"))

            if descr:
                self.doc.append(NoEscape(_add_code_tags(descr)))
            items = schema["items"]["anyOf"][0] if "anyOf" in schema["items"] else schema["items"]
            self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))
            self._object_table(items)
            # Use paragraph-level field details for extensions
            self._field_details_paragraphs(items)

    # ---------- LaTeX element builders ------------------------------------

    def _object_table(self, schema: Dict[str, Any]) -> None:
        self.doc.append(NoEscape("\\rowcolors{1}{}{lightblue}"))

        # Use longtable for automatic page breaks
        self.doc.append(
            NoEscape("\\begin{longtable}{p{3.5cm}p{1.8cm}p{2.5cm}p{6.5cm}}"))

        # Header
        self.doc.append(NoEscape("\\toprule"))
        self.doc.append(NoEscape(
            "\\textbf{Field} & \\textbf{Required} & \\textbf{Type} & \\textbf{Short Description} \\\\"))
        self.doc.append(NoEscape("\\midrule"))
        self.doc.append(NoEscape("\\endfirsthead"))

        # Footer
        self.doc.append(NoEscape("\\bottomrule"))
        self.doc.append(NoEscape("\\endlastfoot"))

        # Now add all the table rows
        self._render_longtable_rows(schema)

        self.doc.append(NoEscape("\\end{longtable}"))

    def _definition_table(self, title: str, schema: Dict[str, Any]) -> None:
        # Replace \nn
        self.doc.append(NoEscape("\\vspace{4mm}\\par\\noindent"))
        self.doc.append(NoEscape(f"\\textbf{{{title}}}"))
        self.doc.append(NoEscape("\\vspace{2mm}\\par\\noindent"))
        self._object_table(schema)
        self._field_details(schema)

    def _render_longtable_rows(self, schema: Dict[str, Any]) -> None:
        """Render table rows for longtable (without headers/footers)"""
        props = schema["properties"]
        required_set = set(schema.get("required", []))

        for field_name, field_schema in props.items():
            if "$ref" in field_schema:
                ref_path = field_schema["$ref"]
                if ref_path.startswith("#/$defs/"):
                    type_name = ref_path.split("/")[-1]
                    # Link to definition
                    field_type = f"\\hyperref[def:{type_name.lower()}]{{\\texttt{{{type_name}}}}}"
                else:
                    field_type = "Reference"
            else:
                field_type = field_schema.get("type", "MISSING")

            # Clean description for table use - remove problematic formatting
            desc = field_schema.get("description", "").replace("\n", " ")
            desc = desc.replace("_", r"\_").replace(
                "&", r"\&").replace("#", r"\#")
            # Remove backticks that could break tables
            desc = desc.replace("`", "")
            desc = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", "",
                          desc)  # Remove LaTeX commands

            # Truncate very long descriptions
            if len(desc) > 150:
                desc = desc[:147] + "..."

            # Just escape underscores
            clean_field = _normalise_key(field_name).replace("_", r"\_")

            # Required field text
            required_text = "Required" if field_name in required_set else ""

            # Add the row to longtable
            self.doc.append(
                NoEscape(f"{clean_field} & {required_text} & {field_type} & {desc} \\\\"))

    def _field_details(self, schema: Dict[str, Any]) -> None:
        """Emit subsubsections for every property inside *schema* (for core sections)."""
        props = schema["properties"]
        for field_name, field_schema in props.items():
            clean = _normalise_key(field_name)
            label = self._unique_label("ssubsec", clean)

            # Create subsubsection for core sections (appears in TOC)
            # Use label=False to prevent PyLaTeX from auto-generating labels
            with self.doc.create(Subsubsection(clean, label=False)):
                # Now add our unique label
                self.doc.append(NoEscape(f"\\label{{{label}}}"))

                if "description" in field_schema:
                    self.doc.append(
                        NoEscape(_add_code_tags(field_schema["description"])))

                # Dump all other keys
                for k, v in field_schema.items():
                    if k in {"$id", "description", "items", "additionalItems", "pattern"}:
                        continue
                    self.doc.append("\n")
                    self.doc.append(bold(k))
                    self.doc.append(": ")
                    self.doc.append(str(v))

    def _field_details_paragraphs(self, schema: Dict[str, Any]) -> None:
        """Emit paragraph-level sections for every property inside *schema* (for extensions)."""
        props = schema["properties"]
        for field_name, field_schema in props.items():
            clean = _normalise_key(field_name)
            label = self._unique_label("field", clean)

            # Create a paragraph-level section for extensions (appears in TOC)
            self.doc.append(NoEscape(f"\\paragraph{{{clean}}}"))
            # Fix: Use the unique label, not a hardcoded one
            self.doc.append(NoEscape(f"\\label{{{label}}}"))

            # Handle $ref fields specially
            if "$ref" in field_schema:
                ref_path = field_schema["$ref"]
                if ref_path.startswith("#/$defs/"):
                    ref_name = ref_path.split("/")[-1]
                    self.doc.append(NoEscape(
                        f"This field references the \\hyperref[def:{ref_name.lower()}]{{{ref_name}}} object type."))
                else:
                    self.doc.append(f"References: {ref_path}")
                continue

            # Handle regular fields
            if "description" in field_schema:
                self.doc.append(
                    NoEscape(_add_code_tags(field_schema["description"])))

                # Dump all other keys
                for k, v in field_schema.items():
                    if k in {"$id", "description", "items", "additionalItems", "pattern"}:
                        continue
                    self.doc.append("\n")
                    self.doc.append(bold(k))
                    self.doc.append(": ")
                    self.doc.append(str(v))

    def _field_details_no_subsection(self, schema: Dict[str, Any]) -> None:
        """Field details without creating subsubsections (for definitions)."""
        props = schema["properties"]
        for field_name, field_schema in props.items():
            clean = _normalise_key(field_name)
            label = self._unique_label("field", clean)

            # Add field as paragraph instead of subsubsection
            self.doc.append(NoEscape("\\vspace{2mm}\\par\\noindent"))
            self.doc.append(NoEscape(f"\\textbf{{{clean}}}"))
            # Fix: Use the unique label, not a hardcoded one
            self.doc.append(NoEscape(f"\\label{{{label}}}"))
            self.doc.append(NoEscape("\\par\\noindent"))

            # Handle $ref fields specially - SAME AS _field_details_paragraphs
            if "$ref" in field_schema:
                ref_path = field_schema["$ref"]
                if ref_path.startswith("#/$defs/"):
                    ref_name = ref_path.split("/")[-1]
                    self.doc.append(NoEscape(
                        f"This field references the \\hyperref[def:{ref_name.lower()}]{{{ref_name}}} object type."))
                else:
                    self.doc.append(f"References: {ref_path}")
                continue

            # Handle regular fields
            if "description" in field_schema:
                self.doc.append(
                    NoEscape(_add_code_tags(field_schema["description"])))

            # Add other field properties
            for k, v in field_schema.items():
                if k in {"$id", "description", "items", "additionalItems", "pattern"}:
                    continue
                self.doc.append("\n")
                self.doc.append(bold(k))
                self.doc.append(": ")
                self.doc.append(str(v))
    # ------------------------------------------------------------------
    # Build/compile helpers
    # ------------------------------------------------------------------

    def _compile_html(self, tex_path: Path) -> None:
        css_file = Path("main.css")
        css_file.write_text(self._bootstrap_css())
        css_url = "https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css"
        subprocess.run([
            "pandoc",
            tex_path.name,
            "-f",
            "latex",
            "-t",
            "html",
            "-s",
            "-o",
            f"{OUTPUT_BASENAME}.html",
            "--toc",
            "--toc-depth=3",
            "-c",
            css_url,
            "-c",
            str(css_file),
        ], check=True)

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------

    def _unique_label(self, prefix: str, text: str) -> str:
        """Generate a unique, LaTeX-safe label."""
        # Clean the text for LaTeX labels but preserve more context
        # Replace colons with underscores, keep alphanumeric and underscores
        clean_text = re.sub(r'[^a-zA-Z0-9_]', '',
                            text.lower().replace(':', '_'))

        # Include current schema context to make labels unique
        base = f"{prefix}_{self._current_schema}_{clean_text}"
        counter = 1
        label = base
        while label in self._labels:
            label = f"{base}_{counter}"
            counter += 1
        self._labels.add(label)
        return label

    def _bootstrap_css(self) -> str:
        return (
            "#TOC { position: fixed; width: 20em; left: -1em; top: 0; height: 100%; "
            "background-color: white; overflow-y: scroll; padding: 0; }\n"
            "#subsec\\:TableofContents { display: none; }\n"
            "body { padding-left: 20em; }\n"
            "@media (max-width:800px){ #TOC {display:none; width: 0em;} body {padding-left: 0em;} }\n"
            "code { color: #000; font-family: monospace; background: #f4f4f4; }\n"
            "tr:nth-of-type(odd) { background-color:#f0f0ff; }"
        )

# ---------------------------------------------------------------------------
# CLI entry‑point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    generator = SigMFDocGenerator(
        SCHEMA_PATHS, LOGO_PATH, ADDITIONAL_CONTENT_MD)
    generator.build_pdf_and_html()
