from src.tarot.player import Player
from random import choice


def getDecision(player: Player, decision_id: str, options: list[str]) -> str:
    behavior = player.behavior

    if behavior == 'random':
        return choice(options)
    elif behavior == 'real':
        pass
    elif behavior == 'ai':
        pass


