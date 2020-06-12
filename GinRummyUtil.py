#-------------------------------------------------------------------------------
# The following code was originally written by Todd Neller in Java.
# It was translated into Python by Anthony Hein.
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Constants and utilities for Gin Rummy.  Meld checking makes use of bitstring
# representations where a single long value represents a set of cards.  Each
# card has an id number i in the range 0-51, and the presence (1) or absense (0)
# of that card is represented at bit i (the 2^i place in binary). This allows
# fast set difference/intersection/equivalence/etc. operations with bitwise
# operators.
#
# Gin Rummy Rules: https://www.pagat.com/rummy/ginrummy.html
# Adopted variant: North American scoring (25 point bonus for undercut, 25 point bonus for going gin)
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

from Deck import Deck
from Card import Card

class GinRummyUtil:

	# Goal score
	GOAL_SCORE = 100


	# Bonus for melding all cards before knocking
	GIN_BONUS = 25

	# Bonus for undercutting (having less than or equal the deadwood of knocking opponent)
	UNDERCUT_BONUS = 25

	# Maximum deadwood points permitted for knocking
	MAX_DEADWOOD = 10


	# Deadwood points indexed by card rank
	DEADWOOD_POINTS = []

	# Card bitstrings indexed by card id number
	cardBitstrings = []

	# List of lists of meld bitstrings.  Melds appearing after melds in lists are supersets, so the
	# first meld not made in a list makes further checking in that list unnnecessary.
	meldBitstrings = []

	# Map from meld bitstrings to corresponding lists of cards
	meldBitstringToCardsMap = {}

	# initialize DEADWOOD_POINTS
	for rank in range(Deck.NUM_RANKS):
		DEADWOOD_POINTS.append(min(rank + 1, 10))

	# initialize cardBitStrings
	bitstring = 1
	for _ in range(Deck.NUM_CARDS):
		cardBitstrings.append(bitstring)
		bitstring <<= 1

	# build run meld lists
	for suit in range(Deck.NUM_SUITS):
		for runRankStart in range(Deck.NUM_RANKS - 2):
			bitstringList = []
			cards = []
			c = Deck.getCard(rank=runRankStart, suit=suit)
			cards.append(c)
			meldBitstring = cardBitstrings[c.getId()]
			c = Deck.getCard(rank=runRankStart + 1, suit=suit)
			cards.append(c)
			meldBitstring |= cardBitstrings[c.getId()]
			for rank in range(runRankStart + 2, Deck.NUM_RANKS):
				c = Deck.getCard(rank=rank, suit=suit)
				cards.append(c)
				meldBitstring |= cardBitstrings[c.getId()]
				bitstringList.append(meldBitstring)
				meldBitstringToCardsMap.update({meldBitstring : cards.copy()})
			meldBitstrings.append(bitstringList)


	# build set meld lists
	for rank in range(Deck.NUM_RANKS):
		cards = []
		for suit in range(Deck.NUM_SUITS):
			cards.append(Deck.getCard(rank=rank, suit=suit))
		for suit in range(Deck.NUM_SUITS + 1):
			cardSet = cards.copy()
			if suit < Deck.NUM_SUITS:
				cardSet.remove(Deck.getCard(rank=rank, suit=suit))
			bitstringList = []
			meldBitstring = 0
			for card in cardSet:
				meldBitstring |= cardBitstrings[card.getId()]
			bitstringList.append(meldBitstring)
			meldBitstringToCardsMap.update({meldBitstring : cardSet})
			meldBitstrings.append(bitstringList)

	# Given card set bitstring, return the corresponding list of cards
	# @param bitstring card set bitstring
	# @return the corresponding list of cards
	def bitstringToCards(bitstring):
		cards = []
		for i in range(Deck.NUM_CARDS):
			if bitstring % 2 == 1:
				cards.append(Deck.allCards[i])
			bitstring //= 2
		return cards

	# Given a list of cards, return the corresponding card set bitstring
	# @param cards a list of cards
	# @return the corresponding card set bitstring
	def cardsToBitstring(cards):
		bitstring = 0
		for card in cards:
			bitstring |= GinRummyUtil.cardBitstrings[card.getId()]
		return bitstring

	# Given a list of cards, return a list of all meld bitstrings that apply to that list of cards
	# @param cards a list of cards
	# @return a list of all meld bitstrings that apply to that list of cards
	def cardsToAllMeldBitstrings(cards):
		bitstringList = []
		cardsBitstring = GinRummyUtil.cardsToBitstring(cards)
		for meldBitstringList in GinRummyUtil.meldBitstrings:
			for meldBitstring in meldBitstringList:
				if (meldBitstring & cardsBitstring) == meldBitstring:
					bitstringList.append(meldBitstring)
				else:
					break
		return bitstringList

	# Given a list of cards, return a list of all lists of card melds that apply to that list of cards
	# @param cards a list of cards
	# @return a list of all lists of card melds that apply to that list of cards
	def cardsToAllMelds(cards):
		meldList = []
		for meldBitstring in GinRummyUtil.cardsToAllMeldBitstrings(cards):
			meldList.append(GinRummyUtil.bitstringToCards(meldBitstring))
		return meldList

	# Given a list of cards, return a list of all card melds lists to which another meld cannot be added.
	# This corresponds to all ways one may maximally meld, although this doesn't imply minimum deadwood/cards in the sets of melds.
	# @param cards a list of cards
	# @return a list of all card melds lists to which another meld cannot be added
	def cardsToAllMaximalMeldSets(cards):
		maximalMeldSets = []
		meldBitstrings = GinRummyUtil.cardsToAllMeldBitstrings(cards)
		closed = []
		queue = []
		allIndices = []

		for i in range(len(meldBitstrings)):
			meldIndexSet = []
			meldIndexSet.append(i)
			allIndices.append(i)
			queue.append(meldIndexSet)

		while not len(queue) == 0:
			meldIndexSet = sorted(queue.pop(0))
			if meldIndexSet in closed:
				continue
			meldSetBitstring = 0
			for meldIndex in meldIndexSet:
				meldSetBitstring |= meldBitstrings[meldIndex]
			closed.append(meldIndexSet)
			isMaximal = True
			for i in range(len(meldBitstrings)):
				if i in meldIndexSet:
					continue
				meldBitstring = meldBitstrings[i]
				if (meldSetBitstring & meldBitstring) == 0:
					# meld has no overlap with melds in set
					isMaximal = False
					newMeldIndexSet = meldIndexSet.copy()
					newMeldIndexSet.append(i)
					queue.append(newMeldIndexSet)

			if isMaximal:
				cardSets = []
				for meldIndex in meldIndexSet:
					meldBitstring = meldBitstrings[meldIndex]
					cardSets.append(GinRummyUtil.bitstringToCards(meldBitstring))

				maximalMeldSets.append(cardSets)
		return maximalMeldSets

	# Given a list of card melds and a hand of cards, return the unmelded deadwood points for that hand
	# @param melds a list of card melds
	# @param hand hand of cards
	# @return the unmelded deadwood points for that hand
	def getDeadwoodPoints1(melds, hand):
		melded = []
		for meld in melds:
			for card in meld:
				melded.append(card)
		deadwoodPoints = 0
		for card in hand:
			if card not in melded:
				deadwoodPoints += GinRummyUtil.DEADWOOD_POINTS[card.rank]
		return deadwoodPoints


	# Return the deadwood points for an individual given card.
	# @param card given card
	# @return the deadwood points for an individual given card
	def getDeadwoodPoints2(card):
		return GinRummyUtil.DEADWOOD_POINTS[card.rank]

	# Return the deadwood points for a list of given cards.
	# @param cards list of given cards
	# @return the deadwood points for a list of given cards
	def getDeadwoodPoints3(cards):
		deadwood = 0
		for card in cards:
			deadwood += GinRummyUtil.DEADWOOD_POINTS[card.rank]
		return deadwood

	# Returns a list of list of melds that all leave a minimal deadwood count.
	# @param cards
	# @return a list of list of melds that all leave a minimal deadwood count
	# Note: This is actually a "weighted maximum coverage problem". See https://en.wikipedia.org/wiki/Maximum_coverage_problem

	def cardsToBestMeldSets(cards):
		minDeadwoodPoints = 10**8
		maximalMeldSets = GinRummyUtil.cardsToAllMaximalMeldSets(cards)
		bestMeldSets = []
		for melds in maximalMeldSets:
			deadwoodPoints = GinRummyUtil.getDeadwoodPoints1(melds, cards)
			if deadwoodPoints <= minDeadwoodPoints:
				if deadwoodPoints < minDeadwoodPoints:
					minDeadwoodPoints = deadwoodPoints
					bestMeldSets.clear()
				bestMeldSets.append(melds)
		return bestMeldSets

	# Return all meld bitstrings.
	# @return all meld bitstrings
	def getAllMeldBitstrings():
		return GinRummyUtil.meldBitstringToCardsMap.keys()

# Test GinRummyUtils for a given list of cards specified in the first line.
if __name__ == "__main__":
	cardNames = "AD AS AH AC 2C 3C 4C 4H 4D 4S"
	# adding these (impossible in Gin Rummy) causes great combinatorial complexity: 3S 5S 6S 7S 7D 7C 7H 8H 9H TH TC TS TD 9D JD QD KD KS KH KC";
	# cardNames = "AC AH AS 2C 2H 2S 3C 3H 3S KD"
	# cardNames = "AC AH AS 2C 2H 2S 3C 3H 3S 4H"
	cardNameArr = cardNames.split(" ")
	cards = []
	for cardName in cardNameArr:
		cards.append(Deck.strCardMap[cardName])
	print("Hand: " + str(cards))
	print("Bitstring representation as long: " + str(GinRummyUtil.cardsToBitstring(cards)))
	print("All melds: ")
	for meld in GinRummyUtil.cardsToAllMelds(cards):
		print(meld)
	print("Maximal meld sets:")
	for meldSet in GinRummyUtil.cardsToAllMaximalMeldSets(cards):
		print(meldSet)
	print("Best meld sets:")
	for meldSet in GinRummyUtil.cardsToBestMeldSets(cards):
		print(str(GinRummyUtil.getDeadwoodPoints1(meldSet, cards)) + ":" + str(meldSet))
