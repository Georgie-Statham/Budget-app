from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone

from decimal import *
import requests
import json

from .models import Expense
from .forms import ExpenseForm

# helper functions

def get_exchange_rate():
    """ gets the current GBP/ILS expchange rate """
    response = requests.get(
        'https://api.exchangeratesapi.io/latest?symbols=GBP,ILS')
    binary = response.content
    output = json.loads(str(binary, 'utf-8'))
    GBP, ILS = (output['rates']['GBP']), (output['rates']['ILS'])
    return Decimal(GBP / ILS)


# views

def home(request):
    # family_total = 0
    category_totals_dict = {}
    amount_paid_dict = {}
    individual_expenses_dict = {}
    family_total = 0

    for category in Expense.CATEGORIES:
        family_expenses_in_category = Expense.objects.filter(
            category=category[0],
            who_for='Everyone',
            date__gte=timezone.now().replace(
                day=1, hour=0, minute=0, second=0)
        )
        category_total = 0
        for expense in family_expenses_in_category:
            category_total += expense.converted_amount
            family_total += expense.converted_amount
            category_totals_dict[category[0]] = category_total

    for person in Expense.WHO_PAID:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            date__gte=timezone.now().replace(
                day=1, hour=0, minute=0, second=0),
            who_paid=person[0]
        )
        amount_paid = 0
        for expense in expenses_paid_for:
            amount_paid += expense.converted_amount
        amount_paid_dict[person[0]] = amount_paid

    for person in Expense.WHO_PAID:
        individual_expenses = Expense.objects.filter(
            who_for=person[0],
            date__gte=timezone.now().replace(
                day=1, hour=0, minute=0, second=0),
        )
        individual_spending = 0
        for expense in individual_expenses:
            individual_spending =+ expense.converted_amount
        individual_expenses_dict[person[0]] = individual_spending


    context = {
        'category_totals_dict': category_totals_dict,
        'family_total': family_total,
        'amount_paid_dict': amount_paid_dict,
        'individual_expenses_dict': individual_expenses_dict
    }
    return render(request, 'home.html', context)

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            if form.cleaned_data['currency'] == 'ILS':
                data.converted_amount = form.cleaned_data['amount'] * get_exchange_rate()
            else:
                data.converted_amount = form.cleaned_data['amount']
            data.save()
            return redirect(home)
        else:
            print(form.errors)
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

def history(request):
    return render(request, 'history.html')
