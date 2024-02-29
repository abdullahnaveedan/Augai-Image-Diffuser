from django.shortcuts import render,redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import *
import shutil
from PIL import Image
import PIL
import os
import glob
from random import randrange
from django.http import HttpResponse, FileResponse
import zipfile
from io import BytesIO
from django.contrib import messages
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView , ListAPIView
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from django.contrib.auth import authenticate , login as auth_login , logout as auth_logout
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import re

# Create your views here.

def index(request):
    return render(request,"index.html")

def diffuseImg(request):
    return render(request,"diffuse.html")

def loginPage(request):
    if request.user.is_authenticated:
        return redirect("diffuseImage")
    return render(request , "loginPage.html")

def accountslogin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            un = User.objects.get(email = email)    
            user = authenticate(request , username = un.username, password = password)
            if user:
                auth_login(request , user)
                return JsonResponse({'status': 'login', 'message': 'Login Sucessfully'})
            else:
                return JsonResponse({'status': 'invalid', 'message': 'Invalid email or password.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Email and password does not exist.'})
    return JsonResponse({'status': 'error', 'message': 'Server error. Retry in a few seconds.'})
    
def logout(request):
    auth_logout(request)
    return redirect("index")

def applyAlgo(zippath,number_of_folder , image_title):
    extract_path = f'zipextrection'
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.mkdir(extract_path)

    with zipfile.ZipFile(zippath, 'r') as zObject:
        zObject.extractall(path=extract_path)

    """**Read all the files and check the extention. If extention is invalid then remove the file**"""

    def list_files(folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return files

    image_extensions = ['.jpg', '.jpeg', '.png' , '.tiff']

    for file_name in list_files(extract_path):
        ext = os.path.splitext(file_name)[1]
        
        if ext.lower() not in image_extensions:
            os.remove(extract_path+'/' + file_name)

    file_names = list_files(extract_path)

    """**Create new directory and make n folders**"""

    mainDir = 'unique-images-folders'

    if os.path.exists(mainDir):
        shutil.rmtree(mainDir)

    os.mkdir(mainDir)

    n = int(number_of_folder) # input by user
    for i in range(0 , n):
        os.mkdir(mainDir + '/' + 'unique-folder-' + str(i + 1))

    """**Algorithm**"""

    for i in range(n):
        for x , file_name in enumerate(file_names):
            original_path = extract_path + '/' + file_name
            newimgpath = mainDir + '/'+"unique-folder-"+str(i+1)+'/'+"u-image-" + str(x+1) + ".jpg"
            shutil.copyfile(original_path, newimgpath)
            picture = Image.open(newimgpath)
            picture = picture.convert('RGB')
            randnum = randrange(50, 99)
            picture.save(newimgpath,'JPEG', optimize=True,quality=randnum)
    zip_main_dir = shutil.make_archive(image_title, 'zip', mainDir)
    
    if os.path.exists("unique-images-folders"):
            shutil.rmtree("unique-images-folders")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    if os.path.exists(zippath):
        os.remove(zippath)

def createAccount(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
    
        if password != confirmPassword:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})
        
        if not re.match("^[a-zA-Z0-9]+$", username):
            return JsonResponse({'status': 'error', 'message': 'Username can only contain alphanumeric characters.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username is already taken. Choose a different one.'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email is already registered. Choose a different one.'})

        if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password) and any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password) and len(password) >= 8):
            return JsonResponse({'status': 'error', 'message': 'Enter password containing numeric digits, alphabets and special chracters.'})
    
        user = User.objects.create_user(
            username = username,
            email=email,
            password=password
        )
        
        user  = authenticate(request , username = username , password = password)
        if user:
            auth_login(request , user)
            return JsonResponse({'status': 'success'})
        else:
            print("Password doesnot same")    
    return JsonResponse({'status': 'error', 'message': 'Some thing went wrong'})

def submitRecord(request):
    if request.method == "POST":
        image_title = "unique-image"
        number_of_folder = 1
        images = request.FILES.getlist('images')
        
        newFolder = r'media/multipleImage/' + image_title
        if os.path.exists(newFolder):
            shutil.rmtree(newFolder)
        os.mkdir(newFolder)
        for image in images:
            multi_img_file = default_storage.save('multipleImage/' + image.name, ContentFile(image.read()))
            shutil.move('media/multipleImage/' + image.name , newFolder)

            multiImg(
                image_title=image.name,
                number_of_folders=number_of_folder,
                input_image=multi_img_file
                ).save()
        zipfile = shutil.make_archive(newFolder, 'zip', newFolder)
        shutil.rmtree(newFolder)
        zippath = "media/multipleImage/" + image_title+'.zip'
        applyAlgo(zippath,number_of_folder , image_title)
        return JsonResponse({'status' : 'success'})
    return redirect("diffuseImage")

def download(request):
    try:
        image_title = "unique-image"
        zip_main_dir = os.path.join(settings.BASE_DIR , f"{image_title}.zip")
        with open(zip_main_dir, 'rb') as zip_file:
            zip_buffer = BytesIO(zip_file.read())
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{image_title}.zip"'
        return response
    finally:
        if os.path.exists(zip_main_dir):
            os.remove(zip_main_dir)