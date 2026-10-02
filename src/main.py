"""카페 키오스크 프로그램의 실행 진입점."""

if __package__:
    from .kiosk import Kiosk
else:
    from kiosk import Kiosk


def main() -> None:
    """키오스크를 만들어 실행한다."""
    Kiosk().run()


if __name__ == "__main__":
    main()
