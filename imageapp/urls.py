from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name="index"),
    path("diffuse-image/", views.diffuseImg, name="diffuseImage"),
    path("accounts/login/", views.loginPage, name="loginPage"),
    path("signin_user/", views.accountslogin, name="acccountslogin"),
    path("accounts/logout/", views.logout, name="logout"),
    path("signup_user/", views.createAccount, name="signup"),  
    path("diffuse-image/submitRecord/", views.submitRecord, name="submitRecord"),
    path("download/", views.download, name="download"),
    path("language-translator/", views.language_translator, name="translator"),
    path("chat-crafters/", views.chat_crafters, name="ChatCrafters"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
