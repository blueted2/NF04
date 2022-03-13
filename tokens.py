from position import Position


class Token:
    def __init__(self, token_type: str, start_pos: Position, end_pos: Position = None):
        self.token_type = token_type
        self.start_pos = start_pos.copy()
        self.end_pos = end_pos.copy() if end_pos is not None else start_pos.copy().advance()
    
    def __repr__(self):
        return f"{self.token_type}"

class ValueToken(Token):
    def __init__(self, token_type: str, value: str, start_pos: Position, end_pos: Position = None):
        super().__init__(token_type, start_pos, end_pos)
        self.value = value

    def __repr__(self):
        return f"{self.token_type}: {self.value}"