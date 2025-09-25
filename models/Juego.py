import threading, time
from models.Carro import Carro
from models.Carretera import Carretera
from models.Obstaculo import Obstaculo
from models.ArbolAVL import ArbolAVL


class JuegoModel:
    def __init__(self, longitud, energia_inicial, velocidad, intervalo):
        self.carro = Carro()
        self.carretera = Carretera(longitud)
        self.energia = energia_inicial
        self.terminado = False

        # Árbol AVL para obstáculos
        self.arbol_obstaculos = ArbolAVL()
        self.obstaculos_visibles = []  # Obstáculos en pantalla

        # Configuración del loop
        self.velocidad = velocidad
        self.intervalo = intervalo
        self.en_ejecucion = True

    def agregar_obstaculo(self, x, carril, tipo="normal", dano=10):
        obstaculo = Obstaculo(x, carril, tipo, dano)
        self.carretera.agregar_obstaculo(obstaculo)

        # Insertar en el árbol AVL también
        self.arbol_obstaculos.insertar(x, carril, tipo, dano, obstaculo)

    def actualizar_obstaculos_visibles(self, x_min, x_max):
        """Consulta el AVL para obtener obstáculos en el rango visible"""
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

    def update(self, screen_width=800):
        """Un ciclo de actualización del juego"""
        if not self.en_ejecucion or self.terminado:
            return

        self.carro.actualizar_salto()

        # Mover todos los obstáculos
        for obst in self.carretera.obstaculos:
            obst.mover(self.velocidad)

        # Actualizar visibles
        x_min = self.carro.x - 100
        x_max = self.carro.x + screen_width
        self.actualizar_obstaculos_visibles(x_min, x_max)

        # Verificar colisiones
        self.verificar_colisiones()

        # Debug info
        estado_salto = f"(saltando, altura={self.carro.altura})" if self.carro.esta_saltando else ""
        print(f"🚗 Carro carril={self.carro.carril} {estado_salto}, energía={self.energia}%")


class GameThread(threading.Thread):
    """Thread que ejecuta la lógica del juego"""
    def __init__(self, juego, screen_width=800):
        super().__init__()
        self.juego = juego
        self.screen_width = screen_width

    def run(self):
        while not self.juego.terminado and self.juego.en_ejecucion:
            self.juego.update(self.screen_width)
            time.sleep(self.juego.intervalo)


class TreeVisualizerThread(threading.Thread):
    """Thread que dibuja/visualiza el árbol AVL"""
    def __init__(self, juego):
        super().__init__()
        self.juego = juego

    def run(self):
        while not self.juego.terminado and self.juego.en_ejecucion:
            # Aquí podrías usar pygame, tkinter, o solo print()
            print("🌳 Estado actual del árbol AVL:")
            self.juego.arbol_obstaculos.imprimir()  # ← debes tener un método imprimir en tu AVL
            time.sleep(2)  # refresca cada 2 seg
