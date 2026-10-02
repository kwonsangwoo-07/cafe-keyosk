"""손님과 점원 정보를 관리한다."""

from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    if __package__:
        from .order import Order
    else:
        from order import Order


class Person:
    def __init__(self, name: str, status: str = "일반") -> None:
        self.name = name
        self.status = status


class Customer(Person):
    """회원 등급과 제휴카드에 따른 할인율을 계산한다."""

    DISCOUNTS: ClassVar[dict[str, float]] = {"일반": 0.0, "실버": 0.05, "골드": 0.10}

    def discount_rate(self, partner_card: bool = False) -> float:
        return min(self.DISCOUNTS.get(self.status, 0.0) + (0.02 if partner_card else 0), 0.20)


class Staff(Person):
    """손님 응대와 상품 준비 상태를 담당한다."""

    def greet(self) -> None:
        print(f"점원: 어서 오세요, {self.name} 카페입니다!")

    def prepare(self, order: Order) -> None:
        order.status = "제조중"
        print("점원: 주문 확인했습니다. 제조를 시작합니다. (대기시간 약 4분)")
        order.status = "제조완료"


