"""
Capa de Negocio - Servicio de Correo Electronico
Proyecto: Sistema de Portafolio de Programadores
Este servicio se encarga del envio de correos usando la API de Brevo
Autor: Estudiante
Fecha: 2026
"""
import httpx
from ..config import settings
from typing import Optional, Dict


class EmailService:
    """
    Servicio para enviar correos electronicos.
    Utiliza la API de Brevo para el envio de emails con plantillas HTML.
    """
    
    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
    
    def __init__(self):
        """Constructor del servicio de email"""
        self.api_key = settings.brevo_api_key
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name
        
        # Verificar si la API esta configurada
        self.brevo_enabled = bool(self.api_key)
        
        # Mostrar estado de configuracion
        print("\n" + "="*60)
        print("Email Service configurado (Brevo API):")
        print(f"   From: {self.from_name} <{self.from_email}>")
        print(f"   API Key: {'Configurada' if self.api_key else 'NO CONFIGURADA'}")
        print(f"   Estado: {'ACTIVO' if self.brevo_enabled else 'INACTIVO'}")
        
        if not self.brevo_enabled:
            print("\n   Aviso: Brevo no configurado.")
            print("   Configura BREVO_API_KEY en el archivo .env")
        
        print("="*60 + "\n")
    
    def enviar_email(
        self,
        destinatario: str,
        asunto: str,
        mensaje: str,
        tipo: str = "generico",
        datos: Optional[Dict] = None
    ) -> bool:
        """
        Metodo para enviar un correo electronico.
        
        Parametros:
            destinatario: Email del destinatario
            asunto: Asunto del correo
            mensaje: Mensaje principal del correo
            tipo: Tipo de notificacion (nueva_asesoria, aprobada, rechazada, recordatorio)
            datos: Datos adicionales para la plantilla
            
        Retorna:
            bool: True si el envio fue exitoso, False en caso contrario
        """
        print(f"\nIniciando envio de email...")
        print(f"   Destinatario: {destinatario}")
        print(f"   Asunto: {asunto}")
        print(f"   Tipo: {tipo}")
        
        # Validar que el servicio este configurado
        if not self.brevo_enabled:
            print("ERROR: Brevo API no esta configurada")
            print("   Configura BREVO_API_KEY en .env o Railway")
            return False
        
        try:
            # Generar contenido HTML
            print(f"Generando HTML del email...")
            html_content = self._generar_html(tipo, mensaje, datos or {})
            
            # Preparar datos para la API de Brevo
            payload = {
                "sender": {
                    "name": self.from_name,
                    "email": self.from_email
                },
                "to": [
                    {"email": destinatario}
                ],
                "subject": asunto,
                "htmlContent": html_content
            }
            
            # Configurar headers con la API Key
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.api_key
            }
            
            # Realizar peticion HTTP a la API
            print(f"Enviando email via Brevo API...")
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.BREVO_API_URL,
                    json=payload,
                    headers=headers
                )
            
            # Verificar respuesta
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"Email enviado exitosamente a {destinatario}")
                print(f"   Message ID: {result.get('messageId', 'N/A')}")
                return True
            else:
                print(f"ERROR al enviar email:")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except httpx.TimeoutException:
            print("ERROR: Timeout al conectar con Brevo API")
            return False
            
        except Exception as e:
            print(f"ERROR al enviar email:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            return False
    
    def _generar_html(self, tipo: str, mensaje: str, datos: Dict) -> str:
        """
        Metodo privado para generar el contenido HTML del correo.
        
        Parametros:
            tipo: Tipo de notificacion
            mensaje: Mensaje principal
            datos: Datos adicionales para la plantilla
            
        Retorna:
            str: Contenido HTML del correo
        """
        
        # Plantilla base HTML
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #A10000 0%, #7B0000 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px;
                    color: #333333;
                    line-height: 1.6;
                }}
                .info-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #A10000;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .info-box ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .info-box li {{
                    margin: 8px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 35px;
                    background: linear-gradient(135deg, #A10000 0%, #7B0000 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666666;
                    font-size: 12px;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Portafolio Devs</h1>
                </div>
                <div class="content">
                    {contenido}
                </div>
                <div class="footer">
                    <p>Este es un email automatico, por favor no responder.</p>
                    <p>2026 Portafolio Devs. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        frontend_url = settings.frontend_url
        
        # Generar contenido segun el tipo de notificacion
        if tipo == "nueva_asesoria":
            contenido = f"""
                <h2>Nueva Solicitud de Asesoria</h2>
                <p>Hola <strong>{datos.get('nombre_programador', 'Programador')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>Detalles de la solicitud:</strong></p>
                    <ul>
                        <li><strong>Solicitante:</strong> {datos.get('nombre_usuario', 'Usuario')}</li>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'No especificada')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'No especificada')}</li>
                        <li><strong>Motivo:</strong> {datos.get('motivo', 'No especificado')}</li>
                    </ul>
                </div>
                
                <p>Ingresa a tu panel para aprobar o rechazar esta solicitud.</p>
                <a href="{frontend_url}/programador" class="button">Ver Panel</a>
            """
        
        elif tipo == "asesoria_aprobada":
            contenido = f"""
                <h2>Asesoria Aprobada</h2>
                <p>Hola <strong>{datos.get('nombre_usuario', 'Usuario')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>Detalles de tu asesoria:</strong></p>
                    <ul>
                        <li><strong>Programador:</strong> {datos.get('nombre_programador', 'Programador')}</li>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'No especificada')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'No especificada')}</li>
                    </ul>
                    <p><strong>Mensaje del programador:</strong></p>
                    <p><em>{datos.get('mensaje_respuesta', 'Sin mensaje adicional')}</em></p>
                </div>
                
                <p>Nos vemos pronto!</p>
            """
        
        elif tipo == "asesoria_rechazada":
            contenido = f"""
                <h2>Solicitud No Aprobada</h2>
                <p>Hola <strong>{datos.get('nombre_usuario', 'Usuario')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>Razon:</strong></p>
                    <p><em>{datos.get('mensaje_respuesta', 'El programador no esta disponible en ese horario')}</em></p>
                </div>
                
                <p>Puedes intentar agendar en otro horario.</p>
                <a href="{frontend_url}" class="button">Ver Programadores</a>
            """
        
        elif tipo == "recordatorio":
            contenido = f"""
                <h2>Recordatorio de Asesoria</h2>
                <p>Hola,</p>
                <p>Te recordamos que tienes una asesoria proxima:</p>
                
                <div class="info-box">
                    <p><strong>Detalles:</strong></p>
                    <ul>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'Hoy')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'Pronto')}</li>
                        <li><strong>Con:</strong> {datos.get('nombre_programador', 'Programador')}</li>
                    </ul>
                </div>
                
                <p>No olvides conectarte a tiempo!</p>
            """
        
        else:
            # Plantilla generica
            contenido = f"""
                <h2>Notificacion</h2>
                <p>{mensaje}</p>
            """
        
        return base_template.format(contenido=contenido)


# Instancia del servicio (Patron Singleton)
email_service = EmailService()