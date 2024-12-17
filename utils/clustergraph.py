#!/usr/bin/env python3
import sys
import json
import geojson
from pathlib import Path

# Leer el archivo de los estudiantes.
students_file = Path(sys.argv[1])
students_content = students_file.read_text(encoding='utf-8')
students_data = json.loads(students_content)

# Leer el archivo del grafo.
mesh_file = Path(sys.argv[2])
mesh_content = mesh_file.read_text(encoding='utf-8')
mesh_data = json.loads(mesh_content)

crs = "urn:ogc:def:crs:EPSG::3857"
if mesh_data['crs']['properties']['name'] != crs or students_data['crs']['properties']['name'] != crs:
    raise ValueError('Invalid CRS')

mesh_graph = geojson.create_graph_from(mesh_data)
clusters = geojson.create_clusters_from(mesh_graph['nodes'], students_data)
cluster_nodes = geojson.create_cluster_nodes_from(clusters)

#print(json.dumps(clusters))
print(json.dumps(cluster_nodes))
