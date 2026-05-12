from django.db import models
from users.models import Student, Supervisor, Lecturer
# Create your models here.
class ThesisStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Proposal(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    document = models.FileField(upload_to='proposal_documents/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(ThesisStatus, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Thesis(models.Model):
    title = models.CharField(max_length=255)
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    status = models.ForeignKey(ThesisStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ThesisGroup(models.Model):
    thesis = models.OneToOneField(Thesis, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.thesis.title
    
class GroupMember(models.Model):
    group = models.ForeignKey(ThesisGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.student.full_name

class ThesisDocument(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE)
    file = models.FileField(upload_to="thesis_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.thesis.title

class Review(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.thesis.title


class Defense(models.Model):
    thesis = models.OneToOneField(Thesis, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)

    def __str__(self):
        return self.thesis.title