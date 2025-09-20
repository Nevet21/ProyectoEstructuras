# models/Carro.py
#Prueba VS
class Carro:
    def __init__(self, ancho=50, alto=30, carril=0, salto_altura=40):
        # posición inicial (x fijo a la izquierda, y depende del carril)
        self.x = 50
        self.carril = carril
        self.y = carril * alto

        # tamaño del carro
        self.ancho = ancho
        self.alto = alto

        # salto
        self.esta_saltando = False
        self.salto_altura = salto_altura
        self.altura_actual = 0  # desplazamiento temporal al saltar

    def mover_arriba(self):
        if self.carril < 2:  # suponiendo 3 carriles (0,1,2)
            self.carril += 1
            self.y = self.carril * self.alto

    def mover_abajo(self):
        if self.carril > 0:
            self.carril -= 1
            self.y = self.carril * self.alto

    def saltar(self):
        if not self.esta_saltando:
            self.esta_saltando = True
            self.altura_actual = self.salto_altura

    def actualizar_salto(self):
        """Actualiza el estado del salto (sube y baja)."""
        if self.esta_saltando:
            self.altura_actual -= 5  # velocidad de caída
            if self.altura_actual <= 0:
                self.altura_actual = 0
                self.esta_saltando = False

    def get_rect(self):
        """Devuelve las coordenadas reales del carro para colisiones"""
        return (
            self.x,
            self.y - self.altura_actual,  # sube con el salto
            self.ancho,
            self.alto,
        )

    def __repr__(self):
        return f"Carro(carril={self.carril}, x={self.x}, y={self.y}, saltando={self.esta_saltando})"
