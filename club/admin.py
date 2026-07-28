from django.contrib import admin
from . models import Post, StudentProfile, AdminProfile, SchoolProfile

# Register your models here.
admin.site.register(Post)
admin.site.register(StudentProfile)
admin.site.register(AdminProfile)
admin.site.register(SchoolProfile)
