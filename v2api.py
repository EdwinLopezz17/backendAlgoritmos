from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import csv
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

class Ciudad:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.distancia = sys.maxsize
        self.visitado = False
        self.enable = True
        self.camino = []
        

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'distancia': self.distancia,
            'visitado': self.visitado,
            'camino': [ciudad.to_dict() for ciudad in self.camino]
        }

matrix = []
matriz_costos = []
ciudades = []

def build_matrix():
    global matrix
    global matriz_costos
    matrix = []
    matriz_costos = []

    with open('data.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        rows = list(csvreader)

        citiesSet = set()
        for row in rows:
            origin, destination, cost = row
            citiesSet.add(origin)
            citiesSet.add(destination)

        ciudades.extend(sorted(citiesSet))

        for city in ciudades:
            matrix.append({'origin': city, 'destinations': [{'city': c, 'cost': 0} for c in ciudades]})

        for row in rows:
            origin, destination, cost = row
            originIndex = next((index for index, item in enumerate(matrix) if item['origin'] == origin), -1)
            destinationIndex = next((index for index, item in enumerate(matrix) if item['origin'] == destination), -1)
            matrix[originIndex]['destinations'][destinationIndex]['cost'] = int(cost)

        matriz_costos = [[destination['cost'] for destination in item['destinations']] for item in matrix]



@app.route('/dijkstra', methods=['POST'])
def ApiDijkstra():

    # Obtener los parámetros enviados desde Angular
    inicio= request.json.get('inicio')
    fin = request.json.get('fin')
    evitar = request.json.get('evitar')

    ciudades_obj = []
    ciudadOrigen = None
    ciudadFin = None
    for i in range(len(ciudades)):
        ciudades_obj.append(Ciudad(i, ciudades[i]))
        if(ciudades[i] == str(inicio)):
            ciudadOrigen = ciudades_obj[i]
        if(ciudades[i] == str(fin)):
            ciudadFin = ciudades_obj[i]
        if(ciudades[i] == str(evitar)):
            ciudades_obj[i].enable = False

    if(ciudadOrigen == None or ciudadFin == None):
        response = {
            'mensaje': 'Uno de las ciudades no esta en la lista'
        }
        return response

    camino, peso = dijkstra(matriz_costos, ciudades_obj, ciudadOrigen, ciudadFin)

    if len(camino) == 0:
        response = {
            'mensaje': 'No se encontró un camino para este destino'
        }
    else:
        camino_dict = [ciudad.to_dict() for ciudad in camino]
        response = {
            'camino': camino_dict,
            'peso': peso
        }

    return jsonify(response)

def dijkstra(matriz_costos, ciudadesObj, inicioObj, finObj):
    inicioObj.distancia = 0
    actual = inicioObj

    while actual != finObj:
        actual.visitado = True

        for i in range(len(matriz_costos[actual.id])):
            if matriz_costos[actual.id][i] != 0 and not ciudadesObj[i].visitado and ciudadesObj[i].enable:
                nueva_distancia = actual.distancia + matriz_costos[actual.id][i]
                if nueva_distancia < ciudadesObj[i].distancia:
                    ciudadesObj[i].distancia = nueva_distancia
                    ciudadesObj[i].camino = actual.camino + [actual]

        min_distancia = sys.maxsize
        for ciudad in ciudadesObj:
            if not ciudad.visitado and ciudad.distancia < min_distancia:
                min_distancia = ciudad.distancia
                actual = ciudad

    camino = finObj.camino + [finObj]
    peso = finObj.distancia

    return camino, peso

if __name__ == '__main__':
    build_matrix()
    app.run()