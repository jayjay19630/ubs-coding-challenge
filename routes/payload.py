from flask import send_file
from routes import app

@app.route('/payload_crackme')
def get_crackme_payload():
    return send_file('payload_crackme')

@app.route('/payload_stack')
def get_stack_payload():
    return send_file('payload_stack')

@app.route('/payload_shellcode')
def get_shellcode_payload():
    return send_file('payload_shellcode')