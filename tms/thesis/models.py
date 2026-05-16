from django.db import models
from users.models import Student, Lecturer


class ThesisStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ThesisGroup(models.Model):
    name = models.CharField(max_length=100)

    supervisor = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE,
        limit_choices_to={'is_supervisor': True}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Proposal(models.Model):
    group = models.OneToOneField(
        'ThesisGroup',
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    document = models.FileField(
        upload_to='proposal_documents/'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.ForeignKey(
        ThesisStatus,
        on_delete=models.CASCADE
    )

    lecturer_comment = models.TextField(
        null=True,
        blank=True
    )

    supervisor_comment = models.TextField(
        null=True,
        blank=True
    )
    reviewed_by_lecturer = models.ForeignKey(
        Lecturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lecturer_reviews"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.title


class Thesis(models.Model):
    title = models.CharField(max_length=255)

    proposal = models.OneToOneField(
        'Proposal',
        on_delete=models.CASCADE
    )

    lecturer = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE,
        related_name="reviewed_thesis"
    )

    supervisor = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE,
        related_name='supervised_thesis'
    )

    status = models.ForeignKey(
        ThesisStatus,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class GroupMember(models.Model):
    group = models.ForeignKey(
        ThesisGroup,
        on_delete=models.CASCADE
    )

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.student.full_name


class ThesisDocument(models.Model):
    thesis = models.ForeignKey(
        Thesis,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="thesis_documents/"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.thesis.title


class Review(models.Model):
    thesis = models.ForeignKey(
        Thesis,
        on_delete=models.CASCADE
    )

    reviewer = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.thesis.title


class Defense(models.Model):
    thesis = models.OneToOneField(
        Thesis,
        on_delete=models.CASCADE
    )

    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)

    def __str__(self):
        return self.thesis.title
    
class GroupConfiguration(models.Model):

    max_students_per_group = models.PositiveIntegerField(
        default=1
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Max Students: {self.max_students_per_group}"
    
class ThesisProgress(models.Model):

    thesis = models.ForeignKey(
        Thesis,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title