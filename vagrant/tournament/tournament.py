#!/usr/bin/env python
# tournament.py -- implementation of a Swiss-system tournament

import psycopg2
import math


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname=tournament")
        cursor = db.cursor()
        return db, cursor
    except:
        print("<error message>")


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    # We delete all the records from players ;)
    cursor.execute("DELETE FROM players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    cursor.execute("SELECT COUNT (*) FROM players;")
    # We get the first row of the query
    single_row_of_data = cursor.fetchone()
    db.close()

    # we return the first element of the row. Which is the counted value.
    return single_row_of_data[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).

    old version of code --> c.execute("INSERT INTO players
    (NAME,WINS,MATCHES_PLAYED) VALUES ($$"+name+"$$,0,0);")
    """
    db, cursor = connect()

    query = "INSERT INTO players (name) VALUES (%s);"
    parameter = (name,)
    cursor.execute(query, parameter)

    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()
    """
    We select the players.ID and players.NAME and we count the number
    of wins of the players. We join the tables, group them by player ID
    and order by wins.
    """
    cursor.execute("SELECT players.id,players.name, \
                    count(matches.ID_PLAYER1)  as wins from players left \
                    join matches on players.id = matches.ID_PLAYER1 \
                    group by players.id order by wins desc;")
    rows = cursor.fetchall()
    standings = []
    for item in rows:
        # calculate wins as appearances on column winner
        query = "SELECT COUNT (*) FROM matches where ID_PLAYER1 = (%s) \
                or ID_PLAYER2 = (%s);"
        parameter = (item[0], item[0])
        cursor.execute(query, parameter)
        matches = cursor.fetchone()
        l = list(item)
        l.append(matches[0])
        standings.append(l)
    db.close()
    return standings


def standingsNiceDisplay(rows):
    """EXTRA CREDIT Writes on the file file.txt the standings
    when the function is called. """

    numberofplayers = countPlayers()
    playerposition = 0
    f = open('file.txt', 'a')
    f.write("Ranking | Name      | Wins  |\n")
    while (playerposition < numberofplayers):
        f.write(" " + str(playerposition + 1) + ".     | " +
                str(rows[playerposition][1]) +
                "  | " + str(rows[playerposition][2]) + "     |\n")
        playerposition = playerposition + 1
    f.close()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost

    """
    db, cursor = connect()
    """ We insert into matches the ouctome of the match. Since the player in the
    first position is the winner then the outcome is always 1."""
    query = "INSERT INTO matches (ID_PLAYER1, ID_PLAYER2,OUTCOME) \
            VALUES (%s, %s, %s);"
    parameter = (winner, loser, 1)
    cursor.execute(query, parameter)
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name

    """
    # We get all the rows from the colums ID, Name of the table players.
    rows = playerStandings()
    isfirst = True
    # We proceed to organize the pairings.
    mypairings = []
    for item in rows:
        # Since item is a pair we want to know if it's the first or the second.
        if (isfirst):
            firstvalue = item
            isfirst = False
        else:
            secondvalue = item
            isfirst = True
            # We prepare the pairing list and append it pairings list.
            mypair = [firstvalue[0], firstvalue[1],
                      secondvalue[0], secondvalue[1]]
            mypairings.append(mypair)
    return mypairings


def swissPairingsId():
    """Returns a list of pairs of players' Ids for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, id2)
        id1: the first player's unique id
        id2: the second player's unique id
    """
    rows = playerStandings()
    isfirst = True
    mypairings = []
    for item in rows:
        if (isfirst):
            firstvalue = item
            isfirst = False
        else:
            secondvalue = item
            isfirst = True
            mypair = [firstvalue[0], secondvalue[0]]
            mypairings.append(mypair)
    return mypairings


def playSampleTournament():
    """ Plays a tournament with the registered players. """

    f = open('file.txt', 'w')
    numberofplayers = countPlayers()
    numberofrounds = int(math.log(numberofplayers, 2))
    f.write("\nWelcome to the 1st Open Grand Slam Tournament.\n")
    f.write("There are " + str(numberofplayers) +
            " players registered.\nThere will be a total of " +
            str(numberofplayers - 1) + " matches in " + str(numberofrounds) +
            " rounds.\nGood luck to you all!\n")
    roundnow = 1
    f.close()

    # We proceed with the rounds
    while (roundnow <= numberofrounds):
        """ We prepare the pairings with a custom function
         that returns only the id's of the pairings."""
        pairingofround = swissPairingsId()
        for itemm in pairingofround:
            # We report the matches for the pairings.
            reportMatch(itemm[0], itemm[1])

        # We proceed with the standings
        f = open('file.txt', 'a')
        f.write("\nStandings after the round\n")
        f.close()
        standings = playerStandings()
        standingsNiceDisplay(standings)
        roundnow = roundnow+1

    f = open('file.txt', 'a')
    f.write("\nAnd the tournament has finished and we have a winner!!!!!\n")
    f.write("Congratulations to " + str(standings[0][1]) + "! Great games!")
    f.close()
