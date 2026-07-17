from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env
    """

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    DATA_FILE: str

    DATABASE_URL: str

    AWS_REGION: str
    COGNITO_USER_POOL_ID: str
    COGNITO_CLIENT_ID: str
    COGNITO_CLIENT_SECRET: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str

    CELERY_BROKER_URL: str

    EMBEDDING_PROVIDER: str
    EMBEDDING_MODEL: str

    CHROMA_DB_PATH: str
    CHROMA_COLLECTION_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()