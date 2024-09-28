import logging
import re

from flask import request, jsonify
from collections import defaultdict, deque

from routes import app

logger = logging.getLogger(__name__)

# Define the POST endpoint
@app.route('/lab_work', methods=['POST'])
def lab_work():
    try:
        res = {
            "username": "theslothspy",
            "password": "JOwi905$%"
        }
        return jsonify(res) 

    except Exception as e:
        return jsonify({"error": str(e)}), 400
