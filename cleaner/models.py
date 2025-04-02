from django.db import models

# Create your models here.
class File(models.Model):
    file = models.FileField(upload_to='files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file.name
    
class DatasetStatistics(models.Model):
    file = models.OneToOneField(File,on_delete=models.CASCADE)
    count = models.IntegerField()
    mean = models.FloatField()
    std = models.FloatField()
    min_value = models.FloatField()
    percentile_25 = models.FloatField()
    percentile_50 = models.FloatField()
    percentile_75 = models.FloatField()
    max_value = models.FloatField()
    
    def __str__(self):
        return f"Statistics of {self.file.file.name}"