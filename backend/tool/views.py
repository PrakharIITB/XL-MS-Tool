# views.py
import time
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import zipfile
from .models import *
from .serializers import *
from .input_proccesor import inputProcessor
from .main import mainApp
from .validate import Validate
import shutil

CSV_PATH = os.path.join(os.getcwd(), 'output', 'static', 'csv')
GZ_PATH = os.path.join(os.getcwd(), 'output', 'static', 'gz')
ZIP_PATH = os.path.join(os.getcwd(), 'output', 'static', 'zip')
WORKDIR = os.path.join(os.getcwd(), 'output')

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

def unzip_folder(zip_file_path, extract_to_path):
    # Create the target directory if it doesn't exist
    if not os.path.exists(extract_to_path):
        os.makedirs(extract_to_path)

    # Unzip the folder
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_path)

    # Move the contents of the extracted folder to the target directory
    extracted_folder = os.path.join(extract_to_path, os.path.basename(zip_file_path).split('.')[0])
    for item in os.listdir(extracted_folder):
        item_path = os.path.join(extracted_folder, item)
        target_path = os.path.join(extract_to_path, item)
        shutil.move(item_path, target_path)

    # Remove the now-empty extracted folder
    os.rmdir(extracted_folder)



class AutomaticProcessAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        choice = request.data['choice']
        threshold = int(request.data['threshold'])
        print('Choice: ', choice)
        currtime = time.time()
        if serializer.is_valid():
            serializer.save()
            csv_file = os.path.join(CSV_PATH, os.listdir(CSV_PATH)[0])
            gz_file = os.path.join(GZ_PATH, os.listdir(GZ_PATH)[0])
            print(csv_file, gz_file)
            print('Processing the files...')
            process = mainApp(threshold, csv_file, gz_file, choice)

            print('Time taken to process the files: ', time.time()-currtime)
            created_img_files = []
            created_csv_files = []
            files = os.listdir(os.path.join(WORKDIR, choice))
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
                
                delete_files(CSV_PATH)
                delete_files(GZ_PATH)
                delete_files(os.path.join(WORKDIR, choice, "alphafold_structures"), '.cif')

            csv_files_objects = CSVFileSerializer(created_csv_files, many=True)
            img_files_objects = ImgFileSerializer(created_img_files, many=True)

            response_data = {
                'csv_files': csv_files_objects.data,
                'image_files': img_files_objects.data
            }


            return Response(response_data, status=status.HTTP_201_CREATED)
            # return Response(status=status.HTTP_200_OK, data={'message': 'Files processed successfully'})


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

class ValidateAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        choice = request.data['choice']
        if serializer.is_valid():
            serializer.save()
            csv_file = os.path.join(CSV_PATH, os.listdir(CSV_PATH)[0])
            zip_file = os.path.join(ZIP_PATH, os.listdir(ZIP_PATH)[0])
            validate = Validate(zip_file, csv_file, choice)
            result = validate.validate()
            return JsonResponse(status=status.HTTP_201_CREATED, data=result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        delete_files(CSV_PATH)
        delete_files(GZ_PATH)
        delete_files(ZIP_PATH)
        return Response(status=status.HTTP_204_NO_CONTENT, message='Files deleted successfully')
    
class ProcessManualView(APIView):
    def post(self, request):
        try:
            threshold = int(request.data['threshold'])
            choice  = request.data['choice']
            print('Choice: ', choice)
            csv_file = os.path.join(CSV_PATH, os.listdir(CSV_PATH)[0])
            zip_file = os.path.join(ZIP_PATH, os.listdir(ZIP_PATH)[0])
            gz_file = os.path.join(GZ_PATH, os.listdir(GZ_PATH)[0])
            unzip_folder(zip_file, os.path.join(WORKDIR, choice, 'manual_structures'))
            print('Processing the files...')
            process = mainApp(threshold, csv_file, gz_file, choice, "manual")
            created_img_files = []
            created_csv_files = []
            files = os.listdir(os.path.join(WORKDIR, choice))
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
                
            delete_files(CSV_PATH)
            delete_files(GZ_PATH)
            delete_files(ZIP_PATH)
            delete_files(os.path.join(WORKDIR, choice, "alphafold_structures"), '.cif')
            delete_files(os.path.join(WORKDIR, choice, "manual_structures"), '.cif')

            # delete_files(workdir+'/'+choice, '.cif')
            csv_files_objects = CSVFileSerializer(created_csv_files, many=True)
            img_files_objects = ImgFileSerializer(created_img_files, many=True)

            response_data = {
                'csv_files': csv_files_objects.data,
                'image_files': img_files_objects.data
            }
            return Response(status=status.HTTP_201_CREATED, data=response_data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    


    
