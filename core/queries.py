
import warnings
import sqlite3

import numpy
import pandas

from sports_data_scraping.espn import nfl_stat_lookups


player_stat_tables = nfl_stat_lookups.player_stat_tables


def pandasDFFromQuery(rows, columns=[]):
    if len(rows) > 0:
        df = pandas.DataFrame(data=rows)
        cols = df.columns
        for col in cols:
            if col.lower().find('date') > -1:
                df[col] = pandas.to_datetime(df[col])
            if col in ['gid', 'pid']:
                df[col] = df[col].astype('str')
    else:
        df = pandas.DataFrame(data=[])
    return(df)


def genQuery(query_str, db_path, err_spec, verbose=False):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = [dict(r) for r in \
                cursor.execute(query_str).fetchall()]
        columns = [c[0] for c in cursor.description]
##    df = ppandasDFFromQuery(rows, columns=columns)
    df = pandasDFFromQuery(rows)
    if verbose and df.shape[0]==0:
        warnings.warn("No data returned for query: %s" % err_spec)
    return(df)


def genQuery_dictArgs(query_str, query_args, db_path, err_spec, verbose=False):
    """
    As the query above, but instead uses a dictionary to specify
    variable arguments to the query
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = [dict(r) for r in \
                cursor.execute(query_str, query_args).fetchall()]
        columns = [c[0] for c in cursor.description]
    df = pandasDFFromQuery(rows)
    if verbose and df.shape[0]==0:
        warnings.warn("No data returned for query: %s" % err_spec)
    return(df)
        


def fetchTeamsLookupData(season, db_path):
    """
    Query data for team names, cities, and abbreviations.
    Return data as two lookup dictionaries.
    """
    # Build Query
    query_text = '''SELECT name, city_name, abrv
                   FROM team_info
                   WHERE season = "%s"''' % \
                   str(season)
    df = genQuery(query_text, db_path, "No teams in table")
    abrv_name_lookup = {k:v for (k,v) in zip(df['abrv'], df['name'])}
    name_city_lookup = {k:v for (k,v) in zip(df['name'], df['city_name'])}

    return(abrv_name_lookup, name_city_lookup)


def fetchPlayerSeasons(pid, db_path):

    # Build Query
    query_str = '''SELECT DISTINCT game_ids.season
                   FROM gptt INNER JOIN game_ids
                   ON gptt.gid = game_ids.gid
                   WHERE gptt.pid = "%s"''' % \
                   (pid)
    err_spec = "player id has no data associated"
    return(genQuery(query_str, db_path, err_spec))


def fetchPlayerGamesSeason(pid, season, db_path):
    """
    Query and return details for distinct games player "pid"
    participated in (i.e., has stat entry for) in season "season"
    """
    # Build Query
    query_str = '''SELECT DISTINCT gptt.gid, gptt.pid, gptt.team,
                           game_ids.week, game_ids.season, game_ids.date,
                           game_ids.home, game_ids.away
                   FROM gptt INNER JOIN game_ids
                   ON gptt.gid = game_ids.gid
                   WHERE gptt.pid = "%s" AND game_ids.season = "%s"''' % \
                   (pid, season)
    err_spec = "player id %s in season %s" % (pid, season)
    return(genQuery(query_str, db_path, err_spec))


def fetchPlayerEntriesSeason(pid, season, db_path):
    """
    Fetch list of games and stat types for which player has entries in 
    a given year.
    """
    # Build Query
    query_str = '''SELECT gptt.gid, gptt.pid, gptt.team, gptt.ps_table
                   FROM gptt INNER JOIN game_ids
                   ON gptt.gid = game_ids.gid
                   WHERE gptt.pid = "%s" AND game_ids.season = "%s"''' % \
                   (pid, season)
    err_spec = "player id %s in season %s" % (pid, season)
    table = genQuery(query_str, db_path, err_spec)
    if table.shape[0] == 0:
        table = pandas.DataFrame(data=None,
                                 columns=['pid', 'gid', 'team', 'ps_table'])
    return(table)


def fetchPlayerStatsDetails(key_value, key_type, gids, stat_area, db_path):
    """
    Fetch stats of specified type for specified games
    for the specified player
    """
    
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
            
    # Fetch and Return Data
    query_str = '''SELECT * 
                   FROM %s 
                   WHERE %s = :key_value AND gid IN %s''' % \
                   (stat_area, key_type, gids_str)
    query_args = {'key_value' : key_value,}
    err_spec = "stats from '%s' for player id %s" % (stat_area, key_value)
    return(genQuery_dictArgs(query_str, query_args, db_path, err_spec))
##    return(genQuery(query_str, db_path, err_spec))


########
#   These queries deal with the roster / position table
########


def fetchPlayerName(pid, db_path):
    """Given a PID, retrieves the player's name"""
    query_str = '''SELECT name FROM player_info WHERE pid=:pid'''
    query_args = {'pid' : pid}
    err_spec = 'PID %s not found in player info table' % pid
    return(genQuery_dictArgs(query_str, query_args, db_path, err_spec))
    


def fetchPlayerPosition(pid, season, db_path):
    """

    """
    if season == 'NFL - 2015':
        season = 'NFL - 2016'
    query_str = '''SELECT pos FROM roster
                   WHERE pid=:pid AND season=:season'''
    query_args = {'pid' : pid,
                  'season' : season
                  }
    err_spec = 'No entries for player %s for season %s' % (pid, season)
    return(genQuery_dictArgs(query_str, query_args, db_path, err_spec))
    

def fetchPlayerPositions(db_path):
    """
    Return a list of all current player positions in the db;
    assume that these are the same across all seasons
    """
    query_str = '''SELECT DISTINCT pos FROM roster'''
    query_args = {}
    err_spec = ''
    return(genQuery_dictArgs(query_str, query_args, db_path, err_spec))


def fetchPlayersPositionSeason(position, season, db_path):
    """
    For a given position and season, fetch all player IDs,
    """

    if season == 'NFL - 2015':
        season = 'NFL - 2016'
    query_str = '''SELECT name, pid, season FROM roster
                   WHERE pos=:position AND season=:season'''
    query_args = {'position':position, 'season':season}
    err_spec = "no players with position %s in season %s" % (position, season)
    return(genQuery_dictArgs(query_str, query_args, db_path, err_spec))
