
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt import views as jwt_views
from security.serializers import CustomTokenObtainPairSerializer

from .views import (
    LogoutView,
)

from django.shortcuts import redirect
urlpatterns = [
    path('token/', 
        jwt_views.TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), 
        name='token_obtain_pair'),
    path('token/refresh/', 
        jwt_views.TokenRefreshView.as_view(), 
        name='token_refresh'),
    path('logout/', LogoutView.as_view(), name ='logout'),
]