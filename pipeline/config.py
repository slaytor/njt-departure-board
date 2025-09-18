from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Manages application settings and credentials."""
    njt_username: str
    njt_password: str

    # This tells Pydantic to load variables from a .env file
    class Config:
        env_file = ".env"


# Create a single, importable instance of the settings
settings = Settings()
