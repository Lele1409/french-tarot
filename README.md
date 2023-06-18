# french-tarot

## Game-Flow

### Create Game

#### Define rules:
- Rules as described in [playing section](#Playing)
- Overwrite the rules depending on the variant played:
    - 3 player variant:
        - cards are dealt four at a time
        - handfuls, double handfuls and triple handful respectively need 13, 15 and 18 trumps
        - if the player taking is short of 1/2 points he misses the contract by one point,
          on the other hand if he is over by 1/2 points he makes the contract by one point
        - for the score to be zero at the end of the game, the takers points are multiplied
          by 2
    - 5 player variant: (assuming the fifth player is indeed playing instead of that
      person exchanging the role of "dead" hence not playing)
        - the dog only contains three cards
        - before touching the dog, the taker calls a king (if he has all four he can call
          a queen, same goes for the queen or the knight), he can call himself
        - the first trick cannot be started with a card of the suit of the king called
        - handfuls, double handfuls and triple handful respectively need 8, 10 and 13 trumps
        - if the player taking (together with his partner) is short of 1/2 points he misses
          the contract by one point, on the other hand if he is over by 1/2 points he makes
          the contract by one point
        - for the score to be zero at the end of the game, points for the taker and his
          partner are split 2/3 for the taker and 1/3 for his partner assuming he has one,
          otherwise the taker gets 3/3 of the points

#### Create the cards:
- represented in form of a list of 78 integers, each integer ranging from 1
  to 78 is a CardId
- allows to display the actual CardName to the user via a translation layer where each
  CardId is associated to a CardName containing a description of its suit and its name

### Playing

#### Dealing cards:
- The cards are shuffled before the game starts, but are not shuffled on following deals
- The dealer is chosen randomly at first, after the role is passed over counter-clockwise
- The player to the left of the dealer left splits the stack at some random point but both
  resulting stacks must have more than 3 cards, then the stack gets reassembled again
- Cards are dealt counter-clockwise
- 3 cards at a time are given to each player in a counter-clockwise order
- the dog:
    - six cards are left to put into the dog
    - not the first card of the deck, not the last card of the deck, not to cards in a 
      row they have to be spaced by 3 cards dealt to a player

#### Choosing a contract
- if none of the players chooses a contract (passes) the cards are put together and 
  re-dealt by the next dealer (person to the right of the original dealer)
- contracts can be outbidden by other players, but every player bids only once 
- starting from the person to the right of the dealer, continuing counter-clockwise 
  ending at the dealer
- all contracts equal or below the current contract cannot be choosen anymore
- if someone chooses a "guarde against the dog" this person is automatically the taker 
  as no one can outbid him anymore

#### After choosing the contract (and _before the first trick?/before the aside?_)
- a player can announce a Chelem which he gets if he wins all tricks, the excuse being 
  played only in the last trick (for the Petit au Bout this means that it is in the 
  second to last trick)

#### From the dog to the aside
- all the cards from the dog are shown to all players
- the taker takes the cards into his hand and puts away the same number of cards into his 
  aside
- depending on the contract (from lowest to highest):
  - "small": normal behaviour
  - "guard": normal behaviour
  - "guard without the dog": the cards from the dog go automatically into the takers 
    aside, without anyone looking at them
  - "guard against the dog": the cards from the dog go automatically into the Defenses 
    points, without anyone looking at them
- kings and trumps cannot be put into the aside, except if a trump has to be put into 
  the aside, but it then has to be shown to the Defense

#### Any trick
- a trick is played counter-clockwise

#### First trick
- the first player to play is the player to the right of the dealer
- a player wanting to announce a handful can do this before playing his first card, 
  handfuls, double handfuls and triple handful respectively need 10, 13 and 15 trumps, 
  all the cards of a handful must be shown to the other players including cards that 
  may be in the aside (in case the player has only trumps and kings)

#### Last trick
- Excuse is lost if played in this trick, except if it is the last card played by a player
  who has announced a Chelem

### End of the game

#### Determining a winner
- Determine if the contract was fulfilled by the taker depending on the points needed 
  depending on the oudlers taken

#### Points
- In total there are 91 points

## Official rules
[Official link](https://www.fftarot.fr/assets/documents/R-RO201206.pdf), french source
by the FFT
