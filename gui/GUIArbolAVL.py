# gui/GUIArbolAVL.py
import pygame
from gui.ArbolLayout import ArbolLayoutManager

class GUIArbolAVL:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layout_manager = ArbolLayoutManager(screen_width, screen_height)
        
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_controles = pygame.font.SysFont("Arial", 16)
        self.font_botones = pygame.font.SysFont("Arial", 14)
        
        self.recorrido_actual = None
        self.texto_recorrido = []

    def dibujar_arbol_completo(self, screen, arbol_obstaculos):
        # Fondo
        screen.fill((25, 25, 40))
        
        # ✅ HEADER MÁS COMPACTO
        header = pygame.Surface((self.screen_width, 50))  # Más compacto
        header.fill((40, 40, 80))
        screen.blit(header, (0, 0))
        
        titulo = pygame.font.SysFont("Arial", 22, bold=True).render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.screen_width//2, 25))
        screen.blit(titulo, titulo_rect)

        if arbol_obstaculos and arbol_obstaculos.raiz:
            # ✅ EMPEZAR MÁS ABAJO para no interferir con el título
            self.layout_manager.y_inicio = 70  # Más espacio desde el título
            self.layout_manager.calcular_layout(arbol_obstaculos.raiz)
            self.layout_manager.aplicar_zoom_y_desplazamiento(arbol_obstaculos.raiz)
            
            self.layout_manager.dibujar_conexiones(screen, arbol_obstaculos.raiz)
            self._dibujar_nodos_recursivo(screen, arbol_obstaculos.raiz)

        # ✅ REORGANIZAR: Botones más arriba, recorrido mejor posicionado
        self.dibujar_botones_recorridos(screen)
        self.dibujar_recorrido_actual(screen)
        self.dibujar_controles(screen)

    def _dibujar_nodos_recursivo(self, screen, nodo):
        if nodo:
            self.layout_manager.dibujar_nodo(screen, nodo)
            self._dibujar_nodos_recursivo(screen, nodo.izquierda)
            self._dibujar_nodos_recursivo(screen, nodo.derecha)

    def dibujar_botones_recorridos(self, screen):
        """Botones más arriba para evitar superposición"""
        # ✅ POSICIÓN MÁS ALTA - aprovechar espacio superior
        botones_y = self.screen_height - 220  # Más arriba
        
        botones = [
            {"texto": "📊 Preorden", "tipo": "preorden", "x": 20, "y": botones_y},
            {"texto": "🔍 Inorden", "tipo": "inorden", "x": 150, "y": botones_y},
            {"texto": "📈 Postorden", "tipo": "postorden", "x": 280, "y": botones_y}
        ]
        
        for boton in botones:
            rect = pygame.Rect(boton["x"], boton["y"], 120, 35)
            color_base = (70, 130, 180)
            color_activo = (100, 160, 210)
            
            color_actual = color_activo if self.recorrido_actual == boton["tipo"] else color_base
            
            pygame.draw.rect(screen, color_actual, rect, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)
            
            texto = self.font_botones.render(boton["texto"], True, (255, 255, 255))
            texto_rect = texto.get_rect(center=rect.center)
            screen.blit(texto, texto_rect)

    def obtener_recorrido_formateado(self, arbol_obstaculos, tipo):
        """CORRECCIÓN: Aprovechar al máximo cada línea antes de saltar"""
        try:
            if not arbol_obstaculos or arbol_obstaculos.esta_vacio():
                return ["Árbol vacío"]
            
            if tipo == "preorden":
                recorrido_raw = arbol_obstaculos.preorden()
            elif tipo == "inorden":
                recorrido_raw = arbol_obstaculos.inorden()
            elif tipo == "postorden":
                recorrido_raw = arbol_obstaculos.postorden()
            else:
                return ["Tipo de recorrido no válido"]
            
            if not recorrido_raw:
                return ["Árbol vacío"]
            
            # ✅ CORRECCIÓN: Algoritmo mejorado para máximo aprovechamiento
            lineas = []
            linea_actual = ""
            max_caracteres_por_linea = 85  # Máximo de caracteres por línea
            
            for i, elemento in enumerate(recorrido_raw):
                elemento_str = str(elemento)
                
                # Si es el primer elemento de la línea
                if not linea_actual:
                    linea_actual = elemento_str
                else:
                    # Calcular cómo quedaría la línea con el nuevo elemento
                    linea_propuesta = linea_actual + "  " + elemento_str
                    
                    # Si cabe en la línea actual, agregarlo
                    if len(linea_propuesta) <= max_caracteres_por_linea:
                        linea_actual = linea_propuesta
                    else:
                        # No cabe, guardar línea actual y empezar nueva
                        lineas.append(linea_actual)
                        linea_actual = elemento_str
                
                # Si es el último elemento, guardar la línea actual
                if i == len(recorrido_raw) - 1 and linea_actual:
                    lineas.append(linea_actual)
            
            # ✅ MEJORA: Si hay pocos elementos, intentar agrupar más
            if len(lineas) > 8:
                # Intentar agrupar más agresivamente
                lineas_compactas = []
                linea_compacta = ""
                max_compacto = 95  # Un poco más de margen
                
                for i, elemento in enumerate(recorrido_raw):
                    elemento_str = str(elemento)
                    
                    if not linea_compacta:
                        linea_compacta = elemento_str
                    else:
                        linea_propuesta = linea_compacta + " " + elemento_str  # Un solo espacio
                        
                        if len(linea_propuesta) <= max_compacto:
                            linea_compacta = linea_propuesta
                        else:
                            lineas_compactas.append(linea_compacta)
                            linea_compacta = elemento_str
                    
                    if i == len(recorrido_raw) - 1 and linea_compacta:
                        lineas_compactas.append(linea_compacta)
                
                # Usar la versión más compacta si es mejor
                if len(lineas_compactas) < len(lineas):
                    lineas = lineas_compactas
            
            # Limitar líneas mostradas
            if len(lineas) > 8:
                # Calcular cuántos elementos estamos mostrando
                elementos_mostrados = 0
                for linea in lineas[:8]:
                    elementos_mostrados += len(linea.split())  # Contar elementos aproximados
                
                lineas = lineas[:8]
                if len(recorrido_raw) > elementos_mostrados:
                    lineas.append(f"... y {len(recorrido_raw) - elementos_mostrados} nodos más")
            
            return lineas
            
        except Exception as e:
            return [f"Error: {str(e)}"]

    def dibujar_recorrido_actual(self, screen):
        """Recorrido que aprovecha todo el ancho disponible"""
        if self.recorrido_actual and self.texto_recorrido:
            # ✅ APROVECHAR ANCHO COMPLETO - usar todo el espacio derecho
            panel_x = 20
            panel_y = self.screen_height - 180  # Justo debajo de los botones
            panel_ancho = self.screen_width - 40  # Todo el ancho disponible
            panel_alto = 150  # Más alto para más líneas
            
            panel = pygame.Surface((panel_ancho, panel_alto), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 200))
            screen.blit(panel, (panel_x, panel_y))
            
            # Título del recorrido
            titulo_texto = self.font_botones.render(
                f"RECORRIDO {self.recorrido_actual.upper()}:", 
                True, (255, 255, 0)
            )
            screen.blit(titulo_texto, (panel_x + 10, panel_y + 10))
            
            # ✅ FORMATO HORIZONTAL COMPACTO que aprovecha todo el ancho
            y_pos = panel_y + 35
            fuente_recorrido = pygame.font.SysFont("Arial", 13)
            
            for i, linea in enumerate(self.texto_recorrido):
                # ✅ APROVECHAR ANCHO COMPLETO - texto más extendido
                texto_linea = fuente_recorrido.render(linea, True, (255, 255, 255))
                screen.blit(texto_linea, (panel_x + 10, y_pos))
                y_pos += 16
                
                # Limitar a 6 líneas máximo
                if i >= 5 and i < len(self.texto_recorrido) - 1:
                    continuacion = fuente_recorrido.render("...", True, (180, 180, 180))
                    screen.blit(continuacion, (panel_x + 10, y_pos))
                    break

    def dibujar_controles(self, screen):
        """Controles compactos en la parte inferior"""
        # ✅ PANEL INFERIOR MÁS COMPACTO
        panel_inferior = pygame.Surface((self.screen_width, 50), pygame.SRCALPHA)
        panel_inferior.fill((0, 0, 0, 128))
        screen.blit(panel_inferior, (0, self.screen_height - 50))
        
        # ✅ CONTROLES EN DOS COLUMNAS para aprovechar espacio
        controles_columna1 = [
            f"Zoom: {self.layout_manager.obtener_zoom_total():.1f}x",
            "🔍 Rueda: Zoom manual"
        ]
        
        controles_columna2 = [
            "🖱️  Arrastrar: Mover vista", 
            "🔄 R: Resetear vista"
        ]
        
        # Columna 1 (izquierda)
        y_pos = self.screen_height - 40
        for i, texto in enumerate(controles_columna1):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            texto_surf = pygame.font.SysFont("Arial", 12).render(texto, True, color)
            screen.blit(texto_surf, (20, y_pos + i * 15))
        
        # Columna 2 (derecha)
        for i, texto in enumerate(controles_columna2):
            color = (200, 200, 200)
            texto_surf = pygame.font.SysFont("Arial", 12).render(texto, True, color)
            screen.blit(texto_surf, (self.screen_width - 200, y_pos + i * 15))
            
        # ✅ BOTÓN VOLVER MEJOR POSICIONADO
        volver_rect = pygame.Rect(self.screen_width - 120, self.screen_height - 40, 100, 25)
        pygame.draw.rect(screen, (180, 70, 70), volver_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), volver_rect, 1, border_radius=5)
        texto_volver = pygame.font.SysFont("Arial", 12).render("🎮 Volver", True, (255, 255, 255))
        texto_volver_rect = texto_volver.get_rect(center=volver_rect.center)
        screen.blit(texto_volver, texto_volver_rect)

    def manejar_eventos_arbol(self, event, arbol_obstaculos):
        """Actualizar coordenadas de los botones"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # ✅ ACTUALIZAR coordenadas de los botones (posición más alta)
            botones_y = self.screen_height - 220
            botones_recorrido = [
                {"tipo": "preorden", "x": 20, "y": botones_y, "ancho": 120, "alto": 35},
                {"tipo": "inorden", "x": 150, "y": botones_y, "ancho": 120, "alto": 35},
                {"tipo": "postorden", "x": 280, "y": botones_y, "ancho": 120, "alto": 35}
            ]
            
            for boton in botones_recorrido:
                if (boton["x"] <= x <= boton["x"] + boton["ancho"] and 
                    boton["y"] <= y <= boton["y"] + boton["alto"]):
                    
                    self.recorrido_actual = boton["tipo"]
                    self.texto_recorrido = self.obtener_recorrido_formateado(arbol_obstaculos, boton["tipo"])
                    print(f"✅ Recorrido {boton['tipo']} ejecutado")
                    break
            
            # ✅ ACTUALIZAR coordenada del botón Volver
            if (self.screen_width - 120 <= x <= self.screen_width - 20 and 
                self.screen_height - 40 <= y <= self.screen_height - 15):
                return "volver"
        
        self.layout_manager.manejar_eventos_zoom(event)
        return None