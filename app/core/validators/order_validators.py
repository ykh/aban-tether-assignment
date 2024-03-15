from decimal import Decimal

from pydantic import UUID4, BaseModel, Field


class CreateOrderValidator(BaseModel):
    customer_id: UUID4
    amount: Decimal = Field(max_digits=20, decimal_places=2, gt=0)
    name: str = Field(max_length=255)
