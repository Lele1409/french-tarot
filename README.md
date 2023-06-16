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
- The dealer is chosen randomly, the player to his left splits the stack at some
  random point but both resulting stacks must have more than 3 cards, then the stack
  gets reassembled again
- Cards are dealt counter-clockwise
- 3 at a time
- the dog:
    - six cards are left to put into the dog
    -

#### Announcing Contracts

#### Any trick

#### First trick

#### Last trick
- Excuse is lost if played in this trick

### End of the game

#### Determining a winner
- Determine if the contract was fulfilled by the taker

#### Points
- In total there are 91 points

## Rules
[Official link](https://www.fftarot.fr/assets/documents/R-RO201206.pdf), french source
by the FFT
