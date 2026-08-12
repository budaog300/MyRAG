from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_ORDER_STATUS = "Новая"

DATE_FORMAT = "%d.%m.%Y %H:%M"

SERVICES_HEADERS = (
    "Название",
    "Цена",
)

ORDERS_HEADERS = (
    "Дата",
    "Имя",
    "Телефон",
    "Услуга",
    "Желаемое время",
    "Статус",
)