from source.jass.base.const import trump_strings_german_long, trump_string_push_german, trump_strings_short, \
    card_strings, card_ids, \
    convert_one_hot_encoded_cards_to_str_encoded_list, convert_one_hot_encoded_cards_to_int_encoded_list, \
    convert_int_encoded_cards_to_str_encoded
from source.jass.base.player_round import PlayerRound
from source.jass.base.rule_schieber import RuleSchieber
from source.jass.player.player import Player


class StdinPlayerSchieber(Player):
    """StdinPlayer selects trump and plays the card which is entered by the user via stdin."""
    def __init__(self):
        self._rule = RuleSchieber()

    def select_trump(self, rnd: PlayerRound) -> int:
        possible_trumps = trump_strings_german_long.copy()
        if rnd.forehand:
            possible_trumps.append(trump_string_push_german)
        print("Your hand: %s" % convert_one_hot_encoded_cards_to_str_encoded_list(rnd.hand))
        print("Possible trumps are: %s" % possible_trumps)
        while True:
            trump_char = input("> Enter trump [1 char] : ").upper()
            if trump_char not in trump_strings_short:
                print("'%s' is no valid trump to select" % trump_char)
                continue
            return trump_strings_short.index(trump_char)

    def play_card(self, rnd: PlayerRound) -> int:
        print('You are player {}'.format(rnd.player))
        # print previous tricks

        if rnd.nr_cards_in_trick == 0:
            trick_cards = []
        else:
            trick_cards = convert_one_hot_encoded_cards_to_int_encoded_list(rnd.current_trick[0:rnd.nr_cards_in_trick-1])

        print("Your hand: %s" % convert_one_hot_encoded_cards_to_str_encoded_list(rnd.hand))
        trump_and_trick = "Trump: '%s'" % trump_strings_german_long[rnd.trump]
        if len(trick_cards) > 0:
            trump_and_trick = trump_and_trick +\
                              ", current trick: %s" % convert_int_encoded_cards_to_str_encoded(trick_cards)
        print(trump_and_trick)

        valid_cards = self._rule.get_valid_cards(rnd.hand, trick_cards, len(trick_cards), rnd.trump)  # 1-hot encoded
        print('Valid cards: {}'.format(convert_one_hot_encoded_cards_to_str_encoded_list(valid_cards)))

        while True:
            card_str = input("> Enter card to play [string] : ").upper()
            if card_str not in card_strings:
                print("'%s' is not a card you have in your hand." % card_str)
                continue
            card = card_ids[card_str]
            if valid_cards[card] != 0:
                return card
            else:
                print("'%s' is not a valid card to play." % card_str)
