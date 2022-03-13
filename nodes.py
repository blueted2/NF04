from dataclasses import dataclass
from tokens import Token


@dataclass
class Node:
    pass

@dataclass
class BinOpNode(Node):
    op_token: Token
    left_node: Node
    right_node: Node

@dataclass
class UnOpNode(Node):
    op_token: Token
    node: Node

@dataclass
class NumberNode(Node):
    value: str
