# 📧 Configuración de Gmail SMTP (100% GRATIS)

Esta guía te ayudará a configurar Gmail para enviar emails desde el backend.

## ⚡ Resumen rápido

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # ← Contraseña de aplicación
EMAIL_FROM=tu_email@gmail.com
```

---

## 🔐 Paso 1: Activar Verificación en 2 Pasos

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. Click en **Seguridad** (menú izquierdo)
3. Busca **Verificación en 2 pasos**
4. Actívala si no está activa (sigue los pasos de Google)

> ⚠️ **IMPORTANTE:** Sin verificación en 2 pasos, NO podrás generar contraseñas de aplicación.

---

## 🔑 Paso 2: Generar Contraseña de Aplicación

1. Ve a: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

2. Selecciona:
   - **App:** Correo
   - **Dispositivo:** Otro (nombre personalizado)
   - Escribe: `Portafolio Devs Backend`

3. Click en **Generar**

4. Google te dará una contraseña de 16 caracteres como:
   ```
   abcd efgh ijkl mnop
   ```

5. **¡COPIA ESTA CONTRASEÑA!** Solo se muestra una vez.

---

## ⚙️ Paso 3: Configurar .env

Abre tu archivo `.env` y configura:

```env
# ===== EMAIL (GMAIL SMTP) =====
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email_real@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=tu_email_real@gmail.com
EMAIL_FROM_NAME=Portafolio Devs
```

> 💡 **Tip:** Los espacios en la contraseña son opcionales, pero ayudan a leerla.

---

## ✅ Paso 4: Verificar que funciona

Reinicia el servidor y deberías ver:

```
============================================================
📧 Email Service configurado (SMTP Gmail):
   Server: smtp.gmail.com:587
   Username: tu_email@gmail.com
   From: tu_email@gmail.com
   SMTP habilitado: ✅
============================================================
```

---

## 🧪 Paso 5: Probar envío

Usa este comando para probar:

```bash
curl -X POST "http://localhost:8000/api/notificaciones/email" ^
  -H "Content-Type: application/json" ^
  -d "{\"destinatario\": \"tu_otro_email@gmail.com\", \"asunto\": \"Test Gmail SMTP\", \"mensaje\": \"Hola! Este es un email de prueba.\", \"tipo_notificacion\": \"generico\"}"
```

O desde PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/notificaciones/email" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"destinatario": "tu_otro_email@gmail.com", "asunto": "Test", "mensaje": "Prueba de email"}'
```

---

## 🚨 Solución de Problemas

### Error: "Username and Password not accepted"

**Causa:** Estás usando tu contraseña normal de Gmail.

**Solución:** 
1. Genera una **Contraseña de Aplicación** (Paso 2)
2. Usa ESA contraseña en `SMTP_PASSWORD`

---

### Error: "Less secure app access"

**Causa:** Tienes que usar contraseñas de aplicación, no contraseñas normales.

**Solución:** 
1. Activa verificación en 2 pasos
2. Genera contraseña de aplicación

---

### Los emails llegan a Spam

**Soluciones:**
1. Agrega tu email a contactos del destinatario
2. Evita palabras spam en el asunto ("gratis", "urgente", etc.)
3. A largo plazo: configura SPF/DKIM en un dominio propio

---

### No puedo acceder a App Passwords

**Causa:** La verificación en 2 pasos no está activa.

**Solución:** Activa primero la verificación en 2 pasos en tu cuenta Google.

---

## 📊 Límites de Gmail SMTP

| Límite | Cantidad |
|--------|----------|
| Emails por día | 500 (cuenta personal) |
| Emails por día | 2,000 (Google Workspace) |
| Destinatarios por email | 100 |

> 💡 500 emails/día es más que suficiente para desarrollo y apps pequeñas.

---

## 🔒 Seguridad

- **NUNCA** compartas tu contraseña de aplicación
- **NUNCA** subas `.env` a GitHub (ya está en `.gitignore`)
- Si sospechas que se filtró, revoca la contraseña en [App Passwords](https://myaccount.google.com/apppasswords)

---

## 🎯 Flujo de emails en el sistema

| Evento | Destinatario | Tipo de Email |
|--------|--------------|---------------|
| Nueva asesoría | Programador | `nueva_asesoria` |
| Asesoría aprobada | Usuario | `asesoria_aprobada` |
| Asesoría rechazada | Usuario | `asesoria_rechazada` |
| Recordatorio | Ambos | `recordatorio` |

---

## ✨ ¡Listo!

Ya puedes enviar emails gratis desde tu backend. 🚀
