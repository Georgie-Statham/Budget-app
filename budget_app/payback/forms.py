from django import forms
from .models import Payback

class PaybackForm(forms.ModelForm):

    class Meta:
        model = Payback
        fields = [
            'date',
            'who_from',
            'who_to',
            'amount',
            'currency',
            'method',
        ]
