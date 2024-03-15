from django.contrib import admin

from core.models import Currency, Customer, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'credit', 'created_at', 'updated_at', 'id')
    search_fields = ('name',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at', 'id')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'currency',
        'customer',
        'amount',
        'cost',
        'ordered_at',
        'is_waiting',
        'is_completed',
        'completed_at',
    )

    list_filter = ('currency', 'customer', 'is_waiting', 'is_completed')

    search_fields = (
        'id',
        'customer__name',
        'currency__code'
    )
