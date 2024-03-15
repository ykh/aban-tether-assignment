import os
from decimal import Decimal

from django.utils import timezone
from pydantic import validate_call
from rest_framework import exceptions

from core.models import Currency, Customer
from core.models.order import Order
from core.serializers.order_serializers import CreateOrderSerializer
from core.services.cache_service import CacheService
from core.services.exchange_service import ExchangeService
from core.validators.order_validators import CreateOrderValidator


class OrderService:
    @staticmethod
    @validate_call
    def create_order(
            order_data: CreateOrderValidator
    ) -> CreateOrderSerializer:
        # Find currency.
        try:
            currency = Currency.objects.get(name__exact=order_data.name)
        except Order.DoesNotExist:
            raise exceptions.NotFound(
                f"Given currency \"{order_data.name}\" not found."
            )

        # Find customer.
        try:
            customer = Customer.objects.get(id=order_data.customer_id)
        except Customer.DoesNotExist:
            raise exceptions.NotFound("Customer not found.")

        # Calculate total cost.
        order_cost = currency.price * order_data.amount

        # Create an Order object.
        order = Order.objects.create(
            currency_id=currency.id,
            customer_id=customer.id,
            amount=order_data.amount,
            cost=order_cost,
        )

        # Straightforward scenario.
        if order_cost >= float(os.environ.get("MIN_USD_ORDER")):
            order.is_waiting = False
            order.is_completed = True
            order.completed_at = timezone.now()

            order.save()

            # Update customer's credit.
            if customer.credit < order_cost:
                raise exceptions.NotAcceptable(
                    "Customer's credit is not enough for this order."
                )

            customer.credit -= order_cost

            customer.save()

            ExchangeService.buy_from_exchange(
                order_data.name,
                order_data.amount
            )

            return CreateOrderSerializer.from_orm(order)

        # Batching orders scenario.
        batch_orders = CacheService.find_batch_orders(
            order.id,
            order.currency.name,
            order.cost,
        )

        if not batch_orders:
            CacheService.set_order(
                order.id,
                order.currency.name,
                order.cost,
            )

            order.is_waiting = True
            order.is_completed = False
            order.completed_at = None

            order.save()

            return CreateOrderSerializer.from_orm(order)

        orders = Order.objects.filter(id__in=batch_orders)
        total_amount = Decimal(0)

        for _order in orders:
            # Update credit for each customer.
            _customer = _order.customer

            if _customer.credit < _order.cost:
                raise exceptions.NotAcceptable(
                    "Customer's credit is not enough for this order."
                )

            _customer.credit -= _order.cost

            _customer.save()

            # Update order fields.
            _order.is_waiting = False
            _order.is_completed = True
            _order.completed_at = timezone.now()

            _order.save()

            total_amount += _order.amount

        # Call exchange method.
        ExchangeService.buy_from_exchange(
            order.currency.name,
            total_amount,
        )

        order.refresh_from_db()

        return CreateOrderSerializer.from_orm(order)
