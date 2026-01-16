from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="อีเมล")
    first_name = forms.CharField(required=False, label="ชื่อ")
    last_name = forms.CharField(required=False, label="นามสกุล")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


# UserUpdateForm ถูกลบออกไปแล้ว

# ฟอร์มนี้คือฟอร์มเดียวที่ต้องใช้ในหน้า Profile
# accounts/forms.py
class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Profile
        fields = ['image', 'phone', 'default_address', 'birth_date', 'address_lat', 'address_lng', 'role']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_staff:
            self.fields.pop('role')