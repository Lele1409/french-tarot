from src.tarot.player import Player
from random import choice


def get_decision(player: Player, decision_id: str, options: list[str]) -> str:
    behavior = player.behavior

    if behavior == 'random':
        chosen_card = choice(options)
        return chosen_card
    if behavior == 'real':
        pass
    if behavior == 'ai':
        pass
