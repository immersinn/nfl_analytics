
import warnings
##import sqlite3

import numpy
import pandas

player_stat_tables = ['ps_kicking',
 'ps_passing',
 'ps_fumbles',
 'ps_defensive',
 'ps_rushing',
 'ps_punt_returns',
 'ps_interceptions',
 'ps_kick_returns',
 'ps_receiving',
 'ps_punting']


def pandasDFFromQuery(rows, cols, err_spec):
    if len(rows) > 0:
        df = pandas.DataFrame(data=rows, columns=cols)
    else:
        df = pandas.DataFrame()
        warnings.warn("No data returned for query: %s" % err_spec)
    return(df)


def fetchTeamsLookupData(season, cursor):
    # Teams Info
    limit = 0
    names = []
    cities = []
    abrvs = []
    for row in cursor.execute('''SELECT name, city_name, abrv
                                 FROM teams
                                 WHERE year = "%s"''' % str(season)):
        names.append(row[0])
        cities.append(row[1])
        abrvs.append(row[2])
    abrv_name_lookup = {k:v for (k,v) in zip(abrvs, names)}
    name_city_lookup = {k:v for (k,v) in zip(names, cities)}
    return(abrv_name_lookup, name_city_lookup)


def fetchPlayerSeasons(pid, cursor):   
    rows = cursor.execute('''SELECT DISTINCT game_ids.season
                             FROM gptt INNER JOIN game_ids
                             ON gptt.gid = game_ids.gid
                             WHERE gptt.pid = "%s"''' % \
                         (pid)).fetchall()
    rows = list(set(rows))
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "player id has no data associated"
    return(pandasDFFromQuery(rows, cols, err_spec))


def fetchPlayerGamesSeason(pid, season, cursor):
    
    rows = cursor.execute('''SELECT gptt.gid, gptt.pid, gptt.team,
                                    game_ids.season, game_ids.date, game_ids.home, game_ids.away
                             FROM gptt INNER JOIN game_ids
                             ON gptt.gid = game_ids.gid
                             WHERE gptt.pid = "%s" AND game_ids.season = "%s"''' % \
                          (pid, season)).fetchall()
    rows = list(set(rows))
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "player id %s in season %s" % (pid, season)
    df = pandasDFFromQuery(rows, cols, err_spec)
    df['date'] = pandas.to_datetime(df['date'])
    return(df)


def fetchPlayerEntriesSeason(pid, season, cursor):
    ''' Fetch list of games and stat types for which player has entries in 
        a given year.
    '''
    
    # Fetch Data
    rows = cursor.execute('''SELECT gptt.gid, gptt.pid, gptt.team, gptt.ps_table
                             FROM gptt INNER JOIN game_ids
                             ON gptt.gid = game_ids.gid
                             WHERE gptt.pid = "%s" AND game_ids.season = "%s"''' % \
                          (pid, season)).fetchall()
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "player id %s in season %s" % (pid, season)
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
        
    # Convert list of gids to single str of expected format
    gids_str = "(" + \
               ", ".join(["'" + str(gid) + "'" for gid in gids]) + \
               ")"
            
    # Fetch Data
    rows = cursor.execute('''SELECT * FROM %s
                             WHERE pid = "%s" AND gid IN  %s''' % \
                          (stat_area, pid,gids_str)).fetchall()
    cols = [c[0] for c in cursor.description]
    
    # Process query results
    err_spec = "stats from '%s' for player id %s" % (stat_area, pid)
    return(pandasDFFromQuery(rows, cols, err_spec))
