#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#


import psycopg2
import math


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit() 
    conn.close()

    



def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    # We delete all the records from players ;)
    c.execute("DELETE FROM players;")
    conn.commit() 
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT (*) FROM players;")

    # We get the first row of the query 
    single_row_of_data = c.fetchone()

    conn.commit() 
    conn.close()

    # we return the first element of the row. Which is the counted value.
    return single_row_of_data[0];




def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).

       old version of code --> c.execute("INSERT INTO players (NAME,WINS,MATCHES_PLAYED) VALUES ($$"+name+"$$,0,0);")
    """
    conn = connect()
    c = conn.cursor()

    # we execute the query passing the parameters with placeholders to avoid problems with apostrophes.
    c.execute("INSERT INTO players (NAME,WINS,MATCHES_PLAYED) VALUES (%s,%s,%s)",(name,0,0))

    conn.commit() 
    conn.close()



def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    # We query the table players and sort it in descending order of wins.
    c.execute("SELECT * FROM players ORDER BY WINS DESC;")
    rows = c.fetchall()


    conn.commit() 
    conn.close()
    return rows

def standingsNiceDisplay(rows):
    """EXTRA CREDIT Writes on the file file.txt the standings when the function is called. """

    numberofplayers = countPlayers()
    playerposition = 0
    f = open('file.txt','a')
    f.write("Ranking | Name      | Wins  |\n")
    while (playerposition<numberofplayers):
        f.write(" "+str(playerposition+1)+".     | "+str(rows[playerposition][1])+"  | "+str(rows[playerposition][2])+"     |\n")
        playerposition = playerposition+1
    f.close()



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost

    """
    conn = connect()
    c = conn.cursor()
    # We insert into matches the ouctome of the match. Since the player in the first position is the winner then the outcome is always 1.
    c.execute("INSERT INTO matches (ID_PLAYER1,ID_PLAYER2,OUTCOME) VALUES (%s,%s,%s)",(winner,loser,1))
    # We update the players statistics
    c.execute("UPDATE players SET MATCHES_PLAYED = MATCHES_PLAYED + 1 WHERE ID = (%s)",(winner,))
    c.execute("UPDATE players SET WINS = WINS + 1 WHERE ID = (%s)",(winner,))
    c.execute("UPDATE players SET MATCHES_PLAYED = MATCHES_PLAYED + 1 WHERE ID = (%s)",(loser,))
    
    


    conn.commit() 
    conn.close()
 
 
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

    class thevalue():
            # The constructor that will be called when creating an instance.
        def __init__(self,first_of_pair):
            self.actualvalue = first_of_pair
            
            

    conn = connect()
    c = conn.cursor()

    # We get all the rows from the colums ID, Name of the table players.

    c.execute("SELECT ID,NAME FROM players ORDER BY WINS;")
    rows = c.fetchall()
    isfirst = True
    # We proceed to organize the pairings.
    mypairings = []
    for item in rows:
        # Since it's item is a pair we want to know if it's the first item or the second.
        if (isfirst):
            firstvalue = thevalue(item)
            isfirst = False
        else:
            secondvalue = thevalue(item)
            isfirst = True
            # We prepare the pairing list and append it pairings list.
            mypair = [firstvalue.actualvalue[0],firstvalue.actualvalue[1],secondvalue.actualvalue[0],secondvalue.actualvalue[1]]
            
            mypairings.append(mypair)
    
    conn.commit() 
    conn.close()
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

    class thevalue():
            # The constructor that will be called when creating an instance.
        def __init__(self,first_of_pair):
            self.actualvalue=first_of_pair
            
            

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT ID FROM players ORDER BY WINS;")
    rows = c.fetchall()
    isfirst = True
    
    mypairings = []
    for item in rows:
        if (isfirst):
            firstvalue = thevalue(item)
            isfirst = False
        else:
            secondvalue = thevalue(item)
            isfirst = True
            mypair = [firstvalue.actualvalue[0],secondvalue.actualvalue[0]]
            
            mypairings.append(mypair)
    
    conn.commit() 
    conn.close()
    return mypairings



def playSampleTournament():
    """ Plays a tournament with the registered players. """

    f = open('file.txt','w')
    numberofplayers = countPlayers()
    numberofrounds = int(math.log(numberofplayers,2))
    f.write("\nWelcome to the 1st Open Grand Slam Tournament.\n")
    f.write("There are "+str(numberofplayers)+" players registered.\nThere will be a total of "+str(numberofplayers-1)+" matches in "+str(numberofrounds)+" rounds.\nGood luck to you all!\n")
    roundnow = 1
    f.close()

    # We proceed with the rounds
    while (roundnow <= numberofrounds):
        # We prepare the pairings with a custom function that returns only the id's of the pairings.
        pairingofround = swissPairingsId()
        for itemm in pairingofround:
            # We report the matches for the pairings.
            reportMatch(itemm[0],itemm[1])
        
        #We proceed with the standings
        f = open('file.txt','a')
        f.write("\nStandings after the round\n")
        f.close()

        standingsNiceDisplay(standings)
        roundnow = roundnow+1
    
    f = open('file.txt','a')
    f.write("\nAnd the tournament has finished and we have a winner!!!!!\n")
    f.write("Congratulations to "+str(standings[0][1])+"! Great games!")
    f.close()




