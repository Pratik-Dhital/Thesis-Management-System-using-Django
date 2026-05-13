from django import forms

from .models import (
    Student,
    Lecturer
)


# ================= STUDENT =================

class StudentProfileForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            'roll_no',
            'faculty',
            'department',
            'academic_level'
        ]


# ================= LECTURER =================

class LecturerProfileForm(forms.ModelForm):

    class Meta:

        model = Lecturer

        fields = [
            'designation',
            'faculty',
            'department'
        ]


# ================= SUPERVISOR =================

# class SupervisorProfileForm(forms.ModelForm):

#     class Meta:

#         model = Supervisor

#         fields = [
#             'designation',
#             'qualification',
#             'faculty',
#             'department'
#         ]