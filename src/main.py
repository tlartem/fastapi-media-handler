from fastapi import FastAPI

from src.api.file_routes import router as files_router
from src.db_conn import init_db

app: FastAPI = FastAPI()

# Подключение роутов
app.include_router(files_router, prefix="/files", tags=["Files"])


@app.on_event("startup")
async def startup() -> None:
    await init_db()
