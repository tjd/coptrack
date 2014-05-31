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
    all_values = (empty, cop, wall)
    to_char = {empty:'.', robber:'R', cop:'C', wall:'W'}
    # add robber if multiple robbers allowed

directions = 'NSWE'
# if an agent can pass its move and stay in the same cell, then:
# directions = 'NSWEP'

# Returns a list of all (N, S, E, W) 4-tuples of values. The order of the
# values in the tuples matters, i.e. the first value is N, the second is S,
# the third is E, and fourth is W.
def make_allping_table(values):
    return [t for t in product(values, repeat=4)]

# Returns a movement dictionary of (N, S, E, W):dir_to_move pairs. The
# dir_to_move value is chosen at random from directions, and makes sure
# that it will not move into a wall.
def make_rand_movement_table():
    apt = make_allping_table(Cell.all_values)
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

# Returns a grid with r rows and c cols and all cells initially empty.
def make_grid(r, c):
    return [c * [Cell.empty] for i in xrange(r)]

def draw_grid(grid):
    for row in grid:
        for c in row:
            print Cell.to_char[c] + ' ',
        print

# Return a dictionary of the contents of the cells NSWE cells of grid[r][c].
def ping(r, c, grid):
    return (
        Cell.wall if r == 0                else grid[r-1][c],
        Cell.wall if r == len(grid) - 1    else grid[r+1][c],
        Cell.wall if c == len(grid[0]) - 1 else grid[r][c+1],
        Cell.wall if c == 0                else grid[r][c-1],
    )
    # return {
    #     'N' : Cell.wall if r == 0                else grid[r-1][c],
    #     'S' : Cell.wall if r == len(grid) - 1    else grid[r+1][c],
    #     'E' : Cell.wall if c == len(grid[0]) - 1 else grid[r][c+1],
    #     'W' : Cell.wall if c == 0                else grid[r][c-1],
    # }

def test_moving():
    grid = make_grid(5, 5)
    grid[0][0] = Cell.cop
    grid[4][4] = Cell.robber

    R = make_rand_movement_table()
    print R
    
    draw_grid(grid)
    p = ping(4, 4, grid)
    print p
    move = R[p]
    print move

if __name__ == '__main__':    
    test_moving()
    # rmt = make_rand_movement_table()
    # print rmt
    # print rmt[(Cell.empty, Cell.empty, Cell.cop, Cell.wall)]
    # print
    # print len(rmt) # 81 for 3 cell values

    # grid = make_grid(5, 5)
    # draw_grid(grid)
    # print ping(0, 0, grid)
    # print ping(1, 1, grid)

    # grid[0][0] = (Cell.cop)
    # grid[4][4] = (Cell.robber)
    # draw_grid(grid)
    # print ping(0, 1, grid)
    # print ping(4, 3, grid)
