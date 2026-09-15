from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./commodity_dashboard.db"

    nasdaq_data_link_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    custom_lme_feed_url: str | None = None
    custom_lme_feed_key: str | None = None

    kite_api_key: str | None = None
    kite_api_secret: str | None = None
    kite_access_token: str | None = None

    smartapi_api_key: str | None = None
    smartapi_client_id: str | None = None
    smartapi_password: str | None = None
    smartapi_totp_secret: str | None = None

    forex_api_key: str | None = None
    forex_provider: str = "exchangerate.host"

    lme_fetch_interval_minutes: int = 30
    mcx_fetch_interval_minutes: int = 15
    nalco_fetch_interval_hours: int = 6
    forex_fetch_interval_minutes: int = 60

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
