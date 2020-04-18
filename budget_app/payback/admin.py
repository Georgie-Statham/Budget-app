from django.contrib import admin

from .models import Payback

class PaybackAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'who_from', 'who_to', 'amount', 'currency', 'GBP',
        'AUD', 'method'
    )

admin.site.register(Payback, PaybackAdmin)
