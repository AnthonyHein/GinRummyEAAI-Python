# -------------------------------------------------------------------------------
# The following code was originally written by Todd Neller in Java.
# It was translated into Python by May Jiang.
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
#  GinRummyPlayer - interface for Gin Rummy player
#  @author Todd W. Neller
#  @version 1.0
# ------------------------------------------------------------------------------- 

# ------------------------------------------------------------------------------- 
# Game outline
# - startGame
# - initial card option: willDrawFaceUpCard to first player.  If declined, willDrawFaceUpCard to second player.
# If initial card accepted by either first turn begins with that draw. Otherwise, first player play begins with face down draw.
# - Each normal turn *
# -- willDrawFaceUpCard offers face up discard pile card. If declined, face down card drawn.
# -- reportDraw called for both players concealing face down draw by reporting null card.
# -- getDiscard called to get discarded card
# -- report discard called for both players
# -- getFinalMelds called for current player to see if player knocks and displays melds.  Player returns null otherwise.
# - If player knocks (i.e. returns final melds), this is reported to players via reportFinalMelds.
# - getFinalMelds called for opponent and reported to players via reportFinalMelds.
# - Game manager lays off cards automatically and reports new player scores with reportScores
# - If players both below goal score, this process is repeated.
# - If two cards remain in draw pile and no one has knocked, there is no scoring and another game begins.
# ------------------------------------------------------------------------------- 

# ------------------------------------------------------------------------------- 
# Copyright (C) 2020 Todd Neller
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

Card = TypeVar('Card')

class GinRummyPlayer:

	# Inform player of 0-based player number (0/1), starting player number (0/1), and dealt cards
	# @param playerNum player's 0-based player number (0/1)
	# @param startingPlayerNum starting player number (0/1)
	# @param cards dealt cards
	def startGame(self, playerNum: int, startingPlayerNum: int, cards: List[Card]) -> None:
		pass

	# Return whether or not player will draw the given face-up card on the draw pile.
	# @param card face-up card on the draw pile
	# @return whether or not player will draw the given face-up card on the draw pile
	def willDrawFaceUpCard(self, card: Card) -> bool:
		pass

	# Report that the given player has drawn a given card and, if known, what the card is.  
	# If the card is unknown because it is drawn from the face-down draw pile, the drawnCard is null.
	# Note that a player that returns false for willDrawFaceUpCard will learn of their face-down draw from this method.
	# @param playerNum - player drawing a card
	# @param drawnCard - the card drawn or null, depending on whether the card is known to the player or not, respectively.
	def reportDraw(self, playerNum: int, drawnCard: Card) -> None:
		pass

	# Get the player's discarded card.  If you took the top card from the discard pile, 
	# you must discard a different card. 
	# If this is not a card in the player's possession, the player forfeits the game.
	# @return the player's chosen card for discarding
	def getDiscard(self) -> Card:
		pass

	# Report that the given player has discarded a given card.
	# @param playerNum the discarding player
	# @param discardedCard the card that was discarded
	def reportDiscard(self, playerNum: int, discardedCard: Card) -> None:
		pass

	# At the end of each turn, this method is called and the player that cannot (or will not) end the round will return a null value.  
	# However, the first player to "knock" (that is, end the round), and then their opponent, will return an ArrayList of ArrayLists of melded cards.  
	# All other cards are counted as "deadwood", unless they can be laid off (added to) the knocking player's melds.
	# When final melds have been reported for the other player, a player should return their final melds for the round.
	# @return null if continuing play and opponent hasn't melded, or an ArrayList of ArrayLists of melded cards.
	def getFinalMelds(self) -> List[List[Card]]:
		pass

	# When an player has ended play and formed melds, the melds (and deadwood) are reported to both players.
	# @param playerNum player that has revealed melds
	# @param melds an ArrayList of ArrayLists of melded cards with the last ArrayList (possibly empty) being deadwood.
	def reportFinalMelds(self, playerNum: int, melds: List[List[Card]]) -> None:
		pass
	 
	# Report current player scores, indexed by 0-based player number.
	# @param scores current player scores, indexed by 0-based player number
	def reportScores(self, scores: List[int]) -> None:
		pass

	# Report layoff actions.
	# @param playerNum player laying off cards
	# @param layoffCard card being laid off
	# @param opponentMeld the opponent meld that card is being added to
	def reportLayoff(self, playerNum: int, layoffCard: Card, opponentMeld: List[Card]) -> None:
		pass

	# Report the final hands of players.
	# @param playerNum player of hand reported
	# @param hand complete hand of given player
	def reportFinalHand(self, playerNum: int, hand: List[Card]) -> None:
		pass



