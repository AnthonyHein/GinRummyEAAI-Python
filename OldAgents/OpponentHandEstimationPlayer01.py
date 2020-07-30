# -------------------------------------------------------------------------------
#  OpponentHandEstimationPlayer
#  Implements a random dummy Gin Rummy player that has the same policy as the
#  SimplyGinRummyPlayer except with the following key changes:
#  - Instead of discarding the highest ranking unmelded card, discard a card
#    which is unlikely to produce a meld based on estimation of opponent's hand.
#
#  This estimation will be calculated using a random forrest classifier written
#  by May Jiang.
#
#  @author Anthony Hein
#  @version 1.0
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Copyright (C) 2020 Anthony Hein
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# Information about the GNU General Public License is available online at:
#   http://www.gnu.org/licenses/
# To receive a copy of the GNU General Public License, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
# -------------------------------------------------------------------------------

from typing import List, TypeVar
from random import randint
from GinRummyUtil import GinRummyUtil
from GinRummyPlayer import GinRummyPlayer
from Card import Card

import numpy as np
import dill

CardObj = TypeVar('Card')

class OpponentHandEstimationPlayer(GinRummyPlayer):

    #---------------------------------------------------------------------------
    # FUNCTIONS FOR THE RANDOM FORREST CLASSIFIER

    def _waysCompleteMeld(self, card1, card2):
        ways = 0
        # Run?
        highId = max(card1.getId(), card2.getId())
        lowId = min(card1.getId(), card2.getId())
        if highId - lowId <= 2:
            if highId - lowId == 2:
                ways += self.unavailableCards[(highId + lowId) // 2] == 0 # in between is available
            else:
                if lowId != 0:
                    ways += self.unavailableCards[lowId - 1] == 0 # below is available
                if highId != 51:
                    ways += self.unavailableCards[highId + 1] == 0 # above is available
        # Set?
        if (highId - lowId) % 13 == 0:
            i = lowId + 13
            while i < 52:
                if i != highId:
                    ways += self.unavailableCards[i] == 0 # some set is available
                i += 13
        return ways


    def _predictOpponentHand(rf, state):
        probs = rf.predict_proba([state])
        return np.array(probs)[:,:,1][:,0]

    def _predictCardsT(hand_probs, t):
        return np.array([roundt(p, t) for p in hand_probs])

    def _predictCardsMax(hand_probs):
        inds = hand_probs.argsort()[-10:][::-1]
        ret = np.zeros((52))
        ret[inds] = 1
        return ret
    #---------------------------------------------------------------------------

    def __init__(self):
        # Random Forrest Classifier
        self.rf = dill.load(open("rf.obj","rb"))

    # Inform player of 0-based player number (0/1), starting player number (0/1), and dealt cards
    # @param playerNum player's 0-based player number (0/1)
    # @param startingPlayerNum starting player number (0/1)
    # @param cards dealt cards
    def startGame(self, playerNum: int, startingPlayerNum: int, cards: List[CardObj]) -> None:
        self.playerNum = playerNum
        self.startingPlayerNum = startingPlayerNum
        self.cards = list(cards)
        self.opponentKnocked = False
        self.drawDiscardBitstrings = [] # long[], or List[int]
        self.faceUpCard = None
        self.drawnCard = None

        # Cards discarded and below the top faceup card.
        self.unavailableCards = np.zeros(52)

        # State is array of length 208 made from flattened 4x52 array where
        # row 0 -> past discards (cards opponent discarded)
        # row 1 -> known cards in opponent's hand (picked up by opponent and not discarded)
        # row 2 -> past faceUpCards not picked up by opponent
        # row 3 -> your own hand
        self.state = np.zeros(208)
        self.oppPastDiscards = self.state[0:52]
        self.oppKnownCards = self.state[52:104]
        self.oppRejectFaceUp = self.state[104:156]
        self.ownCards = self.state[156:208]

        # Take note of current cards in hand.
        for card in cards:
            self.ownCards[card.getId()] =  1

    # Return whether or not player will draw the given face-up card on the draw pile.
    # @param card face-up card on the draw pile
    # @return whether or not player will draw the given face-up card on the draw pile
    def willDrawFaceUpCard(self, card: CardObj) -> bool:
        # Return true if card would be a part of a meld, false otherwise.
        self.faceUpCard = card
        newCards = list(self.cards)
        newCards.append(card)
        for meld in GinRummyUtil.cardsToAllMelds(newCards):
            if card in meld:
                return True
        return False

    # Report that the given player has drawn a given card and, if known, what the card is.
    # If the card is unknown because it is drawn from the face-down draw pile, the drawnCard is None.
    # Note that a player that returns false for willDrawFaceUpCard will learn of their face-down draw from this method.
    # @param playerNum - player drawing a card
    # @param drawnCard - the card drawn or null, depending on whether the card is known to the player or not, respectively.
    def reportDraw(self, playerNum: int, drawnCard: CardObj) -> None:
        # Ignore other player draws.  Add to cards if playerNum is this player.
        if playerNum == self.playerNum:
            self.cards.append(drawnCard)
            self.drawnCard = drawnCard
            self.ownCards[drawnCard.getId()] = 1
        else:
            if drawnCard != None:
                self.oppKnownCards[drawnCard.getId()] = 1
            else:
                self.unavailableCards[self.faceUpCard.getId()] = 1
                self.oppRejectFaceUp[self.faceUpCard.getId()] = 1

    # Get the player's discarded card.  If you took the top card from the discard pile,
    # you must discard a different card.
    # If this is not a card in the player's possession, the player forfeits the game.
    # @return the player's chosen card for discarding
    def getDiscard(self) -> CardObj:
        # Discard a random card (not just drawn face up) leaving minimal deadwood points.
        minDeadwood = float('inf')
        candidateCards = np.copy(self.ownCards)
        candidateCards *= 1000

        if self.drawnCard == self.faceUpCard:
            candidateCards[self.drawnCard.getId()] = 0

        bestMeldSets = GinRummyUtil.cardsToBestMeldSets(self.cards)
        if len(bestMeldSets) == 0:
            candidateCards = candidateCards / np.sum(candidateCards)
            discard = np.random.choice(52, 1, p=candidateCards)[0]
            for card in self.cards:
                if discard == card.getId():
                    return card

        # For each best meld set. Find the cards that do not belong to melds.
        for bestMeldSet in bestMeldSets:
            remainingCards = list(self.cards)
            for meldSet in bestMeldSet:
                for card in meldSet:
                    candidateCards[card.getId()] -= 5 # reward card for being in meld
                    remainingCards.remove(card)

            # Now, look at remaining cards pairwise.
            for i in range(len(remainingCards)):
                for j in range(i + 1, len(remainingCards)):
                    card1 = remainingCards[i]
                    card2 = remainingCards[j]
                    ways = self._waysCompleteMeld(card1, card2)
                    candidateCards[[card1.getId(), card2.getId()]] -= ways

        discard = np.argmax(candidateCards)
        for card in self.cards:
            if discard == card.getId():
                return card

    # Report that the given player has discarded a given card.
    # @param playerNum the discarding player
    # @param discardedCard the card that was discarded
    def reportDiscard(self, playerNum: int, discardedCard: CardObj) -> None:
        # Ignore other player discards.  Remove from cards if playerNum is this player.
        self.faceUpCard = discardedCard
        if playerNum == self.playerNum:
            self.cards.remove(discardedCard)
            self.ownCards[discardedCard.getId()] = 0
        else:
            self.oppKnownCards[discardedCard.getId()] = 0
            self.oppPastDiscards[discardedCard.getId()] = 1

    # At the end of each turn, this method is called and the player that cannot (or will not) end the round will return a null value.
    # However, the first player to "knock" (that is, end the round), and then their opponent, will return an ArrayList of ArrayLists of melded cards.
    # All other cards are counted as "deadwood", unless they can be laid off (added to) the knocking player's melds.
    # When final melds have been reported for the other player, a player should return their final melds for the round.
    # @return null if continuing play and opponent hasn't melded, or an ArrayList of ArrayLists of melded cards.
    def getFinalMelds(self) -> List[List[CardObj]]:
        # Check if deadwood of maximal meld is low enough to go out.
        bestMeldSets = GinRummyUtil.cardsToBestMeldSets(self.cards) # List[List[List[Card]]]
        if not self.opponentKnocked and (len(bestMeldSets) == 0 or \
            GinRummyUtil.getDeadwoodPoints1(bestMeldSets[0], self.cards) > \
            GinRummyUtil.MAX_DEADWOOD):
            return None
        if len(bestMeldSets) == 0:
            return []
        return bestMeldSets[randint(0, len(bestMeldSets)-1)]

    # When an player has ended play and formed melds, the melds (and deadwood) are reported to both players.
    # @param playerNum player that has revealed melds
    # @param melds an ArrayList of ArrayLists of melded cards with the last ArrayList (possibly empty) being deadwood.
    def reportFinalMelds(self, playerNum: int, melds: List[List[CardObj]]) -> None:
        # Melds ignored by simple player, but could affect which melds to make for complex player.
        if playerNum != self.playerNum:
            self.opponentKnocked = True

    # Report current player scores, indexed by 0-based player number.
    # @param scores current player scores, indexed by 0-based player number
    def reportScores(self, scores: List[int]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return

    # Report layoff actions.
    # @param playerNum player laying off cards
    # @param layoffCard card being laid off
    # @param opponentMeld the opponent meld that card is being added to
    def reportLayoff(self, playerNum: int, layoffCard: CardObj, opponentMeld: List[CardObj]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return

    # Report the final hands of players.
    # @param playerNum player of hand reported
    # @param hand complete hand of given player
    def reportFinalHand(self, playerNum: int, hand: List[CardObj]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return
