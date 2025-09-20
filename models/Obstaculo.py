# models/Obstaculo.py
class Obstaculo:
    def __init__(self, x: int, carril: int, tipo="normal", dano=10, ancho=20, alto=20):
        self.x = x
        self.carril = carril
        self.tipo = tipo
        self.dano = dano
        self.ancho = ancho
        self.alto = alto
        self.y = carril * alto

    def mover(self, velocidad_x: int):
        self.x -= velocidad_x

    def colisiona_con(self, carro) -> bool:
        # Rectángulo del obstáculo
        izquierda_obs = self.x
        derecha_obs = self.x + self.ancho
        arriba_obs = self.y
        abajo_obs = self.y + self.alto

        # Rectángulo del carro (ajustado con salto)
        carro_x, carro_y, carro_w, carro_h = carro.get_rect()
        izquierda_carro = carro_x
        derecha_carro = carro_x + carro_w
        arriba_carro = carro_y
        abajo_carro = carro_y + carro_h

        # Verificar intersección
        colision_x = izquierda_obs < derecha_carro and derecha_obs > izquierda_carro
        colision_y = arriba_obs < abajo_carro and abajo_obs > arriba_carro
        return colision_x and colision_y

    def __repr__(self):
        return f"Obstaculo(tipo={self.tipo}, carril={self.carril}, x={self.x}, dano={self.dano})"
