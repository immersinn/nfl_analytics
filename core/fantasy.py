

'''
http://games.espn.go.com/ffl/resources/help/content?name=roster-settings-standard

DEFAULT ROSTER SETTINGS
Total Roster Size: 16
Total Starters: 9
Total On Bench: 7 (0 IR)


POSITIONS   STARTERS	MAXIMUM
Quarterback (QB)	1	4
Running Back (RB)	2	8
Flex (RB/WR/TE)	1	N/A
Wide Receiver (WR)	2	8
Tight End (TE)	1	3
Team Defense/Special Teams (D/ST)	1	3
Place-Kicker (K)	1	3
Bench (BE)	7	N/A


http://games.espn.go.com/ffl/resources/help/content?name=scoring-formats


PASSING
Standard scoring: 
· TD Pass = 4pts
· Every 25 passing yards = 1pts
· 2pt Passing Conversion = 2pts
· Interceptions Thrown = -2pts


RUSHING
Standard scoring: 
· TD Rush = 6pts
· Every 10 rushing yards = 1pt
· 2pt Rushing Conversion = 2pts


RECEIVING
Standard scoring: 
· TD Reception = 6pts
· Every 10 receiving yards = 1pt
· 2pt Receiving Conversion = 2pts


MISCELLANEOUS OFFENSE
Standard scoring: 
· Kickoff Return TD = 6pts
· Punt Return TD = 6pts
· Fumble Recovered for TD = 6pts
· Each Fumble Lost = -2


KICKING
Standard scoring:
· FG Made (50+ yards) = 5pts
· FG Made (40-49 yards) = 4pts
· FG Made (0-39 yards) = 3pts
    Not in box score; get from PBP
    
· Each PAT Made = 1pt
· FG Missed (any distance) = -1
    In box score


PUNTING
Standard scoring:
Punters not used in Standard game


INDIVIDUAL DEFENSIVE PLAYERS
Standard scoring:
IDPs not used in Standard game


TEAM DEFENSE / SPECIAL TEAMS (D/ST)
Standard scoring:
· Kickoff Return TD = 6pts
· Punt Return TD = 6pts
· Interception Return TD = 6pts
    All Returns for TD of these types
    are tracked in the box score, separate tables
    
· Fumble Return TD = 6pts
    Not in box score; need to get from pbp
· Blocked Punt or FG return for TD = 6pts
    Not in box score; need to get from pbp
· Blocked Extra Point return for TD = ??pts (new rule..)
    Not in box score; need to get from pbp
    
· Each Interception = 2pts
· Each Fumble Recovered = 2pts
    These are also covered in the defensive box score
    
· Blocked Punt, PAT or FG = 2pts
· Each Safety = 2pts
    Not in box score; need to get from PBP

· Each Sack = 1pts
    Tracked in defensive box score
    
· 0 points allowed = 5pts
· 1-6 points allowed = 4pts
· 7-13 points allowed = 3pts
· 14-17 points allowed = 1pts
· 18-27 points allowed = 0pts
· 28-34 points allowed = -1pts
· 35-45 points allowed = -3pts
· 46+ points allowed = -5pts
    Tracked at level of game; need to associate with defense though


HEAD COACH
Standard scoring:
Head Coaches not used in Standard game
'''

import numpy
import pandas

from sports_data_scraping.espn import nfl_stat_lookups


def convHorm(hORm):
    """Convert T/F value from various form to Python bool"""
    if hORm == b'\x01':
        return(True)
    elif hORm == 'True':
        return(True)
    elif hORm == True:
        return(True)
    else:
        return(False)


def pointsPerGameCalculator(player,):
    if player.position.lower() in ['off', 'qb', 'rb', 'wr', 'te', 'k', 'pk']:
        return(pointsPerGameCalculatorOff(player))
    elif player.position.lower() in ['def', 'd/st']:
        return(pointsPerGameCalculatorDef(player, player.team))
    else:
        err_msg = "Invalid position value"
        raise ValueError(err_msg)


def pointsPerGameCalculatorOff(player,):
    pts_games = []
    for i,game in player.games.iterrows():
        gid = game['gid']
        pts = 0       
        for attr in nfl_stat_lookups.off_areas:
            if hasattr(player, attr):
                data = getattr(player, attr)
                pts += calcPtsOff(data[data.gid==gid],
                               attr)
        
        pts_games.append({'gid' : gid,
                          'points' : pts})
    df = pandas.DataFrame(pts_games)
    return(df)


def pointsPerGameCalculatorDef(player, team=True):
    pts_games = []
    for i,game in player.games.iterrows():
        gid = game['gid']
        pts = 0
        for attr in nfl_stat_lookups.dst_areas:
            if hasattr(player, attr):
                data = getattr(player, attr)
                pts += calcPtsDef(data[data.gid==gid],
                               attr)

        if team:
            pts += scorePointsAllowed(player.points_allowed)
        pts_games.append({'gid' : gid,
                          'points' : pts})
    df = pandas.DataFrame(pts_games)
    return(df)


def calcPtsOff(player, stat_attr):
    lookup_table = \
                 {"ps_passing" : scorePassing,
                  "ps_rushing" : scoreRushing,
                  "ps_receiving" : scoreReceiving,
                  "ps_kicking" : scoreKicking,
                  "ps_punting" : scorePunting,
                  "ps_kick_returns" : scoreKickReturn,
                  "ps_punt_returns" : scorePuntReturn,
                  "ps_fieldgoal_adv" : scoreFGDist,
                  "ps_kicking_adv" : scoreKickingAdv,
                  "ps_punting_adv" : scorePuntingAdv,
                  "ps_interceptions" : scoreInterceptionDef,
                  "ps_fumbles" : scoreFumblesLost,
                  "ps_2ptconv_adv" : score2PtConv
                  }
    return(lookup_table[stat_attr](player))


def calcPtsDef(player, stat_attr):
    lookup_table = \
                 {"ps_kick_returns" : scoreKickReturn,
                  "ps_punt_returns" : scorePuntReturn,
                  "ps_kicking_adv" : scoreKickingAdv,
                  "ps_interceptions" : scoreInterceptionDef,
                  "ps_fumbles" : scoreFumblesRec,
                  "ps_defensive" : scoreDefTable,
                  "ps_blk_kick_adv" : scoreBlocks,
                  "ps_blk_kick_td_adv" : scoreBlocks4TD,
                  "ps_fbl_ret_td_adv" : scoreFumble4TD,
                  "ps_safety_adv" : scoreSafety,
                  }
    return(lookup_table[stat_attr](player))
        

def scorePassing(data):
    """ 4 per TD for ESPN, 6 for CBS"""
    if data.shape[0] > 0:
        pts = sum(data['td']) * 4 + \
              sum([y // 25 for y in list(data['yds'])]) + \
              sum(data['int']) * -2
    else:
        pts = 0
    return(pts)


def scoreRushing(data):
    if data.shape[0] > 0:
        pts = sum(data['td']) * 6 + \
              sum([max(0, y // 10) for y in list(data['yds'])])
    else:
        pts = 0
    return(pts)


def scoreReceiving(data):
    if data.shape[0] > 0:
        pts = sum(data['td']) * 6 + \
              sum([max(0, y // 10) for y in list(data['yds'])])
    else:
        pts = 0
    return(pts)
                      
                      
def scoreKicking(data):
    if data.shape[0] > 0:
        pts = sum(data['xp-made']) + \
              (sum(data['fg-att']) - sum(data['fg-att'])) * -1 + \
              (sum(data['xp-att']) - sum(data['xp-att'])) * -1
    else:
        pts = 0
    return(pts)


def scoreKickingAdv(data):
    pts = 0
    return(pts)


def scoreFGDist(data):
    """
    ESPN Rules:
      FG Made (50+ yards) = 5pts
        has these as 3 on espn for some reason
      FG Made (40-49 yards) = 4pts
        has as 3 on espn
      FG Made (0-39 yards) = 3pts
    """
    def scoreKick(hORm, dist):
        made = convHorm(hORm)
        if made:
            dist = int(dist)
            if dist >= 50:
                return(3)
            elif dist >= 40:
                return(3)
            elif dist > 0:
                return(3)
        else:
            return(0)

    if data.shape[0] > 0:
        pts = data.apply(lambda x : scoreKick(x['make'],
                                              x['dist']),
                         axis=1).sum()
    else:
        pts = 0
    return(pts)


def scorePunting(data):
    # Not currently needed
    return(0)


def scorePuntingAdv(data):
    # Not currently needed
    return(0)


def scoreKickReturn(data):
    if data.shape[0] > 0:
        pts = sum(data['td']) * 6
    else:
        pts = 0
    return(pts)


def scorePuntReturn(data):
    if data.shape[0] > 0:
        pts = sum(data['td']) * 6
    else:
        pts = 0
    return(pts)


def scoreFumblesLost(data):
    if data.shape[0] > 0:
        pts = sum(data['lost']) * -2
    else:
        pts = 0
    return(pts)


def scoreFumblesRec(data):
    if data.shape[0] > 0:
        pts = sum(data['rec']) * 2
    else:
        pts = 0
    return(pts)


def scoreInterceptionDef(data):
    if data.shape[0] > 0:
        pts = sum(data['td']) * 6 + \
              sum(data['int']) * 2
    else:
        pts = 0
    return(pts)


def scoreDefTable(data):
    '''Scoring for data in the Defense Table only'''
    pts = sum(data['sacks']) 
    return(pts)


def scorePointsAllowed(points):
    """
    · 0 points allowed = 5pts
    · 1-6 points allowed = 4pts
    · 7-13 points allowed = 3pts
    · 14-17 points allowed = 1pts
    · 18-27 points allowed = 0pts
    · 28-34 points allowed = -1pts
    · 35-45 points allowed = -3pts
    · 46+ points allowed = -5pts
    """
    pts = 0
    for p in points:
        p = int(p)
        if p > 45:
            pts += -5
        elif p > 35:
            pts += -3
        elif p > 27:
            pts += -1
        elif p > 17:
            pts += 0
        elif p > 14:
            pts += 1
        elif p > 6:
            pts += 3
        elif p > 0:
            pts += 4
        elif p == 0:
            pts += 5
        else:
            err_msg = "Invalid value for 'points'"
            raise ValueError(err_msg)
    return(pts)


def score2PtConv(data):
    """Calculate points from involvement in successful 2pt Conv."""
    if data.shape[0] > 0:
        pts = data.apply(lambda x : int(convHorm(x['make'])) * 2,
                         axis=1).sum()
    else:
        pts = 0
    return(pts)


def scoreBlocks(data):
    """
    Blocked Punt, PAT or FG = 2pts
    """
    pts = data.shape[0] * 2
    return(pts)


def scoreBlocks4TD(data):
    """
    · Blocked Punt or FG return for TD = 6pts
        Not in box score; need to get from pbp
    · Blocked Extra Point return for TD = ??pts (new rule..)
        Not in box score; need to get from pbp
    """
    pts = data.shape[0] * 6
    return(pts)


def scoreFumble4TD(data):
    """
    · Fumble Return TD = 6pts
        Not in box score; need to get from pbp
    """
    pts = data.shape[0] * 6
    return(pts)


def scoreSafety(data):
    """
    · Each Safety = 2pts
        Not in box score; need to get from PBP
    """
    pts = data.shape[0] * 2
    return(pts)
          

          
