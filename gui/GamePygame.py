import pygame
from models.Juego import JuegoModel

class GamePygame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.WIDTH, self.HEIGHT = width, height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera con Árbol AVL")
        self.clock = pygame.time.Clock()

        # Motor del juego
        self.juego = JuegoModel()
        self.juego.agregar_obstaculo(400, carril=2)
        self.juego.agregar_obstaculo(600, carril=1)  # Más obstáculos para probar AVL

        # Cargar imágenes
        self.car_img = pygame.image.load("assets/car.png")
        self.car_img = pygame.transform.scale(self.car_img, (60, 100))
        self.obst_img = pygame.image.load("assets/obstaculo.png")
        self.obst_img = pygame.transform.scale(self.obst_img, (60, 100))
        self.road_img = pygame.image.load("assets/road.png")
        self.road_img = pygame.transform.scale(self.road_img, (self.WIDTH, self.HEIGHT))

        # Para simular movimiento de carretera
        self.road_x = 0

        # Fuente para HUD
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        # NUEVO: Estado de visualización del árbol
        self.mostrar_arbol = False
        self.recorrido_actual = ""

    def dibujar_arbol_avl(self):
        """Dibuja el árbol AVL en la pantalla"""
        if not self.mostrar_arbol:
            return

        # Fondo del panel del árbol
        panel_arbol = pygame.Surface((300, self.HEIGHT))
        panel_arbol.fill((40, 40, 60))
        self.screen.blit(panel_arbol, (self.WIDTH - 300, 0))

        # Título
        titulo = self.font.render("Árbol AVL de Obstáculos", True, (255, 255, 255))
        self.screen.blit(titulo, (self.WIDTH - 280, 20))

        # Dibujar árbol recursivamente
        self._dibujar_nodo(self.juego.arbol_obstaculos.raiz, self.WIDTH - 150, 80, 100)

        # Mostrar recorrido si está activo
        if self.recorrido_actual:
            texto_recorrido = self.font.render(f"Recorrido: {self.recorrido_actual}", True, (255, 255, 0))
            self.screen.blit(texto_recorrido, (self.WIDTH - 280, self.HEIGHT - 100))

    def _dibujar_nodo(self, nodo, x, y, separacion):
        if nodo:
            # Dibujar líneas a hijos
            if nodo.izquierda:
                pygame.draw.line(self.screen, (100, 200, 100), (x, y), 
                               (x - separacion, y + 60), 2)
                self._dibujar_nodo(nodo.izquierda, x - separacion, y + 60, separacion // 2)
            
            if nodo.derecha:
                pygame.draw.line(self.screen, (100, 200, 100), (x, y), 
                               (x + separacion, y + 60), 2)
                self._dibujar_nodo(nodo.derecha, x + separacion, y + 60, separacion // 2)
            
            # Dibujar nodo
            color_nodo = (0, 150, 200) if nodo == self.juego.arbol_obstaculos.raiz else (200, 100, 50)
            pygame.draw.circle(self.screen, color_nodo, (x, y), 20)
            
            # Texto del nodo (x,y)
            texto = self.font.render(f"{nodo.x},{nodo.y}", True, (255, 255, 255))
            self.screen.blit(texto, (x - 15, y - 10))

    def dibujar_botones(self):
        """Dibuja botones para controles del árbol"""
        # Botón mostrar/ocultar árbol
        pygame.draw.rect(self.screen, (70, 130, 180), (10, 10, 200, 40))
        texto_boton = self.font.render("Mostrar Árbol AVL", True, (255, 255, 255))
        self.screen.blit(texto_boton, (20, 20))

        # Botones de recorridos
        if self.mostrar_arbol:
            recorridos = ["Inorden", "Preorden", "Postorden"]
            for i, recorrido in enumerate(recorridos):
                pygame.draw.rect(self.screen, (90, 160, 90), (10, 60 + i*50, 150, 40))
                texto = self.font.render(recorrido, True, (255, 255, 255))
                self.screen.blit(texto, (20, 70 + i*50))

    def manejar_eventos(self):
        """Maneja clics en botones"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Botón mostrar/ocultar árbol
                if 10 <= x <= 210 and 10 <= y <= 50:
                    self.mostrar_arbol = not self.mostrar_arbol
                
                # Botones de recorridos
                if self.mostrar_arbol:
                    if 10 <= x <= 160 and 60 <= y <= 100:
                        self.recorrido_actual = "Inorden: " + str(self.juego.arbol_obstaculos.inorden())
                    elif 10 <= x <= 160 and 110 <= y <= 150:
                        self.recorrido_actual = "Preorden: " + str(self.juego.arbol_obstaculos.preorden())
                    elif 10 <= x <= 160 and 160 <= y <= 200:
                        self.recorrido_actual = "Postorden: " + str(self.juego.arbol_obstaculos.postorden())
        
        return True

    def run(self):
        running = True
        while running:
            # Manejar eventos (incluyendo botones nuevos)
            running = self.manejar_eventos()

            # Controles del carro
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.juego.carro.mover_arriba()
            if keys[pygame.K_DOWN]:
                self.juego.carro.mover_abajo()
            if keys[pygame.K_SPACE]:
                self.juego.carro.saltar()

            # Actualizar lógica del juego
            self.juego.carro.actualizar_salto()
            for obst in self.juego.carretera.obstaculos:
                obst.mover(self.juego.velocidad)
            
            # Actualizar obstáculos visibles usando AVL
            x_min = max(0, self.juego.carro.x - 100)
            x_max = self.juego.carro.x + self.WIDTH
            self.juego.actualizar_obstaculos_visibles(x_min, x_max)
            
            self.juego.verificar_colisiones()

            # Dibujar fondo con efecto de movimiento
            self.road_x -= 5
            if self.road_x <= -self.WIDTH:
                self.road_x = 0
            self.screen.blit(self.road_img, (self.road_x, 0))
            self.screen.blit(self.road_img, (self.road_x + self.WIDTH, 0))

            # Dibujar carro
            carro = self.juego.carro
            self.screen.blit(self.car_img, (carro.x, carro.carril * carro.alto - carro.altura_actual))

            # Dibujar obstáculos VISIBLES (del AVL)
            for obst in self.juego.obstaculos_visibles:
                self.screen.blit(self.obst_img, (obst.x, obst.carril * obst.alto))

            # NUEVO: Dibujar interfaz del árbol AVL
            self.dibujar_botones()
            self.dibujar_arbol_avl()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()