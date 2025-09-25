# gui/GamePygame.py
import pygame
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.Juego import JuegoModel
from gui.GUIArbolAVL import GUIArbolAVL
from gui.GUIManager import GUIManager

class GamePygame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.WIDTH, self.HEIGHT = width, height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera con Árbol AVL")
        self.clock = pygame.time.Clock()

        # Cargar configuración
        config = self.cargar_configuracion("config.json")
        
        # Inicializar juego
        self.juego = self.inicializar_juego(config)
        
        # Inicializar UI (esto es lo único nuevo)
        self.gui_manager = GUIManager(self.WIDTH, self.HEIGHT)
        self.gui_arbol = GUIArbolAVL(self.WIDTH, self.HEIGHT)
        
        # Estado
        self.mostrar_arbol = False
        self.running = True

    def cargar_configuracion(self, ruta_json):
        try:
            with open(ruta_json, "r") as f:
                return json.load(f)
        except:
            return {"configuraciones": {}, "obstaculos": []}

    def inicializar_juego(self, config):
        conf = config.get("configuraciones", {})
        
        juego = JuegoModel(
            longitud=conf.get("distancia_total", 1000),
            energia_inicial=conf.get("energia_inicial", 100),
            velocidad=conf.get("velocidad_avance", 5),
            intervalo=conf.get("tiempo_refresco_ms", 200) / 1000.0
        )

        for obst in config.get("obstaculos", []):
            juego.agregar_obstaculo(
                obst.get("x", 0),
                carril=obst.get("carril", 0),
                tipo=obst.get("tipo", "normal")
            )

        return juego

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.mostrar_arbol = False
                return

            if self.mostrar_arbol:
                resultado = self.gui_arbol.manejar_eventos_arbol(event, self.juego.arbol_obstaculos)
                if resultado == "volver":
                    self.mostrar_arbol = False
            else:
                resultado = self.gui_manager.manejar_eventos_juego(event)
                if resultado == "mostrar_arbol":
                    self.mostrar_arbol = True

    def actualizar_juego(self):
        if self.mostrar_arbol:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.juego.carro.mover_arriba()
        if keys[pygame.K_DOWN]: self.juego.carro.mover_abajo()
        if keys[pygame.K_SPACE]: self.juego.carro.saltar()

        self.juego.carro.actualizar_salto()
        for obst in self.juego.carretera.obstaculos:
            obst.mover(self.juego.velocidad)
        
        x_min = max(0, self.juego.carro.x - 100)
        x_max = self.juego.carro.x + self.WIDTH
        self.juego.actualizar_obstaculos_visibles(x_min, x_max)
        
        self.juego.verificar_colisiones()

    def dibujar(self):
        if self.mostrar_arbol:
            self.gui_arbol.dibujar_arbol_completo(self.screen, self.juego.arbol_obstaculos)
        else:
            self.gui_manager.dibujar_juego(self.screen, self.juego)

    def run(self):
        while self.running:
            self.manejar_eventos()
            self.actualizar_juego()
            self.dibujar()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    juego = GamePygame()
    juego.run()