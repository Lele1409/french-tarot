# french-tarot

## Game-Flow

### Create Game

#### Define rules:
- Rules as described in [playing section](#Playing)
- Overwrite the rules depending on the variant played:
    - 3 player variant:
        - Cards are dealt four at a time
        - Handfuls, double handfuls and triple handful respectively need 13, 15 and 18 
          trumps
        - If the player taking is short of 1/2 points he misses the contract by one point,
          on the other hand, if he is over by 1/2 points he makes the contract by one 
          point
        - For the score to be zero at the end of the game, the taker's points are 
          multiplied by 2
    - 5 player variant: (assuming the fifth player is indeed playing instead of that
      person exchanging the role of "dead" hence not playing)
        - The dog only contains three cards
        - Before touching the dog, the taker calls a king (if he has all four he can call
          a queen, the same goes for the queen or the knight); he can call himself
        - The first trick cannot be started with a card of the suit of the king called
        - Handfuls, double handfuls and triple handful respectively need 8, 10 and 13 
          trumps
        - If the player taking (together with his partner) is short of 1/2 point, he 
          misses the contract by one point, on the other hand, if he is over by 1/2 point, 
          he makes the contract by one point
        - For the score to be zero at the end of the game, points for the taker and his
          partner are split 2/3 for the taker and 1/3 for his partner assuming he has one,
          otherwise the taker gets 3/3 of the points

### Playing

#### Dealing cards:
- The cards are shuffled before the game starts, but are not shuffled on the following 
  deals
- The dealer is chosen randomly at first, after the role is passed over counter-clockwise
- The player to the left of the dealer left splits the stack at some random point, but
  both resulting stacks must have more than 3 cards, then the stack gets reassembled again
- 3 cards at a time are given to each player in a counter-clockwise order
- The dog:
    - six cards are left to put into the dog
    - not the first card of the deck, not the last card of the deck, not two cards in a 
      row they have to be spaced by 3 cards dealt to a player

#### Choosing a contract
- If none of the players chooses a contract (passes), the cards are put together and 
  re-dealt by the next dealer (person to the right of the original dealer)
- Contracts can be out-bidden by other players, but every player bids only once 
- Starting from the person to the right of the dealer, continuing counter-clockwise 
  ending at the dealer
- All contracts equal or below the current contract cannot be chosen anymore

#### After choosing the contract (and _before the first trick, after the aside_)
- A player can announce a Chelem which he gets if he wins all tricks, the excuse being 
  played only in the last trick (for the Petit au Bout this means that it is in the 
  second to last trick)

#### From the dog to the aside
- All the cards from the dog are shown to all players
- The taker takes the cards into his hand and puts away the same number of cards into his 
  aside
- Kings and trumps cannot be put into the aside, except if a trump has to be put into
  the aside, but it then has to be shown to the Defence
- Depending on the contract (from lowest to highest), the previously defined rules variate 
  a little:
    - "small": normal behavior
    - "guard": normal behavior
    - "guard without the dog": the cards from the dog go automatically into the takers 
  aside, without anyone looking at them
    - "guard against the dog": the cards from the dog go automatically into the Defence's 
  points, without anyone looking at them

#### First trick
- The first player to play is the player to the right of the dealer (if a player has
  called a Chelem, he has to begin wherever he is positioned)
##### Handfuls
- A player wanting to announce a handful can do this before playing his first card
- Handfuls, double handfuls and triple handful respectively need 10, 13 and 15 trumps
- All the cards of a handful must be shown to the other players, in increasing order, 
  including cards that may be in the aside (in case the player has only trumps and kings)
- The excuse can count to the trumps but can only be the last one added to the handful and
  only if there are no other trumps

#### Any trick
- A trick is played counter-clockwise
- If the first card played is of a suit, other players have to play any other card of the
  same suit
- If the first card played is a trump following players have to play a trump of higher
  value than the highest value trump already played in the trick if this is not
  possible, a lower value trump has to be played
- If a player cannot play the suit required he has to play a trump, if the player 
  before him played a trump too, this trump will need to be of higher value than the last
- If a player has no card of the given suit nor a trump, any other card can be played
- If the first card of the trick is the Excuse, the determining card for the trick is 
  the next one
- The Excuse goes back to the player who's played it, but a low-value card has to be 
  given to the opposing team as fast as possible when taking back the card

#### Last trick
- Excuse is not lost if it is the last card played by a player who would be winning a 
  Chelem

### End of the game

#### Determining a winner
- Determine if the taker fulfilled the contract depending on the points needed 
  depending on the oudlers taken

#### Points
- In total, there are 91 points on the cards
- If the Excuse is held by the Defence in case of a Chelem, it is worth 4 points
- The difference of the actual points made and the points needed to get to a win 
  (multiplied by the contracts multiplier _n_ in {1, 2, 4, 6}) plus 25 points make up 
  the points of the taker, them being negative, zero or positive
- To the points of the takers, you have to add or remove points for the handfuls (20, 30 
  or 40 points)
- depending on who won the last trick, and if it contained the Petit, add or remove 10 
  points, multiplied by _n_
- Add points for a possible Chelem 
- The defendants each get this sum
- Those points then have to be multiplied by 3, the number of players in the Defence, 
  resulting in the points for the taker

## Official rules
[Official link](https://www.fftarot.fr/assets/documents/R-RO201206.pdf), french source
by the FFT
