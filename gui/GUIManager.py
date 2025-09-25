# gui/GUIManager.py
import pygame

class GUIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.road_x = 0
        
        # Cargar o crear imágenes como antes
        self.cargar_imagenes()
        
        # Fuentes como antes
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

    def cargar_imagenes(self):
        """Carga imágenes IDÉNTICO a como estaba antes"""
        try:
            self.car_img = pygame.image.load("assets/car.png")
            self.car_img = pygame.transform.scale(self.car_img, (60, 100))
        except:
            self.car_img = pygame.Surface((60, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.car_img, (255, 0, 0), (10, 0, 40, 80))
            pygame.draw.rect(self.car_img, (200, 0, 0), (0, 80, 60, 20))

        try:
            self.obst_img = pygame.image.load("assets/obstaculo.png")
            self.obst_img = pygame.transform.scale(self.obst_img, (60, 100))
        except:
            self.obst_img = pygame.Surface((60, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.obst_img, (0, 100, 255), (0, 0, 60, 100))
            pygame.draw.rect(self.obst_img, (0, 70, 200), (10, 10, 40, 80))

        try:
            self.road_img = pygame.image.load("assets/road.png")
            self.road_img = pygame.transform.scale(self.road_img, (self.screen_width, self.screen_height))
        except:
            self.road_img = pygame.Surface((self.screen_width, self.screen_height))
            self.road_img.fill((100, 100, 100))
            for i in range(0, self.screen_width, 40):
                pygame.draw.rect(self.road_img, (255, 255, 0), (i, self.screen_height//2 - 5, 20, 10))

    def dibujar_juego(self, screen, juego):
        """Dibuja EXACTAMENTE como antes"""
        # Fondo con movimiento (COPIADO del código anterior)
        self.road_x -= 5
        if self.road_x <= -self.screen_width:
            self.road_x = 0

        screen.blit(self.road_img, (self.road_x, 0))
        screen.blit(self.road_img, (self.road_x + self.screen_width, 0))

        # Carriles (COPIADO del código anterior)
        for i in range(1, 3):
            y_pos = i * 100 + 150
            pygame.draw.line(screen, (255, 255, 0), (0, y_pos), (self.screen_width, y_pos), 2)

        # Carro (COPIADO del código anterior)
        carro = juego.carro
        carro_y = 150 + carro.carril * 100 - carro.altura_actual
        screen.blit(self.car_img, (carro.x, carro_y))

        # Obstáculos (COPIADO del código anterior)
        for obst in juego.obstaculos_visibles:
            screen.blit(self.obst_img, (obst.x, 150 + obst.carril * 100))

        # HUD (COPIADO del código anterior)
        self.dibujar_hud(screen, juego.energia)

    def dibujar_hud(self, screen, energia):
        """HUD IDÉNTICO al anterior"""
        # Panel superior (COPIADO)
        panel_superior = pygame.Surface((self.screen_width, 50), pygame.SRCALPHA)
        panel_superior.fill((0, 0, 0, 128))
        screen.blit(panel_superior, (0, 0))

        # Botón (COPIADO)
        pygame.draw.rect(screen, (70, 130, 180), (10, 10, 180, 35), border_radius=5)
        texto_boton = self.font.render("🌳 Mostrar Árbol AVL", True, (255, 255, 255))
        screen.blit(texto_boton, (20, 15))

        # Energía (COPIADO)
        energia_texto = self.font.render(f"⚡ {energia}%", True, (255, 255, 255))
        screen.blit(energia_texto, (self.screen_width - 100, 15))

        # Barra de energía (COPIADO)
        barra_largo = 200
        energia_ratio = energia / 100
        pygame.draw.rect(screen, (50, 50, 50), (self.screen_width - 320, 20, barra_largo, 15))
        pygame.draw.rect(screen, (0, 255, 0), (self.screen_width - 320, 20, barra_largo * energia_ratio, 15))

    def manejar_eventos_juego(self, event):
        """Manejo de eventos COPIADO"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 10 <= x <= 190 and 10 <= y <= 45:
                return "mostrar_arbol"
        return None