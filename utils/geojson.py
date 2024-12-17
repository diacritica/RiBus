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

def create_graph_nodes_from_features(data):
    nodes = []

    # Generar el grafo en formato DOT
    for feature in data['features']:
        props = feature['properties']
        id_ = props['id']
        left, right, top, bottom = props['left'], props['right'], props['top'], props['bottom']

        width = left - right
        height = top - bottom

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

def create_graph_dot(bounds, nodes):
    edges = set()

    dot = "graph {\n"
    for node in nodes:
        dot += f"  node_{int(node['id'])}[label=\"{int(node['id'])}\", shape=\"circle\"]\n"
        for edge in node['edges']:
            edge_id_a = f"{int(node['id'])}--${edge}"
            edge_id_b = f"{edge}--${int(node['id'])}"
            if edge_id_a not in edges:
                dot += f"{int(node['id'])} -- {edge}\n"
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
# Creates a list of dots from a geojson.
#
def create_students_from(nodes, data, min_distance):
    nodes_data = {}

    processed = 0

    # Generar el grafo en formato DOT
    for feature in data['features']:
        geometry = feature['geometry']
        if geometry['type'] != 'Point':
            continue

        x = geometry['coordinates'][0]
        y = geometry['coordinates'][1]

        student_id = feature['properties']['id']
        school_id = feature['properties']['colegio']
        # NOTA: No todos los estudiantes en estudiantes.geojson
        # tienen la propiedad 'distancia'.
        # distance = feature['properties']['distancia']

        [node, distance] = find_nearest_node(nodes, x, y)
        if node is None:
            raise ValueError(f'Node not found for feature {int(feature['properties']['id'])}')

        if distance > min_distance:
            raise ValueError(f'Feature student_{int(feature['properties']['id'])} is outside the node node_{int(node['id'])} by {distance - min_distance} (processed {int(processed)})')

        node_id = f'node_{int(node['id'])}'
        if node_id not in nodes_data:
            nodes_data[node_id] = {
                'id': node_id,
                'schools': {},
            }

        if school_id not in nodes_data[node_id]['schools']:
            nodes_data[node_id]['schools'][school_id] = []

        nodes_data[node_id]['schools'][school_id].append(f'student_{int(student_id)}')
        processed += 1

    return nodes_data

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
