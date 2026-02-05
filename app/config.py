"""
Configuración del Backend FastAPI
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración general"""
    
    spring_boot_url: str = "http://localhost:8081/api"
    jakarta_ee_url: str = "http://localhost:8080/backproyecto/api"
    database_url: str = "mysql+pymysql://root:password@localhost:3306/portafolio_programadores"
    
    # Email - Brevo API (300 emails/día GRATIS)
    brevo_api_key: str = ""  # xkeysib-xxxxx
    email_from: str = "jordystream270@gmail.com"  # Tu email verificado en Brevo
    email_from_name: str = "Portafolio Devs"
    
    # WhatsApp - Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
    
    # Configuración API
    api_port: int = 8000
    debug: bool = True
    frontend_url: str = "http://localhost:4200"
    redis_url: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()