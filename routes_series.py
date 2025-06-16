from flask import Blueprint, request, jsonify
from models import db, Serie, Ejercicio, EjercicioBase

series_bp = Blueprint('series_bp', __name__)

@series_bp.route('/series', methods=['POST'])
def crear_serie():
    data = request.json
    serie = Serie(
        repeticiones=data['repeticiones'],
        peso_kg=data['peso_kg'],
        ejercicios_id=data['ejercicios_id']
    )
    db.session.add(serie)
    db.session.commit()
    return jsonify({'mensaje': 'Serie creada', 'id': serie.id_series}), 201

@series_bp.route('/series', methods=['GET'])
def obtener_series():
    series = Serie.query.all()
    return jsonify([{
        'id_series': s.id_series,
        'repeticiones': s.repeticiones,
        'peso_kg': s.peso_kg,
        'ejercicios_id': s.ejercicios_id,
        'ejercicio': {
            'id': s.ejercicio.id_ejercicios,
            'nombre': s.ejercicio.ejercicio_base.nombre,
            'descripcion': s.ejercicio.ejercicio_base.descripcion
        }
    } for s in series])

@series_bp.route('/series/<int:id>', methods=['GET'])
def obtener_serie(id):
    serie = Serie.query.get_or_404(id)
    return jsonify({
        'id_series': serie.id_series,
        'repeticiones': serie.repeticiones,
        'peso_kg': serie.peso_kg,
        'ejercicios_id': serie.ejercicios_id,
        'ejercicio': {
            'id': serie.ejercicio.id_ejercicios,
            'nombre': serie.ejercicio.ejercicio_base.nombre,
            'descripcion': serie.ejercicio.ejercicio_base.descripcion
        }
    })

@series_bp.route('/series/<int:id>', methods=['PUT'])
def actualizar_serie(id):
    serie = Serie.query.get_or_404(id)
    data = request.json
    serie.repeticiones = data.get('repeticiones', serie.repeticiones)
    serie.peso_kg = data.get('peso_kg', serie.peso_kg)
    serie.ejercicios_id = data.get('ejercicios_id', serie.ejercicios_id)
    db.session.commit()
    return jsonify({'mensaje': 'Serie actualizada'})

@series_bp.route('/series/<int:id>', methods=['DELETE'])
def eliminar_serie(id):
    serie = Serie.query.get_or_404(id)
    db.session.delete(serie)
    db.session.commit()
    return jsonify({'mensaje': 'Serie eliminada'}) 