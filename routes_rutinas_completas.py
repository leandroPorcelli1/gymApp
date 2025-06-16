from flask import Blueprint, request, jsonify
from models import db, Rutina, Ejercicio, Serie, EjercicioBase
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound

rutinas_completas_bp = Blueprint('rutinas_completas_bp', __name__)

@rutinas_completas_bp.route('/rutinas/completas', methods=['POST'])
def crear_rutina_completa():
    try:
        data = request.json
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos de la rutina'
            }), 400
            
        campos_requeridos = ['nombre', 'usuarios_id', 'nivel_rutinas_id', 'ejercicios']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': f'El campo {campo} es requerido'
                }), 400
        
        # Validar que exista el ejercicio base
        for ejercicio_data in data['ejercicios']:
            if 'ejercicios_base_id' not in ejercicio_data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': 'Cada ejercicio debe tener un ejercicios_base_id'
                }), 400
                
            ejercicio_base = EjercicioBase.query.get(ejercicio_data['ejercicios_base_id'])
            if not ejercicio_base:
                return jsonify({
                    'error': 'Ejercicio no encontrado',
                    'detalle': f'No existe un ejercicio base con ID {ejercicio_data["ejercicios_base_id"]}'
                }), 404
        
        # Crear la rutina
        rutina = Rutina(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            usuarios_id=data['usuarios_id'],
            nivel_rutinas_id=data['nivel_rutinas_id']
        )
        db.session.add(rutina)
        db.session.flush()
        
        # Crear los ejercicios y sus series
        ejercicios_creados = []
        for ejercicio_data in data['ejercicios']:
            ejercicio = Ejercicio(
                ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
                rutinas_id=rutina.id_rutinas
            )
            db.session.add(ejercicio)
            db.session.flush()
            
            # Validar series
            if 'series' not in ejercicio_data:
                return jsonify({
                    'error': 'Datos incompletos',
                    'detalle': 'Cada ejercicio debe tener al menos una serie'
                }), 400
                
            series_creadas = []
            for serie_data in ejercicio_data['series']:
                if 'repeticiones' not in serie_data or 'peso_kg' not in serie_data:
                    return jsonify({
                        'error': 'Datos incompletos',
                        'detalle': 'Cada serie debe tener repeticiones y peso_kg'
                    }), 400
                    
                serie = Serie(
                    repeticiones=serie_data['repeticiones'],
                    peso_kg=serie_data['peso_kg'],
                    ejercicios_id=ejercicio.id_ejercicios
                )
                db.session.add(serie)
                series_creadas.append({
                    'id': serie.id_series,
                    'repeticiones': serie.repeticiones,
                    'peso_kg': serie.peso_kg
                })
            
            ejercicio_base = EjercicioBase.query.get(ejercicio_data['ejercicios_base_id'])
            ejercicios_creados.append({
                'id': ejercicio.id_ejercicios,
                'nombre': ejercicio_base.nombre,
                'descripcion': ejercicio_base.descripcion,
                'series': series_creadas
            })
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Rutina completa creada exitosamente',
            'rutina': {
                'id': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'ejercicios': ejercicios_creados
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

@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['GET'])
def obtener_rutina_completa(id):
    try:
        rutina = Rutina.query.get_or_404(id)
        
        ejercicios = Ejercicio.query.filter_by(rutinas_id=id).all()
        
        ejercicios_completos = []
        for ejercicio in ejercicios:
            series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
            
            ejercicios_completos.append({
                'id': ejercicio.id_ejercicios,
                'ejercicios_base_id': ejercicio.ejercicios_base_id,
                'nombre': ejercicio.ejercicio_base.nombre,
                'descripcion': ejercicio.ejercicio_base.descripcion,
                'series': [{
                    'id': serie.id_series,
                    'repeticiones': serie.repeticiones,
                    'peso_kg': serie.peso_kg
                } for serie in series]
            })
        
        return jsonify({
            'id': rutina.id_rutinas,
            'nombre': rutina.nombre,
            'descripcion': rutina.descripcion,
            'usuarios_id': rutina.usuarios_id,
            'nivel_rutinas_id': rutina.nivel_rutinas_id,
            'ejercicios': ejercicios_completos
        })
        
    except NotFound:
        return jsonify({
            'error': 'Rutina no encontrada',
            'detalle': f'No existe una rutina con ID {id}'
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

@rutinas_completas_bp.route('/rutinas/completas', methods=['GET'])
def obtener_todas_rutinas_completas():
    try:
        rutinas = Rutina.query.all()
        
        rutinas_completas = []
        for rutina in rutinas:
            ejercicios = Ejercicio.query.filter_by(rutinas_id=rutina.id_rutinas).all()
            
            ejercicios_completos = []
            for ejercicio in ejercicios:
                series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
                
                ejercicios_completos.append({
                    'id': ejercicio.id_ejercicios,
                    'ejercicios_base_id': ejercicio.ejercicios_base_id,
                    'nombre': ejercicio.ejercicio_base.nombre,
                    'descripcion': ejercicio.ejercicio_base.descripcion,
                    'series': [{
                        'id': serie.id_series,
                        'repeticiones': serie.repeticiones,
                        'peso_kg': serie.peso_kg
                    } for serie in series]
                })
            
            rutinas_completas.append({
                'id': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'usuarios_id': rutina.usuarios_id,
                'nivel_rutinas_id': rutina.nivel_rutinas_id,
                'ejercicios': ejercicios_completos
            })
        
        return jsonify(rutinas_completas)
        
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

@rutinas_completas_bp.route('/rutinas/completas/usuario/<int:usuario_id>', methods=['GET'])
def obtener_rutinas_usuario(usuario_id):
    try:
        # Obtener todas las rutinas del usuario
        rutinas = Rutina.query.filter_by(usuarios_id=usuario_id).all()
        
        if not rutinas:
            return jsonify({
                'mensaje': 'No se encontraron rutinas para este usuario',
                'rutinas': []
            }), 200
        
        rutinas_completas = []
        for rutina in rutinas:
            # Obtener todos los ejercicios de la rutina
            ejercicios = Ejercicio.query.filter_by(rutinas_id=rutina.id_rutinas).all()
            
            ejercicios_completos = []
            for ejercicio in ejercicios:
                # Obtener todas las series del ejercicio
                series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
                
                ejercicios_completos.append({
                    'id': ejercicio.id_ejercicios,
                    'ejercicios_base_id': ejercicio.ejercicios_base_id,
                    'nombre': ejercicio.ejercicio_base.nombre,
                    'descripcion': ejercicio.ejercicio_base.descripcion,
                    'series': [{
                        'id': serie.id_series,
                        'repeticiones': serie.repeticiones,
                        'peso_kg': serie.peso_kg
                    } for serie in series]
                })
            
            rutinas_completas.append({
                'id': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'usuarios_id': rutina.usuarios_id,
                'nivel_rutinas_id': rutina.nivel_rutinas_id,
                'ejercicios': ejercicios_completos
            })
        
        return jsonify({
            'mensaje': f'Se encontraron {len(rutinas_completas)} rutinas para el usuario',
            'rutinas': rutinas_completas
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