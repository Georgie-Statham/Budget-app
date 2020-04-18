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
from main.views import calculate_balance_GBP
from main.currency_converter import currency_converter

# Helper functions
def calculate_balances_AUD():
    balances = {}
    balance_in_GBP = calculate_balance_GBP()
    for user, balance_GBP in balance_in_GBP.items():
        balance_AUD = balance_GBP * currency_converter(
            'AUD', 'GBP', date.today())
        balances[user] = (
            balance_GBP.quantize(Decimal('.01')),
            balance_AUD.quantize(Decimal('.01'))
        )
    return balances

# Class based editing views

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
    balances = calculate_balances_AUD()
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
            if form.cleaned_data['currency'] == 'GBP':
                data.GBP = amount
                data.ILS = amount * currency_converter('ILS', 'GBP', date)
                data.AUD = amount * currency_converter('AUD', 'GBP', date)
            if form.cleaned_data['currency'] == 'AUD':
                data.AUD = amount
                data.GBP = amount * currency_converter('GBP', 'AUD', date)
                data.ILS = amount * currency_converter('ILS', 'AUD', date)
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Payback successfully recorded.')
            return redirect(overview)
        else:
            print(form.errors)
    else:
        form = PaybackForm(initial={'who_from': request.user.username})
    context = {
       'form': form,
       'balances': calculate_balances_AUD()
    }
    return render(request, 'payback_form.html', context)
