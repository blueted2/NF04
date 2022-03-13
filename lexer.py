from typing import Tuple

from errors import Error, IllegalCharError
from position import Position
from tokens import Token, ValueToken

from token_types import *

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBERS = "0123456789"

class Lexer:
    def __init__(self, text: str):
        self.text: str = text
        self.position: Position = Position(-1, 0, -1, text)
        self.current_char: str = None
        self.advance()

    def advance(self):
        self.position.advance(self.current_char)
        self.current_char = self.text[self.position.index] if self.position.index < len(self.text) else None

    def number_token(self) -> Tuple[ValueToken, Error]:
        num_str = ""
        has_colon = False
        start_pos = self.position.copy()

        while self.current_char is not None and self.current_char in NUMBERS + ".":
            if self.current_char == ".":
                if has_colon:
                    start_pos = self.position.copy()
                    end_pos = start_pos.copy().advance()
                    return None, IllegalCharError(start_pos, end_pos, f"Too many '.' in number.")
                has_colon = True

            num_str += self.current_char
            self.advance()

        if self.current_char is not None and self.current_char in LETTERS:
            return None, IllegalCharError(self.position.copy(), self.position.copy().advance(), "Number cannot contain any letters.")

        if has_colon:
            return ValueToken(TT_FLOAT, num_str, start_pos, self.position), None
        else:
            return ValueToken(TT_INT, num_str, start_pos, self.position), None

    def identifier_token(self) -> ValueToken:
        identifier = ""
        start_pos = self.position.copy()

        while self.current_char in LETTERS + NUMBERS + "_":
            identifier += self.current_char
            self.advance()
        
        if (lower := identifier.lower()) in KEYWORDS:
            return ValueToken(TT_KEYWORD, lower, start_pos, self.position.copy())
        else:
            return ValueToken(TT_IDENT, identifier, start_pos, self.position.copy())

    def try_single_char_token(self) -> Token | None:
        """
        Attempts to consume a single char and return the corresponding token. 
        If the char does not correspond to a token, the char will not be consumed (self.advance won't be called), 
        and "None" shall be returned. If it does succeed, a Token shall be returned.
        """

        if not (token_type := SINGLE_CHAR_TOKENS.get(self.current_char)): 
            return None

        pos = self.position.copy()
        self.advance()

        return Token(token_type, pos)
        

    def generate_tokens(self) -> Tuple[list[Token], Error]:
        tokens = []

        while self.current_char is not None:
            c = self.current_char

            if c in ' \t':
                self.advance()
            elif c in "0123456789":
                token, error = self.number_token() 
                if error: return None, error
                tokens.append(token)

            elif c in LETTERS + "_":
                tokens.append(self.identifier_token())
                
            elif token := self.try_single_char_token():
                tokens.append(token)
            
            else:
                start_pos = self.position.copy()
                end_pos = start_pos.copy().advance()
                return None, IllegalCharError(start_pos, end_pos, f"'{c}' was not expected.")
        
        tokens.append(Token(TT_EOF, self.position, self.position.copy().advance()))

        return tokens, None