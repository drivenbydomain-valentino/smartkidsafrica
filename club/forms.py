from django import forms
from .models import AdminProfile, StudentProfile, SchoolProfile

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'user_type',
            'parent_name',
            'parent_phone',
            'parent_whatsapp',
            'avatar',
            'bio',
            'age',
            'user_class',
            'school',
        ]
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent's Name"}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent's Phone"}),
            'parent_whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent's WhatsApp"}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write something about yourself...'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'user_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class'}),
            'school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Name'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = [
            'school_name',
            'director_name',
            'email',
            'avatar',
            'whatsapp_number',
            'contact_number',
            'registration_number',
            'address',
            'nearest_bus_stop',
            'lga',
            'state',
            'num_students',
            'school_type',
            'website',
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'director_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nearest_bus_stop': forms.TextInput(attrs={'class': 'form-control'}),
            'lga': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'num_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'school_type': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = [
            'role',
            'can_manage_users',
            'can_manage_posts',
            'can_manage_schools',
            'can_view_reports',
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'can_manage_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_posts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_schools': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }