import os
import re
import uuid

from django.core.cache import cache
from pydantic import UUID4


class CacheService:
    @classmethod
    def generate_order_key(cls, order_id: UUID4, currency_name: str) -> str:
        return f"order:{order_id}_cur:{currency_name}"

    @classmethod
    def set_order(cls, order_id, currency_name, cost):
        cache.set(cls.generate_order_key(order_id, currency_name), cost)

    @classmethod
    def get_pending_order(cls, order_id: UUID4):
        keys = cache.keys(f"order:{order_id}*")

        if keys:
            return {
                keys[0]: cache.get(keys[0])
            }

        return None

    @classmethod
    def extract_order_id(cls, key: str):
        match = re.match(r"order:([\w-]*)_", key)

        if match:
            return uuid.UUID(match.group(1))

        return None

    @classmethod
    def find_batch_orders(
            cls,
            new_order_id: UUID4,
            new_order_currency: str,
            new_order_cost: float,
    ):
        """
        Find orders as a batch with total cost higher than MIN_USD_ORDER to
        settlement.
        :param new_order_id:
        :param new_order_currency:
        :param new_order_cost:
        :return:
        """
        pending_order_keys = cache.keys(f"order:*_cur:{new_order_currency}")

        selected_order_ids = [new_order_id]
        selected_order_costs = [new_order_cost]
        selected_order_keys = []

        for order_key in pending_order_keys:
            order_cost = cache.get(order_key)

            selected_order_keys.append(order_key)
            cost = sum(selected_order_costs) + order_cost

            if cost >= float(os.environ.get("MIN_USD_ORDER")):
                for key in selected_order_keys:
                    selected_order_ids.append(cls.extract_order_id(key))
                    cache.delete(key)

                return selected_order_ids

            selected_order_costs.append(order_cost)

        return None
