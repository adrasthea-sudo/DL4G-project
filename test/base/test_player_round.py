import unittest
import json

from source.jass.base.const import *
from source.jass.base.round_schieber import RoundSchieber
from source.jass.base.player_round import PlayerRound
from source.jass.ion.log_parser_swisslos import LogParserSwisslos
from source.jass.ion.player_round_serializer import PlayerRoundSerializer
from source.jass.ion.round_serializer import RoundSerializer


class PlayerRoundTestCase(unittest.TestCase):
    def test_init(self):
        _ = PlayerRound()

    def test_from_round(self):
        rnd = RoundSchieber(dealer=WEST)
        hands = np.array([
            get_cards_encoded([C6, S7, S9, HQ, DA, CA, S8, D6, S10]),  # N
            get_cards_encoded([CK, C10, D10, H6, H7, H9, HK, DQ, D8]),  # E
            get_cards_encoded([C7, SA, SQ, HJ, C9, DJ, CQ, DK, C8]),  # S
            get_cards_encoded([CJ, SJ, S6, H10, H8, HA, SK, D9, D7]),  # W
        ], dtype=np.int32)
        rnd.set_hands(hands)
        rnd.action_trump(PUSH)
        rnd.action_trump(U)

        rnd.action_play_card(C7)
        rnd.action_play_card(CK)
        rnd.action_play_card(C6)
        rnd.action_play_card(CJ)

        rnd.action_play_card(S7)
        rnd.action_play_card(SJ)
        rnd.action_play_card(SA)
        rnd.action_play_card(C10)

        rnd.action_play_card(S9)
        rnd.action_play_card(S6)
        rnd.action_play_card(SQ)
        rnd.action_play_card(D10)

        rnd.action_play_card(H10)
        rnd.action_play_card(HJ)
        rnd.action_play_card(H6)
        rnd.action_play_card(HQ)

        rnd.action_play_card(H7)
        rnd.action_play_card(DA)
        rnd.action_play_card(H8)
        rnd.action_play_card(C9)

        rnd.action_play_card(H9)
        rnd.action_play_card(CA)
        rnd.action_play_card(HA)
        rnd.action_play_card(DJ)

        rnd.action_play_card(HK)
        rnd.action_play_card(S8)
        rnd.action_play_card(SK)
        rnd.action_play_card(CQ)

        rnd.action_play_card(DQ)
        rnd.action_play_card(D6)
        rnd.action_play_card(D9)
        rnd.action_play_card(DK)

        rnd.action_play_card(S10)
        rnd.action_play_card(D7)
        rnd.action_play_card(C8)
        rnd.action_play_card(D8)

        for i in range(36):
            player_rnd = PlayerRound.from_complete_round(rnd, i)
            player_rnd.assert_invariants()
            self.assertEqual(i, player_rnd.nr_played_cards)

            self.assertEqual(rnd.declared_trump, player_rnd.declared_trump)
            self.assertEqual(rnd.forehand, player_rnd.forehand)
            self.assertEqual(rnd.trump, player_rnd.trump)

            nr_tricks, nr_cards_in_trick = divmod(i, 4)
            self.assertEqual(nr_tricks, player_rnd.nr_tricks)
            self.assertEqual(nr_cards_in_trick, player_rnd.nr_cards_in_trick)

        player_rnd = PlayerRound.trump_from_complete_round(rnd, forehand=True)
        self.assertEqual(rnd.dealer, player_rnd.dealer)
        self.assertIsNone(player_rnd.trump)
        self.assertIsNone(player_rnd.forehand)
        self.assertEqual(player_rnd.player, next_player[WEST])
        player_rnd.assert_invariants()

        player_rnd = PlayerRound.trump_from_complete_round(rnd, forehand=False)
        self.assertEqual(rnd.dealer, player_rnd.dealer)
        self.assertIsNone(player_rnd.trump)
        self.assertFalse(player_rnd.forehand)
        self.assertEqual(player_rnd.player, partner_player[next_player[WEST]])
        player_rnd.assert_invariants()

    def test_from_partial_round(self):
        # create  round
        rnd = RoundSchieber(dealer=WEST)
        hands = np.array([
            get_cards_encoded([C6, S7, S9, HQ, DA, CA, S8, D6, S10]),  # N
            get_cards_encoded([CK, C10, D10, H6, H7, H9, HK, DQ, D8]),  # E
            get_cards_encoded([C7, SA, SQ, HJ, C9, DJ, CQ, DK, C8]),  # S
            get_cards_encoded([CJ, SJ, S6, H10, H8, HA, SK, D9, D7]),  # W
        ], dtype=np.int32)
        rnd.set_hands(hands)
        rnd.action_trump(PUSH)
        rnd.action_trump(U)


        # play 1 card
        rnd.action_play_card(C7)        # S

        self.assertEqual(EAST, rnd.player)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        self.assertEqual(EAST, player_rnd.player)
        self.assertEqual(C7, player_rnd.current_trick[0])


        rnd.action_play_card(CK)        # E
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(C6)        # N
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(CJ)        # W
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        # full first trick

        rnd.action_play_card(S7)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(SJ)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(SA)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(C10)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()

        rnd.action_play_card(S9)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(S6)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(SQ)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(D10)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()

        rnd.action_play_card(H10)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(HJ)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(H6)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(HQ)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()

        rnd.action_play_card(H7)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(DA)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(H8)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()
        rnd.action_play_card(C9)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()

        rnd.action_play_card(H9)
        rnd.action_play_card(CA)
        rnd.action_play_card(HA)
        rnd.action_play_card(DJ)

        rnd.action_play_card(HK)
        rnd.action_play_card(S8)
        rnd.action_play_card(SK)
        rnd.action_play_card(CQ)

        rnd.action_play_card(DQ)
        rnd.action_play_card(D6)
        rnd.action_play_card(D9)
        rnd.action_play_card(DK)

        rnd.action_play_card(S10)
        rnd.action_play_card(D7)
        rnd.action_play_card(C8)
        rnd.action_play_card(D8)
        player_rnd = PlayerRound()
        player_rnd.set_from_round(rnd)
        player_rnd.assert_invariants()

    def test_from_partial_round_for_other_player(self):
        # create  round
        np.set_printoptions(precision=2, threshold=np.inf, linewidth=np.inf, floatmode='fixed', suppress=True)

        hands = np.array([
            get_cards_encoded([DK, H10, S8, C8, C9, H8, D8, H9, H6]),
            get_cards_encoded([D10, HK, SK, CA, C10, SA, D9, C6, S10]),
            get_cards_encoded([D7, HJ, S7, C7, CK, S6, DJ, SQ, S9]),
            get_cards_encoded([D6, HQ, SJ, CQ, CJ, HA, DQ, DA, H7]),
        ], dtype=np.int32)

        # make a round object, as would be done in the arena
        rnd = RoundSchieber(dealer=WEST)
        rnd.set_hands(hands=hands)
        rnd.action_trump(OBE_ABE)
        rnd.assert_invariants()

        # the played cards
        actions = [D7, D10, DK, D6,
                   H10, HQ, HJ, HK,
                   SK, S8, SJ, S7,
                   CA, C8, CQ, C7,
                   C10, C9, CJ, CK,
                   S6, SA, H8, HA,
                   D9, D8, DQ, DJ,
                   DA, SQ, C6, H9,
                   H7, S9, S10, H6]

        player_rnd = PlayerRound()

        for action in actions:
            # make sure the action is valid
            valid = rnd.get_valid_cards()
            self.assertEqual(1, valid[action])
            player_rnd.set_from_round(rnd)
            player_rnd.assert_invariants()

            for other_player in range(4):
                player_rnd.set_from_round_for_player(rnd, other_player)
                # invariants are not preserved, as this is from another players view
                # player_rnd.assert_invariants()
                np.testing.assert_array_equal(player_rnd.hand, rnd.hands[other_player])
                data = PlayerRoundSerializer.player_round_to_dict(player_rnd)
                player_rnd2 = PlayerRoundSerializer.player_round_from_dict(data)
                # currently, first player is set even if the trick is not yet started, but that is not preserved in the
                # dict representation
                # self.assertTrue(player_rnd == player_rnd2)

            rnd.action_play_card(action)


    def test_game_state_from_round(self):
        # take game string from a record
        round_string = '{"trump":5,"dealer":3,"tss":1,"tricks":[' \
                       '{"cards":["C7","CK","C6","CJ"],"points":17,"win":0,"first":2},' \
                       '{"cards":["S7","SJ","SA","C10"],"points":12,"win":0,"first":0},' \
                       '{"cards":["S9","S6","SQ","D10"],"points":24,"win":3,"first":0},' \
                       '{"cards":["H10","HJ","H6","HQ"],"points":26,"win":1,"first":3},' \
                       '{"cards":["H7","DA","H8","C9"],"points":8,"win":1,"first":1},' \
                       '{"cards":["H9","CA","HA","DJ"],"points":2,"win":1,"first":1},' \
                       '{"cards":["HK","S8","SK","CQ"],"points":19,"win":1,"first":1},' \
                       '{"cards":["DQ","D6","D9","DK"],"points":18,"win":0,"first":1},' \
                       '{"cards":["S10","D7","C8","D8"],"points":31,"win":0,"first":0}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},{"hand":[]}],"jassTyp":"SCHIEBER_2500"}'
        round_dict = json.loads(round_string)
        rnd = RoundSerializer.round_from_dict(round_dict)
        player_rnds = PlayerRound.all_from_complete_round(rnd)
        self.assertEqual(36, len(player_rnds))

        # check properties for all moves
        for player_rnd in player_rnds:
            player_rnd.assert_invariants()
            self.assertEqual(5, player_rnd.trump)
            self.assertEqual(3, player_rnd.dealer)
            self.assertEqual(0, player_rnd.declared_trump)
            self.assertEqual(False, player_rnd.forehand)

        # first trick
        player_rnd = player_rnds[0]
        self.assertEqual(2, player_rnd.player)
        self.assertEqual(9, np.sum(player_rnd.hand))
        self.assertEqual(0, player_rnd.nr_played_cards)
        self.assertEqual(0, player_rnd.nr_tricks)
        self.assertEqual(0, player_rnd.nr_cards_in_trick)
        self.assertTrue(np.all(player_rnd.hand == get_cards_encoded([C7, SA, SQ, HJ, C9, DJ, CQ, DK, C8])))
        self.assertEqual(0, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[1]
        self.assertEqual(1, player_rnd.player)
        self.assertEqual(9, np.sum(player_rnd.hand))
        self.assertEqual(1, player_rnd.nr_played_cards)
        self.assertEqual(0, player_rnd.nr_tricks)
        self.assertEqual(1, player_rnd.nr_cards_in_trick)
        self.assertEqual(C7, player_rnd.current_trick[0])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(0, player_rnd.points_team_0)

        player_rnd = player_rnds[2]
        self.assertEqual(0, player_rnd.player, 0)
        self.assertEqual(9, np.sum(player_rnd.hand), 9)
        self.assertEqual(2, player_rnd.nr_played_cards)
        self.assertEqual(0, player_rnd.nr_tricks)
        self.assertEqual(2, player_rnd.nr_cards_in_trick)
        self.assertEqual(C7, player_rnd.current_trick[0])
        self.assertEqual(CK, player_rnd.current_trick[1])
        self.assertEqual(0, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[3]
        self.assertEqual(3, player_rnd.player)
        self.assertEqual(9, np.sum(player_rnd.hand))
        self.assertEqual(3, player_rnd.nr_played_cards)
        self.assertEqual(0, player_rnd.nr_tricks)
        self.assertEqual(3, player_rnd.nr_cards_in_trick)
        self.assertTrue([C6, C7, CK], player_rnd.nr_cards_in_trick)
        self.assertEqual(C7, player_rnd.current_trick[0])
        self.assertEqual(CK, player_rnd.current_trick[1])
        self.assertEqual(C6, player_rnd.current_trick[2])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(0, player_rnd.points_team_0)

        # second trick
        player_rnd = player_rnds[4]
        self.assertEqual(0, player_rnd.player)
        self.assertEqual(8, np.sum(player_rnd.hand))
        self.assertEqual(4, player_rnd.nr_played_cards)
        self.assertEqual(1, player_rnd.nr_tricks)
        self.assertEqual(0, player_rnd.nr_cards_in_trick)
        self.assertEqual(C7, player_rnd.tricks[0, 0])
        self.assertEqual(CK, player_rnd.tricks[0, 1])
        self.assertEqual(C6, player_rnd.tricks[0, 2])
        self.assertEqual(CJ, player_rnd.tricks[0, 3])
        self.assertEqual(17, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[5]
        self.assertEqual(3, player_rnd.player)
        self.assertEqual(8, np.sum(player_rnd.hand))
        self.assertEqual(5, player_rnd.nr_played_cards)
        self.assertEqual(1, player_rnd.nr_tricks, 1)
        self.assertEqual(1, player_rnd.nr_cards_in_trick)
        self.assertEqual(S7, player_rnd.current_trick[0])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(17, player_rnd.points_team_0)

        player_rnd = player_rnds[6]
        self.assertEqual(2, player_rnd.player, 2)
        self.assertEqual(8, np.sum(player_rnd.hand), 8)
        self.assertEqual(6, player_rnd.nr_played_cards)
        self.assertEqual(1, player_rnd.nr_tricks, 1)
        self.assertEqual(2, player_rnd.nr_cards_in_trick)
        self.assertEqual(S7, player_rnd.current_trick[0])
        self.assertEqual(SJ, player_rnd.current_trick[1])
        self.assertEqual(17, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[7]
        self.assertEqual(1, player_rnd.player, 1)
        self.assertEqual(8, np.sum(player_rnd.hand), 8)
        self.assertEqual(7, player_rnd.nr_played_cards)
        self.assertEqual(1, player_rnd.nr_tricks)
        self.assertEqual(3, player_rnd.nr_cards_in_trick)
        self.assertEqual(S7, player_rnd.current_trick[0])
        self.assertEqual(SJ, player_rnd.current_trick[1])
        self.assertEqual(SA, player_rnd.current_trick[2])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(17, player_rnd.points_team_0)

        # third trick
        player_rnd = player_rnds[8]
        self.assertEqual(0, player_rnd.player)
        self.assertEqual(7, np.sum(player_rnd.hand))
        self.assertEqual(8, player_rnd.nr_played_cards)
        self.assertEqual(2, player_rnd.nr_tricks)
        self.assertEqual(0, player_rnd.nr_cards_in_trick)
        self.assertEqual(C7, player_rnd.tricks[0, 0])
        self.assertEqual(CK, player_rnd.tricks[0, 1])
        self.assertEqual(C6, player_rnd.tricks[0, 2])
        self.assertEqual(CJ, player_rnd.tricks[0, 3])
        self.assertEqual(S7, player_rnd.tricks[1, 0])
        self.assertEqual(SJ, player_rnd.tricks[1, 1])
        self.assertEqual(SA, player_rnd.tricks[1, 2])
        self.assertEqual(C10, player_rnd.tricks[1, 3])
        self.assertEqual(29, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[9]
        self.assertEqual(3, player_rnd.player)
        self.assertEqual(7, np.sum(player_rnd.hand))
        self.assertEqual(9, player_rnd.nr_played_cards)
        self.assertEqual(2, player_rnd.nr_tricks)
        self.assertEqual(1, player_rnd.nr_cards_in_trick)
        self.assertEqual(S9, player_rnd.current_trick[0])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(29, player_rnd.points_team_0)

        player_rnd = player_rnds[10]
        self.assertEqual(2, player_rnd.player)
        self.assertEqual(7, np.sum(player_rnd.hand))
        self.assertEqual(10, player_rnd.nr_played_cards)
        self.assertEqual(2, player_rnd.nr_tricks)
        self.assertEqual(2, player_rnd.nr_cards_in_trick)
        self.assertEqual(S9, player_rnd.current_trick[0])
        self.assertEqual(S6, player_rnd.current_trick[1])
        self.assertEqual(29, player_rnd.points_team_0)
        self.assertEqual(0, player_rnd.points_team_1)

        player_rnd = player_rnds[11]
        self.assertEqual(1, player_rnd.player)
        self.assertEqual(7, np.sum(player_rnd.hand))
        self.assertEqual(11, player_rnd.nr_played_cards)
        self.assertEqual(2, player_rnd.nr_tricks)
        self.assertEqual(3, player_rnd.nr_cards_in_trick)
        self.assertEqual(S9, player_rnd.current_trick[0])
        self.assertEqual(S6, player_rnd.current_trick[1])
        self.assertEqual(SQ, player_rnd.current_trick[2])
        self.assertEqual(0, player_rnd.points_team_1)
        self.assertEqual(29, player_rnd.points_team_0)


if __name__ == '__main__':
    unittest.main()
