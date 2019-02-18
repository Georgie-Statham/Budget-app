from django.shortcuts import render, redirect
from django.template import loader
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from decimal import *
import requests
import json

from .models import Expense
from .forms import ExpenseForm

# helper functions

def get_exchange_rate(date):
    """ Gets the GBP/ILS exchange rate for a specified date """
    response = requests.get(
        'https://api.exchangeratesapi.io/' + str(date) + '?symbols=GBP,ILS')
    output = json.loads(response.content)
    GBP, ILS = (output['rates']['GBP']), (output['rates']['ILS'])
    return Decimal(GBP / ILS)

def this_month():
    """ Determines if a date is in the current month """
    return timezone.now().replace(day=1, hour=0, minute=0, second=0)

def months_so_far():
    """ Creates a list of all the months with entries in Expenses"""
    month_list = []
    for expense in Expense.objects.all().order_by('-date'):
        month, year = expense.date.strftime("%b"), expense.date.strftime("%Y")
        if not (month, year) in month_list:
            month_list.append((month, year))
    return month_list


# views

@login_required(login_url='/accounts/login/')
def home(request):
    months = months_so_far()
    category_totals_dict = {}
    family_total = 0
    amount_paid_dict = {}
    individual_expenses_dict = {}

    for category in Expense.CATEGORIES:
        family_expenses_in_category = Expense.objects.filter(
            category=category[0],
            who_for='Everyone',
            date__gte=this_month()
        )
        category_total = 0
        for expense in family_expenses_in_category:
            category_total += expense.converted_amount
            family_total += expense.converted_amount
            category_totals_dict[category[1]] = category_total

    for person in Expense.USERS:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            date__gte=this_month(),
            who_paid=person[0]
        )
        amount_paid = 0
        for expense in expenses_paid_for:
            amount_paid += expense.converted_amount
        amount_paid_dict[person[0]] = amount_paid

    for person in Expense.USERS:
        individual_expenses = Expense.objects.filter(
            who_for=person[0],
            date__gte=this_month(),
        )
        individual_spending = 0
        for expense in individual_expenses:
            individual_spending += expense.converted_amount
        individual_expenses_dict[person[0]] = individual_spending

    context = {
        'category_totals_dict': category_totals_dict,
        'family_total': family_total,
        'amount_paid_dict': amount_paid_dict,
        'individual_expenses_dict': individual_expenses_dict,
        'months': months,
    }
    return render(request, 'home.html', context)

@login_required(login_url='/accounts/login/')
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            if form.cleaned_data['currency'] == 'ILS':
                date = form.cleaned_data['date']
                data.converted_amount = form.cleaned_data['amount'] * get_exchange_rate(date)
            else:
                data.converted_amount = form.cleaned_data['amount']
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Expense successfully added.')
            return redirect(home)
        else:
            print(form.errors)
    else:
        form = ExpenseForm(initial={'who_paid': request.user.username})
    return render(request, 'add_expense.html', {'form': form})
