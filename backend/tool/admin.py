from django.contrib import admin
from .models import *

# Register your models here.
admin.register(CSVFile)
admin.register(ImgFile)
admin.register(UploadedFile)
admin.register(ProcessedFiles)