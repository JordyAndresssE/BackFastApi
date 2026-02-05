"""
Capa de Negocio - Servicio de WhatsApp
Proyecto: Sistema de Portafolio de Programadores
Este servicio se encarga del envio de mensajes por WhatsApp usando Twilio
Autor: Estudiante
Fecha: 2026
"""
from twilio.rest import Client
from ..config import settings
from typing import Dict


class WhatsAppService:
    """
    Servicio para enviar mensajes por WhatsApp.
    Utiliza la API de Twilio para el envio de mensajes.
    """
    
    def __init__(self):
        """Constructor del servicio de WhatsApp"""
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_whatsapp_from
        
        # Mostrar estado de configuracion
        print("\n" + "="*60)
        print("WhatsApp Service configurado (Twilio):")
        print(f"   From Number: {self.from_number}")
        print(f"   Account SID: {'Configurado' if self.account_sid else 'NO CONFIGURADO'}")
        print(f"   Auth Token: {'Configurado' if self.auth_token else 'NO CONFIGURADO'}")
        
        # Inicializar cliente Twilio si hay credenciales
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            print(f"   Estado: ACTIVO")
        else:
            self.client = None
            print(f"   Estado: SIMULADO (faltan credenciales)")
            print("\n   Para activar WhatsApp, configura en Railway:")
            print("   TWILIO_ACCOUNT_SID=ACxxxxxxxxxx")
            print("   TWILIO_AUTH_TOKEN=xxxxxxxxxx")
            print("   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886")
        
        print("="*60 + "\n")
    
    def enviar_mensaje(self, numero: str, mensaje: str) -> Dict:
        """
        Metodo para enviar un mensaje por WhatsApp.
        
        Parametros:
            numero: Numero de telefono en formato +593999999999
            mensaje: Texto del mensaje a enviar
            
        Retorna:
            Dict: Resultado del envio con status y datos adicionales
        """
        # Si no hay cliente configurado, simular envio
        if not self.client:
            print(f"WhatsApp no disponible (modo simulacion)")
            print(f"   Numero destino: {numero}")
            print(f"   Mensaje: {mensaje[:50]}...")
            return {
                "status": "simulated",
                "mensaje": "WhatsApp no configurado, simulando envio",
                "numero": numero
            }
        
        try:
            # Asegurar formato whatsapp:
            if not numero.startswith("whatsapp:"):
                numero = f"whatsapp:{numero}"
            
            print(f"Enviando WhatsApp...")
            print(f"   De: {self.from_number}")
            print(f"   Para: {numero}")
            print(f"   Mensaje: {mensaje[:80]}...")
            
            # Enviar mensaje usando el cliente de Twilio
            message = self.client.messages.create(
                from_=self.from_number,
                body=mensaje,
                to=numero
            )
            
            print(f"WhatsApp enviado exitosamente")
            print(f"   Message SID: {message.sid}")
            print(f"   Status: {message.status}")
            
            return {
                "status": "sent",
                "sid": message.sid,
                "numero": numero,
                "mensaje": mensaje
            }
            
        except Exception as e:
            print(f"Error al enviar WhatsApp:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e),
                "numero": numero
            }