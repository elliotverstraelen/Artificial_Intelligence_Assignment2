from search import *

#################
# Problem class #
#################

class SoftFlow(Problem):

    def __init__(self, initial):
        self.initial = initial
        
    def actions(self, state):
        # Generate all possible pairs of points that could be connected
        for i in range(state.nbr):
            for j in range(state.nbc):
                for x in range(i+1, state.nbr): # ARE THE RANGES OK ? +1 ?
                    for y in range(0, state.nbc): # ARE THE RANGES OK ? j+1?
                        #check if the points form a valid segment
                        segment = Segment((i,j), (x, y))
                        if state.is_valid_segment(segment):
                            yield segment


    # not sure that this is the right way
    def result(self, state, action):
        grid = [row[:] for row in state.grid]
        p1, p2 = action.entry, action.desktop

        # Update the grid with the new segment
        grid[p1[0]][p1[1]] = str(len(state.segments) + 1)
        grid[p2[0]][p2[1]] = str(len(state.segments) + 1)

        # Add the new segment to the list of segments
        segments = state.segments + [Segment(p1, p2)]
    
        # Create a new state with the updated grid
        return State(grid)

    def goal_test(self, state):
        # Check if all cells are occupied and all segments are connected
        for i in range(state.nbr):
            for j in range(state.nbc):
                if state.grid[i][j] == ' ':
                    return False
        return len(state.segments) == state.nbr * state.nbc - 1

    def h(self, node):
        # find the set of unconnected entry and desktop points
        unconnected = set() # use a set for performance
        for i in range(node.state.nbr):
            for j in range(node.state.nbc):
                cell = node.state.grid[i][j]
                if ord('a') <= ord(cell) <= ord('a') + node.state.nbr:  # IMPORTANT ! does this ASCI calculation work ?
                    unconnected.add((i, j))

        if len(unconnected) % 2 != 0:
            return float('inf') # if unconnected points are not even, the problem is unsolvable
    
        # Compute the sum of the Manhattan distances between all pairs of unconnected points
        h = sum(manhattan_distance(e, d) for e in unconnected for d in unconnected)
        return h
        
    def manhattan_distance(p1, p2):
        # Compute the Manhattan distance between two points
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    def load(path):
        with open(path, 'r') as f:
            lines = f.readlines()
            
        state = State.from_string(''.join(lines))
        return SoftFlow(state)



###############
# State class #
###############

class State:

    def __init__(self, grid):
        self.nbr = len(grid)
        self.nbc = len(grid[0])
        self.grid = grid
        self.segments = [] #do we even need to instanciate it ?
        
    def __str__(self):
        return '\n'.join(''.join(row) for row in self.grid)

    def __eq__(self, other_state):
        pass

    def __hash__(self):
        pass
    
    def __lt__(self, other):
        return hash(self) < hash(other)

    def from_string(string):
        lines = string.strip().splitlines()
        return State(list(
            map(lambda x: list(x.strip()), lines)
        ))
    
    # check wehther a semgnet between 2 points is a valid one or not
    # considered valid if:
    # 1. It connects 2 empty cells in the grid
    # 2. It does not intersect any of the previously placed segments.
    def is_valid_segment(self, p1, p2):
        # Check if points p1 and p2 are empty cells
        if self.grid[p1[0]][p1[1]] != ' ' or self.grid[p2[0]][p2[1]] != ' ':
            return False

        # Check if the segment intersects any of the previously placed segments
        new_segment = Segment(p1, p2)
        for segment in self.segments:
            if new_segment.intersects(segment):
                return False

        return True

class Segment:
    def __init__(self, entry, desktop):
        self.entry = entry
        self.desktop = desktop

    def intersects(self, other):
        # checks if this segment intersects with another segment
        return lines_intersect(self.entry, self.desktop, other.entry, other.desktop)

def lines_intersect(p1, p2, q1, q2):
    # Check if the line segment between points p1 and p2 intersects with
    # the line segment between points q1 and q2.
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]
    dx2 = q2[0] - q1[0]
    dy2 = q2[1] - q1[1]
    delta = dx1*dy2 - dy1*dx2
    if delta == 0:
        return False
    s = (dx2*(q1[1]-p1[1]) - dy2*(q1[0]-p1[0])) / delta
    t = (dx1*(q1[1]-p1[1]) - dy1*(q1[0]-p1[0])) / delta
    return 0 <= s <= 1 and 0 <= t <= 1


#####################
# Launch the search #
#####################

problem = SoftFlow.load(sys.argv[1])

node = astar_search(problem)

# example of print
path = node.path()

print('Number of moves: ', str(node.depth))
for n in path:
    print(n.state)  # assuming that the _str_ function of state outputs the correct format
    print()

