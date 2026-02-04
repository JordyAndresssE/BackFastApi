"""
Servicio de Email
Envío de correos con templates HTML usando Resend
"""
import resend
from jinja2 import Template
from ..config import settings
from typing import Optional, Dict


class EmailService:
    """Servicio para enviar emails usando Resend API"""
    
    def __init__(self):
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name
        
        # Configurar Resend API
        if settings.resend_api_key:
            resend.api_key = settings.resend_api_key
            self.resend_enabled = True
        else:
            self.resend_enabled = False
        
        # Log de configuración al inicializar
        print("\n" + "="*60)
        print("📧 Email Service configurado (Resend):")
        print(f"   From: {self.from_email}")
        print(f"   From Name: {self.from_name}")
        print(f"   Resend API configurada: {'✅' if self.resend_enabled else '❌'}")
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
        Enviar email con template HTML usando Resend
        
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
        if not self.resend_enabled:
            print("❌ ERROR: RESEND_API_KEY no configurada")
            print("   → Agrega esta variable en Railway:")
            print(f"      RESEND_API_KEY=re_xxxxxxxxxx")
            return False
        
        try:
            print(f"📝 Generando HTML del email...")
            # Generar HTML según tipo
            html_content = self._generar_html(tipo, mensaje, datos or {})
            print(f"✅ HTML generado correctamente")
            
            # Enviar email con Resend
            print(f"📤 Enviando email via Resend API...")
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [destinatario],
                "subject": asunto,
                "html": html_content,
            }
            
            response = resend.Emails.send(params)
            
            print(f"✅ Email enviado exitosamente a {destinatario}")
            print(f"   → Resend ID: {response.get('id', 'N/A')}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR al enviar email con Resend:")
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