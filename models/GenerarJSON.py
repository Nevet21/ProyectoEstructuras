# models/GeneradorJSONDinamico.py
import json
import random
from datetime import datetime

class GenerarJSON:
    def __init__(self, config_base):
        self.config_base = config_base
        self.archivo_partida = f"partida_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.obstaculos_generados = []
        
        self.tipos_obstaculos = ["cono", "roca", "aceite", "hueco"]
        self.carriles = [0, 1, 2]

    def generar_obstaculo_aleatorio(self, x_min, x_max):
        """Genera un obstáculo aleatorio en el rango especificado"""
        return {
            "x": random.randint(x_min, x_max),
            "carril": random.choice(self.carriles),
            "tipo": random.choice(self.tipos_obstaculos)
        }

    def guardar_partida(self, arbol_avl, posicion_actual):
        """Guarda el estado actual de la partida"""
        # Obtener todos los obstáculos del árbol AVL
        todos_obstaculos = self._obtener_obstaculos_desde_arbol(arbol_avl)
        
        datos = {
            "configuraciones": self.config_base,
            "obstaculos": todos_obstaculos,
            "metadata": {
                "fecha_actualizacion": datetime.now().isoformat(),
                "total_obstaculos": len(todos_obstaculos),
                "posicion_actual": posicion_actual
            }
        }
        
        with open(self.archivo_partida, 'w') as f:
            json.dump(datos, f, indent=2)
        
        return self.archivo_partida

    def _obtener_obstaculos_desde_arbol(self, arbol_avl):
        """Extrae los obstáculos del árbol AVL en formato JSON"""
        obstaculos = []
        self._recorrer_arbol(arbol_avl.raiz, obstaculos)
        return sorted(obstaculos, key=lambda o: o["x"])  # Ordenar por posición X

    def _recorrer_arbol(self, nodo, obstaculos):
        if nodo:
            self._recorrer_arbol(nodo.izquierda, obstaculos)
            obstaculos.append({
                "x": nodo.x,
                "carril": nodo.y,  # En tu código, 'y' representa el carril
                "tipo": nodo.tipo
            })
            self._recorrer_arbol(nodo.derecha, obstaculos)