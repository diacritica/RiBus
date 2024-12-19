import math

#
# Computes graph bounds based on the bounds
# of all the features in the geojson.
#
def compute_graph_bounds(data):
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
    return bounds

def compute_feature_bounds(data):
    for feature in data['features']:
        minx = float('inf')
        miny = float('inf')
        maxx = float('-inf')
        maxy = float('-inf')

        for coordinate in feature['geometry']['coordinates'][0][0]:
            x = coordinate[0]
            y = coordinate[1]

            maxx = max(x, maxx)
            maxy = max(y, maxy)
            minx = min(x, minx)
            miny = min(y, miny)

        feature['properties']['left'] = minx
        feature['properties']['right'] = maxx
        feature['properties']['top'] = miny
        feature['properties']['bottom'] = maxy

    return data

def create_graph_nodes_from_features(data):
    nodes = []

    # Generar el grafo en formato DOT
    for feature in data['features']:
        props = feature['properties']
        id_ = props['id']
        left, right, top, bottom = props['left'], props['right'], props['top'], props['bottom']

        width = right - left
        height = bottom - top

        half_width = width / 2
        half_height = height / 2

        x = left + half_width
        y = top + half_height

        nodes.append({
            "id": id_,
            "edges": set(),
            "center": {"x": x, "y": y},
            "rect": {"left": left, "right": right, "top": top, "bottom": bottom}
        })

    return nodes

#
# Computes the minimal distance between nodes.
#
def compute_min_distance_from_nodes(nodes, threshold = 1):
    # Buscar la distancia mínima entre celdas
    min_distance = float('inf')
    for ai in range(len(nodes) - 1):
        a = nodes[ai]
        for bi in range(ai + 1, len(nodes)):
            b = nodes[bi]
            d = math.hypot(a['center']['x'] - b['center']['x'], a['center']['y'] - b['center']['y'])
            if d < threshold:
                continue
            min_distance = min(d, min_distance)
    return min_distance

#
# Connects every node adding proper edges.
#
def connect_nodes(nodes, min_distance, threshold = 1):
    connections = 0
    for ai in range(len(nodes) - 1):
        a = nodes[ai]
        for bi in range(ai + 1, len(nodes)):
            b = nodes[bi]
            d = math.hypot(a['center']['x'] - b['center']['x'], a['center']['y'] - b['center']['y'])
            if abs(d - min_distance) < threshold:
                if b['id'] not in a['edges']:
                    connections += 1
                    a['edges'].add(b['id'])

                if a['id'] not in b['edges']:
                    b['edges'].add(a['id'])

                # No puede haber más de 6 conexiones en una celda hexagonal.
                if len(a['edges']) > 6 or len(b['edges']) > 6:
                    print(a['edges'], b['edges'])
                    raise ValueError('¡¿Pero qué has hecho?!')

def create_graph_svg(bounds, nodes, min_distance):
    svg = f"<svg viewBox=\"{-min_distance} {-min_distance} {bounds['width'] + min_distance * 4} {bounds['height'] + min_distance * 4}\">\n"
    for a in nodes:
        for node_id in a['edges']:
            result = [node for node in nodes if node["id"] == node_id]
            if not result:
                continue
            [b] = result
            svg += f"<line x1=\"{a['center']['x'] - bounds['left']}\" y1=\"{a['center']['y'] - bounds['top']}\" x2=\"{b['center']['x'] - bounds['left']}\" y2=\"{b['center']['y'] - bounds['top']}\" stroke-width=\"10\" stroke=\"#f00\" />\n"

    for node in nodes:
        svg += f"  <circle cx=\"{node['center']['x'] - bounds['left']}\" cy=\"{node['center']['y'] - bounds['top']}\" r=\"20\" fill=\"#000\" />\n"

    svg += "</svg>\n"
    return svg

def create_digraph_dot(bounds, nodes):
    edges = set()

    dot = "digraph {\n"
    for node in nodes:
        dot += f"  node_{int(node['id'])}[label=\"{int(node['id'])}\", shape=\"circle\"]\n"
        for edge in node['edges']:
            edge_id_a = f"{int(node['id'])}->${int(edge)}"
            edge_id_b = f"{int(edge)}->${int(node['id'])}"
            if edge_id_a not in edges:
                dot += f"node_{int(node['id'])} -> node_{int(edge)}\n"
                edges.add(edge_id_a)
            if edge_id_b not in edges:
                dot += f"node_{int(edge)} -> node_{int(node['id'])}\n"
                edges.add(edge_id_b)
    dot += "}\n"
    return dot


def create_graph_dot(bounds, nodes):
    edges = set()

    dot = "graph {\n"
    for node in nodes:
        dot += f"  node_{int(node['id'])}[label=\"{int(node['id'])}\", shape=\"circle\"]\n"
        for edge in node['edges']:
            edge_id_a = f"{int(node['id'])}--${int(edge)}"
            edge_id_b = f"{int(edge)}--${int(node['id'])}"
            if edge_id_a not in edges:
                dot += f"node_{int(node['id'])} -- node_{int(edge)}\n"
                edges.add(edge_id_a)
            if edge_id_b not in edges:
                edges.add(edge_id_b)
    dot += "}\n"
    return dot

#
# Finds the nearest node to the specified coordinates.
#
def find_nearest_node(nodes, x, y):
    distance = float('inf')
    found_node = None
    for node in nodes:
        current_distance = math.hypot(x - node['center']['x'], y - node['center']['y'])
        # print('current_distance', current_distance, x, y, node['center']['x'], node['center']['y'])
        if current_distance < distance:
            distance = current_distance
            found_node = node
    return [found_node, distance]

#
# Creates a signle cluster
#
cluster_id = 9999
def create_cluster():
    global cluster_id
    cluster_id += 1
    return {
        'id': f'cluster_{cluster_id}',
        'count': 0,
        'distance': 0,
        'coordinates': {},
        'students': []
    }

def get_cluster_hash(x, y, school_id):
    return f'{x}:{y}:{school_id}'

#
# Creates clusters based on the coordinates and the schools
#
def create_clusters_from(nodes, data):
    clusters = {}
    for feature in data['features']:
        geometry = feature['geometry']
        if geometry['type'] != 'Point':
            continue

        x = geometry['coordinates'][0]
        y = geometry['coordinates'][1]

        student_id = feature['properties']['id']
        school_id = feature['properties']['colegio']
        distance = feature['properties']['distancia']

        cluster_hash = get_cluster_hash(x, y, school_id)
        if cluster_hash not in clusters:
            clusters[cluster_hash] = create_cluster()

        cluster = clusters[cluster_hash]

        cluster['coordinates']['x'] = x
        cluster['coordinates']['y'] = y
        cluster['distance'] = distance

        [node, distance] = find_nearest_node(nodes, x, y)
        if node is None:
            raise ValueError(f'Node not found for feature {student_id}')

        node_id = node['id']
        cluster['school'] = school_id
        cluster['node'] = f'node_{int(node_id)}'
        cluster['students'].append(student_id)

    return clusters

#
# Creates a list of dots from a geojson.
#
def create_cluster_nodes_from(nodes, clusters):
    cluster_nodes = {}

    processed = 0

    # Generar el grafo en formato DOT
    for _, cluster in clusters.items():
        node_id = cluster['node']
        result = [node for node in nodes if node["id"] == int(node_id.lstrip("node_"))]
        if not result:
            continue

        [node] = result

        if node_id not in cluster_nodes:
            cluster_nodes[node_id] = {
                'count': 0,
                'edges': list(map(lambda edge: f"node_{edge}", node['edges'])),
                'schools': {}
            }

        cluster_node = cluster_nodes[node_id]

        school_id = cluster['school']
        if school_id not in cluster_node['schools']:
            cluster_node['schools'][school_id] = []

        cluster_node['schools'][school_id].append({
            'id': cluster['id'],
            'count': len(cluster['students']),
        })

        processed += 1

    for node_id, cluster_node in cluster_nodes.items():
        schools = cluster_node['schools']
        for school_id, school in schools.items():
            sorted(school, key=lambda school_cluster: school_cluster['count'], reverse=True)

    for node in nodes:
        node_id = f"node_{node['id']}"
        if node_id not in cluster_nodes:
            cluster_nodes[node_id] = {
                'count': 0,
                'edges': list(map(lambda edge: f"node_{edge}", node['edges'])),
                'schools': {}
            }

    return cluster_nodes

def create_schools_from(nodes, data):
    schools = {}
    for feature in data['features']:
        geometry = feature['geometry']
        if geometry['type'] != 'Point':
            continue

        school_id = feature['properties']['name']
        x = feature['geometry']['coordinates'][0]
        y = feature['geometry']['coordinates'][1]

        [node, distance] = find_nearest_node(nodes, x, y)
        if node is None:
            raise ValueError(f'Node not found for feature {school_id}')

        node_id = node['id']
        schools[school_id] = {
            'id': school_id,
            'node': f'node_{int(node_id)}'
        }

    return schools

#
# Creates a graph from a geojson.
#
def create_graph_from(data):
    bounds  = compute_graph_bounds(data)
    nodes = create_graph_nodes_from_features(data)
    min_distance = compute_min_distance_from_nodes(nodes)
    num_connections = connect_nodes(nodes, min_distance)
    return {
        'bounds': bounds,
        'nodes': nodes,
        'min_distance': min_distance,
        'num_connections': num_connections
    }

def create_routes_svg(routes, schools, students, full, roads):
    solution_colors = [
        '#f00',
        '#0f0',
        '#00f',
        '#700',
        '#070',
        '#007',
        '#f0f',
        '#ff0',
        '#0ff',
        '#707',
        '#770',
        '#077',
    ]
    svg = f"<svg viewBox=\"{-full['min_distance']} {-full['min_distance']} {full['bounds']['width'] + full['min_distance'] * 4} {full['bounds']['height'] + full['min_distance'] * 4}\">\n"
    for a in full['nodes']:
        for node_id in a['edges']:
            result = [node for node in full['nodes'] if node["id"] == node_id]
            if not result:
                continue
            [b] = result
            svg += f"<line x1=\"{a['center']['x'] - full['bounds']['left']}\" y1=\"{a['center']['y'] - full['bounds']['top']}\" x2=\"{b['center']['x'] - full['bounds']['left']}\" y2=\"{b['center']['y'] - full['bounds']['top']}\" stroke-width=\"10\" stroke=\"#000\" />\n"

    for a in roads['nodes']:
        for node_id in a['edges']:
            result = [node for node in roads['nodes'] if node["id"] == node_id]
            if not result:
                continue
            [b] = result
            svg += f"<line x1=\"{a['center']['x'] - full['bounds']['left']}\" y1=\"{a['center']['y'] - full['bounds']['top']}\" x2=\"{b['center']['x'] - full['bounds']['left']}\" y2=\"{b['center']['y'] - full['bounds']['top']}\" stroke-width=\"8\" stroke=\"#555\" />\n"

    for node in full['nodes']:
        svg += f"  <circle cx=\"{node['center']['x'] - full['bounds']['left']}\" cy=\"{node['center']['y'] - full['bounds']['top']}\" r=\"20\" fill=\"#000\" />\n"

    for solution_index, route in enumerate(routes['solution']):
        prev_node = None

        node_last_index = len(route['path']) - 1
        for node_index, node_step in enumerate(route['path']):
            node_id = int(node_step['node_id'].lstrip('node_'))
            result = [node for node in full['nodes'] if node["id"] == node_id]
            if not result:
                continue

            [node] = result

            cx = node['center']['x'] - full['bounds']['left']
            cy = node['center']['y'] - full['bounds']['top']

            if prev_node:
                is_last_node = node_index == node_last_index
                if is_last_node:
                    svg += f"  <rect x=\"{cx - 60}\" y=\"{cy - 60}\" width=\"120\" height=\"120\" fill=\"{solution_colors[solution_index]}\" />\n"
                else:
                    svg += f"  <circle cx=\"{cx}\" cy=\"{cy}\" r=\"40\" fill=\"{solution_colors[solution_index]}\" />\n"
            else:
                svg += f"  <circle cx=\"{cx}\" cy=\"{cy}\" r=\"80\" fill=\"{solution_colors[solution_index]}\" />\n"


            if prev_node:
                svg += f"<line x1=\"{cx}\" y1=\"{cy}\" x2=\"{prev_node['center']['x'] - full['bounds']['left']}\" y2=\"{prev_node['center']['y'] - full['bounds']['top']}\" stroke-width=\"20\" stroke=\"{solution_colors[solution_index]}\" />\n"
            prev_node = node

        solution_index += 1

    svg += "</svg>\n"
    return svg

