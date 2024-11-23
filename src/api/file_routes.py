from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import quote

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse

from src import tasks
from src.config import settings
from src.db_conn import get_session
from src.models import File
from src.services.file_service import (
    create_file_record,
    get_file_by_uid,
    get_file_format_by_extension,
    save_file_to_disk_in_memory,
    save_file_to_disk_stream,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    request: Request,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    content_length: Optional[str] = request.headers.get("content-length")
    if content_length:
        file_size = int(content_length)

    file_uid = str(uuid.uuid4())

    # Сохранение файла на диск
    if file_size < 10 * 1024 * 1024:
        file_path: str = await save_file_to_disk_in_memory(
            file, settings.STORAGE_PATH, file_uid=file_uid
        )
    else:
        file_path: str = await save_file_to_disk_stream(
            file, settings.STORAGE_PATH, file_uid=file_uid
        )

    # Получение метаданных файла
    file_size: int = os.path.getsize(file_path)
    file_extension: str = os.path.splitext(file.filename)[1]
    file_format: str = get_file_format_by_extension(file)

    # Генерация записи в базе данных
    await create_file_record(
        session=session,
        original_name=file.filename,
        file_size=file_size,
        file_extension=file_extension,
        file_uid=file_uid,
        file_format=file_format,
    )

    tasks.upload_file_to_cloud.delay(
        provider_name="yandex",
        file_path=file_path,
        destination_name=f"{file_uid}{os.path.splitext(file.filename)[1]}",
    )

    return {"uid": file_uid}


@router.get("/{uid}", status_code=status.HTTP_200_OK)
async def get_file(
    uid: str,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    file_record: Optional[File] = await get_file_by_uid(session, uid)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return {
        "uid": file_record.uid,
        "original_name": file_record.original_name,
        "file_size": file_record.file_size,
        "file_extension": file_record.file_extension,
        "file_format": file_record.file_format,
    }


@router.get("/download/{uid}", status_code=status.HTTP_200_OK)
async def download_file(
    uid: str,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    # Получение записи файла из базы данных
    file_record: Optional[File] = await get_file_by_uid(session, uid)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Локальный путь к файлу
    local_file_path: str = os.path.join(
        settings.STORAGE_PATH, f"{file_record.uid}{file_record.file_extension}"
    )

    # Если файл не существует локально
    if not os.path.exists(local_file_path):
        file_key = f"{file_record.uid}{file_record.file_extension}"

        from src.services.s3_storage import YandexCloudProvider

        yandex_provider = YandexCloudProvider()

        try:
            file_path: str = await yandex_provider.download(
                file_key=file_key, save_path=local_file_path
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in cloud storage",
            )
    else:
        file_path = local_file_path

    # Асинхронное чтение файла
    async def file_stream(file_path: str):
        async with aiofiles.open(file_path, mode="rb") as file:
            while chunk := await file.read(settings.CHUNK_SIZE):
                yield chunk

    # Кодировка имени файла для заголовка
    encoded_filename = quote(file_record.original_name)

    # Возврат файла через поток
    return StreamingResponse(
        file_stream(file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )
