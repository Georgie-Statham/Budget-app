from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .forms import RecurringForm
from .models import Recurring

# class based editing views

class RecurringDelete(DeleteView):
    model = Recurring
    template_name_suffix = '_delete_form'
    success_message = 'Recurring expense successfully deleted.'
    success_url = reverse_lazy('scheduled')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(RecurringDelete, self).delete(request, *args, **kwargs)

# views

@login_required(login_url='/accounts/login/')
def scheduled(request):
    scheduled_expenses = Recurring.objects.all().order_by('next_date')
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
            return redirect(scheduled)
        else:
            print(form.errors)
    else:
        form = RecurringForm(initial={'who_paid': request.user.username})
    return render(request, 'recurring_form.html', {'form': form})
