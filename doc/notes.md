## RiBus

We have 1000 children, 9 buses and 17 schools.

A bus route can be initialized by picking a final_node = node_with_school and then create a random path of a distance between X and Y. Such minimum (X) or maximum (Y) distance has to match maximum time for a child to be on a bus.

A preferred way to initialize a bus route is to actually supply one to the program so we don't waste time generating them at the beginning.

Children are picked attending to dest_school and also child_address. A bus is forced to take, in order, all children at a particular child_address that go to the same school (but can ignore children at said child_address that go to a different school). This means that pickup operation operate at a cluster level, where a cluster can be of just one child. A cluster is defined by shared child_address and shared dest_school.

A bus route has an available capacity. This is arbitrary and can be decided to accept overbooking to account for later cancellations.

### Initialization

#### General graph

- Nodes are cells on a map
- Edge definition based on adjacent cells on a map. 
- Every node has n clusters grouping children by same child_address AND dest_school

#### Bus route graph

- Edge definition based on bus-connected cells. Graph is directed.
- Initial 9 routes supplied by manual input
- Range of additional dest_school acceptable per route (knowing that maximum distance between bus route schools can't be > 18min).
- Size of cell (same as General graph, we share node ids)
- Maximum bus route allowed distance (in number of cells/nodes). Alternatively, maximum bus route allowed distance can use sum(time(cell)).


### Bus route

A single bus route is an array of graph nodes where:
- All nodes represent cells that are connected by bus-friendly streets (simple directed path in Bus route Graph)
- Per node, we know the bus payload (in detail) and the bus remaining physical capacity
- A node that has a dest_school frees up payload up to the children that have such dest_school. That dest_school is then removed from the bus route.
- Ends on a dest_school cell and can have more intermediate dest_school

All bus routes are added IN ORDER to a list of bus routes

### Cost function

- (1) students served < bus route expected capacity: + X PTS = function(expected capacity - students served)
- (2) No pickup on a cell: +100 pts (we promote useful cells)
- (3) Child spending > 40 min on a bus ride: +50 pts (we promote reasonable bus time for children)
- (4) Child spending < 3 min on a bus ride: +100 pts (these children can go walking)
- (5) Child spending >= 3 min AND < 8 min on a bus ride: +50 pts (we can serve these children through walking monitors) 
- (6) Extra school beyond the second school: +10 pts (school monitors cost extra)
- (7) dest_school with high graph closeness centrality added to bus route: + X PTS = function(node closeness centrality)

Vulnerable children (wheel chair) might need a separate manual treatment after all bus routes have been sorted out. Alternatively, we might want to give a bonus to a bus route that pick a wheelchair child. Note: not all buses are wheelchari friendly!

(ignoring)
- (8) Pickup of 1-cell children: +2 pts (we promote same-cell children)
- (9) Pickup of 2-cell children: +5 pts (we promote same-cell children)


### Definition of neighbour solution

We have two distinct phases with two respective neighbour solutions. Phase 1 is evaluated completely (attending to end_calculus criteria) before entering Phase 2.

Phase 1: greedy warming up (skeleton)

- Given a group of ordered routes, a neighbour solution is one that randomnly picks one of those bus routes and picks a random interior node. This node is then replaced by another path that connects its previously adjacent nodes in the path. This new connecting path can be as big as max_bypass_path_distance.

The purpose of this phase is to arrive to a fairly good selection of routes. This is what we call the skeleton. 
Optionally, as a last step of this Phase 1, we can find the best order of bus routes processing for such skeleton.

Phase 2: interference optimization

- Given a group of Phase 1 output routes, a neighbour solution is one that randomly picks a children_cluster that could belong to two or more bus routes (with shared dest_school) and is switched to one other bus route (picking a bus route path node where the bus has available capacity). This is tried until 1 children_cluster is swaped.


### Bus route evaluation

This evaluation remains the same for both Phases 1 and 2.

Per bus route:

- We identify the dest_schools in such bus route.
- We traverse the array of bus-connected cells and per cell we:
    - If bus available_capacity allows, we take as many child_dest_school clusters that match  bus-route dest_schools 
    - We evaluate cost function for that cell
    - If the cell corresponds to a bus-route dest_school, we remove child_dest_school clusters and update available capacity

- We process global cost subfunctions that need the whole rout traversing to have ocurred first.

Global evaluation is the sum of independent bus routes.

#### Cost function evaluation per bus route in detail

- (1) students served < bus route expected capacity: + X PTS = function(expected capacity - students served)
- (2) No pickup on a cell: +100 pts (we promote useful cells)
- (3) Child spending > 40 min on a bus ride: +50 pts (we promote reasonable bus time for children)
- (4) Child spending < 3 min on a bus ride: +100 pts (these children can go walking)
- (5) Child spending >= 3 min AND < 8 min on a bus ride: +50 pts (we can serve these children through walking monitors) 
- (6) Extra school beyond the second school: +10 pts (school monitors cost extra)
- (7) dest_school with high graph closeness centrality added to bus route: + X PTS = function(node closeness centrality)

Given a bus route path:
    we first identify the dest_schools found in such route
    we measure cost_function (6) and (7)
    for every bus route node we take the same node in the clusters graph:
        we take dest_school clusters as long as we have available_capacity
        we update payload and available capacity
        we take dest_school clusters in 1-cell nodes as long as we have available capacity
        we update payload and available capacity
        we take dest_school clusters in 2-cell nodes as long as we have available capacity
        we update payload and available capacity

        we remove selected dest_school clusters for the node in the clusters graph

        we update time_on_bus for every dest_school cluster in the bus route so far.
        
        if bus route node has dest_school, we remove dest_school clusters from that node
            we calculate cost_function (3) (4) and (5) for those removed dest_school clusters 
            we update payload and available capacity

        we tag the node with time [nostop, stop, school]

        we calculate cost_function (2) 
   
    we calculate cost_function (1) 

Total cost = Sum(bus routes cost)

