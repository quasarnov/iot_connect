from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Device(models.Model):
    # User who created the device
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Device name
    name = models.CharField(max_length=100)
    # Device serial
    serial = models.CharField(max_length=10)
    # Device description
    description = models.TextField(null=True, blank=True)
    # Creation date
    creation_date = models.DateTimeField(auto_now_add=True)
    # Other fields can be added here
    def __str__(self):
        return self.name

class Measurement(models.Model):
    # Foreign Key to the Device model
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    # ArrayField for storing multiple values
    values = ArrayField(models.FloatField())
    # Timestamp field with auto_now_add
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Measurement from {self.device} at {self.timestamp}"