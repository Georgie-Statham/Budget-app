from datetime import date
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import *
import requests
import json

from .currency_converter import currency_converter
from recurring_expenses.models import Recurring
from .models import Expense


def reschedule(expense, relativedelta):
    """Calculates next date to add expense"""
    expense.next_date = expense.next_date + relativedelta
    expense.save()

def add_recurring_expense(expense):
    """Adds a single scheduled expense and schedules next date"""
    if expense.currency == 'GBP':
        converted_amount = expense.amount
    else:
        converted_amount = expense.amount * currency_converter(
            'GBP', expense.currency, expense.next_date)
    Expense.objects.create(
        date=expense.next_date,
        description=expense.description,
        category=expense.category,
        amount=expense.amount,
        converted_amount=converted_amount,
        currency=expense.currency,
        who_for=expense.who_for,
        who_paid=expense.who_paid
    )
    if expense.how_often == 'Weekly':
        reschedule(expense, relativedelta(weeks=1))
    if expense.how_often == 'Fortnightly':
        reschedule(expense, relativedelta(weeks=2))
    if expense.how_often == 'Monthly':
        reschedule(expense, relativedelta(months=1))

def add_scheduled_expenses():
    """Adds all scheduled expenses from current date or earlier """
    for item in Recurring.objects.filter(next_date__lte=date.today()):
        add_recurring_expense(item)


