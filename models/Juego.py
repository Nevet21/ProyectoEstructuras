import threading, time
from models.Carro import Carro
from models.Carretera import Carretera
from models.Obstaculo import Obstaculo

class JuegoModel(threading.Thread):
    def __init__(self, longitud=100, energia_inicial=100, velocidad=5, intervalo=0.2):
        super().__init__()
        self.carro = Carro()
        self.carretera = Carretera(longitud)
        self.energia = energia_inicial
        self.terminado = False

        # Configuración del loop
        self.velocidad = velocidad
        self.intervalo = intervalo
        self.en_ejecucion = True

    def agregar_obstaculo(self, x, carril, tipo="normal", dano=10):
        obstaculo = Obstaculo(x, carril, tipo, dano)
        self.carretera.agregar_obstaculo(obstaculo)

    def verificar_colisiones(self):
        for obst in self.carretera.obstaculos:
            if obst.colisiona_con(self.carro):
                self.energia -= obst.dano
                print(f"💥 Choque con {obst.tipo}! Energía: {self.energia}%")
                if self.energia <= 0:
                    self.terminado = True
                    print("❌ Juego terminado: sin energía.")

    def detener(self):
        self.en_ejecucion = False

    def run(self):
        while self.en_ejecucion and not self.terminado:
            self.carro.actualizar_salto()

            for obst in self.carretera.obstaculos:
                obst.mover(self.velocidad)

            self.verificar_colisiones()

            estado_salto = f"(saltando, altura={self.carro.altura})" if self.carro.esta_saltando else ""
            print(f"🚗 Carro carril={self.carro.carril} {estado_salto}, energía={self.energia}%")

            time.sleep(self.intervalo)
