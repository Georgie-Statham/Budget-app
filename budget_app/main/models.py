from django.db import models
from datetime import date

class Expense(models.Model):
    CATEGORIES = (
        ('Food', 'Food'),
        ('Baby', 'Baby'),
        ('Entertainment', 'Entertainment'),
        ('Health', 'Pharmacy/Health'),
        ('Hobbies', 'Hobbies'),
        ('Rent', 'Rent'),
        ('Bills', 'Utility bills'),
        ('Clothes', 'Clothes'),
        ('Household', 'Household'),
        ('Cat', 'Cat'),
        ('Transport', 'Transport'),
        ('Travel', 'Travel'),
        ('Misc', 'Miscellaneous')
    )
    CURRENCIES = (('ILS', 'ILS'), ('GBP', 'GBP'))
    WHO_FOR = (
        ('Everyone', 'Everyone'),
        ('Claire', 'Claire'),
        ('Tristan', 'Tristan'),
        ('Georgie', 'Georgie')
    )
    WHO_PAID = (
        ('Claire', 'Claire'),
        ('Tristan', 'Tristan'),
        ('Georgie', 'Georgie')
    )


    date = models.DateField(default=date.today)
    description = models.CharField(max_length=100)
    category = models.CharField(
            max_length=20,
            choices=CATEGORIES,
            default='Food')
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    converted_amount = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(
            max_length=3,
            choices=CURRENCIES,
            default='ILS')
    who_for = models.CharField(
            max_length=10,
            choices=WHO_FOR,
            default='Everyone')
    who_paid = models.CharField(
            max_length=10,
            choices=WHO_PAID)

