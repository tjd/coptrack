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

def opposite_dir(d):
    if d not in 'NEWS':
        return d
    else:
        return {'N':'S', 'S':'N', 'W':'E', 'E':'W'}[d]

# contents for cells
class Cell(object):
    empty = 0
    robber = 1
    cop = 2
    wall = 3
    all_values = (empty, cop, wall) # add robber if multiple robbers allowed
    to_char = {empty:'.', robber:'R', cop:'C', wall:'W'}

class Agent(object):
    def __init__(self, name):
        self.name = name
        self.pos = None
        self.log = ['start']

    def last_move(self): return self.log[-1]
    def get_move(self, ping): pass

class RandomTableAgent(Agent):
    def __init__(self, name):
        super(RandomTableAgent, self).__init__(name)
        self.move_table = make_rand_movement_table()

    def get_move(self, ping):
        return self.move_table[ping]

class RandomOrderedAgent(Agent):
    def __init__(self, name):
        super(RandomOrderedAgent, self).__init__(name)
        self.dirs = list('NSEW')
        random.shuffle(self.dirs)

    # TODO: fix order
    def get_move(self, ping):
        for d in self.dirs:
            if ping[d] == Cell.empty and d != opposite_dir(self.last_move()):
                return d
        assert False, 'no move'

class Grid(object):
    def __init__(self, r, c):
        self.rows, self.cols = r, c
        self.grid = [self.cols * [Cell.empty] for i in xrange(self.rows)]
        self.cop = Agent('Cop')
        self.robber = RandomOrderedAgent('Robber')
        # self.robber = RandomTableAgent('Robber')

    def draw(self):
        for row in self.grid:
            for c in row:
                print Cell.to_char[c] + ' ',
            print

    # Return an NSEW tuple of the contents of the cells neighboring
    # grid[r][c].
    def ping(self, (r, c)):
        return {
          'N':Cell.wall if r == 0                     else self.grid[r-1][c],
          'S':Cell.wall if r == len(self.grid) - 1    else self.grid[r+1][c],
          'E':Cell.wall if c == len(self.grid[0]) - 1 else self.grid[r][c+1],
          'W':Cell.wall if c == 0                     else self.grid[r][c-1],
        }

    def ping_robber(self): return self.ping(self.robber.pos)
    def ping_cop(self): return self.ping(self.cop.pos)

    def set_empty(self, (r, c)):
        self.grid[r][c] = Cell.empty

    def set_cop(self, (r, c)):
        self.grid[r][c] = Cell.cop
        self.cop.pos = (r, c)

    def set_robber(self, (r, c)):
        self.grid[r][c] = Cell.robber
        self.robber.pos = (r, c)

    def do_cop_move(self):
        p = self.ping_cop()
        move = self.cop.get_move(p)
        self.move_cop(move)

    def do_robber_move(self):
        p = self.ping_robber()
        print 'ping', p
        move = self.robber.get_move(p)
        print 'move', move
        self.move_robber(move)

    # d is the direction to move: N, S, E, or W
    def move_cop(self, d):
        r, c = self.cop.pos
        self.cop.log.append(d)
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
        r, c = self.robber.pos
        print 'd', d
        print '%s, %s' % (r, c)
        self.robber.log.append(d)
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

def unigrams(seq):
    result = {}
    for x in seq:
        if x in result:
            result[x] += 1
        else:
            result[x] = 1
    return result

def bigrams(seq):
    result = {}
    for i in xrange(1, len(seq)):
        t = (seq[i-1], seq[i])
        if t in result:
            result[t] += 1
        else:
            result[t] = 1
    return result

def trigrams(seq):
    result = {}
    for i in xrange(2, len(seq)):
        t = (seq[i-2], seq[i-1], seq[i])
        if t in result:
            result[t] += 1
        else:
            result[t] = 1
    return result

def ngrams(seq, n):
    result = {}
    for i in xrange(n-1, len(seq)):
        t = tuple(seq[j] for j in xrange(i - n + 1, i + 1))
        if t in result:
            result[t] += 1
        else:
            result[t] = 1
    return result

def print_sorted_ngrams(ngrams):
    lst = [(ngrams[ng], ng) for ng in ngrams]
    lst.sort()
    lst.reverse()
    for count, ng in lst:
        print '%s %s' % (''.join(ng), count)

def test():
    grid = Grid(5, 5)

    # starting positions
    grid.set_cop((3, 3))
    grid.set_robber((4, 4))

    # make 100 moves
    for i in xrange(100):
        grid.draw()
        print 'i =', i

        grid.do_robber_move()
        print 'Robber moves %s\n' % grid.robber.last_move()

    print grid.robber.log
    # print unigrams(grid.robber.log)
    # print bigrams(grid.robber.log)
    # print trigrams(grid.robber.log)
    # print ngrams(grid.robber.log, 3)
    print_sorted_ngrams(ngrams(grid.robber.log, 3))
    print
    print_sorted_ngrams(ngrams(grid.robber.log, 4))
    print
    print_sorted_ngrams(ngrams(grid.robber.log, 5))
    print
    print_sorted_ngrams(ngrams(grid.robber.log, 6))

if __name__ == '__main__':    
    test()
