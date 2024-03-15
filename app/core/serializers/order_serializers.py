from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, UUID4


class CreateOrderSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    currency_id: UUID4
    customer_id: UUID4
    amount: Decimal
    cost: Decimal
    is_waiting: bool
    is_completed: bool
    ordered_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
