from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuarios = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String, nullable=True)
    google_id = db.Column(db.String, nullable=True, unique=True)
    auth_provider = db.Column(db.String, nullable=False, default='local')

    rutinas = db.relationship('Rutina', backref='usuario', cascade="all, delete-orphan")
    entrenamientos = db.relationship('Entrenamiento', backref='usuario', cascade="all, delete-orphan")

class Rutina(db.Model):
    __tablename__ = 'rutinas'
    id_rutinas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False, unique=True)
    descripcion = db.Column(db.String)
    usuarios_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuarios', ondelete='CASCADE'), nullable=False)
    nivel_rutinas_id = db.Column(db.Integer, db.ForeignKey('nivel_rutinas.id_nivel_rutinas', ondelete='RESTRICT'), nullable=False)

    ejercicios = db.relationship('Ejercicio', backref='rutina', cascade="all, delete-orphan")
    entrenamientos = db.relationship('Entrenamiento', backref='rutina', cascade="all, delete-orphan")

class NivelRutina(db.Model):
    __tablename__ = 'nivel_rutinas'
    id_nivel_rutinas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nivel = db.Column(db.String, nullable=False, unique=True)

    rutinas = db.relationship('Rutina', backref='nivel', cascade="all, delete-orphan")

class Ejercicio(db.Model):
    __tablename__ = 'ejercicios'
    id_ejercicios = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.String)
    rutinas_id = db.Column(db.Integer, db.ForeignKey('rutinas.id_rutinas', ondelete='CASCADE'), nullable=False)

    series = db.relationship('Serie', backref='ejercicio', cascade="all, delete-orphan")

class Entrenamiento(db.Model):
    __tablename__ = 'entrenamientos'
    id_entrenamientos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    usuarios_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuarios', ondelete='CASCADE'), nullable=False)
    rutinas_id = db.Column(db.Integer, db.ForeignKey('rutinas.id_rutinas', ondelete='RESTRICT'), nullable=False)

    realizados = db.relationship('EntrenamientoRealizado', backref='entrenamiento', cascade="all, delete-orphan")

class EntrenamientoRealizado(db.Model):
    __tablename__ = 'entrenamientos_realizados'
    id_entrenamientos_realizados = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entrenamientos_id = db.Column(db.Integer, db.ForeignKey('entrenamientos.id_entrenamientos', ondelete='CASCADE'), nullable=False)
    ejercicios_id = db.Column(db.Integer, db.ForeignKey('ejercicios.id_ejercicios', ondelete='CASCADE'), nullable=False)

    series_realizadas = db.relationship('SerieRealizada', backref='entrenamiento_realizado', cascade="all, delete-orphan")

class Serie(db.Model):
    __tablename__ = 'series'
    id_series = db.Column(db.Integer, primary_key=True, autoincrement=True)
    repeticiones = db.Column(db.Integer, nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)
    ejercicios_id = db.Column(db.Integer, db.ForeignKey('ejercicios.id_ejercicios', ondelete='CASCADE'), nullable=False)

class SerieRealizada(db.Model):
    __tablename__ = 'series_realizadas'
    id_series_realizadas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entrenamientos_realizados_id = db.Column(db.Integer, db.ForeignKey('entrenamientos_realizados.id_entrenamientos_realizados', ondelete='CASCADE'), nullable=False)
    repeticiones = db.Column(db.Integer, nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)