
from django.urls import path
from .views import *

urlpatterns = [
    path('process', FileUploadAPIView.as_view(), name='file_upload_api'),
    path('deleteimg', ImgFileAPIView.as_view(), name='delete_img_api'),
    path('deletecsv', CSVFileAPIView.as_view(), name='delete_csv_api'),
    # Add other URLs as needed
]