#-------------------------------------------------------------------------------
# The following code was originally written by Todd Neller in Java.
# It was translated into Python by Anthony Hein.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# A class for modeling a game of Gin Rummy
# @author Todd W. Neller
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

import random
import time
from Deck import Deck
from GinRummyUtil import GinRummyUtil
from SimpleGinRummyPlayer import SimpleGinRummyPlayer
from OpponentHandEstimationPlayer import OpponentHandEstimationPlayer

import csv
import numpy as np

#-------------------------------------------------------------------------------
# TRACKING
# import numpy as np
# tracking_states = []
# tracking_states2 = []
# tracking_hands = []
#
# def one_hot(cards):
#     ret = np.zeros(52)
#     for card in cards:
#         ret[card.getId()] = 1
#     return ret
#
# def un_one_hot(arr):
#     rankNames = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
#     suitNames = ["C", "H", "S", "D"]
#     ret = []
#     for i in range(len(arr)):
#         if arr[i] != 0:
#             ret.append(rankNames[i%13] + suitNames[i//13])
#     return ret
#-------------------------------------------------------------------------------

class GinRummyGame:

    # Hand size (before and after turn). After draw and before discard there is one extra card.
    HAND_SIZE = 10;

    # Whether or not to print information during game play
    playVerbose = False;

    # Two Gin Rummy players numbered according to their array index.
    players = [];

    # Set whether or not there is to be printed output during gameplay.
    # @param playVerbose whether or not there is to be printed output during gameplay
    def setPlayVerbose(playVerbose):
        GinRummyGame.playVerbose = playVerbose

    # Create a GinRummyGame with two given players
    # @param player0 Player 0
    # @param player1 Player 1
    def __init__(self, player0, player1):
        GinRummyGame.players.extend([player0, player1])

    # Play a game of Gin Rummy and return the winning player number 0 or 1.
    # @return the winning player number 0 or 1
    def play(self):
        scores = [0, 0]
        hands = []
        hands.extend([[], []])

        startingPlayer = random.randrange(2);

        # while game not over
        while scores[0] < GinRummyUtil.GOAL_SCORE and scores[1] < GinRummyUtil.GOAL_SCORE:

            currentPlayer = startingPlayer
            opponent = (1 if currentPlayer == 0 else 0)

            # get shuffled deck and deal cards
            deck = Deck.getShuffle(random.randrange(10 ** 8))
            hands[0] = []
            hands[1] = []
            for i in range(2 * GinRummyGame.HAND_SIZE):
                hands[i % 2] += [deck.pop()]
            for i in range(2):
                GinRummyGame.players[i].startGame(i, startingPlayer, hands[i]);
                if GinRummyGame.playVerbose:
                    print("Player %d is dealt %s.\n" % (i, hands[i]))
            if GinRummyGame.playVerbose:
                print("Player %d starts.\n" % (startingPlayer))
            discards = []
            discards.append(deck.pop())
            if GinRummyGame.playVerbose:
                print("The initial face up card is %s.\n" % (discards[len(discards) - 1]))
            firstFaceUpCard = discards[len(discards) - 1]
            turnsTaken = 0
            knockMelds = None

            # tracking_pastdiscards = {0: np.zeros(52), 1:  np.zeros(52)}
            # tracking_pastpickups = {0: np.zeros(52), 1:  np.zeros(52)}
            # tracking_pastnonpickups = {0: np.zeros(52), 1:  np.zeros(52)}
            # while the deck has more than two cards remaining, play round
            while len(deck) > 2:
                # DRAW
                drawFaceUp = False
                faceUpCard = discards[len(discards) - 1]

                # offer draw face-up iff not 3rd turn with first face up card (decline automatically in that case)
                if not (turnsTaken == 2 and faceUpCard == firstFaceUpCard):
                    # both players declined and 1st player must draw face down
                    drawFaceUp = GinRummyGame.players[currentPlayer].willDrawFaceUpCard(faceUpCard)
                    if GinRummyGame.playVerbose and not drawFaceUp and faceUpCard == firstFaceUpCard and turnsTaken < 2:
                        print("Player %d declines %s.\n" % (currentPlayer, firstFaceUpCard))

                if not (not drawFaceUp and turnsTaken < 2 and faceUpCard == firstFaceUpCard):
                    # continue with turn if not initial declined option
                    drawCard = discards.pop() if drawFaceUp else deck.pop()
                    for i in range(2):
                        to_report = drawCard if i == currentPlayer or drawFaceUp else None
                        GinRummyGame.players[i].reportDraw(currentPlayer, to_report)
                        # TRACKING
                        # if i != currentPlayer: # player i is tracking currentPlayer
                        #     if drawFaceUp:
                        #         tracking_pastpickups[i][faceUpCard.getId()] = 1
                        #     else:
                        #         tracking_pastnonpickups[i][faceUpCard.getId()] = 1
                    if GinRummyGame.playVerbose:
                        print("Player %d draws %s.\n" % (currentPlayer, drawCard))
                    hands[currentPlayer].append(drawCard)

                    # DISCARD
                    discardCard = GinRummyGame.players[currentPlayer].getDiscard()
                    if not discardCard in hands[currentPlayer] or discardCard == faceUpCard:
                        print("Player %d discards %s illegally and forfeits.\n" % (currentPlayer, discardCard))
                        return opponent;

                    hands[currentPlayer].remove(discardCard)
                    for i in range(2):
                        GinRummyGame.players[i].reportDiscard(currentPlayer, discardCard)
                        # TRACKING
                        # if i != currentPlayer: # player i is tracking currentPlayer
                        #     tracking_pastdiscards[i][discardCard.getId()] = 1
                        #     tracking_pastpickups[i][discardCard.getId()] = 0
                        #     tracking_hand = one_hot(GinRummyGame.players[currentPlayer].cards)
                        #     tracking_hand[discardCard.getId()] = 0
                        #     tracking_hands.append(tracking_hand)
                        #     tracking_states.append(np.array([tracking_pastdiscards[i], tracking_pastpickups[i], tracking_pastnonpickups[i]]))
                        #     tracking_states2.append(np.array([tracking_pastdiscards[i], tracking_pastpickups[i], tracking_pastnonpickups[i], one_hot(GinRummyGame.players[i].cards)]))
                    if GinRummyGame.playVerbose:
                        print("Player %d discards %s.\n" % (currentPlayer, discardCard))
                    discards.append(discardCard)
                    if GinRummyGame.playVerbose:
                        unmeldedCards = hands[currentPlayer].copy()
                        bestMelds = GinRummyUtil.cardsToBestMeldSets(unmeldedCards)
                        if len(bestMelds) == 0:
                            print("Player %d has %s with %d deadwood.\n" % (currentPlayer, unmeldedCards, GinRummyUtil.getDeadwoodPoints3(unmeldedCards)))
                        else:
                            melds = bestMelds[0]
                            for meld in melds:
                                for card in meld:
                                    unmeldedCards.remove(card)
                            melds.extend(unmeldedCards)
                            print("Player %d has %s with %d deadwood.\n" % (currentPlayer, melds, GinRummyUtil.getDeadwoodPoints3(unmeldedCards)))

                    # CHECK FOR KNOCK
                    knockMelds = GinRummyGame.players[currentPlayer].getFinalMelds()
                    if knockMelds != None:
                        # player knocked; end of round
                        break

                turnsTaken += 1
                currentPlayer = 1 if currentPlayer == 0 else 0
                opponent = 1 if currentPlayer == 0 else 0

            if knockMelds != None:
                # round didn't end due to non-knocking and 2 cards remaining in draw pile
                # check legality of knocking meld
                handBitstring = GinRummyUtil.cardsToBitstring(hands[currentPlayer])
                unmelded = handBitstring
                for meld in knockMelds:
                    meldBitstring = GinRummyUtil.cardsToBitstring(meld)
                    if (not meldBitstring in GinRummyUtil.getAllMeldBitstrings()) or ((meldBitstring & unmelded) != meldBitstring):
                        # non-meld or meld not in hand
                        print("Player %d melds %s illegally and forfeits.\n" % (currentPlayer, knockMelds))
                        return opponent
                    unmelded &= ~meldBitstring # remove successfully melded cards from

                # compute knocking deadwood
                knockingDeadwood = GinRummyUtil.getDeadwoodPoints1(knockMelds, hands[currentPlayer])
                if knockingDeadwood > GinRummyUtil.MAX_DEADWOOD:
                    print("Player %d melds %s with greater than %d deadwood and forfeits.\n" % (currentPlayer, knockMelds, knockingDeadwood))
                    return opponent

                meldsCopy = []
                for meld in knockMelds:
                    meldsCopy.append(meld.copy())
                for i in range(2):
                    GinRummyGame.players[i].reportFinalMelds(currentPlayer, meldsCopy)
                if GinRummyGame.playVerbose:
                    if knockingDeadwood > 0:
                        print("Player %d melds %s with %d deadwood from %s.\n" % (currentPlayer, knockMelds, knockingDeadwood, GinRummyUtil.bitstringToCards(unmelded)))
                    else:
                        print("Player %d goes gin with melds %s.\n" % (currentPlayer, knockMelds))

                # get opponent meld
                opponentMelds = GinRummyGame.players[opponent].getFinalMelds();
                meldsCopy = []
                for meld in opponentMelds:
                    meldsCopy.append(meld.copy())
                for i in range(2):
                    GinRummyGame.players[i].reportFinalMelds(opponent, meldsCopy)

                # check legality of opponent meld
                opponentHandBitstring = GinRummyUtil.cardsToBitstring(hands[opponent])
                opponentUnmelded = opponentHandBitstring
                for meld in opponentMelds:
                    meldBitstring = GinRummyUtil.cardsToBitstring(meld)
                    if (meldBitstring not in GinRummyUtil.getAllMeldBitstrings()) or ((meldBitstring & opponentUnmelded) != meldBitstring):
                        # non-meld or meld not in hand
                        print("Player %d melds %s illegally and forfeits.\n" % (opponent, opponentMelds))
                        return currentPlayer
                    opponentUnmelded &= ~meldBitstring # remove successfully melded cards from

                if GinRummyGame.playVerbose:
                    print("Player %d melds %s.\n" % (opponent, opponentMelds))

                # lay off on knocking meld (if not gin)
                unmeldedCards = GinRummyUtil.bitstringToCards(opponentUnmelded)
                if knockingDeadwood > 0:
                    # knocking player didn't go gin
                    cardWasLaidOff = False
                    while True:
                        # attempt to lay each card off
                        cardWasLaidOff = False
                        layOffCard = None
                        layOffMeld = None
                        for card in unmeldedCards:
                            for meld in knockMelds:
                                newMeld = meld.copy()
                                newMeld.append(card)
                                newMeldBitstring = GinRummyUtil.cardsToBitstring(newMeld)
                                if newMeldBitstring in GinRummyUtil.getAllMeldBitstrings():
                                    layOffCard = card
                                    layOffMeld = meld
                                    break
                            if layOffCard != None:
                                if GinRummyGame.playVerbose:
                                    print("Player %d lays off %s on %s.\n" % (opponent, layOffCard, layOffMeld))
                                for i in range(2):
                                    GinRummyGame.players[i].reportLayoff(opponent, layOffCard, layOffMeld.copy())
                                unmeldedCards.remove(layOffCard)
                                layOffMeld.append(layOffCard)
                                cardWasLaidOff = True
                                break
                        if not cardWasLaidOff:
                            break

                opponentDeadwood = 0
                for card in unmeldedCards:
                    opponentDeadwood += GinRummyUtil.getDeadwoodPoints2(card)
                if GinRummyGame.playVerbose:
                    print("Player %d has %d deadwood with %s\n" % (opponent, opponentDeadwood, unmeldedCards))

                # compare deadwood and compute new scores
                if knockingDeadwood == 0:
                    # gin round win
                    scores[currentPlayer] += GinRummyUtil.GIN_BONUS + opponentDeadwood
                    if GinRummyGame.playVerbose:
                        print("Player %d scores the gin bonus of %d plus opponent deadwood %d for %d total points.\n" % \
                        (currentPlayer, GinRummyUtil.GIN_BONUS, opponentDeadwood, GinRummyUtil.GIN_BONUS + opponentDeadwood))

                elif knockingDeadwood < opponentDeadwood:
                    # non-gin round win:
                    scores[currentPlayer] += opponentDeadwood - knockingDeadwood;
                    if GinRummyGame.playVerbose:
                        print("Player %d scores the deadwood difference of %d.\n" % (currentPlayer, opponentDeadwood - knockingDeadwood))

                else:
                    # undercut win for opponent
                    scores[opponent] += GinRummyUtil.UNDERCUT_BONUS + knockingDeadwood - opponentDeadwood;
                    if GinRummyGame.playVerbose:
                        print("Player %d undercuts and scores the undercut bonus of %d plus deadwood difference of %d for %d total points.\n" % \
                        (opponent, GinRummyUtil.UNDERCUT_BONUS, knockingDeadwood - opponentDeadwood, GinRummyUtil.UNDERCUT_BONUS + knockingDeadwood - opponentDeadwood))

                startingPlayer = 1 if startingPlayer == 0 else 0 # starting player alternates

            # If the round ends due to a two card draw pile with no knocking, the round is cancelled.
            else:
                if GinRummyGame.playVerbose:
                    print("The draw pile was reduced to two cards without knocking, so the hand is cancelled.")

            # report final hands
            for i in range(2):
                for j in range(2):
                    GinRummyGame.players[i].reportFinalHand(j, hands[j].copy())

            # score reporting
            if GinRummyGame.playVerbose:
                print("Player\tScore\n0\t%d\n1\t%d\n" % (scores[0], scores[1]))
            for i in range(2):
                GinRummyGame.players[i].reportScores(scores.copy())

        if GinRummyGame.playVerbose:
            print("Player %s wins.\n" % (0 if scores[0] > scores[1] else 1))
        return 0 if scores[0] >= GinRummyUtil.GOAL_SCORE else 1


# Test and demonstrate the use of the GinRummyGame class.
if __name__ == "__main__":

    GinRummyGame.setPlayVerbose(False)
    player = OpponentHandEstimationPlayer()
    game = GinRummyGame(SimpleGinRummyPlayer(), player)

    with open('results02.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        while True:

            low = float(input("Low "))
            high = float(input("High "))
            space = int(input("Space "))
            numGames = int(input("Num "))

            lst = np.linspace(low,high,space).tolist()

            for alpha in lst:
                numP1Wins = 0
                print("Playing with alpha: " + str(alpha), end="")
                player.setAlpha(alpha)
                for i in range(numGames):
                    numP1Wins += game.play()
                print(", Win Rate: " + str(numP1Wins / numGames))
                csvwriter.writerow([alpha, numP1Wins / numGames])
