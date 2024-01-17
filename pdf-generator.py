import yaml
from py_markdown_table.markdown_table import markdown_table
import numpy as np
from pylatex import Document, Section, Subsection, Subsubsection, Package, Tabular, Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic, bold, NoEscape
import os
import json

sigmf_version = 'v1.0.0' # TODO PULL FROM SCHEMA
with open('sigmf-schema.json', 'r') as f:
    data = json.load(f)
with open('collection-schema.json', 'r') as f:
    data_collection = json.load(f)
with open('extensions/antenna-schema.json', 'r') as f:
    data_antenna = json.load(f)

def add_code_tags(text): # swaps every pair of ` ` for \code{}
    while text.find('`') != -1:
        text = text.replace('`', '\\code{', 1)
        text = text.replace('`', '}', 1)
    return text

def gen_table(table, d):
    table.add_hline()
    table.add_row((bold('Field'), bold('Required'), bold('Type'), bold('Short Description')))
    table.add_hline()
    for key, value in d["properties"].items():
        field = key.replace('core:','')
        required = "Required" if key in d.get("required", {}) else ""
        dtype = value.get("type", "MISSING")
        #default = str(value.get("default", ""))
        longdescription = value.get("description", "")
        shortdescription = longdescription[:longdescription.find('.')].replace('\n','') # short description, which is up to the first period
        table.add_row((field, required, dtype, shortdescription))
        table.add_hline()

def gen_fields(doc, d):
    for key, value in d["properties"].items():
        with doc.create(Subsubsection(key.replace('core:',''))):
            doc.append(NoEscape(add_code_tags(value["description"]))) # NoEscape allows latex commands within the description
            for key2, value2 in d["properties"][key].items():
                if key2 not in ['$id', 'description', 'items', 'additionalItems', 'pattern']: # pattern had issues with latex that need to be fixed first
                    doc.append('\n')
                    doc.append(bold(key2))
                    doc.append(': ')
                    doc.append(str(value2))

geometry_options = {"tmargin": "1in", "lmargin": "1in", "rmargin": "1in", "bmargin": "1in"}
doc = Document(geometry_options=geometry_options)
doc.packages.append(Package('underscore')) # makes it so _ never means math mode!
doc.packages.append(Package('xcolor'))
doc.packages.append(Package('listings'))
doc.packages.append(Package('microtype'))
doc.packages.append(Package('fancyhdr'))
doc.packages.append(Package('hyperref', options=['hidelinks','colorlinks=true','urlcolor=blue','linkcolor=black'])) #\usepackage[, urlcolor=blue, linkcolor=red]{hyperref}

doc.append(NoEscape('\\newcommand{\\code}[1]{\\texttt{\colorbox{lightgray}{#1}}}'))
doc.append(NoEscape('\\definecolor{lightgray}{RGB}{240,240,240}'))
doc.append(NoEscape('\\newcommand{\\nn}[0]{\\vspace{4mm}\\\\\\noindent}'))

# Footer
doc.append(NoEscape('\\pagestyle{fancy}'))
doc.append(NoEscape('\\fancyhf{}')) # clear all header/footer fields
doc.append(NoEscape('\\renewcommand{\headrulewidth}{0pt}'))
doc.append(NoEscape('\\fancyfoot[LE,RO]{\\thepage}'))
doc.append(NoEscape('\\fancyfoot[LO,CE]{Signal Metadata Format (SigMF) Specification ' + sigmf_version + '}'))
#doc.append(NoEscape('\\fancyfoot[CO,RE]{To: Dean A. Smith}')) # center

with doc.create(Figure(position='h!')) as logo:
    doc.append(NoEscape('\\vspace{-0.8in})'))
    logo.add_image('logo/sigmf_logo.png', width='120px')
    
with doc.create(Section('Signal Metadata Format (SigMF) Specification ' + sigmf_version)):
    with doc.create(Subsection('Abstract')): # Abstract lives in the JSON Schema
        doc.append(data["description"])

    with doc.create(Subsection('Copyright Notice')):
        doc.append(NoEscape('This document is available under the \href{http://creativecommons.org/licenses/by-sa/4.0/}{CC-BY-SA License}. Copyright of contributions to SigMF are retained by their original authors. All contributions under these terms are welcome.'))

    with doc.create(Subsection('Table of Contents')): # NOTE- YOU NEED TO COMPILE LATEX TWICE FOR THIS TO SHOW!
        doc.append(NoEscape('\\vspace{-0.4in}\\def\\contentsname{\\empty}\\setcounter{tocdepth}{3}\\tableofcontents'))

    doc.append(NoEscape(add_code_tags(open('additional_content.md', 'r').read().split('<<<<<<<<<<content from JSON schema>>>>>>>>>>>>')[0])))

    with doc.create(Subsection('Global Object')):
        doc.append(NoEscape(add_code_tags(data["properties"]["global"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data["properties"]["global"])
        gen_fields(doc, data["properties"]["global"])

    with doc.create(Subsection('Captures Array')):
        doc.append(NoEscape(add_code_tags(data["properties"]["captures"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data["properties"]["captures"]["items"]["anyOf"][0])
        gen_fields(doc, data["properties"]["captures"]["items"]["anyOf"][0])

    with doc.create(Subsection('Annotations Array')):
        doc.append(NoEscape(add_code_tags(data["properties"]["annotations"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data["properties"]["annotations"]["items"]["anyOf"][0])
        gen_fields(doc, data["properties"]["annotations"]["items"]["anyOf"][0])

    with doc.create(Subsection('SigMF Collection Format')):
        doc.append(NoEscape(add_code_tags(data_collection["properties"]["collection"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data_collection["properties"]["collection"])
        gen_fields(doc, data_collection["properties"]["collection"])
    
    doc.append(NoEscape(add_code_tags(open('additional_content.md', 'r').read().split('<<<<<<<<<<content from JSON schema>>>>>>>>>>>>')[1])))

with doc.create(Section('Extensions')):
    with doc.create(Subsection('Antenna')):
        doc.append(NoEscape(add_code_tags(data_antenna["properties"]["global"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{2.8in}|')) as table:
            gen_table(table, data_antenna["properties"]["global"])
        gen_fields(doc, data_antenna["properties"]["global"])

        doc.append(NoEscape('\\nn'))
        doc.append(NoEscape(add_code_tags(data_antenna["properties"]["annotations"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data_antenna["properties"]["annotations"]["items"]["anyOf"][0])
        gen_fields(doc, data_antenna["properties"]["annotations"]["items"]["anyOf"][0])

        doc.append(NoEscape('\\nn'))
        doc.append(NoEscape(add_code_tags(data_antenna["properties"]["collection"]["description"])))
        doc.append('\n\n')
        with doc.create(Tabular('|l|l|l|p{3.8in}|')) as table:
            gen_table(table, data_antenna["properties"]["collection"])
        gen_fields(doc, data_antenna["properties"]["collection"])

doc.generate_pdf('sigmf-spec', clean_tex=False) # clean_tex will remove the generated tex file
