"""
Capa de Configuracion - Backend FastAPI
Proyecto: Sistema de Portafolio de Programadores
Autor: Estudiante
Fecha: 2026
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Clase de configuracion del sistema.
    Maneja las variables de entorno para conexion con otros microservicios.
    """
    
    # URLs de microservicios
    spring_boot_url: str = "http://localhost:8081/api"
    jakarta_ee_url: str = "http://localhost:8080/backproyecto/api"
    database_url: str = "mysql+pymysql://root:password@localhost:3306/portafolio_programadores"
    
    # Configuracion de correo electronico (Brevo API)
    brevo_api_key: str = ""
    email_from: str = "jordystream270@gmail.com"
    email_from_name: str = "Portafolio Devs"
    
    # Configuracion de WhatsApp (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
    
    # Configuracion del servidor
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
    """Obtener instancia de configuracion (patron Singleton)"""
    return Settings()


settings = get_settings()