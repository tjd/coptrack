# coptrack.py

from itertools import product
import random, copy

#
# A cop C and robber R move around a graph. They start at random cells (?) and
# then alternate taking turns, with R moving first (or C?).
#
# A cell may contain any number of agents or a cell may contain a single wall.
#
# Let any cop, robber or similar AI entity be an 'agent'.
#
# Agents cannot enter or cross over a cell containing a wall. However, any
# number of agents may simultaneously occupy, enter, exit or cross a cell which
# does not contain a wall.
#
# Agents may be given a map before the start of the first turn. The map may 
# accurately represent the graph which the agent is on, or it may be incorrect.
#
# Agents are limited to sensing the contents of their current cell (i.e. the one
# they are on), and the contents of any cell within a Manhattan distance of x 
# (where x depends upon the particular agent) from their current cell. They
# cannot "see" past these cells, although they can, of course, store the results 
# of any of their sensing actions.
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
# X allow cells to contain multiple objects
# X moves should be simultaneous (as in economic game theory)
# X 'pass' is a legal move, i.e. not moving at all
# X Grid stores a list of agents each with an "update" function that 
#   it calls on each "turn"/"frame" of the simulation
# X Grid keeps track of the locations of all the agents; the agents
#   themselves don't necessarily know where they are
# X sensor readings should include what's in the current cell 
# X above description in comments of the problem needs to be changed
#
# (lower priority)
# - allow for imperfect sensors (?)
# - allow for agent being given a map of the world at the start (?)

def opposite_dir(d):
    """
    Return the cardinal direction opposite to <d>.
    """
    try:
        return {'N':'S', 'S':'N', 'W':'E', 'E':'W'}[d]
    except KeyError:
        return d

# TODO: Is this duplication foolish? Replace both following methods with a
# single solution?
def vector_to_dir(d):
    """
    Return the direction relating to a given unit vector.
    """
    try:
        return {(0,0):'P', (-1,0):'N', (1,0):'S', (0,1):'E', (0,-1):'W'}[d]
    except KeyError:
        return d

def dir_to_vector(d):
    """
    Return the unit vector relating to a given direction.
    """
    try:
        return {'P':(0,0), 'N':(-1,0), 'S':(1,0), 'E':(0,1), 'W':(0,-1)}[d]
    except KeyError:
        return d

def tuple_add(a, b):
    return tuple(map(sum,zip(a,b)))

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


    def __repr__(self):
        """
        Alter the string returned when this class is printed.
        Returns the Agent's <name> instead of default behavior..
        """
        return self.name

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
    """
    Represents a 2D-map with a matrix of cells.
    Each cell can contain multiple objects.
    Agents can traverse adjacent cells.
    Agents cannot enter cells which contain a wall.
    """
    def __init__(self, r, c):
        self.rows, self.cols = r, c
        self.grid = []
        # internal representation of the grid used to track all agents and
        # objects in the world
        for i in xrange(self.rows):
            self.grid.append([])
            for j in xrange(self.cols):
                self.grid[i].append([])
        
        # list of agents on this grid
        self.agents = []

    def draw(self):
        for row in self.grid:
            for c in row:
                print c, '\t',
            print

    def remove_agent(self, agent):
        """
        Remove <agent> from all cells in the grid.
        Does not affect other cell contents.
        """
        for row in self.grid:
            for cell in row:
                if agent in cell:
                    cell.remove(agent)

    def set_empty(self, (r, c)):
        """
        Removes all of cell (r,c)'s contents.
        """
        self.grid[r][c] = []

    def set_agent(self, agent, (r, c)):
        """
        Add <agent> to the grid cell at (r,c).
        """
        # Ensure the agent is not duplicated on the grid by removing all
        # other instances.
        self.remove_agent(agent)
        self.grid[r][c].append(agent)

    def add_agent(self, agent):
        """
        Add an agent to the list of agents managed by this grid.
        Does not add the agent to a cell.
        """
        self.agents.append(agent)

    def ping(self, (r, c)):
        """
        Return an NSEWC tuple of the contents of the cells neighboring
        grid[r][c], and grid[r][c] itself.
        """
        return {
            'N':'wall' if r == 0                        else self.grid[r-1][c],
            'S':'wall' if r == self.rows - 1            else self.grid[r+1][c],
            'E':'wall' if c == self.cols - 1            else self.grid[r][c+1],
            'W':'wall' if c == 0                        else self.grid[r][c-1],
            'C':self.grid[r][c],
        }

    def location_of(self, agent):
        """
        Return the X,Y coordinate of <agent>'s current cell on the grid.
        """
        # Iterate through the cells in each row and return the first cell
        # containing <agent>
        for row in self.grid:
            for cell in row:
                if agent in cell:
                    return self.grid.index(row), row.index(cell)

    def valid_move(self, agent, (r, c)):
        """
        Is the proposed destination (r,c) possible for <agent> to enter?
        Returns false if (r,c) is a cell with a wall.
        Returns false if (r,c) is outside the grid.
        """
        validmove = True

        # If the move lands outside the grid boundary it is false.
        if r >= self.rows or c >= self.cols:
            validmove = False
        else:
            # If the move lands in a cell containing a wall it is false.
            if 'w' in self.grid[r][c]:
                validmove = False

        return validmove

    def move_agent(self, agent, direction, destination):
        """
        Move the agent from the its current cell to the cell at <destination>.
        Record the move in the agent's log.
        """
        # Remove the agent from all cells containing a reference to it.
        self.remove_agent(agent)
        # Add the agent to the destination cell.
        self.set_agent(agent, destination)
        # Record the direction moved in the agent's log.
        # TODO: The agent might move from (0,0) to (1,0) (a Southward move) 
        #       while the passed direction is 'N'.
        agent.log.append(direction)

    def update(self):
        """
        Update each agent and perform the returned action if it is valid.
        """
        # TODO: Is shallow copy enough?
        buffered_grid = copy.copy(self.grid)
        # all changes below are to the buffered_grid
        for agent in self.agents:
            agentloc = self.location_of(agent)
            # Ping the location of the agent to discover the contents
            # of surrounding cells.
            pingvalue = self.ping(agentloc)

            # Query the agent on its proposed next action.
            proposedmove = agent.update(ping_value)

            # Record the destination the agent would move to.
            destination = tuple_add(agentloc, dir_to_vector(proposedmove))

            # If the requested move is physically valid:
            if self.valid_move(agent, destination):
                self.move_agent(agent, proposedmove, destination)
            # don't do the invalid move (i.e. stay in same cell?):
            else:
                print 'Agent %s attempted illegal move %s to %s.' % (agent.name, 
                agentloc, destination)
                # Ensure the agent's log is updated...
                # TODO: Consider: handle this differently eg: agent damaged etc.
                self.move_agent(agent, 'R', agentloc)
        # Apply the updated by replacing the current grid with the buffer.
        self.grid = buffered_grid

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
    print

    a = Agent('a1')
    b = Agent('b1')
    grid.add_agent(a)
    grid.add_agent(b)
    grid.set_agent(a, (1,2))
    grid.set_agent(b, (4,4))
    grid.draw()
    print 
    grid.update()
    grid.draw()


if __name__ == '__main__':    
    test()
