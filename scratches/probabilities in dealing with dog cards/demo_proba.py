import random

analysis = {}

for _ in range(50000):

    deck = [i for i in range(78)]
    players_card = []
    dog = []
    # while len(deck) > 0:
    #     x = random.randint(1, 8)
    #     if (x == 1 or len(deck) == (3-len(dog))*4) \
    #             and not len(deck) == 78 \
    #             and not len(deck) == 1 \
    #             and not len(dog) == 3:
    #         dog.append(deck.pop())
    #     else:
    #         for _ in range(3):
    #             players_card.append(deck.pop())

    dog_cards = [False for _ in range(int((78 - 6) / 3 + 6))]
    while dog_cards.count(True) < 6:
        dog_cards[random.randint(1, len(dog_cards) - 2)] = True

    for state in dog_cards:
        if state:
            dog.append(deck.pop())
        else:
            for _ in range(3):
                players_card.append(deck.pop())

    for card in dog:
        try:
            analysis[card] += 1
        except KeyError:
            analysis[card] = 1

for key, value in analysis.items():
    print(key, ",", value)
