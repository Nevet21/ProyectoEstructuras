import pygame
import os
import sys
import json
import random

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
        
        # Inicializar UI
        self.gui_manager = GUIManager(self.WIDTH, self.HEIGHT)
        self.gui_arbol = GUIArbolAVL(self.WIDTH, self.HEIGHT)
        
        # Estado
        self.mostrar_arbol = False
        self.running = True
        self.ultima_generacion_x = 100

    def cargar_configuracion(self, ruta_json):
        try:
            with open(ruta_json, "r") as f:
                config = json.load(f)
            print("✅ Configuración cargada correctamente")
            return config
        except Exception as e:
            print(f"❌ Error cargando JSON: {e}")
            return {"configuraciones": {}, "obstaculos": []}

    def inicializar_juego(self, config):
        conf = config.get("configuraciones", {})
        
        juego = JuegoModel(
            longitud=conf.get("distancia_total", 1000),
            energia_inicial=conf.get("energia_inicial", 100),
            velocidad=conf.get("velocidad_avance", 5),
            intervalo=conf.get("tiempo_refresco_ms", 200) / 1000.0,
            config_json=config
        )
        
        return juego

    def generar_obstaculos_dinamicos(self):
        """Genera obstáculos dinámicamente - versión simplificada"""
        # ✅ FORZAR GENERACIÓN CADA 200 PIXELES
        if self.juego.carro.x >= self.ultima_generacion_x:
            x_min = self.juego.carro.x + 300
            x_max = x_min + 400
            
            print(f"🎮 GENERANDO desde GamePygame: {x_min}-{x_max}")
            
            num_obstaculos = random.randint(2, 4)
            for i in range(num_obstaculos):
                carril = random.randint(0, 2)
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                x_pos = random.randint(x_min, x_max)
                self.juego.agregar_obstaculo(x_pos, carril, tipo)
            
            self.ultima_generacion_x = self.juego.carro.x + 200  # Siguiente en 200px

    def verificar_obstaculos_estaticos(self):
            """Verifica que los obstáculos NO se muevan"""
            if hasattr(self, 'ultimas_posiciones'):
                # Comparar con posiciones anteriores
                for i, obst in enumerate(self.juego.carretera.obstaculos[:3]):
                    if i < len(self.ultimas_posiciones):
                        if obst.x != self.ultimas_posiciones[i]:
                            print(f"❌ ¡ALERTA! Obstáculo {i} se MOVIÓ de {self.ultimas_posiciones[i]} a {obst.x}")
            
            # Guardar posiciones actuales para la siguiente verificación
            self.ultimas_posiciones = [obst.x for obst in self.juego.carretera.obstaculos[:3]]

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.mostrar_arbol = False
                elif event.key == pygame.K_r:  # Reiniciar juego
                    self.juego.reiniciar()
                    self.ultima_generacion_x = 100
                    print("🔄 Juego reiniciado")
                elif event.key == pygame.K_g:
                    self.generar_obstaculos_dinamicos()
                elif event.key == pygame.K_d:
                    print(f"🔍 Carro: X={self.juego.carro.x}, Carril={self.juego.carro.carril}")
                    print(f"🔍 Energía: {self.juego.energia}%, Obstáculos: {len(self.juego.carretera.obstaculos)}")
                
                # ✅ Controles de movimiento con KEYDOWN
                elif event.key == pygame.K_UP:
                    self.juego.carro.mover_arriba()
                elif event.key == pygame.K_DOWN:
                    self.juego.carro.mover_abajo()
                elif event.key == pygame.K_SPACE:
                    self.juego.carro.saltar()

            # ✅ Manejo de árbol si está activo
            if self.mostrar_arbol:
                resultado = self.gui_arbol.manejar_eventos_arbol(event, self.juego.arbol_obstaculos)
                if resultado == "volver":
                    self.mostrar_arbol = False
            else:
                resultado = self.gui_manager.manejar_eventos_juego(event)
                if resultado == "mostrar_arbol":
                    self.mostrar_arbol = True


    def actualizar_juego(self):
        """Actualización - SIN movimiento de obstáculos"""
        if self.mostrar_arbol or self.juego.terminado:
            return

        # ✅ SOLO EL CARRO SE MUEVE
        self.juego.carro.avanzar()
        self.juego.carro.actualizar_salto()

        # ✅ Generar obstáculos (estáticos)
        self.generar_obstaculos_dinamicos()

        # ❌ ¡ELIMINAR CUALQUIER CÓDIGO QUE MUEVA OBSTÁCULOS!

        # ✅ Actualizar visibilidad
        x_min = max(0, self.juego.carro.x - 100)
        x_max = self.juego.carro.x + self.WIDTH + 200
        self.juego.actualizar_obstaculos_visibles(x_min, x_max)
        self.juego.verificar_colisiones()
        
        # ✅ Debug de movimiento
        if pygame.time.get_ticks() % 1000 < 30:
            print("=== VERIFICACIÓN MOVIMIENTO ===")
            print(f"🚗 Carro X: {self.juego.carro.x} (debe AUMENTAR)")
            if self.juego.carretera.obstaculos:
                obst = self.juego.carretera.obstaculos[0]
                print(f"📍 Obstáculo X: {obst.x} (debe ser FIJO)")
                if obst.x < 500:  # Si es menor que 500, se está moviendo
                    print(f"❌ ¡ERROR! Obstáculo se movió a {obst.x}")


    def dibujar(self):
        if self.mostrar_arbol:
            self.gui_arbol.dibujar_arbol_completo(self.screen, self.juego.arbol_obstaculos)
        else:
            self.gui_manager.dibujar_juego(self.screen, self.juego)
            
            # Mostrar mensaje de game over
            if self.juego.terminado:
                font = pygame.font.Font(None, 74)
                text = font.render("GAME OVER", True, (255, 0, 0))
                text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
                self.screen.blit(text, text_rect)
                
                font_small = pygame.font.Font(None, 36)
                restart_text = font_small.render("Presiona R para reiniciar", True, (255, 255, 255))
                restart_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
                self.screen.blit(restart_text, restart_rect)

    def run(self):
        print("🎮 Juego iniciado - Controles:")
        print("🎮 Flechas: Moverse, ESPACIO: Saltar")
        print("🎮 R: Reiniciar, G: Generar obstáculos, D: Debug info")
        print("🎮 ESC: Volver al juego")
        
        while self.running:
            self.manejar_eventos()
            self.actualizar_juego()
            self.dibujar()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        if hasattr(self.juego, 'guardar_partida_actual'):
            self.juego.guardar_partida_actual()
        pygame.quit()

if __name__ == "__main__":
    juego = GamePygame()
    juego.run()