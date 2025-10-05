from flask import Blueprint, request, jsonify
from modelos.models import db, Ejercicio, EjercicioBase
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound

ejercicios_bp = Blueprint('ejercicios_bp', __name__)

@ejercicios_bp.route('/ejercicios', methods=['POST'])
def crear_ejercicio():
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos del ejercicio'
            }), 400
            
        campos_requeridos = ['ejercicios_base_id', 'rutinas_id']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': f'El campo {campo} es requerido'
                }), 400
        
        # Validar que exista el ejercicio base
        ejercicio_base = EjercicioBase.query.get(data['ejercicios_base_id'])
        if not ejercicio_base:
            return jsonify({
                'error': 'Ejercicio base no encontrado',
                'detalle': f'No existe un ejercicio base con ID {data["ejercicios_base_id"]}'
            }), 404
        
        ejercicio = Ejercicio(
            ejercicios_base_id=data['ejercicios_base_id'],
            rutinas_id=data['rutinas_id']
        )
        db.session.add(ejercicio)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Ejercicio creado exitosamente',
            'ejercicio': {
                'id': ejercicio.id_ejercicios,
                'ejercicios_base_id': ejercicio.ejercicios_base_id,
                'rutinas_id': ejercicio.rutinas_id,
                'nombre': ejercicio_base.nombre,
                'descripcion': ejercicio_base.descripcion
            }
        }), 201
        
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


@ejercicios_bp.route('/ejercicios/<int:id>', methods=['GET'])
def obtener_ejercicio(id):
    try:
        ejercicio = Ejercicio.query.get_or_404(id)
        return jsonify({
            'id_ejercicios': ejercicio.id_ejercicios,
            'ejercicios_base_id': ejercicio.ejercicios_base_id,
            'rutinas_id': ejercicio.rutinas_id,
            'nombre': ejercicio.ejercicio_base.nombre,
            'descripcion': ejercicio.ejercicio_base.descripcion
        })
        
    except NotFound:
        return jsonify({
            'error': 'Ejercicio no encontrado',
            'detalle': f'No existe un ejercicio con ID {id}'
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
@ejercicios_bp.route('/ejercicios-base', methods=['GET'])
def obtener_ejercicios_base():
    try:
        ejercicios = EjercicioBase.query.all()
        return jsonify([{
            'id_ejercicios_base': e.id_ejercicios_base,
            'nombre': e.nombre,
            'descripcion': e.descripcion,
            'video_url': e.video_url
        } for e in ejercicios])
        
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

@ejercicios_bp.route('/ejercicios-base', methods=['POST'])
# @required_token
def crear_ejercicio_base():
    try:
        # # Verificar que el usuario existe
        # usuario = Usuario.query.get(token_payload.get('id_usuario'))
        # if not usuario:
        #     return {'error': 'Usuario no encontrado', 'detalle': 'El usuario autenticado no existe.'}, 404

        data = request.json
        
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos del ejercicio base'
            }), 400
            
        if isinstance(data, list):
            for ejercicio_data in data:
                if not isinstance(ejercicio_data, dict):
                    return jsonify({
                        'error': 'Datos no válidos',
                        'detalle': 'Cada ejercicio debe ser un objeto JSON'
                    }), 400
                    
                if 'nombre' not in ejercicio_data:
                    return jsonify({
                        'error': 'Datos incompletos',
                        'detalle': 'El campo nombre es requerido para cada ejercicio'
                    }), 400
                    
            ejercicios_creados = []
            for ejercicio_data in data:
                ejercicio = EjercicioBase(
                    nombre=ejercicio_data['nombre'],
                    descripcion=ejercicio_data.get('descripcion'),
                    video_url=ejercicio_data.get('video_url')
                )
                db.session.add(ejercicio)
                ejercicios_creados.append({
                    'id': ejercicio.id_ejercicios_base,
                    'nombre': ejercicio.nombre,
                    'descripcion': ejercicio.descripcion,
                    'video_url': ejercicio.video_url
                })
            db.session.commit()
            
            return jsonify({
                'mensaje': f'{len(ejercicios_creados)} ejercicios base creados exitosamente',
                'ejercicios': ejercicios_creados
            }), 201
            
        else:
            if 'nombre' not in data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': 'El campo nombre es requerido'
                }), 400
                
            ejercicio = EjercicioBase(
                nombre=data['nombre'],
                descripcion=data.get('descripcion'),
                video_url=data.get('video_url')
            )
            db.session.add(ejercicio)
            db.session.commit()
            
            return jsonify({
                'mensaje': 'Ejercicio base creado exitosamente',
                'ejercicio': {
                    'id': ejercicio.id_ejercicios_base,
                    'nombre': ejercicio.nombre,
                    'descripcion': ejercicio.descripcion,
                    'video_url': ejercicio.video_url
                }
            }), 201
            
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