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
from rest_framework import status
from .serializers import *
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.sessions.models import Session
import dill

from PyPDF2 import PdfReader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from typing_extensions import Concatenate

BASE_DIR = settings.BASE_DIR

document_search = None
chain = None

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

class createAccount(APIView):
    def post(self, request):
        serializer = UserSerilizer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            if User.objects.filter(email=email).exists():
                return Response({'status': 400, 'message': 'Email already exists'})
            user = User.objects.create_user(username=username, email=email, password=password)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'status': 200, 'message': 'User created successfully', 'token': token.key})
        return Response({'status': 400, 'message': 'Invalid data provided', 'errors': serializer.errors})

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

class text_language(APIView):
    def post(self , request):
        serializer = translationSerilizer(data=request.data)
        if serializer.is_valid():
            inputText = serializer.validated_data.get('input_text')
            inputLang = serializer.validated_data.get('input_language')
            outputLang = serializer.validated_data.get('output_language')
            if len(inputText) == 0:
                inputText = "You are not allowed to send empty"
            if has_special_characters(inputText):
                inputText = remove_special_characters(inputText)
                if len(inputText) == 0:
                    inputText = "nothing here to show."
            output = client.chat.completions.create(
            model="gpt-4",
            messages=[
                    {"role": "system", "content": f"You are a language converter specializing in translating {inputLang} to {outputLang}. Please provide clear and concise sentences for translation. If translation not found send error message in {outputLang} language. Do not use other language exept {outputLang}"},
                    {"role": "user", "content": inputText}
                ]
            )
            output = output.choices[0].message.content.strip()
            return Response({'status': 200, 'output_text': output})
        else:
            return Response({'status': 403, 'errors': serializer.errors}, status=status.HTTP_403_FORBIDDEN)

class chatbotapi(APIView):
    def post(self , request):
        serializer = health_assistance_serializers(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            botname = serializer.validated_data.get('botname')
            inputText = serializer.validated_data.get('question')
            
            if len(inputText) == 0:
                inputText = "You are not allowed to send empty"
                return Response({'status': 200, 'bot_reply': inputText})
            if has_special_characters(inputText):
                inputText = remove_special_characters(inputText)
                if len(inputText) == 0:
                    inputText = "Your message has been removed."
                    return Response({'status': 200, 'bot_reply': inputText})
                
            if botname == "Health":
                gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                        {"role": "system", "content": "You are a virtual health assistant. Users can provide symptoms, and you are responsible for providing accurate medical advice and prescriptions. "
                                                        "For example, you can ask 'What symptoms are you experiencing?' or 'Do you have any pre-existing conditions?' "
                                                        "Your goal is to assist users in managing their health effectively and providing appropriate medical guidance."
                                                        "Donot start with  I'm sorry to hear you're not feeling well"
                        },
                        {"role": "user", "content": inputText}
                    ]
                ) 
            if botname == "Law":
                gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                            {
                            "role": "system","content": "You are a virtual legal assistant. Users can seek legal advice and guidance from you. "
                                    "Your responsibilities include providing accurate legal information, advice on legal procedures, "
                                    "and assistance in understanding legal documents. "
                                    "You can ask users about their legal issues, case details, and any relevant information to provide tailored recommendations. "
                                    "For example, you can ask 'What legal issue are you facing?' or 'Do you have any relevant documents or contracts?' "
                                    "Your goal is to help users navigate legal matters effectively and provide appropriate legal guidance."
                                    "answer should be short and to the point"
                        },
                        {"role": "user", "content": inputText}
                    ]
                )
            gpt_response = gpt_response.choices[0].message.content.strip()
            chatbot_instance = chatbot(username=username, question=inputText, answer=gpt_response, botname=botname)
            chatbot_instance.save()  

            return Response({'status': 200, 'output_text': gpt_response})
        else:
            return Response({'status': 403, 'errors': serializer.errors}, status=status.HTTP_403_FORBIDDEN)

class FetchUserIdView(APIView):
    def post(self, request):
        serializer = UserIdSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['username']
            return Response({'user_id': user_id})
        return Response(serializer.errors, status=400)

class ragChatBot(APIView):
    def post(self, request, format=None):
        global document_search, chain
        serializer = RagBotSerializers(data=request.data) 
        if serializer.is_valid():
            user_id = serializer.validated_data['username']  
            try:
                existing_record = ragbotmodel.objects.get(username=user_id)                
                if existing_record.file:
                    file_path = existing_record.file.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    existing_record.delete()
                
            except ragbotmodel.DoesNotExist:
                pass
            except Exception as e:
                print("Error:", str(e))
            serializer.save()
            pdf_file_path = ragbotmodel.objects.get(username=user_id).file.path
            pdfreader = PdfReader(pdf_file_path)
            raw_text = ''
            for i, page in enumerate(pdfreader.pages):
                content = page.extract_text()
            
            if content:
                raw_text += content
            
            text_splitter = CharacterTextSplitter(
                separator = "\n",
                chunk_size = 800,
                chunk_overlap = 200,
                length_function = len,
            )
            texts =  text_splitter.split_text(raw_text)
            embeddings = OpenAIEmbeddings()
            document_search = FAISS.from_texts (texts, embeddings)
            chain = load_qa_chain(OpenAI(), chain_type="stuff")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ragbotqanda(APIView):
    def post(self , request):
        serializer = ragbotqa(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data.get('input_text')
            docs = document_search.similarity_search(query)
            output = chain.run(input_documents=docs, question=query)
            return Response({'status': 200, 'output_text': output})
        return Response({'status': 403, 'errors': serializer.errors}, status=status.HTTP_403_FORBIDDEN)
        
def chat_crafters(request):
    return render(request , "craftes.html")