"""
Servicio de Email
Envío de correos con templates HTML
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from ..config import settings
from typing import Optional, Dict


class EmailService:
    """Servicio para enviar emails"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name
        
        # Log de configuración al inicializar
        print("\n" + "="*60)
        print("📧 Email Service configurado:")
        print(f"   Servidor: {self.smtp_server}:{self.smtp_port}")
        print(f"   Usuario: {self.username}")
        print(f"   From: {self.from_email}")
        print(f"   From Name: {self.from_name}")
        print(f"   Usuario configurado: {'✅' if self.username else '❌'}")
        print(f"   Password configurado: {'✅' if self.password else '❌'}")
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
        Enviar email con template HTML
        
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
        
        # Validar credenciales
        if not self.username or not self.password:
            print("❌ ERROR: SMTP_USERNAME o SMTP_PASSWORD no configurados")
            print("   → Agrega estas variables en Railway:")
            print(f"      SMTP_USERNAME={self.from_email}")
            print("      SMTP_PASSWORD=tu_password")
            return False
        
        try:
            print(f"📝 Generando HTML del email...")
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = asunto
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = destinatario
            
            # Generar HTML según tipo
            html_content = self._generar_html(tipo, mensaje, datos or {})
            
            # Adjuntar HTML
            part_html = MIMEText(html_content, "html")
            msg.attach(part_html)
            print(f"✅ HTML generado correctamente")
            
            # Enviar email
            print(f"🔌 Conectando a {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print(f"🔐 Iniciando TLS...")
                server.starttls()
                
                print(f"👤 Autenticando con usuario: {self.username}...")
                server.login(self.username, self.password)
                print(f"✅ Autenticación exitosa")
                
                print(f"📤 Enviando mensaje...")
                server.send_message(msg)
            
            print(f"✅ Email enviado exitosamente a {destinatario}\n")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ ERROR DE AUTENTICACIÓN SMTP:")
            print(f"   → Código: {e.smtp_code}")
            print(f"   → Mensaje: {e.smtp_error.decode() if hasattr(e, 'smtp_error') else str(e)}")
            print(f"   → Verifica la contraseña en Railway")
            print(f"   → Usuario: {self.username}")
            return False
            
        except smtplib.SMTPConnectError as e:
            print(f"❌ ERROR DE CONEXIÓN SMTP:")
            print(f"   → No se pudo conectar a {self.smtp_server}:{self.smtp_port}")
            print(f"   → Mensaje: {str(e)}")
            print(f"   → Verifica que el servidor SMTP sea correcto")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ ERROR SMTP:")
            print(f"   → {str(e)}")
            return False
            
        except Exception as e:
            print(f"❌ ERROR INESPERADO al enviar email:")
            print(f"   → Tipo: {type(e).__name__}")
            print(f"   → Mensaje: {str(e)}")
            import traceback
            print(f"   → Traceback:\n{traceback.format_exc()}")
            return False
    
    def _generar_html(self, tipo: str, mensaje: str, datos: Dict) -> str:
        """Generar HTML según tipo de notificación"""
        
        # Template base
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .header {
                    background-color: #A10000;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .content {
                    padding: 30px;
                    color: #333333;
                }
                .info-box {
                    background-color: #f8f9fa;
                    border-left: 4px solid #A10000;
                    padding: 15px;
                    margin: 20px 0;
                }
                .button {
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #A10000;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .footer {
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666666;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Portafolio Devs</h1>
                </div>
                <div class="content">
                    {{ contenido }}
                </div>
                <div class="footer">
                    <p>Este es un email automático, por favor no responder.</p>
                    <p>&copy; 2026 Portafolio Devs. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Contenido según tipo
        if tipo == "nueva_asesoria":
            contenido = f"""
                <h2>📅 Nueva Solicitud de Asesoría</h2>
                <p>Hola <strong>{datos.get('nombre_programador', 'Programador')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>📌 Detalles:</strong></p>
                    <ul>
                        <li><strong>Solicitante:</strong> {datos.get('nombre_usuario', 'Usuario')}</li>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'No especificada')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'No especificada')}</li>
                        <li><strong>Motivo:</strong> {datos.get('motivo', 'No especificado')}</li>
                    </ul>
                </div>
                
                <p>Ingresa a tu panel para aprobar o rechazar esta solicitud.</p>
                <a href="{settings.frontend_url}/programador" class="button">Ver Panel</a>
            """
        
        elif tipo == "asesoria_aprobada":
            contenido = f"""
                <h2>✅ Asesoría Aprobada</h2>
                <p>Hola <strong>{datos.get('nombre_usuario', 'Usuario')}</strong>,</p>
                <p>{mensaje}</p>
                
                <div class="info-box">
                    <p><strong>📌 Detalles:</strong></p>
                    <ul>
                        <li><strong>Programador:</strong> {datos.get('nombre_programador', 'Programador')}</li>
                        <li><strong>Fecha:</strong> {datos.get('fecha', 'No especificada')}</li>
                        <li><strong>Hora:</strong> {datos.get('hora', 'No especificada')}</li>
                    </ul>
                    <p><strong>Mensaje del programador:</strong></p>
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
                    <p><strong>Razón:</strong></p>
                    <p><em>{datos.get('mensaje_respuesta', 'El programador no está disponible en ese horario')}</em></p>
                </div>
                
                <p>Puedes intentar agendar en otro horario.</p>
                <a href="{settings.frontend_url}" class="button">Ver Programadores</a>
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
        
        # Renderizar template
        template = Template(base_template)
        return template.render(contenido=contenido)