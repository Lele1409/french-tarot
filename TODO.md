- [ ] Login/SignUp:
  - [ ] Sign up:
    - [ ] Check for valid username and password
    - [ ] Save username and password-hash to DB
  - [ ] Login:
    - [ ] Send credentials to server for login attempt


- [ ] Lobby:
  - [ ] Gen match_id for Lobby
  - [ ] Create a room on the webserver for client-server communication through websockets
  - [ ] Other players can join the lobby with the match_id
  - [ ] Other non-human players can be added (AI, random)
  - [ ] Can set match settings :
    - [ ] Nb of games, (any defined in rules?) (option: infinite, with possibility to 
          end after each game)
    - [ ] Turn-timer
  - [ ] Start match button, launching the match


- [ ] Match:
  - [ ] Prepare first game :
    - [ ] Create shuffled deck
    - [ ] Create players
    - [ ] Choose starting player
  - [ ] Run game
  - [ ] After any game:
    - [ ] Return deck in order 
    - [ ] Add game score to match score (broadcast to players)


- [ ] Game: (refer to rules-synthesis.md)
  - [ ] Deal cards
  - [ ] Choose contract (if none chosen: re-deal cards)
  - [ ] Show dog (dependong of contract)
  - [ ] Dog to hand/aside (depending on contract)
  - [ ] Taking player creates his aside (depending on contract)
  - [ ] Taking player calls another player (if 5 players)
  - [ ] Play tricks:
    - [ ] If first game: every player can call a handful
    - [ ] every player plays card (apply rules)
    - [ ] determine trick winner, player who will play first the next round


- [ ] Player:
  - [ ] Add a brain to the player, telling him what he knows, (which cards he has seen 
    already) (_for use in AI_)


- [ ] Webpage:
  - [ ] Lock pages to which non-logged in users don't have access
