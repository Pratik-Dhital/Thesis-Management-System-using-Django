from django.contrib import admin
from .models import Faculty, Department, CourseType, AcademicLevel
# Register your models here.

admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(CourseType)
admin.site.register(AcademicLevel)