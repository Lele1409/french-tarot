# **OLD**

# SYNTHESIS


First, we launch the server.
Each time a lobby gets opened, the lobby gets opened in a newly created process. We also add a pipe to this new 
process for "bilateral" communication between the game (decision layer) and server.

_Note: the following part is for real-players (AI-players are handled differently and random decisions just send back 
one randomly chosen option)_

The game runs the code it needs, and when a decision has to be made by a player, the game sends a decision_request to
the server.
The server will (if not already occupied with handling something else) periodically check if there are any other 
decision_requests in the queue and send out these requests to the clients for them to return a decision. If a player does
decide, his decision gets received by the server who sends it back through the pipe to the game that initiated the 
request.
Then the loop repeats.



# IN DETAIL / PER FILE

### src\run.py / src\main.py _(name TBD)_
Start the server

### src\server\server.py
Whenever a user wants to create a lobby, the server will create a new process.
This new process will get a Pipe object:
 - The one end stays with the server, where it is put in a dictionary together with accompagning information about the 
 match,
 - The other end will (through the lobby object) be passed to the match's constructor

(Asynchronously?) the server will be cycling over all pipes in the dictionary defined previously and check for new 
decision_requests.

### src\tarot\match.py
The match object holds the other end of the pipe. The game can then whenever needed ask for a decision through the 
decision layer.

### src\decision\decision.py
When the game needs a decision, the decision layer creates a decision_request object. This object contains information
on the player that has to take the decision, and the decision itself (for example which options exist).
It then puts this object into the queue and waits for a taken_decision to return to the game.
