from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from decimal import *
import requests
import json
from datetime import date

from .forms import PaybackForm
from .models import Payback
from main.models import Expense
from main.views import get_exchange_rate, get_exchange_rate_2

# helper functions

def convert_from_GBP(value_in_GBP, currency):
    # converts the balance calculated in GBP into a different currency
    return value_in_GBP / get_exchange_rate_2(date.today(), currency)

def currency_converter(currency_1, currency_2, date):
    response = requests.get(
        'https://api.exchangeratesapi.io/' + str(date) +
        '?symbols=' + currency_1 + ',' + currency_2)
    output = json.loads(response.content)
    print (output)
    return Decimal(output['rates'][currency_1] / output['rates'][currency_2])


# class based editing views

class PaybackUpdate(SuccessMessageMixin, UpdateView):
    model = Payback
    fields = [
        'date',
        'who_from',
        'who_to',
        'amount',
        'currency',
        'method'
    ]
    template_name_suffix = '_update_form'
    success_message = 'Payback successfully updated.'
    success_url = reverse_lazy('overview')

class PaybackDelete(DeleteView):
    model = Payback
    template_name_suffix = '_delete_form'
    success_message = 'Payback successfully deleted.'
    success_url = reverse_lazy('overview')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(PaybackDelete, self).delete(request, *args, **kwargs)

# Views

@login_required(login_url='/accounts/login/')
def overview(request):
    payback_list = Payback.objects.all().order_by('-date')
    family_expenses = Expense.objects.filter(who_for='Everyone')
    total_family_expenses = sum(
        expense.converted_amount
        for expense
        in family_expenses
    )
    individual_share = total_family_expenses / Decimal(len(Expense.USERS))
    balances = {}
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
            -individual_share
            + amount_paid
            + total_paybacks_made
            - total_paybacks_received
        )
        user_balance_ILS = user_balance_GBP * currency_converter(
            'GBP', 'ILS', date.today())
        user_balance_AUD = user_balance_GBP * currency_converter(
            'GBP', 'AUD', date.today())
        balances[user[0]] = (
            user_balance_GBP.quantize(Decimal('.01')),
            user_balance_ILS.quantize(Decimal('.01')),
            user_balance_AUD.quantize(Decimal('.01')),
        )
    context = {
        'payback_list': payback_list,
        'balances': balances
    }
    return render(request, 'payback.html', context)

@login_required(login_url='/accounts/login/')
def payback_form(request):
    if request.method == 'POST':
        form = PaybackForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            # for curr, x in Payback.CURRENCIES:
            #     if form.cleaned_data['currency'] == curr:
            #         data.curr = amount
            #         print(data.curr)
            #     else:
            #         data.curr = (
            #             amount * get_exchange_rate_2(date, curr)
            #         )
            #         print(data.curr)
            if form.cleaned_data['currency'] == 'ILS':
                data.ILS = amount
                data.GBP = amount * currency_converter('ILS', 'GBP', date)
                data.AUD = amount * currency_converter('ILS', 'AUD', date)
            if form.cleaned_data['currency'] == 'GBP':
                data.GBP = amount
                data.ILS = amount * currency_converter('GBP', 'ILS', date)
                data.AUD = amount * currency_converter('GBP', 'AUD', date)
            if form.cleaned_data['currency'] == 'AUD':
                data.AUD = amount
                data.GBP = amount * currency_converter('AUD', 'GBP', date)
                data.ILS = amount * currency_converter('AUD', 'ILS', date)
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Payback successfully recorded.')
            return redirect(overview)
        else:
            print(form.errors)
    else:
        form = PaybackForm(initial={'who_from': request.user.username})
    return render(request, 'payback_form.html', {'form': form})
