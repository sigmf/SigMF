import json
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "webapp.settings"
django.setup()
from validator.models import Field

schema = json.load(open('../sigmf/schema.json'))
global_keys = schema["global"]["keys"].keys()
capture_keys = schema["capture"]["keys"].keys()
annotations_keys = schema["annotations"]["keys"].keys()

Field.objects.all().delete()
for field in global_keys:
    curr_key = schema["global"]["keys"][field]
    gf = Field(key_name=field,
                        key_required=curr_key["required"],
                        value_type=curr_key["type"],
                        key_help=curr_key["help"],
                        key_category="global")
    gf.save()

for field in capture_keys:
    curr_key = schema["capture"]["keys"][field]
    gf = Field(key_name=field,
                        key_required=curr_key["required"],
                        value_type=curr_key["type"],
                        key_help=curr_key["help"],
                        key_category="capture")
    gf.save()

for field in annotations_keys:
    curr_key = schema["annotations"]["keys"][field]
    gf = Field(key_name=field,
                        key_required=curr_key["required"],
                        value_type=curr_key["type"],
                        key_help=curr_key["help"],
                        key_category="annotations")
    gf.save()
