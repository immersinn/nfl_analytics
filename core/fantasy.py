

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
· Each PAT Made = 1pt
· FG Missed (any distance) = -1


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
· Fumble Return TD = 6pts
· Blocked Punt or FG return for TD = 6pts
· Each Interception = 2pts
· Each Fumble Recovered = 2pts
· Blocked Punt, PAT or FG = 2pts
· Each Safety = 2pts
· Each Sack = 1pts
· 0 points allowed = 5pts
· 1-6 points allowed = 4pts
· 7-13 points allowed = 3pts
· 14-17 points allowed = 1pts
· 18-27 points allowed = 0pts
· 28-34 points allowed = -1pts
· 35-45 points allowed = -3pts
· 46+ points allowed = -5pts


HEAD COACH
Standard scoring:
Head Coaches not used in Standard game
'''


class Team(object):

    def __init__(self,):
        self._players = []
        self._active = []


    def addPlayer(self,):
        pass


def pointsCalculator(player,):
    if player.position in ['off', 'qb', 'rb', 'wr', 'te', 'k']:
        return(pointsCalculatorOff(player))
    elif player.position in ['def', 'd/st']:
        return(pointsCalculatorDef(player, player.team))
    else:
        err_msg = "Invalid position value"
        raise ValueError(err_msg)


def pointsCalculatorOff(player, ):
    pts = 0       
    if hasattr(player, "ps_passing"):
        pts += scorePassing(player.ps_passing)
    if hasattr(player, "ps_rushing"):
        pts += scoreRushing(player.ps_rushing)
    if hasattr(player, "ps_receiving"):
        pts += scoreReceiving(player.ps_receiving)
    if hasattr(player, "ps_fumbles"):
        pts += scoreFumbleLoss(player.ps_fumbles)
    if hasattr(player, "ps_kicking_adv"):
        pts += scoreKicking(player.ps_kicking_adv)
    return(pts)
    

def pointsCalculatorDef(defense_team, team=True):
    pts = scoreKickReturn(defense_team.ps_kick_returns) + \
          scorePuntReturn(defense_team.ps_punt_returns) + \
          scoreInterceptions(defense_team.ps_interceptions) + \
          scoreFumblesRec(defense_team.ps_fumbles) + \
          scoreDefenseGeneral(defense_team.ps_defensive) + \
          0 # blocks; safety
    if team:
          pts += scorePointsAllowed(defense_team.points_allowed)
    return(pts)


def scorePassing(data):
    pts = sum(data['td']) * 4 + \
          sum([y // 25 for y in list(data['yds'])]) + \
          sum(data['int']) * -2 + \
          0  # data['2pt'] * 2
    return(pts)


def scoreRushing(data):
    pts = sum(data['td']) * 6 + \
          sum([y // 10 for y in list(data['yds'])]) + \
          0 # data['2pt'] * 2
    return(pts)


def scoreReceiving(data):
    pts = sum(data['td']) * 6 + \
          sum([y // 10 for y in list(data['yds'])]) + \
          0 # data['2pt'] * 2
    return(pts)


def scoreKicking(data):
    pts = sum(data['xp-made']) + \
          (sum(data['fg-att']) - sum(data['fg-att'])) * -1 + \
          (sum(data['xp-att']) - sum(data['xp-att'])) * -1 + \
          0 # get fg distances an update this
    return(pts)


def scorePunting(data):
    # Not currently needed
    return(0)


def scoreKickReturn(data):
    pts = sum(data['td']) * 6
    return(pts)


def scorePuntReturn(data):
    pts = sum(data['td']) * 6
    return(pts)


def scoreFumbleLoss(data):
    pts = sum(data['lost']) * -2
    return(pts)


def scoreFumblesRec(data):
    pts = sum(data['rec']) * 2 + \
          0 #sum(data['td']) * 6 + \
    return(pts)


def scoreInterceptions(data):
    pts = sum(data['td']) * 6 + \
          sum(data['int']) * 2
    return(pts)


def scoreDefenseGeneral(data):
    '''Scoring for data in the Defense Table only'''
    pts = sum(data['sacks']) + \
          0 # should safety, blocks go here?
    return(pts)


def scorePointsAllowed(points):
    for p in points:
        if p > 45:
            pts = -5
        elif p > 35:
            pts = -3
        elif p > 27:
            pts = -1
        elif p > 17:
            pts = 0
        elif p > 14:
            pts = 1
        elif p > 6:
            pts = 3
        elif p > 0:
            pts = 4
        elif p == 0:
            pts = 5
        else:
            err_msg = "Invalid value for 'points'"
            raise ValueError(err_msg)
    return(pts)

          
          

          
