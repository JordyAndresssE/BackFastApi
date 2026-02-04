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
async def enviar_email(request: EmailRequest):
    """
    Enviar email individual (modo síncrono para ver logs completos)
    """
    try:
        print(f"\n📧 ENVIANDO EMAIL INDIVIDUAL")
        print(f"   Destinatario: {request.destinatario}")
        print(f"   Asunto: {request.asunto}")
        
        # Enviar de forma síncrona para ver los logs
        resultado = email_service.enviar_email(
            destinatario=request.destinatario,
            asunto=request.asunto,
            mensaje=request.mensaje,
            tipo=request.tipo_notificacion,
            datos=request.datos_adicionales
        )
        
        if resultado:
            return RespuestaExito(
                mensaje="Email enviado exitosamente",
                datos={"destinatario": request.destinatario}
            )
        else:
            raise HTTPException(status_code=500, detail="Error al enviar email, revisa los logs")
            
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
    
    FLUJO:
    - Estado 'pendiente' → Email al PROGRAMADOR (nueva solicitud)
    - Estado 'aprobada' → Email al USUARIO + WhatsApp al PROGRAMADOR (confirmación)
    - Estado 'rechazada' → Email al USUARIO (solicitud rechazada)
    - Estado 'cancelada' → Email al USUARIO (asesoría cancelada)
    """
    print(f"\n{'='*70}")
    print(f"🔔 NOTIFICACIÓN DE ASESORÍA")
    print(f"{'='*70}")
    print(f"ID Asesoría: {notificacion.id_asesoria}")
    print(f"Estado: {notificacion.estado.value}")
    print(f"Usuario: {notificacion.nombre_usuario} ({notificacion.email_usuario})")
    print(f"Programador: {notificacion.nombre_programador} ({notificacion.email_programador})")
    print(f"Fecha: {notificacion.fecha_asesoria} {notificacion.hora_asesoria}")
    print(f"{'='*70}\n")
    
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
            print("📨 ENVIANDO → Email al PROGRAMADOR (nueva solicitud)")
            tipo_email = "nueva_asesoria"
            # Email al programador (SÍNCRONO para ver logs)
            email_service.enviar_email(
                destinatario=notificacion.email_programador,
                asunto=f"Nueva solicitud de asesoría de {notificacion.nombre_usuario}",
                mensaje="Tienes una nueva solicitud de asesoría",
                tipo=tipo_email,
                datos=datos
            )
        
        elif notificacion.estado.value == "aprobada":
            print("📨 ENVIANDO → Email al USUARIO (aprobada)")
            print("📱 ENVIANDO → WhatsApp al PROGRAMADOR (recordatorio)")
            tipo_email = "asesoria_aprobada"
            
            # Email al usuario (SÍNCRONO)
            email_service.enviar_email(
                destinatario=notificacion.email_usuario,
                asunto="✅ Tu asesoría ha sido aprobada",
                mensaje=f"Tu asesoría con {notificacion.nombre_programador} fue aprobada",
                tipo=tipo_email,
                datos=datos
            )
            
            # WhatsApp al PROGRAMADOR (recordatorio)
            if notificacion.telefono_programador:
                mensaje_wa = f"✅ Asesoría aprobada!\n📅 {notificacion.fecha_asesoria} a las {notificacion.hora_asesoria}\n👤 Con: {notificacion.nombre_usuario}"
                whatsapp_service.enviar_mensaje(
                    numero=notificacion.telefono_programador,
                    mensaje=mensaje_wa
                )
        
        elif notificacion.estado.value == "rechazada":
            print("📨 ENVIANDO → Email al USUARIO (rechazada)")
            tipo_email = "asesoria_rechazada"
            # Email al usuario (SÍNCRONO)
            email_service.enviar_email(
                destinatario=notificacion.email_usuario,
                asunto="❌ Actualización de tu solicitud de asesoría",
                mensaje=f"Tu solicitud con {notificacion.nombre_programador} fue rechazada",
                tipo=tipo_email,
                datos=datos
            )
        
        elif notificacion.estado.value == "cancelada":
            print("📨 ENVIANDO → Email al USUARIO (cancelada)")
            tipo_email = "asesoria_rechazada"  # Usar mismo template
            # Email al usuario (SÍNCRONO)
            email_service.enviar_email(
                destinatario=notificacion.email_usuario,
                asunto="🚫 Asesoría cancelada",
                mensaje=f"La asesoría con {notificacion.nombre_programador} ha sido cancelada",
                tipo=tipo_email,
                datos=datos
            )
        
        print(f"\n✅ NOTIFICACIONES COMPLETADAS\n{'='*70}\n")
        
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