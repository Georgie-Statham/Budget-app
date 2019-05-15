from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import *
import requests
import json

from main.views import currency_converter
from .models import Recurring
from main.models import Expense


def add_recurring_expense(expense):
    """ Adds a single scheduled expense and schedules next date to add"""
    calc_conv_amount = currency_converter(
            'GBP', expense.currency, expense.next_date)
    Expense.objects.create(
        date=expense.next_date,
        description=expense.description,
        category=expense.category,
        amount=expense.amount,
        converted_amount=calc_conv_amount,
        currency=expense.currency,
        who_for=expense.who_for,
        who_paid=expense.who_paid
    )
    if expense.how_often == 'Weekly':
        expense.next_date = expense.next_date + relativedelta(weeks=1)
    if expense.how_often == 'Fortnightly':
        expense.next_date = expense.next_date + relativedelta(weeks=2)
    if expense.how_often == 'Monthly':
        expense.next_date = expense.next_date + relativedelta(months=1)
    expense.save()

def add_scheduled_expenses():
    """ Adds all scheduled expenses from current date or earlier """
    for expense in Recurring.objects.filter(next_date__lte=date.today()):
        add_recurring_expense(expense)


