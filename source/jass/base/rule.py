# HSLU
#
# Created by Thomas Koller on 31.12.17

""" Implementation of rules of jass game"""

import numpy as np


class Rule:
    """
    Class for implementing rules of the jass game. The class includes rules that depend not on the process (like
    how trump is determined), but only upon cards. Currently this includes to determine the valid cards to play
    in a trick, to determine the winner of a trick and the points of a trick.

    This in an abstract base class that defines the interface.
    """

    def get_valid_cards(self, hand: np.array,
                        current_trick: np.ndarray or list,
                        move_nr: int,
                        trump: int or None) -> np.array:
        """
        Get the valid cards that can be played by the current player.

        Args:
            hand: one-hot encoded array of hands owned by the player
            current_trick: array with the indices of the cards for the previous moves in the current trick
            move_nr: which move the player has to make in the current trick, 0 for first move, 1 for second and so on
            trump: trump color (if used by the rule)

        Returns:
            one-hot encoded array of valid moves
        """
        raise NotImplementedError()

    def calc_points(self, trick: np.ndarray, is_last: bool, trump: int = -1) -> int:
        """
        Calculate the points from the cards in the trick. Must be implemented in subclass

        Args:
            trick: the trick
            is_last: true if this is the last trick
            trump: the trump for the round (if needed by the rules)
        """
        raise NotImplementedError

    def calc_winner(self, trick: np.ndarray, first_player: int, trump: int = -1) -> int:
        """
        Calculate the winner of a completed trick. Must be implemented in subclass.

        Precondition:
            0 <= trick[i] <= 35, for i = 0..3
        Args:
            trick: the completed trick
            first_player: the first player of the trick
            trump: the trump for the round (if needed by the rules)

        Returns:
            the player who won this trick
        """
        raise NotImplementedError



