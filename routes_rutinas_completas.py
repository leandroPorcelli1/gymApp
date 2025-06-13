from flask import Blueprint, request, jsonify
from models import db, Rutina, Ejercicio, Serie

rutinas_completas_bp = Blueprint('rutinas_completas_bp', __name__)

@rutinas_completas_bp.route('/rutinas/completas', methods=['POST'])
def crear_rutina_completa():
    try:
        data = request.json
        
        # Crear la rutina
        rutina = Rutina(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            usuarios_id=data['usuarios_id'],
            nivel_rutinas_id=data['nivel_rutinas_id']
        )
        db.session.add(rutina)
        db.session.flush()  # Para obtener el ID de la rutina sin hacer commit
        
        # Crear los ejercicios y sus series
        ejercicios_creados = []
        for ejercicio_data in data['ejercicios']:
            ejercicio = Ejercicio(
                nombre=ejercicio_data['nombre'],
                descripcion=ejercicio_data.get('descripcion'),
                rutinas_id=rutina.id_rutinas
            )
            db.session.add(ejercicio)
            db.session.flush()  # Para obtener el ID del ejercicio
            
            # Crear las series para este ejercicio
            series_creadas = []
            for serie_data in ejercicio_data['series']:
                serie = Serie(
                    repeticiones=serie_data['repeticiones'],
                    peso_kg=serie_data['peso_kg'],
                    ejercicios_id=ejercicio.id_ejercicios
                )
                db.session.add(serie)
                series_creadas.append({
                    'id': serie.id_series,
                    'repeticiones': serie.repeticiones,
                    'peso_kg': serie.peso_kg
                })
            
            ejercicios_creados.append({
                'id': ejercicio.id_ejercicios,
                'nombre': ejercicio.nombre,
                'descripcion': ejercicio.descripcion,
                'series': series_creadas
            })
        
        # Hacer commit de todos los cambios
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Rutina completa creada exitosamente',
            'rutina': {
                'id': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'ejercicios': ejercicios_creados
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al crear la rutina completa',
            'detalle': str(e)
        }), 400 

@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['GET'])
def obtener_rutina_completa(id):
    try:
        # Obtener la rutina
        rutina = Rutina.query.get_or_404(id)
        
        # Obtener todos los ejercicios de la rutina
        ejercicios = Ejercicio.query.filter_by(rutinas_id=id).all()
        
        ejercicios_completos = []
        for ejercicio in ejercicios:
            # Obtener todas las series del ejercicio
            series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
            
            ejercicios_completos.append({
                'id': ejercicio.id_ejercicios,
                'nombre': ejercicio.nombre,
                'descripcion': ejercicio.descripcion,
                'series': [{
                    'id': serie.id_series,
                    'repeticiones': serie.repeticiones,
                    'peso_kg': serie.peso_kg
                } for serie in series]
            })
        
        return jsonify({
            'id': rutina.id_rutinas,
            'nombre': rutina.nombre,
            'descripcion': rutina.descripcion,
            'usuarios_id': rutina.usuarios_id,
            'nivel_rutinas_id': rutina.nivel_rutinas_id,
            'ejercicios': ejercicios_completos
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener la rutina completa',
            'detalle': str(e)
        }), 400 

@rutinas_completas_bp.route('/rutinas/completas', methods=['GET'])
def obtener_todas_rutinas_completas():
    try:
        # Obtener todas las rutinas
        rutinas = Rutina.query.all()
        
        rutinas_completas = []
        for rutina in rutinas:
            # Obtener todos los ejercicios de la rutina
            ejercicios = Ejercicio.query.filter_by(rutinas_id=rutina.id_rutinas).all()
            
            ejercicios_completos = []
            for ejercicio in ejercicios:
                # Obtener todas las series del ejercicio
                series = Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).all()
                
                ejercicios_completos.append({
                    'id': ejercicio.id_ejercicios,
                    'nombre': ejercicio.nombre,
                    'descripcion': ejercicio.descripcion,
                    'series': [{
                        'id': serie.id_series,
                        'repeticiones': serie.repeticiones,
                        'peso_kg': serie.peso_kg
                    } for serie in series]
                })
            
            rutinas_completas.append({
                'id': rutina.id_rutinas,
                'nombre': rutina.nombre,
                'descripcion': rutina.descripcion,
                'usuarios_id': rutina.usuarios_id,
                'nivel_rutinas_id': rutina.nivel_rutinas_id,
                'ejercicios': ejercicios_completos
            })
        
        return jsonify(rutinas_completas)
        
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener las rutinas completas',
            'detalle': str(e)
        }), 400 

@rutinas_completas_bp.route('/rutinas/completas/<int:id>', methods=['DELETE'])
def eliminar_rutina_completa(id):
    try:
        # Obtener la rutina
        rutina = Rutina.query.get_or_404(id)
        
        # Eliminar todos los ejercicios asociados a la rutina
        ejercicios = Ejercicio.query.filter_by(rutinas_id=id).all()
        for ejercicio in ejercicios:
            # Eliminar todas las series asociadas al ejercicio
            Serie.query.filter_by(ejercicios_id=ejercicio.id_ejercicios).delete()
            db.session.delete(ejercicio)
        
        # Eliminar la rutina
        db.session.delete(rutina)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Rutina completa eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al eliminar la rutina completa',
            'detalle': str(e)
        }), 400 