
import datetime
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import JSONField
from theorema.orgs.models import Organization

SERVER_TYPES = [
    ('full', 'full'),
    ('analysis', 'analysis'),
    ('storage', 'storage')
]
class Server(models.Model):
    parent_server_id=models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField()
    local_address = models.GenericIPAddressField(default='0.0.0.0')
    organization = models.ForeignKey(Organization)
    type = models.CharField(choices=SERVER_TYPES, default='full', max_length=8)


class CameraGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    organization = models.ForeignKey(Organization)

class QuadratorGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    organization = models.ForeignKey(Organization)

CameraAnalysisTypes = [
    (1, 'Full'),
    (2, 'Move'),
    (3, 'Record'),
]

CameraResolutions = [
    (1, '360'),
    (2, '480'),
    (3, '720'),
    (4, 'HD'),
    (5, '2K'),
    (6, '4K'),
]

class Camera(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=400)
    fps = models.SmallIntegerField(default=10) # deprecated
    analysis = models.SmallIntegerField(choices=CameraAnalysisTypes, default=1)
    resolution = models.SmallIntegerField(choices=CameraResolutions, default=1) # deprecated
    storage_life = models.IntegerField(default=7)
    compress_level = models.SmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
