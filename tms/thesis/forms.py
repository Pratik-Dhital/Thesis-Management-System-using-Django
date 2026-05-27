from django import forms
from .models import Proposal
from .models import ThesisDocument
from .models import Defense
class ProposalForm(forms.ModelForm):

    class Meta:

        model = Proposal

        fields = [

            'title',

            'description',

            'document'
        ]

class ThesisDocumentForm(forms.ModelForm):

    class Meta:

        model = ThesisDocument

        fields = [
            'file'
            # 'document_type'
        ]

#schedule defence form

class DefenseForm(forms.ModelForm):

    class Meta:

        model = Defense

        fields = [
            'date',
            'time',
            'venue',
            'submission_deadline'
        ]
        widgets = {

            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),

            'submission_deadline': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),

            'venue': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }