import logging
from decimal import Decimal

logger = logging.getLogger("django")


class ExchangeService:
    @staticmethod
    def buy_from_exchange(currency: str, amount: Decimal):
        """
        External exchange to settle the order.
        :param currency:
        :param amount:
        :return:
        """
        logger.info(f"Order for {amount} \"{currency}\" has been settled.")
