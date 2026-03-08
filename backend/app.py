from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# ✅ CORS DEBE ESTAR AQUÍ, antes de las rutas
CORS(app, resources={
    r"/send-email": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

@app.route("/")
def home():
    return "Backend funcionando"

@app.route("/send-email", methods=["POST", "OPTIONS"])
def send_email():
    # ✅ Manejo explícito de preflight
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        name = data.get("name", "")
        email = data.get("email", "")
        subject = data.get("subject", "")
        message = data.get("message", "")

        # Validación
        if not all([name, email, subject, message]):
            return jsonify({"success": False, "error": "Faltan campos"}), 400

        body = f"""
Nombre: {name}
Email: {email}

Mensaje:
{message}
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        server.quit()

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)