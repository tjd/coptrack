from itertools import product
import random

#
# A cop C and robber R move around a graph. They start at random cells (?) and
# then alternate taking turns, with R moving first (or C?).
#
# On each turn, the agent whose turn it is moves into one of the four adjacent
# non-wall cells. These adjacent cells are referred to as N, S, E, and W. If
# it tries to move into a wall cell, then nothing happens and it stays where
# it is.
#
# C is casing R, i.e. following R and trying to determine its movement
# pattern. R's moves are specified by a movement table, which is a table of
# possible 4-tuples of sensors readings around a cell. One move is given for
# each possible 4-tuple, and so R makes a move by look-up the corresponding
# move for the sensor 4-tuple. 
#
# One C believes it has determine R's movement table, it can stop announce
# the movement table. 
# 

# contents for cells
class Cell(object):
    empty = 0
    robber = 1
    cop = 2
    wall = 3
    all_values = (empty, cop, wall) # add robber if multiple robbers allowed
    to_char = {empty:'.', robber:'R', cop:'C', wall:'W'}

class Grid(object):
    def __init__(self, r, c):
        self.rows, self.cols = r, c
        self.grid = [self.cols * [Cell.empty] for i in xrange(self.rows)]
        self.cop_pos = None
        self.cop_log = []
        self.robber_pos = None
        self.robber_log = []

    def draw(self):
        for row in self.grid:
            for c in row:
                print Cell.to_char[c] + ' ',
            print

    # Return an NSEW tuple of the contents of the cells neighboring
    # grid[r][c].
    def ping(self, (r, c)):
        return (
            Cell.wall if r == 0                     else self.grid[r-1][c], # N
            Cell.wall if r == len(self.grid) - 1    else self.grid[r+1][c], # S
            Cell.wall if c == len(self.grid[0]) - 1 else self.grid[r][c+1], # E
            Cell.wall if c == 0                     else self.grid[r][c-1], # W
        )

    def ping_robber(self): return self.ping(self.robber_pos)
    def ping_cop(self): return self.ping(self.cop_pos)

    def set_empty(self, (r, c)):
        self.grid[r][c] = Cell.empty

    def set_cop(self, (r, c)):
        self.grid[r][c] = Cell.cop
        self.cop_pos = (r, c)

    def set_robber(self, (r, c)):
        self.grid[r][c] = Cell.robber
        self.robber_pos = (r, c)

    # d is the direction to move: N, S, E, or W
    def move_cop(self, d):
        r, c = self.cop_pos
        self.cop_log.append(d)
        self.grid[r][c] = Cell.empty
        if d == 'N':
            self.set_cop((r-1, c))
        elif d == 'S':
            self.set_cop((r+1, c))
        elif d == 'E':
            self.set_cop((r, c+1))
        elif d == 'W':
            self.set_cop((r, c-1))

    # d is the direction to move: N, S, E, or W
    def move_robber(self, d):
        r, c = self.robber_pos
        self.robber_log.append(d)
        self.grid[r][c] = Cell.empty
        if d == 'N':
            self.set_robber((r-1, c))
        elif d == 'S':
            self.set_robber((r+1, c))
        elif d == 'E':
            self.set_robber((r, c+1))
        elif d == 'W':
            self.set_robber((r, c-1))


# Returns a movement dictionary of (N, S, E, W):dir_to_move pairs. The
# dir_to_move value is chosen at random from directions, and makes sure that
# it will not move into a wall.
def make_rand_movement_table():
    # apt is a list of all (N, S, E, W) 4-tuples of values. The order of the
    # values in the tuples matters, i.e. the first value is N, the second is
    # S, the third is E, and fourth is W.
    apt = [t for t in product(Cell.all_values, repeat=4)]
    result = {}
    for n, s, e, w in apt:
        directions = []
        if n != Cell.wall: directions.append('N')
        if s != Cell.wall: directions.append('S')
        if e != Cell.wall: directions.append('E')
        if w != Cell.wall: directions.append('W')
        rand_dir = () if directions == [] else random.choice(directions)
        result[(n, s, e, w)] = rand_dir
    return result

def test_moving():
    grid = Grid(5, 5)

    # starting positions
    grid.set_cop((0, 0))
    grid.set_robber((4, 4))

    # create a random movement table for the robber
    move_table = make_rand_movement_table()
    
    # print move_table
    grid.draw()
    
    p = grid.ping_robber()
    print p
    move = move_table[p]
    print 'Robber moves', move
    print
    grid.move_robber(move)

    grid.draw()
    print grid.robber_pos


if __name__ == '__main__':    
    test_moving()
