

import sqlite3
import pandas
from . import queries as nfl_queries


class Player(object):
    
    def __init__(self, pid,):
        self.pid = pid
        self._openConn()
        
    def _openConn(self,):
        if not (hasattr(self, "_conn") and hasattr(self, "_cursor")):
            self._conn = sqlite3.connect(self._DB_PATH)
            self._cursor = self._conn.cursor()
    
    def _closeConn(self,):
        self._conn.close()
        
    def fetchSeasons(self,):
        pass
    
    
    def fetchStats(self,):
        pass
    
        
    def __enter__(self,):
        # Don't really intend on using this with "with" statements..
        return(self)
        
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # make sure the dbconnection gets closed
        self._closeConn()
        
    def __del__(self,):
        self._closeConn()
    
    
class NFLPlayer(Player):
    
    _DB_PATH = "data/NFLGames"
    _stats_queried = False
    
    def fetchSeasons(self, inplace=True, overwrite=False):
        '''Queries the DB for all Seasons for which the player has
           at least 1 game recorded
        '''
        
        if not overwrite:
            if hasattr(self, "seasons"):
                query = False
            else:
                query = True
        else:
            query = True
            
        if query:
            self.seasons = nfl_queries.fetchPlayerSeasons(self.pid,
                                                          self._cursor)
            
        if not inplace:
            return(self.seasons)
        
        
    def fetchGames(self, seasons=[], inplace=True, overwrite=False):
        '''Queries the DB for all games across all specified seasons in 
           which the player participated (i.e., has a stat entry in at
           least 1 area). If no seasons are provided, the db queries for
           seasons with which the player is associated.
        '''
                   
        if not overwrite:
            if hasattr(self, "games"):
                query = False
            else:
                query = True
        else:
            query = True
            
        if query:
            if not seasons:
                self.fetchSeasons()
                seasons = list(self.seasons.season)

            games = []
            for season in seasons:
                games.append(nfl_queries.fetchPlayerGamesSeason(self.pid,
                                                                season,
                                                                self._cursor))
            games = pandas.concat(games)
            self.games = games
            
        if not inplace:
            return(self.games)
        
        
    def fetchStats(self, seasons=[], overwrite=False):
        '''Queries the DB for all Seasons for which the player has
           at least 1 game recorded
        '''
        
        if not overwrite:
            if self._stats_queried:
                query = False
            else:
                query = True
        else:
            query = True
            
        if query:
            if not seasons:
                self.fetchSeasons()
                seasons = list(self.seasons.season)
                
            stat_entries = []
            for season in seasons:
                stat_entries.append(nfl_queries.fetchPlayerEntriesSeason(self.pid,
                                                                         season,
                                                                         self._cursor))
            stat_entries = pandas.concat(stat_entries)
            
            for sa in pandas.unique(stat_entries.ps_table):
                # Get gids for entries with current sa
                gids = list(pandas.unique(stat_entries[stat_entries.ps_table==sa]['gid']))
                # Set the table as an attribute of the player
                sa = "ps_" + sa.lower()
                setattr(self, sa,
                        nfl_queries.fetchPlayerStatsDetails(self.pid,
                                                            gids,
                                                            sa,
                                                            self._cursor)
                       )
            self._stats_queried = True
