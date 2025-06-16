from flask import Blueprint, request, jsonify
from models import db, Usuario
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import NotFound
import jwt

usuarios_bp = Blueprint('usuarios_bp', __name__)

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)  

# Lista para almacenar tokens invalidados
invalidated_tokens = set()

@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos del usuario'
            }), 400
            
        campos_requeridos = ['nombre', 'email', 'password', 'fecha_nacimiento', 'genero']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': f'El campo {campo} es requerido'
                }), 400
        
        # Validar formato de fecha
        try:
            fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Formato de fecha inválido',
                'detalle': 'La fecha debe estar en formato YYYY-MM-DD'
            }), 400
        
        # Validar que el email no esté en uso
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': 'Email en uso',
                'detalle': 'Ya existe un usuario registrado con este email'
            }), 400
        
        usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password=data['password'],
            fecha_nacimiento=fecha_nacimiento,
            genero=data['genero'],
            auth_provider='local'
        )
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Usuario creado exitosamente',
            'usuario': {
                'id': usuario.id_usuarios,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'fecha_nacimiento': str(usuario.fecha_nacimiento),
                'genero': usuario.genero,
                'auth_provider': usuario.auth_provider
            }
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error de integridad en la base de datos',
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

@usuarios_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        usuarios = Usuario.query.all()
        return jsonify({
            'mensaje': f'Se encontraron {len(usuarios)} usuarios',
            'usuarios': [{
                'id_usuarios': u.id_usuarios,
                'nombre': u.nombre,
                'email': u.email,
                'fecha_nacimiento': str(u.fecha_nacimiento) if u.fecha_nacimiento else None,
                'genero': u.genero,
                'auth_provider': u.auth_provider
            } for u in usuarios]
        })
        
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

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    try:
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

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos a actualizar'
            }), 400
        
        # Solo actualizar campos si el usuario no es de Google
        if usuario.auth_provider != 'google':
            if 'nombre' in data:
                usuario.nombre = data['nombre']
            if 'email' in data:
                # Validar que el nuevo email no esté en uso
                if Usuario.query.filter_by(email=data['email']).first():
                    return jsonify({
                        'error': 'Email en uso',
                        'detalle': 'Ya existe un usuario registrado con este email'
                    }), 400
                usuario.email = data['email']
            if 'password' in data:
                usuario.password = data['password']
            if 'fecha_nacimiento' in data:
                try:
                    usuario.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'error': 'Formato de fecha inválido',
                        'detalle': 'La fecha debe estar en formato YYYY-MM-DD'
                    }), 400
            if 'genero' in data:
                usuario.genero = data['genero']
        else:
            # Para usuarios de Google, solo permitir actualizar ciertos campos
            if 'fecha_nacimiento' in data:
                try:
                    usuario.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'error': 'Formato de fecha inválido',
                        'detalle': 'La fecha debe estar en formato YYYY-MM-DD'
                    }), 400
            if 'genero' in data:
                usuario.genero = data['genero']
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Usuario actualizado exitosamente',
            'usuario': {
                'id': usuario.id_usuarios,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'fecha_nacimiento': str(usuario.fecha_nacimiento) if usuario.fecha_nacimiento else None,
                'genero': usuario.genero,
                'auth_provider': usuario.auth_provider
            }
        })
        
    except NotFound:
        return jsonify({
            'error': 'Usuario no encontrado',
            'detalle': f'No existe un usuario con ID {id}'
        }), 404
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error de integridad en la base de datos',
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

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # Guardar información del usuario antes de eliminarlo
        usuario_info = {
            'id': usuario.id_usuarios,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'auth_provider': usuario.auth_provider
        }
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Usuario eliminado exitosamente',
            'usuario': usuario_info
        })
        
    except NotFound:
        return jsonify({
            'error': 'Usuario no encontrado',
            'detalle': f'No existe un usuario con ID {id}'
        }), 404
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

        # Generate JWT token
        token_payload = {
            'user_id': usuario.id_usuarios,
            'email': usuario.email,
            'auth_provider': usuario.auth_provider,
            'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES
        }
        access_token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')

        return jsonify({
            'mensaje': 'Login exitoso',
            'usuario': {
                'id_usuarios': usuario.id_usuarios,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'auth_provider': usuario.auth_provider
            },
            'access_token': access_token,
            'expires_in': int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
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
def logout():
    try:
        # Obtener el token del header de autorización
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Token no proporcionado',
                'detalle': 'Se requiere un token de autenticación'
            }), 401

        token = auth_header.split(' ')[1]
        
        # Agregar el token a la lista de tokens invalidados
        invalidated_tokens.add(token)
        
        return jsonify({
            'mensaje': 'Sesión cerrada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error al cerrar sesión',
            'detalle': str(e)
        }), 500

# Función para verificar si un token está invalidado
def is_token_invalidated(token):
    return token in invalidated_tokens 