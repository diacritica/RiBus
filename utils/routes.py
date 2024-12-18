#!/usr/bin/env python3
import sys
import json
import geojson
from pathlib import Path

# Leer el archivo de los estudiantes.
routes_file = Path(sys.argv[1])
routes_content = routes_file.read_text(encoding='utf-8')
routes_data = json.loads(routes_content)

schools_file = Path(sys.argv[3])
schools_content = schools_file.read_text(encoding='utf-8')
schools_data = json.loads(schools_content)

students_file = Path(sys.argv[2])
students_content = students_file.read_text(encoding='utf-8')
students_data = json.loads(students_content)

# Leer el archivo de la malla para poder generar.
mesh_full_file = Path(sys.argv[4])
mesh_full_content = mesh_full_file.read_text(encoding='utf-8')
mesh_full_data = json.loads(mesh_full_content)
mesh_full = geojson.create_graph_from(mesh_full_data)

mesh_roads_file = Path(sys.argv[5])
mesh_roads_content = mesh_roads_file.read_text(encoding='utf-8')
mesh_roads_data = json.loads(mesh_roads_content)
mesh_roads = geojson.create_graph_from(mesh_roads_data)

svg = geojson.create_routes_svg(routes_data, students_data, schools_data, mesh_full, mesh_roads)
svg_file = routes_file.with_suffix('.svg')
svg_file.write_text(svg, encoding='utf-8')

