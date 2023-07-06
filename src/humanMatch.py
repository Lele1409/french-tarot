import src.tarot as tarot
import src.humanIO as humanIO

TITLE = """
______    _____               _   
| ___ \  |_   _|             | |  
| |_/ /   _| | __ _ _ __ ___ | |_ 
|  __/ | | | |/ _` | '__/ _ \| __|
| |  | |_| | | (_| | | | (_) | |_ 
\_|   \__, \_/\__,_|_|  \___/ \__|
       __/ |                      
      |___/                       

"""


def startMatch():
    # Init variables
    deck = None
    points = None
    lastDealer = None
    gameEnd = False
    tarot.MODE = 'human'

    # Print the game's title screen
    print(TITLE)

    # Get the desired number of players
    humanIO.printh("Please specify the number of players for the game.")
    humanIO.printh(f"Please enter one of the following options ['3', '4', '5']:")
    players = int(humanIO.inputh())

    # Get names for all the players
    playerNames = []
    for i in range(players):
        humanIO.printh(f"Player {i+1}, what is your name? [entering 'random' will make the player play itself]")
        playerNames.append(humanIO.inputh())

    while not gameEnd:
        # Create game
        runningGame = tarot.Game(players, deck=deck, matchPoints=points, lastDealer=lastDealer)

        # Assign a name to each player in the game
        for player in runningGame.players:
            playerName = playerNames[runningGame.players.index(player)]
            if 'random' in playerName:
                player.rename(f"Player R{runningGame.players.index(player)}")
                player.strategy = 'random'
            else:
                player.rename(playerName)

        # Start the game
        runningGame.play()
        players, deck, points, lastDealer = runningGame.end()

        # Check if player wants to continue playing
        print()
        humanIO.printh("Do you want to start another game?")
        humanIO.printh(f"Please enter one of the following options ['y', 'n']:")
        decision = humanIO.inputh()
        if decision == 'n':
            gameEnd = True

    humanIO.printh("The final points are:")
    for i in range(len(players)):
        humanIO.printh(f"{points[i]}", recipient=players[i].name)


if __name__ == '__main__':
    startMatch()
