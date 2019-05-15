from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        # import requests
        # import json
        # from main.views import currency_converter
        from recurring_expenses.add_recurring_expenses import add_recurring_expense, add_scheduled_expenses
        add_scheduled_expenses()
