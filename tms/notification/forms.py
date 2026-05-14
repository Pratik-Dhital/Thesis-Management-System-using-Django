from django import forms
from .models import Notification
from users.models import Student


class SendNotificationForm(forms.Form):

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4
            }
        )
    )

    send_type = forms.ChoiceField(
        choices=[
            ('group', 'Send To Group'),
            ('student', 'Send To Single Student')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )