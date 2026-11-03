from django.contrib import admin

from .models import Center, StudentProfile, TeacherProfile, User

admin.site.register([Center, User, StudentProfile, TeacherProfile])
