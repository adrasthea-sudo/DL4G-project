# HSLU
#
# Created by Ruedi Arnold on 18.01.2018
#

import unittest
import json

from source.jass.player_service.request_parser import PlayerRoundParser


class RequestValidatorTest(unittest.TestCase):

    def test_parse_select_trump_request_no_data(self):
        request_data = None
        result = PlayerRoundParser(request_data).is_valid_request()
        self.assertFalse(result)

    def test_parse_select_trump_request_no_json(self):
        request_data = 'i am not a json string'
        result = PlayerRoundParser(request_data).is_valid_request()
        self.assertFalse(result)

    def test_parse_select_trump_request_ok(self):
        request_data = '{"dealer":0,"tss":1,"tricks":[],"currentPlayer":3,"player":[{"hand":[]},' \
                       '{"hand":[]},{"hand":[]},{"hand":["HJ","S9","SJ","C7","C8","HA",' \
                       '"C6","H7","CJ"]}],"jassTyp":"SCHIEBER_1000"}'
        request_dict = json.loads(request_data)
        select_trump_parser = PlayerRoundParser(request_dict)
        self.assertTrue(select_trump_parser.is_valid_request())
        rnd = select_trump_parser.get_parsed_round()
        self.assertEqual(0, rnd.dealer)
        self.assertFalse(rnd.forehand)
        expected_hand = [0, 0, 0, 0, 0, 0, 0, 0, 0,  # D
                         1, 0, 0, 1, 0, 0, 0, 1, 0,  # H
                         0, 0, 0, 1, 0, 1, 0, 0, 0,  # S
                         0, 0, 0, 1, 0, 0, 1, 1, 1]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        rnd.assert_invariants()

    def test_parse_select_trump_request_missing_element(self):
        # element "dealer" is missing (i.e. misspelled)
        request_data = '{"dealerXXX":0,"tss":1,"tricks":[],"player":[{"hand":[]},' \
                       '{"hand":[]},{"hand":[]},{"hand":["HJ","S9","SJ","C7","C8","HA",' \
                       '"C6","H7","CJ"]}],"jassTyp":"SCHIEBER_1000"}'
        request_dict = json.loads(request_data)
        result = PlayerRoundParser(request_dict).is_valid_request()
        self.assertFalse(result)


    def test_parse_select_trump_request_wrong_jassTyp(self):
        request_data = '{"dealer":0,"tss":1,"tricks":[],"player":[{"hand":[]},' \
                       '{"hand":[]},{"hand":[]},{"hand":["HJ","S9","SJ","C7","C8","HA",' \
                       '"C6","H7","CJ"]}],"jassTyp":"WHATEVER"}'
        request_dict = json.loads(request_data)
        result = PlayerRoundParser(request_dict).is_valid_request()
        self.assertFalse(result)

    def test_parse_play_card_request_valid_middle_of_game(self):
        request_data = '{"trump":4,"dealer":3,"tss":1,"currentPlayer":2,"tricks":[' \
                       '{"cards":["SA","S7","SQ","S6"],"points":14,"win":2,"first":2},' \
                       '{"cards":["C8","CJ","CQ","CK"],"points":17,"win":3,"first":2},' \
                       '{"cards":["D6","D7","DJ","DA"],"points":13,"win":0,"first":3},' \
                       '{"cards":["HA","H6"],"points":0,"win":0,"first":0}],' \
                       '"player":[{"hand":[]},{"hand":[]},' \
                       '{"hand":["S8","S9","SK","CA","C10","H9"]},{"hand":[]}],' \
                       '"jassTyp":"SCHIEBER_2500"}'
        request_dict = json.loads(request_data)
        play_card_parser = PlayerRoundParser(request_dict)
        self.assertTrue(play_card_parser.is_valid_request())
        rnd = play_card_parser.get_parsed_round()
        self.assertEqual(3, rnd.nr_tricks)
        self.assertEqual(3, rnd.dealer)
        self.assertEqual(4, rnd.trump)
        self.assertFalse(rnd.forehand)
        expected_hand = [0, 0, 0, 0, 0, 0, 0, 0, 0,  # D
                         0, 0, 0, 0, 0, 1, 0, 0, 0,  # H
                         0, 1, 0, 0, 0, 1, 1, 0, 0,  # S
                         1, 0, 0, 0, 1, 0, 0, 0, 0]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        rnd.assert_invariants()

    # old test, data is now illegal as points and winner must be present in complete tricks
    def do_not_test_parse_play_card_request_valid_middle_of_game_no_points_and_winner(self):
        request_data = '{"trump":4,"dealer":3,"tss":1,"currentPlayer":2,"tricks":[' \
                       '{"cards":["SA","S7","SQ","S6"],"first":2},' \
                       '{"cards":["C8","CJ","CQ","CK"],"first":2},' \
                       '{"cards":["D6","D7","DJ","DA"],"first":3},' \
                       '{"cards":["HA","H6"],"points":0,"win":0,"first":0}],' \
                       '"player":[{"hand":[]},{"hand":[]},' \
                       '{"hand":["S8","S9","SK","CA","C10","H9"]},{"hand":[]}],' \
                       '"jassTyp":"SCHIEBER_2500"}'
        request_dict = json.loads(request_data)
        play_card_parser = PlayerRoundParser(request_dict)
        self.assertTrue(play_card_parser.is_valid_request())
        rnd = play_card_parser.get_parsed_round()
        self.assertEqual(3, rnd.nr_tricks)
        self.assertEqual(3, rnd.dealer)
        self.assertEqual(4, rnd.trump)
        self.assertFalse(rnd.forehand)
        expected_hand = [0, 0, 0, 0, 0, 0, 0, 0, 0,  # D
                         0, 0, 0, 0, 0, 1, 0, 0, 0,  # H
                         0, 1, 0, 0, 0, 1, 1, 0, 0,  # S
                         1, 0, 0, 0, 1, 0, 0, 0, 0]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        self.assertEqual(14, rnd.trick_points[0])
        self.assertEqual(17, rnd.trick_points[1])
        self.assertEqual(13, rnd.trick_points[2])
        rnd.assert_invariants()

    def test_parse_play_card_request_valid_first_trick(self):
        request_data = '{"trump":0,"dealer":3,"tss":0,"currentPlayer":3, "tricks":[' \
                       '{"cards":["DJ","D7","D10"],"points":0,"win":0,"first":2}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},' \
                       '{"hand":["S6","S7","S8","C6","C7","C8","D6","D8","HJ"]}],' \
                       '"jassTyp":"SCHIEBER_1000"}'
        request_dict = json.loads(request_data)
        play_card_parser = PlayerRoundParser(request_dict)
        self.assertTrue(play_card_parser.is_valid_request())
        rnd = play_card_parser.get_parsed_round()
        self.assertEqual(3, rnd.dealer)
        self.assertEqual(0, rnd.trump)
        self.assertTrue(rnd.forehand)
        self.assertEqual(0, rnd.nr_tricks)
        expected_hand = [0, 0, 0, 0, 0, 0, 1, 0, 1,  # D
                         0, 0, 0, 1, 0, 0, 0, 0, 0,  # H
                         0, 0, 0, 0, 0, 0, 1, 1, 1,  # S
                         0, 0, 0, 0, 0, 0, 1, 1, 1]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        current_trick = rnd.current_trick.tolist()
        self.assertEqual([3, 7, 4, -1], current_trick)
        rnd.assert_invariants()

    def test_parse_play_card_request_valid_last_trick(self):
        request_data = '{"trump":2,"dealer":2,"tss":1,"currentPlayer":3,"tricks":[' \
                       '{"cards":["SJ","S8","S6","S7"],"points":20,"win":1,"first":1},' \
                       '{"cards":["S9","S10","SQ","SK"],"points":31,"win":1,"first":1},' \
                       '{"cards":["CJ","CA","C6","C10"],"points":23,"win":0,"first":1},' \
                       '{"cards":["C8","C7","D7","CK"],"points":4,"win":1,"first":0},' \
                       '{"cards":["H8","HJ","H6","HA"],"points":13,"win":2,"first":1},' \
                       '{"cards":["DJ","DQ","D6","DA"],"points":16,"win":3,"first":2},' \
                       '{"cards":["CQ","H10","D10","C9"],"points":23,"win":3,"first":3},' \
                       '{"cards":["H7","HQ","HK","D8"],"points":7,"win":1,"first":3},' \
                       '{"cards":["SA","D9","H9"],"points":20,"win":1,"first":1}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},{"hand":["DK"]}],"jassTyp":"SCHIEBER_2500"}'
        request_dict = json.loads(request_data)
        play_card_parser = PlayerRoundParser(request_dict)
        self.assertTrue(play_card_parser.is_valid_request())
        rnd = play_card_parser.get_parsed_round()
        self.assertEqual(2, rnd.dealer)
        self.assertEqual(2, rnd.trump)
        self.assertFalse(rnd.forehand)
        self.assertEqual(8, rnd.nr_tricks)
        expected_hand = [0, 1, 0, 0, 0, 0, 0, 0, 0,  # D
                         0, 0, 0, 0, 0, 0, 0, 0, 0,  # H
                         0, 0, 0, 0, 0, 0, 0, 0, 0,  # S
                         0, 0, 0, 0, 0, 0, 0, 0, 0]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        current_trick = rnd.current_trick.tolist()
        self.assertEqual([18, 5, 14, -1], current_trick)
        rnd.assert_invariants()

    # old test, data is now illegal as points and winner must be present in complete tricks
    def do_not_test_parse_play_card_request_valid_last_trick_no_points_and_win(self):
        request_data = '{"trump":2,"dealer":2,"tss":1,"currentPlayer":3,"tricks":[' \
                       '{"cards":["SJ","S8","S6","S7"],"first":1},' \
                       '{"cards":["S9","S10","SQ","SK"],"first":1},' \
                       '{"cards":["CJ","CA","C6","C10"],"first":1},' \
                       '{"cards":["C8","C7","D7","CK"],"first":0},' \
                       '{"cards":["H8","HJ","H6","HA"],"first":1},' \
                       '{"cards":["DJ","DQ","D6","DA"],"first":2},' \
                       '{"cards":["CQ","H10","D10","C9"],"first":3},' \
                       '{"cards":["H7","HQ","HK","D8"],"first":3},' \
                       '{"cards":["SA","D9","H9"],"first":1}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},{"hand":["DK"]}],"jassTyp":"SCHIEBER_2500"}'
        request_dict = json.loads(request_data)
        play_card_parser = PlayerRoundParser(request_dict)
        self.assertTrue(play_card_parser.is_valid_request())
        rnd = play_card_parser.get_parsed_round()
        self.assertEqual(2, rnd.dealer)
        self.assertEqual(2, rnd.trump)
        self.assertFalse(rnd.forehand)
        self.assertEqual(8, rnd.nr_tricks)
        expected_hand = [0, 1, 0, 0, 0, 0, 0, 0, 0,  # D
                         0, 0, 0, 0, 0, 0, 0, 0, 0,  # H
                         0, 0, 0, 0, 0, 0, 0, 0, 0,  # S
                         0, 0, 0, 0, 0, 0, 0, 0, 0]  # C
        self.assertEqual(expected_hand, rnd.hand.tolist())
        current_trick = rnd.current_trick.tolist()
        self.assertEqual([18, 5, 14, -1], current_trick)
        self.assertEqual(20, rnd.trick_points[0])
        self.assertEqual(31, rnd.trick_points[1])
        self.assertEqual(23, rnd.trick_points[2])
        self.assertEqual(4, rnd.trick_points[3])
        self.assertEqual(13, rnd.trick_points[4])
        self.assertEqual(16, rnd.trick_points[5])
        self.assertEqual(23, rnd.trick_points[6])
        self.assertEqual(7, rnd.trick_points[7])
        self.assertEqual(1, rnd.trick_winner[0])
        self.assertEqual(1, rnd.trick_winner[1])
        self.assertEqual(0, rnd.trick_winner[2])
        self.assertEqual(1, rnd.trick_winner[3])
        self.assertEqual(2, rnd.trick_winner[4])
        self.assertEqual(3, rnd.trick_winner[5])
        self.assertEqual(3, rnd.trick_winner[6])
        self.assertEqual(1, rnd.trick_winner[7])

        rnd.assert_invariants()


if __name__ == '__main__':
    unittest.main()
