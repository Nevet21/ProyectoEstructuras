# models/ArbolAVL.py
class NodoAVL:
    def __init__(self, x, y, tipo, dano, obstaculo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.dano = dano
        self.obstaculo = obstaculo  # Referencia al objeto Obstaculo real
        self.izquierda = None
        self.derecha = None
        self.altura = 1

    def __str__(self):
        return f"Nodo({self.x},{self.y})"

class ArbolAVL:
    def __init__(self):
        self.raiz = None

    def altura(self, nodo):
        if not nodo:
            return 0
        return nodo.altura

    def balance(self, nodo):
        if not nodo:
            return 0
        return self.altura(nodo.izquierda) - self.altura(nodo.derecha)

    def rotacion_derecha(self, y):
        x = y.izquierda
        T2 = x.derecha

        x.derecha = y
        y.izquierda = T2

        y.altura = max(self.altura(y.izquierda), self.altura(y.derecha)) + 1
        x.altura = max(self.altura(x.izquierda), self.altura(x.derecha)) + 1

        return x

    def rotacion_izquierda(self, x):
        y = x.derecha
        T2 = y.izquierda

        y.izquierda = x
        x.derecha = T2

        x.altura = max(self.altura(x.izquierda), self.altura(x.derecha)) + 1
        y.altura = max(self.altura(y.izquierda), self.altura(y.derecha)) + 1

        return y

    def insertar(self, x, y, tipo, dano, obstaculo):
        self.raiz = self._insertar(self.raiz, x, y, tipo, dano, obstaculo)

    def _insertar(self, nodo, x, y, tipo, dano, obstaculo):
        # Paso 1: Inserción normal BST
        if not nodo:
            return NodoAVL(x, y, tipo, dano, obstaculo)

        # Comparar por x, luego por y
        if x < nodo.x or (x == nodo.x and y < nodo.y):
            nodo.izquierda = self._insertar(nodo.izquierda, x, y, tipo, dano, obstaculo)
        elif x > nodo.x or (x == nodo.x and y > nodo.y):
            nodo.derecha = self._insertar(nodo.derecha, x, y, tipo, dano, obstaculo)
        else:
            # Coordenadas duplicadas - no permitidas
            return nodo

        # Paso 2: Actualizar altura del nodo actual
        nodo.altura = 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))

        # Paso 3: Obtener el factor de balance
        balance = self.balance(nodo)

        # Paso 4: Casos de desbalance

        # Caso Left Left
        if balance > 1 and (x < nodo.izquierda.x or (x == nodo.izquierda.x and y < nodo.izquierda.y)):
            return self.rotacion_derecha(nodo)

        # Caso Right Right
        if balance < -1 and (x > nodo.derecha.x or (x == nodo.derecha.x and y > nodo.derecha.y)):
            return self.rotacion_izquierda(nodo)

        # Caso Left Right
        if balance > 1 and (x > nodo.izquierda.x or (x == nodo.izquierda.x and y > nodo.izquierda.y)):
            nodo.izquierda = self.rotacion_izquierda(nodo.izquierda)
            return self.rotacion_derecha(nodo)

        # Caso Right Left
        if balance < -1 and (x < nodo.derecha.x or (x == nodo.derecha.x and y < nodo.derecha.y)):
            nodo.derecha = self.rotacion_derecha(nodo.derecha)
            return self.rotacion_izquierda(nodo)

        return nodo

    def obtener_en_rango(self, x_min, x_max, y_min, y_max):
        """Obtiene todos los obstáculos dentro del rango especificado"""
        resultados = []
        self._obtener_en_rango(self.raiz, x_min, x_max, y_min, y_max, resultados)
        return resultados

    def _obtener_en_rango(self, nodo, x_min, x_max, y_min, y_max, resultados):
        if not nodo:
            return

        # Si el nodo actual está en el rango, agregarlo
        if x_min <= nodo.x <= x_max and y_min <= nodo.y <= y_max:
            resultados.append(nodo.obstaculo)

        # Si el x_min es menor que el x del nodo, buscar en el subárbol izquierdo
        if x_min < nodo.x or (x_min <= nodo.x and y_min < nodo.y):
            self._obtener_en_rango(nodo.izquierda, x_min, x_max, y_min, y_max, resultados)

        # Si el x_max es mayor que el x del nodo, buscar en el subárbol derecho
        if x_max > nodo.x or (x_max >= nodo.x and y_max > nodo.y):
            self._obtener_en_rango(nodo.derecha, x_min, x_max, y_min, y_max, resultados)

    def inorden(self):
        """Recorrido inorden: izquierda - raíz - derecha"""
        resultado = []
        self._inorden(self.raiz, resultado)
        return [f"({nodo.x},{nodo.y})" for nodo in resultado]

    def _inorden(self, nodo, resultado):
        if nodo:
            self._inorden(nodo.izquierda, resultado)
            resultado.append(nodo)
            self._inorden(nodo.derecha, resultado)

    def preorden(self):
        """Recorrido preorden: raíz - izquierda - derecha"""
        resultado = []
        self._preorden(self.raiz, resultado)
        return [f"({nodo.x},{nodo.y})" for nodo in resultado]

    def _preorden(self, nodo, resultado):
        if nodo:
            resultado.append(nodo)
            self._preorden(nodo.izquierda, resultado)
            self._preorden(nodo.derecha, resultado)

    def postorden(self):
        """Recorrido postorden: izquierda - derecha - raíz"""
        resultado = []
        self._postorden(self.raiz, resultado)
        return [f"({nodo.x},{nodo.y})" for nodo in resultado]

    def _postorden(self, nodo, resultado):
        if nodo:
            self._postorden(nodo.izquierda, resultado)
            self._postorden(nodo.derecha, resultado)
            resultado.append(nodo)

    def esta_vacio(self):
        return self.raiz is None

    # Método para debug
    def imprimir_arbol(self, nodo=None, nivel=0, prefijo="Raíz: "):
        if nodo is None:
            nodo = self.raiz
        if nodo is not None:
            print(" " * nivel * 4 + prefijo + f"({nodo.x},{nodo.y})")
            if nodo.izquierda is not None:
                self.imprimir_arbol(nodo.izquierda, nivel + 1, "Izq: ")
            if nodo.derecha is not None:
                self.imprimir_arbol(nodo.derecha, nivel + 1, "Der: ")