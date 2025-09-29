import pygame

class MenuEliminar:
    """
    Menú modal para listar y eliminar nodos (10 por página).
    Este Menu espera recibir la instancia GamePygame como `juego`.
    Accede al modelo real con: self.juego.juego  (JuegoModel).
    Usa self.juego.arbol_lock para proteger operaciones en el AVL/carretera.
    """

    def __init__(self, juego, fuente):
        self.juego = juego               # instancia GamePygame
        self.fuente = fuente
        self.indice_actual = 0           # índice dentro de la página
        self.offset = 0                  # página (0 = primera)
        self.opciones_por_pagina = 10
        self.activo = False

    def activar(self):
        self.activo = True
        self.indice_actual = 0
        self.offset = 0

    def desactivar(self):
        self.activo = False

    def manejar_evento(self, event):
        """Recibe eventos (teclado) mientras el menú está activo."""
        if not self.activo:
            return

        # obtener la lista actual de nodos desde el JuegoModel
        modelo = getattr(self.juego, "juego", None)
        if modelo is None:
            return
        arbol = getattr(modelo, "arbol_obstaculos", None)
        if arbol is None:
            return

        nodos = []
        try:
            nodos = arbol.obtener_todos_nodos() or []
        except Exception:
            nodos = []

        total = len(nodos)
        if total == 0:
            # nada que hacer
            self.desactivar()
            self.juego.input_activo = False
            self.juego.input_mode = None
            self.juego.modo_eliminar = False
            return

        if event.type != pygame.KEYDOWN:
            return

        # Navegación vertical dentro de la página
        if event.key == pygame.K_UP:
            if self.indice_actual > 0:
                self.indice_actual -= 1
            else:
                # si al inicio y hay página previa, saltar a la página anterior
                if self.offset > 0:
                    self.offset -= 1
                    self.indice_actual = min(self.opciones_por_pagina - 1,
                                             total - 1 - self.offset * self.opciones_por_pagina)

        elif event.key == pygame.K_DOWN:
            max_idx = min(self.opciones_por_pagina - 1,
                          total - self.offset * self.opciones_por_pagina - 1)
            if self.indice_actual < max_idx:
                self.indice_actual += 1
            else:
                # pasar a siguiente página si existe
                total_pages = (total - 1) // self.opciones_por_pagina
                if self.offset < total_pages:
                    self.offset += 1
                    self.indice_actual = 0

        # Páginas: izquierda / derecha
        elif event.key == pygame.K_LEFT:
            if self.offset > 0:
                self.offset -= 1
                self.indice_actual = 0

        elif event.key == pygame.K_RIGHT:
            total_pages = (total - 1) // self.opciones_por_pagina
            if self.offset < total_pages:
                self.offset += 1
                self.indice_actual = 0

        # ENTER = eliminar nodo seleccionado (seguro con lock)
        elif event.key == pygame.K_RETURN:
            idx = self.offset * self.opciones_por_pagina + self.indice_actual
            if 0 <= idx < total:
                nodo = nodos[idx]
                # eliminar de forma segura
                try:
                    with self.juego.arbol_lock:
                        # eliminar del array de carretera (si existe)
                        modelo.carretera.obstaculos = [
                            o for o in modelo.carretera.obstaculos
                            if not (o.x == nodo.x and o.carril == getattr(nodo, 'carril', getattr(nodo, 'y', None)))
                        ]
                        # eliminar del AVL (usa la firma que tenga tu árbol: aquí pasamos x,y)
                        # algunos implementan eliminar(x) o eliminar(x,y). Intentamos con x,y
                        try:
                            modelo.arbol_obstaculos.eliminar(nodo.x, getattr(nodo, 'carril', getattr(nodo, 'y', None)))
                        except TypeError:
                            # fallback por si la firma es diferente
                            try:
                                modelo.arbol_obstaculos.eliminar(nodo.x)
                            except Exception as e:
                                print("❌ Error eliminando del AVL:", e)
                except Exception as e:
                    print("❌ Error al eliminar nodo:", e)
                else:
                    print(f"🗑️ Nodo eliminado: ({nodo.x},{getattr(nodo,'carril',getattr(nodo,'y',None))}) - {getattr(nodo,'tipo', '')}")

                # refresh: si ya no quedan nodos cerramos el menú
                try:
                    nodos_after = modelo.arbol_obstaculos.obtener_todos_nodos() if getattr(modelo.arbol_obstaculos, "raiz", None) else []
                except Exception:
                    nodos_after = []
                if not nodos_after:
                    self.desactivar()
                    self.juego.input_activo = False
                    self.juego.input_mode = None
                    self.juego.modo_eliminar = False
                else:
                    total_after = len(nodos_after)
                    total_pages_after = (total_after - 1) // self.opciones_por_pagina
                    if self.offset > total_pages_after:
                        self.offset = total_pages_after
                    # asegurar índice válido
                    max_idx_after = min(self.opciones_por_pagina - 1,
                                        total_after - self.offset * self.opciones_por_pagina - 1)
                    self.indice_actual = min(self.indice_actual, max_idx_after)

        # ESC = cerrar modal sin borrar
        elif event.key == pygame.K_ESCAPE:
            self.desactivar()
            self.juego.input_activo = False
            self.juego.input_mode = None
            self.juego.modo_eliminar = False
            print("🔙 Saliste del modo eliminación")

    def dibujar(self, pantalla):
        """Dibuja modal centrado con la página actual."""
        if not self.activo:
            return

        modelo = getattr(self.juego, "juego", None)
        if modelo is None:
            return
        arbol = getattr(modelo, "arbol_obstaculos", None)
        if arbol is None:
            return

        try:
            nodos = arbol.obtener_todos_nodos() or []
        except Exception:
            nodos = []

        # fondo semitransparente
        overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pantalla.blit(overlay, (0, 0))

        # cuadro centrado
        ancho, alto = 520, 420
        cx, cy = pantalla.get_width() // 2, pantalla.get_height() // 2
        rect = pygame.Rect(cx - ancho // 2, cy - alto // 2, ancho, alto)
        pygame.draw.rect(pantalla, (30, 30, 30), rect)
        pygame.draw.rect(pantalla, (200, 200, 200), rect, 3)

        # título y conteo
        total = len(nodos)
        titulo = self.fuente.render(f"Juego pausado - Modo gestión del árbol activado", True, (255, 255, 0))
        pantalla.blit(titulo, (rect.left + 12, rect.top + 8))
        sub = self.fuente.render(f"Nodos disponibles para eliminar: {total}  (←/→ páginas)", True, (200, 200, 200))
        pantalla.blit(sub, (rect.left + 12, rect.top + 36))

        if total == 0:
            texto = self.fuente.render("No hay nodos para eliminar", True, (255, 0, 0))
            pantalla.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery))
            return

        # calcular rango visible
        inicio = self.offset * self.opciones_por_pagina
        fin = min(inicio + self.opciones_por_pagina, total)
        nodos_visibles = nodos[inicio:fin]

        # render lista
        y0 = rect.top + 70
        for i, nodo in enumerate(nodos_visibles):
            idx = inicio + i
            texto_str = f"{idx+1}. ({nodo.x},{getattr(nodo,'carril',getattr(nodo,'y',None))}) - {getattr(nodo,'tipo','')}"
            if i == self.indice_actual:
                # highlight
                hrect = pygame.Rect(rect.left + 10, y0 + i * 32 - 2, ancho - 20, 28)
                pygame.draw.rect(pantalla, (20, 100, 20), hrect)
                color = (255, 255, 255)
            else:
                color = (200, 200, 200)
            texto = self.fuente.render(texto_str, True, color)
            pantalla.blit(texto, (rect.left + 20, y0 + i * 32))

        # pie con página
        total_pages = max(1, (total - 1) // self.opciones_por_pagina + 1)
        page_text = self.fuente.render(f"Página {self.offset+1}/{total_pages}  (↑/↓ mover, ←/→ páginas, Enter=Eliminar, Esc=Salir)", True, (180, 180, 180))
        pantalla.blit(page_text, (rect.left + 12, rect.bottom - 34))
