import jwt
import stripe
from functools import wraps
from flask import request, jsonify, current_app

from models import User, db
from . import billing


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )

            current_user = User.query.get(data['sub'])

            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@billing.route('/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(current_user):
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    data = request.get_json()
    price_id = data.get('price_id')

    if not price_id:
        return jsonify({'message': 'Price ID is required'}), 400

    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email
        )

        current_user.stripe_customer_id = customer.id
        db.session.commit()
    else:
        customer = stripe.Customer.retrieve(
            current_user.stripe_customer_id
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=current_app.config.get(
                'FRONTEND_URL',
                'http://localhost:5000'
            ) + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=current_app.config.get(
                'FRONTEND_URL',
                'http://localhost:5000'
            ) + '/cancel',
        )

        return jsonify({
            'id': checkout_session.id
        })

    except Exception as e:
        return jsonify({
            'message': str(e)
        }), 403


@billing.route('/portal', methods=['POST'])
@token_required
def customer_portal(current_user):
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    if not current_user.stripe_customer_id:
        return jsonify({
            'message': 'No Stripe customer found'
        }), 400

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=current_app.config.get(
                'FRONTEND_URL',
                'http://localhost:5000'
            ) + '/account',
        )

        return jsonify({
            'url': portal_session.url
        })

    except Exception as e:
        return jsonify({
            'message': str(e)
        }), 403


@billing.route('/webhook', methods=['POST'])
def stripe_webhook():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )

    except ValueError:
        return jsonify({
            'message': 'Invalid payload'
        }), 400

    except stripe.error.SignatureVerificationError:
        return jsonify({
            'message': 'Invalid signature'
        }), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_invoice_payment_succeeded(invoice)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return jsonify({
        'status': 'success'
    })


def handle_checkout_session(session):
    pass


def handle_invoice_payment_succeeded(invoice):
    pass


def handle_subscription_deleted(subscription):
    pass
