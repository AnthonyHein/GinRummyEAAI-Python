#-------------------------------------------------------------------------------
# The following code was originally written by Todd Neller in Java.
# It was translated into Python by Anthony Hein.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Please see the related Deck.py file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# A class for representing standard (French) playing cards.
# Rank numbers are 0 through 12, corresponding to possible rank names:
#   "A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K".
#
# Suit numbers are 0 through 3, corresponding to possible suit names:
#   "C", "H", "S", "D".  Note that suit colors alternate.
#
# The __str__ method for each card will be the concatenation of a rank name with a suit name.
#
# It's possible to go between 4 different card representations using this class:
# (1) Card object representation
# (2) String representation
# (3) single integer representation (0 - 51)
# (4) two integer (rank, suit) representation
#
# _Avoid the construction of new Card objects._
# Use the Card objects already created in allCards, retrieving them via
# (1) strCardMap using the method get(String),
# (2) getCard(int), or
# (3) getCard(int rank, int suit).
#
# @author Todd W. Neller, translated to Python by Anthony Hein
# @version 1.0
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Copyright (C) 2020 Todd Neller
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Information about the GNU General Public License is available online at:
#   http://www.gnu.org/licenses/
# To receive a copy of the GNU General Public License, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#-------------------------------------------------------------------------------

class Card:

    # Array of abbreviated card rank names in ascending order of rank.
    rankNames = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

    # Array of abbreviated card suit names indexed by suit index.
    suitNames = ["C", "H", "S", "D"]

    # Number of card ranks.
    NUM_RANKS = len(rankNames)

    # Number of card suits.
    NUM_SUITS = len(suitNames)

    # Total number of cards.
    NUM_CARDS = NUM_RANKS * NUM_SUITS

    # Constructor to create a card object with the corresponding zero-based indices to rankNames and suitNames, respectively.
    # AVOID USE IF POSSIBLE.  Use the Card objects already created in allCards, retrieving them via
    # (1) strCardMap using the method get(String),
    # (2) getCard(int), or
    # (3) getCard(int rank, int suit).
    # @param rank rank of card (zero-based index to rankNames)
    # @param suit suit of card (zero-based index to suitNames)
    def __init__(self, rank, suit):
       # rank index (zero-based index to rankNames)
    	self.rank = rank

        # suit index (zero-based index to suitNames)
    	self.suit = suit

    # Get rank of card (zero-based index to rankNames).
    # @return rank of card (zero-based index to rankNames)
    def getRank(self):
    	return self.rank

    # Get suit of card (zero-based index to suitNames).
    # @return suit of card (zero-based index to suitNames)
    def getSuit(self):
    	return self.suit

    # Return whether or not the card is Red.
    # @return whether or not the card is Red
    def isRed(self):
    	return self.suit % 2 == 1

    # Return the Card id number.
    # @return the Card id number
    def getId(self):
    	return self.suit * Card.NUM_RANKS + self.rank

    # Return card representation as a string.
    def __str__(self):
    	return Card.rankNames[self.rank] + Card.suitNames[self.suit]

    def __repr__(self):
        return Card.rankNames[self.rank] + Card.suitNames[self.suit]


# Unit testing.
if __name__ == "__main__":
    print("\nAll cards:\n")
    allCards = []
    for s in range(Card.NUM_SUITS):
        for r in range(Card.NUM_RANKS):
            c = Card(r, s)
            print(str(c) + ("\n" if r == Card.NUM_RANKS - 1 else " "), end="")
            allCards += [c]

    print("\nLowest-valued card:\n")
    print("getRank:\t", allCards[0].getRank())
    print("getSuit:\t", allCards[0].getSuit())
    print("isRed:\t\t", allCards[0].isRed())
    print("getId:\t\t", allCards[0].getId())
    print("__str__:\t", str(allCards[0]))

    print("\nHighest-valued card:\n")
    print("getRank:\t", allCards[Card.NUM_CARDS - 1].getRank())
    print("getSuit:\t", allCards[Card.NUM_CARDS - 1].getSuit())
    print("isRed:\t\t", allCards[Card.NUM_CARDS - 1].isRed())
    print("getId:\t\t", allCards[Card.NUM_CARDS - 1].getId())
    print("__str__:\t", str(allCards[Card.NUM_CARDS - 1]))
