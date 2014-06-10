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
# X allow for imperfect sensors (?)
# - allow for agent being given a map of the world at the start (?)
# - Implement Manhattan distance Pings and Moves (greater than 1)
# - consider: break agents, ngrams, grid, into separate files?

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
        return {(0,0):'C', (-1,0):'N', (1,0):'S', (0,1):'E', (0,-1):'W'}[d]
    except KeyError:
        return d

def dir_to_vector(d):
    """
    Return the unit vector relating to a given direction.
    """
    try:
        return {'C':(0,0), 'N':(-1,0), 'S':(1,0), 'E':(0,1), 'W':(0,-1)}[d]
    except KeyError:
        return d

def tuple_add(a, b):
    return tuple(map(sum,zip(a,b)))

class Entity_type(object):
    """
    Enumerated type for the contents of cells.
    """
    empty = 0
    robber = 1
    cop = 2
    wall = 3
    all_values = (empty, cop, wall) # add robber if multiple robbers allowed
    to_char = {empty:'.', robber:'R', cop:'C', wall:'W'}


class Entity(object):
    """
    The most basic class which may appear on a grid.
    <type> defines the role of the entity in the simulation.
    """
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        """
        Alter the string returned when this class is printed.
        Returns the Entity <type> instead of default behavior..
        """
        return Entity_type.to_char[self.type]



class Agent(Entity):
    def __init__(self, type, name, see_dist = 1, move_dist = 1):
        super(Agent, self).__init__(type)
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


class OrderedAgent(Agent):
    """
    Moves according to a fixed array of directions.
    Moves in the first direction in the array unless that move is not possible.
    Never moves in the opposite direction of the last recorded move.
    """
    def __init__(self, type, name, dirs = list('NSEW')):
        super(OrderedAgent, self).__init__(type, name)
        self.dirs = dirs

    def update(self, ping_value):
        for d in self.dirs:
            walls = [x for x in ping_value[d] if x.type == Entity_type.wall]
            if not walls and d != opposite_dir(self.last_move()):
                return d
        assert False, 'no move'


class StalkerAgent(Agent):
    """
    Follows the first instance of an Entity_type that it sees.
    """
    def __init__(self, type, name, target_type):
        super(StalkerAgent, self).__init__(type, name)
        self.target_type = target_type
        self.target = None

    def update(self, ping_value):
        move = 'C'

        for d, cell in ping_value.iteritems():
            # If there is no target yet:
            if self.target == None:
                # List the entities in <cell> which match <self.target_type>
                potentialt = [t for t in cell if t.type == self.target_type]
                # If there is anything in <potentialt>
                if potentialt:
                    # Use the first thing as our new target
                    self.target = potentialt[0]
            # Move towards the cell containing <target>:
            if self.target in cell:
                move = d

        return move



class Map(object):
    """
    Represents a 2D-map with a matrix of cells.
    Each cell can contain multiple objects.
    Agents can traverse adjacent cells.
    Agents cannot enter cells which contain a wall.
    """
    def __init__(self, r, c):
        self.rows, self.cols = r, c
        self.grid = []
        self.buffergrid = []
        # internal representation of the grid used to track all agents and
        # objects in the world
        for i in xrange(self.rows):
            self.grid.append([])
            for j in xrange(self.cols):
                self.grid[i].append([])
        
        # list of agents on this grid
        self.agents = []

    def draw(self, grid):
        for row in grid:
            for c in row:
                print c, '\t',
            print

    def copy_grid(self, grid):
        duplicate = []

        # Create an independent copy of <grid>:
        # For each row in <grid>:
        for r in xrange(len(self.grid)):
            # Add an empty row to <duplicate>.
            duplicate.append([])

            # For each cell in the <grid>'s row:
            for c in xrange(len(self.grid[r])):
                # Create a copy of <grid>'s cell and add it to <copygrid>'s row.
                duplicate[r].append(copy.copy(self.grid[r][c]) )

        return duplicate

    def remove_agent(self, grid, agent):
        """
        Remove <agent> from all cells in the grid.
        Does not affect other cell contents.
        """
        for row in grid:
            for cell in row:
                if agent in cell:
                    cell.remove(agent)

    def set_empty(self, grid, (r, c)):
        """
        Removes all of cell (r,c)'s contents.
        """
        grid[r][c] = []

    def set_agent(self, grid, agent, (r, c)):
        """
        Add <agent> to the grid cell at (r,c).
        """
        # Ensure the agent is not duplicated on the grid by removing all
        # other instances.
        self.remove_agent(grid, agent)
        grid[r][c].append(agent)

    def add_agent(self, agent):
        """
        Add an agent to the list of agents managed by this grid.
        Does not add the agent to a cell.
        """
        self.agents.append(agent)

    def ping(self, grid, (r, c)):
        """
        Return an NSEWC tuple of the contents of the cells neighboring
        grid[r][c], and grid[r][c] itself.
        """
        return {
            'N':[Entity(Entity_type.wall)] if r == 0     else grid[r-1][c],
            'S':[Entity(Entity_type.wall)] if r == self.rows - 1 else grid[r+1][c],
            'E':[Entity(Entity_type.wall)] if c == self.cols - 1 else grid[r][c+1],
            'W':[Entity(Entity_type.wall)] if c == 0     else grid[r][c-1],
            'C':grid[r][c],
        }

    def fuzzy_ping(self, grid, (r, c), errorprob):
        """
        Return an NSEWC tuple of the contents of the cells neighboring
        grid[r][c], and grid[r][c] itself.
        Returned data may be inaccurate.
        Each returned cell has a probability of <errorprob> to be randomized.
        Randomized cells may contain a wall or nothing.
        """
        # Start from a real ping.
        fuzzyping = self.ping(grid, (r,c))

        # All of the following effects only <fuzzyping>; not the real grid.
        for cell in fuzzyping.keys():
            # With a probability of <errorprob>: scramble the contents of a cell
            # in <fuzzyping>.
            if random.random() <= errorprob:
                # Scramble the cells by replacing them with a wall or nothing.
                # This replaces any agents which may have previously appeared
                # in a cell.
                fuzzyping[cell] = [Entity(Entity_type.wall)] if random.random() <= .5 else []
        return fuzzyping

    def location_of(self, grid, agent):
        """
        Return the X,Y coordinate of <agent>'s current cell on the grid.
        """
        # Iterate through the cells in each row and return the first cell
        # containing <agent>
        for row in grid:
            for cell in row:
                if agent in cell:
                    return grid.index(row), row.index(cell)

    def valid_move(self, grid, agent, (r, c)):
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
            if 'w' in grid[r][c]:
                validmove = False

        return validmove

    def move_agent(self, grid, agent, direction, destination):
        """
        Move the agent from the its current cell to the cell at <destination>.
        Record the move in the agent's log.
        """
        # Remove the agent from all cells containing a reference to it.
        self.remove_agent(grid, agent)
        # Add the agent to the destination cell.
        self.set_agent(grid, agent, destination)

        if direction == None: direction = 'C'
        # Record the direction moved in the agent's log.
        # TODO: The agent might move from (0,0) to (1,0) (a Southward move) 
        #       while the passed direction is 'N'.
        agent.log.append(direction)

    def update(self):
        """
        Update each agent and perform the returned action if it is valid.
        """
        self.buffergrid = self.copy_grid(self.grid)
        # To maintain simultaneous turn-taking:
        # All write-actions are applied to <buffergrid>
        # All read-actions are retrieved from <grid>
        for agent in self.agents:
            agentloc = self.location_of(self.grid, agent)
            # Ping the location of the agent to discover the contents
            # of surrounding cells.
            pingvalue = self.ping(self.grid, agentloc)

            # Query the agent on its proposed next action.
            proposedmove = agent.update(pingvalue)
            
            if dir_to_vector(proposedmove) != None:
                # Record the destination the agent would move to.
                destination = tuple_add(agentloc, dir_to_vector(proposedmove))
            else:
                destination = agentloc

            # If the requested move is physically valid:
            if self.valid_move(self.grid, agent, destination):
                self.move_agent(self.buffergrid, agent, proposedmove, destination)
            # don't do the invalid move (i.e. stay in same cell?):
            else:
                print 'Agent %s attempted illegal move %s to %s.' % (agent.name, 
                agentloc, destination)
                # Ensure the agent's log is updated...
                # TODO: Consider: handle this differently eg: agent damaged etc.
                self.move_agent(self.buffergrid, agent, 'C', agentloc)

        print 'Actual grid: '
        self.draw(self.grid)
        print 'Buffered grid: '
        self.draw(self.buffergrid)
        # Apply the updated by replacing the current grid with the buffer.
        self.grid = copy.copy(self.buffergrid)


def ngrams(seq, n):
    """
    Count the ngram totals in <seq>
    Each unique sequence of n characters has its own count.
    The sequences and counts are placed in a dictionary (<seq>:<count>).
    """
    result = {}
    for i in xrange(n-1, len(seq)):
        # t = tuple(seq[j] for j in xrange(i - n + 1, i + 1))
        t = tuple(seq[i + 1 - n : i + 1])
        if t in result:
            result[t] += 1
        else:
            result[t] = 1
    return result

def cummulative_ngrams(l, n):
    """
    Count the cummulative ngram totals for a list of sequences.
    <l> is a list of character sequences.
    The ngram count of each sequence is compiled in a single result dictionary.
    """
    result = {}
    for i in l:
        # Count the ngram totals for the single sequence <i>.
        rtotal = ngrams(i, n)

        # Add the data from <i> into our cumulative result dictionary:
        for key, value in rtotal.iteritems():
            # If this ngram exists in our results already, add the occurrences
            # recorded in <i> to our cumulative result:
            if key in result.keys():
                result[key] += value
            # Else this ngram has not occurred yet, create a new entry in our
            # cumulative result.
            else:
                result[key] = value
    return result

def compute_model_n(corpus, n):
    """
    Computes a basic ngram model given a corpus and n.
    <corpus> represents an ngram count dictionary of the form d[ngram]:count.
    Computes the max-likelihood-estimate of the nth character given we know the 
    n-1 preceding characters for every sequence in the corpus.
    """
    ngram_model = {}
    # Get the number of occurrences of sequences with length n-1
    prefix = cummulative_ngrams(corpus, n-1)
    # Get the number of occurrences of sequences with length n
    whole = cummulative_ngrams(corpus, n)
    # e.g. if n = 3 <whole> might contain an entry for 'abc' implying 
    # <prefix> contains entries for 'ab' and 'bc'

    for phrase in whole.keys():
        # e.g. when n = 3: 
        # Pr(abc)  =  Pr(c|ab)  =  count(abc) / count(ab)
        # below: whole[phrase] = count(phrase)
        prob = whole[phrase] / float(prefix[phrase[:-1]])
        ngram_model[phrase] = prob
    return ngram_model

def print_sorted_ngrams(ngrams):
    lst = [(ngrams[ng], ng) for ng in ngrams]
    lst.sort()
    lst.reverse()
    for count, ng in lst:
        print '%s %s' % (''.join(ng), count)

def simulate():
    print 'Empty Grid...\n'
    world = Map(5, 5)
    world.draw(world.grid)

    print '\nAdding Agents...\n'
    a = OrderedAgent(Entity_type.robber, 'a1')
    b = StalkerAgent(Entity_type.cop, 'b1', Entity_type.robber)
    world.add_agent(a)
    world.add_agent(b)
    world.set_agent(world.grid, a, (1,2))
    world.set_agent(world.grid, b, (4,4))
    world.draw(world.grid)


    for i in xrange(9):
        print '\nUpdating... %s\n' % (i)
        world.update()
        print 'update finished: '
        world.draw(world.grid)


def test():
    print 'Empty Grid...\n'
    world = Map(5, 5)
    world.draw(world.grid)

    print '\nAdding Agents...\n'
    a = OrderedAgent(Entity_type.robber, 'a1')
    b = StalkerAgent(Entity_type.cop, 'b1', Entity_type.robber)
    world.add_agent(a)
    world.add_agent(b)
    world.set_agent(world.grid, a, (1,2))
    world.set_agent(world.grid, b, (4,4))
    world.draw(world.grid)


    for i in xrange(100):
        print '\nUpdating... %s\n' % (i)
        world.update()
        world.draw(world.grid)

    for agent in world.agents:
        print agent.log
        print print_sorted_ngrams(ngrams(agent.log, 3))

    loc = (0,1)
    print '\nA ping at %s' % (loc,)
    print world.ping(world.grid, loc)

    print '\nA fuzzy ping at %s' % (loc,)
    print world.fuzzy_ping(world.grid, loc, .5)


    print '\nThe real grid remains:\n'
    world.draw(world.grid)

if __name__ == '__main__':    
    simulate()
