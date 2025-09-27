# gui/GUIArbolAVL.py
import pygame

class GUIArbolAVL:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Fuentes más pequeñas
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.recorrido_lineas = []

    def dibujar_arbol_completo(self, screen, arbol_obstaculos):
        screen.fill((25, 25, 40))

        # Header
        header = pygame.Surface((self.screen_width, 60))
        header.fill((40, 40, 80))
        screen.blit(header, (0, 0))

        # Título
        titulo = self.font.render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.screen_width//2, 30))
        screen.blit(titulo, titulo_rect)

        # Árbol
        if arbol_obstaculos and arbol_obstaculos.raiz:
            # separación inicial más pequeña
            self.dibujar_arbol_recursivo(screen, arbol_obstaculos.raiz, 
                                         self.screen_width//2, 100, 150)

        # Panel inferior
        panel_inferior = pygame.Surface((self.screen_width, 100), pygame.SRCALPHA)
        panel_inferior.fill((0, 0, 0, 128))
        screen.blit(panel_inferior, (0, self.screen_height - 100))

        self.dibujar_controles_arbol(screen)

    def dibujar_arbol_recursivo(self, screen, nodo, x, y, separacion):
        if nodo.izquierda:
            nuevo_x = x - separacion
            nuevo_y = y + 60
            pygame.draw.line(screen, (80, 80, 120), (x+2, y+12), (nuevo_x+2, nuevo_y-8), 2)
            pygame.draw.line(screen, (100, 200, 100), (x, y+10), (nuevo_x, nuevo_y-10), 2)
            self.dibujar_arbol_recursivo(screen, nodo.izquierda, nuevo_x, nuevo_y, separacion * 0.6)

        if nodo.derecha:
            nuevo_x = x + separacion
            nuevo_y = y + 60
            pygame.draw.line(screen, (80, 80, 120), (x+2, y+12), (nuevo_x+2, nuevo_y-8), 2)
            pygame.draw.line(screen, (100, 200, 100), (x, y+10), (nuevo_x, nuevo_y-10), 2)
            self.dibujar_arbol_recursivo(screen, nodo.derecha, nuevo_x, nuevo_y, separacion * 0.6)

        # Nodo más pequeño
        radio = 15
        color_nodo = (0, 150, 200) if getattr(nodo, 'es_raiz', False) else (200, 100, 50)
        pygame.draw.circle(screen, (20, 20, 40), (x+2, y+2), radio+1)
        pygame.draw.circle(screen, color_nodo, (x, y), radio)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), radio, 1)
        
        texto_coords = self.font_small.render(f"{nodo.x},{nodo.y}", True, (255, 255, 255))
        texto_rect = texto_coords.get_rect(center=(x, y))
        screen.blit(texto_coords, texto_rect)

        altura_texto = self.font_small.render(f"h:{nodo.altura}", True, (200, 200, 200))
        screen.blit(altura_texto, (x - 10, y + radio))

    def dibujar_controles_arbol(self, screen):
        botones = [
            ("🔍 Inorden", (20, self.screen_height - 80)),
            ("📊 Preorden", (20, self.screen_height - 45)),
            ("📈 Postorden", (150, self.screen_height - 80)),
            ("🎮 Volver", (150, self.screen_height - 45))
        ]

        for texto, pos in botones:
            pygame.draw.rect(screen, (70, 130, 180), (pos[0], pos[1], 110, 28), border_radius=5)
            texto_btn = self.font_small.render(texto, True, (255, 255, 255))
            screen.blit(texto_btn, (pos[0] + 8, pos[1] + 5))

        if self.recorrido_lineas:
            y_pos = self.screen_height - 120
            for linea in self.recorrido_lineas[-3:]:
                texto_rec = self.font_small.render(linea, True, (255, 255, 0))
                screen.blit(texto_rec, (280, y_pos))
                y_pos += 18

    def formatear_recorrido(self, recorrido, tipo):
        if not recorrido:
            return ["No hay elementos en el árbol"]
        
        lineas = []
        linea_actual = f"{tipo}: "
        
        for elemento in recorrido:
            if len(linea_actual + elemento) > 40:
                lineas.append(linea_actual)
                linea_actual = elemento + ", "
            else:
                linea_actual += elemento + ", "
        
        if linea_actual:
            lineas.append(linea_actual.rstrip(", "))
        
        return lineas

    def manejar_eventos_arbol(self, event, arbol_obstaculos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if 20 <= x <= 130:
                if self.screen_height - 80 <= y <= self.screen_height - 52:
                    recorrido = arbol_obstaculos.inorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "INORDEN")
                elif self.screen_height - 45 <= y <= self.screen_height - 17:
                    recorrido = arbol_obstaculos.preorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "PREORDEN")
            
            if 150 <= x <= 260:
                if self.screen_height - 80 <= y <= self.screen_height - 52:
                    recorrido = arbol_obstaculos.postorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "POSTORDEN")
                elif self.screen_height - 45 <= y <= self.screen_height - 17:
                    return "volver"
        
        return None
