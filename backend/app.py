from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# ✅ CONFIGURAR CORS CORRECTAMENTE (debe ser antes de las rutas)
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"],
     supports_credentials=False,
     max_age=3600)

# Variables de entorno
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend funcionando correctamente"}), 200

@app.route("/send-email", methods=["POST", "OPTIONS"])
def send_email():
    """Endpoint para enviar emails desde el formulario de contacto"""
    
    # ✅ Manejo explícito de preflight CORS
    if request.method == "OPTIONS":
        return "", 204

    try:
        # Obtener datos JSON
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False, 
                "error": "No se recibieron datos"
            }), 400

        # Extraer datos con validación
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        # Validar que todos los campos estén presentes
        if not all([name, email, subject, message]):
            return jsonify({
                "success": False, 
                "error": "Faltan campos requeridos (name, email, subject, message)"
            }), 400

        # Validar email básico
        if "@" not in email:
            return jsonify({
                "success": False, 
                "error": "Email inválido"
            }), 400

        # Verificar que las credenciales estén configuradas
        if not EMAIL_USER or not EMAIL_PASS:
            return jsonify({
                "success": False, 
                "error": "Credenciales de email no configuradas en el servidor"
            }), 500

        # Construir el cuerpo del email
        body = f"""
Nombre: {name}
Email de contacto: {email}

Asunto: {subject}

Mensaje:
{message}
"""

        # Crear mensaje
        msg = MIMEText(body)
        msg["Subject"] = f"[Contacto Web] {subject}"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER
        msg["Reply-To"] = email

        # Enviar email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        server.quit()

        print(f"✅ Email enviado desde: {email}")
        return jsonify({"success": True, "message": "Email enviado correctamente"}), 200

    except smtplib.SMTPAuthenticationError:
        print("❌ Error de autenticación SMTP")
        return jsonify({
            "success": False, 
            "error": "Error de autenticación con el servidor de email"
        }), 500
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {str(e)}")
        return jsonify({
            "success": False, 
            "error": f"Error al enviar email: {str(e)}"
        }), 500
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return jsonify({
            "success": False, 
            "error": f"Error inesperado: {str(e)}"
        }), 500

# Manejador de errores 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

# Manejador de errores 405
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método no permitido"}), 405

if __name__ == "__main__":
    # Para desarrollo local
    app.run(debug=False, host="0.0.0.0", port=5000)