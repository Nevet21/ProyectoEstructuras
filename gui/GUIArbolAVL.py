# gui/GUIArbolAVL.py
import pygame

class GUIArbolAVL:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.recorrido_lineas = []

    def dibujar_arbol_completo(self, screen, arbol_obstaculos):
        """EXACTAMENTE igual que antes"""
        # Fondo azul oscuro
        screen.fill((25, 25, 40))

        # Header
        header = pygame.Surface((self.screen_width, 80))
        header.fill((40, 40, 80))
        screen.blit(header, (0, 0))

        # Título
        titulo = self.font.render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.screen_width//2, 40))
        screen.blit(titulo, titulo_rect)

        # Árbol
        if arbol_obstaculos and arbol_obstaculos.raiz:
            self.dibujar_arbol_recursivo(screen, arbol_obstaculos.raiz, 
                                       self.screen_width//2, 120, 250)

        # Panel inferior
        panel_inferior = pygame.Surface((self.screen_width, 120), pygame.SRCALPHA)
        panel_inferior.fill((0, 0, 0, 128))
        screen.blit(panel_inferior, (0, self.screen_height - 120))

        # Controles
        self.dibujar_controles_arbol(screen)

    def dibujar_arbol_recursivo(self, screen, nodo, x, y, separacion):
        """EXACTAMENTE igual que antes"""
        if nodo.izquierda:
            nuevo_x = x - separacion
            nuevo_y = y + 80
            pygame.draw.line(screen, (80, 80, 120), (x+2, y+17), (nuevo_x+2, nuevo_y-13), 3)
            pygame.draw.line(screen, (100, 200, 100), (x, y+15), (nuevo_x, nuevo_y-15), 3)
            self.dibujar_arbol_recursivo(screen, nodo.izquierda, nuevo_x, nuevo_y, separacion * 0.6)

        if nodo.derecha:
            nuevo_x = x + separacion
            nuevo_y = y + 80
            pygame.draw.line(screen, (80, 80, 120), (x+2, y+17), (nuevo_x+2, nuevo_y-13), 3)
            pygame.draw.line(screen, (100, 200, 100), (x, y+15), (nuevo_x, nuevo_y-15), 3)
            self.dibujar_arbol_recursivo(screen, nodo.derecha, nuevo_x, nuevo_y, separacion * 0.6)

        # Nodo
        color_nodo = (0, 150, 200) if getattr(nodo, 'es_raiz', False) else (200, 100, 50)
        pygame.draw.circle(screen, (20, 20, 40), (x+3, y+3), 26)
        pygame.draw.circle(screen, color_nodo, (x, y), 25)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 25, 2)
        
        texto_coords = self.font_small.render(f"{nodo.x},{nodo.y}", True, (255, 255, 255))
        texto_rect = texto_coords.get_rect(center=(x, y))
        screen.blit(texto_coords, texto_rect)

        altura_texto = self.font_small.render(f"h:{nodo.altura}", True, (200, 200, 200))
        screen.blit(altura_texto, (x - 12, y + 20))

    def dibujar_controles_arbol(self, screen):
        """EXACTAMENTE igual que antes"""
        botones = [
            ("🔍 Inorden", (20, self.screen_height - 100)),
            ("📊 Preorden", (20, self.screen_height - 60)),
            ("📈 Postorden", (150, self.screen_height - 100)),
            ("🎮 Volver al Juego", (150, self.screen_height - 60))
        ]

        for texto, pos in botones:
            pygame.draw.rect(screen, (70, 130, 180), (pos[0], pos[1], 140, 35), border_radius=5)
            texto_btn = self.font_small.render(texto, True, (255, 255, 255))
            screen.blit(texto_btn, (pos[0] + 10, pos[1] + 8))

        if self.recorrido_lineas:
            y_pos = self.screen_height - 150
            for linea in self.recorrido_lineas[-3:]:
                texto_rec = self.font_small.render(linea, True, (255, 255, 0))
                screen.blit(texto_rec, (300, y_pos))
                y_pos += 25

    def formatear_recorrido(self, recorrido, tipo):
        """EXACTAMENTE igual que antes"""
        if not recorrido:
            return ["No hay elementos en el árbol"]
        
        lineas = []
        linea_actual = f"{tipo}: "
        
        for elemento in recorrido:
            if len(linea_actual + elemento) > 60:
                lineas.append(linea_actual)
                linea_actual = elemento + ", "
            else:
                linea_actual += elemento + ", "
        
        if linea_actual:
            lineas.append(linea_actual.rstrip(", "))
        
        return lineas

    def manejar_eventos_arbol(self, event, arbol_obstaculos):
        """EXACTAMENTE igual que antes"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if 20 <= x <= 160:
                if self.screen_height - 100 <= y <= self.screen_height - 65:
                    recorrido = arbol_obstaculos.inorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "INORDEN")
                elif self.screen_height - 60 <= y <= self.screen_height - 25:
                    recorrido = arbol_obstaculos.preorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "PREORDEN")
            
            if 150 <= x <= 290:
                if self.screen_height - 100 <= y <= self.screen_height - 65:
                    recorrido = arbol_obstaculos.postorden()
                    self.recorrido_lineas = self.formatear_recorrido(recorrido, "POSTORDEN")
                elif self.screen_height - 60 <= y <= self.screen_height - 25:
                    return "volver"
        
        return None