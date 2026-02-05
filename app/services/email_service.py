"""
Servicio de Email
Envío de correos con templates HTML usando SMTP (Gmail)
100% GRATIS - Sin límites
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings
from typing import Optional, Dict


class EmailService:
    """Servicio para enviar emails usando SMTP (Gmail)"""
    
    def __init__(self):
        # Configuración SMTP
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name
        
        # Verificar configuración
        self.smtp_enabled = bool(
            self.smtp_server and 
            self.smtp_username and 
            self.smtp_password
        )
        
        # Log de configuración
        print("\n" + "="*60)
        print("📧 Email Service configurado (SMTP Gmail):")
        print(f"   Server: {self.smtp_server}:{self.smtp_port}")
        print(f"   Username: {self.smtp_username}")
        print(f"   From: {self.from_email}")
        print(f"   SMTP habilitado: {'✅' if self.smtp_enabled else '❌'}")
        
        if not self.smtp_enabled:
            print("\n   ⚠️ SMTP no configurado correctamente.")
            print("   → Configura estas variables en .env:")
            print("      SMTP_SERVER=smtp.gmail.com")
            print("      SMTP_PORT=587")
            print("      SMTP_USERNAME=tu_email@gmail.com")
            print("      SMTP_PASSWORD=tu_contraseña_de_aplicacion")
        
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
        Enviar email con template HTML usando SMTP
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            mensaje: Mensaje principal
            tipo: Tipo de notificación (nueva_asesoria, aprobada, rechazada, recordatorio)
            datos: Datos adicionales para el template
        """
        print(f"\n📧 Iniciando envío de email...")
        print(f"   → Destinatario: {destinatario}")
        print(f"   → Asunto: {asunto}")
        print(f"   → Tipo: {tipo}")
        
        # Validar configuración
        if not self.smtp_enabled:
            print("❌ ERROR: SMTP no está configurado")
            print("   → Configura SMTP_USERNAME y SMTP_PASSWORD en .env")
            return False
        
        try:
            # Generar HTML
            print(f"📝 Generando HTML del email...")
            html_content = self._generar_html(tipo, mensaje, datos or {})
            
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = asunto
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = destinatario
            
            # Agregar contenido HTML
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            # Enviar via SMTP
            print(f"📤 Conectando a {self.smtp_server}:{self.smtp_port}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Seguridad TLS
                print(f"🔐 Autenticando...")
                server.login(self.smtp_username, self.smtp_password)
                print(f"📨 Enviando email...")
                server.sendmail(self.from_email, destinatario, msg.as_string())
            
            print(f"✅ Email enviado exitosamente a {destinatario}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ ERROR de autenticación SMTP:")
            print(f"   → {str(e)}")
            print("\n💡 SOLUCIÓN:")
            print("   1. Activa 'Verificación en 2 pasos' en tu cuenta Google")
            print("   2. Genera una 'Contraseña de aplicación':")
            print("      → https://myaccount.google.com/apppasswords")
            print("   3. Usa esa contraseña en SMTP_PASSWORD")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ ERROR SMTP: {str(e)}")
            return False
            
        except Exception as e:
            print(f"❌ ERROR al enviar email:")
            print(f"   → Tipo: {type(e).__name__}")
            print(f"   → Mensaje: {str(e)}")
            
            import traceback
            print(f"   → Traceback:\n{traceback.format_exc()}")
            return False
    
    def _generar_html(self, tipo: str, mensaje: str, datos: Dict) -> str:
        """Generar HTML según tipo de notificación"""
        
        # Template base profesional
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
                .emoji {{
                    font-size: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Portafolio Devs</h1>
                </div>
                <div class="content">
                    {contenido}
                </div>
                <div class="footer">
                    <p>Este es un email automático, por favor no responder.</p>
                    <p>© 2026 Portafolio Devs. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        frontend_url = settings.frontend_url
        
        # Contenido según tipo
        if tipo == "nueva_asesoria":
            contenido = f"""
                <h2>📅 Nueva Solicitud de Asesoría</h2>
                <p>Hola <strong>{datos.get('nombre_programador', 'Programador')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>📌 Detalles de la solicitud:</strong></p>
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
                <h2>✅ ¡Asesoría Aprobada!</h2>
                <p>Hola <strong>{datos.get('nombre_usuario', 'Usuario')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>📌 Detalles de tu asesoría:</strong></p>
                    <ul>
                        <li><strong>Programador:</strong> {datos.get('nombre_programador', 'Programador')}</li>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'No especificada')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'No especificada')}</li>
                    </ul>
                    <p><strong>💬 Mensaje del programador:</strong></p>
                    <p><em>{datos.get('mensaje_respuesta', 'Sin mensaje adicional')}</em></p>
                </div>
                
                <p>¡Nos vemos pronto! 🎉</p>
            """
        
        elif tipo == "asesoria_rechazada":
            contenido = f"""
                <h2>❌ Solicitud No Aprobada</h2>
                <p>Hola <strong>{datos.get('nombre_usuario', 'Usuario')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>💬 Razón:</strong></p>
                    <p><em>{datos.get('mensaje_respuesta', 'El programador no está disponible en ese horario')}</em></p>
                </div>
                
                <p>Puedes intentar agendar en otro horario.</p>
                <a href="{frontend_url}" class="button">Ver Programadores</a>
            """
        
        elif tipo == "recordatorio":
            contenido = f"""
                <h2>⏰ Recordatorio de Asesoría</h2>
                <p>Hola,</p>
                <p>Te recordamos que tienes una asesoría próxima:</p>
                
                <div class="info-box">
                    <p><strong>📌 Detalles:</strong></p>
                    <ul>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'Hoy')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'Pronto')}</li>
                        <li><strong>Con:</strong> {datos.get('nombre_programador', 'Programador')}</li>
                    </ul>
                </div>
                
                <p>¡No olvides conectarte a tiempo! 🚀</p>
            """
        
        else:  # generico
            contenido = f"""
                <h2>📬 Notificación</h2>
                <p>{mensaje}</p>
            """
        
        return base_template.format(contenido=contenido)


# Instancia global (singleton)
email_service = EmailService()