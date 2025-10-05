from flask import Blueprint, request, jsonify
from modelos.models import db, Usuario
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import NotFound
from security import create_token, required_token, is_token_invalidated

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@required_token
def obtener_usuario(id, token_payload):
    try:
        # --- Validación de Propiedad ---
        if token_payload.get('id_usuario') != id:
            return jsonify({'error': 'No autorizado', 'detalle': 'No puedes ver datos de otro usuario.'}), 403

        usuario = Usuario.query.get_or_404(id)
        return jsonify({
            'id_usuarios': usuario.id_usuarios,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'fecha_nacimiento': str(usuario.fecha_nacimiento) if usuario.fecha_nacimiento else None,
            'genero': usuario.genero,
            'auth_provider': usuario.auth_provider
        })
        
    except NotFound:
        return jsonify({
            'error': 'Usuario no encontrado',
            'detalle': f'No existe un usuario con ID {id}'
        }), 404
    except SQLAlchemyError as e:
        return jsonify({
            'error': 'Error en la base de datos',
            'detalle': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Error inesperado',
            'detalle': str(e)
        }), 500

@usuarios_bp.route('/usuarios/google-login', methods=['POST'])
def google_login():
    try:
        data = request.json
        
        if not data or 'token' not in data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un token de Google'
            }), 400
        
        # Obtener el token de ID de Google del request
        token = data['token']
        
        # Verificar el token con Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )

        # Verificar que el token es válido
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return jsonify({
                'error': 'Token inválido',
                'detalle': 'El token proporcionado no es válido'
            }), 400

        # Obtener información del usuario
        email = idinfo['email']
        nombre = idinfo.get('name', '')
        google_id = idinfo['sub']  # ID único de Google
        
        # Buscar si el usuario ya existe
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            # Crear nuevo usuario si no existe
            usuario = Usuario(
                nombre=nombre,
                email=email,
                google_id=google_id,
                auth_provider='google',
                password=None,
                fecha_nacimiento=None,
                genero=None
            )
            db.session.add(usuario)
            db.session.commit()
        elif usuario.auth_provider != 'google':
            # Si el usuario existe pero no es de Google, actualizar sus datos
            usuario.google_id = google_id
            usuario.auth_provider = 'google'
            db.session.commit()

        access_token = create_token(usuario.id_usuarios, usuario.email, usuario.auth_provider)

        return jsonify({
            'mensaje': 'Login exitoso',
            'usuario': {
                'id_usuarios': usuario.id_usuarios,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'auth_provider': usuario.auth_provider
            },
            'access_token': access_token,
        }), 200

    except ValueError as e:
        return jsonify({
            'error': 'Error de validación',
            'detalle': str(e)
        }), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error en la base de datos',
            'detalle': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error inesperado',
            'detalle': str(e)
        }), 500

@usuarios_bp.route('/usuarios/logout', methods=['POST'])
@required_token
def logout(token_payload): # Se añade token_payload aunque no se use directamente, es requerido por el decorador
    try:
        # Obtener el token del header de autorización
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Token no proporcionado',
                'detalle': 'Se requiere un token de autenticación'
            }), 401

        token = auth_header.split(' ')[1]
        
        # Usar is_token_invalidated de security.py
        if is_token_invalidated(token):
            return jsonify({'error': 'Token ya invalidado'}), 401
        
        # Invalidar el token usando la función de security.py
        is_token_invalidated.invalidate(token)
        
        return jsonify({
            'mensaje': 'Sesión cerrada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error al cerrar sesión',
            'detalle': str(e)
        }), 500 