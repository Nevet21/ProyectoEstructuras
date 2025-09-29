# Reemplaza el contenido de tu archivo GamePygame.py por esta clase (o aplica los cambios puntuales).
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
from gui.MenuEliminar import MenuEliminar


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
        self.tree_queue = queue.Queue()
        self.arbol_lock = threading.Lock()

        # Lanzar thread del árbol (daemon para que no bloquee cierre)
        self.tree_thread = threading.Thread(target=self._arbol_worker, daemon=True)
        self.tree_thread.start()

        # Nuevo estado para gestión del árbol
        self.mostrar_gestion_arbol = False

        # Estados para insertar / eliminar con UI en pantalla
        self.modo_insertar = False
        self.modo_eliminar = False
        self.input_activo = False        # cuando mostramos cuadro de texto
        self.input_mode = None          # "insert" o "delete" o None
        self.buffer_input = ""          # texto del input (ej: "450,1")
        self.selection_list = []        # lista de nodos cuando eliminamos
        self.selection_index = 0        # índice seleccionado en la lista

        # 1. Definir fuente primero
        self.font = pygame.font.SysFont("Arial", 20)  

        # 2. Ahora sí crear el menú
        self.menu_eliminar = MenuEliminar(self, self.font)
        

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

    # ------------------ Worker del árbol (thread) ---------------
    def _arbol_worker(self):
        while self.running:
            try:
                tarea = self.tree_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if tarea is None:
                continue

            accion, payload = tarea
            try:
                if accion == "insertar":
                    # Si fuera a usar queue para insertar, payload puede ser (x,y,tipo,dano,obst)
                    with self.arbol_lock:
                        if isinstance(payload, (tuple, list)):
                            try:
                                self.juego.arbol_obstaculos.insertar(*payload)
                            except TypeError:
                                # fallback: intentar insertar solo el objeto
                                self.juego.arbol_obstaculos.insertar(payload)
                        else:
                            # payload es el objeto obstáculo o un valor
                            self.juego.arbol_obstaculos.insertar(payload)
                    print(f"🌳 [thread] Insertado en AVL via queue: {payload}")

                elif accion == "rebuild_from_list":
                    with self.arbol_lock:
                        try:
                            self.juego.arbol_obstaculos.raiz = None
                        except Exception:
                            pass
                        for v in payload:
                            # espera lista de (x,y,tipo,dano,obst) o de obstacles
                            if isinstance(v, (tuple, list)):
                                self.juego.arbol_obstaculos.insertar(*v)
                            else:
                                # si v es obstáculo creado por Juego.agregar_obstaculo
                                self.juego.arbol_obstaculos.insertar(v.x, v.carril, v.tipo, v.dano, v)
                    print("🌳 [thread] Árbol reconstruido desde lista")

                elif accion == "stop":
                    break

                self.tree_queue.task_done()
            except Exception as e:
                print(f"❌ Error en worker del árbol: {e}")

    # ------------------ Generación obstáculos ------------------
    def generar_obstaculos_dinamicos(self):
        """Genera obstáculos dinámicamente - versión corregida"""
        if self.juego.carro.x >= self.ultima_generacion_x:
            x_min = self.juego.carro.x + 300
            x_max = x_min + 400

            num_obstaculos = random.randint(1, 3)
            for i in range(num_obstaculos):
                carril = random.randint(0, 2)
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                x_pos = random.randint(x_min, x_max)

                # --- crear una sola vez el obstáculo (agregar_obstaculo ya inserta en el AVL) ---
                obst_obj = self.juego.agregar_obstaculo(x_pos, carril, tipo)
                if obst_obj:
                    print(f"✅ Generado dinámico: {tipo} en ({x_pos},{carril})")
                    # ya fue insertado en arbol dentro de agregar_obstaculo, no encolamos nada

            self.ultima_generacion_x = self.juego.carro.x + 200

    def verificar_obstaculos_estaticos(self):
        if hasattr(self, 'ultimas_posiciones'):
            for i, obst in enumerate(self.juego.carretera.obstaculos[:3]):
                if i < len(self.ultimas_posiciones):
                    if obst.x != self.ultimas_posiciones[i]:
                        print(f"❌ ¡ALERTA! Obstáculo {i} se MOVIÓ de {self.ultimas_posiciones[i]} a {obst.x}")
        self.ultimas_posiciones = [obst.x for obst in self.juego.carretera.obstaculos[:3]]

    # ------------------ Helpers interno ------------------
    def _make_local_event(self, event):
        """Convierte un event con pos global a uno con pos local (panel árbol),
           restando self.GAME_WIDTH en x."""
        if hasattr(event, "pos"):
            d = event.dict.copy()
            gx, gy = event.pos
            d['pos'] = (gx - self.GAME_WIDTH, gy)
            return pygame.event.Event(event.type, d)
        return event

    # ------------------ Eventos ------------------
    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # ========== EVENTOS GLOBALES (siempre disponibles) ==========
            if event.type == pygame.KEYDOWN:
                # Tecla R siempre disponible para reiniciar
                if event.key == pygame.K_r:
                    self.juego.reiniciar()
                    self.ultima_generacion_x = 100
                    self.mostrar_gestion_arbol = False
                    self.juego.en_ejecucion = True
                    self.gui_arbol.desactivar_modos()
                    self.input_activo = False
                    self.input_mode = None
                    self.menu_eliminar.desactivar()
                    print("🔄 Juego reiniciado")
                    continue
                
                # Tecla ESC para activar/desactivar modo gestión
                elif event.key == pygame.K_ESCAPE:
                    # Si el juego terminó, ESC puede activar/desactivar gestión manualmente
                    if self.juego.terminado:
                        if self.mostrar_gestion_arbol:
                            # Salir del modo gestión
                            self.mostrar_gestion_arbol = False
                            self.gui_arbol.desactivar_modos()
                            self.input_activo = False
                            self.input_mode = None
                            self.menu_eliminar.desactivar()
                            print("🔙 Saliendo del modo gestión (juego terminado)")
                        else:
                            # Entrar al modo gestión
                            self.mostrar_gestion_arbol = True
                            print("🌳 Activando modo gestión del árbol (juego terminado)")
                    else:
                        # Si el juego está activo, ESC alterna entre juego y gestión
                        if self.mostrar_gestion_arbol:
                            # Salir del modo gestión
                            self.mostrar_gestion_arbol = False
                            self.juego.en_ejecucion = True
                            self.gui_arbol.desactivar_modos()
                            self.input_activo = False
                            self.input_mode = None
                            self.menu_eliminar.desactivar()
                            print("▶️ Volviendo al juego desde gestión del árbol")
                        else:
                            # Entrar al modo gestión
                            self.mostrar_gestion_arbol = True
                            self.juego.en_ejecucion = False
                            print("⏸️ Juego pausado - Modo gestión del árbol activado")
                    continue

                # Resto de teclas del juego (solo si no está en modo gestión)
                if not self.mostrar_gestion_arbol and self.juego.en_ejecucion:
                    if event.key == pygame.K_g:
                        self.generar_obstaculos_dinamicos()
                    elif event.key == pygame.K_d:
                        print(f"🔍 Carro: X={self.juego.carro.x}, Carril={self.juego.carro.carril}")
                        print(f"🔍 Energía: {self.juego.energia}%, Obstáculos: {len(self.juego.carretera.obstaculos)}")
                        with self.arbol_lock:
                            if self.juego.arbol_obstaculos and self.juego.arbol_obstaculos.raiz:
                                nodos = self.juego.arbol_obstaculos.obtener_todos_nodos()
                                print(f"🌳 Nodos en árbol AVL: {len(nodos)}")
                    elif event.key == pygame.K_UP:
                        self.juego.carro.mover_arriba()
                    elif event.key == pygame.K_DOWN:
                        self.juego.carro.mover_abajo()
                    elif event.key == pygame.K_SPACE:
                        self.juego.carro.saltar()
                    elif event.key in (pygame.K_i, pygame.K_p, pygame.K_o, pygame.K_b):
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

            # ========== MODO GESTIÓN DEL ÁRBOL (cuando está activo) ==========
            if self.mostrar_gestion_arbol:
                # Si tenemos un input activo (overlay), capturamos teclado aquí
                if self.input_activo and event.type == pygame.KEYDOWN:
                    # Manejo del modo eliminación
                    if self.input_mode == "delete":
                        self.menu_eliminar.manejar_evento(event)
                        # Si el menú se desactivó, limpiar estados
                        if not self.menu_eliminar.activo:
                            self.input_activo = False
                            self.input_mode = None
                            self.modo_eliminar = False
                        continue

                    # Modo insert -> manejo de texto simple
                    if self.input_mode == "insert":
                        if event.key == pygame.K_RETURN:
                            self._procesar_input_en_overlay(self.buffer_input)
                            self.buffer_input = ""
                            self.input_activo = False
                            self.input_mode = None
                        elif event.key == pygame.K_BACKSPACE:
                            self.buffer_input = self.buffer_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            # ESC también cierra el input overlay
                            self.input_activo = False
                            self.input_mode = None
                            self.modo_insertar = False
                            self.buffer_input = ""
                        else:
                            ch = event.unicode
                            if ch.isdigit() or ch in ",-":
                                self.buffer_input += ch
                        continue

                # Manejar eventos del panel árbol
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    mx, my = event.pos
                    if mx > self.GAME_WIDTH:
                        local_event = self._make_local_event(event)
                        with self.arbol_lock:
                            resultado = self.gui_arbol.manejar_eventos_arbol(local_event, self.juego.arbol_obstaculos)
                        
                        if resultado:
                            if resultado == "modo_insercion":
                                self.modo_insertar = True
                                self.modo_eliminar = False
                                self.input_activo = True
                                self.input_mode = "insert"
                                self.buffer_input = ""
                                print("🌳 Modo inserción activado")
                            elif resultado == "modo_eliminacion":
                                self.modo_eliminar = True
                                self.modo_insertar = False
                                with self.arbol_lock:
                                    nodos = self.juego.arbol_obstaculos.obtener_todos_nodos()
                                self.selection_list = [(n.x, n.y, n.tipo) for n in nodos]
                                self.selection_index = 0
                                self.input_activo = True
                                self.input_mode = "delete"
                                self.buffer_input = ""
                                self.menu_eliminar.activar()
                                print(f"🌳 Modo eliminación activado - {len(self.selection_list)} nodos")
                            elif resultado == "continuar":
                                # Solo permitir "continuar" si el juego NO ha terminado
                                if not self.juego.terminado:
                                    self.mostrar_gestion_arbol = False
                                    self.juego.en_ejecucion = True
                                    self.gui_arbol.desactivar_modos()
                                    self.menu_eliminar.desactivar()
                                    print("▶️ Volviendo al juego")
                                else:
                                    print("⚠️ Juego terminado - Usa R para reiniciar")
                            elif isinstance(resultado, tuple) and resultado[0] == "nodo_seleccionado":
                                nodo = resultado[1]
                                print(f"🎯 Nodo seleccionado para eliminar: ({nodo.x},{nodo.y}) - {nodo.tipo}")
                                with self.arbol_lock:
                                    self.juego.arbol_obstaculos.eliminar(nodo.x, nodo.y)
                                self.juego.carretera.obstaculos = [
                                    o for o in self.juego.carretera.obstaculos if not (o.x == nodo.x and o.carril == nodo.y)
                                ]
                                print(f"🗑️ Nodo eliminado: ({nodo.x},{nodo.y})")
                                self.gui_arbol.desactivar_modos()
                            elif isinstance(resultado, tuple) and resultado[0] == "insertar_en_posicion":
                                x, y = resultado[1]
                                x = max(0, int(x))
                                y = max(0, min(2, int(y)))
                                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                                # ✅ Usar el método de inserción sin restricciones
                                if hasattr(self.juego, 'agregar_obstaculo_modo_gestion'):
                                    nuevo = self.juego.agregar_obstaculo_modo_gestion(x, y, tipo)
                                else:
                                    nuevo = self.juego.agregar_obstaculo(x, y, tipo)
                                if nuevo:
                                    print(f"✅ Nodo insertado por click: ({x},{y}) - {tipo}")
                                    self.gui_arbol.desactivar_modos()
                                else:
                                    print(f"❌ No se pudo insertar nodo en ({x},{y})")
                        continue

                # Eventos del panel izquierdo de juego en modo gestión
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    mx, my = event.pos
                    if mx <= self.GAME_WIDTH:
                        self.gui_manager.manejar_eventos_juego(event)
                    continue

            # ========== EVENTOS NORMALES DEL JUEGO (cuando NO está en gestión) ==========
            # Eventos del mouse en juego normal
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                mx, my = event.pos
                if mx > self.GAME_WIDTH:
                    local_event = self._make_local_event(event)
                    with self.arbol_lock:
                        resultado = self.gui_arbol.manejar_eventos_arbol(local_event, self.juego.arbol_obstaculos)
                    if resultado == "rebuild":
                        lista = [o.x for o in self.juego.carretera.obstaculos]
                        self.tree_queue.put(("rebuild_from_list", lista))
                else:
                    self.gui_manager.manejar_eventos_juego(event)

            with self.arbol_lock:
                resultado_layout = self.gui_arbol.layout_manager.manejar_eventos_zoom(event)

    # ------------------ Procesamiento del input overlay ------------------
    def _procesar_input_en_overlay(self, texto):
        """Procesa la cadena 'X,Y' cuando el overlay está activo."""
        try:
            partes = texto.split(",")
            if len(partes) < 2:
                print("⚠️ Formato inválido. Usa X,Y")
                return
            x = int(partes[0].strip())
            carril = int(partes[1].strip())
            carril = max(0, min(2, carril))

            if self.input_mode == "insert":
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                if hasattr(self.juego, 'agregar_obstaculo_modo_gestion'):
                    nuevo = self.juego.agregar_obstaculo_modo_gestion(x, carril, tipo)
                else:
                    nuevo = self.juego.agregar_obstaculo(x, carril, tipo)
                if nuevo:
                    print(f"✅ Insertado (overlay): ({x},{carril}) tipo {tipo}")
                else:
                    print(f"❌ No se pudo insertar en ({x},{carril})")
                nuevo = self.juego.agregar_obstaculo(x, carril, tipo)
                if nuevo:
                    print(f"✅ Insertado (overlay): ({x},{carril}) tipo {tipo}")
                else:
                    print(f"❌ No se pudo insertar en ({x},{carril})")
            elif self.input_mode == "delete":
                # buscar en carretera
                objetivo = next((o for o in self.juego.carretera.obstaculos if o.x == x and o.carril == carril), None)
                if objetivo:
                    # eliminar del árbol y de la carretera
                    with self.arbol_lock:
                        self.juego.arbol_obstaculos.eliminar(objetivo.x, objetivo.carril)
                    self.juego.carretera.obstaculos = [o for o in self.juego.carretera.obstaculos if not (o.x == x and o.carril == carril)]
                    print(f"🗑️ Eliminado (overlay): ({x},{carril})")
                else:
                    print("⚠️ No se encontró obstáculo en esas coordenadas.")
        except Exception as e:
            print("Error procesando input:", e)
        finally:
            # limpiar estado
            self.input_activo = False
            self.input_mode = None
            self.modo_insertar = False
            self.modo_eliminar = False
            self.buffer_input = ""

    # ------------------ Actualización por frame ------------------
    def actualizar_juego(self):
        # Si el juego terminó, NO activar modo gestión automáticamente
        if self.juego.terminado:
            # Solo asegurarnos de que el juego esté pausado
            self.juego.en_ejecucion = False
            return

        # Si está en pausa -> no avanzar
        if not self.juego.en_ejecucion:
            return

        # ✅ Solo aquí avanza el juego normalmente (cuando NO terminó y está en ejecución)
        self.generar_obstaculos_dinamicos()
        self.juego.update(self.WIDTH)

    # ------------------ Dibujo ------------------
    def dibujar(self):
        self.screen.fill((0, 0, 0))

        # Panel izquierdo
        game_surface = pygame.Surface((self.GAME_WIDTH, self.HEIGHT))
        self.gui_manager.dibujar_juego(game_surface, self.juego)
        self.screen.blit(game_surface, (0, 0))

        # Panel árbol (derecha)
        tree_surface = pygame.Surface((self.TREE_WIDTH, self.HEIGHT), pygame.SRCALPHA)
        tree_surface.fill((30, 30, 30))
        with self.arbol_lock:
            self.gui_arbol.dibujar_arbol_completo(tree_surface, self.juego.arbol_obstaculos)
        self.screen.blit(tree_surface, (self.GAME_WIDTH, 0))

        # Dibujar GAME OVER si el juego terminó (SIN overlay oscuro)
        if self.juego.terminado and not self.mostrar_gestion_arbol:
            # Solo texto GAME OVER, sin overlay oscuro
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 60))
            self.screen.blit(text, text_rect)

            font_small = pygame.font.Font(None, 36)
            restart_text = font_small.render("Presiona R para reiniciar", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
            self.screen.blit(restart_text, restart_rect)

            gestion_text = font_small.render("ESC para modo gestión del árbol", True, (200, 200, 200))
            gestion_rect = gestion_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 40))
            self.screen.blit(gestion_text, gestion_rect)

        # Overlay de gestión del árbol (si está activo) - SOLO aquí se oscurece
        if self.mostrar_gestion_arbol:
            # Overlay oscuro para modo gestión
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Oscuro con transparencia
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 36)
            
            # Mensaje diferente dependiendo del estado del juego
            if self.juego.terminado:
                texto_linea1 = font.render("MODO GESTIÓN DEL ÁRBOL - Juego terminado", True, (255, 255, 0))
                texto_linea2 = font.render("Usa los botones para insertar/eliminar nodos", True, (255, 200, 0))
                texto_linea3 = font.render("ESC para salir - R para reiniciar", True, (200, 200, 0))
            else:
                texto_linea1 = font.render("MODO GESTIÓN DEL ÁRBOL - Juego pausado", True, (255, 255, 255))
                texto_linea2 = font.render("Usa los botones para insertar/eliminar nodos", True, (200, 200, 200))
                texto_linea3 = font.render("ESC para continuar el juego", True, (200, 200, 200))
            
            texto_rect1 = texto_linea1.get_rect(center=(self.WIDTH//2, 30))
            texto_rect2 = texto_linea2.get_rect(center=(self.WIDTH//2, 70))
            texto_rect3 = texto_linea3.get_rect(center=(self.WIDTH//2, 110))
            self.screen.blit(texto_linea1, texto_rect1)
            self.screen.blit(texto_linea2, texto_rect2)
            self.screen.blit(texto_linea3, texto_rect3)

            # Si hay un input activo, dibujar cuadro
            if self.input_activo:
                if self.input_mode == "insert":
                    self._draw_input_box("Insertar (X,Y):", self.buffer_input)
                elif self.input_mode == "delete":
                    self.menu_eliminar.dibujar(self.screen)


    def _draw_input_box(self, prompt, content):
        font = pygame.font.Font(None, 28)
        box_w, box_h = 360, 90
        box_surf = pygame.Surface((box_w, box_h))
        box_surf.fill((40, 40, 60))
        pygame.draw.rect(box_surf, (200, 200, 200), (0, 0, box_w, box_h), 2)
        prompt_s = font.render(prompt, True, (255, 255, 255))
        content_s = font.render(content + ("|" if int(time.time()*2)%2==0 else ""), True, (255, 255, 0))
        box_surf.blit(prompt_s, (10, 8))
        box_surf.blit(content_s, (10, 40))
        # centrar en pantalla
        x = (self.WIDTH - box_w)//2
        y = (self.HEIGHT - box_h)//2
        self.screen.blit(box_surf, (x, y))


    # ------------------ Loop principal ------------------
    def run(self):
        print("🎮 Juego iniciado - Controles: Flechas, ESPACIO, R, ESC")
        try:
            while self.running:
                self.manejar_eventos()
                self.actualizar_juego()
                self.layout_manager.actualizar_recorrido()
                self.dibujar()
                pygame.display.flip()
                self.clock.tick(30)
        finally:
            self.running = False
            try:
                self.tree_queue.put(("stop", None))
            except Exception:
                pass
            pygame.quit()

if __name__ == "__main__":
    juego = GamePygame()
    juego.run()
