from flask import Blueprint, request, jsonify
from models import db, Ejercicio, EjercicioBase
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
from security import required_token
from models import Usuario

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

@ejercicios_bp.route('/ejercicios/batch', methods=['POST'])
def crear_ejercicios_batch():
    try:
        data = request.json
        
        if not data or not isinstance(data, list):
            return jsonify({
                'error': 'Datos no válidos',
                'detalle': 'Se requiere un array JSON con los datos de los ejercicios'
            }), 400
            
        for ejercicio_data in data:
            if not isinstance(ejercicio_data, dict):
                return jsonify({
                    'error': 'Datos no válidos',
                    'detalle': 'Cada ejercicio debe ser un objeto JSON'
                }), 400
                
            campos_requeridos = ['ejercicios_base_id', 'rutinas_id']
            for campo in campos_requeridos:
                if campo not in ejercicio_data:
                    return jsonify({
                        'error': 'Datos incompletos',
                        'detalle': f'El campo {campo} es requerido para cada ejercicio'
                    }), 400
                    
            # Validar que exista el ejercicio base
            ejercicio_base = EjercicioBase.query.get(ejercicio_data['ejercicios_base_id'])
            if not ejercicio_base:
                return jsonify({
                    'error': 'Ejercicio base no encontrado',
                    'detalle': f'No existe un ejercicio base con ID {ejercicio_data["ejercicios_base_id"]}'
                }), 404
        
        ejercicios_creados = []
        for ejercicio_data in data:
            ejercicio = Ejercicio(
                ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
                rutinas_id=ejercicio_data['rutinas_id']
            )
            db.session.add(ejercicio)
        
        db.session.commit()
        
        # Obtener los ejercicios recién creados
        for ejercicio_data in data:
            ejercicio = Ejercicio.query.filter_by(
                ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
                rutinas_id=ejercicio_data['rutinas_id']
            ).first()
            if ejercicio:
                ejercicio_base = EjercicioBase.query.get(ejercicio.ejercicios_base_id)
                ejercicios_creados.append({
                    'id': ejercicio.id_ejercicios,
                    'nombre': ejercicio_base.nombre,
                    'descripcion': ejercicio_base.descripcion,
                    'rutinas_id': ejercicio.rutinas_id
                })
        
        return jsonify({
            'mensaje': f'{len(ejercicios_creados)} ejercicios creados exitosamente',
            'ejercicios': ejercicios_creados
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

@ejercicios_bp.route('/ejercicios', methods=['GET'])
def obtener_ejercicios():
    try:
        ejercicios = Ejercicio.query.all()
        return jsonify([{
            'id_ejercicios': e.id_ejercicios,
            'ejercicios_base_id': e.ejercicios_base_id,
            'rutinas_id': e.rutinas_id,
            'nombre': e.ejercicio_base.nombre,
            'descripcion': e.ejercicio_base.descripcion
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

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['PUT'])
def actualizar_ejercicio(id):
    try:
        ejercicio = Ejercicio.query.get_or_404(id)
        data = request.json
        
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos a actualizar'
            }), 400
            
        if 'ejercicios_base_id' in data:
            # Validar que exista el nuevo ejercicio base
            ejercicio_base = EjercicioBase.query.get(data['ejercicios_base_id'])
            if not ejercicio_base:
                return jsonify({
                    'error': 'Ejercicio base no encontrado',
                    'detalle': f'No existe un ejercicio base con ID {data["ejercicios_base_id"]}'
                }), 404
            ejercicio.ejercicios_base_id = data['ejercicios_base_id']
            
        if 'rutinas_id' in data:
            ejercicio.rutinas_id = data['rutinas_id']
            
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Ejercicio actualizado exitosamente',
            'ejercicio': {
                'id': ejercicio.id_ejercicios,
                'ejercicios_base_id': ejercicio.ejercicios_base_id,
                'rutinas_id': ejercicio.rutinas_id,
                'nombre': ejercicio.ejercicio_base.nombre,
                'descripcion': ejercicio.ejercicio_base.descripcion
            }
        })
        
    except NotFound:
        return jsonify({
            'error': 'Ejercicio no encontrado',
            'detalle': f'No existe un ejercicio con ID {id}'
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

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['DELETE'])
def eliminar_ejercicio(id):
    try:
        ejercicio = Ejercicio.query.get_or_404(id)
        db.session.delete(ejercicio)
        db.session.commit()
        return jsonify({
            'mensaje': 'Ejercicio eliminado exitosamente',
            'id': id
        })
        
    except NotFound:
        return jsonify({
            'error': 'Ejercicio no encontrado',
            'detalle': f'No existe un ejercicio con ID {id}'
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

@ejercicios_bp.route('/ejercicios-base', methods=['GET'])
def obtener_ejercicios_base():
    try:
        ejercicios = EjercicioBase.query.all()
        return jsonify([{
            'id_ejercicios_base': e.id_ejercicios_base,
            'nombre': e.nombre,
            'descripcion': e.descripcion
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
def crear_ejercicio_base(token_payload):
    try:
        # Verificar que el usuario existe
        usuario = Usuario.query.get(token_payload.get('id_usuario'))
        if not usuario:
            return {'error': 'Usuario no encontrado', 'detalle': 'El usuario autenticado no existe.'}, 404

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
                    descripcion=ejercicio_data.get('descripcion')
                )
                db.session.add(ejercicio)
                ejercicios_creados.append({
                    'id': ejercicio.id_ejercicios_base,
                    'nombre': ejercicio.nombre,
                    'descripcion': ejercicio.descripcion
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
                descripcion=data.get('descripcion')
            )
            db.session.add(ejercicio)
            db.session.commit()
            
            return jsonify({
                'mensaje': 'Ejercicio base creado exitosamente',
                'ejercicio': {
                    'id': ejercicio.id_ejercicios_base,
                    'nombre': ejercicio.nombre,
                    'descripcion': ejercicio.descripcion
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