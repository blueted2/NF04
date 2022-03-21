from __future__ import annotations

from dataclasses import dataclass
from textwrap import indent
from tokens import Token


FLOAT = "float"
INT   = "int"

@dataclass(frozen=True, eq=True)
class Node:
    pass    
@dataclass(frozen=True, eq=True)
class BinOpNode(Node):
    op_token: Token
    left_node: Node
    right_node: Node

    def __repr__(self) -> str:
        return f"[ {self.op_token} | {self.left_node}, {self.right_node} ]"

@dataclass(frozen=True, eq=True)
class UnOpNode(Node):
    op_token: Token
    node: Node

    def __repr__(self) -> str:
        return f"< {self.op_token} | {self.node} >"

@dataclass(frozen=True, eq=True)
class NumberNode(Node):
    value: str
    number_type: str

    def __repr__(self) -> str:
        return f"{self.value}"

@dataclass(frozen=True, eq=True)
class TypeNode(Node):
    type: PointerTypeNode | IdentifierNode | BuiltInTypeNode

@dataclass(frozen=True, eq=True)
class PointerTypeNode(Node):
    type_node: TypeNode

    def __repr__(self) -> str:
        return f"*{self.type_node}"

# TODO: Add list type node
@dataclass(frozen=True, eq=True)
class IdentifierNode(Node):
    value: str

        
@dataclass(frozen=True, eq=True)
class BuiltInTypeNode(Node):
    value: str
    
@dataclass(frozen=True, eq=True)
class VariablesNode(Node):
    variable_types: list[VariableDefLineNode]

    def __repr__(self) -> str:
        return "\n".join([f"{node}" for node in self.variable_types])


@dataclass(frozen=True, eq=True)
class VariableDefLineNode(Node):
    type: TypeNode
    variables: list[IdentifierNode]

    def __repr__(self) -> str:
        return f"{self.type}: " + " ".join([str(node) for node in self.variables])

@dataclass(frozen=True, eq=True)
class InstructionNode(Node):
    pass

@dataclass(frozen=True, eq=True)
class InstructionListNode(Node):
    instructions: list[InstructionNode]

@dataclass(frozen=True, eq=True)
class ProgramNode(Node):
    header: VariablesNode
    body: InstructionListNode | None
    # types: None | TypesNode

    def __repr__(self) -> str:
        result = "Variables:\n"
        result += indent(str(self.header), "  ")
        return result