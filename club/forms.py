from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    AdminProfile,
    ParentProfile,
    SchoolProfile,
    StudentProfile,
    TeacherProfile,
)

User = get_user_model()


# ============================================================
# COMMON LOGIN FORM
# ============================================================

class UserLoginForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, request=None, user_type=None, *args, **kwargs):
        self.request = request
        self.user_type = user_type
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError("Invalid username or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

            if (
                self.user_type == "parent"
                and getattr(self.user_cache, "user_type", None) != "parent"
            ):
                raise forms.ValidationError(
                    "This account is not registered for this login."
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


# ============================================================
# STUDENT REGISTRATION
# ============================================================

class StudentRegistrationForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control"}
        ),
    )

    parent_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    parent_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    parent_whatsapp = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control"}
        ),
    )

    user_class = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    school = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    avatar = forms.ImageField(
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username


# ============================================================
# PARENT REGISTRATION
# ============================================================

class ParentRegistrationForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control"}
        ),
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    nearest_bus_stop = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    occupation = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    avatar = forms.ImageField(
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username


class ParentProfileForm(forms.ModelForm):

    class Meta:
        model = ParentProfile
        fields = [
            "avatar",
            "phone_number",
            "address",
        ]

        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address"}
            ),
        }


# ============================================================
# TEACHER REGISTRATION
# ============================================================

class TeacherRegistrationForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control"}
        ),
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    school_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    subject_specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    years_of_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control"}
        ),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    avatar = forms.ImageField(
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username


# ============================================================
# SCHOOL REGISTRATION
# ============================================================

class SchoolRegistrationForm(forms.Form):

    school_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    director_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control"}
        ),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    registration_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )

    nearest_bus_stop = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    num_students = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control"}
        ),
    )

    school_type = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
    )

    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control"}
        ),
    )

    avatar = forms.ImageField(
        required=False,
    )

    def clean_school_name(self):
        school_name = self.cleaned_data["school_name"].strip()

        if User.objects.filter(
            username__iexact=school_name
        ).exists():
            raise forms.ValidationError(
                "A school account with this name already exists."
            )

        return school_name