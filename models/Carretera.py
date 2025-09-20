class Carretera:
    def __init__(self, longitud=100):
        """
        longitud: distancia total de la carretera en 'unidades' (metros simulados)
        """
        self.longitud = longitud
        self.obstaculos = []  # lista de obstáculos

    def agregar_obstaculo(self, obstaculo):
        # Evitar que haya dos obstáculos en la misma posición y carril
        for o in self.obstaculos:
            if o.x == obstaculo.x and o.carril == obstaculo.carril:
                raise ValueError("Ya existe un obstáculo en esa posición y carril.")
        self.obstaculos.append(obstaculo)

    def obtener_obstaculos_en_rango(self, x_min, x_max):
        """
        Devuelve los obstáculos visibles en el rango [x_min, x_max]
        """
        return [o for o in self.obstaculos if x_min <= o.x <= x_max]
