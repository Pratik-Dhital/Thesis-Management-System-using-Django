from django.db import models

# Create your models here.

class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class CourseType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class AcademicLevel(models.Model):
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    level_no = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course_type.name} {self.level_no}"