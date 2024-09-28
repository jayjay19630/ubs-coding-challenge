from flask import send_file
from routes import app

@app.route('/payload_crackme')
def get_crackme_payload():
    return send_file('payload_crackme')