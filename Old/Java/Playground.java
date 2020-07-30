import ginrummy.Card;

import java.util.HashMap;
import java.util.ArrayList;

public class Playground {

    protected Card[] cards = {new Card(3, 2), new Card(10, 1)};
    protected HashMap<String, Object> state;

    //--------------------------------------------------------------------------
    // PRIVATE CLASS B/C JAVA DOESN'T HAVE TUPLES
    class EvalTuple {
        public int action;
        public double[] probs;

        public EvalTuple(int action, double[] probs) {
            this.action = action;
            this.probs = probs;
        }
    }
    //--------------------------------------------------------------------------

    public Playground() {
        state = initGameGetState();
        setDiscard(this.cards[1]);
    }

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
        int[][] obs = {state.get("hand"), state.get("topDiscard"), state.get("deadCards"), state.get("opponentKnownCards")};

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

    @Override
    public boolean willDrawFaceUpCard(Card card) {
        // Process card.
    	this.faceUpCard = card;
        this.setDiscard(card);

        // Update legal actions.
        this.state.replace("legalActions", {2, 3});

        // Get recommended action and probs.
        EvalTuple policyResponse = evalStep(this.state);

        return policyResponse.action == 3;
    }


    # obs = state['obs']
    # legal_actions = state['legal_actions']
    # probs = self._act(obs)
    # probs = remove_illegal(probs, legal_actions)
    # action = np.random.choice(len(probs), p=probs)

    // THIS IS ME DRILLING INTO THE RL CARD IMPL ON GITHUB
    // SINCE EVAL_STEP DOESN'T EXIST FOR JAVA TF
    public EvalTuple evalStep(HashMap<String, Object> state) {
        int[][] obs = this.state.get("obs");
        int[] legalActions = this.state.get("legalActions");

    }

    // THIS IS ME DRILLING INTO THE RL CARD IMPL ON GITHUB
    // SINCE EVAL_STEP DOESN'T EXIST FOR JAVA TF
    // def _act(self, info_state):
    // ''' Predict action probability givin the observation and legal actions
    // Args:
    //     info_state (numpy.array): An obervation.
    // Returns:
    //     action_probs (numpy.array): The predicted action probability.
    // '''
    // info_state = np.expand_dims(info_state, axis=0)
    // action_probs = self._sess.run(
    //         self._avg_policy_probs,
    //         feed_dict={self._info_state_ph: info_state, self.is_train: False})[0]
    //
    // return action_probs

    // THIS IS ME DRILLING INTO THE RL CARD IMPL ON GITHUB
    // SINCE EVAL_STEP DOESN'T EXIST FOR JAVA TF
    public act(int[][] obsState) {
        double[] actionProbs = this.sess.runner().
    }

    public double[] removeIllegal(double[] actionProbs, int[] legalActions) {
        double[] probs = new double[actionProbs.length];
        double totalProb = 0;
        for (int i = 0; i < legalActions.length; i++) {
            probs[legalActions[i]] = actionProbs[legalActions[i]];
            totalProb += actionProbs[legalActions[i]];
        }
        if (totalProb < 0.00001) {
            for (int i = 0; i < legalActions.length; i++) {
                probs[legalActions[i]] = 1.0 / legalActions.length;
            }
        }
        else {
            for (int i = 0; i < legalActions.length; i++) {
                probs[legalActions[i]] /= totalProb;
            }
        }
        return probs;
    }

    public static void main(String[] args) {
            Playground pg = new Playground();
    }

}
