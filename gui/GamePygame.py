import pygame
import os
import sys
import json   # 👈 nuevo import

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.Juego import JuegoModel

class GamePygame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.WIDTH, self.HEIGHT = width, height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera con Árbol AVL")
        self.clock = pygame.time.Clock()

        # 🔹 Cargar configuraciones desde JSON ANTES de instanciar JuegoModel
        data = self.cargar_json("config.json")
        config = data.get("configuraciones", {})

        longitud = config.get("distancia_total", 1000)
        energia_inicial = config.get("energia_inicial", 100)   # 👈 puedes agregar este campo en el JSON
        velocidad = config.get("velocidad_avance", 5)
        intervalo = config.get("tiempo_refresco_ms", 200) / 1000.0  # lo paso a segundos

        # Motor del juego con parámetros del JSON
        self.juego = JuegoModel(longitud, energia_inicial, velocidad, intervalo)

        # Guardar otros atributos extra en el juego
        self.juego.altura_salto = config.get("altura_salto", 50)
        self.juego.color_carrito = config.get("color_carrito", "rojo")

        # 🔹 Cargar obstáculos
        for obst in data.get("obstaculos", []):
            x = obst.get("x", 0)
            carril = obst.get("carril", 0)
            tipo = obst.get("tipo", "cono")
            self.juego.agregar_obstaculo(x, carril=carril, tipo=tipo)

        # Cargar imágenes
        self.cargar_imagenes()
        
        # Efecto de movimiento de carretera
        self.road_x = 0

        # Fuentes
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)

        # Estado de visualización
        self.mostrar_arbol = False
        self.recorrido_actual = ""
        self.recorrido_lineas = []

    def cargar_json(self, ruta_json):
        """Carga configuraciones y obstáculos desde un archivo JSON"""
        try:
            with open(ruta_json, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando {ruta_json}: {e}")
            return {}


    def cargar_imagenes(self):
        """Carga imágenes con fallback a formas geométricas"""
        try:
            # Intentar cargar imágenes
            self.car_img = pygame.image.load("assets/car.png")
            self.car_img = pygame.transform.scale(self.car_img, (60, 100))
        except:
            # Fallback: crear imagen de carro rojo
            self.car_img = pygame.Surface((60, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.car_img, (255, 0, 0), (10, 0, 40, 80))
            pygame.draw.rect(self.car_img, (200, 0, 0), (0, 80, 60, 20))

        try:
            self.obst_img = pygame.image.load("assets/obstaculo.png")
            self.obst_img = pygame.transform.scale(self.obst_img, (60, 100))
        except:
            # Fallback: crear imagen de obstáculo azul
            self.obst_img = pygame.Surface((60, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.obst_img, (0, 100, 255), (0, 0, 60, 100))
            pygame.draw.rect(self.obst_img, (0, 70, 200), (10, 10, 40, 80))

        try:
            self.road_img = pygame.image.load("assets/road.png")
            self.road_img = pygame.transform.scale(self.road_img, (self.WIDTH, self.HEIGHT))
        except:
            # Fallback: crear carretera gris con líneas
            self.road_img = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.road_img.fill((100, 100, 100))  # Gris carretera
            # Líneas de carretera
            for i in range(0, self.WIDTH, 40):
                pygame.draw.rect(self.road_img, (255, 255, 0), (i, self.HEIGHT//2 - 5, 20, 10))

    def dibujar_juego(self):
        """Dibuja la interfaz completa del juego"""
        # Dibujar fondo con efecto de movimiento
        self.road_x -= 5
        if self.road_x <= -self.WIDTH:
            self.road_x = 0

        self.screen.blit(self.road_img, (self.road_x, 0))
        self.screen.blit(self.road_img, (self.road_x + self.WIDTH, 0))

        # Dibujar carriles (líneas divisorias)
        for i in range(1, 3):
            y_pos = i * 100 + 150
            pygame.draw.line(self.screen, (255, 255, 0), (0, y_pos), (self.WIDTH, y_pos), 2)

        # Dibujar carro con efecto de salto
        carro = self.juego.carro
        carro_y = 150 + carro.carril * 100 - carro.altura_actual
        self.screen.blit(self.car_img, (carro.x, carro_y))

        # Dibujar obstáculos visibles
        for obst in self.juego.obstaculos_visibles:
            self.screen.blit(self.obst_img, (obst.x, 150 + obst.carril * 100))

        # Dibujar HUD (interfaz de usuario)
        self.dibujar_hud()

    def dibujar_hud(self):
        """Dibuja la interfaz de usuario durante el juego"""
        # Panel superior semi-transparente
        panel_superior = pygame.Surface((self.WIDTH, 50), pygame.SRCALPHA)
        panel_superior.fill((0, 0, 0, 128))  # Negro semi-transparente
        self.screen.blit(panel_superior, (0, 0))

        # Botón mostrar árbol
        pygame.draw.rect(self.screen, (70, 130, 180), (10, 10, 180, 35), border_radius=5)
        texto_boton = self.font.render("🌳 Mostrar Árbol AVL", True, (255, 255, 255))
        self.screen.blit(texto_boton, (20, 15))

        # Energía con barra de progreso
        energia_texto = self.font.render(f"⚡ {self.juego.energia}%", True, (255, 255, 255))
        self.screen.blit(energia_texto, (self.WIDTH - 100, 15))

        # Barra de energía
        barra_largo = 200
        energia_ratio = self.juego.energia / 100
        pygame.draw.rect(self.screen, (50, 50, 50), (self.WIDTH - 320, 20, barra_largo, 15))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.WIDTH - 320, 20, barra_largo * energia_ratio, 15))

    def dibujar_arbol_completo(self):
        """Dibuja el árbol AVL en pantalla completa"""
        # Fondo profesional para el árbol
        self.screen.fill((25, 25, 40))  # Azul oscuro

        # Header con gradiente
        header = pygame.Surface((self.WIDTH, 80))
        header.fill((40, 40, 80))
        self.screen.blit(header, (0, 0))

        # Título centrado
        titulo = self.font.render("🌳 Árbol AVL de Obstáculos", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.WIDTH//2, 40))
        self.screen.blit(titulo, titulo_rect)

        # Dibujar árbol centrado
        if self.juego.arbol_obstaculos and self.juego.arbol_obstaculos.raiz:
            self.dibujar_arbol_recursivo(self.juego.arbol_obstaculos.raiz, self.WIDTH//2, 120, 250)

        # Panel inferior para recorridos
        panel_inferior = pygame.Surface((self.WIDTH, 120), pygame.SRCALPHA)
        panel_inferior.fill((0, 0, 0, 128))
        self.screen.blit(panel_inferior, (0, self.HEIGHT - 120))

        # Dibujar botones y recorridos
        self.dibujar_controles_arbol()

    def dibujar_arbol_recursivo(self, nodo, x, y, separacion):
        """Dibuja el árbol recursivamente con diseño profesional"""
        if nodo.izquierda:
            nuevo_x = x - separacion
            nuevo_y = y + 80
            # Línea con sombra
            pygame.draw.line(self.screen, (80, 80, 120), (x+2, y+17), (nuevo_x+2, nuevo_y-13), 3)
            pygame.draw.line(self.screen, (100, 200, 100), (x, y+15), (nuevo_x, nuevo_y-15), 3)
            self.dibujar_arbol_recursivo(nodo.izquierda, nuevo_x, nuevo_y, separacion * 0.6)

        if nodo.derecha:
            nuevo_x = x + separacion
            nuevo_y = y + 80
            pygame.draw.line(self.screen, (80, 80, 120), (x+2, y+17), (nuevo_x+2, nuevo_y-13), 3)
            pygame.draw.line(self.screen, (100, 200, 100), (x, y+15), (nuevo_x, nuevo_y-15), 3)
            self.dibujar_arbol_recursivo(nodo.derecha, nuevo_x, nuevo_y, separacion * 0.6)

        # Dibujar nodo con efecto 3D
        color_nodo = (0, 150, 200) if nodo == self.juego.arbol_obstaculos.raiz else (200, 100, 50)
        
        # Sombra
        pygame.draw.circle(self.screen, (20, 20, 40), (x+3, y+3), 26)
        # Nodo principal
        pygame.draw.circle(self.screen, color_nodo, (x, y), 25)
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 25, 2)
        
        # Texto del nodo
        texto_coords = self.font_small.render(f"{nodo.x},{nodo.y}", True, (255, 255, 255))
        texto_rect = texto_coords.get_rect(center=(x, y))
        self.screen.blit(texto_coords, texto_rect)

        # Altura del nodo (pequeño)
        altura_texto = self.font_small.render(f"h:{nodo.altura}", True, (200, 200, 200))
        self.screen.blit(altura_texto, (x - 12, y + 20))

    def dibujar_controles_arbol(self):
        """Dibuja los botones y muestra los recorridos"""
        # Botones en esquina inferior izquierda
        botones = [
            ("🔍 Inorden", (20, self.HEIGHT - 100)),
            ("📊 Preorden", (20, self.HEIGHT - 60)),
            ("📈 Postorden", (150, self.HEIGHT - 100)),
            ("🎮 Volver al Juego", (150, self.HEIGHT - 60))
        ]

        for texto, pos in botones:
            pygame.draw.rect(self.screen, (70, 130, 180), (pos[0], pos[1], 120, 35), border_radius=5)
            texto_btn = self.font_small.render(texto, True, (255, 255, 255))
            self.screen.blit(texto_btn, (pos[0] + 10, pos[1] + 8))

        # Mostrar recorrido actual (formateado)
        if self.recorrido_lineas:
            y_pos = self.HEIGHT - 150
            for linea in self.recorrido_lineas[-3:]:  # Mostrar últimas 3 líneas
                texto_rec = self.font_small.render(linea, True, (255, 255, 0))
                self.screen.blit(texto_rec, (300, y_pos))
                y_pos += 25

    def formatear_recorrido(self, recorrido, tipo):
        """Formatea el recorrido para mostrarlo en múltiples líneas"""
        if not recorrido:
            return ["No hay elementos en el árbol"]
        
        elementos = ", ".join(recorrido)
        lineas = []
        linea_actual = f"{tipo}: "
        
        for elemento in recorrido:
            if len(linea_actual + elemento) > 60:  # Límite de caracteres por línea
                lineas.append(linea_actual)
                linea_actual = elemento + ", "
            else:
                linea_actual += elemento + ", "
        
        if linea_actual:
            lineas.append(linea_actual.rstrip(", "))
        
        return lineas

    def manejar_eventos(self):
        """Maneja todos los eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.mostrar_arbol:
                    self.mostrar_arbol = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if self.mostrar_arbol:
                    # Botones del árbol
                    if 20 <= x <= 140:
                        if self.HEIGHT - 100 <= y <= self.HEIGHT - 65:
                            recorrido = self.juego.arbol_obstaculos.inorden()
                            self.recorrido_lineas = self.formatear_recorrido(recorrido, "INORDEN")
                        elif self.HEIGHT - 60 <= y <= self.HEIGHT - 25:
                            recorrido = self.juego.arbol_obstaculos.preorden()
                            self.recorrido_lineas = self.formatear_recorrido(recorrido, "PREORDEN")
                    
                    if 150 <= x <= 270:
                        if self.HEIGHT - 100 <= y <= self.HEIGHT - 65:
                            recorrido = self.juego.arbol_obstaculos.postorden()
                            self.recorrido_lineas = self.formatear_recorrido(recorrido, "POSTORDEN")
                        elif self.HEIGHT - 60 <= y <= self.HEIGHT - 25:
                            self.mostrar_arbol = False
                else:
                    # Botón mostrar árbol
                    if 10 <= x <= 190 and 10 <= y <= 45:
                        self.mostrar_arbol = True
                        self.recorrido_lineas = []
        
        return True

    def actualizar_logica(self):
        """Actualiza la lógica del juego"""
        if self.mostrar_arbol:
            return  # No actualizar juego cuando se muestra el árbol

        # Controles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.juego.carro.mover_arriba()
        if keys[pygame.K_DOWN]: self.juego.carro.mover_abajo()
        if keys[pygame.K_SPACE]: self.juego.carro.saltar()

        # Actualizar juego
        self.juego.carro.actualizar_salto()
        for obst in self.juego.carretera.obstaculos:
            obst.mover(self.juego.velocidad)
        
        # Consultar obstáculos visibles usando AVL
        x_min = max(0, self.juego.carro.x - 100)
        x_max = self.juego.carro.x + self.WIDTH
        self.juego.actualizar_obstaculos_visibles(x_min, x_max)
        
        self.juego.verificar_colisiones()

    def run(self):
        """Bucle principal del juego"""
        running = True
        while running:
            running = self.manejar_eventos()
            self.actualizar_logica()
            
            # Dibujar según el modo
            if self.mostrar_arbol:
                self.dibujar_arbol_completo()
            else:
                self.dibujar_juego()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    juego = GamePygame()
    juego.run()