import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "asyncpg==0.29.0", "sqlalchemy[asyncio]==2.0.30"
)
