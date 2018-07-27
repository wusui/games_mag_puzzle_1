#!/usr/bin/python
"""
Find all possible movies.

Loop through the TOPNMOVIES for each year in the range.  Extract
that data into a dictionary where each entry matches a pattern
of possible movie titles. This list of patterns matches possible
title patterns in the puzzle.
"""
from html.parser import HTMLParser
import re
import requests

PAGE = "https://www.imdb.com/search/title?year=%d&title_type" + \
       "=feature&page=%d&ref_=adv_nxt"
TOPNMOVIES = 300


class MoviesParse(HTMLParser):
    # pylint: disable=W0223
    """
    Extract movie names from an imdb page.

    self.results is a dictionary returned from the parsing of the
    movie page.  It is indexed by word pattern, and each entry is
    a list of movies that match the word pattern.  The movie data
    is saved as a title and an imdb link.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = {}
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for apt in attrs:
                if apt[0] == 'href':
                    if apt[1].endswith('ref_=adv_li_tt'):
                        self.title = apt[1]

    def handle_data(self, data):
        if self.title:
            self.result[data] = self.title
            self.title = ''


def get_sample_of_movies(year, page):
    """
    Return a dictionary of movie titles indexed by imdb link.

    Arguments:
       year -- year of this search
       page -- page number of top movies for that year.
    """
    page1 = PAGE % (year, page)
    ndata = requests.get(page1)
    parser = MoviesParse()
    parser.feed(ndata.text)
    return parser.result


def fix_title(imdb_str):
    """
    Given an imdb string, strip off extraneous information.
    """
    title = imdb_str.split('?')
    return title[0][1:-1]


def massage_data(inputd):
    """
    Strip of punctuation in titles prior to doing searches.
    """
    outd = {}
    for movie in inputd.keys():
        mname = re.sub("[-:,'!/?]", '', movie)
        outd[mname] = fix_title(inputd[movie])
    return outd


def collect_data(year, page):
    """
    Collect range of rated movies for a given year

    Arguments:
        year -- year number
        page -- imdb page for top n pages
    """
    table = get_sample_of_movies(year, page)
    return massage_data(table)


def extract_movie_sizes(input_file):
    """
    Return a list of movie title sizes.

    Arguments:
        input_file -- text of puzzle file.  Third element in this
                      text is a movie title pattern ('4,4,3,4'
                      for example).
    """
    mlist = []
    with open(input_file, 'r+') as in_file:
        figures = in_file.read().split('\n')
    for mline in figures:
        if not mline:
            continue
        parts = mline.split('|')
        if parts[2] == '?':
            continue
        if parts[0] == 'C':
            continue
        mlist.append(parts[2])
    olist = list(set(mlist))
    return olist


def conv_to_indx(movie):
    """
    Convert a movie title to an index based on word lengths.

    For example: Gone With the Wind --> 4,4,3,4

    Arguments:
        movie -- movie title

    Returns a text representation of the word lengths.
    """
    numbs = [str(len(i)) for i in movie.split(' ')]
    return ','.join(numbs)


def find_films(ploc, start_info):
    """
    Find all possible movies for this puzzle.

    Arguments:
        ploc -- text of the puzzle.
        start_info -- dictionary of ranges for the puzzle.

    Returns:
        dictionary indexed by movie letter pattern.  Each entry
        is a list of possible movies.  Each element of that list
        consists of a title and an imdb reference.
    """
    mdict = {}
    keys = extract_movie_sizes(ploc)
    for key in keys:
        mdict[key] = []
    for level in range(1, (TOPNMOVIES // 50)+1):
        for yrv in range(start_info['year'], start_info['first'] - 1, -1):
            if start_info['verbose'] == 1:
                endm = level * 50
                strtm = endm - 49
                print("find movies %d through %d for %d" % (strtm, endm, yrv))
            movies = collect_data(yrv, level)
            for movie in movies:
                mindx = conv_to_indx(movie)
                if mindx in keys:
                    mdict[mindx].append([movie, movies[movie]])
    return mdict
