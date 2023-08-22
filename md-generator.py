import yaml
from py_markdown_table.markdown_table import markdown_table

sigmf_version = 'v1.0.0'
data=yaml.safe_load(open('sigmf.schema.yaml', 'r'))

def gen_table(d):
    table = []
    for key, value in d["properties"].items():
        newdict = {"Field": '[`' + key.replace('core:','') + '`](#' + key.replace('core:','') + ')'}
        newdict["Required"] = "Required" if key in d["required"] else ""
        newdict["Type"] = value.get("type", "MISSING")
        newdict["Default"] = str(value.get("default", ""))
        description = value.get("description", "")
        indx = description.find('.')
        newdict["Short Description"] = description[:indx].replace('\n','') # short description, which is up to the first period
        table.append(newdict)
    return markdown_table(table).set_params(quote=False, row_sep = 'markdown', padding_weight='right').get_markdown()

def gen_fields(d):
    fields_str = ''
    for key, value in d["properties"].items():
        fields_str += "### " + key.replace('core:','') + '\n\n'
        fields_str += value["description"] + '\n\n'
        for key2, value2 in d["properties"][key].items():
            if key2 not in ['$id', 'description', 'items', 'additionalItems']:
                fields_str += '**' + key2 + '**: ' + str(value2) + '  \n' # two spaces cause a linebreak instead of new paragraph
        fields_str += '\n'
    return fields_str

md = '# Signal Metadata Format Specification ' + sigmf_version + '\n\n'
md += data["description"] + '\n'
md += "## Global Object\n\n" + data["properties"]["global"]["description"].replace('. ','.\n') + '\n\n'
md += gen_table(data["properties"]["global"]) + '\n\n'
md += gen_fields(data["properties"]["global"])
md += "## Captures Array\n\n" + data["properties"]["captures"]["description"] + '\n\n'
md += gen_table(data["properties"]["captures"]["items"]["anyOf"][0]) + '\n\n'
md += gen_fields(data["properties"]["captures"]["items"]["anyOf"][0])
md += "## Annotations Array\n\n" + data["properties"]["annotations"]["description"] + '\n\n'
md += gen_table(data["properties"]["annotations"]["items"]["anyOf"][0]) + '\n\n'
md += gen_fields(data["properties"]["annotations"]["items"]["anyOf"][0])

open('sigmf-spec.md', 'w').write(md)
