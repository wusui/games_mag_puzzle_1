# Games Magazine role-playing puzzle solver

This package can be used to solve puzzles similar to the Role-Playing
Contest printed in the September 2018 issue of Games Magazine

This package requires that python 3 is installed.

### Setup and Layout

Extract the contents of this git repo into a directory.  You should end
up with three directories.

* role_playing -- location of the python code and the user-created ini file
* games -- location of directories that each define a puzzle
* data -- location of text files witten into parts of html files being created

### role_playing.ini file

Before running this program, create a file named role_playing.ini in the role_playing directory.  The contents of this file will look like the following:

```
[DEFAULT]
contest = current
year = 2018
first_year = 25
verbose = False
```

Fields are:
* contest -- Name of the directory in games directory where the current puzzle.txt file is stored (see next section for description)
* year -- Most recent year for a movie in this puzzle.  If omitted, the current year is used.
* first_year -- First year for a movie in this puzzle.  This can be either a year number or a number of years (25 here would  include movies for the last 25 years).  The code tries to intelligently guess what the user meant.
* verbose -- If True, display progress lines while running.  Defaults to False

### Game directory and puzzle.txt format

Before running this program, the user also needs to create a puzzle to be used.  The text 'Contest-directory' in the rest of this document is a directory name chosen by the user. 

This puzzle is in games/contest-directory/puzzle.txt.  To create the puzzle, do the following:
* cd games
* mkdir contest-directory
d* vi puzzle.txt

Puzzle.txt will contain entries defining each of the individual figures in the contest (both squares and circles).  Each line in puzzle.txt will represent an entry, with fields being deliniated by vertical bars ('|').

The fields in a puzzle.txt line will consist of the following:
* Indicator if the figure represented is a Circle (actor) or Square (movie).
* X,Y coordinate address of this figure.  The upper leftmost point in this grid is 0,0.
* Information on the word lengths in the figure. A question mark indicates that this figure contains one of the answers that we are trying to find.
* A colon separated list of coordinates of other figures that this figure links to.  The links here point left to right, top to bottom.  This lowers the amount
of data needed.  When solving, the link of course points both ways.

For example, consider the following set of data:

```
C|0,0|8,7|1,0:0,1
S|1,0|2|2,0
```

The first entry here is an actor (circle) located in the top left corner of the puzzle page (location 0,0).  The text in the circle is "8,7" and it points to two other locations (1,0 and 0,1).

The second entry here is a movie (square) located to the right of the previous figure.  The text in this square is "2" and it points to one other location (2,0).

## Running this program

To run this program, cd role_playing and run python3 start_module.py.  It takes about 5 minutes to run and produces a solution file named games/contest-directory/solution.html.

### Files Created

There are two major tasks in this program.  The first is to scan imdb files for eligible movies and the second is to analyze the results to find answers associated with each figure.  After the first task is finished, a file named movies.json is created containing information about possible movies.  After the second task is finished, a file name answers.json is created containing possible solutions.  In order to convert this information into html file, an additional file named solution.txt is created.

These json files that are created can act as checkpoints for this program.  If one keeps the movies.json file around, then when this program is rerun the first step is skipped.  If one keeps the answers.json file around, then the second step is skipped.

Before rerunning this problem, one should remove games/contest-directory/movies.json, games/contest-directory/answers.json, and games/contest-directory/solution.txt.
