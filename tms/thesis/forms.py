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

class DefenseForm(forms.ModelForm):

    class Meta:

        model = Defense

        fields = [
            'date',
            'time',
            'venue'
        ]