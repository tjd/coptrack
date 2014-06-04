# coptrack.py

from itertools import product
import random

#
# A cop C and robber R move around a graph. They start at random cells (?) and
# then alternate taking turns, with R moving first (or C?).
#
# In the case with only one C and one R, both C and R are limited to knowing
# the contents of their current cell (i.e. the one they are on), and the 4
# orthogonally adjacent cells (north, south, east, and west). They cannot
# "see" past these cells, although they can, of course, store the results of
# any of their sensing actions.
#
# The things that can be sensed are an empty cell, a wall (i.e a non-empty
# cell), a robber, and a cop.
#
# R is assumed to be following a set of movement rules. There is no set
# limitation to the rules R might be following. R could even be controlled by
# a human player.
#
# C's goal is to figure out R's rules, or an approximation thereof. C could
# prove it knows R's rules by predicting R's next move for a long sequence.
#
# The challenge is to come up with an algorithm that C can use to efficiently
# determine R's movement pattern.
# 
# A key detail here is that the cop moves around the grid at the same time the
# robber does, and R's movements can be influenced by C. Possibly, C could
# somehow use this fact to its advantage.
#

#
# TODO (roughly in order of priority):
# - allow cells to contain multiple objects
# - moves should be simultaneous (as in economic game theory)
# - 'pass' is a legal move, i.e. not moving at all
# - Grid stores a list of agents each with an "update" function that 
#   it calls on each "turn"/"frame" of the simulation
# - Grid keeps track of the locations of all the agents; the agents
#   themselves don't necessarily know where they are
# - sensor readings should include what's in the current cell 
# - above description in comments of the problem needs to be changed
#
# (lower priority)
# - allow for imperfect sensors (?)
# - allow for agent being given a map of the world at the start (?)


def opposite_dir(d):
    try:
        return {'N':'S', 'S':'N', 'W':'E', 'E':'W'}[d]
    except KeyError:
        return d

# enumerated type for the contents of cells
class Cell_type(object):
    empty = 0
    robber = 1
    cop = 2
    wall = 3
    all_values = (empty, cop, wall) # add robber if multiple robbers allowed
    to_char = {empty:'.', robber:'R', cop:'C', wall:'W'}

class Agent(object):
    def __init__(self, name, see_dist = 1, move_dist = 1):
        self.name = name

        # see_dist is how many cells away the agent can see using the
        # Manhattan metric
        self.see_dist = see_dist

        # move_dist is the max number of moves an agent can make on its turn
        self.move_dist = move_dist

        # a record of all the moves the agent is made, in order from start to
        # end
        self.log = ['start']

    def last_move(self): return self.log[-1]

    # Abstract function to be implemented by the inheriting agent. The input
    # is a sensor ping showing the contents of the surrounding cells, and the
    # return value is the action the agent wants to make.
    #
    # The Grid is responsible for catching illegal moves, e.g. an agent might
    # decide to move into a wall, but the Grid will have to (somehow) disallow
    # that.
    def update(self, ping_value): pass


class Grid(object):
    def __init__(self, r, c):
        self.rows, self.cols = r, c

        # internal representation of the grid used to track all agents and
        # objects in the world
        self.grid = [self.cols * [[]] for i in xrange(self.rows)]
        
        # list of agents on this grid
        self.agents = []

    def draw(self):
        for row in self.grid:
            for c in row:
                print c,
            print

    # Return an NSEWC tuple of the contents of the cells neighboring
    # grid[r][c], and grid[r][c] itself.
    def ping(self, (r, c)):
        return {
          'N':self.grid[r-1][c],
          'S':self.grid[r+1][c],
          'E':self.grid[r][c+1],
          'W':self.grid[r][c-1],
          'C':self.grid[r][c],
        }

    # # Return an NSEW tuple of the contents of the cells neighboring
    # # grid[r][c].
    # def ping(self, (r, c)):
    #     return {
    #       'N':Cell_type.wall if r == 0                     else self.grid[r-1][c],
    #       'S':Cell_type.wall if r == len(self.grid) - 1    else self.grid[r+1][c],
    #       'E':Cell_type.wall if c == len(self.grid[0]) - 1 else self.grid[r][c+1],
    #       'W':Cell_type.wall if c == 0                     else self.grid[r][c-1],
    #     }


    def set_empty(self, (r, c)):
        self.grid[r][c] = []

    def set_agent(self, agent, (r, c)):
        self.agents.append(agent)
        self.grid[r][c].append(agent)

    def update(self):
        buffered_grid = copy_of(self.grid)
        # all changes below are to the buffered_grid
        for agent in self.agents:
            ping_value = ping(location_of(agent))
            proposed_moved = agent.update(ping_value)
            if physically_legal(proposed_move):
                # do the move:
                # remove agent from current location
                # move it to new location
            else:
                # don't do the move (i.e. stay in same cell?)
                
        grid = buffered_grid


    # # d is the direction to move: N, S, E, or W
    # def move_cop(self, d):
    #     r, c = self.cop.pos
    #     self.cop.log.append(d)
    #     self.grid[r][c] = Cell_type.empty
    #     if d == 'N':
    #         self.set_cop((r-1, c))
    #     elif d == 'S':
    #         self.set_cop((r+1, c))
    #     elif d == 'E':
    #         self.set_cop((r, c+1))
    #     elif d == 'W':
    #         self.set_cop((r, c-1))

    # # d is the direction to move: N, S, E, or W
    # def move_robber(self, d):
    #     r, c = self.robber.pos
    #     print 'd', d
    #     print '%s, %s' % (r, c)
    #     self.robber.log.append(d)
    #     self.grid[r][c] = Cell_type.empty
    #     if d == 'N':
    #         self.set_robber((r-1, c))
    #     elif d == 'S':
    #         self.set_robber((r+1, c))
    #     elif d == 'E':
    #         self.set_robber((r, c+1))
    #     elif d == 'W':
    #         self.set_robber((r, c-1))



# def ngrams(seq, n):
#     result = {}
#     for i in xrange(n-1, len(seq)):
#         # t = tuple(seq[j] for j in xrange(i - n + 1, i + 1))
#         t = tuple(seq[i + 1 - n : i + 1])
#         if t in result:
#             result[t] += 1
#         else:
#             result[t] = 1
#     return result

# def print_sorted_ngrams(ngrams):
#     lst = [(ngrams[ng], ng) for ng in ngrams]
#     lst.sort()
#     lst.reverse()
#     for count, ng in lst:
#         print '%s %s' % (''.join(ng), count)

# def test():
#     grid = Grid(5, 5)

#     # starting positions
#     grid.set_cop((3, 3))
#     grid.set_robber((4, 4))

#     # make 100 moves
#     for i in xrange(100):
#         grid.draw()
#         print 'i =', i

#         grid.do_robber_move()
#         print 'Robber moves %s\n' % grid.robber.last_move()

#     print grid.robber.log
#     print_sorted_ngrams(ngrams(grid.robber.log, 3))
#     print
#     print_sorted_ngrams(ngrams(grid.robber.log, 4))
#     print
#     print_sorted_ngrams(ngrams(grid.robber.log, 5))
#     print
#     print_sorted_ngrams(ngrams(grid.robber.log, 6))

def test():
    grid = Grid(5, 5)
    grid.draw()

if __name__ == '__main__':    
    test()
