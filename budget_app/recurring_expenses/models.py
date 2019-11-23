from django.db import models
from django.contrib.auth.models import User
import django.contrib.auth
from django.core.exceptions import ValidationError
from datetime import date

class Recurring(models.Model):
    CATEGORIES = (
        ('Food', 'Food'),
        ('Baby', 'Baby'),
        ('Fun_with_friends', 'Fun with friends'),
        ('Fun_with_each_other', 'Fun with each other'),
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
    CURRENCIES = (('ILS', 'ILS'), ('GBP', 'GBP'), ('AUD', 'AUD'))

    USERS = [
        (user.username, user.username)
        for user in User.objects.all()
    ]
    WHO_FOR = USERS.copy()
    WHO_FOR.append(('Everyone', 'Everyone'))

    TIME_PERIODS = (
        ('Weekly', 'Weekly'),
        ('Fortnightly', 'Fortnightly'),
        ('Monthly', 'Monthly'),
    )

    start_date = models.DateField(default=date.today)
    next_date = models.DateField()
    how_often = models.CharField(
            max_length=11,
            choices=TIME_PERIODS,
        )
    description = models.CharField(max_length=100)
    category = models.CharField(
            max_length=20,
            choices=CATEGORIES,
            default='Food')
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(
            max_length=3,
            choices=CURRENCIES,
            default='AUD')
    who_for = models.CharField(
            max_length=10,
            choices=WHO_FOR,
            default='Everyone')
    who_paid = models.CharField(
            max_length=11,
            choices=USERS,
        )
