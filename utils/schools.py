#!/usr/bin/env python3
import sys
import json
import geojson
from pathlib import Path

# Leer el archivo de los estudiantes.
schools_file = Path(sys.argv[1])
schools_content = schools_file.read_text(encoding='utf-8')
schools_data = json.loads(schools_content)

# Leer el archivo del grafo.
mesh_file = Path(sys.argv[2])
mesh_content = mesh_file.read_text(encoding='utf-8')
mesh_data = json.loads(mesh_content)

crs = "urn:ogc:def:crs:EPSG::3857"
if mesh_data['crs']['properties']['name'] != crs or schools_data['crs']['properties']['name'] != crs:
    raise ValueError('Invalid CRS')

mesh_graph = geojson.create_graph_from(mesh_data)
schools = geojson.create_schools_from(mesh_graph['nodes'], schools_data)

#print(json.dumps(clusters))
print(json.dumps(schools))
