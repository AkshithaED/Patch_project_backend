from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
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
 

from django import forms
from .models import Patch
from django.contrib.postgres.forms import SplitArrayWidget

class PatchAdminForm(forms.ModelForm):
    class Meta:
        model = Patch
        fields = '__all__'
        widgets = {
            'high_level_scope': SplitArrayWidget(widget=forms.TextInput(), size=5),
            'third_party_jars': SplitArrayWidget(widget=forms.TextInput(), size=5),
        }
