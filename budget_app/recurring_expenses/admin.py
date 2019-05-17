from django.contrib import admin

from .models import Recurring

class RecurringAdmin(admin.ModelAdmin):
    list_display = (
        'how_often', 'description', 'category', 'amount', 'currency'
    )

admin.site.register(Recurring, RecurringAdmin)
