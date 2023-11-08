from source.jass.player.eva_mcts.node import Node


class Tree:
    def __init__(self) -> None:
        self.root_node = Node()