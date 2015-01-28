__author__ = 'Christian Cooper'

from datetime import datetime

def duration(start):
    delta = datetime.now() - start
    s = str(delta.seconds) + "."
    s += str(delta.microseconds)[0:3]
    s += "s"
    return s


def log_duration(msg, start):
    """Log the duration between the time given in start and the current time prefixed with the supplied message"""
    print "{} duration: {}".format(msg, duration(start))


class Coordinate(object):
    """
    Represents a single coordinate on the map
    """

    def __init__(self, x, y, h):
        """Build structure"""
        self.x = x
        self.y = y
        self.h = h
        self.exits = []

    def __str__(self):
        return "Coordinate(Pos: ({},{}), Alt.: {})".format(self.x, self.y, self.h)


class Ski(object):
    """
    Solves the problem of finding the longest downhill ski-run with the largest drop given a file with format defining
    a grid of altitudes like so:

    -------------------------------------------------------------------------------
    <max_x> <max_y>
    <value[0, 0]> <value[1, 0]> ... value[max_x-1, 0]>
    <value[0, 1]> <value[1, 1]> ... value[max_x-1, 1]>
      ...
    <value[0, max_y-2]> <value[1, max_y-2]> ... value[max_x-1, max_y-2]>
    <value[0, max_y-1]> <value[1, max_y-1]> ... value[max_x-1, max_y-1]>
    -------------------------------------------------------------------------------
    """

    def __init__(self, data_file_name):
        # Data structures
        self.max_x, self.max_y = None, None
        self.slope = []
        self.local_maxima = []

        print "Loading data..."
        start = datetime.now()
        f = open(data_file_name)
        x = 0
        for line in f.readlines():
            if not self.max_x:
                # Process header
                self.max_x, self.max_y = map(int, line.split())
            else:
                # Build a coordinate for each value on the line
                row = []
                y = 0
                self.slope.append(row)
                for h in line.split():
                    row.append(Coordinate(x, y, int(h)))
                    y += 1
                x += 1
        f.close()
        print "  Map extents X:[0..{}], Y:[0..{}]".format(self.max_x - 1, self.max_y - 1)
        log_duration("Load", start)

    def structure_data(self):
        """
        Build a directed graph of coordinates and identify all local maxima
        """
        print "Structuring data..."
        start = datetime.now()

        max_x = self.max_x - 1
        max_y = self.max_y - 1
        for x in range(self.max_x):
            for y in range(self.max_y):
                current_coordinate = self.slope[x][y]
                local_max_h = current_coordinate.h

                # Identify downhill North slope
                if x > 0:
                    neighbour = self.slope[x - 1][y]
                    if neighbour.h < current_coordinate.h:
                        current_coordinate.exits.append(neighbour)
                    local_max_h = max(local_max_h, neighbour.h)

                # Identify downhill East slope
                if y < max_y:
                    neighbour = self.slope[x][y + 1]
                    if neighbour.h < current_coordinate.h:
                        current_coordinate.exits.append(neighbour)
                    local_max_h = max(local_max_h, neighbour.h)

                # Identify downhill South slope
                if x < max_x:
                    neighbour = self.slope[x + 1][y]
                    if neighbour.h < current_coordinate.h:
                        current_coordinate.exits.append(neighbour)
                    local_max_h = max(local_max_h, neighbour.h)

                # Identify downhill West slope
                if y > 0:
                    neighbour = self.slope[x][y - 1]
                    if neighbour.h < current_coordinate.h:
                        current_coordinate.exits.append(neighbour)
                    local_max_h = max(local_max_h, neighbour.h)

                # Record if local maximum
                if local_max_h == current_coordinate.h:
                    self.local_maxima.append(current_coordinate)

        print "  Local maxima found: {}".format(len(self.local_maxima))
        log_duration("Structuring", start)

    def find_longest(self):
        """
        From every local maxima do a breadth first navigation of all downhill runs to find longest run,
        tiebreak on longest drop when multiple longest runs exist

        :return: tuple(
            start coordinate,
            finish coordinate,
            length of run,
            distance of drop,
            cardinal compass points of route as String)
        """
        print "Finding longest route..."
        start_time = datetime.now()

        # Details of best route
        start = None
        finish = None
        max_length = 0
        max_drop = 0
        route = ""

        # Sort from the highest to the lowest
        self.local_maxima.sort(lambda c1, c2: c2.h - c1.h)
        log_duration("Sorted maxima (split)", start_time)

        # Start point must be a local maximum
        cell_counter = 0
        for start_cell in self.local_maxima:
            # Seed a new run starting from the current cell
            current_run = [(start_cell, 0)]
            next_run = []
            cell_counter += 1
            while True:
                # Do a breadth first traversal
                for next_cell, current_run_length in current_run:
                    for neighbour in next_cell.exits:
                        next_run.append((neighbour, current_run_length + 1))

                # See if all trail-ends are termini
                if len(next_run) == 0:
                    # Look for a run that beats the current best
                    for finish_cell, finish_run_length in current_run:
                        full_drop = start_cell.h - finish_cell.h

                        if finish_run_length > max_length or (finish_run_length == max_length and full_drop > max_drop):
                            # Found new best
                            start = start_cell
                            finish = finish_cell
                            max_length = finish_run_length
                            max_drop = full_drop
                            #print "  {} - Found new best: {} -> {}, run length: {}, run drop: {}".format(
                            #    duration(start_time), start, finish, max_length, max_drop)
                    # Move on to next highest local maximum
                    break
                else:
                    # Set up for next stage of breadth search
                    current_run = next_run
                    next_run = []

        log_duration("Finding longest", start_time)
        return start, finish, max_length, max_drop

if __name__ == "__main__":
    overall_start = datetime.now()

    # Map with known result
    # ski = Ski("simple_map.txt")

    ski = Ski("map.txt")
    ski.structure_data()
    b_start, b_finish, b_length, b_drop = ski.find_longest()

    b_nodes = b_length + 1
    print "Best route:"
    print "  Starts:   {}".format(b_start)
    print "  Finishes: {}".format(b_finish)
    print "  Nodes:    {}".format(b_nodes)
    print "  Length:   {}".format(b_length)
    print "  Drop:     {}".format(b_drop)
    print "Quiz email:"
    print "  {}{}@redmart.com".format(b_nodes, b_drop)
    log_duration("Full run", overall_start)

