# models/Carro.py
class Carro:
    def __init__(self, ancho=50, alto=30, carril=1, salto_altura=40):
        self.x = 0  # ✅ CAMBIAR de 100 a 0 - Empieza al inicio
        self.carril = carril
        self.y = 400 + carril * 60  # Posición Y basada en carril
        self.velocidad_x = 2  # ✅ VELOCIDAD DE AVANCE

        # tamaño del carro
        self.ancho = ancho
        self.alto = alto

        # salto
        self.esta_saltando = False
        self.salto_altura = salto_altura
        self.altura_actual = 0

    def avanzar(self):
        """✅ EL CARRO SÍ AVANZA EN X - IMPORTANTE"""
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