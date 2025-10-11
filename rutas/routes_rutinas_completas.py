from flask import Blueprint, request, jsonify
from modelos.models import db, Rutina, Ejercicio, Serie, EjercicioBase, Entrenamiento, EntrenamientoRealizado, Usuario
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound
from security import required_token
from sqlalchemy import func
from modelos.models import SerieRealizada

rutinas_completas_bp = Blueprint('rutinas_completas_bp', __name__)

# --- Helper Function para construir la respuesta JSON de una rutina ---
def _build_rutina_json(rutina):
    """Construye un diccionario serializable en JSON a partir de un objeto Rutina."""
    ejercicios_completos = []
    for ejercicio in rutina.ejercicios:
        ejercicios_completos.append({
            'id': ejercicio.id_ejercicios,
            'ejercicios_base_id': ejercicio.ejercicios_base_id,
            'nombre': ejercicio.ejercicio_base.nombre,
            'descripcion': ejercicio.ejercicio_base.descripcion,
            'video_url': ejercicio.ejercicio_base.video_url,
            'series': [{'id': s.id_series, 'repeticiones': s.repeticiones, 'peso_kg': s.peso_kg} for s in ejercicio.series]
        })
    return {
        'id': rutina.id_rutinas,
        'nombre': rutina.nombre,
        'descripcion': rutina.descripcion,
        'usuarios_id': rutina.usuarios_id,
        'nivel_rutinas_id': rutina.nivel_rutinas_id,
        'ejercicios': ejercicios_completos
    }

@rutinas_completas_bp.route('/rutinas/completas', methods=['POST'])
@required_token
def crear_rutina_completa(token_payload):
    try:
        data = request.json

        # Validar datos requeridos
        if not data:
            return jsonify({
                'error': 'Datos no proporcionados',
                'detalle': 'Se requiere un cuerpo JSON con los datos de la rutina'
            }), 400

        # Se elimina 'usuarios_id' de los campos requeridos, se toma del token.
        campos_requeridos = ['nombre', 'nivel_rutinas_id', 'ejercicios']
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
            usuarios_id=token_payload.get('id_usuario'), # ID del usuario desde el token
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
@required_token
def obtener_rutina_completa(id, token_payload):
    try:
        # --- Mejora de Rendimiento: Carga Eficiente de Datos Relacionados ---
        rutina = Rutina.query.options(
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.ejercicio_base),
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.series)
        ).get_or_404(id)

        # --- Validación de Propiedad ---
        if rutina.usuarios_id != token_payload.get('id_usuario'):
            return jsonify({'error': 'No autorizado para ver esta rutina.'}), 403

        return jsonify(_build_rutina_json(rutina))

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
@required_token
def obtener_todas_rutinas_completas(token_payload):
    """ Obtiene todas las rutinas completas del usuario autenticado. """
    try:
        user_id = token_payload.get('id_usuario')
        # --- Consulta Segura y Optimizada ---
        rutinas = Rutina.query.filter_by(usuarios_id=user_id).options(
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.ejercicio_base),
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.series)
        ).order_by(Rutina.nombre).all()

        return jsonify([_build_rutina_json(rutina) for rutina in rutinas])

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
@required_token
def obtener_rutinas_usuario(usuario_id, token_payload):
    try:
        # --- Validación de Propiedad ---
        if token_payload.get('id_usuario') != usuario_id:
            return jsonify({'error': 'No autorizado', 'detalle': 'No puedes ver rutinas de otro usuario.'}), 403

        # --- Consulta Optimizada ---
        rutinas = Rutina.query.filter_by(usuarios_id=usuario_id).options(
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.ejercicio_base),
            db.joinedload(Rutina.ejercicios).joinedload(Ejercicio.series)
        ).order_by(Rutina.nombre).all()

        if not rutinas:
            return jsonify({
                'mensaje': 'No se encontraron rutinas para este usuario',
                'rutinas': []
            }), 200

        return jsonify({
            'mensaje': f'Se encontraron {len(rutinas)} rutinas para el usuario',
            'rutinas': [_build_rutina_json(rutina) for rutina in rutinas]
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
@required_token
def obtener_entrenamientos_realizados_por_rutina(id_rutina, token_payload):
    """
    Obtiene todos los entrenamientos realizados asociados a una rutina específica.
    """
    try:
        # 1. Verificar que la rutina exista
        rutina = Rutina.query.get_or_404(id_rutina)

        # --- Validación de Propiedad ---
        if rutina.usuarios_id != token_payload.get('id_usuario'):
            return jsonify({'error': 'No autorizado para ver los entrenamientos de esta rutina.'}), 403

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



@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['DELETE'])
@required_token
def eliminar_rutina_completa(id, token_payload):
    try:
        rutina = Rutina.query.get_or_404(id)
        # --- Validación de Propiedad ---
        if rutina.usuarios_id != token_payload.get('id_usuario'):
            return jsonify({'error': 'No autorizado', 'detalle': 'No puedes eliminar rutinas de otro usuario.'}), 403

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

# --- Funciones de Servicio para Estadísticas ---

def _get_max_pesos_por_rutina(usuario_id):
    """
     Encuentra el peso máximo levantado para cada rutina de un usuario y el ejercicio asociado.

     Usa una función de ventana de SQL (`row_number`) para rankear los levantamientos
     por peso dentro de cada rutina y seleccionar solo el más alto (ranking 1),
     optimizando el proceso en una única consulta.
     """
    subquery = db.session.query(
        Entrenamiento.rutinas_id,
        SerieRealizada.peso_kg,
        EjercicioBase.nombre.label("ejercicio_nombre"),
        func.row_number().over(
            partition_by=Entrenamiento.rutinas_id,
            order_by=SerieRealizada.peso_kg.desc()
        ).label('rn')
    ).join(EntrenamientoRealizado, SerieRealizada.entrenamientos_realizados_id == EntrenamientoRealizado.id_entrenamientos_realizados)\
     .join(Entrenamiento, EntrenamientoRealizado.entrenamientos_id == Entrenamiento.id_entrenamientos)\
     .join(Ejercicio, EntrenamientoRealizado.ejercicios_id == Ejercicio.id_ejercicios)\
     .join(EjercicioBase, Ejercicio.ejercicios_base_id == EjercicioBase.id_ejercicios_base)\
     .filter(Entrenamiento.usuarios_id == usuario_id).subquery()

    return db.session.query(
        Rutina.id_rutinas,
        Rutina.nombre.label("rutina_nombre"),
        subquery.c.peso_kg.label("max_peso"),
        subquery.c.ejercicio_nombre.label("ejercicio_max_peso")
    ).join(subquery, Rutina.id_rutinas == subquery.c.rutinas_id)\
     .filter(subquery.c.rn == 1).all()


def _get_avg_pesos_por_rutina(usuario_id):
    """
    Ejecuta una consulta para calcular el peso promedio levantado para cada rutina de un usuario.
    """
    return db.session.query(
        Rutina.id_rutinas,
        func.avg(SerieRealizada.peso_kg).label("promedio_peso")
    ).join(Entrenamiento, Rutina.id_rutinas == Entrenamiento.rutinas_id)\
     .join(EntrenamientoRealizado, Entrenamiento.id_entrenamientos == EntrenamientoRealizado.entrenamientos_id)\
     .join(SerieRealizada, EntrenamientoRealizado.id_entrenamientos_realizados == SerieRealizada.entrenamientos_realizados_id)\
     .filter(Rutina.usuarios_id == usuario_id)\
     .group_by(Rutina.id_rutinas).all()


@rutinas_completas_bp.route('/rutinas/estadisticas', methods=['GET'])
@required_token
def estadisticas_rutinas(token_payload):
    """
    Calcula y devuelve las estadísticas de rendimiento para todas las rutinas de un usuario.

    Para cada rutina, calcula:
    - El peso máximo levantado en un único levantamiento.
    - El nombre del ejercicio donde se logró dicho peso máximo.
    - El peso promedio general, considerando todas las series de todos los entrenamientos.

    """
    try:
        # 1. Validaciones iniciales
        usuario_id = token_payload.get('id_usuario')
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado', 'detalle': 'El usuario asociado al token no existe.'}), 404

        rutinas_usuario = Rutina.query.filter_by(usuarios_id=usuario_id).all()
        if not rutinas_usuario:
            return jsonify({'mensaje': 'No se encontraron rutinas para este usuario.'}), 200

        max_pesos = _get_max_pesos_por_rutina(usuario_id)
        avg_pesos = _get_avg_pesos_por_rutina(usuario_id)

    # Procesamiento y combinación de resultados
        max_map = {r.id_rutinas: r for r in max_pesos}
        avg_map = {r.id_rutinas: r.promedio_peso for r in avg_pesos}

        resultado_final = []
        for rutina in rutinas_usuario:
            max_info = max_map.get(rutina.id_rutinas)
            avg_info = avg_map.get(rutina.id_rutinas)

            resultado_final.append({
                "rutina_id": rutina.id_rutinas,
                "rutina_nombre": rutina.nombre,
                "max_peso_levantado": float(max_info.max_peso) if max_info and max_info.max_peso is not None else 0,
                "ejercicio_max_peso": max_info.ejercicio_max_peso if max_info else None,
                "promedio_peso_general": float(avg_info) if avg_info is not None else 0
            })

        # Validación final y respuesta
        if not any(r['max_peso_levantado'] > 0 for r in resultado_final):
            return jsonify({
                'mensaje': 'No hay estadísticas de peso disponibles.',
                'detalle': 'Aún no se han registrado entrenamientos con peso para estas rutinas.',
                'estadisticas': resultado_final
            }), 200

        return jsonify(resultado_final), 200

    except Exception as e:
        return jsonify({"error": "Ocurrió un error al calcular las estadísticas", "detalle": str(e)}), 500