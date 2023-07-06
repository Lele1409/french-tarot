import src.game
import src.utils
import time
import random as rd


def testsAfterPlaying(game):
    nCards = 0
    for n in range(len(game.players)):
        nCards += len(game.players[n].cardsWon)
    assert nCards == 78, print(nCards)
    assert sum(game.wonCardPoints) == 91, print(sum(game.wonCardPoints))


if __name__ == '__main__':
    # Set execution mode to random
    src.game.MODE = 'human'

    GAMES = 0
    while True:
        start = time.perf_counter_ns()  # Single test performance timer start

        # Try running the game if it fails at some point show debug information
        game = src.game.Game(rd.randint(3, 5), lastDealer=rd.randint(0, 3))
        try:
            game.play()
        except Exception as e:
            src.utils.printAllGameFields(game)
            raise e

        singleTime = time.perf_counter_ns() - start  # Single test performance timer end calc
        print(singleTime, GAMES)

        # Run tests
        testsAfterPlaying(game)

        GAMES += 1
