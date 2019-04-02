from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from decimal import *
import requests
import json

from .forms import PaybackForm
from .models import Payback
from main.views import get_exchange_rate

# class based editing views

class PaybackUpdate(SuccessMessageMixin, UpdateView):
    model = Payback
    fields = ['date', 'who_from', 'who_to', 'amount',
            'currency', 'method']
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

@login_required(login_url='/accounts/login/')
def overview(request):
    payback_list = Payback.objects.all().order_by('-date')
    context = {'payback_list': payback_list}
    return render(request, 'payback.html', context)

@login_required(login_url='/accounts/login/')
def payback_form(request):
    if request.method == 'POST':
        form = PaybackForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            date = form.cleaned_data['date']
            if form.cleaned_data['currency'] == 'ILS':
                data.amount_in_ILS = form.cleaned_data['amount']
                data.amount_in_GBP = form.cleaned_data['amount'] * get_exchange_rate(date)   # converts ILS to GBP
            else:
                data.amount_in_GBP = form.cleaned_data['amount']
                data.amount_in_ILS = form.cleaned_data['amount'] / get_exchange_rate(date)   # converts GBP to ILS
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Payback successfully recorded.')
            return redirect(overview)
        else:
            print(form.errors)
    else:
        form = PaybackForm(initial={'who_from': request.user.username})
    return render(request, 'payback_form.html', {'form': form})
