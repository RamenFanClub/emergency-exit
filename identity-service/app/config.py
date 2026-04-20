from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Service configuration loaded from environment variables."""

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "ee_identity"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    class Config:
        env_file = ".env"


settings = Settings()
