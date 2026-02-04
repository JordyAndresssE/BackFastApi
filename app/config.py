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
    
    # Email - Resend API
    resend_api_key: str = ""
    email_from: str = "noreply@portafolio.com"
    email_from_name: str = "Portafolio Devs"
    
    # Legacy SMTP (deprecated, usar Resend)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
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