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
	meldBitstrings

    # Map from meld bitstrings to corresponding lists of cards
	meldBitstringToCardsMap;

	# initialize DEADWOOD_POINTS
    for _ in range(Deck.NUM_RANKS):
        DEADWOOD_POINTS += [min(rank + 1, 10)]

	# initialize cardBitStrings
	bitstring = 1
    for _ in range(Deck.NUM_CARDS):
		cardBitstrings += [bitstring]
		bitstring <<= 1

	# build list of lists of meld bitstring where each subsequent meld bitstring
    # in the list is a superset of previous meld bitstrings
	meldBitstrings = [];
	meldBitstringToCardsMap = {};

	# build run meld lists
    for suit in range(Deck.NUM_SUITS):
        for runRankStart in range(Deck.NUM_RANKS - 2):
            bitstringList = []
            cards = []
            c = Deck.getCard(numRankStart, suit)
            cards.append(c)
            meldBitstring = cardBitstrings[c.getId()]
            c = Deck.getCard(runRankStart + 1, suit)
            cards.append(c)
            meldBitstring |= cardBitstrings[c.getId()]
            for rank in range(runRankStart + 2, Deck.NUM_RANKS):
                c = Deck.getCard(rank, suit)
                cards.append(c)
                meldBitstring |= cardBitstrings[c.getId()]
                bitstringList.append(meldBitstring)
                meldBitstringToCardsMap.update({meldBitstring : cards.copy()})
            meldBitstrings.append(bitstringList)


	# build set meld lists
    for rank in range(Deck.NUM_RANKS):
        cards = []
        for suit in range(Deck.NUM_SUITS):
            cards.append(Deck.getCard(rank, suit))
        for suit in range(Deck.NUM_SUITS + 1):
            cardSet = cards.copy()
            if suit < Deck.NUM_SUITS:
                cardSet.remove(Deck.getCard(rank, suit))
            bitstringList = []
            meldBitstring = 0
            for card in cardSet:
                meldBitstring |= cardBitStrings[card.getId()]
            bitstringList.append(meldBitstring)
            meldBitstringToCardsMap.update({meldBitstring : cardSet})
            meldBitstrings.append(bitstringList)

	# Given card set bitstring, return the corresponding list of cards
	# @param bitstring card set bitstring
	# @return the corresponding list of cards
	bitstringToCards(Long bitstring) {
		ArrayList<Card> cards = new ArrayList<Card>();
		for (int i = 0; i < Card.NUM_CARDS; i++) {
			if (bitstring % 2 == 1)
				cards.add(Card.allCards[i]);
			bitstring /= 2;
		}
		return cards;
	}

	/**
	 * Given a list of cards, return the corresponding card set bitstring
	 * @param cards a list of cards
	 * @return the corresponding card set bitstring
	 */
	public static long cardsToBitstring(ArrayList<Card> cards) {
		long bitstring = 0L;
		for (Card card : cards)
			bitstring |= cardBitstrings[card.getId()];
		return bitstring;
	}

	/**
	 * Given a list of cards, return a list of all meld bitstrings that apply to that list of cards
	 * @param cards a list of cards
	 * @return a list of all meld bitstrings that apply to that list of cards
	 */
	public static ArrayList<Long> cardsToAllMeldBitstrings(ArrayList<Card> cards) {
		ArrayList<Long> bitstringList = new ArrayList<Long>();
		long cardsBitstring = cardsToBitstring(cards);
		for (ArrayList<Long> meldBitstringList : meldBitstrings)
			for (long meldBitstring : meldBitstringList)
				if ((meldBitstring & cardsBitstring) == meldBitstring)
					bitstringList.add(meldBitstring);
				else
					break;
		return bitstringList;
	}

	/**
	 * Given a list of cards, return a list of all lists of card melds that apply to that list of cards
	 * @param cards a list of cards
	 * @return a list of all lists of card melds that apply to that list of cards
	 */
	public static ArrayList<ArrayList<Card>> cardsToAllMelds(ArrayList<Card> cards) {
		ArrayList<ArrayList<Card>> meldList = new ArrayList<ArrayList<Card>>();
		for (long meldBitstring : cardsToAllMeldBitstrings(cards))
			meldList.add(bitstringToCards(meldBitstring));
		return meldList;
	}

	/**
	 * Given a list of cards, return a list of all card melds lists to which another meld cannot be added.
	 * This corresponds to all ways one may maximally meld, although this doesn't imply minimum deadwood/cards in the sets of melds.
	 * @param cards a list of cards
	 * @return a list of all card melds lists to which another meld cannot be added
	 */
	public static ArrayList<ArrayList<ArrayList<Card>>> cardsToAllMaximalMeldSets(ArrayList<Card> cards) {
		ArrayList<ArrayList<ArrayList<Card>>> maximalMeldSets = new ArrayList<ArrayList<ArrayList<Card>>>();
		ArrayList<Long> meldBitstrings = cardsToAllMeldBitstrings(cards);
		HashSet<HashSet<Integer>> closed = new HashSet<HashSet<Integer>>();
		Queue<HashSet<Integer>> queue = new LinkedList<HashSet<Integer>>();
		HashSet<Integer> allIndices = new HashSet<Integer>();
		for (int i = 0; i < meldBitstrings.size(); i++) {
			HashSet<Integer> meldIndexSet = new HashSet<Integer>();
			meldIndexSet.add(i);
			allIndices.add(i);
			queue.add(meldIndexSet);
		}
		while (!queue.isEmpty()) {
			HashSet<Integer> meldIndexSet = queue.poll();
//			System.out.println(meldSet);
			if (closed.contains(meldIndexSet))
				continue;
			long meldSetBitstring = 0L;
			for (int meldIndex : meldIndexSet)
				meldSetBitstring |= meldBitstrings.get(meldIndex);
			closed.add(meldIndexSet);
			boolean isMaximal = true;
			for (int i = 0; i < meldBitstrings.size(); i++) {
				if (meldIndexSet.contains(i))
					continue;
				long meldBitstring = meldBitstrings.get(i);
				if ((meldSetBitstring & meldBitstring) == 0) { // meld has no overlap with melds in set
					isMaximal = false;
					HashSet<Integer> newMeldIndexSet = (HashSet<Integer>) meldIndexSet.clone();
					newMeldIndexSet.add(i);
					queue.add(newMeldIndexSet);
				}
			}
			if (isMaximal) {
				ArrayList<ArrayList<Card>> cardSets = new ArrayList<ArrayList<Card>>();
				for (int meldIndex : meldIndexSet) {
					long meldBitstring  = meldBitstrings.get(meldIndex);
					cardSets.add(bitstringToCards(meldBitstring));
				}
				maximalMeldSets.add(cardSets);
			}
		}
		return maximalMeldSets;
	}

	/**
	 * Given a list of card melds and a hand of cards, return the unmelded deadwood points for that hand
	 * @param melds a list of card melds
	 * @param hand hand of cards
	 * @return the unmelded deadwood points for that hand
	 */
	public static int getDeadwoodPoints(ArrayList<ArrayList<Card>> melds, ArrayList<Card> hand) {
		HashSet<Card> melded = new HashSet<Card>();
		for (ArrayList<Card> meld : melds)
			for (Card card : meld)
				melded.add(card);
		int deadwoodPoints = 0;
		for (Card card : hand)
			if (!melded.contains(card))
				deadwoodPoints += DEADWOOD_POINTS[card.rank];
		return deadwoodPoints;
	}

	/**
	 * Return the deadwood points for an individual given card.
	 * @param card given card
	 * @return the deadwood points for an individual given card
	 */
	public static int getDeadwoodPoints(Card card) {
		return DEADWOOD_POINTS[card.rank];
	}

	/**
	 * Return the deadwood points for a list of given cards.
	 * @param cards list of given cards
	 * @return the deadwood points for a list of given cards
	 */
	public static int getDeadwoodPoints(ArrayList<Card> cards) {
		int deadwood = 0;
		for (Card card : cards)
			deadwood += DEADWOOD_POINTS[card.rank];
		return deadwood;
	}

	/**
	 * Returns a list of list of melds that all leave a minimal deadwood count.
	 * @param cards
	 * @return a list of list of melds that all leave a minimal deadwood count
	 */
	// Note: This is actually a "weighted maximum coverage problem". See https://en.wikipedia.org/wiki/Maximum_coverage_problem
	public static ArrayList<ArrayList<ArrayList<Card>>> cardsToBestMeldSets(ArrayList<Card> cards) {
		int minDeadwoodPoints = Integer.MAX_VALUE;
		ArrayList<ArrayList<ArrayList<Card>>> maximalMeldSets = cardsToAllMaximalMeldSets(cards);
		ArrayList<ArrayList<ArrayList<Card>>> bestMeldSets = new ArrayList<ArrayList<ArrayList<Card>>>();
		for (ArrayList<ArrayList<Card>> melds : maximalMeldSets) {
			int deadwoodPoints = getDeadwoodPoints(melds, cards);
			if (deadwoodPoints <= minDeadwoodPoints) {
				if (deadwoodPoints < minDeadwoodPoints) {
					minDeadwoodPoints = deadwoodPoints;
					bestMeldSets.clear();
				}
				bestMeldSets.add(melds);
			}
		}
		return bestMeldSets;
	}

	/**
	 * Return all meld bitstrings.
	 * @return all meld bitstrings
	 */
	public static Set<Long> getAllMeldBitstrings() {
		return meldBitstringToCardsMap.keySet();
	}

	/**
	 * Test GinRummyUtils for a given list of cards specified in the first line.
	 * @param args (unused)
	 */
	public static void main(String[] args) {
		String cardNames = "AD AS AH AC 2C 3C 4C 4H 4D 4S"; // adding these (impossible in Gin Rummy) causes great combinatorial complexity: 3S 5S 6S 7S 7D 7C 7H 8H 9H TH TC TS TD 9D JD QD KD KS KH KC";
//		String cardNames = "AC AH AS 2C 2H 2S 3C 3H 3S KD";
//		String cardNames = "AC AH AS 2C 2H 2S 3C 3H 3S 4H";

		String[] cardNameArr = cardNames.split(" ");
		ArrayList<Card> cards = new ArrayList<Card>();
		for (String cardName : cardNameArr)
			cards.add(Card.strCardMap.get(cardName));
		System.out.println("Hand: " + cards);
		System.out.println("Bitstring representation as long: " + cardsToBitstring(cards));
		System.out.println("All melds:");
		for (ArrayList<Card> meld : cardsToAllMelds(cards))
			System.out.println(meld);
		System.out.println("Maximal meld sets:");
		for (ArrayList<ArrayList<Card>> meldSet : cardsToAllMaximalMeldSets(cards))
			System.out.println(meldSet);
		System.out.println("Best meld sets:");
		for (ArrayList<ArrayList<Card>> meldSet : cardsToBestMeldSets(cards))
			System.out.println(getDeadwoodPoints(meldSet, cards) + ":" + meldSet);
	}

}
