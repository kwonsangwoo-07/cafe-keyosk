"""키오스크의 상품 선택, 장바구니, 결제 흐름을 연결한다."""

if __package__:
    from .menu import Menu, Product, select_category, show_main_menu
    from .order import CartItem, Order, calculate_total
    from .payment import CardPayment, CashPayment, Payment
    from .person import Customer, Staff
    from .receipt import show_receipt, show_waiting_time
else:
    from menu import Menu, Product, select_category, show_main_menu
    from order import CartItem, Order, calculate_total
    from payment import CardPayment, CashPayment, Payment
    from person import Customer, Staff
    from receipt import show_receipt, show_waiting_time


def check_customer() -> bool:
    """새 손님을 받을지 확인한다."""
    return input("손님이 방문했나요? (Enter: 예, q: 영업 종료): ").strip().lower() != "q"


class Kiosk:
    """메뉴, 장바구니, 점원을 연결해 손님 주문을 처리한다."""

    def __init__(self) -> None:
        self.menu = Menu()
        self.cart: list[CartItem] = []
        self.staff = Staff("바리스타")

    def all_products(self) -> list[Product]:
        return self.menu.all_products()

    def show_recommendations(self) -> None:
        self.menu.show_recommendations()

    def add_item(self, category: str) -> None:
        """상품과 추가 옵션을 선택해 장바구니에 넣는다."""
        products = self.menu.products[category]
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

        # 각 상품 클래스가 자기 옵션의 입력과 추가금을 계산한다.
        options = product.select_options()
        if options is None:
            return
        option, option_price = options
        try:  # 입력한 수량을 정수로 바꾼다.
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
        """할인과 결제를 처리한 후 재고와 주문 상태를 갱신한다."""
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
        # 회원 할인과 제휴카드 할인을 결제 예정 금액에 반영한다.
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
        # 결제가 끝난 주문만 재고와 매출에 반영한다.
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
        """손님이 방문하는 동안 키오스크 입력을 반복한다."""
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
