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



class FileUploadAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        choice = request.data['choice']
        threshold = int(request.data['threshold'])
        print('Choice: ', choice)
        currtime = time.time()
        if serializer.is_valid():
            serializer.save()
            workdir = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"
            csv_file = os.listdir(workdir+'/static/csv')[0]
            gz_file = os.listdir(workdir+'/static/gz')[0]
            print('Processing the files...')
            process = mainApp(threshold, workdir+'/static/csv/'+csv_file, workdir+'/static/gz/'+gz_file, choice)

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
                delete_files(workdir+"/"+choice+"/alphafold_structures", '.cif')

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

class ValidateAPIView(APIView):
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        choice = request.data['choice']
        if serializer.is_valid():
            serializer.save()
            workdir = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"
            csv_file = os.listdir(workdir+'/static/csv')[0]
            zip_file = os.listdir(workdir+'/static/zip')[0]
            validate = Validate(workdir+'/static/zip/'+zip_file, workdir+'/static/csv/'+csv_file, choice)
            result = validate.validate()
            print(result)
            return JsonResponse(status=status.HTTP_201_CREATED, data=result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        workdir = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"
        delete_files(workdir+'/static/csv')
        delete_files(workdir+'/static/gz')
        delete_files(workdir+'/static/zip')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProcessManualView(APIView):
    def post(self, request):
        try:
            threshold = int(request.data['threshold'])
            choice  = request.data['choice']
            print('Choice: ', choice)
            workdir = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"
            csv_file = os.listdir(workdir+'/static/csv')[0]
            gz_file = os.listdir(workdir+'/static/gz')[0]
            zip_file = os.listdir(workdir+'/static/zip')[0]
            unzip_folder(workdir+'/static/zip/'+zip_file, workdir+"/"+choice+"/"+"manual_structures")
            print('Processing the files...')
            process = mainApp(threshold, workdir+'/static/csv/'+csv_file, workdir+'/static/gz/'+gz_file, choice, "manual")
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
            delete_files(workdir+'/static/zip')
            delete_files(workdir+"/"+choice+"/manual_structures", '.cif')
            delete_files(workdir+"/"+choice+"/alphafold_structures", '.cif')

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
    


    
