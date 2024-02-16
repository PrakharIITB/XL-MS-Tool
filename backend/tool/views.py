# views.py
import time
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .input_proccesor import inputProcessor
from .main import mainApp

def delete_files(dir, ext=None):
    if ext:
        files = [f for f in os.listdir(dir) if f.endswith(ext)]
        for file in files:
            file_path = os.path.join(dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return
    try:
        files = os.listdir(dir)
        for file in files:
            file_path = os.path.join(dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except OSError:
        print('Error while deleting files')



class FileUploadAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        choice = request.data['choice']
        print('Choice: ', choice)
        currtime = time.time()
        if serializer.is_valid():
            serializer.save()
            workdir = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"
            csv_file = os.listdir(workdir+'/static/csv')[0]
            gz_file = os.listdir(workdir+'/static/gz')[0]
            print('Processing the files...')
            process = mainApp(30, workdir+'/static/csv/'+csv_file, workdir+'/static/gz/'+gz_file, choice)

            print('Time taken to process the files: ', time.time()-currtime)
            created_img_files = []
            created_csv_files = []
            files = os.listdir(os.path.join(workdir, choice))
            for file in files:
                if file.endswith('.csv') or file.endswith('.xlsx'):
                    csv_file_obj = CSVFile.objects.create(
                        csv_file=file
                    )
                    created_csv_files.append(csv_file_obj)
                elif file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                    img_file_obj = ImgFile.objects.create(
                        image_file=file
                    )
                    created_img_files.append(img_file_obj)
                
                delete_files(workdir+'/static/csv')
                delete_files(workdir+'/static/gz')
                delete_files(workdir+'/'+choice, '.cif')

            csv_files_objects = CSVFileSerializer(created_csv_files, many=True)
            img_files_objects = ImgFileSerializer(created_img_files, many=True)

            response_data = {
                'csv_files': csv_files_objects.data,
                'image_files': img_files_objects.data
            }


            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CSVFileAPIView(APIView):    
    def delete(self, request):
        csv_files = CSVFile.objects.all()
        csv_files.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ImgFileAPIView(APIView):
    def delete(self, request):
        img_files = ImgFile.objects.all()
        img_files.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
