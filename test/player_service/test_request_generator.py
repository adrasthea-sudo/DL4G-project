import unittest
import json
from source.jass.base.player_round import PlayerRound
from source.jass.ion.log_parser_swisslos import LogParserSwisslos
from source.jass.ion.player_round_serializer import PlayerRoundSerializer
from source.jass.player_service.request_generator import PlayerRoundRequestGenerator
from source.jass.player_service.request_parser import PlayerRoundParser


class PlayerRoundGeneratorTestCase(unittest.TestCase):
    def test_generator(self):
        # load some data to use for the tests
        rnd_entries = LogParserSwisslos.parse_rounds('../resources/small_log.txt')
        for rnd_entry in rnd_entries:
            player_rnds = PlayerRound.all_from_complete_round(rnd_entry.rnd)
            for player_rnd in player_rnds:
                #json_data = PlayerRoundRequestGenerator.generate_json(player_rnd)
                json_data = json.dumps(PlayerRoundSerializer.player_round_to_dict(player_rnd))
                # in the service, we directly get the json dict
                json_dict = json.loads(json_data)
                parser = PlayerRoundParser(json_dict)
                is_valid = parser.is_valid_request()
                self.assertTrue(is_valid)
                self.assertTrue(player_rnd == parser.get_parsed_round())


if __name__ == '__main__':
    unittest.main()
