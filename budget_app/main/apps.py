from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'

    # def ready(self):
    #     from recurring_expenses.add_recurring_expenses import add_scheduled_expenses
    #     add_scheduled_expenses()

