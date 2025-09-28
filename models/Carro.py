# models/Carro.py
# models/Carro.py
class Carro:
    def __init__(self, ancho=50, alto=30, carril=1, salto_altura=100, velocidad=10):
        self.x = 0  # Posición X inicial
        self.carril = carril

        # La Y real se calcula a partir del carril (0, 1, 2) → posición en pixeles
        self.y = 400 + carril * 60

        # ✅ velocidad se pasa desde el JSON (por medio de JuegoModel)
        self.velocidad_x = velocidad

        # tamaño del carro
        self.ancho = ancho
        self.alto = alto

        # salto
        self.esta_saltando = False
        self.salto_altura = salto_altura
        self.altura_actual = 0

    def avanzar(self):
        """Mover el carro en el eje X según su velocidad"""
        self.x += self.velocidad_x


    def mover_arriba(self):
        if self.carril > 0:
            self.carril -= 1
            self.actualizar_posicion_y()

    def mover_abajo(self):
        if self.carril < 2:
            self.carril += 1
            self.actualizar_posicion_y()

    def actualizar_posicion_y(self):
        """Actualiza la posición Y basada en el carril"""
        self.y = 400 + self.carril * 60

    def saltar(self):
        if not self.esta_saltando:
            self.esta_saltando = True
            self.altura_actual = self.salto_altura

    def actualizar_salto(self):
        """Actualiza el estado del salto"""
        if self.esta_saltando:
            self.altura_actual -= 5
            if self.altura_actual <= 0:
                self.altura_actual = 0
                self.esta_saltando = False

    def obtener_rectangulo(self):
        """Devuelve el rectángulo de colisión"""
        y_pos = self.y - self.altura_actual
        return (self.x, y_pos, self.ancho, self.alto)

    def __repr__(self):
        return f"Carro(x={self.x}, carril={self.carril}, y={self.y})"