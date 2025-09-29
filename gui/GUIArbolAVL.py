# gui/GUIArbolAVL.py - MODIFICAR LA POSICIÓN DE LOS BOTONES

import pygame
from gui import ArbolLayout


class GUIArbolAVL:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layout_manager = ArbolLayout.ArbolLayoutManager(screen_width, screen_height)
        self.font_controles = pygame.font.SysFont("Arial", 14)
        
        # Nuevos estados para gestión del árbol
        self.modo_insercion = False
        self.modo_eliminacion = False
        self.nodo_seleccionado = None
        
        # 🔥 BOTONES MÁS ABAJO - en la parte inferior del panel
        boton_y = screen_height - 120  # 120px desde abajo
        self.boton_insertar = pygame.Rect(screen_width - 200, boton_y, 80, 30)
        self.boton_eliminar = pygame.Rect(screen_width - 100, boton_y, 80, 30)
        self.boton_continuar = pygame.Rect(screen_width - 150, boton_y + 40, 100, 30)

    def dibujar_arbol_completo(self, screen, arbol_obstaculos):
        # **FONDO ORIGINAL**
        screen.fill((25, 25, 40))
        
        # **HEADER ORIGINAL** - más compacto
        titulo = self.font_controles.render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        screen.blit(titulo, (10, 10))

        if arbol_obstaculos and arbol_obstaculos.raiz:
            # **CÁLCULO ORIGINAL**
            self.layout_manager.calcular_layout(arbol_obstaculos.raiz)
            self.layout_manager.aplicar_zoom_y_desplazamiento(arbol_obstaculos.raiz)
            
            # **DIBUJO ORIGINAL**: conexiones primero, luego nodos
            self.layout_manager.dibujar_conexiones(screen, arbol_obstaculos.raiz)
            self._dibujar_nodos_recursivo(screen, arbol_obstaculos.raiz)

        # Dibujar interfaz de gestión del árbol (ahora en la parte inferior)
        self.dibujar_interfaz_gestion(screen)
        self.dibujar_controles(screen)

    def _dibujar_nodos_recursivo(self, screen, nodo):
        if nodo:
            # Resaltar nodo seleccionado
            if nodo == self.nodo_seleccionado:
                nodo.color_recorrido = (255, 255, 0)  # Amarillo para selección
            elif not hasattr(nodo, 'color_recorrido') or nodo.color_recorrido == (0, 0, 0):
                nodo.color_recorrido = (0, 0, 0)  # Negro por defecto
            
            self.layout_manager.dibujar_nodo(screen, nodo)
            self._dibujar_nodos_recursivo(screen, nodo.izquierda)
            self._dibujar_nodos_recursivo(screen, nodo.derecha)

    def dibujar_interfaz_gestion(self, screen):
        """Dibuja la interfaz para insertar/eliminar nodos EN LA PARTE INFERIOR"""
        # Fondo semitransparente para los botones
        fondo_botones = pygame.Rect(0, self.screen_height - 150, self.screen_width, 150)
        pygame.draw.rect(screen, (40, 40, 60, 180), fondo_botones)
        pygame.draw.rect(screen, (80, 80, 100), fondo_botones, 2)  # Borde
        
        # Título de la sección de gestión
        titulo_gestion = self.font_controles.render("Gestión del Árbol AVL", True, (255, 255, 255))
        screen.blit(titulo_gestion, (10, self.screen_height - 140))
        
        # Dibujar botones
        color_insertar = (0, 200, 0) if self.modo_insercion else (60, 120, 60)
        color_eliminar = (200, 0, 0) if self.modo_eliminacion else (120, 60, 60)
        color_continuar = (0, 100, 200)
        
        pygame.draw.rect(screen, color_insertar, self.boton_insertar, border_radius=5)
        pygame.draw.rect(screen, color_eliminar, self.boton_eliminar, border_radius=5)
        pygame.draw.rect(screen, color_continuar, self.boton_continuar, border_radius=5)
        
        # Texto de botones
        texto_insertar = self.font_controles.render("Insertar", True, (255, 255, 255))
        texto_eliminar = self.font_controles.render("Eliminar", True, (255, 255, 255))
        texto_continuar = self.font_controles.render("Continuar", True, (255, 255, 255))
        
        screen.blit(texto_insertar, (self.boton_insertar.x + 10, self.boton_insertar.y + 8))
        screen.blit(texto_eliminar, (self.boton_eliminar.x + 10, self.boton_eliminar.y + 8))
        screen.blit(texto_continuar, (self.boton_continuar.x + 10, self.boton_continuar.y + 8))
        
        # Instrucciones dinámicas MEJORADAS
        instrucciones_y = self.screen_height - 110
        if self.modo_insercion:
            instruccion = self.font_controles.render("Haz clic en el árbol para insertar un nuevo nodo", True, (255, 255, 0))
            screen.blit(instruccion, (10, instrucciones_y))
            
            instruccion2 = self.font_controles.render("Las coordenadas se convertirán automáticamente", True, (200, 200, 100))
            screen.blit(instruccion2, (10, instrucciones_y + 20))
            
        elif self.modo_eliminacion:
            instruccion = self.font_controles.render("Selecciona un nodo del árbol para eliminarlo", True, (255, 100, 100))
            screen.blit(instruccion, (10, instrucciones_y))
            
            instruccion2 = self.font_controles.render("Confirma la eliminación en la consola", True, (200, 150, 150))
            screen.blit(instruccion2, (10, instrucciones_y + 20))
        else:
            instruccion = self.font_controles.render("Selecciona una opción para gestionar el árbol", True, (200, 200, 200))
            screen.blit(instruccion, (10, instrucciones_y))

    def dibujar_controles(self, screen):
        """Dibuja los controles generales EN LA PARTE INFERIOR, debajo de los botones"""
        controles = [
            f"Zoom: {self.layout_manager.obtener_zoom_total():.1f}x",
            "Rueda: Zoom manual",
            "Arrastrar: Mover árbol",
            "R: Resetear vista",
            "I/P/O/B: Recorridos del árbol"
        ]
        
        # Posicionar controles justo encima del borde inferior
        y_pos = self.screen_height - 70
        for i, texto in enumerate(controles):
            texto_surf = self.font_controles.render(texto, True, (180, 180, 200))
            screen.blit(texto_surf, (10, y_pos + i * 16))

    def manejar_eventos_arbol(self, event, arbol_obstaculos):
        """Maneja eventos para la gestión del árbol"""
        resultado = self.layout_manager.manejar_eventos_zoom(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            
            # Verificar clics en botones
            if self.boton_insertar.collidepoint(event.pos):
                self.modo_insercion = True
                self.modo_eliminacion = False
                self.nodo_seleccionado = None
                print("🌳 Modo inserción activado - Haz clic en el árbol para insertar")
                return "modo_insercion"
            
            elif self.boton_eliminar.collidepoint(event.pos):
                self.modo_insercion = False
                self.modo_eliminacion = True
                self.nodo_seleccionado = None
                
                # Obtener y mostrar nodos disponibles para eliminar
                if arbol_obstaculos:
                    nodos_disponibles = arbol_obstaculos.obtener_todos_nodos()
                    print(f"🌳 Nodos disponibles para eliminar: {len(nodos_disponibles)}")
                    for i, nodo in enumerate(nodos_disponibles):
                        print(f"   {i+1}. ({nodo.x},{nodo.y}) - {nodo.tipo}")
                
                return "modo_eliminacion"
            
            elif self.boton_continuar.collidepoint(event.pos):
                self.modo_insercion = False
                self.modo_eliminacion = False
                self.nodo_seleccionado = None
                return "continuar"
            
            # Manejar selección de nodos para eliminación
            elif self.modo_eliminacion and arbol_obstaculos:
                nodo_clickeado = self._buscar_nodo_en_posicion(arbol_obstaculos.raiz, (mouse_x, mouse_y))
                if nodo_clickeado:
                    self.nodo_seleccionado = nodo_clickeado
                    return "nodo_seleccionado", nodo_clickeado
            
            # Manejar inserción en posición del click
            elif self.modo_insercion and arbol_obstaculos:
                # MEJORADO: Conversión más precisa de coordenadas
                x_juego, y_juego = self._convertir_coordenadas_pantalla_a_juego(mouse_x, mouse_y)
                
                if x_juego is not None and y_juego is not None:
                    print(f"🎯 Insertando en coordenadas: juego({x_juego},{y_juego})")
                    return "insertar_en_posicion", (x_juego, y_juego)
        
        return resultado
    
    def _convertir_coordenadas_pantalla_a_juego(self, mouse_x, mouse_y):
        """Convierte coordenadas de pantalla a coordenadas del juego"""
        try:
            # Obtener parámetros del layout
            zoom_total = self.layout_manager.obtener_zoom_total()
            offset_x = self.layout_manager.offset_x
            offset_y = self.layout_manager.offset_y
            
            # Convertir a coordenadas del árbol (sin zoom/offset)
            x_arbol = (mouse_x / zoom_total) - offset_x
            y_arbol = (mouse_y / zoom_total) - offset_y
            
            # Ajustar a coordenadas del juego
            # X: escalar apropiadamente (ajusta este factor según tu juego)
            x_juego = max(0, int(x_arbol / 2))
            
            # Y: convertir a carril (0, 1, 2)
            # Asumiendo que los nodos están entre y=100 y y=300 aprox
            if y_arbol < 100:
                y_juego = 0
            elif y_arbol < 180:
                y_juego = 1
            else:
                y_juego = 2
            
            # Validar que sean coordenadas razonables
            if x_juego > 10000:  # Límite máximo razonable
                print("❌ Coordenada X demasiado grande")
                return None, None
                
            print(f"🔄 Conversión: pantalla({mouse_x},{mouse_y}) -> árbol({x_arbol:.1f},{y_arbol:.1f}) -> juego({x_juego},{y_juego})")
            return x_juego, y_juego
            
        except Exception as e:
            print(f"❌ Error en conversión de coordenadas: {e}")
            return None, None

    def _buscar_nodo_en_posicion(self, nodo, pos_mouse):
        """Busca recursivamente si el click fue sobre un nodo"""
        if not nodo or not hasattr(nodo, 'x_final') or not hasattr(nodo, 'y_final'):
            return None
        
        # Usar las coordenadas finales ya calculadas
        nodo_x = nodo.x_final
        nodo_y = nodo.y_final
        
        # Verificar si el click está cerca del nodo (radio de 20px)
        distancia = ((pos_mouse[0] - nodo_x) ** 2 + (pos_mouse[1] - nodo_y) ** 2) ** 0.5
        if distancia <= 20:
            return nodo
        
        # Buscar en hijos
        encontrado = None
        if nodo.izquierda:
            encontrado = self._buscar_nodo_en_posicion(nodo.izquierda, pos_mouse)
            if encontrado:
                return encontrado
        
        if nodo.derecha:
            encontrado = self._buscar_nodo_en_posicion(nodo.derecha, pos_mouse)
            if encontrado:
                return encontrado
        
        return None

    def desactivar_modos(self):
        """Desactiva todos los modos de gestión"""
        self.modo_insercion = False
        self.modo_eliminacion = False
        self.nodo_seleccionado = None