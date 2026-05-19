from django.db import models
from django.contrib.auth.models import AbstractUser
from academics.models import Faculty, Department, AcademicLevel

# Create your models here.

ROLE_CHOICES = (
    ('student', 'Student'),
    ('lecturer', 'Lecturer'),
    ('admin', 'Admin'),
)

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150) 
    roll_no = models.PositiveIntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    academic_level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.roll_no}"
    
class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    is_supervisor = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
