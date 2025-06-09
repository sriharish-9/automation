from enum import Enum

class OrderStatus(Enum):
    PROCESSING = "processing"
    INQUIRY = "inquiry"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class CalendarView(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"