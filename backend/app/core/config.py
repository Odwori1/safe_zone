import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "safe_zone")
    db_user: str = os.getenv("DB_USER", "safe_zone_user")
    db_password: str = os.getenv("DB_PASSWORD", "0791486006@safezone")  # Correct password

    # Security
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3001").split(",")

    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Timezone & Internationalization (NEW)
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "UTC")
    supported_locales: List[str] = os.getenv("SUPPORTED_LOCALES", "en-US,es-ES,fr-FR,de-DE").split(",")

    # S3 File Storage (Phase 3, Item 3)
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "safe-zone-media")
    s3_presigned_expiry: int = int(os.getenv("S3_PRESIGNED_EXPIRY", "3600"))

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
