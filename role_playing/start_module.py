#!/usr/bin/python
"""
Collect starting information
"""
import configparser
from datetime import datetime
import os
import json
import find_movies
import link_nodes
import solve_nodes
import build_html
import popularity


def start_rtn():
    """
    Read role_playing.ini for starting values

    Returns:
        contest: directory in games directory (location of data)
        year: year contest starts (current year if omitted)
        first_year: first year (either year, or year gap (last n years))

    """
    ini_file = 'role_playing.ini'
    try:
        config = configparser.ConfigParser()
        config.read(ini_file)
        info = config['DEFAULT']
        verbosity = False
        if 'verbose' in info:
            verbosity = config.getboolean('DEFAULT', 'verbose')
        if 'year' in info:
            year = int(info['year'])
        else:
            year = datetime.now().year
        first = int(info['first_year'])
        offset = year - first
        if first < offset:
            first = offset
        return {'contest': info['contest'], 'year': year, 'first': first,
                'verbose': verbosity}
    except KeyError as errval:
        print("Unable to extract %s from %s" % (errval, ini_file))
        return False


def main_program():
    """
    Solve a  Games Magazine role-playing puzzle.

    role_playing.ini DEFAULT value of contest should be set to the directory
    in ../games that has the puzzle.txt information for the puzzle that you
    want to solve.

    movies.json contains a dictionary indexed by movie title word lengths
    ("4,4,3,4" could be "Gone with the Wind").  It is created by scanning
    puzzle.txt for possible movie titles and then finding those titles on
    Imdb for the years specified.  If this file exists, then it is used.  If
    you want to rerun the scanning for movie titles (takes a while), then
    remove the movies.json file.

    Once the movies are loaded, the second long period of execution occurs
    during which time entries in the puzzle are figured.  When run in verbose
    mode, solutions found will be displayed.

    answers.json stores the answers as a directory indexed by a string
    derived from the x-y coordinates of a figure in the puzzle.  Each
    entry is a list of possible answers.  When finished, in most cases
    this list will contain only one entry.

    After all solutions are found, generate_html is called.
    """
    params = start_rtn()
    gpath = os.path.join('..', 'games', params['contest'])
    ploc = os.path.join(gpath, 'puzzle.txt')
    moviesf = os.path.join(gpath, 'movies.json')
    if os.path.isfile(moviesf):
        with open(moviesf, 'r') as json_file:
            info = json.loads(json_file.read())
    else:
        info = find_movies.find_films(ploc, params)
        with open(moviesf, 'w') as outfile:
            json.dump(info, outfile)
    answersf = os.path.join(gpath, 'answers.json')
    if os.path.isfile(answersf):
        with open(answersf, 'r') as json_file:
            answers = json.loads(json_file.read())
    else:
        answers = do_searching(ploc, info, params)
        with open(answersf, 'w') as outfile:
            json.dump(answers, outfile)
    generate_html(ploc, answers, gpath)


def generate_html(ploc, answers, gpath):
    """
    Generate the html output

    The original puzzle mapping is passed in so that moved fields that do
    not change can be initialized or reinitialized.
    The text entries in that puzzle are changed prior to being saved in
    solution.txt.

    Arguments:
        ploc    -- location of the puzzle.txt file
        answers -- dictionary indexed by location of lists of possible answers.
                 When solved, most of these have one entry.
        gpath   -- directory where the files being generated will be stored.

    Results int the creation of the solutions.txt file.
    """
    with open(ploc, 'r+') as in_file:
        figures = in_file.read().split('\n')
    txt = ''
    for entry in figures:
        if not entry:
            continue
        parts = entry.split('|')
        indx = parts[1]
        a_var = answers[indx]
        if len(a_var) > 1:
            if parts[0] == 'C':
                a_var = sorted(a_var, key=popularity.rank_people, reverse=True)
            else:
                a_var = sorted(a_var, key=popularity.rank_movies, reverse=True)
        parts[2] = a_var[0]
        txt += '|'.join(parts)+'\n'
    out_file = os.path.join(gpath, 'solution.txt')
    with open(out_file, 'w') as out_file:
        out_file.write(txt)
    build_html.generate_html(gpath, 'solution.txt')


def do_searching(ploc, info, params):
    """
    Main loop of the repeating searches being performed.

    This calls solve_nodes.solve_nodes to fill in squares and circles based
    on nearby completed entries.  It then tries to fill in pages that have
    question marks, and removes potential entries that already exist as
    solutions.  When there are no more candidates for checking left,
    it ends up making one more pass through the grid rechecking those nodes
    that still have multsiple possible entries.

    Finally, it reformats the data to have the page location of the figure
    and a list of possible answers in that location.  This list gets returned.

    Arguments:
        ploc -- location of the puzzle.txt file.
        info -- partial solution previously derived.
        params -- role_playing.ini data.
    """
    mnodes = link_nodes.link_nodes(ploc, info, params['verbose'])
    for dkey in mnodes:
        first_node = mnodes[dkey].name
        break
    while mnodes[first_node].last_mod:
        mnodes = solve_nodes.solve_nodes(mnodes)
        mnodes = solve_nodes.fix_question_marks(mnodes)
    for dkey in mnodes:
        if len(mnodes[dkey].possible) > 1:
            mnodes[first_node].last_mod.append(mnodes[dkey].name)
    mnodes = solve_nodes.solve_nodes(mnodes)
    mnodes = solve_nodes.fix_question_marks(mnodes)
    for entry in mnodes[first_node].fixed_links:
        entry[1].possible = entry[0].possible
    answers = {}
    for node in mnodes:
        answers[node] = [x[0] for x in mnodes[node].possible]
    return answers

if __name__ == "__main__":
    main_program()
