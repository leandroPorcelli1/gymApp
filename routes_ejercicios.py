from flask import Blueprint, request, jsonify
from models import db, Ejercicio

ejercicios_bp = Blueprint('ejercicios_bp', __name__)

@ejercicios_bp.route('/ejercicios', methods=['POST'])
def crear_ejercicio():
    data = request.json
    ejercicio = Ejercicio(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        rutinas_id=data['rutinas_id']
    )
    db.session.add(ejercicio)
    db.session.commit()
    return jsonify({'mensaje': 'Ejercicio creado', 'id': ejercicio.id_ejercicios}), 201

@ejercicios_bp.route('/ejercicios/batch', methods=['POST'])
def crear_ejercicios_batch():
    data = request.json
    ejercicios_creados = []
    
    for ejercicio_data in data:
        ejercicio = Ejercicio(
            nombre=ejercicio_data['nombre'],
            descripcion=ejercicio_data.get('descripcion'),
            rutinas_id=ejercicio_data['rutinas_id']
        )
        db.session.add(ejercicio)
    
    # Hacer commit para obtener los IDs
    db.session.commit()
    
    # Obtener los ejercicios recién creados
    for ejercicio_data in data:
        ejercicio = Ejercicio.query.filter_by(
            nombre=ejercicio_data['nombre'],
            rutinas_id=ejercicio_data['rutinas_id']
        ).first()
        if ejercicio:
            ejercicios_creados.append({
                'id': ejercicio.id_ejercicios,
                'nombre': ejercicio.nombre,
                'descripcion': ejercicio.descripcion,
                'rutinas_id': ejercicio.rutinas_id
            })
    
    return jsonify({
        'mensaje': f'{len(ejercicios_creados)} ejercicios creados',
        'ejercicios': ejercicios_creados
    }), 201

@ejercicios_bp.route('/ejercicios', methods=['GET'])
def obtener_ejercicios():
    ejercicios = Ejercicio.query.all()
    return jsonify([{
        'id_ejercicios': e.id_ejercicios,
        'nombre': e.nombre,
        'descripcion': e.descripcion,
    } for e in ejercicios])

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['GET'])
def obtener_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    return jsonify({
        'id_ejercicios': ejercicio.id_ejercicios,
        'nombre': ejercicio.nombre,
        'descripcion': ejercicio.descripcion,
    })

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['PUT'])
def actualizar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    data = request.json
    ejercicio.nombre = data.get('nombre', ejercicio.nombre)
    ejercicio.descripcion = data.get('descripcion', ejercicio.descripcion)
    ejercicio.rutinas_id = data.get('rutinas_id', ejercicio.rutinas_id)
    db.session.commit()
    return jsonify({'mensaje': 'Ejercicio actualizado'})

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['DELETE'])
def eliminar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    db.session.delete(ejercicio)
    db.session.commit()
    return jsonify({'mensaje': 'Ejercicio eliminado'}) 