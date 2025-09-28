import random
import threading, time
from models.GenerarJSON import GenerarJSON
from models.Carro import Carro
from models.Carretera import Carretera
from models.Obstaculo import Obstaculo
from models.ArbolAVL import ArbolAVL

class JuegoModel:
    def __init__(self, longitud, energia_inicial, velocidad, intervalo, config_json):
        self.carro = Carro()
        self.carretera = Carretera(longitud)
        self.energia = energia_inicial
        self.energia_maxima = energia_inicial
        self.terminado = False

        # Árbol AVL para obstáculos
        self.arbol_obstaculos = ArbolAVL()
        self.obstaculos_visibles = []

        # Configuración del loop
        self.velocidad = velocidad
        self.intervalo = intervalo
        self.en_ejecucion = True

        self.generador_json = GenerarJSON(config_json.get("configuraciones", {}))
        self.ultima_generacion_x = 100
        self.intervalo_generacion = 150
        self.probabilidad_obstaculo = 0.8
        
        self.ultima_generacion_x = 300  # Empezar después de los obstáculos iniciales
        self.intervalo_generacion = 200  # Distancia entre generaciones
        
        # Generar obstáculos iniciales
        obstaculos_config = config_json.get("obstaculos", [])
        self.generar_obstaculos_iniciales(obstaculos_config)

    def generar_obstaculos_iniciales(self, obstaculos_config):
        """Genera obstáculos iniciales - QUE ESTÉN FUERA DE PANTALLA INICIAL"""
        # Obstáculos del JSON (ajustar posiciones si son muy cercanas)
        for obst_data in obstaculos_config:
            try:
                x = obst_data.get("x", 0)
                # ✅ Si x es menor a 300, ajustarlo para que no esté muy cerca del inicio
                if x < 300:
                    x = 300 + random.randint(0, 200)
                carril = obst_data.get("carril", 0)
                tipo = obst_data.get("tipo", "cono")
                self.agregar_obstaculo(x, carril, tipo)
            except Exception as e:
                print(f"❌ Error cargando obstáculo del JSON: {e}")
        
        # ✅ Generar obstáculos adicionales FUERA de la pantalla inicial
        if len(self.carretera.obstaculos) < 3:
            for i in range(3):
                x = 400 + (i * 250)  # ✅ Empezar en x=400 (fuera de pantalla inicial)
                carril = random.randint(0, 2)
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                self.agregar_obstaculo(x, carril, tipo)

    def generar_obstaculos_dinamicos(self, screen_width=800):
        """Genera obstáculos dinámicamente - EQUILIBRADO"""
        # ✅ GENERACIÓN MÁS ESPACIADA
        if self.carro.x >= self.ultima_generacion_x - 200:  # ✅ Más espaciado
            # ✅ Obstáculos a distancia razonable
            x_min = self.carro.x + screen_width - 100  # ✅ Distancia equilibrada
            x_max = x_min + 400  # ✅ Rango más amplio para dispersión
            
            print(f"🎯 GENERANDO EQUILIBRADO: {x_min}-{x_max} (Carro en X={self.carro.x})")
            
            # ✅ CANTIDAD EQUILIBRADA de obstáculos
            num_obstaculos = random.randint(1, 2)  # ✅ Máximo 3, mínimo 1
            obstaculos_generados = 0
            
            carriles_disponibles = [0, 1, 2]
            random.shuffle(carriles_disponibles)
            
            # ✅ PATRÓN MÁS JUSTO - no llenar todos los carriles
            for i in range(min(num_obstaculos, 1)):  # ✅ Máximo 2 obstáculos por generación
                if carriles_disponibles:
                    carril = carriles_disponibles.pop()
                else:
                    break  # ✅ No forzar más obstáculos si no hay carriles
                    
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                
                # ✅ Obstáculos más dispersos
                x_pos = random.randint(x_min, x_max)
                
                if self.agregar_obstaculo(x_pos, carril, tipo):
                    obstaculos_generados += 1
                    print(f"✅ Generado {tipo} en carril {carril}, x={x_pos}")
            
            # ✅ Próxima generación más espaciada
            self.ultima_generacion_x = self.carro.x + 250  # ✅ Más espacio entre generaciones
            print(f"📦 Generados {obstaculos_generados} obstáculos (modo equilibrado)")

    def guardar_partida_actual(self):
        """Guarda el estado actual en JSON"""
        try:
            archivo = self.generador_json.guardar_partida(self.arbol_obstaculos, self.carro.x)
            print(f"💾 Partida guardada: {archivo}")
        except Exception as e:
            print(f"❌ Error guardando partida: {e}")

    def agregar_obstaculo(self, x, carril, tipo="normal", dano=10):
        """Agrega obstáculo con verificación de superposición - AJUSTADO"""
        try:
            # ✅ VERIFICAR DISTANCIA MÍNIMA DEL CARRO (ahora que empieza en x=0)
            if x <= self.carro.x + 150:  # Mínimo 150px de distancia desde x=0
                x = self.carro.x + 200  # Ajustar a 200px de distancia
                print(f"🔧 Ajustando posición a X={x} por distancia mínima")
            
            # ✅ VERIFICAR SUPERPOSICIÓN CON OTROS OBSTÁCULOS
            for obstaculo_existente in self.carretera.obstaculos:
                # Evitar obstáculos en la misma zona (±100px)
                if (abs(obstaculo_existente.x - x) < 150 and 
                    obstaculo_existente.carril == carril):
                    print(f"🚫 Obstáculo muy cerca en X={obstaculo_existente.x}, carril {carril}")
                    return None
            
            obstaculo = Obstaculo(x, carril, tipo, dano)
            self.carretera.agregar_obstaculo(obstaculo)
            self.arbol_obstaculos.insertar(x, carril, tipo, dano, obstaculo)
            print(f"➕ Obstáculo agregado: {tipo} en X:{x}, Carril:{carril}")
            return obstaculo
        except Exception as e:
            print(f"❌ ERROR agregando obstáculo: {e}")
            return None

    def actualizar_obstaculos_visibles(self, x_min, x_max):
        """Actualiza obstáculos visibles"""
        try:
            self.obstaculos_visibles = self.arbol_obstaculos.obtener_en_rango(x_min, x_max, 0, 3)
        except:
            # Fallback si el árbol falla
            self.obstaculos_visibles = [
                obst for obst in self.carretera.obstaculos 
                if x_min <= obst.x <= x_max
            ]
        
        # Debug ocasional
        if random.random() < 0.05:
            print(f"👀 {len(self.obstaculos_visibles)} obstáculos visibles")

    def verificar_colisiones(self):
        """Verifica colisiones"""
        for obst in self.obstaculos_visibles:
            if obst.colisiona_con(self.carro):
                if not getattr(obst, 'ya_colisionado', False):
                    self.energia -= obst.dano
                    obst.ya_colisionado = True
                    print(f"💥 Choque con {obst.tipo}! Energía: {max(0, self.energia)}%")
                    
                    if self.energia <= 0:
                        self.terminado = True
                        print("❌ Juego terminado")
                        break

    def update(self, screen_width=800):
        """Ciclo de actualización - CON generación fuera de pantalla"""
        if not self.en_ejecucion or self.terminado:
            return

        # 1. El carro avanza
        self.carro.avanzar()

        # ✅ 2. Generar obstáculos DINÁMICOS fuera de pantalla
        self.generar_obstaculos_dinamicos(screen_width)  # ✅ Pasar screen_width

        # 3. Actualizar salto del carro
        self.carro.actualizar_salto()

        # 4. Actualizar obstáculos visibles
        x_min = max(0, self.carro.x - 100)
        x_max = self.carro.x + screen_width + 200  # ✅ Ver más allá de la pantalla
        self.actualizar_obstaculos_visibles(x_min, x_max)

        # 5. Verificar colisiones
        self.verificar_colisiones()
        
        # 6. Debug
        if self.carro.x % 500 == 0:
            print(f"🚗 Carro AVANZA: X={self.carro.x}")
            if self.carretera.obstaculos:
                print(f"📍 Obstáculo más cercano: X={self.carretera.obstaculos[0].x}")

    def reiniciar(self):
        """Reinicia el juego"""
        self.carro = Carro()
        self.carretera.obstaculos.clear()
        self.arbol_obstaculos = ArbolAVL()
        self.obstaculos_visibles.clear()
        self.energia = self.energia_maxima
        self.terminado = False
        self.ultima_generacion_x = 100
        # Regenerar obstáculos iniciales
        self.generar_obstaculos_iniciales([])
        print("🔄 Juego reiniciado")

class GameThread(threading.Thread):
    def __init__(self, juego, screen_width=800):
        super().__init__()
        self.juego = juego
        self.screen_width = screen_width

    def run(self):
        while not self.juego.terminado and self.juego.en_ejecucion:
            self.juego.update(self.screen_width)
            time.sleep(self.juego.intervalo)