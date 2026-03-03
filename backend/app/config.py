from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    supabase_url: str
    supabase_key: str
    max_file_size_mb: int = 10 

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()