## RiBus

We have 1000 children, 9 buses and 17 schools.

A bus route can be initialized by picking a final_node = node_with_school and then create a random path of a distance between X and Y. Such minimum (X) or maximum (Y) distance has to match maximum time for a child to be on a bus.

Children are picked attending to dest_school and also child_address. A bus is forced to take, in order, all children at a particular child_address that go to the same school (but can ignore children at said child_address that go to a different school). This means that pickup operation operate at a cluster level, where a cluster can be of just one child. A cluster is defined by shared child_address and shared dest_school.

A bus route has an available capacity. This is arbitrary and can be decided to accept overbooking to account for later cancellations.

### Initialization

#### General graph

- Nodes are cells on a map
- Edge definition based on adjacent cells on a map. 
- Every node has n clusters grouping children by same child_address AND dest_school

#### Bus route graph

- Edge definition based on bus-connected cells. Graph is directed.
- Initial 9 routes allocated to random dest_school (we might want to favor bigger schools in the future)
- Range of additional dest_school acceptable per route (knowing that maximum distance between schools can't be > 18min).
- Size of cell (same as General graph, we share node ids)
- Maximum bus route allowed distance (in number of cells/nodes)


### Bus route

A single bus route is an array of graph nodes where:
- All nodes represent cells that are connected by bus-friendly streets (simple directed path in Bus route Graph)
- Per node, we know the bus payload (in detail) and the bus remaining capacity
- A node that has a dest_school frees up payload up to the children that have such dest_school
- Ends on a dest_school cell and can have more intermediate dest_school

All bus routes are added IN ORDER to a list of bus routes

### Cost function

- (1) No pickup on a cell: +50 pts (we promote useful cells)
- (2) Pickup of 1-cell children: +2 pts (we promote same-cell children)
- (3) Pickup of 2-cell children: +5 pts (we promote same-cell children)
- (4) Child spending > 40 min on a bus ride: +50 pts (we promote reasonable bus time for children)
- (5) Extra school beyond the second school: +10 pts (school monitors cost extra)

Vulnerable children (wheel chair) might need a separate manual treatment after all bus routes have been sorted out. Alternatively, we might want to give a bonus to a bus route that pick a wheelchair child. Note: not all buses are wheelchari friendly!

### Definition of neighbour solution

- Given a group of ordered routes, a neighbour solution is one that randomly picks one of those bus routes and creates a completely new route following the initialization criteria (has to end on a school, has to have at least 1 other school in its journey and has to have a length between X and Y)

**Deprecated**
- Given a groups of bus routes, a neighbour solution is one that randomnly picks one of those bus routes and then randomly substitutes a cell X for another unused adjacent cell (f(X)) while keeping the maximum distance restriction.
- final_node (that includes a dest_school) can't be subject to this random selection but intermediate dest_schools can.


### Bus route evaluation

- We identify the dest_schools in such bus route.
- We traverse the array of bus-connected cells and per cell we:
    - If bus available_capacity allows, we take as many child_dest_school clusters that match  bus-route dest_schools 
    - We evaluate cost function for that cell
    - If the cell corresponds to a bus-route dest_school, we remove child_dest_school clusters and update available capacity

Global evaluation is the sum of independent bus routes.


Given a bus route path:
    we identify the dest_schools found in such route
    we measure cost_function (5) for number of schools > 2
    for every node we take the same node in the children route path:
        we take dest_school clusters as long as we have available_capacity
        we update payload and available capacity
        we take dest_school clusters in 1-cell nodes as long as we have available capacity
        we update payload and available capacity
        we take dest_school clusters in 2-cell nodes as long as we have available capacity
        we update payload and available capacity

        we remove selected dest_school clusters for the node
        
        if node has dest_school, we remove dest_school clusters from that node
        we update payload and available capacity

        we tag the node with time [nostop, stop, school]
        we calculate cost_function (1) (2) (3)

    for every node we:
        for every dest_school cluster we obtain total time for it
        we calculate cost_function (4)

Total cost = Sum(bus routes cost)

