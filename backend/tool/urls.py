
from django.urls import path
from .views import *

urlpatterns = [
    path('process', AutomaticProcessAPIView.as_view(), name='file_upload_api'),
    path('deleteimg', ImgFileAPIView.as_view(), name='delete_img_api'),
    path('deletecsv', CSVFileAPIView.as_view(), name='delete_csv_api'),
    path('validate', ValidateAPIView.as_view(), name='validate_api'),
    path('processmanual', ProcessManualView.as_view(), name='process_manual_api')
    # Add other URLs as needed
]