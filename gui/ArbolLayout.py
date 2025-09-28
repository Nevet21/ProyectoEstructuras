# gui/ArbolLayoutManager.py
import pygame

class ArbolLayoutManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Espaciado
        self.nivel_altura = 60
        self.espacio_base = 100
        self.zoom_manual = 1.0
        self.zoom_auto = 1.0
        
        # ✅ NUEVO: Sistema de zoom direccional
        self.offset_x = 0
        self.offset_y = 0
        self.arrastrando = False
        self.ultimo_mouse_pos = (0, 0)
        self.ultimo_ancho_arbol = 0
        
        # ✅ NUEVO: Punto de ancla para zoom direccional
        self.zoom_anchor_x = 0
        self.zoom_anchor_y = 0
        
        # Posición inicial
        self.y_inicio = 70
        
        self.font_nodo = pygame.font.SysFont("Arial", 12, bold=True)
        self.font_altura = pygame.font.SysFont("Arial", 10)

    def calcular_zoom_automatico(self, ancho_arbol):
        """Zoom automático simple basado en el ancho"""
        if ancho_arbol == 0:
            return 1.0
        
        margen = 200
        zoom_calculado = (self.screen_width - margen) / ancho_arbol
        
        if self.ultimo_ancho_arbol > 0:
            zoom_calculado = (zoom_calculado * 0.3 + self.zoom_auto * 0.7)
        
        return max(0.4, min(zoom_calculado, 1.2))

    def calcular_altura_arbol(self, nodo):
        """Calcula la altura total del árbol"""
        if not nodo:
            return 0
        return 1 + max(self.calcular_altura_arbol(nodo.izquierda), 
                      self.calcular_altura_arbol(nodo.derecha))

    def calcular_layout(self, nodo, nivel=0, x_min=0, x_max=None):
        """Layout del árbol"""
        if x_max is None:
            x_max = self.screen_width
            
        if not nodo:
            return None, 0
        
        inicio_vertical = self.y_inicio
        espacio = int(self.espacio_base * (0.6 ** min(nivel, 3)))
        
        izquierda, ancho_izq = self.calcular_layout(nodo.izquierda, nivel + 1, x_min, x_max)
        x_actual = x_min + ancho_izq + espacio
        derecha, ancho_der = self.calcular_layout(nodo.derecha, nivel + 1, x_actual + espacio, x_max)
        ancho_total = ancho_izq + ancho_der + espacio * 2
        
        if nivel == 0 and ancho_total != self.ultimo_ancho_arbol:
            self.zoom_auto = self.calcular_zoom_automatico(ancho_total)
            self.ultimo_ancho_arbol = ancho_total
        
        nodo.x_dibujo = x_actual
        nodo.y_dibujo = inicio_vertical + nivel * self.nivel_altura
        nodo.ancho_subarbol = ancho_total
        
        return nodo, ancho_total

    def obtener_zoom_total(self):
        return self.zoom_auto * self.zoom_manual

    def aplicar_zoom_y_desplazamiento(self, nodo):
        """Aplicación de zoom y desplazamiento"""
        if not nodo:
            return
            
        zoom_total = self.obtener_zoom_total()
        
        # ✅ ELIMINADO: Centrado automático cuando se arrastra
        # El zoom direccional maneja el centrado
        
        nodo.x_final = (nodo.x_dibujo + self.offset_x) * zoom_total
        nodo.y_final = (nodo.y_dibujo + self.offset_y) * zoom_total
        
        self.aplicar_zoom_y_desplazamiento(nodo.izquierda)
        self.aplicar_zoom_y_desplazamiento(nodo.derecha)

    def manejar_eventos_zoom(self, event):
        """✅ ZOOM MUY SUAVE - SENSIBILIDAD MUY REDUCIDA"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Zoom in
                self.zoom_direccional(event.pos, 1.05)  # ✅ MUY SUAVE
            elif event.button == 5:  # Zoom out
                self.zoom_direccional(event.pos, 1/1.05)  # ✅ MUY SUAVE
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
                
                # ✅ ARRASTRE MUY SUAVE
                sensibilidad_arrastre = 0.6  # ✅ Más suave aún
                self.offset_x += (dx / max(zoom_total, 0.1)) * sensibilidad_arrastre
                self.offset_y += (dy / max(zoom_total, 0.1)) * sensibilidad_arrastre
                self.ultimo_mouse_pos = event.pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset
                self.zoom_manual = 1.0
                self.offset_x = 0
                self.offset_y = 0
                self.arrastrando = False
                print("🔄 Vista reseteada")

    def zoom_direccional(self, mouse_pos, factor_zoom):
        """✅ ZOOM EXTRA SUAVE"""
        zoom_anterior = self.zoom_manual
        
        # ✅ ZOOM MUY GRADUAL
        if factor_zoom > 1:  # Zoom in
            self.zoom_manual = min(self.zoom_manual * factor_zoom, 3.0)  # ✅ Límite más bajo
        else:  # Zoom out
            self.zoom_manual = max(self.zoom_manual * factor_zoom, 0.4)  # ✅ Límite más alto
        
        if self.zoom_manual != zoom_anterior:
            zoom_total_anterior = self.zoom_auto * zoom_anterior
            zoom_total_nuevo = self.obtener_zoom_total()
            
            mouse_x_arbol = (mouse_pos[0] / zoom_total_anterior) - self.offset_x
            mouse_y_arbol = (mouse_pos[1] / zoom_total_anterior) - self.offset_y
            
            self.offset_x = (mouse_pos[0] / zoom_total_nuevo) - mouse_x_arbol
            self.offset_y = (mouse_pos[1] / zoom_total_nuevo) - mouse_y_arbol
            
            # ✅ FEEDBACK VISUAL MÁS DETALLADO
            print(f"🔍 Zoom total: {zoom_total_nuevo:.2f}x | Manual: {self.zoom_manual:.2f}x | Auto: {self.zoom_auto:.2f}x")

    def dibujar_nodo(self, screen, nodo):
        """Dibuja nodos"""
        if not nodo or not hasattr(nodo, 'x_final'):
            return
            
        x, y = int(nodo.x_final), int(nodo.y_final)
        
        # Solo dibujar si está dentro de la pantalla (optimización)
        if not (-50 <= x <= self.screen_width + 50 and -50 <= y <= self.screen_height + 50):
            return
        
        radio = 20
        color_nodo = (0, 150, 200) if getattr(nodo, 'es_raiz', False) else (200, 100, 50)
        
        pygame.draw.circle(screen, (20, 20, 40), (x + 2, y + 2), radio + 1)
        pygame.draw.circle(screen, color_nodo, (x, y), radio)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), radio, 1)
        
        texto_coords = self.font_altura.render(f"({nodo.x},{nodo.y})", True, (255, 255, 255))
        texto_rect = texto_coords.get_rect(center=(x, y))
        screen.blit(texto_coords, texto_rect)
        
        altura_text = self.font_altura.render(f"h:{nodo.altura}", True, (200, 200, 200))
        screen.blit(altura_text, (x - 12, y + radio + 5))

    def dibujar_conexiones(self, screen, nodo):
        """Dibuja líneas entre nodos (optimizado)"""
        if not nodo or not hasattr(nodo, 'x_final'):
            return
            
        grosor = max(1, int(2 * min(self.zoom_manual, 2)))  # ✅ Grosor adaptativo al zoom
        
        if nodo.izquierda and hasattr(nodo.izquierda, 'x_final'):
            x1, y1 = int(nodo.x_final), int(nodo.y_final)
            x2, y2 = int(nodo.izquierda.x_final), int(nodo.izquierda.y_final)
            
            # ✅ Solo dibujar si al menos un extremo está visible
            if (self.es_punto_visible(x1, y1) or self.es_punto_visible(x2, y2)):
                pygame.draw.line(screen, (100, 200, 100), (x1, y1 + 10), (x2, y2 - 10), grosor)
                self.dibujar_conexiones(screen, nodo.izquierda)
            
        if nodo.derecha and hasattr(nodo.derecha, 'x_final'):
            x1, y1 = int(nodo.x_final), int(nodo.y_final)
            x2, y2 = int(nodo.derecha.x_final), int(nodo.derecha.y_final)
            
            if (self.es_punto_visible(x1, y1) or self.es_punto_visible(x2, y2)):
                pygame.draw.line(screen, (100, 200, 100), (x1, y1 + 10), (x2, y2 - 10), grosor)
                self.dibujar_conexiones(screen, nodo.derecha)

    def es_punto_visible(self, x, y):
        """✅ OPTIMIZACIÓN: Verifica si un punto está visible en pantalla"""
        return (-100 <= x <= self.screen_width + 100 and 
                -100 <= y <= self.screen_height + 100)

    def obtener_vista_actual(self):
        """✅ NUEVO: Devuelve información de la vista actual"""
        return {
            'zoom': self.obtener_zoom_total(),
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'zoom_manual': self.zoom_manual,
            'zoom_auto': self.zoom_auto
        }