"""상품과 메뉴를 관리한다."""

if __package__:
    from .menu_data import MENU_DATA
else:
    from menu_data import MENU_DATA


class Product:
    """모든 상품의 공통 가격, 재고, 매출을 관리한다."""

    def __init__(self, name: str, price: int, stock: int, category: str) -> None:
        self.name, self.price, self.category = name, price, category
        self.__stock = stock  # 재고는 외부에서 직접 바꾸지 못하도록 캡슐화한다.
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

    def select_options(self) -> tuple[str, int] | None:
        """기본 상품은 추가 옵션 없이 판매한다."""
        return "", 0

    def __str__(self) -> str:
        stock = "SOLD OUT" if self.stock == 0 else f"재고 {self.stock}"
        return f"{self.name} / {self.price:,}원 / {stock}"


class Beverage(Product):
    """음료 사이즈와 샷 또는 시럽 추가금을 처리한다."""

    def select_options(self) -> tuple[str, int] | None:
        size = input("사이즈 (1 Small / 2 Medium +500원 / 3 Large +1,000원): ").strip()
        sizes = {"1": ("Small", 0), "2": ("Medium", 500), "3": ("Large", 1000)}
        if size not in sizes:
            print("잘못된 사이즈입니다.")
            return None
        option, option_price = sizes[size]

        extra = input("추가 옵션 (1 샷 +500원 / 2 시럽 +500원 / 3 없음): ").strip()
        if extra not in {"1", "2", "3"}:
            print("잘못된 옵션입니다.")
            return None
        if extra in {"1", "2"}:
            option += " + " + ("샷" if extra == "1" else "시럽")
            option_price += 500
        return option, option_price


class Food(Product):
    """푸드의 워밍 여부를 선택하며 추가금은 없다."""

    def select_options(self) -> tuple[str, int] | None:
        warming = input("워밍 선택 (1 워밍 / 2 노워밍): ").strip()
        if warming not in {"1", "2"}:
            print("잘못된 워밍 선택입니다.")
            return None
        return ("워밍" if warming == "1" else "노워밍"), 0


class MDProduct(Product):
    """MD 상품은 정해진 가격 그대로 판매한다."""

    def select_options(self) -> tuple[str, int] | None:
        """MD에는 크기나 추가 옵션을 적용하지 않는다."""
        return "", 0


class Menu:
    """초기 상품 데이터로 메뉴를 만들고 카테고리별 상품을 제공한다."""

    PRODUCT_CLASSES = {"음료": Beverage, "푸드": Food, "MD": MDProduct}

    def __init__(self) -> None:
        self.products: dict[str, list[Product]] = {
            category: [self.PRODUCT_CLASSES[category](name, price, stock, category)
                       for name, price, stock in entries]
            for category, entries in MENU_DATA.items()
        }

    def all_products(self) -> list[Product]:
        return [product for products in self.products.values() for product in products]

    def show_recommendations(self) -> None:
        print("\n추천 메뉴 (카테고리별 누적 매출 BEST)")
        for category, products in self.products.items():
            best = max(products, key=lambda product: product.sales)
            print(f"{category} BEST: {best.name} (매출 {best.sales:,}원)")


def show_main_menu() -> None:
    """키오스크 첫 화면의 선택지를 출력한다."""
    print("\n======================\n      CAFE KIOSK\n======================")
    print("1. 음료  2. 푸드  3. MD  4. 추천 메뉴  5. 장바구니  6. 주문 취소  0. 종료")


def select_category(key: str) -> str | None:
    """입력 번호를 상품 카테고리 이름으로 바꾼다."""
    return {"1": "음료", "2": "푸드", "3": "MD"}.get(key)
