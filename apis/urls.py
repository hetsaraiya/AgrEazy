from django.urls import path, include
from .views import *
urlpatterns = [
    path('login', login_view, name="login"),
    path('signup', signup_view, name="signup"),
    path('logout', logout_view, name="logout_view"),
    path('upload_verification_docs', upload_verification_docs, name="upload_verification_docs"),
]
