"""
Capa de Negocio - Servicio de Recordatorios
Proyecto: Sistema de Portafolio de Programadores
Este servicio programa recordatorios automaticos usando APScheduler
Autor: Estudiante
Fecha: 2026
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import List, Dict
from .email_service import EmailService


class SchedulerService:
    """
    Servicio para programar recordatorios automaticos.
    Utiliza APScheduler para programar tareas en segundo plano.
    """
    
    def __init__(self):
        """Constructor del servicio de recordatorios"""
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.email_service = EmailService()
        print("Scheduler iniciado")
    
    def programar_recordatorio(
        self,
        id_asesoria: str,
        fecha_hora: datetime,
        email_programador: str,
        email_usuario: str,
        minutos_antes: int = 30
    ) -> str:
        """
        Metodo para programar un recordatorio automatico.
        
        Parametros:
            id_asesoria: ID de la asesoria
            fecha_hora: Fecha y hora de la asesoria
            email_programador: Email del programador
            email_usuario: Email del usuario
            minutos_antes: Minutos antes de enviar el recordatorio
            
        Retorna:
            str: ID del job programado
        """
        # Calcular cuando enviar el recordatorio
        momento_envio = fecha_hora - timedelta(minutes=minutos_antes)
        
        # Verificar que no sea en el pasado
        if momento_envio <= datetime.now():
            print("Aviso: El momento de envio esta en el pasado, enviando ahora")
            momento_envio = datetime.now() + timedelta(seconds=10)
        
        # Crear job ID unico
        job_id = f"recordatorio_{id_asesoria}_{datetime.now().timestamp()}"
        
        # Programar envio al programador
        self.scheduler.add_job(
            func=self._enviar_recordatorio,
            trigger=DateTrigger(run_date=momento_envio),
            args=[email_programador, id_asesoria, fecha_hora],
            id=f"{job_id}_programador",
            name=f"Recordatorio asesoria {id_asesoria} - Programador"
        )
        
        # Programar envio al usuario
        self.scheduler.add_job(
            func=self._enviar_recordatorio,
            trigger=DateTrigger(run_date=momento_envio),
            args=[email_usuario, id_asesoria, fecha_hora],
            id=f"{job_id}_usuario",
            name=f"Recordatorio asesoria {id_asesoria} - Usuario"
        )
        
        print(f"Recordatorio programado: {id_asesoria} para {momento_envio}")
        return job_id
    
    def _enviar_recordatorio(self, email: str, id_asesoria: str, fecha_hora: datetime):
        """Metodo privado para enviar el email de recordatorio"""
        try:
            datos = {
                "fecha": fecha_hora.strftime("%Y-%m-%d"),
                "hora": fecha_hora.strftime("%H:%M"),
                "id_asesoria": id_asesoria
            }
            
            self.email_service.enviar_email(
                destinatario=email,
                asunto="Recordatorio: Asesoria proxima",
                mensaje=f"Tu asesoria es hoy a las {datos['hora']}",
                tipo="recordatorio",
                datos=datos
            )
            
            print(f"Recordatorio enviado a {email}")
            
        except Exception as e:
            print(f"Error al enviar recordatorio: {str(e)}")
    
    def obtener_jobs_pendientes(self) -> List[Dict]:
        """Obtener lista de recordatorios programados"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "nombre": job.name,
                "proxima_ejecucion": str(job.next_run_time)
            }
            for job in jobs
        ]
    
    def cancelar_recordatorio(self, job_id: str) -> bool:
        """Cancelar un recordatorio programado"""
        try:
            self.scheduler.remove_job(job_id)
            print(f"Recordatorio cancelado: {job_id}")
            return True
        except Exception as e:
            print(f"Error al cancelar recordatorio: {str(e)}")
            return False
    
    def shutdown(self):
        """Detener el scheduler"""
        self.scheduler.shutdown()
        print("Scheduler detenido")