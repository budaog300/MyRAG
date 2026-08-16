import io
from pathlib import Path
from markitdown import MarkItDown


class DocumentConverterService:
    def __init__(self):
        self.converter = MarkItDown()

    def convert(
        self,
        *,
        source: str | Path | None = None,
        content: str | None = None,
        file_bytes: bytes | None = None,
    ) -> str:
        """
        Конвертирует документ в Markdown.

        Источник может быть:
        - уже готовый текст через content;
        - bytes через file_bytes;
        - путь к файлу через source.
        """

        if content is not None:
            return content

        if file_bytes is not None:
            if source is None:
                raise ValueError(
                    "Для file_bytes необходимо указать source с расширением файла"
                )

            extension = Path(source).suffix

            result = self.converter.convert_stream(
                io.BytesIO(file_bytes),
                file_extension=extension,
            )

            return result.text_content

        if source is not None:
            path = Path(source)

            if not path.exists():
                raise FileNotFoundError(f"Файл не найден: {path}")

            result = self.converter.convert(path)

            return result.text_content

        raise ValueError("Не указан источник документа")