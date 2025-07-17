import os, pytz
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
tz = pytz.timezone("America/Argentina/Buenos_Aires")

# Set en memoria para tokens invalidados
_invalidated_tokens = set()

def is_token_invalidated(token):
    return token in _invalidated_tokens

def _invalidate_token(token):
    _invalidated_tokens.add(token)

# Permitir llamar is_token_invalidated.invalidate(token)
is_token_invalidated.invalidate = _invalidate_token

# Crear un JWT token

def create_token(id_usuario, email, auth_provider):
    payload = {
        "id_usuario": id_usuario,
        "email": email,
        "auth_provider": auth_provider,
        "exp": datetime.datetime.now(tz) + datetime.timedelta(hours=24),
        "iat": datetime.datetime.now(tz)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

# Verificar un JWT token

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

# Decorador para requerir token en endpoints

def required_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        token = auth_header.split(' ')[1]
        if is_token_invalidated(token):
            return jsonify({'error': 'Token invalidado'}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        # Puedes pasar el payload al endpoint si lo necesitas
        return f(*args, **kwargs, token_payload=payload)
    return decorated 