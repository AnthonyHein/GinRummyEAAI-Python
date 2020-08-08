from Card import Card
from Deck import Deck

from OpponentHandEstimationPlayer2 import OpponentHandEstimationPlayer2

class SocketPlayer(OpponentHandEstimationPlayer2):

    #---------------------------------------------------------------------------
    # FUNCTIONS FOR SOCKET SERVER COMMUNICATION

    verbose = False

    def interpretSocketOutput(self, dataStr):
        # Shouldn't hit this.
        if dataStr == "":
            return None

        dataArgs = dataStr.split(" ")

        if dataArgs[0] != "startGame":
            if SocketPlayer.verbose:
                print("Card: " + str(self.cards))

        if dataArgs[0] == "startGame":
            playerNum = dataArgs[1]
            startingPlayerNum = dataArgs[2]

            cards = []
            for i in range(3, len(dataArgs)):
                cards.append(Deck.strCardMap[dataArgs[i]])

            self.startGame(playerNum, startingPlayerNum, cards)

            return bytes("Successfully called startGame\n", "ascii")

        if dataArgs[0] == "willDrawFaceUpCard":
            card = Deck.strCardMap[dataArgs[1]]

            res = "true" if self.willDrawFaceUpCard(card) else "false"

            if SocketPlayer.verbose:
                print("Sending " + res)

            return bytes(res + "\n", "ascii")

        if dataArgs[0] == "reportDraw":
            playerNum = dataArgs[1]
            drawnCard = Deck.strCardMap[dataArgs[2]]

            self.reportDraw(playerNum, drawnCard)

            return bytes("Successfully called reportDraw\n", "ascii")

        if dataArgs[0] == "getDiscard":
            res = str(self.getDiscard())

            if SocketPlayer.verbose:
                print("Sending " + res)

            return bytes(res + "\n", "ascii")

        if dataArgs[0] == "reportDiscard":
            playerNum = dataArgs[1]
            discardedCard = Deck.strCardMap[dataArgs[2]]

            self.reportDiscard(playerNum, discardedCard)

            return bytes("Successfully called reportDiscard\n", "ascii")

        if dataArgs[0] == "getFinalMelds":
            res = ""

            melds = self.getFinalMelds()
            if melds == None:
                return bytes("null\n", "ascii")
            for meld in melds:
                for card in meld:
                    res += str(card) + " "
                res = res.strip()
                res += "\n"

            res += "\n"

            if SocketPlayer.verbose:
                print("Sending " + res)

            return bytes(res, "ascii")

        if dataArgs[0] == "reportFinalMelds":
            playerNum = dataArgs[1]

            self.reportFinalMelds(playerNum, None)

            return bytes("Successfully called reportFinalMelds\n", "ascii")

    #---------------------------------------------------------------------------
