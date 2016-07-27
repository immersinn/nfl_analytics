
import warnings
import sqlite3

import numpy
import pandas


def pandasDFFromQuery(rows, cols, err_spec):
    if len(rows) > 0:
        df = pandas.DataFrame(data=rows, columns=cols)
    else:
        df = pandas.DataFrame()
        warnings.warn("No data returned for query: %s" % err_spec)
    return(df)


def fetchPlayerGamesYear(pid, year, cursor):
    
    rows = cursor.execute('''SELECT gptt.gid, gptt.pid, gptt.team,
                                    game_ids.year, game_ids.date, game_ids.home, game_ids.away
                             FROM gptt INNER JOIN game_ids
                             ON gptt.gid = game_ids.gid
                             WHERE gptt.pid = %s AND game_ids.year = %s''' % \
                          (pid, year)).fetchall()
    rows = list(set(rows))
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "player id %s in year %s" % (pid, year)
    return(pandasDFFromQuery(rows, cols, err_spec))


def fetchPlayerEntriesYear(pid, year, cursor):
    ''' Fetch list of games and stat types for which player has entries in 
        a given year.
    '''
    
    # Fetch Data
    rows = cursor.execute('''SELECT gptt.gid, gptt.pid, gptt.team, gptt.ps_table
                             FROM gptt INNER JOIN game_ids
                             ON gptt.gid = game_ids.gid
                             WHERE gptt.pid = %s AND game_ids.year = %s''' % \
                          (pid, year)).fetchall()
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "player id %s in year %s" % (pid, year)
    return(pandasDFFromQuery(rows, cols, err_spec))


def fetchPlayerStatsDetails(pid, gids, stat_area, cursor):
    ''' Fetch stats of specified type for specified games
        for the specified player
    '''
    
    if type(gids) not in [list, set, tuple]:
        err_msg = "gids not valid iterable type (str, list, or tuple)"
        raise TypeError(err_msg)
    if stat_area not in player_stat_tables:
        err_msg = "Invalid stat area provided (" + \
                  ", ".join(player_stat_tables) + ")"
        raise ValueError(err_msg)
        
    # Convert list of gids to singel str of expected format
    gids_str = "(" + \
               ", ".join(["'" + str(gid) + "'" for gid in gids]) + \
               ")"
            
    # Fetch Data
    rows = cursor.execute('''SELECT * FROM %s
                             WHERE pid = %s AND gid IN  %s''' % \
                          (stat_area, pid,gids_str)).fetchall()
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "stats from '%s' for player id %s" % (stat_area, pid)
    return(pandasDFFromQuery(rows, cols, err_spec))
