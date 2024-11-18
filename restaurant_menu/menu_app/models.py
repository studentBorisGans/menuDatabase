# Defines data structures for app
from django.db import models

# Create your models here.
class ProcessedData(models.Model):
    data = models.TextField()
    uploadedTime = models.DateTimeField(auto_now_add=True)

    