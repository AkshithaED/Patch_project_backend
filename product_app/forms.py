from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Patch
# -----------------------
# Custom User Forms
# -----------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')
 
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')
 

class PatchAdminForm(forms.ModelForm):
    class Meta:
        model = Patch
        fields = '__all__'
