from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import createAccount , text_language , chatbotapi , FetchUserIdView
urlpatterns = [
    path('', views.index, name="index"),
    path("diffuse-image/", views.diffuseImg, name="diffuseImage"),
    path("accounts/login/", views.loginPage, name="loginPage"),
    path("signin_user/", views.accountslogin, name="acccountslogin"),
    path("accounts/logout/", views.logout, name="logout"),
    path("accounts/signup/", createAccount.as_view()), #  API for register user
    path("diffuse-image/submitRecord/", views.submitRecord, name="submitRecord"),
    path("download/", views.download, name="download"),
    path("api/text/language/translate/", text_language.as_view()), # API for Language
    path("api/assistant/chatbot/", chatbotapi.as_view()), # API for Chat assistant
    path("api/fetch/id/", FetchUserIdView.as_view()),
    path("chat-crafters/", views.chat_crafters, name="ChatCrafters"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
