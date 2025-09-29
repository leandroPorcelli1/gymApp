from flask import Blueprint, request, jsonify
from models import db, Rutina, Ejercicio, Serie, EjercicioBase, Entrenamiento, EntrenamientoRealizado, SerieRealizada
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
from security import required_token

rutinas_completas_bp = Blueprint('rutinas_completas_bp', __name__)

@rutinas_completas_bp.route('/rutinas/completas', methods=['POST'])
# @required_token
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
                db.session.flush()

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
# @required_token
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
# @required_token
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
# @required_token
def obtener_rutinas_usuario(usuario_id):
    try:
        # # Verificar que el id del token coincida con el usuario_id del endpoint
        # if token_payload.get('id_usuario') != usuario_id:
        #     return {'error': 'No autorizado', 'detalle': 'No puedes ver rutinas de otro usuario.'}, 403
        # # Obtener todas las rutinas del usuario
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
                    'video_url': ejercicio.ejercicio_base.video_url,
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


@rutinas_completas_bp.route('/rutinas/<int:id_rutina>/entrenamientos-realizados', methods=['GET'])
# @required_token
def obtener_entrenamientos_realizados_por_rutina(id_rutina):
    """
    Obtiene todos los entrenamientos realizados asociados a una rutina específica.
    """
    try:
        # 1. Verificar que la rutina exista
        rutina = Rutina.query.get_or_404(id_rutina)

        # 2. Obtener todos los entrenamientos para esa rutina, cargando eficientemente los datos relacionados
        entrenamientos = Entrenamiento.query.filter_by(rutinas_id=id_rutina).options(
            db.joinedload(Entrenamiento.realizados).joinedload(EntrenamientoRealizado.series_realizadas),
            db.joinedload(Entrenamiento.realizados).joinedload(EntrenamientoRealizado.ejercicio).joinedload(Ejercicio.ejercicio_base)
        ).order_by(Entrenamiento.fecha.desc()).all()

        if not entrenamientos:
            return jsonify({
                'mensaje': 'No se encontraron entrenamientos realizados para esta rutina',
                'entrenamientos': []
            }), 200

        # 3. Construir la respuesta JSON
        resultado = []
        for entrenamiento in entrenamientos:
            entrenamiento_info = {
                'id_entrenamiento': entrenamiento.id_entrenamientos,
                'fecha': entrenamiento.fecha.isoformat(),
                'ejercicios_realizados': []
            }
            for realizado in entrenamiento.realizados:
                entrenamiento_info['ejercicios_realizados'].append({
                    'id_entrenamiento_realizado': realizado.id_entrenamientos_realizados,
                    'ejercicio': {
                        'id_ejercicio': realizado.ejercicio.id_ejercicios,
                        'nombre': realizado.ejercicio.ejercicio_base.nombre
                    },
                    'series_realizadas': [
                        {'id_series_realizadas': s.id_series_realizadas, 'repeticiones': s.repeticiones, 'peso_kg': s.peso_kg} for s in realizado.series_realizadas
                    ]
                })
            resultado.append(entrenamiento_info)

        return jsonify(resultado)

    except NotFound:
        return jsonify({'error': 'Rutina no encontrada', 'detalle': f'No existe una rutina con ID {id_rutina}'}), 404
    except Exception as e:
        return jsonify({'error': 'Ocurrió un error inesperado', 'detalle': str(e)}), 500


@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['PUT'])
# @required_token
def modificar_rutina_completa(id):
    try:
        rutina = Rutina.query.get_or_404(id)
        # # Verificar que el usuario autenticado es el dueño de la rutina
        # if rutina.usuarios_id != token_payload.get('id_usuario'):
        #     return {'error': 'No autorizado', 'detalle': 'No puedes modificar rutinas de otro usuario.'}, 403
        data = request.json

        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos a modificar'
            }), 400

        # Modificar datos básicos de la rutina si se proporcionan
        if 'nombre' in data:
            rutina.nombre = data['nombre']
        if 'descripcion' in data:
            rutina.descripcion = data['descripcion']
        if 'nivel_rutinas_id' in data:
            rutina.nivel_rutinas_id = data['nivel_rutinas_id']

        # Modificar ejercicios si se proporcionan
        if 'ejercicios' in data:
            # Obtener ejercicios existentes
            ejercicios_existentes = Ejercicio.query.filter_by(rutinas_id=id).all()
            ejercicios_existentes_dict = {e.id_ejercicios: e for e in ejercicios_existentes}

            for ejercicio_data in data['ejercicios']:
                # Si el ejercicio tiene id_ejercicios, es una modificación
                if 'id_ejercicios' in ejercicio_data:
                    ejercicio = ejercicios_existentes_dict.get(ejercicio_data['id_ejercicios'])
                    if not ejercicio:
                        return jsonify({
                            'error': 'Ejercicio no encontrado',
                            'detalle': f'No existe un ejercicio con ID {ejercicio_data["id_ejercicios"]} en esta rutina'
                        }), 404

                    # Modificar series si se proporcionan
                    if 'series' in ejercicio_data:
                        # Eliminar series existentes
                        Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).delete()

                        # Crear nuevas series
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

                # Si no tiene id_ejercicios pero tiene ejercicios_base_id, es un nuevo ejercicio
                elif 'ejercicios_base_id' in ejercicio_data:
                    ejercicio_base = EjercicioBase.query.get(ejercicio_data['ejercicios_base_id'])
                    if not ejercicio_base:
                        return jsonify({
                            'error': 'Ejercicio base no encontrado',
                            'detalle': f'No existe un ejercicio base con ID {ejercicio_data["ejercicios_base_id"]}'
                        }), 404

                    ejercicio = Ejercicio(
                        ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
                        rutinas_id=rutina.id_rutinas
                    )
                    db.session.add(ejercicio)
                    db.session.flush()

                    # Crear series para el nuevo ejercicio
                    if 'series' in ejercicio_data:
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
                else:
                    return jsonify({
                        'error': 'Datos incompletos',
                        'detalle': 'Cada ejercicio debe tener id_ejercicios (para modificar) o ejercicios_base_id (para crear)'
                    }), 400

        db.session.commit()

        # Obtener la rutina actualizada para la respuesta
        ejercicios = Ejercicio.query.filter_by(rutinas_id=id).all()
        ejercicios_completos = []
        for ejercicio in ejercicios:
            series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
            ejercicios_completos.append({
                'id_ejercicios': ejercicio.id_ejercicios,
                'ejercicios_base_id': ejercicio.ejercicios_base_id,
                'nombre': ejercicio.ejercicio_base.nombre,
                'descripcion': ejercicio.ejercicio_base.descripcion,
                'series': [{
                    'id_series': serie.id_series,
                    'repeticiones': serie.repeticiones,
                    'peso_kg': serie.peso_kg
                } for serie in series]
            })

        return jsonify({
            'mensaje': 'Rutina modificada exitosamente',
            'rutina': {
                'id_rutinas': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'usuarios_id': rutina.usuarios_id,
                'nivel_rutinas_id': rutina.nivel_rutinas_id,
                'ejercicios': ejercicios_completos
            }
        })

    except NotFound:
        return jsonify({
            'error': 'Rutina no encontrada',
            'detalle': f'No existe una rutina con ID {id}'
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

@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['DELETE'])
# @required_token
def eliminar_rutina_completa(id):
    try:
        rutina = Rutina.query.get_or_404(id)
        # # --- Lógica de Seguridad (para cuando se reactive @required_token) ---
        # # Verificar que el usuario autenticado es el dueño de la rutina
        # if rutina.usuarios_id != token_payload.get('id_usuario'):
        #     return jsonify({'error': 'No autorizado', 'detalle': 'No puedes eliminar rutinas de otro usuario.'}), 403


        db.session.delete(rutina)
        db.session.commit()

        return jsonify({
            'mensaje': 'Rutina eliminada exitosamente',
            'detalle': f'Se eliminó la rutina con ID {id} y todos sus datos asociados (ejercicios, series y entrenamientos realizados).'
        }), 200

    except NotFound:
        return jsonify({
            'error': 'Rutina no encontrada',
            'detalle': f'No existe una rutina con ID {id}'
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