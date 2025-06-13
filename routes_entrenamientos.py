from flask import Blueprint, request, jsonify
from models import db, Entrenamiento

entrenamientos_bp = Blueprint('entrenamientos_bp', __name__)

@entrenamientos_bp.route('/entrenamientos', methods=['POST'])
def crear_entrenamiento():
    data = request.json
    entrenamiento = Entrenamiento(
        fecha=data['fecha'],
        usuarios_id=data['usuarios_id'],
        rutinas_id=data['rutinas_id']
    )
    db.session.add(entrenamiento)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento creado', 'id': entrenamiento.id_entrenamientos}), 201

@entrenamientos_bp.route('/entrenamientos', methods=['GET'])
def obtener_entrenamientos():
    entrenamientos = Entrenamiento.query.all()
    return jsonify([{
        'id_entrenamientos': e.id_entrenamientos,
        'fecha': str(e.fecha),
        'usuarios_id': e.usuarios_id,
        'rutinas_id': e.rutinas_id
    } for e in entrenamientos])

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['GET'])
def obtener_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    return jsonify({
        'id_entrenamientos': entrenamiento.id_entrenamientos,
        'fecha': str(entrenamiento.fecha),
        'usuarios_id': entrenamiento.usuarios_id,
        'rutinas_id': entrenamiento.rutinas_id
    })

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['PUT'])
def actualizar_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    data = request.json
    entrenamiento.fecha = data.get('fecha', entrenamiento.fecha)
    entrenamiento.usuarios_id = data.get('usuarios_id', entrenamiento.usuarios_id)
    entrenamiento.rutinas_id = data.get('rutinas_id', entrenamiento.rutinas_id)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento actualizado'})

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['DELETE'])
def eliminar_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    db.session.delete(entrenamiento)
    db.session.commit()
    return jsonify({'mensaje': 'Entrenamiento eliminado'}) 