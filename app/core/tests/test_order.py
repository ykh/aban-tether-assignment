from datetime import datetime

from django.test import TestCase
from django_redis import get_redis_connection

from core.models import Currency, Customer, Order
from core.serializers.order_serializers import CreateOrderSerializer
from core.services import OrderService
from core.services.cache_service import CacheService
from core.validators.order_validators import CreateOrderValidator


class TestCreateOrder(TestCase):
    def setUp(self) -> None:
        get_redis_connection("default").flushall()

        self.currency_aban = Currency.objects.create(
            name="ABAN",
            price=10,
        )

        self.currency_usdt = Currency.objects.create(
            name="USDT",
            price=1,
        )

        self.currency_btc = Currency.objects.create(
            name="BTC",
            price=71000,
        )

    def test_create_order_with_valid_data(self):
        customer = Customer.objects.create(
            name="Customer A",
            credit=1000,
        )

        class Input:
            customer_id = customer.id
            currency_name = "ABAN"
            amount = 5

        class Expected:
            cost = float(Input.amount * self.currency_aban.price)
            customer_credit = customer.credit - cost

        result: CreateOrderSerializer = OrderService.create_order(
            CreateOrderValidator(
                customer_id=Input.customer_id,
                amount=Input.amount,
                name=Input.currency_name,
            )
        )

        self.assertIsInstance(result, CreateOrderSerializer)

        # Due to better readability, I prefer to use Equal instead of DictEqual.
        self.assertEqual(
            result.currency_id,
            self.currency_aban.id,
            msg="Currency id of the result is wrong.",
        )
        self.assertEqual(
            result.customer_id,
            Input.customer_id,
            msg="Customer's id is wrong.",
        )
        self.assertEqual(
            result.amount,
            Input.amount,
            msg="Amount value is wrong.",
        )
        self.assertEqual(
            result.cost,
            float(Input.amount * self.currency_aban.price),
            msg="Total cost value is not correct.",
        )
        self.assertFalse(result.is_waiting)
        self.assertTrue(result.is_completed)

        self.assertIsInstance(result.completed_at, datetime)

        customer.refresh_from_db()

        self.assertEqual(
            customer.credit,
            Expected.customer_credit,
            msg="Customer's credit value is wrong.",
        )

    def test_create_order_for_batching_pending_orders(self):
        customer = Customer.objects.create(
            name="Customer A",
            credit=1000,
        )

        class Order1Input:
            customer_id = customer.id
            currency_name = "USDT"
            amount = 5

        order1: CreateOrderSerializer = OrderService.create_order(
            CreateOrderValidator(
                customer_id=Order1Input.customer_id,
                amount=Order1Input.amount,
                name=Order1Input.currency_name,
            )
        )

        self.assertTrue(order1.is_waiting)
        self.assertFalse(order1.is_completed)
        self.assertIsNone(order1.completed_at)

        class Order2Input:
            customer_id = customer.id
            currency_name = "USDT"
            amount = 3

        order2: CreateOrderSerializer = OrderService.create_order(
            CreateOrderValidator(
                customer_id=Order2Input.customer_id,
                amount=Order2Input.amount,
                name=Order2Input.currency_name,
            )
        )

        self.assertTrue(order2.is_waiting)
        self.assertFalse(order2.is_completed)
        self.assertIsNone(order2.completed_at)

        class Order3Input:
            customer_id = customer.id
            currency_name = "USDT"
            amount = 3

        order3: CreateOrderSerializer = OrderService.create_order(
            CreateOrderValidator(
                customer_id=Order3Input.customer_id,
                amount=Order3Input.amount,
                name=Order3Input.currency_name,
            )
        )

        self.assertFalse(order3.is_waiting)
        self.assertTrue(order3.is_completed)
        self.assertIsInstance(order3.completed_at, datetime)

        _order = Order.objects.get(id=order1.id)

        self.assertFalse(_order.is_waiting)
        self.assertTrue(_order.is_completed)
        self.assertIsInstance(_order.completed_at, datetime)

        _order = Order.objects.get(id=order2.id)

        self.assertFalse(_order.is_waiting)
        self.assertTrue(_order.is_completed)
        self.assertIsInstance(_order.completed_at, datetime)

        customer.refresh_from_db()

        self.assertEqual(customer.credit, 1000 - 11)

        # All these three orders should be removed from pending list in cache.
        self.assertIsNone(CacheService.get_pending_order(order1.id))
        self.assertIsNone(CacheService.get_pending_order(order2.id))
        self.assertIsNone(CacheService.get_pending_order(order3.id))
