from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'date', 'mode')
    search_fields = ('enrollment__student__name',)
    list_filter = ('mode', 'date')

admin.site.register(Payment, PaymentAdmin)