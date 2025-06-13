from flask import Blueprint, request, jsonify
from models import db, NivelRutina

nivel_rutinas_bp = Blueprint('nivel_rutinas_bp', __name__)

@nivel_rutinas_bp.route('/nivel_rutinas', methods=['POST'])
def crear_nivel_rutina():
    data = request.json
    nivel = NivelRutina(
        nivel=data['nivel']
    )
    db.session.add(nivel)
    db.session.commit()
    return jsonify({'mensaje': 'Nivel de rutina creado', 'id': nivel.id_nivel_rutinas}), 201

@nivel_rutinas_bp.route('/nivel_rutinas', methods=['GET'])
def obtener_niveles_rutina():
    niveles = NivelRutina.query.all()
    return jsonify([{
        'id_nivel_rutinas': n.id_nivel_rutinas,
        'nivel': n.nivel
    } for n in niveles])

@nivel_rutinas_bp.route('/nivel_rutinas/<int:id>', methods=['GET'])
def obtener_nivel_rutina(id):
    nivel = NivelRutina.query.get_or_404(id)
    return jsonify({
        'id_nivel_rutinas': nivel.id_nivel_rutinas,
        'nivel': nivel.nivel
    })

@nivel_rutinas_bp.route('/nivel_rutinas/<int:id>', methods=['PUT'])
def actualizar_nivel_rutina(id):
    nivel = NivelRutina.query.get_or_404(id)
    data = request.json
    nivel.nivel = data.get('nivel', nivel.nivel)
    db.session.commit()
    return jsonify({'mensaje': 'Nivel de rutina actualizado'})

@nivel_rutinas_bp.route('/nivel_rutinas/<int:id>', methods=['DELETE'])
def eliminar_nivel_rutina(id):
    nivel = NivelRutina.query.get_or_404(id)
    db.session.delete(nivel)
    db.session.commit()
    return jsonify({'mensaje': 'Nivel de rutina eliminado'}) 