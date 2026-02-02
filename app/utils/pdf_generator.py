"""
Generador de PDFs
Crea reportes en PDF usando ReportLab
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date
import os
from typing import List, Dict
from ..schemas import FiltrosReporteAsesorias


class PDFGenerator:
    """Generador de reportes PDF"""
    
    def __init__(self):
        # Crear carpeta para reportes si no existe
        self.output_dir = "reportes_pdf"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generar_reporte_asesorias(
        self,
        datos: List[Dict],
        filtros: FiltrosReporteAsesorias
    ) -> str:
        """
        Generar PDF de reporte de asesorías
        
        Returns:
            Path del PDF generado
        """
        # Nombre del archivo
        filename = f"reporte_asesorias_{date.today()}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#A10000'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        # Título
        story.append(Paragraph("📊 Reporte de Asesorías", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Información del reporte
        info_style = styles['Normal']
        story.append(Paragraph(f"<b>Fecha de generación:</b> {date.today()}", info_style))
        
        if filtros.fecha_inicio:
            story.append(Paragraph(f"<b>Desde:</b> {filtros.fecha_inicio}", info_style))
        if filtros.fecha_fin:
            story.append(Paragraph(f"<b>Hasta:</b> {filtros.fecha_fin}", info_style))
        if filtros.id_programador:
            story.append(Paragraph(f"<b>Programador:</b> {filtros.id_programador}", info_style))
        if filtros.estado:
            story.append(Paragraph(f"<b>Estado:</b> {filtros.estado.value}", info_style))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Estadísticas generales
        total = len(datos)
        pendientes = len([d for d in datos if d.get('estado') == 'pendiente'])
        aprobadas = len([d for d in datos if d.get('estado') == 'aprobada'])
        rechazadas = len([d for d in datos if d.get('estado') == 'rechazada'])
        
        stats_data = [
            ['📊 Estadísticas', ''],
            ['Total de asesorías', str(total)],
            ['Pendientes', str(pendientes)],
            ['Aprobadas', str(aprobadas)],
            ['Rechazadas', str(rechazadas)]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A10000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Tabla de asesorías
        if datos:
            story.append(Paragraph("<b>📋 Detalle de Asesorías</b>", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            # Encabezados
            table_data = [['ID', 'Usuario', 'Fecha', 'Hora', 'Estado']]
            
            # Datos
            for asesoria in datos[:50]:  # Limitar a 50 registros
                table_data.append([
                    asesoria.get('id', 'N/A')[:10],
                    asesoria.get('nombreUsuario', 'N/A')[:20],
                    asesoria.get('fechaAsesoria', 'N/A'),
                    asesoria.get('horaAsesoria', 'N/A'),
                    asesoria.get('estado', 'N/A')
                ])
            
            detail_table = Table(table_data, colWidths=[1*inch, 2*inch, 1.2*inch, 1*inch, 1*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(detail_table)
        
        # Footer
        story.append(Spacer(1, 1*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Generado por Portafolio Devs - Sistema de Reportes", footer_style))
        
        # Generar PDF
        doc.build(story)
        print(f"✅ PDF generado: {filepath}")
        
        return filepath