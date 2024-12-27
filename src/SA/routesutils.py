import random

def getFreshRoute(rb, bus):

    school = rb.list_of_schools[random.choice(list(rb.list_of_schools))]
    route = {"id":bus["id"], "bus_capacity":bus["capacity"], "bus_available_capacity":bus["capacity"], "students":0, "orig_schools": [school], "schools":[school], "cost":0}
    length = rb.avg_length_of_routes - random.choice(range(rb.delta_length))
    connected_nodes = []

    # we take the last tuple, and then the second node, which has to be, by definition, a school node
    last_node = list(nx.dfs_edges(rb.bus_grid, school["node"], depth_limit=length))[-1][-1]

    # we also need to make sure the path goes through 1 other school TBD. For now we pick one random
    for path in nx.all_simple_paths(rb.bus_grid, source=school["node"], target=last_node, cutoff=length):
        if len(path) >= int(length):
            connected_nodes = path
            break
    connected_nodes_length = len(connected_nodes)

    path = []
    node_index = {}

    for index, node in enumerate(connected_nodes):
        if index == 0:
            path.append({"node_id":node, "school": [school], "0cell": [], 
                "1cell": [], 
                "2cell":[], 
                "payload": 0, "time": 2})
        else:
            schools_by_node = []
            sbn_list = rb.getSchoolsByNode(node)

            # FIXME redundant
            for s in sbn_list:
                schools_by_node.append(rb.list_of_schools[s])

            if schools_by_node:
                path.append({"node_id":node, "school": schools_by_node, "0cell": [], 
                    "1cell": [], 
                    "2cell":[], 
                    "payload": 0, "time": 2})     
                route["schools"] = route["schools"] + schools_by_node
                route["orig_schools"] = route["orig_schools"] + schools_by_node

            else:
                path.append({"node_id":node, "school": [], "0cell": [], 
                    "1cell": [], 
                    "2cell":[], 
                    "payload": 0, "time": 0})     
                     
        # we create a reverse index to acount for the following path reverse
        # print('route["schools"]',route["schools"])
        node_index[node] = connected_nodes_length - index -1

    route["path"] = path
    route["path"].reverse()
    route["node_index"] = node_index

    if len(route["orig_schools"]) > 2:
        route["cost"] += 10

    return route
