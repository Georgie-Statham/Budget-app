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
from .add_recurring_expenses import *
from .currency_converter import currency_converter

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

"CHANGE SO MAIN CURRENCY IS AUD"

def calculate_balance_AUD():
    """ Calculates the amount owed by each user in AUD and GBP"""
    family_expenses = Expense.objects.filter(who_for='Everyone')
    total_family_expenses = sum(
        expense.AUD
        for expense
        in family_expenses
    )
    individual_share = total_family_expenses / Decimal(len(Expense.USERS))

    balance_AUD = {}
    for user in Expense.USERS:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            who_paid=user[0]
        )
        amount_paid = sum(
            expense.AUD
            for expense
            in expenses_paid_for
        )

        ind_exp_paid_by_other_user = (
            Expense.objects.filter(who_for=user[0])
                           .exclude(who_paid=user[0])
        )
        total_ind_exp_paid_by_other_user = sum(
            item.AUD
            for item
            in ind_exp_paid_by_other_user
        )

        ind_exp_paid_for_other_user = (
            Expense.objects.filter(who_paid=user[0])
                           .exclude(who_for=user[0])
                           .exclude(who_for='Everyone')
        )
        total_ind_exp_paid_for_other_user = sum(
            item.AUD
            for item
            in ind_exp_paid_for_other_user
        )

        paybacks_made = Payback.objects.filter(who_from=user[0])
        total_paybacks_made = sum(
            item.AUD
            for item
            in paybacks_made
        )
        paybacks_received = Payback.objects.filter(who_to=user[0])
        total_paybacks_received = sum(
            item.AUD
            for item
            in paybacks_received
        )

        user_balance_AUD = (
            - individual_share
            + amount_paid
            - total_ind_exp_paid_by_other_user
            + total_ind_exp_paid_for_other_user
            + total_paybacks_made
            - total_paybacks_received
        )
        balance_AUD[user[0]] = user_balance_AUD
    return balance_AUD

# Views

@login_required(login_url='/accounts/login/')
def home(request):
    months = months_so_far()
    category_totals_dict = {}
    family_total = 0
    amount_paid_dict = {}
    individual_expenses_dict = {}

    # add recurring expenses that have been since app last opened
    add_scheduled_expenses()

    for category in Expense.CATEGORIES:
        family_expenses_in_category = Expense.objects.filter(
            category=category[0],
            who_for='Everyone',
            date__gte=this_month()
        )
        category_total = 0
        for expense in family_expenses_in_category:
            category_total += expense.AUD
            family_total += expense.AUD
            category_totals_dict[category[1]] = category_total

    for person in Expense.USERS:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            date__gte=this_month(),
            who_paid=person[0]
        )
        amount_paid = 0
        for expense in expenses_paid_for:
            amount_paid += expense.AUD
        amount_paid_dict[person[0]] = amount_paid

    for person in Expense.USERS:
        individual_expenses = Expense.objects.filter(
            who_for=person[0],
            date__gte=this_month(),
        )
        individual_spending = 0
        for expense in individual_expenses:
            individual_spending += expense.AUD
        individual_expenses_dict[person[0]] = individual_spending
    amount_owed = calculate_balance_AUD()[
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
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            if form.cleaned_data['currency'] == 'GBP':
                data.GBP = amount
                data.AUD = amount * currency_converter('AUD', 'GBP', date)
            if form.cleaned_data['currency'] == 'AUD':
                data.AUD = amount
                data.GBP = amount * currency_converter('GBP', 'AUD', date)
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Expense successfully added.')
            return redirect(home)
        else:
            print(form.errors)
    else:
        form = ExpenseForm(initial={'who_paid': request.user.username})
    return render(request, 'add_expense.html', {'form': form})
