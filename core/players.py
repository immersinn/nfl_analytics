

import pandas
from . import queries as nfl_queries
from . import fantasy as nfl_fantasy


class PlayerSeason(object):

    ptype = 'PLAYER'
    

    def __init__(self, pid, season):
        self.pid = pid
        self.season = season


    def fetchName(self,):
        self.name = list(self.queries.fetchPlayerName(self.pid,
                                                      self._DB_PATH).ix[0])[0]


    def fetchPosition(self,):
        self.position = list(self.queries.fetchPlayerPosition(self.pid,
                                                              self.season,
                                                              self._DB_PATH).ix[0])[0]


    def fetchGames(self, overwrite=False):
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
            games = []
            games.append(self.queries.fetchPlayerGamesSeason(self.pid,
                                                             self.season,
                                                             self._DB_PATH))
            games = pandas.concat(games)
            self.games = games


    def fetchStatEntries(self, overwrite=False):

        query = True    
        if query:
            stat_entries = self.queries.fetchPlayerEntriesSeason(self.pid,
                                                                 self.season,
                                                                 self._DB_PATH)
            self.stat_entries = stat_entries
        
        
        
    def fetchStats(self, overwrite=False):
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
            for sa in pandas.unique(self.stat_entries.ps_table):
                # Get gids for entries with current sa
                gids = list(pandas.unique(self.stat_entries\
                                          [self.stat_entries.ps_table==sa]\
                                          ['gid']
                                          )
                            )
                # Set the table as an attribute of the player
                key_type = 'pid'
                if self.ptype=="TEAM":
                    if sa.endswith('_adv'):
                        key_type = 'team'
                setattr(self, sa,
                        self.queries.fetchPlayerStatsDetails(self.pid,
                                                             key_type,
                                                             gids,
                                                             sa,
                                                             self._DB_PATH)
                       )
            self._stats_queried = True


    def calcPPG(self,):
        ppg = self.fantasy.pointsPerGameCalculator(player=self)
        df = ppg.merge(self.games)
        df = df.sort_values(by='date')
        self.ppg = df
    
    
class NFLPlayerSeason(PlayerSeason):
    
    _DB_PATH = "data/NFLGames"
    _stats_queried = False
    queries = nfl_queries
    fantasy = nfl_fantasy


    def prep(self,):
        self.fetchName()
        self.fetchPosition()
        self.fetchGames()
        self.fetchStatEntries()
        self.fetchStats()
        self.calcPPG()


class NFLDefenseSeason(NFLPlayerSeason):

    ptype = 'TEAM'


    def fetchPIDs(self,):
        """
        Provided a team name, queries the roster table to determine all defensive
        special teams players on the team.  These players' PIDs arr then associated
        with the Team Defensive Player instance.
        """
        pass


    def fetchName(self,):
        self.name = self.pid


    def fetchPosition(self,):
        self.team = False
        self.position = 'D/ST'



class Player(object):

    
    def __init__(self, pid,):
        self.pid = pid


        
    def fetchSeasons(self, overwrite=False):
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
            self.seasons = self.queries.fetchPlayerSeasons(self.pid,
                                                           self._DB_PATH)
            

    def fetchGames(self, seasons=[], overwrite=False):
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
                games.append(self.queries.fetchPlayerGamesSeason(self.pid,
                                                                 season,
                                                                 self._DB_PATH))
            games = pandas.concat(games)
            self.games = games
            
        
        
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
                stat_entries.append(self.queries.fetchPlayerEntriesSeason(self.pid,
                                                                          season,
                                                                          self._DB_PATH))
            stat_entries = pandas.concat(stat_entries)
            
            for sa in pandas.unique(stat_entries.ps_table):
                # Get gids for entries with current sa
                gids = list(pandas.unique(stat_entries[stat_entries.ps_table==sa]['gid']))
                # Set the table as an attribute of the player
                setattr(self, sa,
                        self.queries.fetchPlayerStatsDetails(self.pid,
                                                             gids,
                                                             sa,
                                                             self._DB_PATH)
                       )
            self._stats_queried = True


    def calcPoints(self,):
        self.fetchStats()
        return(self.fantasy.pointsCalculator(self,))

    
