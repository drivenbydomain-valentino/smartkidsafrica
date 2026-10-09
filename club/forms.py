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

from django import forms

class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)
    age = forms.IntegerField(required=False)
    user_class = forms.CharField(max_length=100, required=False)
    school = forms.CharField(max_length=255, required=False)
    parent_name = forms.CharField(max_length=255, required=False)
    parent_phone = forms.CharField(max_length=20, required=False)
    parent_whatsapp = forms.CharField(max_length=20, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    avatar = forms.ImageField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

# ============================================================
# PARENT REGISTRATION
# ============================================================

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ParentRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Choose a username"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Create a password"}
        ),
    )

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter full name"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter email address"}
        ),
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter phone number"}
        ),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter WhatsApp number"}
        ),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter residential address",
            }
        ),
    )

    nearest_bus_stop = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nearest bus stop / landmark"}
        ),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "LGA"}
        ),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "State"}
        ),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Country"}
        ),
    )

    occupation = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Occupation"}
        ),
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Tell us a bit about yourself",
            }
        ),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": "image/*"}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

# ============================================================
# TEACHER REGISTRATION
# ============================================================

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Create a password"}),
    )

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter WhatsApp number"}),
    )

    school_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter school name"}),
    )

    subject_specialization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mathematics, Physics"}),
    )

    years_of_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Years of experience"}),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "LGA"}),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Tell us about yourself"}),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

# ============================================================
# SCHOOL REGISTRATION
# ============================================================

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SchoolRegistrationForm(forms.Form):
    school_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter official school name"}
        ),
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Create account password"}
        ),
    )

    director_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Director / Principal name"}
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "School email address"}
        ),
    )

    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "WhatsApp phone number"}
        ),
    )

    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Official contact number"}
        ),
    )

    registration_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Government Reg / Approval No."}
        ),
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Physical street address",
            }
        ),
    )

    nearest_bus_stop = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nearest landmark or bus stop"}
        ),
    )

    lga = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "LGA"}),
    )

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
    )

    country = forms.CharField(
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    num_students = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Approximate student population"}
        ),
    )

    school_type = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g. Nursery, Primary, Secondary"}
        ),
    )

    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "https://yourschool.com"}
        ),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def clean_school_name(self):
        school_name = self.cleaned_data["school_name"].strip()
        if User.objects.filter(username__iexact=school_name).exists():
            raise forms.ValidationError(
                "A school account with this name already exists."
            )
        return school_name