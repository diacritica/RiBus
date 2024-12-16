
# optimize for only one route change

def route_total_cost(routes):

    total_cost = 0
    total_cost += route_cost_by(routes, "a", 5)
    total_cost += route_cost_by(routes, "e", 4)
    total_cost += route_cost_by(routes, "r", 2)
    total_cost += route_cost_by(routes, "l", 1)

    total_cost += route_cost_by_no_pickup(routes, 10)
    total_cost += route_cost_by_nonlocal_children(routes, 30)
    total_cost += route_cost_by_long_trip(routes, 50)


    return total_cost

def route_cost_by(routes, l, weight):

    cost = 0
    for r in routes:
        for w in r:
            cost += w.count(l) * weight
    return cost


def route_cost_by_no_pickup(routes, weight):

    cost = 0
    for r in routes:
        for w in r:
            if w.count("b") < 0:
                cost +=  weight
    return cost


def route_cost_by_nonlocal_children(routes, weight):

    cost = 0
    for r in routes:
        for w in r:
            cost += w.count("z") * weight
    return cost

def route_cost_by_long_trip(routes, weight):

    cost = 0
    for r in routes:
        for w in r:
            cost += w.count("v") * weight
    return cost


