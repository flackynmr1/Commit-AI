from datetime import datetime, timedelta
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    subscription_tier = db.Column(db.String(20), default='free')
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)
    stripe_subscription_id = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customers = db.relationship(
        'Customer',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_auth_token(token):
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload['sub']
            return User.query.get(user_id)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    website_url = db.Column(db.String(255))
    widget_config = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    conversations = db.relationship(
        'Conversation',
        backref='customer',
        lazy=True,
        cascade='all, delete-orphan'
    )

    training_data = db.relationship(
        'TrainingData',
        backref='customer',
        lazy=True,
        cascade='all, delete-orphan'
    )

    usage_records = db.relationship(
        'Usage',
        backref='customer',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    messages = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class TrainingData(db.Model):
    __tablename__ = 'training_data'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    intent = db.Column(db.String(100), nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('customer_id', 'intent', name='_customer_intent_uc'),
    )


class Usage(db.Model):
    __tablename__ = 'usage'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    messages_processed = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)

    __table_args__ = (
        db.UniqueConstraint('customer_id', 'date', name='_customer_date_uc'),
    )