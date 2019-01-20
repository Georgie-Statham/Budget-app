from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone

from .models import Expense
from .forms import ExpenseForm

# helper functions

def get_exchange_rate():
    pass

exchange_rate = 0.21

def converted_amount():
    if form.currency == 'ILS':
        Expense.converted_amount = form.amount * exchange_rate
        return Expense.converted_amount
    else:
        Expense.converted_amount = form.amount
        return Expense.converted_amount

# views

def home(request):
    family_total = 0
    for category in Expense.CATEGORIES:
        family_expenses_in_category = Expense.objects.filter(
            category=category,
            who_for='Everyone',
            date__gte=timezone.now().replace(
                day=1, hour=0, minute=0, second=0)
        )
        category_total = 0
        for expense in family_expenses_in_category:
            category_total += converted_amount
        family_total += category_total

    context = {
        'categories': Expense.CATEGORIES,
        'category_total': category_total,
        'family_total': family_total,
    }
    return render(request, 'home.html', context)

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            converted_amount()
            form.commit()
            return redirect(home)
        else:
            print(form.errors)
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})
