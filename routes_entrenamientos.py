from flask import Blueprint, request, jsonify
from models import db, Entrenamiento, Rutina, EntrenamientoRealizado, Ejercicio, EjercicioBase, SerieRealizada

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
    
    return jsonify({
        'mensaje': 'Entrenamiento creado',
        'entrenamiento': {
            'id_entrenamientos': entrenamiento.id_entrenamientos,
            'fecha': str(entrenamiento.fecha),
            'usuarios_id': entrenamiento.usuarios_id,
            'rutinas_id': entrenamiento.rutinas_id,
            'rutina': {
                'id': entrenamiento.rutina.id_rutinas,
                'nombre': entrenamiento.rutina.nombre,
                'descripcion': entrenamiento.rutina.descripcion
            },
            'ejercicios_realizados': []
        }
    }), 201

@entrenamientos_bp.route('/entrenamientos', methods=['GET'])
def obtener_entrenamientos():
    entrenamientos = Entrenamiento.query.all()
    entrenamientos_info = []
    
    for entrenamiento in entrenamientos:
        # Obtener los ejercicios realizados
        ejercicios_realizados = EntrenamientoRealizado.query.filter_by(entrenamientos_id=entrenamiento.id_entrenamientos).all()
        ejercicios_info = []
        
        for realizado in ejercicios_realizados:
            # Obtener las series realizadas
            series = SerieRealizada.query.filter_by(entrenamientos_realizados_id=realizado.id_entrenamientos_realizados).all()
            series_info = [{
                'id': serie.id_series_realizadas,
                'repeticiones': serie.repeticiones,
                'peso_kg': serie.peso_kg
            } for serie in series]
            
            ejercicios_info.append({
                'id': realizado.ejercicio.id_ejercicios,
                'nombre': realizado.ejercicio.ejercicio_base.nombre,
                'descripcion': realizado.ejercicio.ejercicio_base.descripcion,
                'series_realizadas': series_info
            })
        
        entrenamientos_info.append({
            'id_entrenamientos': entrenamiento.id_entrenamientos,
            'fecha': str(entrenamiento.fecha),
            'usuarios_id': entrenamiento.usuarios_id,
            'rutinas_id': entrenamiento.rutinas_id,
            'rutina': {
                'id': entrenamiento.rutina.id_rutinas,
                'nombre': entrenamiento.rutina.nombre,
                'descripcion': entrenamiento.rutina.descripcion
            },
            'ejercicios_realizados': ejercicios_info
        })
    
    return jsonify(entrenamientos_info)

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['GET'])
def obtener_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    
    # Obtener los ejercicios realizados
    ejercicios_realizados = EntrenamientoRealizado.query.filter_by(entrenamientos_id=id).all()
    ejercicios_info = []
    
    for realizado in ejercicios_realizados:
        # Obtener las series realizadas
        series = SerieRealizada.query.filter_by(entrenamientos_realizados_id=realizado.id_entrenamientos_realizados).all()
        series_info = [{
            'id': serie.id_series_realizadas,
            'repeticiones': serie.repeticiones,
            'peso_kg': serie.peso_kg
        } for serie in series]
        
        ejercicios_info.append({
            'id': realizado.ejercicio.id_ejercicios,
            'nombre': realizado.ejercicio.ejercicio_base.nombre,
            'descripcion': realizado.ejercicio.ejercicio_base.descripcion,
            'series_realizadas': series_info
        })
    
    return jsonify({
        'id_entrenamientos': entrenamiento.id_entrenamientos,
        'fecha': str(entrenamiento.fecha),
        'usuarios_id': entrenamiento.usuarios_id,
        'rutinas_id': entrenamiento.rutinas_id,
        'rutina': {
            'id': entrenamiento.rutina.id_rutinas,
            'nombre': entrenamiento.rutina.nombre,
            'descripcion': entrenamiento.rutina.descripcion
        },
        'ejercicios_realizados': ejercicios_info
    })

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['PUT'])
def actualizar_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    data = request.json
    entrenamiento.fecha = data.get('fecha', entrenamiento.fecha)
    entrenamiento.usuarios_id = data.get('usuarios_id', entrenamiento.usuarios_id)
    entrenamiento.rutinas_id = data.get('rutinas_id', entrenamiento.rutinas_id)
    db.session.commit()
    
    # Obtener los ejercicios realizados
    ejercicios_realizados = EntrenamientoRealizado.query.filter_by(entrenamientos_id=id).all()
    ejercicios_info = []
    
    for realizado in ejercicios_realizados:
        # Obtener las series realizadas
        series = SerieRealizada.query.filter_by(entrenamientos_realizados_id=realizado.id_entrenamientos_realizados).all()
        series_info = [{
            'id': serie.id_series_realizadas,
            'repeticiones': serie.repeticiones,
            'peso_kg': serie.peso_kg
        } for serie in series]
        
        ejercicios_info.append({
            'id': realizado.ejercicio.id_ejercicios,
            'nombre': realizado.ejercicio.ejercicio_base.nombre,
            'descripcion': realizado.ejercicio.ejercicio_base.descripcion,
            'series_realizadas': series_info
        })
    
    return jsonify({
        'mensaje': 'Entrenamiento actualizado',
        'entrenamiento': {
            'id_entrenamientos': entrenamiento.id_entrenamientos,
            'fecha': str(entrenamiento.fecha),
            'usuarios_id': entrenamiento.usuarios_id,
            'rutinas_id': entrenamiento.rutinas_id,
            'rutina': {
                'id': entrenamiento.rutina.id_rutinas,
                'nombre': entrenamiento.rutina.nombre,
                'descripcion': entrenamiento.rutina.descripcion
            },
            'ejercicios_realizados': ejercicios_info
        }
    })

@entrenamientos_bp.route('/entrenamientos/<int:id>', methods=['DELETE'])
def eliminar_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get_or_404(id)
    
    # Guardar la información antes de eliminar
    entrenamiento_info = {
        'id_entrenamientos': entrenamiento.id_entrenamientos,
        'fecha': str(entrenamiento.fecha),
        'usuarios_id': entrenamiento.usuarios_id,
        'rutinas_id': entrenamiento.rutinas_id,
        'rutina': {
            'id': entrenamiento.rutina.id_rutinas,
            'nombre': entrenamiento.rutina.nombre,
            'descripcion': entrenamiento.rutina.descripcion
        }
    }
    
    db.session.delete(entrenamiento)
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Entrenamiento eliminado',
        'entrenamiento': entrenamiento_info
    }) 