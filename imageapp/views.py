from django.shortcuts import render,redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import *
import shutil
from PIL import Image
import os
from random import randrange
from django.http import HttpResponse
import zipfile
from io import BytesIO
from django.contrib.auth import authenticate , login as auth_login , logout as auth_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
import re
from django.conf import settings
import openai
from string import punctuation

from .serializers import *
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



BASE_DIR = settings.BASE_DIR

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

def applyAlgo(zip_path,number_of_folder , image_title):
    extract_path = os.path.join(BASE_DIR , 'zipextrection')

    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.mkdir(extract_path)
    

    with zipfile.ZipFile(zip_path, 'r') as zObject:
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

    main_dir = os.path.join(BASE_DIR , 'unique-images-folders')

    if os.path.exists(main_dir):
        shutil.rmtree(main_dir)

    os.mkdir(main_dir)

    n = int(number_of_folder) # input by user
    for i in range(0 , n):
        os.mkdir(main_dir + '/' + 'unique-folder-' + str(i + 1))

    """**Algorithm**"""

    for i in range(n):
        for x , file_name in enumerate(file_names):
            original_path = extract_path + '/' + file_name
            newimgpath = main_dir + '/'+"unique-folder-"+str(i+1)+'/'+"u-image-" + str(x+1) + ".jpg"
            shutil.copyfile(original_path, newimgpath)
            picture = Image.open(newimgpath)
            picture = picture.convert('RGB')
            randnum = randrange(50, 99)
            picture.save(newimgpath,'JPEG', optimize=True,quality=randnum)
    zip_main_dir = shutil.make_archive(os.path.join(BASE_DIR , image_title), 'zip', main_dir)
    
    if os.path.exists(main_dir):
            shutil.rmtree(main_dir)
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    if os.path.exists(zip_path):
        os.remove(zip_path)

@api_view(['POST'])
def createAccount(request):
    data = request.data
    serializer = UserSerializer(data = data)
    print(serializer)
    serializer.save()
    return Response({'status' :200 , 'payload' : data , 'message' : "Saved in DB"})

    # if request.method == "POST":
    #     username = request.POST.get('username')
    #     email = request.POST.get('email')
    #     password = request.POST.get('password')
    #     confirmPassword = request.POST.get('confirmPassword')
    
    #     if password != confirmPassword:
    #         return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})
        
    #     if not re.match("^[a-zA-Z0-9]+$", username):
    #         return JsonResponse({'status': 'error', 'message': 'Username can only contain alphanumeric characters.'})

    #     if User.objects.filter(username=username).exists():
    #         return JsonResponse({'status': 'error', 'message': 'Username is already taken. Choose a different one.'})

    #     if User.objects.filter(email=email).exists():
    #         return JsonResponse({'status': 'error', 'message': 'Email is already registered. Choose a different one.'})

    #     if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password) and any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password) and len(password) >= 8):
    #         return JsonResponse({'status': 'error', 'message': 'Enter password containing numeric digits, alphabets and special chracters.'})
    
    #     user = User.objects.create_user(
    #         username = username,
    #         email=email,
    #         password=password
    #     )
        
    #     user  = authenticate(request , username = username , password = password)
    #     if user:
    #         auth_login(request , user)
    #         return JsonResponse({'status': 'success'}) 
    
    # return JsonResponse({'status': 'error', 'message': 'Some thing went wrong'})


def submitRecord(request):
    if request.method == "POST":
        image_title = "unique-image"
        number_of_folder = 1
        images = request.FILES.getlist('images')
        newFolder = os.path.join(BASE_DIR, 'media', 'multipleImage', image_title)
        if os.path.exists(newFolder):
            shutil.rmtree(newFolder)
        
        os.mkdir(newFolder)
        for image in images:
            multi_img_file = default_storage.save('multipleImage/' + image.name, ContentFile(image.read()))
            shutil.move(os.path.join(BASE_DIR, 'media', 'multipleImage', image.name) , newFolder)

            multiImg(
                image_title=image.name,
                number_of_folders=number_of_folder,
                input_image=multi_img_file
                ).save()
        zip_file = shutil.make_archive(newFolder, 'zip', newFolder)
        shutil.rmtree(newFolder)
        applyAlgo(zip_file, number_of_folder, image_title)
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
def has_special_characters(user_input):
    return any(char in punctuation for char in user_input)

def remove_special_characters(user_input):
    cleaned_input = ''.join(char for char in user_input if char.isalnum() or char.isspace())
    return cleaned_input

def language_translator(request):
    if request.method == "POST":
        inputLang = request.POST["input_lang"]
        outputLang = request.POST["output_lang"]
        inputText = request.POST["user_input"]
      
        if len(inputText) == 0:
            inputText = "You are not allowed to send empty"
        if has_special_characters(inputText):
            inputText = remove_special_characters(inputText)
            if len(inputText) == 0:
                inputText = "nothing here to show."
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
                {"role": "system", "content": f"You are a language converter specializing in translating {inputLang} to {outputLang}. Please provide clear and concise sentences for translation. If translation not found send error message in {outputLang} language. Do not use other language exept {outputLang}"},
                {"role": "user", "content": inputText}
            ]
        )
        response = response.choices[0].message.content.strip()

        return JsonResponse({'status' : 'success' , 'message' : response})
    return render(request , "translator.html")

def chat_crafters(request):

    return render(request , "craftes.html")