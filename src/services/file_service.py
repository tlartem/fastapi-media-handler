from __future__ import annotations

import mimetypes
import os
from typing import TYPE_CHECKING, Optional

import aiofiles

from src.models import File

if TYPE_CHECKING:
    from fastapi import UploadFile
    from sqlalchemy.ext.asyncio import AsyncSession


async def save_file_to_disk_stream(
    file: UploadFile, destination: str, file_uid: str
) -> str:
    # Генерируем имя файла с использованием UUID
    _, file_extension = os.path.splitext(file.filename)
    unique_filename = f"{file_uid}{file_extension}"
    file_path = os.path.join(destination, unique_filename)

    # Сохраняем файл на диск
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    print(f"File streamed saved to: {file_path}")
    return file_path


async def save_file_to_disk_in_memory(
    file: UploadFile, destination: str, file_uid: str
) -> str:
    # Генерируем имя файла с использованием UUID
    _, file_extension = os.path.splitext(file.filename)
    unique_filename = f"{file_uid}{file_extension}"
    file_path = os.path.join(destination, unique_filename)

    # Сохраняем файл на диск
    content: bytes = await file.read()
    async with aiofiles.open(file_path, "wb") as out_file:
        await out_file.write(content)

    print(f"File normal saved to: {file_path}")
    return file_path


async def create_file_record(
    session: AsyncSession,
    original_name: str,
    file_size: int,
    file_extension: str,
    file_uid: str,
    file_format: Optional[str] = None,
) -> str:
    new_file = File(
        uid=file_uid,
        original_name=original_name,
        file_size=file_size,
        file_extension=file_extension,
        file_format=file_format,
    )
    session.add(new_file)
    await session.commit()
    return file_uid


async def get_file_by_uid(session: AsyncSession, file_uid: str) -> Optional[File]:
    from sqlalchemy import select

    result = await session.execute(select(File).where(File.uid == file_uid))
    return result.scalar_one_or_none()


def get_file_format_by_extension(file: UploadFile) -> str:
    """
    Определяет тип файла по расширению.

    Если пользователь может загрузить файл не того расширения, то следует использовать анализатор первых байт файла.
    """

    file_type, _ = mimetypes.guess_type(file.filename)
    return file_type or "unknown"
