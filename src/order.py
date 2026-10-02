"""장바구니 항목과 주문 정보를 관리한다."""

from dataclasses import dataclass, field
from itertools import count

if __package__:
    from .menu import Product
else:
    from menu import Product


@dataclass
class CartItem:
    product: Product
    quantity: int = 1
    option: str = ""
    option_price: int = 0

    @property
    def unit_price(self) -> int:
        return self.product.price + self.option_price


_order_numbers = count(1)  # 주문번호는 프로그램 실행 중 순서대로 부여한다.


@dataclass
class Order:
    items: list[CartItem]
    service_type: str
    payment_method: str = "미결제"
    status: str = "주문접수"
    order_number: int = field(default_factory=lambda: next(_order_numbers))
    subtotal: int = 0
    discount: int = 0

    @property
    def total(self) -> int:
        return max(0, self.subtotal - self.discount)

    def __str__(self) -> str:
        return f"주문번호 {self.order_number} / 총금액 {self.total:,}원 / {self.payment_method}"


def calculate_total(items: list[CartItem]) -> int:
    """옵션 가격과 수량을 반영한 장바구니 합계를 계산한다."""
    return sum(item.unit_price * item.quantity for item in items)
