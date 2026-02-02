"""
Servicio de WhatsApp
Envío de mensajes usando Twilio API
"""
from twilio.rest import Client
from ..config import settings
from typing import Dict


class WhatsAppService:
    """Servicio para enviar mensajes por WhatsApp"""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_whatsapp_from
        
        # Inicializar cliente Twilio si hay credenciales
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("⚠️ Credenciales de Twilio no configuradas")
    
    def enviar_mensaje(self, numero: str, mensaje: str) -> Dict:
        """
        Enviar mensaje por WhatsApp
        
        Args:
            numero: Número en formato +593999999999
            mensaje: Texto del mensaje
            
        Returns:
            Dict con resultado del envío
        """
        if not self.client:
            print("⚠️ Servicio de WhatsApp no disponible (simulated)")
            return {
                "status": "simulated",
                "mensaje": "WhatsApp no configurado, simulando envío",
                "numero": numero
            }
        
        try:
            # Asegurar formato whatsapp:
            if not numero.startswith("whatsapp:"):
                numero = f"whatsapp:{numero}"
            
            # Enviar mensaje
            message = self.client.messages.create(
                from_=self.from_number,
                body=mensaje,
                to=numero
            )
            
            print(f"✅ WhatsApp enviado a {numero}: {message.sid}")
            
            return {
                "status": "sent",
                "sid": message.sid,
                "numero": numero,
                "mensaje": mensaje
            }
            
        except Exception as e:
            print(f"❌ Error al enviar WhatsApp: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "numero": numero
            }