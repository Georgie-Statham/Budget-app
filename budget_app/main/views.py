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
from payback.models import Payback

# helper functions

def currency_converter(currency_1, currency_2, date):
    """ Calculates exchange rate from currency_2 to currency_1
    on the specified date. Based on European Central Bank """
    response = requests.get(
        'https://api.exchangeratesapi.io/' + str(date) +
        '?symbols=' + currency_1 + ',' + currency_2)
    output = json.loads(response.content)
    return Decimal(output['rates'][currency_1] / output['rates'][currency_2])

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

def calculate_balance_GBP():
    """ Calculates the amount owed by each user in GBP, ILS, and AUD """
    family_expenses = Expense.objects.filter(who_for='Everyone')
    total_family_expenses = sum(
        expense.converted_amount
        for expense
        in family_expenses
    )
    individual_share = total_family_expenses / Decimal(len(Expense.USERS))

    balance_GBP = {}
    for user in Expense.USERS:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            who_paid=user[0]
        )
        amount_paid = sum(
            expense.converted_amount
            for expense
            in expenses_paid_for
        )

        ind_exp_paid_by_other_user = (
            Expense.objects.filter(who_for=user[0])
                           .exclude(who_paid=user[0])
        )
        total_ind_exp_paid_by_other_user = sum(
            item.converted_amount
            for item
            in ind_exp_paid_by_other_user
        )

        ind_exp_paid_for_other_user = (
            Expense.objects.filter(who_paid=user[0])
                           .exclude(who_for=user[0])
                           .exclude(who_for='Everyone')
        )
        total_ind_exp_paid_for_other_user = sum(
            item.converted_amount
            for item
            in ind_exp_paid_for_other_user
        )

        paybacks_made = Payback.objects.filter(who_from=user[0])
        total_paybacks_made = sum(
            item.GBP
            for item
            in paybacks_made
        )
        paybacks_received = Payback.objects.filter(who_to=user[0])
        total_paybacks_received = sum(
            item.GBP
            for item
            in paybacks_received
        )

        user_balance_GBP = (
            - individual_share
            + amount_paid
            - total_ind_exp_paid_by_other_user
            + total_ind_exp_paid_for_other_user
            + total_paybacks_made
            - total_paybacks_received
        )
        balance_GBP[user[0]] = user_balance_GBP
    return balance_GBP

# Views

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
    amount_owed = calculate_balance_GBP()[
            request.user.username].quantize(Decimal('.01'))
    context = {
        'category_totals_dict': category_totals_dict,
        'family_total': family_total,
        'amount_paid_dict': amount_paid_dict,
        'individual_expenses_dict': individual_expenses_dict,
        'months': months,
        'amount_owed': amount_owed,
        'amount_owed_abs': abs(amount_owed)
    }
    return render(request, 'home.html', context)

@login_required(login_url='/accounts/login/')
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            if form.cleaned_data['currency'] != 'GBP':
                date = form.cleaned_data['date']
                currency = form.cleaned_data['currency']
                data.converted_amount = form.cleaned_data['amount'] * currency_converter('GBP', currency, date)
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
