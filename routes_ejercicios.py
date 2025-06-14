from flask import Blueprint, request, jsonify
from models import db, Ejercicio, EjercicioBase

ejercicios_bp = Blueprint('ejercicios_bp', __name__)

@ejercicios_bp.route('/ejercicios', methods=['POST'])
def crear_ejercicio():
    data = request.json
    ejercicio = Ejercicio(
        ejercicios_base_id=data['ejercicios_base_id'],
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
            ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
            rutinas_id=ejercicio_data['rutinas_id']
        )
        db.session.add(ejercicio)
    
    # Hacer commit para obtener los IDs
    db.session.commit()
    
    # Obtener los ejercicios recién creados
    for ejercicio_data in data:
        ejercicio = Ejercicio.query.filter_by(
            ejercicios_base_id=ejercicio_data['ejercicios_base_id'],
            rutinas_id=ejercicio_data['rutinas_id']
        ).first()
        if ejercicio:
            ejercicio_base = EjercicioBase.query.get(ejercicio.ejercicios_base_id)
            ejercicios_creados.append({
                'id': ejercicio.id_ejercicios,
                'nombre': ejercicio_base.nombre,
                'descripcion': ejercicio_base.descripcion,
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
        'ejercicios_base_id': e.ejercicios_base_id,
        'rutinas_id': e.rutinas_id,
        'nombre': e.ejercicio_base.nombre,
        'descripcion': e.ejercicio_base.descripcion
    } for e in ejercicios])

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['GET'])
def obtener_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    return jsonify({
        'id_ejercicios': ejercicio.id_ejercicios,
        'ejercicios_base_id': ejercicio.ejercicios_base_id,
        'rutinas_id': ejercicio.rutinas_id,
        'nombre': ejercicio.ejercicio_base.nombre,
        'descripcion': ejercicio.ejercicio_base.descripcion
    })

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['PUT'])
def actualizar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    data = request.json
    ejercicio.ejercicios_base_id = data.get('ejercicios_base_id', ejercicio.ejercicios_base_id)
    ejercicio.rutinas_id = data.get('rutinas_id', ejercicio.rutinas_id)
    db.session.commit()
    return jsonify({'mensaje': 'Ejercicio actualizado'})

@ejercicios_bp.route('/ejercicios/<int:id>', methods=['DELETE'])
def eliminar_ejercicio(id):
    ejercicio = Ejercicio.query.get_or_404(id)
    db.session.delete(ejercicio)
    db.session.commit()
    return jsonify({'mensaje': 'Ejercicio eliminado'})

@ejercicios_bp.route('/ejercicios-base', methods=['GET'])
def obtener_ejercicios_base():
    ejercicios = EjercicioBase.query.all()
    return jsonify([{
        'id_ejercicios_base': e.id_ejercicios_base,
        'nombre': e.nombre,
        'descripcion': e.descripcion
    } for e in ejercicios])

@ejercicios_bp.route('/ejercicios-base', methods=['POST'])
def crear_ejercicio_base():
    data = request.json
    if isinstance(data, list):
        ejercicios_creados = []
        for ejercicio_data in data:
            ejercicio = EjercicioBase(
                nombre=ejercicio_data['nombre'],
                descripcion=ejercicio_data.get('descripcion')
            )
            db.session.add(ejercicio)
            ejercicios_creados.append({
                'id': ejercicio.id_ejercicios_base,
                'nombre': ejercicio.nombre,
                'descripcion': ejercicio.descripcion
            })
        db.session.commit()
        return jsonify({
            'mensaje': f'{len(ejercicios_creados)} ejercicios base creados',
            'ejercicios': ejercicios_creados
        }), 201
    else:
        ejercicio = EjercicioBase(
            nombre=data['nombre'],
            descripcion=data.get('descripcion')
        )
        db.session.add(ejercicio)
        db.session.commit()
        return jsonify({
            'mensaje': 'Ejercicio base creado',
            'ejercicio': {
                'id': ejercicio.id_ejercicios_base,
                'nombre': ejercicio.nombre,
                'descripcion': ejercicio.descripcion
            }
        }), 201 