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

def past_months():
    current_month_and_year = (this_month().month, this_month().year)
    month_list = []
    for expense in Expense.objects.all():
        month, year = expense.date.strftime("%b"), expense.date.strftime("%Y")
        if not (month, year) in month_list:
            month_list.append((month, year))
    return month_list

# editing views

class ExpenseUpdate(UpdateView):
    model = Expense
    fields = ['date', 'description', 'category', 'amount',
            'currency', 'who_for', 'who_paid']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('current_month')

class ExpenseDelete(DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('current_month')

class PreviousExpenseUpdate(UpdateView):
    model = Expense
    fields = ['date', 'description', 'category', 'amount',
            'currency', 'who_for', 'who_paid']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('home')

# class PreviousExpenseUpdate(UpdateView):
#     model = Expense
#     fields = ['date', 'description', 'category', 'amount',
#             'currency', 'who_for', 'who_paid']
#     template_name_suffix = '_update_form'

#     def month(self, pk):
#         expense_object = Expense.object.filter(pk=pk)
#         date = expense_object.date
#         month = expense.date.strftime("%b")
#         return self.month

#     def year(self, pk):
#         expense_object = Expense.object.filter(pk=pk)
#         date = expense_object.date
#         year = expense.date.strftime("%Y")
#         return self.year

    # def get_success_url(self):
    #     return reverse_lazy('previous_month', args = (
    #                                     self.month, self.year))


class PreviousExpenseDelete(DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('home')

# views

@login_required(login_url='/accounts/login/')
def current_month(request):
    expenses_this_month = Expense.objects.filter(
        date__gte=this_month()).order_by('-date')
    months = past_months()
    context = {
        'expenses_this_month': expenses_this_month,
        'months': months
    }
    return render(request, 'current_month.html', context)

@login_required(login_url='/accounts/login/')
def previous_month(request, month, year):
    month_datetime = datetime.strptime(month, '%b')
    month_int = month_datetime.strftime("%m")
    expenses_in_month = Expense.objects.filter(
            date__year=year, date__month=month_int).order_by('-date')
    context = {
        'expenses_in_month': expenses_in_month,
        'month': month,
        'year': year,
    }
    return render(request, 'previous_month.html', context)
