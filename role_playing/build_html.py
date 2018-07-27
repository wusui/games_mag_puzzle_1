#!/usr/bin/python
"""
Generate an html file drawing of the layout.

The user supplied information is in ../games
Html pieces (toppart.txt and botpart.txt) are stored in ../data
"""
import os


def generate_html(location, info_file):
    """
    Wrap text returned from movie_xlate with html code.

    Arguments:
        location: directory/folder in ../games where this puzzle's
                  information is stored
        info_file: text_file containing layout information

    Creates ../games/solution.html based on information in info_file.
    Uses ../games/toppart.txt and ../games/botpart.txt
    """
    toppart = os.path.join('..', 'data', 'toppart.txt')
    botpart = os.path.join('..', 'data', 'botpart.txt')
    intext = os.path.join('..', 'games', location, info_file)
    outputf = os.path.join('..', 'games', location, 'solution.html')
    with open(toppart, 'r+') as in_file:
        txt = in_file.read()
    movie_txt, data_x, data_y, pt_size = movie_xlate(intext)
    txt = txt % (data_x, data_y, pt_size)
    with open(outputf, 'w') as out_file:
        out_file.write(txt)
    with open(outputf, 'a+') as out_file:
        out_file.write(movie_txt)
    with open(botpart, 'r+') as in_file:
        txt = in_file.read()
    with open(outputf, 'a+') as out_file:
        out_file.write(txt)


def measurements(std_size):
    """
    Generate a dictionary of useful numbers for page formatting.

    Arguments:
        std_size: size of a cell
    The following values are returned:
        'std_size_loc' == size of cell in display output
        'half_size' == mid-point locator in cell
        'point_size' == point size of text inside circles and squares
        'c_radius' == radius of circle
        'sq_len'  == length of side of square
        'sq_off' == offset of upper left corner of square in cell
        'txt_off' == vertical offset of text in figure
        'gap_off' == vertical gap between lines of text in figure
    """
    return {
        'std_size_loc': std_size,
        'half_size': int(std_size / 2),
        'point_size': int(std_size / 10),
        'c_radius': int(std_size * 2 / 5),
        'sq_len': int(std_size * 7 / 10),
        'sq_off': int(std_size * 3 / 20),
        'txt_off': int(std_size * 3 / 50),
        'gap_off': int(std_size * 3 / 200)
    }


def movie_xlate(in_text):
    """
    Return an html translation of the data in a solution.

    Arguments:
        in_text: text file containing layout information in movie puzzle format

    returns:
       A string of the html code drawing the information in in_text, along with
       sizes of the output and point size of the text.
    """
    with open(in_text, 'r+') as in_file:
        figures = in_file.read().split('\n')
    size_data = measurements(200)
    ostring = ''
    tstring = ''
    ret_parm = get_figure_info(figures, size_data)
    afigs = ret_parm[0]
    text = ret_parm[1]
    ostring += ret_parm[2]
    max_coord = ret_parm[3]
    ostring += '      context.textBaseline="top";\n'
    for indx, parts in enumerate(afigs):
        ostring += draw_figure(parts, size_data)
        tstring += fill_in_text(parts, size_data, text[indx])
    ostring += tstring
    return (ostring, max_coord[0]+size_data['std_size_loc'],
            max_coord[1]+size_data['std_size_loc'],
            size_data['point_size'])


def get_figure_info(figures, size_data):
    """
    Parse movie data and make calls to draw line segments.

    Arguments:
        figures: list of lines read from movie puzzle text.
        size_data: measurements information

    Returns:
        afig: list representing each figure in the diagram:
              [Circle(C) or Square(S), x-location, y-location]
        text: Text inside the figure  (list of lines)
        ostring: Html text that draws all the interconnecting lines.
        (data_x, data-Y): maximum x-location, maximum y-location
    """
    data_x = 0
    data_y = 0
    ostring = ''
    text = []
    afigs = []
    for figure in figures:
        if not figure:
            continue
        oparts = figure.split('|')
        coords = oparts[1].split(',')
        xval = int(coords[0]) * size_data['std_size_loc']
        yval = int(coords[1]) * size_data['std_size_loc']
        if xval > data_x:
            data_x = xval
        if yval > data_y:
            data_y = yval
        afigs.append([oparts[0], xval, yval])
        text.append(oparts[2])
        ostring += draw_segment(oparts[3].split(':'), size_data, xval, yval)
    return [afigs, text, ostring, (data_x, data_y)]


def draw_segment(segments, size_data, xval, yval):
    """
    Draw line segments

    Arguments:
        segments: List of endpoints for each line segment
        size_data: measurements information
        xval: x-coordinate of starting point
        yval: y-ccordinate of starting point

    Returns:
        Html text that draws these lines.
    """
    ostring = ''
    for segment in segments:
        if not segment:
            continue
        endp = segment.split(',')
        xep = int(endp[0]) * size_data['std_size_loc']
        yep = int(endp[1]) * size_data['std_size_loc']
        ostring += "      context.beginPath();\n"
        ostring += "      context.moveTo(%d,%d);\n" % \
            (xval+size_data['half_size'], yval+size_data['half_size'])
        ostring += "      context.lineTo(%d,%d);\n" % \
            (xep+size_data['half_size'], yep+size_data['half_size'])
        ostring += "      context.stroke();\n"
    return ostring


def draw_figure(parts, size_data):
    """
    Draw figures (either square or circle)

    Arguments:
        parts: figure information. 'C' or 'S', x-coordinate, y-coordinate
        size_data: measurements information

    Returns: Html text that draws these figures.
    """
    ostring = ''
    if parts[0].endswith('S'):
        ostring += "      context.beginPath();\n"
        ostring += "      context.rect(%d,%d,%d,%d);\n" % \
            (parts[1]+size_data['sq_off'], parts[2]+size_data['sq_off'],
             size_data['sq_len'], size_data['sq_len'])
        ostring += "      context.fillStyle = 'white';\n"
        ostring += "      context.fill();\n"
    else:
        ostring += "      context.beginPath();\n"
        ostring += "      context.arc(%d,%d,%d,0,2*Math.PI);\n" % \
            (parts[1]+size_data['half_size'],
             parts[2]+size_data['half_size'],
             size_data['c_radius'])
        ostring += "      context.fillStyle = 'white';\n"
        ostring += "      context.fill();\n"
        ostring += "      context.closePath();\n"
    ostring += "      context.stroke();\n"
    return ostring


def fill_in_text(parts, size_data, in_text):
    """
    Write the text that appears inside the squares and circles.

    Arguments:
        parts: figure information. 'C' or 'S', x-coordinate, y-coordinate
        size_data: measurements information
        in_text: Text to be written

    Returns: Formatted Html text of the text input.
    """
    tstring = ''
    words = in_text.split(" ")
    wcount = len(words)
    gaps = wcount - 1
    vstart = wcount * size_data['txt_off'] + gaps * size_data['gap_off']
    vspc = parts[2] + size_data['half_size'] - vstart
    for word in words:
        hspc = parts[1] + size_data['half_size']
        tstring += "      hspc = %d - context.measureText" % hspc
        tstring += "('%s').width/2;\n" % word
        tstring += "      hspc = Math.floor(hspc);\n"
        tstring += "      context.fillStyle = 'black';\n"
        tstring += "      context.fillText('%s', hspc, %d);\n" % \
            (word, vspc)
        vspc += size_data['sq_off']
    tstring += 'context.font = "Bold %dpx Arial";\n' % size_data['point_size']
    return tstring

if __name__ == "__main__":
    generate_html('current', 'puzzle.txt')
