"""
Servicio de Recordatorios Programados
Usa APScheduler para enviar recordatorios antes de asesorías
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import List, Dict
from .email_service import EmailService


class SchedulerService:
    """Servicio para programar recordatorios automáticos"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.email_service = EmailService()
        print("✅ Scheduler iniciado")
    
    def programar_recordatorio(
        self,
        id_asesoria: str,
        fecha_hora: datetime,
        email_programador: str,
        email_usuario: str,
        minutos_antes: int = 30
    ) -> str:
        """
        Programar recordatorio automático
        
        Args:
            id_asesoria: ID de la asesoría
            fecha_hora: Fecha y hora de la asesoría
            email_programador: Email del programador
            email_usuario: Email del usuario
            minutos_antes: Minutos antes de enviar el recordatorio
            
        Returns:
            ID del job programado
        """
        # Calcular cuándo enviar el recordatorio
        momento_envio = fecha_hora - timedelta(minutes=minutos_antes)
        
        # Verificar que no sea en el pasado
        if momento_envio <= datetime.now():
            print("⚠️ El momento de envío está en el pasado, enviando ahora")
            momento_envio = datetime.now() + timedelta(seconds=10)
        
        # Crear job ID único
        job_id = f"recordatorio_{id_asesoria}_{datetime.now().timestamp()}"
        
        # Programar envío al programador
        self.scheduler.add_job(
            func=self._enviar_recordatorio,
            trigger=DateTrigger(run_date=momento_envio),
            args=[email_programador, id_asesoria, fecha_hora],
            id=f"{job_id}_programador",
            name=f"Recordatorio asesoría {id_asesoria} - Programador"
        )
        
        # Programar envío al usuario
        self.scheduler.add_job(
            func=self._enviar_recordatorio,
            trigger=DateTrigger(run_date=momento_envio),
            args=[email_usuario, id_asesoria, fecha_hora],
            id=f"{job_id}_usuario",
            name=f"Recordatorio asesoría {id_asesoria} - Usuario"
        )
        
        print(f"✅ Recordatorio programado: {id_asesoria} para {momento_envio}")
        return job_id
    
    def _enviar_recordatorio(self, email: str, id_asesoria: str, fecha_hora: datetime):
        """Enviar email de recordatorio"""
        try:
            datos = {
                "fecha": fecha_hora.strftime("%Y-%m-%d"),
                "hora": fecha_hora.strftime("%H:%M"),
                "id_asesoria": id_asesoria
            }
            
            self.email_service.enviar_email(
                destinatario=email,
                asunto="⏰ Recordatorio: Asesoría próxima",
                mensaje=f"Tu asesoría es hoy a las {datos['hora']}",
                tipo="recordatorio",
                datos=datos
            )
            
            print(f"✅ Recordatorio enviado a {email}")
            
        except Exception as e:
            print(f"❌ Error al enviar recordatorio: {str(e)}")
    
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
            print(f"✅ Recordatorio cancelado: {job_id}")
            return True
        except Exception as e:
            print(f"❌ Error al cancelar recordatorio: {str(e)}")
            return False
    
    def shutdown(self):
        """Detener el scheduler"""
        self.scheduler.shutdown()
        print("🛑 Scheduler detenido")