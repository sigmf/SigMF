from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
class Field(models.Model):
    key_name = models.CharField(max_length=200)
    key_category = models.CharField(max_length=200)
    key_required = models.BooleanField(default=False)
    key_help = models.TextField(blank=True)
    value_type = models.CharField(max_length=200)
    value_format = models.CharField(max_length=200, blank=True)

    @python_2_unicode_compatible
    def __str__(self):
        return ("key = " + self.key_name + " ["
                + self.value_type + "], "
                + " required = " + str(self.key_required))
