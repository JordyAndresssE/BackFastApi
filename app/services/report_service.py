"""
Servicio de Reportes
Genera dashboards consultando Spring Boot y Jakarta EE
"""
import httpx
from typing import Dict, List
from datetime import date, datetime
from ..config import settings
from ..schemas import (
    FiltrosReporteAsesorias, FiltrosReporteProyectos,
    DashboardAsesorias, DashboardProyectos,
    EstadisticaAsesoria, EstadisticaProyecto
)


class ReportService:
    """Servicio para generar reportes y dashboards"""
    
    def __init__(self):
        self.spring_url = settings.spring_boot_url
        self.jakarta_url = settings.jakarta_ee_url
    
    async def generar_dashboard_asesorias(self, filtros: FiltrosReporteAsesorias) -> DashboardAsesorias:
        """
        Generar dashboard de asesorías consultando Jakarta EE
        """
        try:
            # Consultar asesorías desde Jakarta
            asesorias = await self._obtener_asesorias_jakarta(filtros)
            
            # Calcular estadísticas
            total = len(asesorias)
            pendientes = len([a for a in asesorias if a.get('estado') == 'pendiente'])
            aprobadas = len([a for a in asesorias if a.get('estado') == 'aprobada'])
            rechazadas = len([a for a in asesorias if a.get('estado') == 'rechazada'])
            canceladas = len([a for a in asesorias if a.get('estado') == 'cancelada'])
            
            estadisticas = EstadisticaAsesoria(
                total=total,
                pendientes=pendientes,
                aprobadas=aprobadas,
                rechazadas=rechazadas,
                canceladas=canceladas
            )
            
            # Asesorías recientes (últimas 10)
            asesorias_recientes = sorted(
                asesorias,
                key=lambda x: x.get('fechaSolicitud', ''),
                reverse=True
            )[:10]
            
            # Agrupar por programador
            por_programador = self._agrupar_por_programador(asesorias)
            
            # Agrupar por fecha
            por_fecha = self._agrupar_por_fecha(asesorias)
            
            return DashboardAsesorias(
                estadisticas=estadisticas,
                asesorias_recientes=asesorias_recientes,
                por_programador=por_programador,
                por_fecha=por_fecha
            )
            
        except Exception as e:
            print(f"❌ Error al generar dashboard asesorías: {str(e)}")
            raise
    
    async def generar_dashboard_proyectos(self, filtros: FiltrosReporteProyectos) -> DashboardProyectos:
        """
        Generar dashboard de proyectos consultando Spring Boot
        """
        try:
            # Consultar proyectos desde Spring Boot
            proyectos = await self._obtener_proyectos_spring(filtros)
            
            # Calcular estadísticas
            total = len(proyectos)
            academicos = len([p for p in proyectos if p.get('tipo') == 'academico'])
            laborales = len([p for p in proyectos if p.get('tipo') == 'laboral'])
            
            # Contar tecnologías
            por_tecnologia = self._contar_tecnologias(proyectos)
            
            estadisticas = EstadisticaProyecto(
                total=total,
                academicos=academicos,
                laborales=laborales,
                por_tecnologia=por_tecnologia
            )
            
            # Proyectos recientes
            proyectos_recientes = proyectos[:10]
            
            # Agrupar por programador
            por_programador = self._agrupar_proyectos_por_programador(proyectos)
            
            # Tecnologías populares
            tecnologias_populares = sorted(
                [{"tecnologia": k, "cantidad": v} for k, v in por_tecnologia.items()],
                key=lambda x: x['cantidad'],
                reverse=True
            )[:10]
            
            return DashboardProyectos(
                estadisticas=estadisticas,
                proyectos_recientes=proyectos_recientes,
                por_programador=por_programador,
                tecnologias_populares=tecnologias_populares
            )
            
        except Exception as e:
            print(f"❌ Error al generar dashboard proyectos: {str(e)}")
            raise
    
    async def obtener_datos_asesorias(self, filtros: FiltrosReporteAsesorias) -> List[Dict]:
        """Obtener datos de asesorías para reportes"""
        return await self._obtener_asesorias_jakarta(filtros)
    
    async def obtener_datos_proyectos(self, filtros: FiltrosReporteProyectos) -> List[Dict]:
        """Obtener datos de proyectos para reportes"""
        return await self._obtener_proyectos_spring(filtros)
    
    async def obtener_estadisticas_generales(self) -> Dict:
        """Obtener estadísticas generales de la plataforma"""
        try:
            # Consultar usuarios desde Spring Boot
            async with httpx.AsyncClient() as client:
                usuarios_resp = await client.get(f"{self.spring_url}/usuarios")
                usuarios = usuarios_resp.json() if usuarios_resp.status_code == 200 else []
                
                # Consultar proyectos
                proyectos_resp = await client.get(f"{self.spring_url}/proyectos")
                proyectos = proyectos_resp.json() if proyectos_resp.status_code == 200 else []
                
                # Consultar asesorías
                asesorias_resp = await client.get(f"{self.jakarta_url}/asesorias")
                asesorias = asesorias_resp.json() if asesorias_resp.status_code == 200 else []
            
            return {
                "total_usuarios": len(usuarios),
                "total_programadores": len([u for u in usuarios if u.get('rol') == 'programador']),
                "total_proyectos": len(proyectos),
                "total_asesorias": len(asesorias),
                "asesorias_pendientes": len([a for a in asesorias if a.get('estado') == 'pendiente'])
            }
            
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {str(e)}")
            return {}
    
    # ==========================================
    # MÉTODOS PRIVADOS
    # ==========================================
    
    async def _obtener_asesorias_jakarta(self, filtros: FiltrosReporteAsesorias) -> List[Dict]:
        """Consultar asesorías desde Jakarta EE"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint base
                url = f"{self.jakarta_url}/asesorias"
                
                # Aplicar filtros
                if filtros.id_programador:
                    url = f"{self.jakarta_url}/asesorias/programador/{filtros.id_programador}"
                elif filtros.estado:
                    url = f"{self.jakarta_url}/asesorias/estado/{filtros.estado.value}"
                
                response = await client.get(url)
                
                if response.status_code == 200:
                    asesorias = response.json()
                    
                    # Filtrar por fechas si es necesario
                    if filtros.fecha_inicio or filtros.fecha_fin:
                        asesorias = self._filtrar_por_fechas(
                            asesorias,
                            filtros.fecha_inicio,
                            filtros.fecha_fin
                        )
                    
                    return asesorias
                else:
                    print(f"⚠️ Error al consultar asesorías: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error al obtener asesorías: {str(e)}")
            return []
    
    async def _obtener_proyectos_spring(self, filtros: FiltrosReporteProyectos) -> List[Dict]:
        """Consultar proyectos desde Spring Boot"""
        try:
            async with httpx.AsyncClient() as client:
                # Endpoint base
                url = f"{self.spring_url}/proyectos"
                
                # Aplicar filtros
                if filtros.id_programador:
                    url = f"{self.spring_url}/proyectos/programador/{filtros.id_programador}"
                elif filtros.tipo:
                    url = f"{self.spring_url}/proyectos/tipo/{filtros.tipo}"
                
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️ Error al consultar proyectos: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error al obtener proyectos: {str(e)}")
            return []
    
    def _agrupar_por_programador(self, asesorias: List[Dict]) -> List[Dict]:
        """Agrupar asesorías por programador"""
        agrupado = {}
        for asesoria in asesorias:
            id_prog = asesoria.get('idProgramador', 'unknown')
            if id_prog not in agrupado:
                agrupado[id_prog] = {
                    "id_programador": id_prog,
                    "total": 0,
                    "pendientes": 0,
                    "aprobadas": 0
                }
            agrupado[id_prog]["total"] += 1
            estado = asesoria.get('estado', '')
            if estado == 'pendiente':
                agrupado[id_prog]["pendientes"] += 1
            elif estado == 'aprobada':
                agrupado[id_prog]["aprobadas"] += 1
        
        return list(agrupado.values())
    
    def _agrupar_por_fecha(self, asesorias: List[Dict]) -> List[Dict]:
        """Agrupar asesorías por fecha"""
        agrupado = {}
        for asesoria in asesorias:
            fecha = asesoria.get('fechaAsesoria', 'sin-fecha')
            if fecha not in agrupado:
                agrupado[fecha] = {"fecha": fecha, "cantidad": 0}
            agrupado[fecha]["cantidad"] += 1
        
        return sorted(agrupado.values(), key=lambda x: x['fecha'])
    
    def _agrupar_proyectos_por_programador(self, proyectos: List[Dict]) -> List[Dict]:
        """Agrupar proyectos por programador"""
        agrupado = {}
        for proyecto in proyectos:
            id_prog = proyecto.get('idProgramador', 'unknown')
            if id_prog not in agrupado:
                agrupado[id_prog] = {
                    "id_programador": id_prog,
                    "total": 0,
                    "academicos": 0,
                    "laborales": 0
                }
            agrupado[id_prog]["total"] += 1
            tipo = proyecto.get('tipo', '')
            if tipo == 'academico':
                agrupado[id_prog]["academicos"] += 1
            elif tipo == 'laboral':
                agrupado[id_prog]["laborales"] += 1
        
        return list(agrupado.values())
    
    def _contar_tecnologias(self, proyectos: List[Dict]) -> Dict[str, int]:
        """Contar ocurrencias de tecnologías"""
        tecnologias = {}
        for proyecto in proyectos:
            techs = proyecto.get('tecnologias', [])
            if isinstance(techs, list):
                for tech in techs:
                    tecnologias[tech] = tecnologias.get(tech, 0) + 1
        return tecnologias
    
    def _filtrar_por_fechas(
        self,
        asesorias: List[Dict],
        fecha_inicio: date = None,
        fecha_fin: date = None
    ) -> List[Dict]:
        """Filtrar asesorías por rango de fechas"""
        if not fecha_inicio and not fecha_fin:
            return asesorias
        
        filtradas = []
        for asesoria in asesorias:
            fecha_str = asesoria.get('fechaAsesoria', '')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    if fecha_inicio and fecha < fecha_inicio:
                        continue
                    if fecha_fin and fecha > fecha_fin:
                        continue
                    filtradas.append(asesoria)
                except:
                    pass
        
        return filtradas