"""
Router de Notificaciones
Endpoints para enviar emails, WhatsApp y recordatorios
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from ..schemas import (
    EmailRequest, WhatsAppRequest, NotificacionAsesoria,
    RecordatorioRequest, RespuestaExito, RespuestaError
)
from ..services.email_service import EmailService
from ..services.whatsapp_service import WhatsAppService
from ..services.scheduler_service import SchedulerService

router = APIRouter()

# Instanciar servicios
email_service = EmailService()
whatsapp_service = WhatsAppService()
scheduler_service = SchedulerService()


@router.post("/email", response_model=RespuestaExito)
async def enviar_email(request: EmailRequest, background_tasks: BackgroundTasks):
    """
    Enviar email individual
    """
    try:
        # Enviar en background para no bloquear
        background_tasks.add_task(
            email_service.enviar_email,
            destinatario=request.destinatario,
            asunto=request.asunto,
            mensaje=request.mensaje,
            tipo=request.tipo_notificacion,
            datos=request.datos_adicionales
        )
        
        return RespuestaExito(
            mensaje="Email enviado exitosamente",
            datos={"destinatario": request.destinatario}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar email: {str(e)}")


@router.post("/whatsapp", response_model=RespuestaExito)
async def enviar_whatsapp(request: WhatsAppRequest):
    """
    Enviar mensaje por WhatsApp usando Twilio
    """
    try:
        resultado = whatsapp_service.enviar_mensaje(
            numero=request.numero,
            mensaje=request.mensaje
        )
        
        return RespuestaExito(
            mensaje="WhatsApp enviado exitosamente",
            datos=resultado
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar WhatsApp: {str(e)}")


@router.post("/asesoria", response_model=RespuestaExito)
async def notificar_asesoria(notificacion: NotificacionAsesoria, background_tasks: BackgroundTasks):
    """
    Enviar notificaciones completas de asesoría
    (Email al programador y usuario, opcional WhatsApp)
    """
    try:
        # Preparar datos para el template
        datos = {
            "id_asesoria": notificacion.id_asesoria,
            "nombre_programador": notificacion.nombre_programador,
            "nombre_usuario": notificacion.nombre_usuario,
            "fecha": notificacion.fecha_asesoria,
            "hora": notificacion.hora_asesoria,
            "motivo": notificacion.motivo or "No especificado",
            "estado": notificacion.estado.value,
            "mensaje_respuesta": notificacion.mensaje_respuesta
        }
        
        # Determinar tipo de email según estado
        if notificacion.estado.value == "pendiente":
            tipo_email = "nueva_asesoria"
            # Email al programador
            background_tasks.add_task(
                email_service.enviar_email,
                destinatario=notificacion.email_programador,
                asunto=f"Nueva solicitud de asesoría de {notificacion.nombre_usuario}",
                mensaje="Tienes una nueva solicitud de asesoría",
                tipo=tipo_email,
                datos=datos
            )
        
        elif notificacion.estado.value == "aprobada":
            tipo_email = "asesoria_aprobada"
            # Email al usuario
            background_tasks.add_task(
                email_service.enviar_email,
                destinatario=notificacion.email_usuario,
                asunto="Tu asesoría ha sido aprobada",
                mensaje=f"Tu asesoría con {notificacion.nombre_programador} fue aprobada",
                tipo=tipo_email,
                datos=datos
            )
        
        elif notificacion.estado.value == "rechazada":
            tipo_email = "asesoria_rechazada"
            # Email al usuario
            background_tasks.add_task(
                email_service.enviar_email,
                destinatario=notificacion.email_usuario,
                asunto="Actualización de tu solicitud de asesoría",
                mensaje=f"Tu solicitud con {notificacion.nombre_programador} fue rechazada",
                tipo=tipo_email,
                datos=datos
            )
        
        # WhatsApp si está habilitado
        if notificacion.tipo_notificacion in ["whatsapp", "ambos"]:
            if notificacion.telefono_programador:
                mensaje_wa = f"Hola {notificacion.nombre_programador}! Nueva asesoría: {notificacion.fecha_asesoria} a las {notificacion.hora_asesoria}"
                background_tasks.add_task(
                    whatsapp_service.enviar_mensaje,
                    numero=notificacion.telefono_programador,
                    mensaje=mensaje_wa
                )
        
        return RespuestaExito(
            mensaje=f"Notificaciones de asesoría enviadas ({notificacion.estado.value})",
            datos={"id_asesoria": notificacion.id_asesoria}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al notificar asesoría: {str(e)}")


@router.post("/recordatorio", response_model=RespuestaExito)
async def programar_recordatorio(recordatorio: RecordatorioRequest):
    """
    Programar recordatorio automático antes de la asesoría
    """
    try:
        job_id = scheduler_service.programar_recordatorio(
            id_asesoria=recordatorio.id_asesoria,
            fecha_hora=recordatorio.fecha_hora_asesoria,
            email_programador=recordatorio.email_programador,
            email_usuario=recordatorio.email_usuario,
            minutos_antes=recordatorio.minutos_antes
        )
        
        return RespuestaExito(
            mensaje="Recordatorio programado exitosamente",
            datos={
                "job_id": job_id,
                "asesoria": recordatorio.id_asesoria,
                "se_enviara_en": f"{recordatorio.minutos_antes} minutos antes"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al programar recordatorio: {str(e)}")


@router.get("/pendientes")
async def obtener_recordatorios_pendientes():
    """
    Obtener lista de recordatorios programados
    """
    try:
        recordatorios = scheduler_service.obtener_jobs_pendientes()
        return {
            "total": len(recordatorios),
            "recordatorios": recordatorios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener recordatorios: {str(e)}")