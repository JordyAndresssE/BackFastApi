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
        
        # Log de configuración
        print("\n" + "="*60)
        print("📱 WhatsApp Service configurado (Twilio):")
        print(f"   From Number: {self.from_number}")
        print(f"   Account SID: {'✅ ' + self.account_sid[:20] + '...' if self.account_sid else '❌ NO CONFIGURADO'}")
        print(f"   Auth Token: {'✅ Configurado' if self.auth_token else '❌ NO CONFIGURADO'}")
        
        # Inicializar cliente Twilio si hay credenciales
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            print(f"   Estado: ✅ ACTIVO")
        else:
            self.client = None
            print(f"   Estado: ⚠️ SIMULADO (faltan credenciales)")
            print("\n💡 Para activar WhatsApp, agrega en Railway:")
            print("   TWILIO_ACCOUNT_SID=ACxxxxxxxxxx")
            print("   TWILIO_AUTH_TOKEN=xxxxxxxxxx")
            print("   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886")
        
        print("="*60 + "\n")
    
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
            print(f"⚠️ WhatsApp no disponible (modo simulación)")
            print(f"   → Número destino: {numero}")
            print(f"   → Mensaje: {mensaje[:50]}...")
            return {
                "status": "simulated",
                "mensaje": "WhatsApp no configurado, simulando envío",
                "numero": numero
            }
        
        try:
            # Asegurar formato whatsapp:
            if not numero.startswith("whatsapp:"):
                numero = f"whatsapp:{numero}"
            
            print(f"📱 Enviando WhatsApp...")
            print(f"   → De: {self.from_number}")
            print(f"   → Para: {numero}")
            print(f"   → Mensaje: {mensaje[:80]}...")
            
            # Enviar mensaje
            message = self.client.messages.create(
                from_=self.from_number,
                body=mensaje,
                to=numero
            )
            
            print(f"✅ WhatsApp enviado exitosamente")
            print(f"   → Message SID: {message.sid}")
            print(f"   → Status: {message.status}")
            
            return {
                "status": "sent",
                "sid": message.sid,
                "numero": numero,
                "mensaje": mensaje
            }
            
        except Exception as e:
            print(f"❌ Error al enviar WhatsApp:")
            print(f"   → Tipo: {type(e).__name__}")
            print(f"   → Mensaje: {str(e)}")
            
            # Sugerencias según el error
            if "20003" in str(e) or "authenticate" in str(e).lower():
                print("\n💡 SOLUCIÓN:")
                print("   → Verifica TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN")
            elif "21608" in str(e):
                print("\n💡 SOLUCIÓN:")
                print("   → El número no está registrado en Twilio Sandbox")
                print("   → Envía 'join <sandbox-word>' al +14155238886")
            
            return {
                "status": "error",
                "error": str(e),
                "numero": numero
            }