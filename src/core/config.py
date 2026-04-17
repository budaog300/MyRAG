from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsAI(BaseSettings):
    API_KEY: str
    API_URL: str
    BASE_URL: str

    model_config = SettingsConfigDict(env_file=".env.ai")

    @property
    def get_auth_data(self) -> dict:
        return {
            "API_KEY": self.API_KEY,
            "API_URL": self.API_URL,
            "BASE_URL": self.BASE_URL,
        }


class SettingsQdrant(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env.qdrant")

    @property
    def get_auth_data(self) -> dict:
        return {"QDRANT_URL": self.QDRANT_URL, "QDRANT_API_KEY": self.QDRANT_API_KEY}


class SettingsBot(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env.bot")

    @property
    def get_auth_data(self) -> dict:
        return {"TELEGRAM_BOT_TOKEN": self.TELEGRAM_BOT_TOKEN}


settingsAI = SettingsAI()
settingsQdrant = SettingsQdrant()
settingsBot = SettingsBot()
