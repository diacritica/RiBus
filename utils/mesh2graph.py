#!/usr/bin/env python3
import sys
import json
import math
from pathlib import Path

# Leer el archivo de entrada
input_file = Path(sys.argv[1])
content = input_file.read_text(encoding='utf-8')
data = json.loads(content)

# Definir los límites iniciales
bounds = {
    "left": float('inf'),
    "top": float('inf'),
    "right": float('-inf'),
    "bottom": float('-inf'),
    "width": 0,
    "height": 0,
}

# Calcular los límites
for feature in data['features']:
    props = feature['properties']
    left, right, top, bottom = props['left'], props['right'], props['top'], props['bottom']
    bounds['left'] = min(left, bounds['left'])
    bounds['top'] = min(top, bounds['top'])
    bounds['right'] = max(right, bounds['right'])
    bounds['bottom'] = max(bottom, bounds['bottom'])

bounds['width'] = bounds['right'] - bounds['left']
bounds['height'] = bounds['bottom'] - bounds['top']

nodes = []

# Generar el grafo en formato DOT
dot = "digraph {\n"
for feature in data['features']:
    props = feature['properties']
    id_ = props['id']
    left, right, top, bottom = props['left'], props['right'], props['top'], props['bottom']

    width = left - right
    height = top - bottom

    half_width = width / 2
    half_height = height / 2

    x = (left - bounds['left']) + half_width
    y = (top - bounds['top']) + half_height

    print(feature['type'], feature['geometry']['type'], id_, left, right, top, bottom, x, y)

    nodes.append({
        "id": id_,
        "edges": set(),
        "center": {"x": x, "y": y},
        "rect": {"left": left, "right": right, "top": top, "bottom": bottom}
    })
    dot += f"  node_{id_}[label=\"{id_}\", shape=\"circle\"]\n"

dot += '\n'

# Buscar la distancia mínima entre celdas
min_distance = float('inf')
for ai in range(len(nodes) - 1):
    a = nodes[ai]
    for bi in range(ai + 1, len(nodes)):
        b = nodes[bi]
        d = math.hypot(a['center']['x'] - b['center']['x'], a['center']['y'] - b['center']['y'])
        # Ignorar elementos solapados (distancia aproximada a 0)
        if d < 1:
            continue
        min_distance = min(d, min_distance)

# Buscar nodos a distancia de 1 casilla y generar SVG
svg = f"<svg viewBox=\"{-min_distance} {-min_distance} {bounds['width'] + min_distance * 4} {bounds['height'] + min_distance * 4}\">\n"
for ai in range(len(nodes) - 1):
    a = nodes[ai]
    for bi in range(ai + 1, len(nodes)):
        b = nodes[bi]
        d = math.hypot(a['center']['x'] - b['center']['x'], a['center']['y'] - b['center']['y'])
        if abs(d - min_distance) < 1:
            if b['id'] not in a['edges']:
                dot += f"node_{a['id']} -> node_{b['id']}\n"
                svg += f"<line x1=\"{a['center']['x']}\" y1=\"{a['center']['y']}\" x2=\"{b['center']['x']}\" y2=\"{b['center']['y']}\" stroke-width=\"10\" stroke=\"#f00\" />\n"
                a['edges'].add(b['id'])
            if a['id'] not in b['edges']:
                b['edges'].add(a['id'])
                dot += f"node_{b['id']} -> node_{a['id']}\n"
            # No puede haber más de 6 conexiones en una celda hexagonal.
            if len(a['edges']) > 6 or len(b['edges']) > 6:
                print(a['edges'], b['edges'])
                raise ValueError('¡¿Pero qué has hecho?!')

# Generamos los puntos por encima de las líneas
for node in nodes:
    svg += f"  <circle cx=\"{node['center']['x']}\" cy=\"{node['center']['y']}\" r=\"20\" fill=\"#000\" />\n"

dot += '}\n'
svg += '</svg>\n'

# Guardar los archivos DOT y SVG
dot_file = input_file.with_suffix('.dot')
dot_file.write_text(dot, encoding='utf-8')

svg_file = input_file.with_suffix('.svg')
svg_file.write_text(svg, encoding='utf-8')

