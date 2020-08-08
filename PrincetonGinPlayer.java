import ginrummy.*;

import java.util.ArrayList;
import java.util.Random;

// Socket work. ----------------------------------------------------------------
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
//------------------------------------------------------------------------------


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
public class PrincetonGinPlayer implements ginrummy.GinRummyPlayer {

	// Socket work. ------------------------------------------------------------
    static Socket socket;
	static BufferedReader stdIn;
	static PrintWriter out;

    static {
        try {
            socket = new Socket("localhost",41869);
            stdIn = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        	out = new PrintWriter(socket.getOutputStream(), true);
        } catch (UnknownHostException e1) {
            e1.printStackTrace();
        } catch (IOException e1) {
            e1.printStackTrace();
        } catch (Exception e) {
            // Pass
        }
    }

    private boolean verbose = false; // put true for extra print statements
	//--------------------------------------------------------------------------

	// Constructor, doesn't exist in SimpleGinRummyPlayer.java.
	public PrincetonGinPlayer() {
        // Pass
	}

	@Override
	public void startGame(int playerNum, int startingPlayerNum, Card[] cards) {
		// try {
		// 	if (socket != null)
		// 		socket.close();
       //      socket = new Socket("localhost",41869);
       //  } catch (UnknownHostException e1) {
       //      // TODO Auto-generated catch block
       //      e1.printStackTrace();
       //  } catch (IOException e1) {
       //      // TODO Auto-generated catch block
       //      e1.printStackTrace();
       //  }
		// try{
		//     stdIn =new BufferedReader(new InputStreamReader(socket.getInputStream()));
		//     out = new PrintWriter(socket.getOutputStream(), true);
       // }catch(Exception e){
		//    // Pass
       // }

		String dataStr = "startGame " + playerNum + " " + startingPlayerNum;

		for (int i = 0; i < cards.length; i++) {
			dataStr += " " + cards[i].toString();
		}
		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
            if (verbose) { System.out.println(in); }
		} catch (Exception e) {
			// Pass
		}

	}

	@Override
	public boolean willDrawFaceUpCard(Card card) {
		String dataStr = "willDrawFaceUpCard " + card.toString();

		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			boolean b = Boolean.parseBoolean(in);
			if (verbose) { System.out.println(b); }
			return b;
		} catch (Exception e) {
			// Pass
		}
		return false;
	}

	@Override
	public void reportDraw(int playerNum, Card drawnCard) {
		if (drawnCard == null)
			return;

		String dataStr = "reportDraw " + playerNum + " " + drawnCard.toString();

		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			if (verbose) { System.out.println(in); }
		} catch (Exception e) {
			// Pass
		}
	}

	@SuppressWarnings("unchecked")
	@Override
	public Card getDiscard() {
		String dataStr = "getDiscard";

		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			if (verbose) { System.out.println(in); }
			return Card.strCardMap.get(in);
		} catch (Exception e) {
			// Pass
		}
		return null;
	}

	@Override
	public void reportDiscard(int playerNum, Card discardedCard) {
		String dataStr = "reportDiscard " + playerNum + " " + discardedCard.toString();

		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			if (verbose) { System.out.println(in); }
		} catch (Exception e) {
			// Pass
		}
	}

	@Override
	public ArrayList<ArrayList<Card>> getFinalMelds() {
		String dataStr = "getFinalMelds";
		ArrayList<ArrayList<Card>> meldList = new ArrayList<ArrayList<Card>>();
		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			if (in.equals("null")) {
				return null;
			}

			while (!in.equals("")) {
				if (verbose) { System.out.println(in); }
				ArrayList<Card> meld = new ArrayList<Card>();
				String[] splited = in.split(" ");
				for (int i = 0; i < splited.length; i++) {
					meld.add(Card.strCardMap.get(splited[i]));
				}
				meldList.add(meld);
				in = stdIn.readLine();
			}
			return meldList;
		} catch (Exception e) {
			// Pass
		}
		return null;
	}

	@Override
	public void reportFinalMelds(int playerNum, ArrayList<ArrayList<Card>> melds) {
		String dataStr = "reportFinalMelds " + playerNum; // melds isn't used for anything
		try {
			out.write(dataStr);
			out.flush();
			String in = stdIn.readLine();
			if (verbose) { System.out.println(in); }
		} catch (Exception e) {
			// Pass
		}
	}

	@Override
	public void reportScores(int[] scores) {
		// Ignored by simple player, but could affect strategy of more complex player.
		return;
	}

	@Override
	public void reportLayoff(int playerNum, Card layoffCard, ArrayList<Card> opponentMeld) {
		// Ignored by simple player, but could affect strategy of more complex player.
		return;
	}

	@Override
	public void reportFinalHand(int playerNum, ArrayList<Card> hand) {
		// Ignored by simple player, but could affect strategy of more complex player.
		return;
	}

	public static void main(String[] args) {
		JavaPlayer player = new JavaPlayer();
		Card[] cards = {
			new Card(0,3),
			new Card(0,2),
			new Card(0,1),
			new Card(0,0),
			new Card(1,0),
			new Card(2,0),
			new Card(3,0),
			new Card(3,1),
			new Card(3,2),
			new Card(3,3)
		};
		player.startGame(0, 0, cards);
		player.willDrawFaceUpCard(new Card(3,1));
		player.reportDraw(0, new Card(3,1));
		player.getDiscard();
		player.reportDiscard(1, new Card(10,0));
		player.getFinalMelds();
		player.reportFinalMelds(0, null);
	}

}
