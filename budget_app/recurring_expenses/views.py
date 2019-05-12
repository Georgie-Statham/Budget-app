from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import RecurringForm

@login_required(login_url='/accounts/login/')
def scheduled(request):
    return render(request, 'scheduled.html')

@login_required(login_url='/accounts/login/')
def recurring_form(request):
    if request.method == 'POST':
        form = RecurringForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=True)
            messages.add_message(
                request, messages.SUCCESS, 'Recurring expense successfully added.')
            return redirect(home)
        else:
            print(form.errors)
    else:
        form = RecurringForm(initial={'who_paid': request.user.username})
    return render(request, 'recurring_form.html', {'form': form})
