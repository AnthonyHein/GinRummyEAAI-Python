package ginrummy;

import java.util.ArrayList;
import java.util.Random;
import org.tensorflow.Graph;
import org.tensorflow.Session;
import org.tensorflow.Tensor;
import org.tensorflow.TensorFlow;
import org.tensorflow.SavedModelBundle;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.util.HashMap;


/**
 * Implements a random dummy Gin Rummy player that has the following trivial, poor play policy:
 * Ignore opponent actions and cards no longer in play.
 * Draw face up card only if it becomes part of a meld.  Draw face down card otherwise.
 * Discard a highest ranking unmelded card without regard to breaking up pairs, etc.
 * Knock as early as possible.
 *
 * @author Todd W. Neller
 * @version 1.0

Copyright (C) 2020 Todd Neller

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Information about the GNU General Public License is available online at:
  http://www.gnu.org/licenses/
To receive a copy of the GNU General Public License, write to the Free
Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
02111-1307, USA.

 */

public class NFSPPlayer implements GinRummyPlayer {
    // Agent
    protected Graph graph;
    protected Session sess;

    // Player management
	protected int playerNum;
	@SuppressWarnings("unused")
	protected int startingPlayerNum;

    // Player state
	protected ArrayList<Card> cards = new ArrayList<Card>();
    protected int action;

    // Board management
	protected boolean opponentKnocked = false;
	protected Card faceUpCard, drawnCard;
	protected ArrayList<Long> drawDiscardBitstrings = new ArrayList<Long>();
    protected HashMap<String, Object> state;

    // ====================================
    // Action_ids:
    //        0 -> score_player_0_id
    //        1 -> score_player_1_id
    //        2 -> draw_card_id
    //        3 -> pick_up_discard_id
    //        4 -> declare_dead_hand_id
    //        5 -> gin_id
    //        6 to 57 -> discard_id card_id
    //        58 to 109 -> knock_id card_id
    // ====================================

    // DON'T TOUCH THIS --------------------------------------------------------
    public HashMap<String, Object> initGameGetState() {
        // Create state map.
        HashMap<String, int[]> state = new HashMap<String, int[]>();

        // Create hand array.
        state.put("hand", new int[52]);

        // Mark cards in hand.
        int[] hand = state.get("hand");
        for (Card card : this.cards) {
            hand[card.getId()] = 1;
        }

        // Create space for other parameters.
        state.put("topDiscard", new int[52]);
        state.put("deadCards", new int[52]);
        state.put("opponentKnownCards", new int[52]);

        // Compile representation of observations.
        int[][] obs = { state.get("hand"),
                        state.get("topDiscard"),
                        state.get("deadCards"),
                        state.get("opponentKnownCards")};

        // Created Extracted State.
        HashMap<String, Object> extractedState = new HashMap<String, Object>();
        extractedState.put("obs", obs);
        extractedState.put("legalActions", null);

        return extractedState;

    }

    public int getStateIndex(String label) {
        if (label.equals("hand")) {
            return 0;
        }
        else if (label.equals("topDiscard")) {
            return 1;
        }
        else if (label.equals("deadCards")) {
            return 2;
        }
        else if (label.equals("opponentKnownCards")) {
            return 3;
        }
        else {
            throw new ArrayIndexOutOfBoundsException("Unknown label.");
        }
    }

    public void setDiscard(Card card) {
        int[] newTopDiscard = new int[52];
        newTopDiscard[card.getId()] = 1;
        ((int[][]) this.state.get("obs"))[getStateIndex("topDiscard")] = newTopDiscard;
    }
    // -------------------------------------------------------------------------

	@Override
	public void startGame(int playerNum, int startingPlayerNum, Card[] cards) {
        // Basic stuff.
        this.playerNum = playerNum;
		this.startingPlayerNum = startingPlayerNum;
		this.cards.clear();
		for (Card card : cards)
			this.cards.add(card);
		this.opponentKnocked = false;
		this.drawDiscardBitstrings.clear();
        hthis.faceUpCard = null;
        this.drawnCard = null;
        this.action = null;

        this.state = self.initGameGetState();

        // Load Saved Model.
        this.graph = new Graph();
        Path modelPath = Paths.get("saved_graph_file");
        byte[] graphDefBytes = Files.readAllBytes(modelPath);
        this.graph.importGraphDef(graphDefBytes);

        // Create a session
        this.sess = new Session(this.graph);
	}

	@Override
	public boolean willDrawFaceUpCard(Card card) {
		// Return true if card would be a part of a meld, false otherwise.
		this.faceUpCard = card;
		@SuppressWarnings("unchecked")
		ArrayList<Card> newCards = (ArrayList<Card>) cards.clone();
		newCards.add(card);
		for (ArrayList<Card> meld : GinRummyUtil.cardsToAllMelds(newCards))
			if (meld.contains(card))
				return true;
		return false;
	}

	@Override
	public void reportDraw(int playerNum, Card drawnCard) {
		// Ignore other player draws.  Add to cards if playerNum is this player.
		if (playerNum == this.playerNum) {
			cards.add(drawnCard);
			this.drawnCard = drawnCard;
		}
	}

	@SuppressWarnings("unchecked")
	@Override
	public Card getDiscard() {
		// Discard a random card (not just drawn face up) leaving minimal deadwood points.
		int minDeadwood = Integer.MAX_VALUE;
		ArrayList<Card> candidateCards = new ArrayList<Card>();
		for (Card card : cards) {
			// Cannot draw and discard face up card.
			if (card == drawnCard && drawnCard == faceUpCard)
				continue;
			// Disallow repeat of draw and discard.
			ArrayList<Card> drawDiscard = new ArrayList<Card>();
			drawDiscard.add(drawnCard);
			drawDiscard.add(card);
			if (drawDiscardBitstrings.contains(GinRummyUtil.cardsToBitstring(drawDiscard)))
				continue;

			ArrayList<Card> remainingCards = (ArrayList<Card>) cards.clone();
			remainingCards.remove(card);
			ArrayList<ArrayList<ArrayList<Card>>> bestMeldSets = GinRummyUtil.cardsToBestMeldSets(remainingCards);
			int deadwood = bestMeldSets.isEmpty() ? GinRummyUtil.getDeadwoodPoints(remainingCards) : GinRummyUtil.getDeadwoodPoints(bestMeldSets.get(0), remainingCards);
			if (deadwood <= minDeadwood) {
				if (deadwood < minDeadwood) {
					minDeadwood = deadwood;
					candidateCards.clear();
				}
				candidateCards.add(card);
			}
		}
		Card discard = candidateCards.get(random.nextInt(candidateCards.size()));
		// Prevent future repeat of draw, discard pair.
		ArrayList<Card> drawDiscard = new ArrayList<Card>();
		drawDiscard.add(drawnCard);
		drawDiscard.add(discard);
		drawDiscardBitstrings.add(GinRummyUtil.cardsToBitstring(drawDiscard));
		return discard;
	}

	@Override
	public void reportDiscard(int playerNum, Card discardedCard) {
		// Ignore other player discards.  Remove from cards if playerNum is this player.
		if (playerNum == this.playerNum)
			cards.remove(discardedCard);
	}

	@Override
	public ArrayList<ArrayList<Card>> getFinalMelds() {
		// Check if deadwood of maximal meld is low enough to go out.
		ArrayList<ArrayList<ArrayList<Card>>> bestMeldSets = GinRummyUtil.cardsToBestMeldSets(cards);
		if (!opponentKnocked && (bestMeldSets.isEmpty() || GinRummyUtil.getDeadwoodPoints(bestMeldSets.get(0), cards) > GinRummyUtil.MAX_DEADWOOD))
			return null;
		return bestMeldSets.isEmpty() ? new ArrayList<ArrayList<Card>>() : bestMeldSets.get(random.nextInt(bestMeldSets.size()));
	}

	@Override
	public void reportFinalMelds(int playerNum, ArrayList<ArrayList<Card>> melds) {
		// Melds ignored by simple player, but could affect which melds to make for complex player.
		if (playerNum != this.playerNum)
			opponentKnocked = true;
	}

	@Override
	public void reportScores(int[] scores) {
		// Ignored by simple player, but could affect strategy of more complex player.
	}

	@Override
	public void reportLayoff(int playerNum, Card layoffCard, ArrayList<Card> opponentMeld) {
		// Ignored by simple player, but could affect strategy of more complex player.

	}

	@Override
	public void reportFinalHand(int playerNum, ArrayList<Card> hand) {
		// Ignored by simple player, but could affect strategy of more complex player.
	}

}
