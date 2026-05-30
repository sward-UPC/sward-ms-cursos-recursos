from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_url: str = (
        "postgresql+asyncpg://sward:sward@localhost:5432/cursos_recursos_db"
    )
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "sward-recursos-educativos"
    eventbridge_bus_name: str = "sward-event-bus"
    lms_service_url: str = "http://localhost:8002"
    environment: str = "development"
    service_name: str = "sward-ms-cursos-recursos"


settings = Settings()
