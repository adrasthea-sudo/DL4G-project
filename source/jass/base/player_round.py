# HSLU
#
# Created by Thomas Koller on 04.08.18
#

from typing import List

import source.jass.base.rule_factory
import numpy as np
from source.jass.base.const import next_player, partner_player
from source.jass.base.round import Round


class PlayerRound:
    """
    Class for one round of jass from the players point of view. It contains all the information about the round
    that the player can observe at a specific time in the round. This information is
        - the dealer
        - the player that declared trump,
        - the trump chosen
        - trump was declared forehand (derived information)
        - the tricks that have been played so far
        - the winner and the first player (derived) of each trick
        - the number of points that have been made by the current jass_players team in this round
        - the number of points that have been made by the opponent team in this round
        - the number of cards played in the current trick
        - the cards played in the current trick
        - the current player
        - the hand of the current player

    Similar to the class Round, PlayerRound captures
    the information at different stages of the game, like:
        - Player can choose to select a trump or push the right to make trump to his partner
        - Player needs to select trump after his partner pushed
        - Player needs to play a card.
    """

    def __init__(self,
                 dealer=None,
                 player=None,
                 trump=None,
                 forehand=None,
                 declared_trump=None,
                 jass_type=None,
                 rule=None) -> None:
        """
        Initialize the class. If dealer is supplied the player and dealer will be set accordingly and only the
        cards will have to be initialized separately to put the object in a consistent initial configuration.

        Args:
            dealer: the dealer or None if it should remain uninitialized
        """
        #
        # general information about the round
        #

        # dealer of the round
        self.dealer = dealer        # type: int

        # player of the next action, i.e. declaring trump or playing a card, i.e. player whose view of the
        # round this class describes
        self.player = player        # type: int

        # selected trump
        self.trump = trump               # type: int

        # true if trump was declared forehand, false if it was declared rearhand, None if it has not been declared yet
        self.forehand = forehand            # type: int

        # the player, who declared trump (derived)
        self.declared_trump = declared_trump      # type: int

        #
        # information about held and played cards
        #

        # the current hands of the player
        self.hand = np.zeros(shape=36, dtype=np.int32)

        # the tricks played so far, with the cards of the tricks int encoded in the order they are played
        # a value of -1 indicates that the card has not been played yet
        self.tricks = np.full(shape=[9, 4], fill_value=-1, dtype=np.int32)

        # the winner of the tricks
        self.trick_winner = np.full(shape=9, fill_value=-1, dtype=np.int32)

        # the points made in the tricks
        self.trick_points = np.zeros(shape=9, dtype=np.int32)

        # the first player of the trick (derived)
        self.trick_first_player = np.full(shape=9, fill_value=-1, dtype=np.int32)

        # the number of completed tricks
        self.nr_tricks = 0

        # the current trick is a view onto self.trick
        self.current_trick = self.tricks[0, :]

        # the number of cards in the current trick
        self.nr_cards_in_trick = 0

        # the total number of played cards
        self.nr_played_cards = 0

        self.points_team_0 = 0          # points made by the team of players 0 and 2
        self.points_team_1 = 0          # points made by the team of players 1 and 3

        # the jass_type (as used by the round_factory to create this type of round)
        self.jass_type = jass_type

        # create an appropriate object of type Rule that implements the rules for this round
        self.rule = rule
        if rule is None and jass_type is not None:
            # create the rule object
            self.rule = source.jass.base.rule_factory.get_rule(jass_type)

    def __repr__(self):
        """
        Build representation string of the object. This will also be used by str.
        Returns:
            String representation of the object
        """
        return str(self.__dict__)

    def __eq__(self, other: 'PlayerRound'):
        """
        Compare two instances. Useful for tests when the representations are encoded and decoded. The objects are
        considered equal if they have the same properties. As the properties are numpy arrays, we can not compare
        dict directly.
        Args:
            other: the other object to compare to.

        Returns:
            True if the objects are the same.
        """
        # noinspection PyPep8
        return self.dealer == other.dealer and \
               self.player == other.player and \
               self.trump == other.trump and \
               self.forehand == other.forehand and \
               self.declared_trump == other.declared_trump and \
               (self.hand == other.hand).all() and \
               (self.tricks == other.tricks).all() and \
               (self.trick_first_player == other.trick_first_player).all() and \
               (self.trick_winner == other.trick_winner).all() and \
               (self.trick_points == other.trick_points).all() and \
               self.nr_tricks == other.nr_tricks and \
               (self.current_trick == other.current_trick).all() and \
               self.nr_cards_in_trick == other.nr_cards_in_trick and \
               self.nr_played_cards == other.nr_played_cards and \
               self.points_team_0 == other.points_team_0 and \
               self.points_team_1 == other.points_team_1 and \
               self.jass_type == other.jass_type

    # additional derived properties
    @property
    def points_team_own(self) -> int:
        """
        Points made by the players team
        Returns: the current points made by the current players team
        """
        if self.player == 0 or self.player == 2:
            return self.points_team_0
        else:
            return self.points_team_1

    @property
    def points_team_opponent(self) -> int:
        """
        Points made by the opponent players team
        Returns: the current points made by the current players opponent team
        """
        if self.player == 0 or self.player == 2:
            return self.points_team_1
        else:
            return self.points_team_0

    def set_from_round(self, rnd: Round):
        """
        Initialize PlayerRound from a Round at the same card. The data in arrays is copied from the round.
        This should be able to be used both for playing card stage and trump selection (then the rnd must be in the
        trump selection state too).
        Args:
            rnd:
        """
        self.dealer = rnd.dealer
        self.player = rnd.player
        self.trump = rnd.trump
        self.forehand = rnd.forehand
        self.declared_trump = rnd.declared_trump

        if rnd.nr_played_cards < 36:
            self.hand[:] = rnd.hands[self.player, :]
        self.tricks[:, :] = rnd.tricks[:, :]
        self.trick_winner[:] = rnd.trick_winner[:]
        self.trick_points[:] = rnd.trick_points[:]
        self.trick_first_player[:] = rnd.trick_first_player[:]
        self.nr_tricks = rnd.nr_tricks
        self.nr_cards_in_trick = rnd.nr_cards_in_trick
        # current trick is a view to the trick
        if rnd.nr_played_cards < 36:
            self.current_trick = self.tricks[self.nr_tricks]
        else:
            self.current_trick = None
        self.nr_tricks = rnd.nr_tricks
        self.nr_cards_in_trick = rnd.nr_cards_in_trick
        self.nr_played_cards = rnd.nr_played_cards
        self.points_team_0 = rnd.points_team_0
        self.points_team_1 = rnd.points_team_1
        self.jass_type = rnd.jass_type
        self.rule = rnd.rule

    def set_from_round_for_player(self, rnd: Round, player: int):
        """
        Initialize PlayerRound from a Round at the same card, but not from the point of the current player, but from
         another player. This is used in the server to send information about the current game to a client without
         revealing any other players cards. I.e. the hand array will be the one from the player submitted as argument
         whilte the rnd.player is the one taking the next turn. The data in arrays is copied from the round.
        Args:
            rnd:
        """
        self.dealer = rnd.dealer
        self.player = rnd.player
        self.trump = rnd.trump
        self.forehand = rnd.forehand
        self.declared_trump = rnd.declared_trump

        if rnd.nr_played_cards < 36:
            self.hand[:] = rnd.hands[player, :]
        self.tricks[:, :] = rnd.tricks[:, :]
        self.trick_winner[:] = rnd.trick_winner[:]
        self.trick_points[:] = rnd.trick_points[:]
        self.trick_first_player[:] = rnd.trick_first_player[:]
        self.nr_tricks = rnd.nr_tricks
        self.nr_cards_in_trick = rnd.nr_cards_in_trick
        # current trick is a view to the trick
        if rnd.nr_played_cards < 36:
            self.current_trick = self.tricks[self.nr_tricks]
        else:
            self.current_trick = None
        self.nr_tricks = rnd.nr_tricks
        self.nr_cards_in_trick = rnd.nr_cards_in_trick
        self.nr_played_cards = rnd.nr_played_cards
        self.points_team_0 = rnd.points_team_0
        self.points_team_1 = rnd.points_team_1
        self.jass_type = rnd.jass_type
        self.rule = rnd.rule

    def set_from_round_shared(self, rnd: Round):
        """
        Initialize PlayerRound from a full Round at the same card. The data in arrays is shared between the
        PlayerRound and Round, so it should not be changed. As arrays are already allocated in __init__ and
        overwritten here, the method is best employed when the object is used several times.

        Args:
            rnd:
        """
        self.dealer = rnd.dealer
        self.player = rnd.player
        self.trump = rnd.trump
        self.forehand = rnd.forehand
        self.declared_trump = rnd.declared_trump
        self.hand = rnd.hands[self.player, :]
        self.tricks = rnd.tricks
        self.trick_winner = rnd.trick_winner
        self.trick_points = rnd.trick_points
        self.trick_first_player = rnd.trick_first_player
        self.current_trick = rnd.current_trick
        self.nr_tricks = rnd.nr_tricks
        self.nr_cards_in_trick = rnd.nr_cards_in_trick
        self.nr_played_cards = rnd.nr_played_cards
        self.points_team_0  = rnd.points_team_0
        self.points_team_1 = rnd.points_team_1
        self.jass_type = rnd.jass_type
        self.rule = rnd.rule

    def calculate_points_from_tricks(self) -> None:
        """
        Calculate the points of the teams from the trick points and trick winners.
        """
        self.points_team_0 = 0
        self.points_team_1 = 0
        for trick in range(self.nr_tricks):
            if self.trick_winner[trick] == 0 or self.trick_winner[trick] == 2:
                self.points_team_0 += self.trick_points[trick]
            else:
                self.points_team_1 += self.trick_points[trick]

    def get_valid_cards(self):
        """
        Get the valid cards for the player. Delegated to the rule
        Returns:
            the valid cards
        """
        return self.rule.get_valid_cards(self.hand,
                                         self.current_trick,
                                         self.nr_cards_in_trick,
                                         self.trump)

    @staticmethod
    def from_complete_round(rnd: Round, cards_played: int) -> 'PlayerRound':
        """
        Create a PlayerRound object from a complete Round object for a specific card.

        Preconditions:
            0 <= cards_played <= 35
            rnd.nr_played_cards == 36

        Args:
            rnd: The Round from which to create the PlayerRound.
            cards_played: the number of cards played for which the PlayerRound should be created

        Returns:
            a PlayerRound object for the state when the cards have been played.

        """
        player_rnd = PlayerRound(dealer=rnd.dealer,
                                 trump=rnd.trump,
                                 declared_trump=rnd.declared_trump,
                                 forehand=rnd.forehand,
                                 jass_type=rnd.jass_type,
                                 rule=rnd.rule)

        player_rnd.nr_played_cards = cards_played

        # calculate the number of tricks played and how many cards in the current trick
        player_rnd.nr_tricks, player_rnd.nr_cards_in_trick = divmod(cards_played, 4)

        if cards_played > 0:
            # copy the trick first player,
            # Changed: don't copy this right after trump, so that is is only available when the trick
            # has actually started
            if player_rnd.nr_cards_in_trick == 0:
                player_rnd.trick_first_player[0:player_rnd.nr_tricks] = rnd.trick_first_player[
                                                                        0:player_rnd.nr_tricks]
                # only full tricks
                player_rnd.tricks[0:player_rnd.nr_tricks, :] = rnd.tricks[0:player_rnd.nr_tricks, :]

                # current trick is empty (or none if last card)
                if cards_played == 36:
                    player_rnd.current_trick = None
                else:
                    # this is the next trick, after the full ones
                    player_rnd.current_trick = player_rnd.tricks[player_rnd.nr_tricks]
            else:
                # copy all the full tricks first
                player_rnd.tricks[0:player_rnd.nr_tricks, :] = rnd.tricks[0:player_rnd.nr_tricks, :]

                # copy the trick in progress
                player_rnd.tricks[player_rnd.nr_tricks, 0:player_rnd.nr_cards_in_trick] = \
                    rnd.tricks[player_rnd.nr_tricks, 0:player_rnd.nr_cards_in_trick]
                # make sure the current trick points to that

                player_rnd.current_trick = player_rnd.tricks[player_rnd.nr_tricks]

                # copy first player for the completed tricks and the current trick
                player_rnd.trick_first_player[0:player_rnd.nr_tricks+1] = rnd.trick_first_player[
                                                                        0:player_rnd.nr_tricks+1]
            # copy the results from the tricks
            player_rnd.trick_winner[0:player_rnd.nr_tricks] = rnd.trick_winner[0:player_rnd.nr_tricks]
            player_rnd.trick_points[0:player_rnd.nr_tricks] = rnd.trick_points[0:player_rnd.nr_tricks]

            player_rnd.calculate_points_from_tricks()

            # determine player
            player_rnd.player = (rnd.trick_first_player[player_rnd.nr_tricks]-player_rnd.nr_cards_in_trick) % 4
        else:
            # no cards played yet
            player_rnd.player = next_player[player_rnd.dealer]

        # determine hand still held by the player, which are the cards that the player will play in the next
        # tricks of the full rnd, that are not played yet
        for i in range(player_rnd.nr_tricks, 9):
            # determine which card was played in this trick by the player
            index = (rnd.trick_first_player[i] - player_rnd.player) % 4
            card_played = rnd.tricks[i, index]
            player_rnd.hand[card_played] = 1
        return player_rnd

    @staticmethod
    def all_from_complete_round(rnd: Round) -> List['PlayerRound']:
        """
        Get all 36 player rounds from a complete round
        Args:
            rnd: The Round from which to create the PlayerRound.

        Returns:
            the list of player_rounds for cards 0..35
        """
        return [PlayerRound.from_complete_round(rnd, i) for i in range(0, 36)]

    @staticmethod
    def trump_from_complete_round(rnd: Round, forehand: bool) -> 'PlayerRound' or None:
        """
        Create a player round from a complete round for the state of trump selection.
        Args:
            rnd: a complete round
            forehand: true if the trump selection should be for the forehand player, false if it should be for the
            rearhand player after push

        Returns:
            a PlayerRound for trump selection or None if trump selection was asked to be returned for rearhand, when
            there was no rearhand trump selection in that round
        """
        if not forehand and rnd.forehand:
            return None

        player_rnd = PlayerRound(dealer=rnd.dealer, jass_type=rnd.jass_type, rule=rnd.rule)

        if forehand:
            player_rnd.player = next_player[player_rnd.dealer]
            player_rnd.forehand = None
        else:
            player_rnd.player = partner_player[next_player[player_rnd.dealer]]
            player_rnd.forehand = False

        # determine hand still held by the player, which are the cards that the player will play in the next
        # tricks of the full rnd, that are not played yet
        for i in range(0, 9):
            # determine which card was played in this trick by the player
            index = (rnd.trick_first_player[i] - player_rnd.player) % 4
            card_played = rnd.tricks[i, index]
            player_rnd.hand[card_played] = 1
        return player_rnd

    @staticmethod
    def trump_from_round_start(rnd: Round, forehand: bool) -> 'PlayerRound' or None:
        """
        Create a player round from a complete round for the state of trump selection.
        Args:
            rnd: a complete round
            forehand: true if the trump selection should be for the forehand player, false if it should be for the
            rearhand player after push

        Returns:
            a PlayerRound for trump selection or None if trump selection was asked to be returned for rearhand, when
            there was no rearhand trump selection in that round
        """
        if not forehand and rnd.forehand:
            return None

        player_rnd = PlayerRound(dealer=rnd.dealer, jass_type=rnd.jass_type, rule=rnd.rule)

        if forehand:
            player_rnd.player = next_player[player_rnd.dealer]
            player_rnd.forehand = None
        else:
            player_rnd.player = partner_player[next_player[player_rnd.dealer]]
            player_rnd.forehand = False

        # determine hand still held by the player, which are the cards that the player will play in the next
        # tricks of the full rnd, that are not played yet
        for i in range(0, 9):
            # determine which card was played in this trick by the player
            index = (rnd.trick_first_player[i] - player_rnd.player) % 4
            card_played = rnd.tricks[i, index]
            player_rnd.hand[card_played] = 1
        return player_rnd

    def assert_invariants(self) -> None:
        """
        Validates the internal consistency and throws an assertion exception if an error is detected.
        """
        # trump declaration
        if self.trump is not None:
            if self.forehand:
                assert self.declared_trump == next_player[self.dealer]
            else:
                assert self.declared_trump == partner_player[next_player[self.dealer]]
            # self player is only allowed to be None at the end of the game
            assert self.player is not None or self.nr_played_cards == 36

        # first player should be set, after a card has been played
        if self.nr_played_cards > 0:
            assert self.trick_first_player[0] == next_player[self.dealer]


        # trick winners
        for i in range(1, self.nr_tricks):
            assert self.trick_winner[i - 1] == self.trick_first_player[i]

        # cards played
        assert self.nr_played_cards == 4 * self.nr_tricks + self.nr_cards_in_trick

        # cards in hand
        assert self.hand.size == 36
        assert self.hand.sum() == 9-self.nr_tricks

        # check current trick
        if self.nr_played_cards == 36:
            assert self.current_trick is None
        else:
            nr_cards_in_current_trick = np.count_nonzero(self.current_trick[:] > -1)
            expected_cards_in_current_trick = (self.nr_played_cards % 4)
            assert nr_cards_in_current_trick == expected_cards_in_current_trick

