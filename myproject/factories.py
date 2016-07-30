

class PlayerFactory:

    @classmethod
    def makePlayer(Class, pid):
        return(Class.Player(pid))


class GameFactory:

    @classmethod
    def makeGame(Class, gid):
        return(Class.Game(gid))
