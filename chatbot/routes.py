from flask import request, jsonify
from . import chatbot
from models import Customer, Conversation, TrainingData, Usage, db
import json
from datetime import datetime


@chatbot.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Chatbot module is running'
    })


@chatbot.route('/message', methods=['POST'])
def message():
    data = request.get_json() or {}

    customer_id = data.get('customer_id')
    session_id = data.get('session_id', 'default')
    user_message = data.get('message', '')

    if not customer_id:
        return jsonify({'message': 'customer_id is required'}), 400

    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    training_items = TrainingData.query.filter_by(
        customer_id=customer_id
    ).all()

    bot_response = "Tack för ditt meddelande! Vi återkommer snart."

    for item in training_items:
        if item.intent.lower() in user_message.lower():
            bot_response = item.response
            break

    conversation = Conversation(
        customer_id=customer_id,
        session_id=session_id,
        messages=json.dumps([
            {'role': 'user', 'content': user_message},
            {'role': 'assistant', 'content': bot_response}
        ]),
        timestamp=datetime.utcnow()
    )

    db.session.add(conversation)

    usage = Usage(
        customer_id=customer_id,
        messages_processed=1,
        cost=0.0
    )

    db.session.add(usage)
    db.session.commit()

    return jsonify({
        'reply': bot_response
    })


@chatbot.route('/training', methods=['POST'])
def add_training_data():
    data = request.get_json() or {}

    customer_id = data.get('customer_id')
    intent = data.get('intent')
    response = data.get('response')

    if not customer_id or not intent or not response:
        return jsonify({
            'message': 'customer_id, intent and response are required'
        }), 400

    item = TrainingData(
        customer_id=customer_id,
        intent=intent,
        response=response
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        'message': 'Training data added'
    }), 201