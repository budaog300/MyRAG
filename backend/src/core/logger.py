import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

from src.core.constants import LOG_DIR
from src.core.request_context import request_id_ctx, task_id_ctx


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.task_id = task_id_ctx.get()
        return True


class DailyFileHandler(RotatingFileHandler):
    def __init__(
        self,
        log_dir: Path,
        filename_prefix: str = "backend",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ):
        self.log_dir = log_dir
        self.filename_prefix = filename_prefix
        self.current_date = datetime.now().date()

        log_dir.mkdir(parents=True, exist_ok=True)

        filename = self._get_filename()

        super().__init__(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )

    def _get_filename(self) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        return str(self.log_dir / f"{self.filename_prefix}_{date}.log")

    def emit(self, record: logging.LogRecord) -> None:
        current_date = datetime.now().date()

        if current_date != self.current_date:
            self.current_date = current_date

            self.close()
            self.baseFilename = self._get_filename()
            self.stream = self._open()

        super().emit(record)


def setup_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | task_id=%(task_id)s | %(message)s")

        request_id_filter = RequestIdFilter()

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        console.addFilter(request_id_filter)

        file_handler = DailyFileHandler(log_dir=LOG_DIR, filename_prefix="backend", max_bytes=10 * 1024 * 1024, backup_count=5)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_id_filter)

        logger.addHandler(console)
        logger.addHandler(file_handler)

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

    return logger