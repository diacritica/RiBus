## RiBus

We have 1000 children, 9 buses and 18 schools.

A bus route can be initialized by picking a final_node = node_with_school and then create a random path of a distance between X and Y. Such minimum (X) or maximum (Y) distance has to match maximum time for a child to be on a bus.

Children are picked attending to dest_school and also child_address. A bus is forced to take all children at a particular child_address that go to the same school (but can ignore children at said child_address that go to a different school). This means that pickup operation operate at a cluster level, where a cluster can be of just one child. A cluster is defined by shared child_address and shared dest_school.

A bus route has an available capacity. This is arbitrary and can be decided to accept overbooking.

### Initialization

#### General graph

- Nodes are cells on a map
- Edge definition based on adjacent cells on a map
- Every node has n clusters grouping children by same child_address AND dest_school

#### Bus route graph

- Initial 9 routes allocated to dest_school (we might want to favor bigger schools here)
- Number of additional dest_school acceptable per route (knowing that maximum distance between schools can't be > 18min) and that per every dest_school, we reduce the capacity by one (a school monitor is required)
- Size of cell (same as General graph)
- Maximum bus route allowed distance (in number of cells/nodes)
- Edge definition based on bus-connected cells on a map plus adjacent cells on a map that shared a 1-distance bus-connected cell
 

### Bus route

A single bus route is an array of graph nodes where:
- All nodes represent cells that are connected by bus-friendly streets
- Per node, we know the bus payload and the bus available capacity
- A node that has a dest_school frees up payload up to the children that have such dest_school
- Ends on a dest_school cell and can have more intermediate dest_school

### Cost function

- No pickup on a cell: +50 pts (we promote useful cells)
- Pickup of nearby children: +2 pts (we promote same-cell children)
- Child spending > 40 min on a bus ride: +50 pts (we promote reasonable bus time for children)

Vulnerable children (wheel chair) might need a separate manual treatment after all bus routes have been sorted out. Alternatively, we might want to give a bonus to a bus route that pick a wheelchair child. Note: not all buses are wheelchari friendly!

### Definition of neighbour solution

- Given a groups of bus routes, a neighbour solution is one that randomnly picks one of those bus routes and then randomly substitutes a cell X for another unused adjacent cell (f(X)) while keeping the maximum distance restriction.
- final_node (that includes a dest_school) can't be subject to this random selection but intermediate dest_schools can.

### Bus route evaluation

- We identify the dest_schools in such bus route.
- We traverse the array of bus-connected cells and per cell we:
    - If bus available_capacity allows, we take as many child_dest_school clusters that match  bus-route dest_schools 
    - We evaluate cost function for that cell
    - If the cell corresponds to a bus-route dest_school, we remove child_dest_school clusters and update available capacity