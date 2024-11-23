import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DiskCleaner:
    """
    Класс для очистки заданной директории от старых файлов.
    """

    def __init__(self, directory: Union[str, Path], max_age_days: int):
        self.directory = Path(directory)
        self.max_age = timedelta(days=max_age_days)

    def clean(self) -> None:
        """
        Запускает процесс очистки директории.
        """
        if not self.directory.exists() or not self.directory.is_dir():
            logging.error(
                f"Путь {self.directory} не существует или не является директорией."
            )
            return

        cutoff_time = datetime.now() - self.max_age
        logging.info(
            f"Начало очистки {self.directory}. Файлы старше {cutoff_time} будут удалены."
        )

        files_deleted = 0

        for file_path in self.directory.iterdir():
            if file_path.is_file() and self._is_file_old(file_path, cutoff_time):
                try:
                    file_path.unlink()
                    logging.info(f"Удален файл: {file_path}")
                    files_deleted += 1
                except Exception as e:
                    logging.error(f"Ошибка при удалении файла {file_path}: {e}")

        logging.info(f"Очистка завершена. Удалено файлов: {files_deleted}")

    def _is_file_old(self, file_path: Path, cutoff_time: datetime) -> bool:
        """
        Проверяет, старше ли файл заданного времени.
        """
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return file_mtime < cutoff_time


if __name__ == "__main__":
    DIRECTORY_TO_CLEAN = "uploads/"
    MAX_FILE_AGE_DAYS = 7

    cleaner = DiskCleaner(
        directory=DIRECTORY_TO_CLEAN,
        max_age_days=MAX_FILE_AGE_DAYS,
    )
    cleaner.clean()
