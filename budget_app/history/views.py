from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from datetime import date, datetime

from main.models import Expense


# helper functions

def months_so_far():
    month_list = []
    for expense in Expense.objects.all().order_by('-date'):
        month, year = expense.date.strftime("%b"), expense.date.strftime("%Y")
        if not (month, year) in month_list:
            month_list.append((month, year))
    return month_list

# class based editing views

class ExpenseUpdate(SuccessMessageMixin, UpdateView):
    model = Expense
    fields = ['date', 'description', 'category', 'amount',
            'currency', 'who_for', 'who_paid']
    template_name_suffix = '_update_form'
    success_message = 'Expense successfully updated.'

    def get_success_url(self):
        self.month = self.kwargs['month']
        self.year = self.kwargs['year']
        return reverse_lazy(
        'detailed_month', kwargs={'month': self.month, 'year': self.year})

class ExpenseDelete(DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'
    success_message = 'Expense successfully deleted.'

    def get_success_url(self):
        self.month = self.kwargs['month']
        self.year = self.kwargs['year']
        return reverse_lazy(
        'detailed_month', kwargs={'month': self.month, 'year': self.year})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ExpenseDelete, self).delete(request, *args, **kwargs)


# views

@login_required(login_url='/accounts/login/')
def detailed_month(request, month, year):
    category_totals_dict = {}
    family_total = 0
    amount_paid_dict = {}
    individual_breakdown = {}
    month_datetime = datetime.strptime(month, '%b')
    month_int = month_datetime.strftime("%m")

    for category in Expense.CATEGORIES:
        family_expenses_in_category = Expense.objects.filter(
            category=category[0],
            who_for='Everyone',
            date__month=month_int
        )
        category_total = 0
        for expense in family_expenses_in_category:
            category_total += expense.converted_amount
            family_total += expense.converted_amount
            category_totals_dict[category[1]] = category_total

    for person in Expense.USERS:
        expenses_paid_for = Expense.objects.filter(
            who_for='Everyone',
            date__month=month_int,
            who_paid=person[0]
        )
        amount_paid = 0
        for expense in expenses_paid_for:
            amount_paid += expense.converted_amount
        amount_paid_dict[person[0]] = amount_paid

    expenses_in_month = Expense.objects.filter(
            date__year=year, date__month=month_int).order_by('-date')

    for user in Expense.USERS:
        user_category_totals_dict = {}
        user_category_totals_dict['total'] = 0
        user_total = 0
        for category in Expense.CATEGORIES:
            user_expenses_in_category = Expense.objects.filter(
            category=category[0],
            who_for=user[0],
            date__month=month_int
        )
            user_category_total = 0
            for expense in user_expenses_in_category:
                user_category_total += expense.converted_amount
                user_total += expense.converted_amount
                user_category_totals_dict[category[1]] = user_category_total
                user_category_totals_dict['total'] = user_total
            individual_breakdown[user[0]]=user_category_totals_dict

    months = months_so_far()
    context = {
        'expenses_in_month': expenses_in_month,
        'month': month,
        'year': year,
        'months': months,
        'category_totals_dict': category_totals_dict,
        'family_total': family_total,
        'amount_paid_dict': amount_paid_dict,
        'individual_breakdown': individual_breakdown,
    }
    return render(request, 'detailed_month.html', context)