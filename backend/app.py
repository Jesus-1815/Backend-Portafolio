@app.route("/send-email", methods=["POST","OPTIONS"])
def send_email():

    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    try:
        data = request.json

        name = data["name"]
        email = data["email"]
        subject = data["subject"]
        message = data["message"]

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

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})