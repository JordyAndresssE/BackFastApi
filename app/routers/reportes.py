"""
Router de Reportes
Endpoints para generar dashboards, PDFs y Excel
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
from datetime import date
from ..schemas import (
    FiltrosReporteAsesorias, FiltrosReporteProyectos,
    DashboardAsesorias, DashboardProyectos, FormatoReporte
)
from ..services.report_service import ReportService
from ..utils.pdf_generator import PDFGenerator
from ..utils.excel_generator import ExcelGenerator
import os

router = APIRouter()

# Instanciar servicios
report_service = ReportService()
pdf_generator = PDFGenerator()
excel_generator = ExcelGenerator()


@router.get("/asesorias/dashboard", response_model=DashboardAsesorias)
async def obtener_dashboard_asesorias(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    id_programador: Optional[str] = None,
    estado: Optional[str] = None
):
    """
    Dashboard de asesorías con estadísticas y gráficos
    """
    try:
        filtros = FiltrosReporteAsesorias(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_programador=id_programador,
            estado=estado
        )
        
        dashboard = await report_service.generar_dashboard_asesorias(filtros)
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar dashboard: {str(e)}")


@router.get("/proyectos/dashboard", response_model=DashboardProyectos)
async def obtener_dashboard_proyectos(
    id_programador: Optional[str] = None,
    tipo: Optional[str] = None
):
    """
    Dashboard de proyectos con estadísticas
    """
    try:
        filtros = FiltrosReporteProyectos(
            id_programador=id_programador,
            tipo=tipo
        )
        
        dashboard = await report_service.generar_dashboard_proyectos(filtros)
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar dashboard: {str(e)}")


@router.get("/asesorias/pdf")
async def generar_pdf_asesorias(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    id_programador: Optional[str] = None,
    estado: Optional[str] = None
):
    """
    Generar reporte PDF de asesorías
    """
    try:
        # Obtener datos
        filtros = FiltrosReporteAsesorias(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            id_programador=id_programador,
            estado=estado,
            formato=FormatoReporte.PDF
        )
        
        datos = await report_service.obtener_datos_asesorias(filtros)
        
        # Generar PDF
        pdf_path = pdf_generator.generar_reporte_asesorias(datos, filtros)
        
        # Retornar archivo
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"reporte_asesorias_{date.today()}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")


@router.get("/proyectos/excel")
async def generar_excel_proyectos(
    id_programador: Optional[str] = None,
    tipo: Optional[str] = None
):
    """
    Generar reporte Excel de proyectos
    """
    try:
        # Obtener datos
        filtros = FiltrosReporteProyectos(
            id_programador=id_programador,
            tipo=tipo,
            formato=FormatoReporte.EXCEL
        )
        
        datos = await report_service.obtener_datos_proyectos(filtros)
        
        # Generar Excel
        excel_path = excel_generator.generar_reporte_proyectos(datos, filtros)
        
        # Retornar archivo
        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"reporte_proyectos_{date.today()}.xlsx"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar Excel: {str(e)}")


@router.get("/estadisticas")
async def obtener_estadisticas_generales():
    """
    Estadísticas generales de la plataforma
    """
    try:
        stats = await report_service.obtener_estadisticas_generales()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")