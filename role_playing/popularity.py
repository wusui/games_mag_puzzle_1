#!/usr/bin/python
"""
Determine popularity

When there are two or more entries for an actor or movie figure, then the
most popular one should be picked.
"""
from html.parser import HTMLParser
import re
import requests


class RatePeople(HTMLParser):
    # pylint: disable=W0223
    """
    Scan for number of results on this person's Google page.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = 0

    def handle_data(self, data):
        if data.startswith('About '):
            if data.endswith(' results'):
                numb = data.split(' ')[1]
                numb = re.sub('[,]', '', numb)
                self.result = int(numb)


class RateMovies(HTMLParser):
    # pylint: disable=W0223
    """
    Scan for Box Office gross on this movie's Google page.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.result = 0

    def handle_data(self, data):
        if data.startswith('Box office'):
            self.flag = True
        if self.flag:
            if data.endswith('million USD'):
                numb = data.split('.')[0]
                self.result = int(numb)
                self.flag = False


def rank_people(peep):
    """
    Return integer value from Google page hit count for this user.

    Arguments:
        peep -- person's name
    """
    parm = '+'.join(peep.split(' '))
    page1 = "https://www.google.com/search?q=%s" % parm
    ndata = requests.get(page1)
    parser = RatePeople()
    parser.feed(ndata.text)
    return parser.result


def rank_movies(movie):
    """
    Return integer value from Google page Box Office returns for this movie

    Arguments:
        movie -- movie title
    """
    parm = '+'.join(movie.split(' '))
    parm += '+movie'
    page1 = "https://www.google.com/search?q=%s" % parm
    ndata = requests.get(page1)
    parser = RateMovies()
    parser.feed(ndata.text)
    return parser.result
