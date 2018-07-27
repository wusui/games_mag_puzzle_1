#!/usr/bin/python
"""
Experiments
"""
from html.parser import HTMLParser
import re
import requests


class ActorsInMovieParse(HTMLParser):
    """
    Scan imdb page to determine if an actor was in a given movie
    """
    # pylint: disable=W0223
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.state = 0
        self.name = ''
        self.role = ''
        self.imdb_id = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            for apt in attrs:
                if apt[0] == 'itemprop' and apt[1] == 'actor':
                    self.state = 1
                if apt[0] == 'class' and apt[1] == 'character' \
                        and self.state == 4:
                    self.state = 5
        if tag == 'a':
            for apt in attrs:
                if apt[0] == 'href':
                    if apt[1].startswith('/name/nm'):
                        if self.state == 1:
                            self.imdb_id = apt[1].split('?')[0]
                            self.state = 2
        if tag == 'span':
            if self.state == 2:
                self.state = 3

    def handle_data(self, data):
        if self.state == 3:
            self.name = data
        if self.state == 5:
            self.role += data

    def handle_endtag(self, tag):
        if tag == 'span':
            if self.state == 3:
                self.state = 4
        if tag == 'td':
            if self.state == 5:
                self.state = 0
                if self.role.find('uncredited') < 0:
                    self.name = re.sub("[']", '', self.name)
                    self.result.append([self.name, self.imdb_id[1:-1]])


class MoviesByActorParse(HTMLParser):
    """
    Scan imdb page to determine if a movie starred a given actor.
    """
    # pylint: disable=W0223
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.state = 0
        self.imdb_id = ''
        self.prev = 'x'
        self.nownumv = ''
        self.checktxt = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for apt in attrs:
                if apt[0] == 'id':
                    if apt[1].startswith("actor-") or \
                       apt[1].startswith("actress"):
                        self.state = 1
        if tag == 'a':
            for apt in attrs:
                if apt[0] == 'href':
                    if apt[1].startswith('/title/tt'):
                        if self.state == 1:
                            parts = apt[1].split('?')
                            self.imdb_id = parts[0][1:-1]
                            self.nownumv = parts[1].split('_')[-1]

    def handle_data(self, data):
        if self.state == 1:
            self.checktxt += data

    def handle_endtag(self, tag):
        if self.state == 1:
            if tag == 'div':
                self.state = 0
                do_it = True
                if self.prev == self.nownumv:
                    do_it = False
                self.prev = self.nownumv
                self.nownumv = ''
                if self.checktxt.find("uncredited") >= 0:
                    do_it = False
                if self.checktxt.find("(TV") >= 0:
                    do_it = False
                if do_it:
                    title = self.checktxt.split('\n')[4]
                    title = re.sub("[-:,'!/?]", '', title)
                    self.result.append([title, self.imdb_id])
                self.checktxt = ''


def get_actor_from_movie(movie):
    """
    Get list of actors in a movie

    Arguments:
        movie -- movie we are checking

    Returns a list of actors in that movie
    """
    page1 = "https://www.imdb.com/%s/fullcredits?ref_=tt_cl_sm#cast" % movie
    ndata = requests.get(page1)
    parser = ActorsInMovieParse()
    parser.feed(ndata.text)
    return parser.result


def get_movie_from_actor(actor):
    """
    Get list of movies an actor appeared in

    Arguments:
        actor -- name of actor

    Returns a list of movies that actor appeared in
    """
    page1 = "https://www.imdb.com/%s" % actor
    ndata = requests.get(page1)
    parser = MoviesByActorParse()
    parser.feed(ndata.text)
    return parser.result


def pattern_matches(pattern, inputd):
    """
    Find specific pattern.

    Determine if the word lengths in a string match a numeric pattern

    Arguements:
       pattern -- list of word lengths in title or name
       inputd -- text to be checked

    Returns true or false.
    """
    apattern = [len(i) for i in inputd[0].split(' ')]
    return pattern == apattern


def find_pattern(pattern, inlist):
    """
    Find general patterns.

    Arguemnents:
        pattern -- list of lists of numbers.
        inlist -- list of texts to be checked.

    Returns list of entries in inlist that match a pattern in pattern
    """
    answer_list = []
    for searchm in inlist:
        for searche in searchm:
            if pattern_matches(pattern, searche):
                answer_list.append(searche)
    return answer_list
