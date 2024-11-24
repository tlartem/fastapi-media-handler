# Задача

Разработать **REST API микросервис** для приёма, обработки и управления медиафайлами. Микросервис должен:

- Принимать файлы через HTTP-запросы.
- Сохранять файлы на локальный диск.
- Отправлять копии файлов в облачное хранилище.
- Генерировать уникальные идентификаторы (UID) для каждого файла.
- Сохранять метаданные файлов в базе данных.

## Технологический стек

- **Язык программирования:** Python
- **Web-фреймворк:** FastAPI
- **База данных:** PostgreSQL
- **ORM:** SQLAlchemy
- **Облачное хранилище:** Использование условного API для демонстрации интеграции

---

## Функциональные требования

1. **Приём файлов:**  
   Поддержка загрузки файлов через HTTP POST запросы. Файлы могут быть любого типа (изображения, видео, аудио и т.д.).

2. **Потоковый приём файлов:**  
   Возможность загрузки файлов через стрим.

3. **Сохранение файлов на диск:**  
   Файлы сохраняются локально после загрузки.

4. **Отправка в облако:**  
   Асинхронная отправка копии файла в облачное хранилище.

5. **Генерация UID:**  
   Генерация уникального идентификатора для каждого файла.

6. **Сохранение метаданных:**  
   Сохранение метаданных файла в PostgreSQL через SQLAlchemy:  
   - Размер
   - Формат
   - Оригинальное название
   - Расширение

---

## Дополнительные задачи (Бонус)

1. **Очистка локального диска:**  
   Реализация крон-задачи для регулярного удаления старых/неиспользуемых файлов.

2. **Получение файла по UID:**  
   Реализация API-метода для скачивания файла по его уникальному идентификатору.

---

## Требования к коду

- Чистый, хорошо структурированный и комментированный код.
- Обработка ошибок.
- Базовые тесты функциональности.
