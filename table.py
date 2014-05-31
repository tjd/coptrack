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

# possible contents for cells
cell_values = ['empty', 'robber', 'wall'] 
# if multiple cops are allowed:
# cell_values = ['empty', 'cop', 'robber', 'wall']

directions = 'NSWE'
# if an agent can pass its move and stay in the same cell, then:
# directions = 'NSWEP'

# Returns a list of all (N, S, E, W) 4-tuples of values. The order of the
# values in the tuples matters, i.e. the first value is N, the second is S,
# the third is E, and fourth is W.
def make_allping_table(values):
    return [t for t in product(values, repeat=4)]

# Returns a movement dictionary of ((N, S, E, W), dir_to_move) pairs. The
# dir_to_move value is chosen at random from directions. Thus, a move might
# try to move into a wall.
def make_rand_movement_table():
    apt = make_allping_table(cell_values)
    rand_dir = random.choice(directions)
    return {t:rand_dir for t in apt}

if __name__ == '__main__':    
    rmt = make_rand_movement_table()
    print rmt
    print rmt[('empty', 'empty', 'robber', 'wall')]
    print len(rmt) # 81 for 3 cell values
