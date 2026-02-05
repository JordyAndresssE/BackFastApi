"""
Capa de Datos - Modelos Pydantic
Proyecto: Sistema de Portafolio de Programadores
Define los esquemas de validacion de datos para la API
Autor: Estudiante
Fecha: 2026
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# Enumeraciones para estados y tipos
class EstadoAsesoria(str, Enum):
    """Estados posibles de una asesoria"""
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"


class TipoNotificacion(str, Enum):
    """Tipos de notificaciones disponibles"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    AMBOS = "ambos"


class FormatoReporte(str, Enum):
    """Formatos de exportacion de reportes"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


# Esquemas para notificaciones
class EmailRequest(BaseModel):
    """Esquema para solicitud de envio de email"""
    destinatario: EmailStr
    asunto: str
    mensaje: str
    tipo_notificacion: str = Field(..., description="nueva_asesoria, aprobada, rechazada, recordatorio")
    datos_adicionales: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "destinatario": "programador@example.com",
                "asunto": "Nueva solicitud de asesoria",
                "mensaje": "Tienes una nueva solicitud de asesoria",
                "tipo_notificacion": "nueva_asesoria",
                "datos_adicionales": {
                    "nombre_usuario": "Juan Perez",
                    "fecha": "2026-02-15",
                    "hora": "10:00"
                }
            }
        }


class WhatsAppRequest(BaseModel):
    """Esquema para solicitud de envio de WhatsApp"""
    numero: str = Field(..., description="Numero en formato +593999999999")
    mensaje: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero": "+593999999999",
                "mensaje": "Hola! Tienes una nueva asesoria agendada."
            }
        }


class NotificacionAsesoria(BaseModel):
    """Esquema para notificacion completa de asesoria"""
    id_asesoria: str
    email_programador: EmailStr
    nombre_programador: str
    email_usuario: EmailStr
    nombre_usuario: str
    fecha_asesoria: str
    hora_asesoria: str
    motivo: Optional[str] = None
    estado: EstadoAsesoria
    mensaje_respuesta: Optional[str] = None
    tipo_notificacion: TipoNotificacion = TipoNotificacion.EMAIL
    telefono_programador: Optional[str] = None
    telefono_usuario: Optional[str] = None


class RecordatorioRequest(BaseModel):
    """Esquema para programar recordatorio"""
    id_asesoria: str
    fecha_hora_asesoria: datetime
    email_programador: EmailStr
    email_usuario: EmailStr
    minutos_antes: int = 30
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_asesoria": "ASES123",
                "fecha_hora_asesoria": "2026-02-15T10:00:00",
                "email_programador": "dev@example.com",
                "email_usuario": "cliente@example.com",
                "minutos_antes": 30
            }
        }


# Esquemas para reportes
class FiltrosReporteAsesorias(BaseModel):
    """Esquema de filtros para reporte de asesorias"""
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    id_programador: Optional[str] = None
    estado: Optional[EstadoAsesoria] = None
    formato: FormatoReporte = FormatoReporte.JSON


class FiltrosReporteProyectos(BaseModel):
    """Esquema de filtros para reporte de proyectos"""
    id_programador: Optional[str] = None
    tipo: Optional[str] = None
    formato: FormatoReporte = FormatoReporte.JSON


class EstadisticaAsesoria(BaseModel):
    """Esquema para estadisticas de asesorias"""
    total: int
    pendientes: int
    aprobadas: int
    rechazadas: int
    canceladas: int


class EstadisticaProyecto(BaseModel):
    """Esquema para estadisticas de proyectos"""
    total: int
    academicos: int
    laborales: int
    por_tecnologia: dict


class DashboardAsesorias(BaseModel):
    """Esquema para dashboard de asesorias"""
    estadisticas: EstadisticaAsesoria
    asesorias_recientes: List[dict]
    por_programador: List[dict]
    por_fecha: List[dict]


class DashboardProyectos(BaseModel):
    """Esquema para dashboard de proyectos"""
    estadisticas: EstadisticaProyecto
    proyectos_recientes: List[dict]
    por_programador: List[dict]
    tecnologias_populares: List[dict]


# Esquemas de respuesta
class RespuestaExito(BaseModel):
    """Esquema para respuesta exitosa"""
    mensaje: str
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    """Esquema para respuesta de error"""
    error: str
    detalle: Optional[str] = None