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
        """Carga las imágenes desde assets/"""
        try:
            # 1. Cargar carro
            self.car_img = pygame.image.load("assets/car.png")
            self.car_img = pygame.transform.scale(self.car_img, (60, 100))
            
            # 2. Cargar carretera (IMPORTANTE: esta es la que faltaba)
            self.road_img = pygame.image.load("assets/road.png")
            self.road_img = pygame.transform.scale(self.road_img, (self.screen_width, self.screen_height))
            
            # 3. Cargar imágenes de obstáculos (SIMPLE)
            self.obstaculo_imagenes = {
                "cono": pygame.image.load("assets/cono.png"),
                "roca": pygame.image.load("assets/roca.png"),
                "aceite": pygame.image.load("assets/aceite.png"),
                "hueco": pygame.image.load("assets/hueco.png")
            }
            
            # Escalar todas las imágenes de obstáculos
            for tipo in self.obstaculo_imagenes:
                self.obstaculo_imagenes[tipo] = pygame.transform.scale(
                    self.obstaculo_imagenes[tipo], (60, 100)
                )
                
        except Exception as e:
            print(f"❌ Error cargando imágenes: {e}")
            # Si hay error, crear imágenes básicas de emergencia
            self.crear_imagenes_emergencia()

    def crear_imagenes_emergencia(self):
        """Solo si falla la carga de imágenes"""
        # Carro rojo básico
        self.car_img = pygame.Surface((60, 100))
        self.car_img.fill((255, 0, 0))
        
        # Carretera gris básica
        self.road_img = pygame.Surface((self.screen_width, self.screen_height))
        self.road_img.fill((100, 100, 100))
        
        # Obstáculos de colores básicos
        self.obstaculo_imagenes = {
            "cono": pygame.Surface((60, 100)),    # Amarillo
            "roca": pygame.Surface((60, 100)),    # Gris
            "aceite": pygame.Surface((60, 100)),  # Negro  
            "hueco": pygame.Surface((60, 100))    # Marrón
        }
        
        # Colorear los obstáculos
        self.obstaculo_imagenes["cono"].fill((255, 255, 0))
        self.obstaculo_imagenes["roca"].fill((128, 128, 128))
        self.obstaculo_imagenes["aceite"].fill((0, 0, 0))
        self.obstaculo_imagenes["hueco"].fill((139, 69, 19))

    def dibujar_juego(self, screen, juego):
        """Dibuja el juego"""
        # Fondo
        self.road_x -= 5
        if self.road_x <= -self.screen_width:
            self.road_x = 0

        screen.blit(self.road_img, (self.road_x, 0))
        screen.blit(self.road_img, (self.road_x + self.screen_width, 0))

        # Carriles
        for i in range(1, 3):
            y_pos = i * 100 + 150
            pygame.draw.line(screen, (255, 255, 0), (0, y_pos), (self.screen_width, y_pos), 2)

        # Carro
        carro_x = self.screen_width // 2 - 30
        carro_y = 150 + juego.carro.carril * 100 - juego.carro.altura_actual
        screen.blit(self.car_img, (carro_x, carro_y))

        # Obstáculos - imagen según tipo
        for obst in juego.obstaculos_visibles:
            x_relativo = obst.x - juego.carro.x
            x_pantalla = self.screen_width // 2 + x_relativo
            
            if -100 < x_relativo < self.screen_width + 100:
                y_pantalla = 150 + obst.carril * 100
                # Usar la imagen correcta para cada tipo
                imagen = self.obstaculo_imagenes.get(obst.tipo, self.obstaculo_imagenes["cono"])
                screen.blit(imagen, (x_pantalla, y_pantalla))

        # HUD
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