from dataclasses import dataclass
from enums import OrderStatus

@dataclass
class OrderInfo:
    id: str
    status: OrderStatus
    title: str
    element_selector: str