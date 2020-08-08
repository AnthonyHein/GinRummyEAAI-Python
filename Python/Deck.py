#-------------------------------------------------------------------------------
# Deck.py was created to address translation problems between Java and Python.
# It represents a standard deck of cards.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Author: Anthony Hein
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Please see the related Card.py file.
#-------------------------------------------------------------------------------

from Card import Card
import random
from sys import stderr, exit

class Deck:

    # An array of all unique Card objects.
    allCards = []

    # Array of abbreviated card rank names in ascending order of rank.
    rankNames = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

    # Array of abbreviated card suit names indexed by suit index.
    suitNames = ["C", "H", "S", "D"]

    # Parallel array to suitNames indicating whether or not the corresponding suit is red.
    isSuitRed = [False, True, False, True]

    # Number of card ranks.
    NUM_RANKS = len(rankNames)

    # Number of card suits.
    NUM_SUITS = len(suitNames)

    # Total number of cards.
    NUM_CARDS = NUM_RANKS * NUM_SUITS

    # Map from String representations to Card objects.
    strCardMap = {}

    # Map from String representations to Card id numbers.
    strIdMap = {}

    # Map from Card id numbers to String representations.
    idStrMap = {}

    # Create all cards and initialize static maps.
    for s in range(NUM_SUITS):
        for r in range(NUM_RANKS):
            c = Card(r, s)
            allCards += [c]
            strCardMap[str(c)] = c
            strIdMap[str(c)] = c.getId()
            idStrMap[c.getId()] = str(c)

    # Get a Deck of cards without a shuffle
    # @return a deck of cards in standard order
    def getDeck():
        return Deck.allCards

    # Get the Card object corresponding to the given Card id number (0 - 51)
    # @param id Card id number (0 - 51)
    # @param rank index
    # @param suit index
    # @return corresponding Card object
    def getCard(id=-1, rank=-1, suit=-1):
        if id >= 0:
            return Deck.allCards[id]
        elif rank >= 0 and suit >= 0:
            return Deck.allCards[suit * Deck.NUM_RANKS + rank]
        else:
            print("ERROR: bad parameters to getCard in Deck class.", file=stderr)
            exit(1)

    # Get the Card id number corresponding to the given rank and suit indices
    # @param rank rank index
    # @param suit suit index
    # @return corresponding Card id number
    def getId(rank, suit):
        return suit * Deck.NUM_RANKS + rank

    # Return a Stack deck of Cards corresponding to the given shuffle seed number
    # @param seed shuffle seed number
    # @return corresponding Stack deck of Cards
    def getShuffle(seed):
        deck = []
        random.seed(seed)
        for i in range(Deck.NUM_CARDS):
            deck += [Deck.allCards[i]]
        random.shuffle(deck)
        return deck

# Unit testing.
# Show shuffle seed 5742.
if __name__ == "__main__":
    print("\nStandard deck:\n")
    deck = Deck.getDeck()
    for i in range(Deck.NUM_CARDS):
        print(str(deck[i]) + ("\n" if (i + 1) % Deck.NUM_RANKS == 0 else " "), end="")

    print("\nDeck with shuffle seed 5742:\n")
    deck = Deck.getShuffle(5742)
    for i in range(Deck.NUM_CARDS):
        print(str(deck[i]) + ("\n" if (i + 1) % Deck.NUM_RANKS == 0 else " "), end="")

    print("\nGet the 2 of spades:\n")
    print("getCard(id=37):\t\t", str(Deck.getCard(id=27)))
    print("getCard(rank=1, suit=2):", str(Deck.getCard(rank=1, suit=2)))
    print("getId(1, 2):\t\t", Deck.getId(1,2))
