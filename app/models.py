"""
Modelos SQLAlchemy que mapean las tablas EXISTENTES en portafolio_programadores
IMPORTANTE: Solo LEEN las tablas, NO las crean (Spring Boot ya las crea)
"""
from sqlalchemy import Column, String, Integer, Text, Date, Time, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


# ==========================================
# TABLA: usuarios (Creada por Spring Boot)
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"
    
    uid = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    foto_perfil = Column(String(500))
    rol = Column(String(50), nullable=False)
    
    # Campos de programadores
    especialidad = Column(String(255))
    descripcion = Column(Text)
    tecnologias = Column(Text)  # Separado por comas o JSON
    
    # Redes sociales (ajusta según tus columnas reales)
    linkedin = Column(String(255))
    github = Column(String(255))
    twitter = Column(String(255))
    sitio_web = Column(String(255))
    
    # Disponibilidad (ajusta según tu estructura)
    # disponibilidad = Column(Text)  # Si es JSON


# ==========================================
# TABLA: proyectos (Creada por Spring Boot)
# ==========================================
class Proyecto(Base):
    __tablename__ = "proyectos"
    
    id = Column(String(50), primary_key=True)
    id_programador = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(50))  # academico, laboral
    participacion = Column(String(50))
    tecnologias = Column(Text)
    repo_url = Column(String(500))
    demo_url = Column(String(500))
    imagen_url = Column(String(500))


# ==========================================
# TABLA: asesorias (Creada por Jakarta EE)
# ==========================================
class Asesoria(Base):
    __tablename__ = "asesorias"
    
    id = Column(String(50), primary_key=True)
    id_programador = Column(String(255), nullable=False)
    id_usuario = Column(String(255), nullable=False)
    nombre_usuario = Column(String(255))
    email_usuario = Column(String(255))
    fecha_solicitud = Column(DateTime)
    fecha_asesoria = Column(Date)
    hora_asesoria = Column(Time)
    motivo = Column(Text)
    estado = Column(String(50))  # pendiente, aprobada, rechazada, cancelada
    mensaje_respuesta = Column(Text)
    motivo_cancelacion = Column(Text)
    fecha_cancelacion = Column(DateTime)