from flask import Blueprint, request, jsonify
from models import db, Rutina, Ejercicio, EjercicioBase

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
    rutinas_info = []
    
    for rutina in rutinas:
        # Obtener los ejercicios asociados a la rutina
        ejercicios = Ejercicio.query.filter_by(rutinas_id=rutina.id_rutinas).all()
        ejercicios_info = []
        
        for ejercicio in ejercicios:
            ejercicios_info.append({
                'id': ejercicio.id_ejercicios,
                'ejercicios_base_id': ejercicio.ejercicios_base_id,
                'nombre': ejercicio.ejercicio_base.nombre,
                'descripcion': ejercicio.ejercicio_base.descripcion
            })
        
        rutinas_info.append({
            'id_rutinas': rutina.id_rutinas,
            'nombre': rutina.nombre,
            'descripcion': rutina.descripcion,
            'usuarios_id': rutina.usuarios_id,
            'nivel_rutinas_id': rutina.nivel_rutinas_id,
            'ejercicios': ejercicios_info
        })
    
    return jsonify(rutinas_info)

@rutinas_bp.route('/rutinas/<int:id>', methods=['GET'])
def obtener_rutina(id):
    rutina = Rutina.query.get_or_404(id)
    
    # Obtener los ejercicios asociados a la rutina
    ejercicios = Ejercicio.query.filter_by(rutinas_id=id).all()
    ejercicios_info = []
    
    for ejercicio in ejercicios:
        ejercicios_info.append({
            'id': ejercicio.id_ejercicios,
            'ejercicios_base_id': ejercicio.ejercicios_base_id,
            'nombre': ejercicio.ejercicio_base.nombre,
            'descripcion': ejercicio.ejercicio_base.descripcion
        })
    
    return jsonify({
        'id_rutinas': rutina.id_rutinas,
        'nombre': rutina.nombre,
        'descripcion': rutina.descripcion,
        'usuarios_id': rutina.usuarios_id,
        'nivel_rutinas_id': rutina.nivel_rutinas_id,
        'ejercicios': ejercicios_info
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