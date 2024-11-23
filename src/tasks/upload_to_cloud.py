import asyncio

from src.services.s3_storage import YandexCloudProvider
from src.tasks.celery_app import app as celery


@celery.task(name="upload_file_to_cloud", ignore_result=True)
def upload_file_to_cloud(*args, **kwargs):
    asyncio.run(_upload_file_to_cloud(*args, **kwargs))


async def _upload_file_to_cloud(
    provider_name: str, file_path: str, destination_name: str
) -> None:
    provider = YandexCloudProvider()
    await provider.upload(destination_name, file_path)
