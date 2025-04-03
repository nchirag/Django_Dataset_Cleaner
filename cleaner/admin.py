from django.contrib import admin
from .models import *

admin.site.register(File)
admin.site.register(DatasetStatistics)
admin.site.register(DetectedIssue)

# Register your models here.
