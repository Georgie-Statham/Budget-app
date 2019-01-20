from django.contrib import admin

from .models import Expense

class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'description', 'category', 'amount', 'currency', 'who_for',
        'who_paid')

admin.site.register(Expense, ExpenseAdmin)
