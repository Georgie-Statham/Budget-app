from django import forms
from .models import Recurring

class RecurringForm(forms.ModelForm):

    class Meta:
        model = Recurring
        fields = [
            'start_date',
            'how_often',
            'description',
            'category',
            'amount',
            'currency',
            'who_for',
            'who_paid',
        ]
