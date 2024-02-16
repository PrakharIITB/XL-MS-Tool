from django.db import models

class UploadedFile(models.Model):
    csv_file = models.FileField(upload_to='static/csv/')
    gz_file = models.FileField(upload_to='static/gz/')

class CSVFile(models.Model):
    csv_file = models.FileField(upload_to='static/output/')
    def __str__(self):
        return self.csv_file

class ImgFile(models.Model):
    image_file = models.FileField(upload_to='static/output/')
    def __str__(self):
        return self.image_file

class ProcessedFiles(models.Model):
    csv_files = models.ManyToManyField(CSVFile)
    image_files = models.ManyToManyField(ImgFile)
