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
        """Genera obstáculos iniciales desde JSON y algunos extra"""
        # Obstáculos del JSON
        for obst_data in obstaculos_config:
            try:
                x = obst_data.get("x", 0)
                carril = obst_data.get("carril", 0)
                tipo = obst_data.get("tipo", "cono")
                self.agregar_obstaculo(x, carril, tipo)
            except Exception as e:
                print(f"❌ Error cargando obstáculo del JSON: {e}")
        
        # ✅ Generar obstáculos adicionales si hay pocos
        if len(self.carretera.obstaculos) < 3:
            for i in range(3):
                x = 300 + (i * 200)
                carril = random.randint(0, 2)
                tipo = random.choice(["cono", "roca", "aceite", "hueco"])
                self.agregar_obstaculo(x, carril, tipo)

    def generar_obstaculos_dinamicos(self):
        """Genera obstáculos dinámicamente con distribución inteligente"""
        if self.carro.x <= self.ultima_generacion_x:
            return  # Esperar a que el carro avance más
            
        x_min = self.carro.x + 400  # Más distancia para reaccionar
        x_max = x_min + 600  # Rango más amplio
        
        print(f"🎯 GENERANDO entre X={x_min} y X={x_max}")
        
        # ✅ DISTRIBUCIÓN INTELIGENTE - máximo 2 obstáculos por grupo
        num_obstaculos = random.randint(1, 3)  # Reducir cantidad
        obstaculos_generados = 0
        
        # ✅ EVITAR MUCHOS OBSTÁCULOS EN LA MISMA ZONA
        carriles_disponibles = [0, 1, 2]
        random.shuffle(carriles_disponibles)  # Mezclar carriles
        
        for i in range(min(num_obstaculos, 3)):  # Máximo 3 obstáculos
            if not carriles_disponibles:
                break
                
            carril = carriles_disponibles.pop()  # Tomar carril disponible
            tipo = random.choice(["cono", "roca", "aceite", "hueco"])
            
            # ✅ DISTRIBUIR EN X - no todos en la misma posición
            if i == 0:
                x_pos = random.randint(x_min, x_min + 200)  # Primer obstáculo cerca
            elif i == 1:
                x_pos = random.randint(x_min + 200, x_min + 400)  # Segundo más lejos
            else:
                x_pos = random.randint(x_min + 400, x_max)  # Tercero más lejos aún
            
            if self.agregar_obstaculo(x_pos, carril, tipo):
                obstaculos_generados += 1
                print(f"✅ Generado {tipo} en carril {carril}, x={x_pos}")
        
        # ✅ ACTUALIZAR PARA PRÓXIMA GENERACIÓN
        self.ultima_generacion_x = x_max
        print(f"📦 Generados {obstaculos_generados} obstáculos")
        print(f"📍 Próxima generación en X={self.ultima_generacion_x}")

    def guardar_partida_actual(self):
        """Guarda el estado actual en JSON"""
        try:
            archivo = self.generador_json.guardar_partida(self.arbol_obstaculos, self.carro.x)
            print(f"💾 Partida guardada: {archivo}")
        except Exception as e:
            print(f"❌ Error guardando partida: {e}")

    def agregar_obstaculo(self, x, carril, tipo="normal", dano=10):
        """Agrega obstáculo con verificación de superposición"""
        try:
            # ✅ VERIFICAR DISTANCIA MÍNIMA DEL CARRO
            if x <= self.carro.x + 150:  # Mínimo 150px de distancia
                x = self.carro.x + 200
                print(f"🔧 Ajustando posición a X={x} por distancia mínima")
            
            # ✅ VERIFICAR SUPERPOSICIÓN CON OTROS OBSTÁCULOS
            for obstaculo_existente in self.carretera.obstaculos:
                # Evitar obstáculos en la misma zona (±100px)
                if (abs(obstaculo_existente.x - x) < 150 and 
                    obstaculo_existente.carril == carril):
                    print(f"🚫 Obstáculo muy cerca en X={obstaculo_existente.x}, carril {carril}")
                    return False  # No agregar este obstáculo
            
            obstaculo = Obstaculo(x, carril, tipo, dano)
            self.carretera.agregar_obstaculo(obstaculo)
            self.arbol_obstaculos.insertar(x, carril, tipo, dano, obstaculo)
            print(f"➕ Obstáculo agregado: {tipo} en X:{x}, Carril:{carril}")
            return True
        except Exception as e:
            print(f"❌ ERROR agregando obstáculo: {e}")
            return False

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
        """Ciclo de actualización - SIN movimiento de obstáculos"""
        if not self.en_ejecucion or self.terminado:
            return

        # ✅ 1. SOLO EL CARRO AVANZA
        self.carro.avanzar()  # Esto aumenta self.carro.x

        # ✅ 2. Generar obstáculos dinámicos
        self.generar_obstaculos_dinamicos()

        # ✅ 3. Actualizar salto del carro
        self.carro.actualizar_salto()

        # ❌ 4. ¡NO MOVER OBSTÁCULOS! Eliminar cualquier código aquí

        # ✅ 5. Actualizar obstáculos visibles
        x_min = max(0, self.carro.x - 100)
        x_max = self.carro.x + screen_width + 200
        self.actualizar_obstaculos_visibles(x_min, x_max)

        # ✅ 6. Verificar colisiones
        self.verificar_colisiones()
        
        # ✅ 7. Debug para confirmar movimiento correcto
        if self.carro.x % 100 == 0:
            print(f"🚗 Carro AVANZA: X={self.carro.x}")
            if self.carretera.obstaculos:
                print(f"📍 Obstáculo FIJO: X={self.carretera.obstaculos[0].x}")

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