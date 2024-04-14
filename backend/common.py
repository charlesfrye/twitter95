import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "sqlalchemy", "psycopg2-binary", "sqlmodel"
)
