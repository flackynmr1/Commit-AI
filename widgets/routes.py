from flask import jsonify
from . import widgets


@widgets.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "message": "Widgets module running"
    })


@widgets.route('/embed/<customer_id>', methods=['GET'])
def embed(customer_id):
    return jsonify({
        "customer_id": customer_id,
        "widget": "placeholder"
    })