"""주문 영수증과 대기 안내를 출력한다."""

if __package__:
    from .order import Order
else:
    from order import Order


class Receipt:
    """완료된 주문의 영수증 내용을 출력한다."""

    def __init__(self, order: Order) -> None:
        self.order = order

    def print(self) -> None:
        order = self.order
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


def show_receipt(order: Order) -> None:
    """주문을 영수증 객체에 전달해 출력한다."""
    Receipt(order).print()


def show_waiting_time() -> None:
    """결제 후 예상 대기시간을 안내한다."""
    print("상품을 준비하고 있습니다. 대기시간은 약 4분입니다.")
