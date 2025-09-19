from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    njt_username: str
    njt_password: str
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()
