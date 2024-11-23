from typing import Any, Dict, List

import aiobotocore
import aiobotocore.client
import aiobotocore.session
import aiofiles
from aiobotocore.client import AioBaseClient

from src.config import settings
from src.services.s3_storage.storage_protocol import CloudStorageProvider


class YandexCloudProvider(CloudStorageProvider):
    def __init__(self):
        self.s3_config = {
            "region_name": settings.AWS_S3_REGION_NAME,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "endpoint_url": settings.AWS_S3_ENDPOINT_URL,
        }

    async def upload(self, filename_key: str, file_path: str) -> None:
        """
        Загружает файл в облако Яндекс S3 с использованием Multipart Upload.

        :param filename_key: Имя файла в облаке (ключ).
        :param file_path: Локальный путь к файлу.
        """
        session = aiobotocore.session.AioSession()

        async with session.create_client("s3", **self.s3_config) as client:
            upload_id = await self._initiate_multipart_upload(client, filename_key)
            parts_info = await self._upload_parts(
                client, filename_key, upload_id, file_path
            )
            await self._complete_multipart_upload(
                client, filename_key, upload_id, parts_info
            )

    async def _initiate_multipart_upload(
        self, client: AioBaseClient, filename_key: str
    ) -> str:
        """
        Инициализирует multipart-загрузку и возвращает Upload ID.

        :param client: Клиент S3.
        :param filename_key: Имя файла в облаке (ключ).
        :return: Идентификатор загрузки (Upload ID).
        """
        response = await client.create_multipart_upload(
            Key=filename_key,
            Bucket=settings.BACKET_NAME,
        )
        return response["UploadId"]

    async def _upload_parts(
        self, client: AioBaseClient, filename_key: str, upload_id: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Загружает файл по частям.

        :param client: Клиент S3.
        :param filename_key: Имя файла в облаке (ключ).
        :param upload_id: Идентификатор загрузки (Upload ID).
        :param file_path: Путь к локальному файлу для загрузки.
        :return: Информация о загруженных частях.
        """
        parts_info = []
        part_number = 0

        async with aiofiles.open(file_path, mode="rb") as file:
            while True:
                contents = await file.read(settings.READ_CHUNK_SIZE)
                if not contents:
                    break

                part_number += 1
                response = await client.upload_part(
                    Body=contents,
                    UploadId=upload_id,
                    PartNumber=part_number,
                    Key=filename_key,
                    Bucket=settings.BACKET_NAME,
                )
                parts_info.append(
                    {
                        "PartNumber": part_number,
                        "ETag": response["ETag"],
                    }
                )

        return parts_info

    async def _complete_multipart_upload(
        self,
        client: AioBaseClient,
        filename_key: str,
        upload_id: str,
        parts_info: List[Dict[str, Any]],
    ) -> None:
        """
        Завершает multipart-загрузку.

        :param client: Клиент S3.
        :param filename_key: Имя файла в облаке (ключ).
        :param upload_id: Идентификатор загрузки (Upload ID).
        :param parts_info: Информация о загруженных частях.
        """
        await client.complete_multipart_upload(
            UploadId=upload_id,
            Key=filename_key,
            Bucket=settings.BACKET_NAME,
            MultipartUpload={"Parts": parts_info},
        )

    async def download(self, file_key: str, save_path: str) -> None:
        """
        Скачивает один файл из облака S3 и сохраняет его локально.

        :param bucket_name: Имя S3-бакета.
        :param file_key: Ключ файла в бакете.
        :param save_path: Локальный путь для сохранения файла.
        """
        session = aiobotocore.session.AioSession()

        async with session.create_client("s3", **self.s3_config) as client:
            response = await client.get_object(
                Bucket=settings.BACKET_NAME, Key=file_key
            )

            async with aiofiles.open(save_path, mode="wb") as local_file:
                while chunk := await response["Body"].read(settings.CHUNK_SIZE):
                    await local_file.write(chunk)

        print(f"Файл {file_key} успешно скачан и сохранён в {save_path}.")

        return save_path
