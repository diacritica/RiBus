#!/usr/bin/env python3
import sys
import json
import geojson
from pathlib import Path

# Leer el archivo de entrada
input_file = Path(sys.argv[1])
content = input_file.read_text(encoding='utf-8')
data = json.loads(content)

geojson.compute_feature_bounds(data)

graph = geojson.create_graph_from(data)
dot = geojson.create_digraph_dot(graph['bounds'], graph['nodes'])
svg = geojson.create_graph_svg(graph['bounds'], graph['nodes'], graph['min_distance'])

# Guardar los archivos DOT y SVG
dot_file = input_file.with_suffix('.dot')
dot_file.write_text(dot, encoding='utf-8')

svg_file = input_file.with_suffix('.svg')
svg_file.write_text(svg, encoding='utf-8')

