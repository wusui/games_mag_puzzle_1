#!/usr/bin/python
"""
Create a map of nodes and links and then solve the puzzle.
"""
import scan_exp


class Mnode:
    """
    The basic data unit for the solving of this puzzle.

    Each Mnode represents one of the figures (A circle or square) in the
    puzzle.  An Mnode has its own name (text form of the coordinates of
    the figure (0,0 is upper left), an indicator whether or not it
    is a square or cricle, a pattern representing the original puzzle
    number (or ?), a list of possible solutions, and a list of pointers
    to adjoining Mnodes.

    This also keeps track of found values, rearranges links at the start
    to handle the (5,2,5) square inconsistency in the Summer of 2018 puzzle,
    and a list of most recently modified Mnodes.
    """
    answers = []
    solved_movies = []
    solved_actors = []
    fixed_links = []
    last_mod = []

    def __init__(self, instring, movies, verbosity):
        self.verbose = verbosity
        parts = instring.split('|')
        self.odd = False
        self.name = parts[1]
        self.type = parts[0]
        self.pattern = parts[2]
        self.possible = []
        self.linked_nodes = []
        if parts[2] == '?':
            return
        if self.type == 'S':
            for pos_ans in movies[self.pattern]:
                self.possible.append(pos_ans)
            if len(self.possible) == 1:
                self.display_progress()
                self.solved_movies.append(self.possible[0][0])

    def get_associated(self):
        """
        Find associations.

        Return a list of associated entries.  For an actor, this would
        be movies that that person appeared in.  For a movie, it would
        be the cast.
        """
        ret_list = []
        for entry in self.possible:
            if self.type == 'S':
                alist = scan_exp.get_actor_from_movie(entry[1])
            else:
                alist = scan_exp.get_movie_from_actor(entry[1])
            ret_list = ret_list + alist
        return ret_list

    def display_progress(self):
        """
        Helpful user message.

        When a new entry in the puzzle is found, display it.  This is mostly
        useful to display progress information to the user during the
        second part of the program (the second big delay section).
        """
        if self.verbose:
            print('"' + self.possible[0][0] +
                  '" has been placed in the puzzle')


def get_id(fline):
    """
    Given an input line, get the number/name of this Mnode.
    """
    parts = fline.split('|')
    return parts[1]


def link_nodes(ploc, movies, verbosity):
    """
    Set up the puzzle grid based on data input.

    Arguments:
       ploc -- file name of the original puzzle (puzzle.txt)
       movies -- movie information previously found
       verbosity -- print progress messages if true
    """
    m_nodes = {}
    with open(ploc, 'r+') as in_file:
        figures = in_file.read().split('\n')
    if not figures[-1]:
        figures = figures[0:-1]
    for figure in figures:
        cell_id = get_id(figure)
        m_nodes[cell_id] = Mnode(figure, movies, verbosity)
    for figure in figures:
        parts = figure.split('|')
        endpt1 = parts[1]
        if not parts[3]:
            continue
        for endpt2 in parts[3].split(':'):
            m_nodes[endpt1].linked_nodes.append(endpt2)
            m_nodes[endpt2].linked_nodes.append(endpt1)
    fix_odd_link(m_nodes)
    for key in m_nodes:
        if len(m_nodes[key].possible) == 1:
            m_nodes[key].last_mod.append(key)
    return m_nodes


def fix_odd_link(m_nodes):
    """
    Handle discrepancies in the links in the original puzzle

    Argument:
        m_node -- list of Mnodes used in the puzzle
    """
    odd_nodes = []
    first_node = False
    for s_node in m_nodes:
        scn_node = m_nodes[s_node]
        if not first_node:
            first_node = scn_node
        if len(scn_node.linked_nodes) == 1:
            scn_node.odd = True
            odd_nodes.append(scn_node)
    for scn_node1 in odd_nodes:
        if not scn_node1.odd:
            continue
        for scn_node2 in odd_nodes:
            if not scn_node2.odd:
                continue
            if scn_node1 == scn_node2:
                continue
            if scn_node1.type == scn_node2.type:
                if scn_node1.pattern == scn_node2.pattern:
                    first_node.fixed_links.append([scn_node1, scn_node2])
                    scn_node1.odd = False
                    scn_node2.odd = False
    for pair in first_node.fixed_links:
        last_link = pair[1].linked_nodes[0]
        end_link = m_nodes[last_link]
        end_link.linked_nodes.remove(pair[1].name)
        end_link.linked_nodes.append(pair[0].name)
        pair[0].linked_nodes.append(end_link.name)
