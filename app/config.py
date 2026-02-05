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
    
    # Email - SMTP (Gmail u otro proveedor)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""  # tu_email@gmail.com
    smtp_password: str = ""  # Contraseña de aplicación (NO tu contraseña normal)
    email_from: str = ""     # Mismo email que smtp_username
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