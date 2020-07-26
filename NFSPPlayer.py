from typing import List, TypeVar
from random import randint
from GinRummyUtil import GinRummyUtil
from GinRummyPlayer import GinRummyPlayer
import tensorflow as tf
import rlcard
from rlcard.agents import NFSPAgent
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
from Card import Card
import numpy as np

class NFSPPlayer(GinRummyPlayer):

    def __init__(self):
        # load pretrained model from tensorflow
        evaluate_every = 100
        evaluate_num = 100
        episode_num = 6000
        memory_init_size = 1000
        train_every = 64
        i = 0
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        self.env = rlcard.make('gin-rummy')
        with self.graph.as_default():
            self.agent = NFSPAgent(self.sess,
                          scope='nfsp' + str(i),
                          action_num=self.env.action_num,
                          state_shape=[4,52],
                          hidden_layers_sizes=[128],
                          anticipatory_param=0.5,
                          batch_size=256,
                          rl_learning_rate=0.01,
                          sl_learning_rate=0.005,
                          min_buffer_size_to_learn=memory_init_size,
                          q_replay_memory_size=int(1e5),
                          q_replay_memory_init_size=memory_init_size,
                          train_every = train_every,
                          q_train_every=train_every,
                          q_batch_size=256,
                          q_mlp_layers=[128])
        print("restoring checkpoint...")
        check_point_path = "gin_rummy_nfsp4"
        with self.sess.as_default():
            with self.graph.as_default():
                saver = tf.train.Saver()
                saver.restore(self.sess, tf.train.latest_checkpoint(check_point_path))
        print("checkpoint restored!")


    def init_game_get_state(self):
        state = {}
        state['hand'] = np.zeros(52, dtype=int)
        for card in self.cards:
            state['hand'][card.getId()] = 1
        state['top_discard'] = np.zeros(52, dtype=int)
        state['dead_cards'] = np.zeros(52, dtype=int)
        state['opponent_known_cards'] = np.zeros(52, dtype=int)
        rep = [state['hand'], state['top_discard'], state['dead_cards'], \
               state['opponent_known_cards']] #, unknown_cards_rep] # changed
        obs = np.array(rep)
        extracted_state = {'obs': obs, 'legal_actions': None}
        return extracted_state

    def get_state_index(self, label):
        inds = {'hand': 0, 'top_discard': 1, 'dead_cards': 2, \
                'opponent_known_cards': 3}
        return inds[label]
    def set_discard(self, card):
        self.state['obs'][self.get_state_index('top_discard')] = np.zeros(52, dtype=int)
        self.state['obs'][self.get_state_index('top_discard')][card.getId()] = 1

    # Inform player of 0-based player number (0/1), starting player number (0/1), and dealt cards
    # @param playerNum player's 0-based player number (0/1)
    # @param startingPlayerNum starting player number (0/1)
    # @param cards dealt cards
    def startGame(self, playerNum: int, startingPlayerNum: int, cards: List[Card]) -> None:
        self.playerNum = playerNum
        self.startingPlayerNum = startingPlayerNum
        self.cards = list(cards)
        self.opponentKnocked = False
        self.drawDiscardBitstrings = [] # long[], or List[int]
        self.faceUpCard = None
        self.drawnCard = None
        self.state = self.init_game_get_state()
        self.action = None

    # ====================================
    # Action_ids:
    #        0 -> score_player_0_id
    #        1 -> score_player_1_id
    #        2 -> draw_card_id
    #        3 -> pick_up_discard_id
    #        4 -> declare_dead_hand_id
    #        5 -> gin_id
    #        6 to 57 -> discard_id card_id
    #        58 to 109 -> knock_id card_id
    # ====================================

    # Return whether or not player will draw the given face-up card on the draw pile.
    # @param card face-up card on the draw pile
    # @return whether or not player will draw the given face-up card on the draw pile
    def willDrawFaceUpCard(self, card: Card) -> bool:
        # Return true if card would be a part of a meld, false otherwise.
        self.faceUpCard = card
        # update state
        self.set_discard(card)

        self.state['legal_actions'] = [2,3]
        action, probs = self.agent.eval_step(self.state)

        return True if action == 3 else False

        # self.faceUpCard = card
        # newCards = list(self.cards)
        # newCards.append(card)
        # for meld in GinRummyUtil.cardsToAllMelds(newCards):
        #     if card in meld:
        #         return True
        # return False

    # Report that the given player has drawn a given card and, if known, what the card is.
    # If the card is unknown because it is drawn from the face-down draw pile, the drawnCard is null.
    # Note that a player that returns false for willDrawFaceUpCard will learn of their face-down draw from this method.
    # @param playerNum - player drawing a card
    # @param drawnCard - the card drawn or null, depending on whether the card is known to the player or not, respectively.
    def reportDraw(self, playerNum: int, drawnCard: Card) -> None:
        # Ignore other player draws.  Add to cards if playerNum is this player.
        if playerNum == self.playerNum:
            self.cards.append(drawnCard)
            self.drawnCard = drawnCard
            # add to state
            self.state['obs'][self.get_state_index('hand')][drawnCard.getId()] = 1
        # if other player card is not null add to state
        elif drawnCard is not None:
            self.state['obs'][self.get_state_index('opponent_known_cards')][drawnCard.getId()] = 1

    # Get the player's discarded card.  If you took the top card from the discard pile,
    # you must discard a different card.
    # If this is not a card in the player's possession, the player forfeits the game.
    # @return the player's chosen card for discarding
    def getDiscard(self) -> Card:
        # Discard a random card (not just drawn face up) leaving minimal deadwood points.
        self.state['legal_actions'] = []
        for card in self.cards:
            if card == self.drawnCard and self.drawnCard == self.faceUpCard:
                continue
            self.state['legal_actions'].append(card.getId()+6)
        action, probs = self.agent.eval_step(self.state)
        for card in self.cards:
            if card.getId() == action-6:
                return card
        # minDeadwood = float('inf')
        # candidateCards = []
        # for card in self.cards:
        #     # Cannot draw and discard face up card.
        #     if card == self.drawnCard and self.drawnCard == self.faceUpCard:
        #         continue
        #     # Disallow repeat of draw and discard.
        #     drawDiscard = [self.drawnCard, card]
        #     if GinRummyUtil.cardsToBitstring(drawDiscard) in self.drawDiscardBitstrings:
        #         continue

        #     remainingCards = list(self.cards)
        #     remainingCards.remove(card)
        #     bestMeldSets = GinRummyUtil.cardsToBestMeldSets(remainingCards)
        #     deadwood = GinRummyUtil.getDeadwoodPoints3(remainingCards) if len(bestMeldSets) == 0 \
        #                else GinRummyUtil.getDeadwoodPoints1(bestMeldSets[0], remainingCards)
        #     if deadwood <= minDeadwood:
        #         if deadwood < minDeadwood:
        #             minDeadwood = deadwood
        #             candidateCards.clear()
        #         candidateCards.append(card)
        # # Prevent future repeat of draw, discard pair.
        # discard = candidateCards[randint(0, len(candidateCards)-1)]
        # drawDiscard = [self.drawnCard, discard]
        # self.drawDiscardBitstrings.append(GinRummyUtil.cardsToBitstring(drawDiscard))
        # return discard


    # Report that the given player has discarded a given card.
    # @param playerNum the discarding player
    # @param discardedCard the card that was discarded
    def reportDiscard(self, playerNum: int, discardedCard: Card) -> None:
        # Ignore other player discards.  Remove from cards if playerNum is this player.
        if playerNum == self.playerNum:
            self.cards.remove(discardedCard)
            # update state
            self.state['obs'][self.get_state_index('hand')][discardedCard.getId()] = 0
        else:
            self.state['obs'][self.get_state_index('opponent_known_cards')][discardedCard.getId()] = 0
        self.set_discard(discardedCard)

    # At the end of each turn, this method is called and the player that cannot (or will not) end the round will return a null value.
    # However, the first player to "knock" (that is, end the round), and then their opponent, will return an ArrayList of ArrayLists of melded cards.
    # All other cards are counted as "deadwood", unless they can be laid off (added to) the knocking player's melds.
    # When final melds have been reported for the other player, a player should return their final melds for the round.
    # @return null if continuing play and opponent hasn't melded, or an ArrayList of ArrayLists of melded cards.
    def getFinalMelds(self) -> List[List[Card]]:
        # Check if deadwood of maximal meld is low enough to go out.
        # TODO: maybe get action from agent
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
    def reportFinalMelds(self, playerNum: int, melds: List[List[Card]]) -> None:
        # Melds ignored by simple player, but could affect which melds to make for complex player.
        if playerNum != self.playerNum:
            self.opponentKnocked = True
        # add dead cards to state.
        for l in melds:
            for card in l:
                self.state['obs'][self.get_state_index('dead_cards')][card.getId()] = 1

    # Report current player scores, indexed by 0-based player number.
    # @param scores current player scores, indexed by 0-based player number
    def reportScores(self, scores: List[int]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return

    # Report layoff actions.
    # @param playerNum player laying off cards
    # @param layoffCard card being laid off
    # @param opponentMeld the opponent meld that card is being added to
    def reportLayoff(self, playerNum: int, layoffCard: Card, opponentMeld: List[Card]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return

    # Report the final hands of players.
    # @param playerNum player of hand reported
    # @param hand complete hand of given player
    def reportFinalHand(self, playerNum: int, hand: List[Card]) -> None:
        # Ignored by simple player, but could affect strategy of more complex player.
        return

# def play():
#     player = NFSPPlayer()

# play()
