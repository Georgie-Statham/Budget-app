from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RecurringForm
from .models import Recurring

@login_required(login_url='/accounts/login/')
def scheduled(request):
    scheduled_expenses = Recurring.objects.all()
    return render(
        request,
        'scheduled.html',
        {'scheduled_expenses': scheduled_expenses}
    )

@login_required(login_url='/accounts/login/')
def recurring_form(request):
    if request.method == 'POST':
        form = RecurringForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.next_date = form.cleaned_data['start_date']
            data.save()
            messages.add_message(
                request, messages.SUCCESS, 'Recurring expense successfully added.')
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = RecurringForm(initial={'who_paid': request.user.username})
    return render(request, 'recurring_form.html', {'form': form})
