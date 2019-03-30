from django.db import models
from django.contrib.auth.models import User
import django.contrib.auth
from django.core.exceptions import ValidationError
from datetime import date
from main.models import no_future

class Payback(models.Model):

    USERS = [
        (user.username, user.username)
        for user in User.objects.all()
    ]
    CURRENCIES = (('ILS', 'ILS'), ('GBP', 'GBP'))
    METHODS = (('Bank_transfer', 'Bank Transfer'), ('Cash', 'Cash'))

    date = models.DateField(default=date.today, validators=[no_future])
    who_from = models.CharField(
            max_length=10,
            choices=USERS,
        )
    who_to = models.CharField(
            max_length=10,
            choices=USERS,
        )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(
            max_length=3,
            choices=CURRENCIES,
            default='GBP')
    amount_in_GBP = models.DecimalField(max_digits=7, decimal_places=2)
    amount_in_ILS = models.DecimalField(max_digits=7, decimal_places=2)
    method = models.CharField(
            max_length=20,
            choices=METHODS,
            default='Bank_transfer'
        )


