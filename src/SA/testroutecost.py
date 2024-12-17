route_structure = {"bus_capacity":55,"bus_real_capacity":53,
                   "path":[{"id":1,"school":0,"payload":10,"time":1,"existing":[],
                            "local_clusters":[{"id":345,"n":5,"school":2},{"id":666,"n":2,"school":3}],
                            "nearby_clusters":[{"id":111,"n":2,"school":3},{"id":222,"n":1,"school":3}]},
                            {"id":3,"school":0,"payload":12,"time":1,"existing":[{"id":345,"n":5,"school":2,"duration":1},{"id":666,"n":2,"school":3,"duration":1},{"id":111,"n":2,"school":3,"duration":1},{"id":222,"n":1,"school":3,"duration":1}],
                            "local_clusters":[{"id":444,"n":2,"school":2}],
                            "nearby_clusters":[]},
                    {"id":7,"school":0,"payload":12,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":9,"school":0,"payload":19,"time":1,"local_clusters":[{"id":555,"n":3,"school":3},{"id":777,"n":2,"school":2}],
                            "nearby_clusters":[{"id":888,"n":1,"school":3},{"id":999,"n":1,"school":3}]},
                    {"id":20,"school":2,"payload":13,"time":2,"local_clusters":[],"nearby_clusters":[{"id":33,"n":2,"school":3},{"id":321,"n":1,"school":3}]},
                    {"id":23,"school":0,"payload":13,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":12,"school":3,"payload":0,"time":2,"local_clusters":[],"nearby_clusters":[]}]}


def route_total_cost(route_structure):

    total_cost = 0
    total_cost += route_cost_by_no_pickup(route_structure, 10)
    total_cost += route_cost_by_nonlocal_children(route_structure, 1)
 
    return total_cost

def route_cost_by_no_pickup(route_structure, weight):

    cost = 0
    for p in route_structure["path"][:-1]:
        if (len(p["local_clusters"]) == 0) and (len(p["nearby_clusters"]) == 0):
            cost +=  weight
    return cost


def route_cost_by_nonlocal_children(routes, weight):

    cost = 0
    for p in route_structure["path"][:-1]:
        for nc in p["nearby_clusters"]:
            cost += nc["n"] * weight
    return cost

def route_cost_by_long_trip(routes, weight):

    cost = 0
    for r in routes:
        for w in r:
            cost += w.count("v") * weight
    return cost

if __name__=="__main__":
    print("cost",route_total_cost(route_structure))



routes = [

{"id":"A", "bus_capacity":55, "schools":["CEIP AAA","CEIP BBB"], 
 "path": [
     {"node_id":"node_123", "school": False, "0cell": [{"school":"CEIP AAA", "cluster_id":666, "count":3},{"school":"CEIP AAA", "cluster_id":555, "count":1},{"school":"CEIP BBB", "cluster_id":166, "count":1}], 
      "1cell": [{"school":"CEIP BBB", "cluster_id":266, "count":1}], 
      "2cell":[{"school":"CEIP AAA", "cluster_id":366, "count":1}], 
      "payload": 7, "time": 1},

     {"node_id":"node_124", "school": False, "0cell": [{"school":"CEIP AAA", "cluster_id":666, "count":3},{"school":"CEIP AAA", "cluster_id":555, "count":1},{"school":"CEIP BBB", "cluster_id":166, "count":1}, {"school":"CEIP BBB", "cluster_id":167, "count":3}], 
      "1cell": [{"school":"CEIP BBB", "cluster_id":266, "count":1}], 
      "2cell":[{"school":"CEIP AAA", "cluster_id":366, "count":1}], 
      "payload": 10, "time": 1},

     {"node_id":"node_125", "school": False, "0cell": [{"school":"CEIP AAA", "cluster_id":666, "count":3},{"school":"CEIP AAA", "cluster_id":555, "count":1},{"school":"CEIP BBB", "cluster_id":166, "count":1}, {"school":"CEIP BBB", "cluster_id":167, "count":3}], 
      "1cell": [{"school":"CEIP BBB", "cluster_id":266, "count":1}], 
      "2cell":[{"school":"CEIP AAA", "cluster_id":366, "count":1}], 
      "payload": 10, "time": 0.60},


     {"node_id":"node_126", "school": "CEIP AAA", "0cell": [{"school":"CEIP BBB", "cluster_id":166, "count":1}, {"school":"CEIP BBB", "cluster_id":167, "count":3}], 
      "1cell": [{"school":"CEIP BBB", "cluster_id":266, "count":1}], 
      "2cell":[], 
      "payload": 5, "time": 2},

     {"node_id":"node_127", "school": False, "0cell": [{"school":"CEIP BBB", "cluster_id":166, "count":1}, {"school":"CEIP BBB", "cluster_id":167, "count":3}], 
      "1cell": [{"school":"CEIP BBB", "cluster_id":266, "count":1}], 
      "2cell":[], 
      "payload": 5, "time": 0.60},

     {"node_id":"node_128", "school": "CEIP BBB", "0cell": [], 
      "1cell": [], 
      "2cell":[], 
      "payload": 0, "time": 2},
 ]
 
 },

{"id":"B"},
{"id":"C"},
{},
{},
{},
{},


]

route_structure = {"bus_capacity":55,"bus_real_capacity":53,
                   "path":[{"id":1,"school":0,"payload":10,"time":1,"existing":[],
                            "local_clusters":[{"id":345,"n":5,"school":2},{"id":666,"n":2,"school":3}],
                            "nearby_clusters":[{"id":111,"n":2,"school":3},{"id":222,"n":1,"school":3}]},
                            {"id":3,"school":0,"payload":12,"time":1,"existing":[{"id":345,"n":5,"school":2,"duration":1},{"id":666,"n":2,"school":3,"duration":1},{"id":111,"n":2,"school":3,"duration":1},{"id":222,"n":1,"school":3,"duration":1}],
                            "local_clusters":[{"id":444,"n":2,"school":2}],
                            "nearby_clusters":[]},
                    {"id":7,"school":0,"payload":12,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":9,"school":0,"payload":19,"time":1,"local_clusters":[{"id":555,"n":3,"school":3},{"id":777,"n":2,"school":2}],
                            "nearby_clusters":[{"id":888,"n":1,"school":3},{"id":999,"n":1,"school":3}]},
                    {"id":20,"school":2,"payload":13,"time":2,"local_clusters":[],"nearby_clusters":[{"id":33,"n":2,"school":3},{"id":321,"n":1,"school":3}]},
                    {"id":23,"school":0,"payload":13,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":12,"school":3,"payload":0,"time":2,"local_clusters":[],"nearby_clusters":[]}]}