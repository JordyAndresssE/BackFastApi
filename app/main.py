"""
Capa de Presentacion - Punto de entrada de la API
Proyecto: Sistema de Portafolio de Programadores
Arquitectura: N Capas (Presentacion, Negocio, Datos)
Autor: Estudiante
Fecha: 2026
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .routers import notificaciones, reportes


# Inicializacion de la aplicacion FastAPI
app = FastAPI(
    title="Portafolio Devs - Notificaciones y Reportes API",
    description="Microservicio para notificaciones automatizadas y generacion de reportes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configuracion de CORS para permitir peticiones desde el frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:4200",
        "http://localhost:4201",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registro de routers (Capa de Presentacion)
app.include_router(
    notificaciones.router,
    prefix="/api/notificaciones",
    tags=["Notificaciones"]
)

app.include_router(
    reportes.router,
    prefix="/api/reportes",
    tags=["Reportes"]
)


# Endpoints de verificacion del sistema
@app.get("/")
async def root():
    """Endpoint principal - verificacion del estado del servicio"""
    return {
        "mensaje": "FastAPI Backend - Portafolio Devs",
        "version": "1.0.0",
        "estado": "activo",
        "microservicios": {
            "spring_boot": settings.spring_boot_url,
            "jakarta_ee": settings.jakarta_ee_url
        },
        "documentacion": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar que el servicio esta funcionando"""
    return {
        "status": "healthy",
        "service": "notificaciones-reportes",
        "timestamp": "2026-02-01T00:00:00Z"
    }


# Manejadores de excepciones globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador para excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador para excepciones generales del sistema"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detalle": str(exc) if settings.debug else "Error no especificado"
        }
    )


# Ejecucion directa del servidor (desarrollo)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.debug
    )