"""카드와 현금 결제 방식을 정의한다."""


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
        try:
            change = calculate_change(paid, self.amount)
        except ValueError as error:
            print(error)
            return False
        print(f"현금 결제 완료: {self.amount:,}원 , 잔돈 {change:,}원")
        return True


def calculate_change(received: int, total: int) -> int:
    """받은 현금에서 결제 금액을 빼서 잔돈을 구한다."""
    if received < total:
        raise ValueError("금액이 부족합니다.")
    return received - total
