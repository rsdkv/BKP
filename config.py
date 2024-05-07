from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    SHODAN_KEY: str
    
    @property
    def BOT_TOKEN(self):
        return f"{self.TELEGRAM_BOT_TOKEN}"
    
    @property
    def SHODAN_API_KEY(self):
        return f"{self.SHODAN_KEY}"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()