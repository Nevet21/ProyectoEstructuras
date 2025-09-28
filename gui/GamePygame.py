import pygame
import os
import sys
import json
import random
import threading
import queue
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.Juego import JuegoModel
from gui.GUIArbolAVL import GUIArbolAVL
from gui.GUIManager import GUIManager
from gui.ArbolLayout import ArbolLayoutManager

class GamePygame:
    def __init__(self, width=1000, height=600):
        pygame.init()

        # --- Layout: panel juego (izq) + panel árbol (der)
        self.GAME_WIDTH = 800   # ancho del área del juego
        self.TREE_WIDTH = 600  # ancho del panel donde se dibuja el árbol
        self.WIDTH, self.HEIGHT = self.GAME_WIDTH + self.TREE_WIDTH, height

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera con Árbol AVL")
        self.clock = pygame.time.Clock()

        # Cargar configuración
        config = self.cargar_configuracion("config.json")

        # Inicializar juego
        self.juego = self.inicializar_juego(config)

        # Inicializar GUI (pasando tamaños de panel relevantes)
        self.gui_manager = GUIManager(self.GAME_WIDTH, self.HEIGHT)
        self.gui_arbol = GUIArbolAVL(self.TREE_WIDTH, self.HEIGHT)
        self.layout_manager = ArbolLayoutManager(self.TREE_WIDTH, self.HEIGHT)

        # Estado del juego
        self.running = True
        self.ultima_generacion_x = 100

        # Cola y lock para comunicación y seguridad entre threads
        # -> El hilo principal encola tareas para el thread del árbol (por ejemplo insertar)
        self.tree_queue = queue.Queue()
        # Lock para proteger acceso concurrente al árbol (lectura/escritura)
        self.arbol_lock = threading.Lock()

        # Lanzar thread del árbol (daemon para que no bloquee cierre)
        self.tree_thread = threading.Thread(target=self._arbol_worker, daemon=True)
        self.tree_thread.start()

    # ------------------ Config y Juego ------------------
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

    # --------------- Worker del árbol (thread) ---------------
    def _arbol_worker(self):
        """
        Hilo que procesa pedidos de actualización del árbol.
        Recibe mensajes desde self.tree_queue en forma de tuplas:
          ("insertar", value) -> insertar en el AVL
          ("rebuild_from_list", lista) -> reconstruir/actualizar árbol (ejemplo)
          ("stop", None) -> parar (no necesario si daemon)
        """
        while self.running:
            try:
                # Espera por una tarea (timeout para permitir chequear self.running)
                tarea = self.tree_queue.get(timeout=0.5)
            except queue.Empty:
                # Aquí podrías hacer mantenimiento periódico si lo deseas
                continue

            if tarea is None:
                continue

            accion, payload = tarea

            try:
                if accion == "insertar":
                    # Protegemos al modificar el árbol
                    with self.arbol_lock:
                        # asumimos que juego.arbol_obstaculos tiene método insertar
                        self.juego.arbol_obstaculos.insertar(payload)
                    # debug
                    print(f"🌳 [thread] Insertado en AVL: {payload}")

                elif accion == "rebuild_from_list":
                    # reconstruir o actualizar con una lista de valores (ejemplo)
                    with self.arbol_lock:
                        # el método exacto depende de tu implementación del AVL
                        # Aquí solo damos una idea: vaciar y volver a insertar
                        try:
                            self.juego.arbol_obstaculos.clear()  # si existe
                        except Exception:
                            pass
                        for v in payload:
                            self.juego.arbol_obstaculos.insertar(v)
                    print("🌳 [thread] Árbol reconstruido desde lista")

                elif accion == "stop":
                    break

                # marca la tarea como hecha
                self.tree_queue.task_done()

            except Exception as e:
                print(f"❌ Error en worker del árbol: {e}")

    # ------------------ Generación obstáculos ------------------
    def generar_obstaculos_dinamicos(self):
        """Genera obstáculos dinámicamente - versión simplificada"""
        if self.juego.carro.x >= self.ultima_generacion_x:
            x_min = self.juego.carro.x + 300
            x_max = x_min + 400

            print(f"🎮 GENERANDO desde GamePygame: {x_min}-{x_max}")

            num_obstaculos = random.randint(2, 4)
            for i in range(num_obstaculos):
                carril = random.randint(0, 2)
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                x_pos = random.randint(x_min, x_max)
                obst = self.juego.agregar_obstaculo(x_pos, carril, tipo)

                # Encolar inserción al AVL en el thread del árbol (usa x_pos o un id)
                # El valor que insertes depende de cómo identifiques nodos en tu AVL.
                # Aquí insertamos x_pos como ejemplo.
                obstaculo_obj = self.juego.agregar_obstaculo(x_pos, carril, tipo)
                if obstaculo_obj:
                    # Enviar todos los parámetros que necesita ArbolAVL.insertar()
                    self.tree_queue.put(("insertar", x_pos, carril, tipo, obstaculo_obj.dano, obstaculo_obj))

            self.ultima_generacion_x = self.juego.carro.x + 200  # Siguiente en 200px

    def verificar_obstaculos_estaticos(self):
        """Verifica que los obstáculos NO se muevan"""
        if hasattr(self, 'ultimas_posiciones'):
            for i, obst in enumerate(self.juego.carretera.obstaculos[:3]):
                if i < len(self.ultimas_posiciones):
                    if obst.x != self.ultimas_posiciones[i]:
                        print(f"❌ ¡ALERTA! Obstáculo {i} se MOVIÓ de {self.ultimas_posiciones[i]} a {obst.x}")

        self.ultimas_posiciones = [obst.x for obst in self.juego.carretera.obstaculos[:3]]

    # ------------------ Eventos ------------------
    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.juego.toggle_pausa()
                    pass
                elif event.key == pygame.K_r:  # Reiniciar juego
                    self.juego.reiniciar()
                    self.ultima_generacion_x = 100
                    print("🔄 Juego reiniciado")
                elif event.key == pygame.K_g:
                    # Forzar generación (y encolar inserciones correspondientes)
                    self.generar_obstaculos_dinamicos()
                elif event.key == pygame.K_d:
                    print(f"🔍 Carro: X={self.juego.carro.x}, Carril={self.juego.carro.carril}")
                    print(f"🔍 Energía: {self.juego.energia}%, Obstáculos: {len(self.juego.carretera.obstaculos)}")

                # Controles de movimiento con KEYDOWN
                elif event.key == pygame.K_UP:
                    self.juego.carro.mover_arriba()
                elif event.key == pygame.K_DOWN:
                    self.juego.carro.mover_abajo()
                elif event.key == pygame.K_SPACE:
                    self.juego.carro.saltar()
                                # ---- Recorridos del árbol: I, P, O (se reenviarán al layout manager) ----
                elif event.key in (pygame.K_i, pygame.K_p, pygame.K_o, pygame.K_b):
                    # Tomamos la raíz de forma segura
                    with self.arbol_lock:
                        arbol = getattr(self.juego, "arbol_obstaculos", None)
                        raiz = getattr(arbol, "raiz", None) if arbol is not None else None

                        if raiz:
                            if event.key == pygame.K_i:
                                self.layout_manager.iniciar_recorrido("inorden", raiz)
                            elif event.key == pygame.K_p:
                                self.layout_manager.iniciar_recorrido("preorden", raiz)
                            elif event.key == pygame.K_o:
                                self.layout_manager.iniciar_recorrido("postorden", raiz)
                            elif event.key == pygame.K_b:
                                self.layout_manager.iniciar_recorrido("anchura", raiz)                            
                        else:
                            print("ℹ️ No hay raíz del árbol para recorrer.")


            # Eventos del mouse / interacción: decidir si se envía al panel del árbol
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                mouse_x, mouse_y = event.pos
                if mouse_x > self.GAME_WIDTH:
                    # Evento para panel árbol -> proteger el acceso al árbol mientras se maneja
                    with self.arbol_lock:
                        resultado = self.gui_arbol.manejar_eventos_arbol(event, self.juego.arbol_obstaculos)
                    # si tu gui_arbol devuelve "rebuild" o algo, lo puedes encolar:
                    if resultado == "rebuild":
                        # ejemplo: reconstruir árbol a partir de lista de obstáculos
                        lista = [o.x for o in self.juego.carretera.obstaculos]
                        self.tree_queue.put(("rebuild_from_list", lista))
                else:
                    # Evento para la UI del juego
                    self.gui_manager.manejar_eventos_juego(event)

    # ------------------ Actualización por frame ------------------
    def actualizar_juego(self):
        """Actualización - SIN bloquear dibujo del árbol"""
        if not self.juego.en_ejecucion or self.juego.terminado:
            return  

        # Solo el carro se mueve
        self.juego.carro.avanzar()
        self.juego.carro.actualizar_salto()

        # Generar obstáculos (esto encola inserciones al árbol)
        self.generar_obstaculos_dinamicos()

        # (Opcional) verificar que los obstáculos no se muevan
        self.verificar_obstaculos_estaticos()

        # Actualizar visibilidad y colisiones
        x_min = max(0, self.juego.carro.x - 100)
        x_max = self.juego.carro.x + self.GAME_WIDTH + 200
        self.juego.actualizar_obstaculos_visibles(x_min, x_max)
        self.juego.verificar_colisiones()

        # Nota: no esperes la cola del árbol aquí. El thread la procesa.
        # Si necesitas resultados del thread, podrías usar otra queue de retorno.

        # Debug de movimiento (opcional)
        if pygame.time.get_ticks() % 1000 < 30:
            print("=== VERIFICACIÓN MOVIMIENTO ===")
            print(f"🚗 Carro X: {self.juego.carro.x} (debe AUMENTAR)")
            if self.juego.carretera.obstaculos:
                obst = self.juego.carretera.obstaculos[0]
                print(f"📍 Obstáculo X: {obst.x} (debe ser FIJO)")
                if obst.x < 500:
                    print(f"❌ ¡ERROR! Obstáculo se movió a {obst.x}")

    # ------------------ Dibujo ------------------
    def dibujar(self):
        # Fondo general
        self.screen.fill((0, 0, 0))

        # --- Panel del juego (izquierda) ---
        game_surface = pygame.Surface((self.GAME_WIDTH, self.HEIGHT))
        self.gui_manager.dibujar_juego(game_surface, self.juego)
        self.screen.blit(game_surface, (0, 0))

        # --- Panel del árbol (derecha) ---
        tree_surface = pygame.Surface((self.TREE_WIDTH, self.HEIGHT), pygame.SRCALPHA)
        tree_surface.fill((30, 30, 30))  # fondo del panel (puedes poner transparente)
        # Protegemos lectura del árbol mientras lo dibujamos
        with self.arbol_lock:
            self.gui_arbol.dibujar_arbol_completo(tree_surface, self.juego.arbol_obstaculos)
        self.screen.blit(tree_surface, (self.GAME_WIDTH, 0))

        # --- Mensajes por encima del juego (game over) ---
        if self.juego.terminado:
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.GAME_WIDTH//2, self.HEIGHT//2))
            self.screen.blit(text, text_rect)

            font_small = pygame.font.Font(None, 36)
            restart_text = font_small.render("Presiona R para reiniciar", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.GAME_WIDTH//2, self.HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)

# ------------------ Loop principal ------------------
    def run(self):
        print("🎮 Juego iniciado - Controles:")
        print("🎮 Flechas: Moverse, ESPACIO: Saltar")
        print("🎮 R: Reiniciar, G: Generar obstáculos, D: Debug info")
        print("🎮 I: Inorden, P: Preorden, O: Postorden")
        print("🎮 ESC: Volver al juego")

        try:
            while self.running:
                self.manejar_eventos()
                self.actualizar_juego()

                # 🔹 Aquí llamamos a la actualización del recorrido
                self.layout_manager.actualizar_recorrido()

                self.dibujar()

                pygame.display.flip()
                self.clock.tick(30)  # FPS
        finally:
            # limpieza (si quieres esperar que la cola termine)
            self.running = False
            try:
                self.tree_queue.put(("stop", None))
            except Exception:
                pass
            pygame.quit()


if __name__ == "__main__":
    juego = GamePygame()
    juego.run()