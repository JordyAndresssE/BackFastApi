"""
Conexión a MySQL - Base de datos portafolio_programadores (compartida)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Crear engine con la configuración exacta
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,       # Verifica conexiones antes de usar
    pool_recycle=3600,        # Recicla conexiones cada hora
    pool_size=10,             # Mantener 10 conexiones abiertas
    max_overflow=20,          # Hasta 20 conexiones adicionales
    echo=settings.debug,      # Log de queries en modo debug
    connect_args={
        "charset": "utf8mb4"  # Soporte completo de caracteres
    }
)

# Sesión para hacer queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()


# Dependency para inyectar sesión en endpoints
def get_db():
    """
    Dependency para obtener sesión de base de datos
    
    Uso en endpoints:
    @router.get("/test")
    def test(db: Session = Depends(get_db)):
        usuarios = db.query(Usuario).all()
        return usuarios
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función de prueba de conexión
def test_connection():
    """Probar conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("✅ Conexión a MySQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return False