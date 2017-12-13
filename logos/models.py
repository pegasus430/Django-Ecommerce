from __future__ import unicode_literals

from django.db import models

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class LabelLogo(models.Model):
    name = models.CharField(max_length=100)
    custom_label_logo = models.ImageField(
        upload_to='media/logos/label_logo/%Y/%m/%d', 
        blank=True,
        null=True,)
    custom_label_logo_optimised = ImageSpecField(source='custom_label_logo',
        processors=[ResizeToFit(500, 500)],
        format='JPEG',
        options={'quality': 60})

    def __unicode__(self):
        return self.name