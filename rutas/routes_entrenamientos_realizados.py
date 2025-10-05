from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Se importan los modelos necesarios para las nuevas validaciones
from modelos.models import db, EntrenamientoRealizado, Entrenamiento, Ejercicio, SerieRealizada, Rutina
from security import required_token

entrenamientos_realizados_bp = Blueprint('entrenamientos_realizados_bp', __name__)


@entrenamientos_realizados_bp.route('/entrenamientos_realizados', methods=['POST'])
@required_token
def crear_entrenamiento_realizados(token_payload):
    data = request.json
    if not data:
        return jsonify({'error': 'No se proporcionaron datos en el cuerpo de la solicitud'}), 400

    # Se obtiene el ID del usuario directamente del token para mayor seguridad
    user_id_from_token = token_payload.get('id_usuario')

    # --- Inicio de Validaciones ---

    # 1. Validación de campos requeridos
    # Se elimina 'usuarios_id' de los campos requeridos en el JSON, ya que se toma del token.
    required_fields = ['fecha', 'rutinas_id', 'ejercicios']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Faltan campos requeridos: {", ".join(missing_fields)}'}), 400

    # 2. Validación de tipos, formatos y existencia
    try:
        datetime.fromisoformat(data['fecha'].split('T')[0])
    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha es inválido. Use YYYY-MM-DD.'}), 400

    if not isinstance(data['rutinas_id'], int):
        return jsonify({'error': 'El campo "rutinas_id" debe ser un entero.'}), 400

    # Validar que la rutina exista y que pertenezca al usuario autenticado
    rutina = Rutina.query.get(data['rutinas_id'])
    if not rutina:
        return jsonify({'error': 'Rutina no encontrada', 'detalle': f"La rutina con id {data['rutinas_id']} no existe."}), 404

    # --- Validación de Propiedad ---
    if rutina.usuarios_id != user_id_from_token:
        return jsonify({'error': 'Acción no permitida', 'detalle': 'No puedes registrar un entrenamiento para una rutina que no te pertenece.'}), 403

    if not isinstance(data['ejercicios'], list) or not data['ejercicios']:
        return jsonify({'error': 'El campo "ejercicios" debe ser una lista no vacía.'}), 400

    # 3. Validación de ejercicios y su pertenencia a la rutina
    for i, ejercicio_data in enumerate(data['ejercicios']):
        if not isinstance(ejercicio_data, dict):
            return jsonify({'error': f'El elemento en el índice {i} de "ejercicios" debe ser un objeto.'}), 400

        if 'ejercicios_id' not in ejercicio_data or not isinstance(ejercicio_data['ejercicios_id'], int):
            return jsonify(
                {'error': f'El ejercicio en el índice {i} debe tener un "ejercicios_id" de tipo entero.'}), 400

        # Se valida que el ejercicio exista, pero no su pertenencia a la rutina
        ejercicio_id = ejercicio_data['ejercicios_id']
        ejercicio = Ejercicio.query.get(ejercicio_id)
        if not ejercicio:
            return jsonify({'error': f'El ejercicio con ID {ejercicio_id} no existe.'}), 404

        if 'series' not in ejercicio_data or not isinstance(ejercicio_data['series'], list) or not ejercicio_data[
            'series']:
            return jsonify({
                               'error': f'El campo "series" del ejercicio en el índice {i} es requerido y debe ser una lista no vacía.'}), 400

        for j, serie_data in enumerate(ejercicio_data['series']):
            if not isinstance(serie_data, dict):
                return jsonify({'error': f'La serie en el índice {j} del ejercicio {i} debe ser un objeto.'}), 400

            serie_required_fields = ['repeticiones', 'peso_kg']
            if any(field not in serie_data for field in serie_required_fields):
                return jsonify(
                    {
                        'error': f'Faltan campos en la serie {j} del ejercicio {i}: {", ".join(serie_required_fields)}'}), 400

            if not isinstance(serie_data['repeticiones'], int) or serie_data['repeticiones'] < 0:
                return jsonify(
                    {
                        'error': f'El campo "repeticiones" en la serie {j} del ejercicio {i} debe ser un entero no negativo.'}), 400
            if not isinstance(serie_data['peso_kg'], (int, float)) or serie_data['peso_kg'] < 0:
                return jsonify(
                    {
                        'error': f'El campo "peso_kg" en la serie {j} del ejercicio {i} debe ser un número no negativo.'}), 400

    # --- Fin de Validaciones ---

    try:
        entrenamiento = Entrenamiento(
            fecha=data['fecha'],
            usuarios_id=user_id_from_token, # Se usa el ID del token
            rutinas_id=data['rutinas_id']
        )
        db.session.add(entrenamiento)
        db.session.flush()

        ultimo_entrenamiento_realizado = None
        for ejercicio_data in data['ejercicios']:
            entrenamiento_realizado = EntrenamientoRealizado(
                entrenamientos_id=entrenamiento.id_entrenamientos,
                ejercicios_id=ejercicio_data["ejercicios_id"]
            )
            db.session.add(entrenamiento_realizado)
            db.session.flush()
            ultimo_entrenamiento_realizado = entrenamiento_realizado

            for serie_data in ejercicio_data['series']:
                serie_realizada = SerieRealizada(
                    entrenamientos_realizados_id=entrenamiento_realizado.id_entrenamientos_realizados,
                    repeticiones=serie_data['repeticiones'],
                    peso_kg=serie_data['peso_kg']
                )
                db.session.add(serie_realizada)

        db.session.commit()

        return jsonify(
            {'mensaje': 'Entrenamiento realizado creado con éxito',
             'id': ultimo_entrenamiento_realizado.id_entrenamientos_realizados}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error en la base de datos', 'detalle': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ocurrió un error inesperado', 'detalle': str(e)}), 500


@entrenamientos_realizados_bp.route('/entrenamientos_realizados', methods=['GET'])
@required_token
def obtener_entrenamientos_realizados(token_payload):
    try:
        user_id_from_token = token_payload.get('id_usuario')

        # --- Consulta Optimizada y Segura ---
        # Se obtienen solo los entrenamientos del usuario autenticado
        # y se cargan los datos relacionados de forma eficiente para evitar N+1 queries.
        entrenamientos = Entrenamiento.query.filter_by(usuarios_id=user_id_from_token).options(
            db.joinedload(Entrenamiento.realizados).joinedload(EntrenamientoRealizado.series_realizadas),
            db.joinedload(Entrenamiento.realizados).joinedload(EntrenamientoRealizado.ejercicio).joinedload(Ejercicio.ejercicio_base)
        ).order_by(Entrenamiento.fecha.desc()).all()

        realizados_info = []
        for entrenamiento in entrenamientos:
            for realizado in entrenamiento.realizados:
                series_info = [{'id': s.id_series_realizadas, 'repeticiones': s.repeticiones, 'peso_kg': s.peso_kg} for s in realizado.series_realizadas]
                realizados_info.append({
                    'id_entrenamientos_realizados': realizado.id_entrenamientos_realizados,
                    'entrenamientos_id': realizado.entrenamientos_id,
                    'fecha_entrenamiento': entrenamiento.fecha.isoformat(),
                    'ejercicio': {
                        'id': realizado.ejercicio.id_ejercicios,
                        'nombre': realizado.ejercicio.ejercicio_base.nombre
                    },
                    'series_realizadas': series_info
                })

        return jsonify(realizados_info), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Error en la base de datos', 'detalle': str(e)}), 500


@entrenamientos_realizados_bp.route('/entrenamientos_realizados/<int:id>', methods=['GET'])
@required_token
def obtener_entrenamiento_realizado(id, token_payload):
    realizado = EntrenamientoRealizado.query.get(id)

    # --- Validación de Existencia ---
    # Se añade una validación explícita para devolver un mensaje de error personalizado.
    if not realizado:
        return jsonify({'error': 'Entrenamiento realizado no encontrado', 'detalle': f'No se encontró un entrenamiento realizado con el ID {id}.'}), 404

    # --- Validación de Propiedad ---
    # Se verifica que el entrenamiento realizado pertenezca al usuario autenticado.
    if realizado.entrenamiento.usuarios_id != token_payload.get('id_usuario'):
        return jsonify({'error': 'No autorizado para ver este recurso.'}), 403

    ejercicio = Ejercicio.query.get(realizado.ejercicios_id)
    if not ejercicio:
        return jsonify({'error': f'El ejercicio con ID {realizado.ejercicios_id} no fue encontrado.'}), 404

    series = SerieRealizada.query.filter_by(entrenamientos_realizados_id=id).all()
    series_info = [{'id': s.id_series_realizadas, 'repeticiones': s.repeticiones, 'peso_kg': s.peso_kg} for s in series]

    return jsonify({
        'id_entrenamientos_realizados': realizado.id_entrenamientos_realizados,
        'entrenamientos_id': realizado.entrenamientos_id,
        'ejercicios_id': realizado.ejercicios_id,
        'ejercicio': {
            'id': ejercicio.id_ejercicios,
            'nombre': ejercicio.ejercicio_base.nombre,
            'descripcion': ejercicio.ejercicio_base.descripcion
        },
        'series_realizadas': series_info
    })



