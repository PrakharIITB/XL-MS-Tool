# serializers.py
from rest_framework import serializers
from .models import *

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['csv_file', 'gz_file']

class ProcessedFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedFiles
        fields = '__all__'

class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = '__all__'

class ImgFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImgFile
        fields = '__all__'


