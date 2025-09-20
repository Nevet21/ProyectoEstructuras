import pygame
from models.Juego import JuegoModel

class GamePygameH:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.WIDTH, self.HEIGHT = width, height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Juego Carretera")
        self.clock = pygame.time.Clock()

        # Motor del juego
        self.juego = JuegoModel()
        # Agregar obstáculo de prueba
        self.juego.agregar_obstaculo(400, carril=1)

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

            # Dibujar
            self.screen.fill((0, 0, 0))
            carro = self.juego.carro
            pygame.draw.rect(self.screen, (0, 255, 0),
                             (carro.x, carro.carril * carro.alto - carro.altura_actual,
                              carro.ancho, carro.alto))
            for obst in self.juego.carretera.obstaculos:
                pygame.draw.rect(self.screen, (255, 0, 0),
                                 (obst.x, obst.carril * obst.alto, obst.ancho, obst.alto))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

