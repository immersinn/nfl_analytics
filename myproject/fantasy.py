

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



def scorePassing(data):
    pts = data['td'] * 4 + \
          data['yds'] // 25 + \
          data['int'] * -2 + \
          0  # data['2pt'] * 2

    return(pts)
