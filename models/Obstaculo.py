class Obstaculo:
    def __init__(self, x, carril, tipo="normal", dano=10):
        self.x = x
        self.carril = carril
        self.tipo = tipo
        self.dano = dano
        self.ancho = 20
        self.alto = 20
        self.ya_colisionado = False

    def mover(self, velocidad):
        """✅ LOS OBSTÁCULOS SE MUEVEN HACIA EL CARRO"""
        self.x -= velocidad  # Se mueven hacia la izquierda

    def obtener_rectangulo(self):
        """Devuelve el rectángulo de colisión"""
        y_pos = 400 + self.carril * 60
        return (self.x, y_pos, self.ancho, self.alto)

    def colisiona_con(self, carro):
        """Verifica colisión con el carro"""
        obst_rect = self.obtener_rectangulo()
        carro_rect = carro.obtener_rectangulo()
        
        return (carro_rect[0] < obst_rect[0] + obst_rect[2] and
                carro_rect[0] + carro_rect[2] > obst_rect[0] and
                carro_rect[1] < obst_rect[1] + obst_rect[3] and
                carro_rect[1] + carro_rect[3] > obst_rect[1])