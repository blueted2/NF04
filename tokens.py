from typing import Optional
from position import Position
from token_types import TT_LITERAL


class Token:
    def __init__(self, token_type: str, value: str, start_pos: Position, end_pos: Optional[Position] = None):
        self.token_type = token_type
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos if end_pos is not None else start_pos.next()
    
    def __repr__(self):
        return f"({self.token_type}: {repr(self.value)})"
