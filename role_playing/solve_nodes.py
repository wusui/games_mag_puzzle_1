#!/usr/bin/python
"""
Solve it
"""
import scan_exp


def solve_nodes(mnodes):
    """
    Solve the puzzle.

    Loop through all nodes that have changed.  Terminate when there are
    no nodes saved in the first in first out node list.  When this is
    empty all touched nodes have been processed.

    Arguments:
        mnodes -- list of Mnodes.
    """
    for dkey in mnodes:
        first_node = mnodes[dkey].name
        break
    while mnodes[first_node].last_mod:
        thisn = mnodes[first_node].last_mod[0]
        mnodes[first_node].last_mod = mnodes[first_node].last_mod[1:]
        for neighbor in mnodes[thisn].linked_nodes:
            if len(mnodes[neighbor].possible) == 1 or \
                     mnodes[neighbor].pattern == '?':
                continue
            match = []
            for my_sols in mnodes[thisn].possible:
                if mnodes[thisn].type == 'S':
                    alist = scan_exp.get_actor_from_movie(my_sols[1])
                else:
                    alist = scan_exp.get_movie_from_actor(my_sols[1])
                n_pattern = [int(i) for i in
                             mnodes[neighbor].pattern.split(',')]
                match = match + scan_exp.find_pattern(n_pattern, [alist])
            mnodes = merge_nearby(mnodes, neighbor, match, thisn, first_node)
    return mnodes


def merge_nearby(mnodes, neighbor, match, thisn, first_node):
    """
    Merge info from touching nodes.

    Arguments:
        mnodes -- list of Mnodes
        neighbor -- nearby node.
        match -- information of entries that match
        thisn -- neighbor of neighbor used to provide data to shorten
                 the list of possible values there
        first_node -- node for keeping track of class variables
    """
    change = False
    if len(mnodes[neighbor].possible) > 1:
        mergeset = []
        for entry in mnodes[neighbor].possible:
            if entry in match:
                mergeset.append(entry)
        if len(mnodes[neighbor].possible) != len(mergeset):
            change = True
        mnodes[neighbor].possible = mergeset
    else:
        mnodes[neighbor].possible = match
        change = True
    if len(mnodes[neighbor].possible) == 1:
        mnodes[neighbor].display_progress()
        if mnodes[thisn].type == 'S':
            mnodes[neighbor].solved_actors.append(
                mnodes[neighbor].possible[0][0])
        else:
            mnodes[neighbor].solved_movies.append(
                mnodes[neighbor].possible[0][0])
    if change:
        mnodes[first_node].last_mod.append(neighbor)
    return mnodes


def fix_question_marks(mnodes):
    """
    Handle nodes with question marks.

    As nodes get solved, those with question marks are special cases
    because they are the answers we are seeking, and because they do
    not have letter information.

    This progam repeats cycles of solve_nodes() and fix_question_marks()
    calls until the entire grid is filled.

    Arguements:
        mnodes -- list of nodes
    """
    first_node = False
    for dkey in mnodes:
        if not first_node:
            first_node = mnodes[dkey].name
        if mnodes[dkey].pattern == '?':
            goodn = []
            for node in mnodes[dkey].linked_nodes:
                if mnodes[node].possible:
                    if len(mnodes[node].possible) < 4:
                        goodn.append(node)
            if len(goodn) < 2:
                continue
            g1_assoc = mnodes[goodn[0]].get_associated()
            g2_assoc = mnodes[goodn[1]].get_associated()
            for answer in g1_assoc:
                if answer in g2_assoc:
                    if answer not in mnodes[dkey].possible:
                        mnodes[dkey].possible.append(answer)
            if len(mnodes[dkey].possible) == 1:
                mnodes[dkey].display_progress()
                mnodes[first_node].last_mod.append(dkey)
                mnodes[first_node].answers.append(mnodes[dkey].possible[0][0])
                n_pattern = [len(x) for x in
                             mnodes[dkey].possible[0][0].split(' ')]
                mnodes[dkey].pattern = ','.join([str(x) for x in n_pattern])
    mnodes = remove_dup_solutions(mnodes, first_node)
    return mnodes


def remove_dup_solutions(mnodes, first_node):
    """
    Remove entries found elsewhere in the puzzle.

    Arguements:
        mnodes -- list of puzzle nodes.
        first_node -- default node to extract common data from
    """
    for dkey in mnodes:
        dlist = []
        if len(mnodes[dkey].possible) > 1:
            for entry in mnodes[dkey].possible:
                nfield = entry[0]
                if nfield in mnodes[first_node].solved_actors:
                    dlist.append(entry)
                if nfield in mnodes[first_node].solved_movies:
                    dlist.append(entry)
                if nfield in mnodes[first_node].answers:
                    dlist.append(entry)
            for entry in dlist:
                mnodes[dkey].possible.remove(entry)
    return mnodes
