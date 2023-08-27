VALID_PLAYER_BEHAVIOR = ['random', 'real', 'ai']
INVALID_PLAYER_BEHAVIOR_EXCEPTION = f"A player's behavior must be one of the following: {VALID_PLAYER_BEHAVIOR}"


class Player:
    def __init__(self, behavior: str = 'random'):
        self._set_behavior(behavior)

        self.hand: [str] = []

    def _set_behavior(self, behavior):
        """The player type can either be 'random,' 'real,' or 'AI'"""
        if behavior not in VALID_PLAYER_BEHAVIOR:
            raise PlayerException(INVALID_PLAYER_BEHAVIOR_EXCEPTION)
        self.behavior = behavior


class PlayerBrain(Player):
    """
    Child object containing all the information gathered by the player agent.
    Used if the player's behavior is 'AI'
    """


class PlayerException(Exception):
    """Exception object for the Player object"""
