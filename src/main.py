"""카페 키오스크: 상품, 주문, 재고, 결제 흐름을 보여 주는 콘솔 프로그램."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import ClassVar
from person import Person

class Customer(Person):
    DISCOUNTS: ClassVar[dict[str, float]] = {"일반": 0.0, "실버": 0.05, "골드": 0.10}

    def discount_rate(self, partner_card: bool = False) -> float:
        return min(self.DISCOUNTS.get(self.status, 0.0) + (0.02 if partner_card else 0), 0.20)


class Staff(Person):
    def greet(self) -> None:
        print(f"점원: 어서 오세요, {self.name} 카페입니다!")

    def prepare(self, order: Order) -> None:
        order.status = "제조중"
        print("점원: 주문 확인했습니다. 제조를 시작합니다. (대기시간 약 4분)")
        order.status = "제조완료"


class Product:
    def __init__(self, name: str, price: int, stock: int, category: str) -> None:
        self.name, self.price, self.category = name, price, category
        self.__stock = stock
        self.sales = 0

    @property
    def stock(self) -> int:
        return self.__stock

    def restock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("입고 수량은 1개 이상이어야 합니다.")
        self.__stock += quantity

    def sell(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("수량은 1개 이상이어야 합니다.")
        if quantity > self.__stock:
            raise ValueError(f"재고 부족: {self.name} (남은 재고 {self.__stock}개)")
        self.__stock -= quantity
        self.sales += self.price * quantity

    def __str__(self) -> str:
        stock = "SOLD OUT" if self.stock == 0 else f"재고 {self.stock}"
        return f"{self.name} / {self.price:,}원 / {stock}"


class Beverage(Product):
    pass


class Food(Product):
    pass


class MDProduct(Product):
    pass


@dataclass
class CartItem:
    product: Product
    quantity: int = 1
    option: str = ""
    option_price: int = 0

    @property
    def unit_price(self) -> int:
        return self.product.price + self.option_price


_order_numbers = count(1)


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


class Payment:
    def __init__(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("결제 금액은 음수일 수 없습니다.")
        self.amount = amount

    def pay(self) -> bool:
        raise NotImplementedError


class CardPayment(Payment):
    def pay(self) -> bool:
        print(f"카드 결제 승인: {self.amount:,}원")
        return True


class CashPayment(Payment):
    def pay(self, received: str) -> bool:  # type: ignore[override]
        try:
            paid = int(received.replace(",", "").strip())
        except (ValueError, AttributeError):
            print("잘못된 입력입니다. 숫자로 입력해주세요.")
            return False
        if paid < self.amount:
            print("금액이 부족합니다.")
            return False
        print(f"현금 결제 완료: {self.amount:,}원 , 잔돈 {paid - self.amount:,}원")
        return True


def calculate_total(items: list[CartItem]) -> int:
    return sum(item.unit_price * item.quantity for item in items)


def calculate_change(received: int, total: int) -> int:
    if received < total:
        raise ValueError("금액이 부족합니다.")
    return received - total


# 메인메뉴 출력
def show_main_menu() -> None:
    print("\n======================\n      CAFE KIOSK\n======================")
    print("1. 음료  2. 푸드  3. MD  4. 추천 메뉴  5. 장바구니  6. 주문 취소  0. 종료")


def select_category(key: str) -> str | None:
    return {"1": "음료", "2": "푸드", "3": "MD"}.get(key)
# key, value 값을 받기위해서 -> get을 사용한다. 리스트{}를 받았을때, {"",""} 이런식으로 표현한다.


def show_receipt(order: Order) -> None:
    print("\n---------- 영수증 ----------")
    print(f"주문번호: {order.order_number} ({order.service_type})")
    for item in order.items:
        label = f" {item.option}" if item.option else ""
        print(f"{item.product.name}{label} x {item.quantity}: {item.unit_price * item.quantity:,}원")
    print(f"주문금액: {order.subtotal:,}원")
    print(f"할인: -{order.discount:,}원")
    print(f"최종금액: {order.total:,}원")
    print(f"결제방법: {order.payment_method}")
    print("----------------------------")


def show_waiting_time() -> None:
    print("상품을 준비하고 있습니다. 대기시간은 약 4분입니다.")


def check_customer() -> bool:
    return input("손님이 방문했나요? (Enter: 예, q: 영업 종료): ").strip().lower() != "q"


class Kiosk:
    def __init__(self) -> None:
        self.menu: dict[str, list[Product]] = {
            "음료": [Beverage("아메리카노", 4500, 10, "음료"), Beverage("카페라떼", 5000, 5, "음료"),
                    Beverage("녹차", 4000, 8, "음료"), Beverage("초코 블렌디드", 5500, 6, "음료")],
            "푸드": [Food("햄치즈 샌드위치", 6000, 2, "푸드"), Food("크로와상", 3500, 8, "푸드"), Food("감자빵", 4000, 6, "푸드")],
            "MD": [MDProduct("화이트 텀블러", 30000, 3, "MD"), MDProduct("머그컵", 15000, 5, "MD")],
        }
        self.cart: list[CartItem] = []
        self.staff = Staff("바리스타")

    def all_products(self) -> list[Product]:
        return [product for products in self.menu.values() for product in products]

    def show_recommendations(self) -> None:
        print("\n추천 메뉴 (카테고리별 누적 매출 BEST)")
        for category, products in self.menu.items():
            best = max(products, key=lambda product: product.sales)
            print(f"{category} BEST: {best.name} (매출 {best.sales:,}원)")

    # dic = 연산자 [] , 카테고리의 값에 들어간다, products(인스턴스 = 실체)
    def add_item(self, category: str) -> None:
        products = self.menu[category]
        print(f"\n[{category}]")
        
        for index, product in enumerate(products, 1):
            print(f"{index}. {product}")
        
        raw = input("상품 번호 (0: 뒤로): ").strip()
        if raw == "0":
            return
        
        try:
            product = products[int(raw) - 1]
        except (ValueError, IndexError):
            print("잘못된 메뉴 번호입니다.")
            return
        
        if product.stock == 0 :
            print("SOLD OUT")
            return
        
        option, option_price = "", 0
        if isinstance(product, Beverage):
            size = input("사이즈 (1 Small / 2 Medium +500원 / 3 Large +1,000원): ").strip()
            if size not in {"1", "2", "3"}:
                print("잘못된 사이즈입니다.")
                return
            option = {"1": "Small", "2": "Medium", "3": "Large"}[size]
            option_price = {"1": 0, "2": 500, "3": 1000}[size]
            extra = input("추가 옵션 (1 샷 +500원 / 2 시럽 +500원 / 3 없음): ").strip()
            if extra not in {"1", "2", "3"}:
                print("잘못된 옵션입니다.")
                return
            if extra in {"1", "2"}:
                option += " + " + ("샷" if extra == "1" else "시럽")
                option_price += 500
        try:
            quantity = int(input("수량: "))
            if quantity < 1 or quantity > product.stock:
                print(f"주문 수량을 확인해주세요. 현재 재고 {product.stock}개")
                return
        except ValueError:
            print("숫자를 입력해주세요.")
            return
        self.cart.append(CartItem(product, quantity, option, option_price))
        print(f"장바구니에 담았습니다. 현재 합계 {calculate_total(self.cart):,}원")

    def show_cart(self) -> None:
        if not self.cart:
            print("장바구니가 비어 있습니다.")
            return
        print("\n장바구니")
        for index, item in enumerate(self.cart, 1):
            option = f" {item.option}" if item.option else ""
            print(f"{index}. {item.product.name}{option} x {item.quantity}: {item.unit_price * item.quantity:,}원")
        print(f"합계: {calculate_total(self.cart):,}원")
        action = input("번호를 입력해 삭제, Enter: 계속 쇼핑, p: 결제: ").strip().lower()
        if action == "p":
            self.checkout()
        elif action:
            try:
                del self.cart[int(action) - 1]
            except (ValueError, IndexError):
                print("잘못된 번호입니다.")

    def checkout(self) -> None:
        if not self.cart:
            print("장바구니가 비어 있습니다.")
            return
        service = input("이용 방법 (1 매장 / 2 포장): ").strip()
        if service not in {"1", "2"}:
            print("잘못된 선택입니다.")
            return
        member = input("회원 등급 (1 일반 / 2 실버 / 3 골드): ").strip()
        customer = Customer("손님", {"1": "일반", "2": "실버", "3": "골드"}.get(member, "일반"))
        partner_card = input("제휴카드가 있나요? (y/n): ").strip().lower() == "y"
        subtotal = calculate_total(self.cart)
        discount = int(subtotal * customer.discount_rate(partner_card))
        order = Order(self.cart.copy(), "매장" if service == "1" else "포장", subtotal=subtotal, discount=discount)
        print(f"결제 예정 금액: {order.total:,}원 (할인 {discount:,}원)")
        method = input("결제 방법 (1 카드 / 2 현금): ").strip()
        payment: Payment
        if method == "1":
            payment = CardPayment(order.total)
            success = payment.pay()
            order.payment_method = "카드"
        elif method == "2":
            payment = CashPayment(order.total)
            success = payment.pay(input("받은 금액: "))
            order.payment_method = "현금"
        else:
            print("잘못된 결제 방법입니다.")
            return
        if not success:
            print("결제가 완료되지 않아 주문을 보류했습니다. 장바구니를 유지합니다.")
            return
        try:
            for item in order.items:
                item.product.sell(item.quantity)
        except ValueError as error:
            print(error)
            print("결제를 취소하고 장바구니를 유지합니다.")
            return
        order.status = "결제완료"
        self.staff.prepare(order)
        show_waiting_time()
        order.status = "수령완료"
        print("점원: 주문하신 상품 나왔습니다. 감사합니다!")
        print(order)
        if input("영수증을 출력할까요? (y/n): ").strip().lower() == "y":
            show_receipt(order)
        self.cart.clear()

    def run(self) -> None:
        print("카페 키오스크에 오신 것을 환영합니다.")
        while check_customer() :
            self.staff.greet()

            while True :
                show_main_menu()

                choice = input("번호 선택: ").strip()
                category = select_category(choice)

                if category:
                    self.add_item(category)
                elif choice == "4":
                    self.show_recommendations()
                elif choice == "5":
                    self.show_cart()
                elif choice == "6":
                    self.cart.clear()
                    print("주문과 장바구니를 취소했습니다.")
                elif choice == "0":
                    print("주문 없이 돌아갑니다.")
                    break
                else:
                    print("잘못된 입력입니다. 메뉴 번호를 선택해주세요.")
                
                if not self.cart :
                    continue
            
                if input("주문을 마치고 결제할까요? (y: 결제 / Enter: 계속): ").strip().lower() == "y" :
                    before = len(self.cart)
                    self.checkout()
                    if len(self.cart) < before or not self.cart :
                        break
            print("점원: 이용해 주셔서 감사합니다. 안녕히 가세요!")
        print("손님이 없어 매장을 정리합니다. 영업을 종료합니다.")


def main() -> None:
    Kiosk().run()


if __name__ == "__main__":
    main()
