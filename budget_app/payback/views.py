from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PaybackForm
from .models import Payback
from main.views import get_exchange_rate


@login_required(login_url='/accounts/login/')
def overview(request):
    return render(request, 'payback.html')

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
