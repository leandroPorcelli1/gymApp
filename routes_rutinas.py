from flask import Blueprint, request, jsonify
from models import db, Rutina

rutinas_bp = Blueprint('rutinas_bp', __name__)

@rutinas_bp.route('/rutinas', methods=['POST'])
def crear_rutina():
    data = request.json
    rutina = Rutina(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        usuarios_id=data['usuarios_id'],
        nivel_rutinas_id=data['nivel_rutinas_id']
    )
    db.session.add(rutina)
    db.session.commit()
    return jsonify({'mensaje': 'Rutina creada', 'id': rutina.id_rutinas}), 201

@rutinas_bp.route('/rutinas', methods=['GET'])
def obtener_rutinas():
    rutinas = Rutina.query.all()
    return jsonify([{
        'id_rutinas': r.id_rutinas,
        'nombre': r.nombre,
        'descripcion': r.descripcion,
        'usuarios_id': r.usuarios_id,
        'nivel_rutinas_id': r.nivel_rutinas_id
    } for r in rutinas])

@rutinas_bp.route('/rutinas/<int:id>', methods=['GET'])
def obtener_rutina(id):
    rutina = Rutina.query.get_or_404(id)
    return jsonify({
        'id_rutinas': rutina.id_rutinas,
        'nombre': rutina.nombre,
        'descripcion': rutina.descripcion,
        'usuarios_id': rutina.usuarios_id,
        'nivel_rutinas_id': rutina.nivel_rutinas_id
    })

@rutinas_bp.route('/rutinas/<int:id>', methods=['PUT'])
def actualizar_rutina(id):
    rutina = Rutina.query.get_or_404(id)
    data = request.json
    rutina.nombre = data.get('nombre', rutina.nombre)
    rutina.descripcion = data.get('descripcion', rutina.descripcion)
    rutina.usuarios_id = data.get('usuarios_id', rutina.usuarios_id)
    rutina.nivel_rutinas_id = data.get('nivel_rutinas_id', rutina.nivel_rutinas_id)
    db.session.commit()
    return jsonify({'mensaje': 'Rutina actualizada'})

@rutinas_bp.route('/rutinas/<int:id>', methods=['DELETE'])
def eliminar_rutina(id):
    rutina = Rutina.query.get_or_404(id)
    db.session.delete(rutina)
    db.session.commit()
    return jsonify({'mensaje': 'Rutina eliminada'}) 