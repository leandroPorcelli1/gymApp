from flask import Blueprint, request, jsonify
from models import db, SerieRealizada

series_realizadas_bp = Blueprint('series_realizadas_bp', __name__)

@series_realizadas_bp.route('/series_realizadas', methods=['POST'])
def crear_serie_realizada():
    data = request.json
    serie_realizada = SerieRealizada(
        entrenamientos_realizados_id=data['entrenamientos_realizados_id'],
        repeticiones=data['repeticiones'],
        peso_kg=data['peso_kg']
    )
    db.session.add(serie_realizada)
    db.session.commit()
    return jsonify({'mensaje': 'Serie realizada creada', 'id': serie_realizada.id_series_realizadas}), 201

@series_realizadas_bp.route('/series_realizadas', methods=['GET'])
def obtener_series_realizadas():
    series = SerieRealizada.query.all()
    return jsonify([{
        'id_series_realizadas': s.id_series_realizadas,
        'entrenamientos_realizados_id': s.entrenamientos_realizados_id,
        'repeticiones': s.repeticiones,
        'peso_kg': s.peso_kg
    } for s in series])

@series_realizadas_bp.route('/series_realizadas/<int:id>', methods=['GET'])
def obtener_serie_realizada(id):
    serie = SerieRealizada.query.get_or_404(id)
    return jsonify({
        'id_series_realizadas': serie.id_series_realizadas,
        'entrenamientos_realizados_id': serie.entrenamientos_realizados_id,
        'repeticiones': serie.repeticiones,
        'peso_kg': serie.peso_kg
    })

@series_realizadas_bp.route('/series_realizadas/<int:id>', methods=['PUT'])
def actualizar_serie_realizada(id):
    serie = SerieRealizada.query.get_or_404(id)
    data = request.json
    serie.entrenamientos_realizados_id = data.get('entrenamientos_realizados_id', serie.entrenamientos_realizados_id)
    serie.repeticiones = data.get('repeticiones', serie.repeticiones)
    serie.peso_kg = data.get('peso_kg', serie.peso_kg)
    db.session.commit()
    return jsonify({'mensaje': 'Serie realizada actualizada'})

@series_realizadas_bp.route('/series_realizadas/<int:id>', methods=['DELETE'])
def eliminar_serie_realizada(id):
    serie = SerieRealizada.query.get_or_404(id)
    db.session.delete(serie)
    db.session.commit()
    return jsonify({'mensaje': 'Serie realizada eliminada'}) 