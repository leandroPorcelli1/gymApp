from flask import Blueprint, request, jsonify
from models import db, Usuario
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    # Convertir el string de fecha a objeto date
    fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
    
    usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        password=data['password'],
        fecha_nacimiento=fecha_nacimiento,
        genero=data['genero'],
        auth_provider='local'  # Especificamos que es un usuario local
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado', 'id': usuario.id_usuarios}), 201

@usuarios_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{
        'id_usuarios': u.id_usuarios,
        'nombre': u.nombre,
        'email': u.email,
        'fecha_nacimiento': str(u.fecha_nacimiento) if u.fecha_nacimiento else None,
        'genero': u.genero,
        'auth_provider': u.auth_provider
    } for u in usuarios])

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        'id_usuarios': usuario.id_usuarios,
        'nombre': usuario.nombre,
        'email': usuario.email,
        'fecha_nacimiento': str(usuario.fecha_nacimiento) if usuario.fecha_nacimiento else None,
        'genero': usuario.genero,
        'auth_provider': usuario.auth_provider
    })

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.json
    
    # Solo actualizar campos si el usuario no es de Google
    if usuario.auth_provider != 'google':
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.email = data.get('email', usuario.email)
        usuario.password = data.get('password', usuario.password)
        usuario.fecha_nacimiento = data.get('fecha_nacimiento', usuario.fecha_nacimiento)
        usuario.genero = data.get('genero', usuario.genero)
    else:
        # Para usuarios de Google, solo permitir actualizar ciertos campos
        usuario.fecha_nacimiento = data.get('fecha_nacimiento', usuario.fecha_nacimiento)
        usuario.genero = data.get('genero', usuario.genero)
    
    db.session.commit()
    return jsonify({'mensaje': 'Usuario actualizado'})

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado'})

@usuarios_bp.route('/usuarios/google-login', methods=['POST'])
def google_login():
    try:
        # Obtener el token de ID de Google del request
        token = request.json.get('token')
        
        # Verificar el token con Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )

        # Verificar que el token es válido
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Token inválido')

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

        return jsonify({
            'mensaje': 'Login exitoso',
            'usuario': {
                'id_usuarios': usuario.id_usuarios,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'auth_provider': usuario.auth_provider
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Error en el servidor'}), 500 