from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .routers import notificaciones, reportes

# Inicializar FastAPI
app = FastAPI(
    title="Portafolio Devs - Notificaciones & Reportes API",
    description="Microservicio para notificaciones automatizadas y generación de reportes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:4200",
        "http://localhost:4201",
        "*"  # En producción cambiar por dominios específicos
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
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


# ==========================================
# ENDPOINTS PRINCIPALES
# ==========================================

@app.get("/")
async def root():
    """Endpoint raíz - Health check"""
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
    """Health check del servicio"""
    return {
        "status": "healthy",
        "service": "notificaciones-reportes",
        "timestamp": "2026-02-01T00:00:00Z"
    }


# ==========================================
# MANEJADORES DE ERRORES
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador de excepciones generales"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detalle": str(exc) if settings.debug else "Error no especificado"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.debug
    )