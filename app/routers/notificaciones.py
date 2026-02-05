"""
Capa de Presentacion - Router de Notificaciones
Proyecto: Sistema de Portafolio de Programadores
Este router maneja los endpoints para enviar emails, WhatsApp y recordatorios
Autor: Estudiante
Fecha: 2026
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

# Instanciar servicios de la capa de negocio
email_service = EmailService()
whatsapp_service = WhatsAppService()
scheduler_service = SchedulerService()


@router.post("/email", response_model=RespuestaExito)
async def enviar_email(request: EmailRequest):
    """
    Endpoint para enviar un correo electronico individual.
    Recibe los datos del correo y llama al servicio de email.
    """
    try:
        print(f"\nENVIANDO EMAIL INDIVIDUAL")
        print(f"   Destinatario: {request.destinatario}")
        print(f"   Asunto: {request.asunto}")
        
        # Llamar al servicio de email
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
    Endpoint para enviar un mensaje por WhatsApp.
    Utiliza el servicio de Twilio para el envio.
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
    Endpoint principal para notificar sobre asesorias.
    
    Flujo de notificaciones segun el estado:
    - Estado 'pendiente': Email al programador y al usuario
    - Estado 'aprobada': Email a ambos + WhatsApp al usuario
    - Estado 'rechazada': Email a ambos + WhatsApp al usuario
    - Estado 'cancelada': Email a ambos + WhatsApp al usuario
    """
    print(f"\n{'='*70}")
    print(f"NOTIFICACION DE ASESORIA")
    print(f"{'='*70}")
    print(f"ID Asesoria: {notificacion.id_asesoria}")
    print(f"Estado: {notificacion.estado.value}")
    print(f"Usuario: {notificacion.nombre_usuario} ({notificacion.email_usuario})")
    print(f"Programador: {notificacion.nombre_programador} ({notificacion.email_programador})")
    print(f"Fecha: {notificacion.fecha_asesoria} {notificacion.hora_asesoria}")
    print(f"{'='*70}\n")
    
    try:
        # Preparar datos para las plantillas de email
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
        
        # Procesar segun el estado de la asesoria
        if notificacion.estado.value == "pendiente":
            # ASESORIA CREADA - Notificar a programador y usuario
            
            # Email al programador
            print("ENVIANDO - Email al PROGRAMADOR (nueva solicitud)")
            email_service.enviar_email(
                destinatario=notificacion.email_programador,
                asunto=f"Nueva solicitud de asesoria de {notificacion.nombre_usuario}",
                mensaje="Tienes una nueva solicitud de asesoria pendiente de aprobacion",
                tipo="nueva_asesoria",
                datos=datos
            )
            
            # Email al usuario
            print("ENVIANDO - Email al USUARIO (solicitud enviada)")
            email_service.enviar_email(
                destinatario=notificacion.email_usuario,
                asunto=f"Tu solicitud de asesoria fue enviada",
                mensaje=f"Tu solicitud de asesoria con {notificacion.nombre_programador} fue enviada exitosamente. Te notificaremos cuando sea aprobada o rechazada.",
                tipo="generico",
                datos=datos
            )
        
        elif notificacion.estado.value == "aprobada":
            # ASESORIA APROBADA - Notificar a ambos
            print(f"\nTipo de notificacion: {notificacion.tipo_notificacion.value}")
            print(f"Telefono usuario: {notificacion.telefono_usuario or 'NO PROPORCIONADO'}")
            
            # Email al usuario
            if notificacion.tipo_notificacion.value in ["email", "ambos"]:
                print("ENVIANDO - Email al USUARIO (aprobada)")
                email_service.enviar_email(
                    destinatario=notificacion.email_usuario,
                    asunto="Tu asesoria ha sido aprobada",
                    mensaje=f"Buenas noticias! Tu asesoria con {notificacion.nombre_programador} fue aprobada.",
                    tipo="asesoria_aprobada",
                    datos=datos
                )
            
            # Email al programador
            print("ENVIANDO - Email al PROGRAMADOR (confirmacion de agenda)")
            email_service.enviar_email(
                destinatario=notificacion.email_programador,
                asunto=f"Asesoria confirmada con {notificacion.nombre_usuario}",
                mensaje=f"Has aprobado la asesoria con {notificacion.nombre_usuario}. Recuerda estar disponible en la fecha acordada.",
                tipo="asesoria_aprobada",
                datos=datos
            )
            
            # WhatsApp al usuario
            if notificacion.tipo_notificacion.value in ["whatsapp", "ambos"]:
                if notificacion.telefono_usuario:
                    print("ENVIANDO - WhatsApp al USUARIO (confirmacion)")
                    mensaje_wa = f"Tu asesoria fue aprobada!\nFecha: {notificacion.fecha_asesoria} a las {notificacion.hora_asesoria}\nCon: {notificacion.nombre_programador}"
                    whatsapp_service.enviar_mensaje(
                        numero=notificacion.telefono_usuario,
                        mensaje=mensaje_wa
                    )
                else:
                    print(f"Aviso: WhatsApp solicitado pero telefono_usuario no proporcionado")
        
        elif notificacion.estado.value == "rechazada":
            # ASESORIA RECHAZADA - Notificar a ambos
            print(f"\nTipo de notificacion: {notificacion.tipo_notificacion.value}")
            
            # Email al usuario
            if notificacion.tipo_notificacion.value in ["email", "ambos"]:
                print("ENVIANDO - Email al USUARIO (rechazada)")
                email_service.enviar_email(
                    destinatario=notificacion.email_usuario,
                    asunto="Actualizacion de tu solicitud de asesoria",
                    mensaje=f"Tu solicitud de asesoria con {notificacion.nombre_programador} no fue aprobada.",
                    tipo="asesoria_rechazada",
                    datos=datos
                )
            
            # Email al programador
            print("ENVIANDO - Email al PROGRAMADOR (confirmacion de rechazo)")
            email_service.enviar_email(
                destinatario=notificacion.email_programador,
                asunto=f"Has rechazado la asesoria de {notificacion.nombre_usuario}",
                mensaje=f"Has rechazado la solicitud de asesoria de {notificacion.nombre_usuario}.",
                tipo="generico",
                datos=datos
            )
            
            # WhatsApp al usuario
            if notificacion.tipo_notificacion.value in ["whatsapp", "ambos"]:
                if notificacion.telefono_usuario:
                    print("ENVIANDO - WhatsApp al USUARIO (rechazada)")
                    mensaje_wa = f"Tu solicitud de asesoria fue rechazada.\nProgramador: {notificacion.nombre_programador}\nMotivo: {notificacion.mensaje_respuesta or 'No especificado'}"
                    whatsapp_service.enviar_mensaje(
                        numero=notificacion.telefono_usuario,
                        mensaje=mensaje_wa
                    )
        
        elif notificacion.estado.value == "cancelada":
            # ASESORIA CANCELADA - Notificar a ambos
            print(f"\nTipo de notificacion: {notificacion.tipo_notificacion.value}")
            
            # Email al usuario
            if notificacion.tipo_notificacion.value in ["email", "ambos"]:
                print("ENVIANDO - Email al USUARIO (cancelada)")
                email_service.enviar_email(
                    destinatario=notificacion.email_usuario,
                    asunto="Asesoria cancelada",
                    mensaje=f"La asesoria con {notificacion.nombre_programador} ha sido cancelada.",
                    tipo="asesoria_rechazada",
                    datos=datos
                )
            
            # Email al programador
            print("ENVIANDO - Email al PROGRAMADOR (cancelada)")
            email_service.enviar_email(
                destinatario=notificacion.email_programador,
                asunto=f"Asesoria cancelada con {notificacion.nombre_usuario}",
                mensaje=f"La asesoria con {notificacion.nombre_usuario} ha sido cancelada.",
                tipo="asesoria_rechazada",
                datos=datos
            )
            
            # WhatsApp al usuario
            if notificacion.tipo_notificacion.value in ["whatsapp", "ambos"]:
                if notificacion.telefono_usuario:
                    print("ENVIANDO - WhatsApp al USUARIO (cancelada)")
                    mensaje_wa = f"Tu asesoria ha sido cancelada.\nEra para: {notificacion.fecha_asesoria} a las {notificacion.hora_asesoria}\nCon: {notificacion.nombre_programador}"
                    whatsapp_service.enviar_mensaje(
                        numero=notificacion.telefono_usuario,
                        mensaje=mensaje_wa
                    )
        
        print(f"\nNOTIFICACIONES COMPLETADAS\n{'='*70}\n")
        
        return RespuestaExito(
            mensaje=f"Notificaciones de asesoria enviadas ({notificacion.estado.value})",
            datos={"id_asesoria": notificacion.id_asesoria}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al notificar asesoria: {str(e)}")


@router.post("/recordatorio", response_model=RespuestaExito)
async def programar_recordatorio(recordatorio: RecordatorioRequest):
    """
    Endpoint para programar un recordatorio automatico.
    El recordatorio se enviara antes de la asesoria.
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
    Endpoint para obtener la lista de recordatorios programados.
    """
    try:
        recordatorios = scheduler_service.obtener_jobs_pendientes()
        return {
            "total": len(recordatorios),
            "recordatorios": recordatorios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener recordatorios: {str(e)}")