from dataclasses import dataclass
from core.enums import OrderStatus

@dataclass
class OrderInfo:
    id: str
    status: OrderStatus
    title: str
    element_selector: str