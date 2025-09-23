import pygame
from models.Juego import JuegoModel

class GamePygame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.WIDTH, self.HEIGHT = width, height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera")
        self.clock = pygame.time.Clock()

        # Motor del juego
        self.juego = JuegoModel()
        self.juego.agregar_obstaculo(400, carril=2)

        # Cargar imágenes
        self.car_img = pygame.image.load("assets/car.png")
        self.car_img = pygame.transform.scale(self.car_img, (60, 100))

        self.obst_img = pygame.image.load("assets/obstaculo.png")
        self.obst_img = pygame.transform.scale(self.obst_img, (60, 100))

        self.road_img = pygame.image.load("assets/road.png")
        self.road_img = pygame.transform.scale(self.road_img, (self.WIDTH, self.HEIGHT))

        # Para simular movimiento de carretera
        # Para simular movimiento de carretera
        self.road_x = 0


        # Fuente para HUD
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Controles
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
            self.juego.verificar_colisiones()

            # Dibujar fondo con efecto de movimiento
            # Dibujar fondo con efecto de movimiento horizontal
            self.road_x -= 5  # se mueve hacia la izquierda
            if self.road_x <= -self.WIDTH:
                self.road_x = 0

            self.screen.blit(self.road_img, (self.road_x, 0))
            self.screen.blit(self.road_img, (self.road_x + self.WIDTH, 0))


            # Dibujar carro
            carro = self.juego.carro
            self.screen.blit(
                self.car_img,
                (carro.x, carro.carril * carro.alto - carro.altura_actual)
            )

            # Dibujar obstáculos
            for obst in self.juego.carretera.obstaculos:
                self.screen.blit(
                    self.obst_img,
                    (obst.x, obst.carril * obst.alto)
                )



            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

