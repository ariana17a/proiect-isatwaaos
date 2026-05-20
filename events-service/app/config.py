from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "University Events API"
    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    database_url: str = "sqlite:///./app.db"

    # Prepared for future Google OAuth integration.
    google_client_id: str = ""
    google_client_secret: str = ""
    google_allowed_domain: str = "student.usv.ro"

    frontend_event_base_url: str = "http://localhost:3000/events"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
