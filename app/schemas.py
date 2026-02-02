"""
Modelos Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class EstadoAsesoria(str, Enum):
    """Estados posibles de una asesoría"""
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"


class TipoNotificacion(str, Enum):
    """Tipos de notificaciones"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    AMBOS = "ambos"


class FormatoReporte(str, Enum):
    """Formatos de reporte"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


# ==========================================
# NOTIFICACIONES
# ==========================================

class EmailRequest(BaseModel):
    """Request para enviar email"""
    destinatario: EmailStr
    asunto: str
    mensaje: str
    tipo_notificacion: str = Field(..., description="nueva_asesoria, aprobada, rechazada, recordatorio")
    datos_adicionales: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "destinatario": "programador@example.com",
                "asunto": "Nueva solicitud de asesoría",
                "mensaje": "Tienes una nueva solicitud de asesoría",
                "tipo_notificacion": "nueva_asesoria",
                "datos_adicionales": {
                    "nombre_usuario": "Juan Pérez",
                    "fecha": "2026-02-15",
                    "hora": "10:00"
                }
            }
        }


class WhatsAppRequest(BaseModel):
    """Request para enviar WhatsApp"""
    numero: str = Field(..., description="Número en formato +593999999999")
    mensaje: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero": "+593999999999",
                "mensaje": "Hola! Tienes una nueva asesoría agendada."
            }
        }


class NotificacionAsesoria(BaseModel):
    """Notificación completa de asesoría"""
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
    """Request para programar recordatorio"""
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


# ==========================================
# REPORTES
# ==========================================

class FiltrosReporteAsesorias(BaseModel):
    """Filtros para reporte de asesorías"""
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    id_programador: Optional[str] = None
    estado: Optional[EstadoAsesoria] = None
    formato: FormatoReporte = FormatoReporte.JSON


class FiltrosReporteProyectos(BaseModel):
    """Filtros para reporte de proyectos"""
    id_programador: Optional[str] = None
    tipo: Optional[str] = None
    formato: FormatoReporte = FormatoReporte.JSON


class EstadisticaAsesoria(BaseModel):
    """Estadística de asesorías"""
    total: int
    pendientes: int
    aprobadas: int
    rechazadas: int
    canceladas: int


class EstadisticaProyecto(BaseModel):
    """Estadística de proyectos"""
    total: int
    academicos: int
    laborales: int
    por_tecnologia: dict


class DashboardAsesorias(BaseModel):
    """Dashboard de asesorías"""
    estadisticas: EstadisticaAsesoria
    asesorias_recientes: List[dict]
    por_programador: List[dict]
    por_fecha: List[dict]


class DashboardProyectos(BaseModel):
    """Dashboard de proyectos"""
    estadisticas: EstadisticaProyecto
    proyectos_recientes: List[dict]
    por_programador: List[dict]
    tecnologias_populares: List[dict]


# ==========================================
# RESPUESTAS GENÉRICAS
# ==========================================

class RespuestaExito(BaseModel):
    """Respuesta exitosa genérica"""
    mensaje: str
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    """Respuesta de error"""
    error: str
    detalle: Optional[str] = None