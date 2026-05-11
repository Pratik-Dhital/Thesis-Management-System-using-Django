from django.contrib import admin
from .models import User, Student, Lecturer, Supervisor
# Register your models here.
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Supervisor)

