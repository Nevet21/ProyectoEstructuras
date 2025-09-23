import threading, time
from models.Carro import Carro
from models.Carretera import Carretera
from models.Obstaculo import Obstaculo
from models.ArbolAVL import ArbolAVL  # ← Tu árbol AVL

class JuegoModel(threading.Thread):
    def __init__(self, longitud=100, energia_inicial=100, velocidad=5, intervalo=0.2):
        super().__init__()
        self.carro = Carro()
        self.carretera = Carretera(longitud)
        self.energia = energia_inicial
        self.terminado = False

        # NUEVO: Árbol AVL para obstáculos
        self.arbol_obstaculos = ArbolAVL()
        self.obstaculos_visibles = []  # Obstáculos en pantalla

        # Configuración del loop
        self.velocidad = velocidad
        self.intervalo = intervalo
        self.en_ejecucion = True

    def agregar_obstaculo(self, x, carril, tipo="normal", dano=10):
        obstaculo = Obstaculo(x, carril, tipo, dano)
        self.carretera.agregar_obstaculo(obstaculo)
        
        # NUEVO: Insertar en el árbol AVL también
        self.arbol_obstaculos.insertar(x, carril, tipo, dano, obstaculo)

    def actualizar_obstaculos_visibles(self, x_min, x_max):
        """Consulta el AVL para obtener obstáculos en el rango visible"""
        # NUEVO: Usar el árbol AVL para consulta eficiente
        self.obstaculos_visibles = self.arbol_obstaculos.obtener_en_rango(
            x_min, x_max, 0, 3  # y entre carriles 0-3
        )

    def verificar_colisiones(self):
        # Solo verificar con obstáculos visibles (más eficiente)
        for obst in self.obstaculos_visibles:
            if obst.colisiona_con(self.carro):
                self.energia -= obst.dano
                print(f"💥 Choque con {obst.tipo}! Energía: {self.energia}%")
                if self.energia <= 0:
                    self.terminado = True
                    print("❌ Juego terminado: sin energía.")

    def run(self):
        while self.en_ejecucion and not self.terminado:
            self.carro.actualizar_salto()

            # Mover todos los obstáculos
            for obst in self.carretera.obstaculos:
                obst.mover(self.velocidad)

            # NUEVO: Actualizar qué obstáculos son visibles
            x_min = self.carro.x - 100  # Margen izquierdo
            x_max = self.carro.x + self.WIDTH  # Hasta el final de pantalla
            self.actualizar_obstaculos_visibles(x_min, x_max)

            self.verificar_colisiones()

            estado_salto = f"(saltando, altura={self.carro.altura})" if self.carro.esta_saltando else ""
            print(f"🚗 Carro carril={self.carro.carril} {estado_salto}, energía={self.energia}%")

            time.sleep(self.intervalo)