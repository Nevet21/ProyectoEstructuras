# gui/ArbolLayoutManager.py
import pygame

class ArbolLayoutManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # VOLVEMOS al espaciado original que funcionaba
        self.nivel_altura = 80  # Original
        self.espacio_base = 150  # Original  
        self.zoom_manual = 1.0
        self.zoom_auto = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.arrastrando = False
        self.ultimo_mouse_pos = (0, 0)
        self.ultimo_ancho_arbol = 0
        
        # **MODIFICACIÓN: Fuentes más pequeñas**
        self.font_nodo = pygame.font.SysFont("Arial", 9, bold=True)  # Reducido de 16 a 12
        self.font_altura = pygame.font.SysFont("Arial", 8)  # Reducido de 12 a 10

    def calcular_zoom_automatico(self, ancho_arbol):
        """Zoom automático simple basado en el ancho"""
        if ancho_arbol == 0:
            return 1.0
        
        # Margen para dejar espacio a los lados
        margen = 200
        zoom_calculado = (self.screen_width - margen) / ancho_arbol
        
        # Suavizar transición
        if self.ultimo_ancho_arbol > 0:
            zoom_calculado = (zoom_calculado * 0.3 + self.zoom_auto * 0.7)
        
        return max(0.4, min(zoom_calculado, 1.2))  # Límites razonables

    def calcular_altura_arbol(self, nodo):
        if not nodo:
            return 0
        return 1 + max(self.calcular_altura_arbol(nodo.izquierda), 
                      self.calcular_altura_arbol(nodo.derecha))

    def calcular_layout(self, nodo, nivel=0, x_min=0, x_max=None):
        """LAYOUT ORIGINAL - marcando la raíz"""
        if x_max is None:
            x_max = self.screen_width
            
        if not nodo:
            return None, 0
        
        # Marcar si es la raíz
        if nivel == 0:
            nodo.es_raiz = True
        else:
            nodo.es_raiz = False
        
        # **VOLVEMOS AL CÁLCULO ORIGINAL**
        espacio = int(self.espacio_base * (0.6 ** min(nivel, 3)))  # Reducción por nivel
        
        # Subárbol izquierdo
        izquierda, ancho_izq = self.calcular_layout(nodo.izquierda, nivel + 1, x_min, x_max)
        
        # Posición actual
        x_actual = x_min + ancho_izq + espacio
        
        # Subárbol derecho
        derecha, ancho_der = self.calcular_layout(nodo.derecha, nivel + 1, x_actual + espacio, x_max)
        
        ancho_total = ancho_izq + ancho_der + espacio * 2
        
        # Actualizar zoom automático si es la raíz
        if nivel == 0 and ancho_total != self.ultimo_ancho_arbol:
            self.zoom_auto = self.calcular_zoom_automatico(ancho_total)
            self.ultimo_ancho_arbol = ancho_total
        
        # **POSICIÓN ORIGINAL - empezando desde arriba**
        nodo.x_dibujo = x_actual
        nodo.y_dibujo = 100 + nivel * self.nivel_altura  # Original: desde arriba
        nodo.ancho_subarbol = ancho_total
        
        return nodo, ancho_total

    def obtener_zoom_total(self):
        return self.zoom_auto * self.zoom_manual

    def aplicar_zoom_y_desplazamiento(self, nodo):
        """Aplicación ORIGINAL de zoom"""
        if not nodo:
            return
            
        zoom_total = self.obtener_zoom_total()
        
        # **CENTRADO ORIGINAL - simple**
        if not self.arrastrando and self.offset_x == 0:
            if hasattr(nodo, 'ancho_subarbol'):
                ancho_zoom = nodo.ancho_subarbol * zoom_total
                self.offset_x = (self.screen_width - ancho_zoom) / 2 / max(zoom_total, 0.1)
        
        nodo.x_final = (nodo.x_dibujo + self.offset_x) * zoom_total
        nodo.y_final = (nodo.y_dibujo + self.offset_y) * zoom_total
        
        self.aplicar_zoom_y_desplazamiento(nodo.izquierda)
        self.aplicar_zoom_y_desplazamiento(nodo.derecha)

    def manejar_eventos_zoom(self, event):
        """Manejo ORIGINAL de eventos"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Zoom in
                self.zoom_manual = min(self.zoom_manual * 1.2, 3.0)
            elif event.button == 5:  # Zoom out
                self.zoom_manual = max(self.zoom_manual / 1.2, 0.3)
            elif event.button == 1:  # Arrastrar
                self.arrastrando = True
                self.ultimo_mouse_pos = event.pos
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.arrastrando = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.arrastrando:
                dx = event.pos[0] - self.ultimo_mouse_pos[0]
                dy = event.pos[1] - self.ultimo_mouse_pos[1]
                zoom_total = self.obtener_zoom_total()
                self.offset_x += dx / max(zoom_total, 0.1)
                self.offset_y += dy / max(zoom_total, 0.1)
                self.ultimo_mouse_pos = event.pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset
                self.zoom_manual = 1.0
                self.offset_x = 0
                self.offset_y = 0
                self.arrastrando = False

    def dibujar_nodo(self, screen, nodo):
        """DIBUJO ORIGINAL de nodos - CON FUENTES MÁS PEQUEÑAS"""
        if not nodo or not hasattr(nodo, 'x_final'):
            return
            
        x, y = int(nodo.x_final), int(nodo.y_final)
        
        # **ESTILO ORIGINAL**
        radio = 20
        color_nodo = (0, 150, 200) if getattr(nodo, 'es_raiz', False) else (200, 100, 50)
        
        pygame.draw.circle(screen, (20, 20, 40), (x + 2, y + 2), radio + 1)
        pygame.draw.circle(screen, color_nodo, (x, y), radio)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), radio, 1)
        
        # **Coordenadas con fuente más pequeña**
        texto_coordenadas = self.font_nodo.render(f"({nodo.x},{nodo.y})", True, (255, 255, 255))
        texto_rect = texto_coordenadas.get_rect(center=(x, y))
        screen.blit(texto_coordenadas, texto_rect)
        
        # **Tipo de obstáculo con fuente más pequeña**
        tipo_text = self.font_altura.render(f"{nodo.tipo}", True, (200, 200, 200))
        tipo_rect = tipo_text.get_rect(center=(x, y + radio + 8))
        screen.blit(tipo_text, tipo_rect)

    def dibujar_conexiones(self, screen, nodo):
        """CONEXIONES ORIGINALES"""
        if not nodo or not hasattr(nodo, 'x_final'):
            return
            
        grosor = 2  # Original
        
        if nodo.izquierda and hasattr(nodo.izquierda, 'x_final'):
            x1, y1 = int(nodo.x_final), int(nodo.y_final)
            x2, y2 = int(nodo.izquierda.x_final), int(nodo.izquierda.y_final)
            # **LÍNEA ORIGINAL**
            pygame.draw.line(screen, (100, 200, 100), (x1, y1 + 10), (x2, y2 - 10), grosor)
            self.dibujar_conexiones(screen, nodo.izquierda)
            
        if nodo.derecha and hasattr(nodo.derecha, 'x_final'):
            x1, y1 = int(nodo.x_final), int(nodo.y_final)
            x2, y2 = int(nodo.derecha.x_final), int(nodo.derecha.y_final)
            pygame.draw.line(screen, (100, 200, 100), (x1, y1 + 10), (x2, y2 - 10), grosor)
            self.dibujar_conexiones(screen, nodo.derecha)