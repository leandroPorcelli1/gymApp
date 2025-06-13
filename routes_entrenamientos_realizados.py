from flask import Blueprint, request, jsonify
from models import db, EntrenamientoRealizado

entrenamientos_realizados_bp = Blueprint('entrenamientos_realizados_bp', __name__)

@entrenamientos_realizados_bp.route('/entrenamientos_realizados', methods=['POST'])
def crear_entrenamiento_realizado():
    data = request.json
    entrenamiento_realizado = EntrenamientoRealizado(
        entrenamientos_id=data['entrenamientos_id'],
        ejercicios_id=data['ejercicios_id']
    )
    db.session.add(entrenamiento_realizado)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento realizado creado', 'id': entrenamiento_realizado.id_entrenamientos_realizados}), 201

@entrenamientos_realizados_bp.route('/entrenamientos_realizados', methods=['GET'])
def obtener_entrenamientos_realizados():
    realizados = EntrenamientoRealizado.query.all()
    return jsonify([{
        'id_entrenamientos_realizados': r.id_entrenamientos_realizados,
        'entrenamientos_id': r.entrenamientos_id,
        'ejercicios_id': r.ejercicios_id
    } for r in realizados])

@entrenamientos_realizados_bp.route('/entrenamientos_realizados/<int:id>', methods=['GET'])
def obtener_entrenamiento_realizado(id):
    realizado = EntrenamientoRealizado.query.get_or_404(id)
    return jsonify({
        'id_entrenamientos_realizados': realizado.id_entrenamientos_realizados,
        'entrenamientos_id': realizado.entrenamientos_id,
        'ejercicios_id': realizado.ejercicios_id
    })

@entrenamientos_realizados_bp.route('/entrenamientos_realizados/<int:id>', methods=['PUT'])
def actualizar_entrenamiento_realizado(id):
    realizado = EntrenamientoRealizado.query.get_or_404(id)
    data = request.json
    realizado.entrenamientos_id = data.get('entrenamientos_id', realizado.entrenamientos_id)
    realizado.ejercicios_id = data.get('ejercicios_id', realizado.ejercicios_id)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento realizado actualizado'})

@entrenamientos_realizados_bp.route('/entrenamientos_realizados/<int:id>', methods=['DELETE'])
def eliminar_entrenamiento_realizado(id):
    realizado = EntrenamientoRealizado.query.get_or_404(id)
    db.session.delete(realizado)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento realizado eliminado'}) 