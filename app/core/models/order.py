import uuid

from django.db import models
from django.utils import timezone

from core.models.currency import Currency
from core.models.customer import Customer


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    is_waiting = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
