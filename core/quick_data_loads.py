

import numpy
import pandas

from nfl_analytics.core import players as nfl_players
from nfl_analytics.core import fantasy as nfl_fantasy
from nfl_analytics.core import queries as nfl_queries


positions = ['QB', 'WR', 'RB', 'TE', 'K', 'PK']
db_path = 'data/NFLGames'

# Teams Info
abrv_name_lookup, name_city_lookup = \
    nfl_queries.fetchTeamsLookupData('NFL - 2015', 'data/NFLGames')


def updateAddFields(ppg_dfs):
    # Add full player names
    ### TO DO

    # Add additional info about home, away
    def determineOpponent(row):
        if row['is_home']==True:
            return(row['away_full'])
        else:
            return(row['home_full'])

    ppg_dfs['home_full'] = [abrv_name_lookup[n.lower()] for n in ppg_dfs.home]
    ppg_dfs['away_full'] = [abrv_name_lookup[n.lower()] for n in ppg_dfs.away]
    ppg_dfs['is_home'] = [hf==t for (hf, t) in \
                          zip(ppg_dfs.home_full, ppg_dfs.team)]
    ppg_dfs['opponent'] = ppg_dfs.apply(lambda x: determineOpponent(x), axis=1)

    return(ppg_dfs)


def fix_season(season):
    """Temp fix for season - roster discrepency
    """
    if season == 'NFL - 2016':
        return('NFL - 2015')
    else:
        return(season)


def flattenDataSub(sub_df):
    data = sub_df.to_dict()
    flat_data = {}
    for k,val in data.items():
        if k not in ['season', 'team', 'pid']:
            for w,v in enumerate(val.values()):
                flat_data[k + '_' + str(w)] = v
        else:
            flat_data[k] = list(val.values())[0]
    return(flat_data)


def flattenDataSubs(data, window):
    flat_data = []
    for start in range(0,data.shape[0]-window):
        flat_data.append(flattenDataSub(data.ix[start:(start+window)]))
    flat_data = pandas.DataFrame(flat_data)
    return(flat_data)


def flattenPlayerData(player, window=3):
    ppg_df = player.ppg
    ppg_df.index = range(ppg_df.shape[0])
    ppg_df = updateAddFields(ppg_df)
    reduced = ppg_df[['points', 'team', 'pid', 'opponent', 'is_home', 'season', 'week']]
    flat_data = flattenDataSubs(reduced, window)
    return(flat_data)


def fetch_preprocess_qb_data_ppg():
    return(fetchfetchPrepSeasonPosition(position='QB',
                                        season='NFL - 2015',
                                        cutoff=7,
                                        db_path='data/NFLGames'))


def fetchPrepSeasonPosition(position, season, cutoff, db_path='data/NFLGames'):

    # Load and filter
    player_df = nfl_queries.fetchPlayersPositionSeason(pos=position,
                                                       season=season,
                                                       db_path=db_path)
    players = [nfl_players.NFLPlayerSeason(pid=pid, season=season) \
               for pid in player_df.pid]
    for p in players:
        p.prep()
    players = [p for p in players if p.ppg.shape[0] > cutoff]

    # Merge all ppgs into single df
    ppg_dfs = pandas.concat([p.ppg for p in players])
    ppg_dfs = ppg_dfs.reset_index()
    ppg_dfs.week = [int(w) for w in ppg_dfs.week]
    ppg_dfs = updateAddFields(ppg_dfs)

    return(ppg_dfs)


def fetchPrepSeasonsPositions(positions, seasons, cutoff, db_path='data/NFLGames'):

    # Create players, retrieve player data
    player_dfs = []
    for position in positions:
        for season in seasons:
            player_dfs.append(nfl_queries.fetchPlayersPositionSeason(position=position,
                                                                     season=season,
                                                                     db_path=db_path)
                              )
    player_df = pandas.concat(player_dfs)
    players = [nfl_players.NFLPlayerSeason(pid=pid, season=fix_season(season)) \
               for (pid,season) in zip(list(player_df.pid),
                                       list(player_df.season))]
    for p in players:
        p.prep()
    players = [p for p in players if p.ppg.shape[0] > cutoff]

    return(players)


def fetch_prep_data_nn(rolling_weeks=3,
                       positions=['QB'],
                       seasons=['NFL - 2015'],
                       cutoff=7,
                       db_path='data/NFLGames'):

    # Fetch and Prep Players
    players = fetchPrepSeasonsPositions(positions=positions,
                                        seasons=seasons,
                                        cutoff=cutoff)
    
    # Transform data for training
    flat_data = []
    for player in players:
        flat_data.append(flattenPlayerData(player,
                                           window=rolling_weeks))
    flat_data = pandas.concat(flat_data)

    return(flat_data)


class NNWindowedDataPrep():

    def __init__(self,):
        pass

    def fit(self, X, y=None):
        # 1) One-hot on all team data
        #    a) all opponents
        #    b) "team"
        # 2) True-False to 1/0
        # 3) Ordinal for "seaso"n
        pass

    def transform(self, X):
        pass

    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))
