from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from datetime import date, datetime

from main.models import Expense


# helper functions

def this_month():
    return timezone.now().replace(day=1, hour=0, minute=0, second=0)

def months_so_far():
    month_list = []
    for expense in Expense.objects.all():
        month, year = expense.date.strftime("%b"), expense.date.strftime("%Y")
        if not (month, year) in month_list:
            month_list.append((month, year))
    return month_list

# class based editing views

class ExpenseUpdate(UpdateView):
    model = Expense
    fields = ['date', 'description', 'category', 'amount',
            'currency', 'who_for', 'who_paid']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        self.month = self.kwargs['month']
        self.year = self.kwargs['year']
        return reverse_lazy(
        'detailed_month', kwargs={'month': self.month, 'year': self.year})

class ExpenseDelete(DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        self.month = self.kwargs['month']
        self.year = self.kwargs['year']
        return reverse_lazy(
        'detailed_month', kwargs={'month': self.month, 'year': self.year})

# views

@login_required(login_url='/accounts/login/')
def detailed_month(request, month, year):
    month_datetime = datetime.strptime(month, '%b')
    month_int = month_datetime.strftime("%m")
    expenses_in_month = Expense.objects.filter(
            date__year=year, date__month=month_int).order_by('-date')
    months = months_so_far()
    context = {
        'expenses_in_month': expenses_in_month,
        'month': month,
        'year': year,
        'months': months
    }
    return render(request, 'detailed_month.html', context)
