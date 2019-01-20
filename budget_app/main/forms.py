from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = [
            'date', 'description', 'category', 'amount',
            'currency', 'who_for', 'who_paid']
