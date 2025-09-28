# gui/GUIArbolAVL.py
import pygame
from gui.ArbolLayout import ArbolLayoutManager

class GUIArbolAVL:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layout_manager = ArbolLayoutManager(screen_width, screen_height)
        self.font_controles = pygame.font.SysFont("Arial", 14)

    def dibujar_arbol_completo(self, screen, arbol_obstaculos):
        # **FONDO ORIGINAL**
        screen.fill((25, 25, 40))
        
        # **HEADER ORIGINAL**
        titulo = self.font_controles.render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        screen.blit(titulo, (10, 10))

        if arbol_obstaculos and arbol_obstaculos.raiz:
            # **CÁLCULO ORIGINAL**
            self.layout_manager.calcular_layout(arbol_obstaculos.raiz)
            self.layout_manager.aplicar_zoom_y_desplazamiento(arbol_obstaculos.raiz)
            
            # **DIBUJO ORIGINAL**: conexiones primero, luego nodos
            self.layout_manager.dibujar_conexiones(screen, arbol_obstaculos.raiz)
            self._dibujar_nodos_recursivo(screen, arbol_obstaculos.raiz)

        self.dibujar_controles(screen)

    def _dibujar_nodos_recursivo(self, screen, nodo):
        if nodo:
            self.layout_manager.dibujar_nodo(screen, nodo)
            self._dibujar_nodos_recursivo(screen, nodo.izquierda)
            self._dibujar_nodos_recursivo(screen, nodo.derecha)

    def dibujar_controles(self, screen):
        # **CONTROLES ORIGINALES**
        controles = [
            f"Zoom: {self.layout_manager.obtener_zoom_total():.1f}x",
            "Rueda: Zoom manual",
            "Arrastrar: Mover",
            "R: Resetear vista"
        ]
        
        y_pos = self.screen_height - 70
        for i, texto in enumerate(controles):
            texto_surf = self.font_controles.render(texto, True, (200, 200, 200))
            screen.blit(texto_surf, (10, y_pos + i * 18))

    def manejar_eventos_arbol(self, event, arbol_obstaculos):
        self.layout_manager.manejar_eventos_zoom(event)
        return None