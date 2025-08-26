import os
import re
import ssl
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv



class Config:
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    load_dotenv()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

    # 👇 Flask-SQLAlchemy necesita esta URI
    SQLALCHEMY_DATABASE_URI = re.sub(
        r'^postgresql:',
        'postgresql+psycopg2:',
        os.getenv("DATABASE_URL")
    )

    @staticmethod
    async def async_main() -> None:
        db_url = os.getenv('DATABASE_URL')

        # Reemplazar driver para async
        db_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', db_url)

        # Limpiar parámetros extra (ej: ?sslmode=require)
        clean_url = re.sub(r'\?(.*)', '', db_url)

        # Crear contexto SSL
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = True
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED

        # Engine async
        engine = create_async_engine(
            clean_url,
            connect_args={"ssl": ssl_ctx},
            echo=True
        )

        async with engine.connect() as conn:
            result = await conn.execute(text("select 'hello world'"))
            print(result.fetchall())

        await engine.dispose()


