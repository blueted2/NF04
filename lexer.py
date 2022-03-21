from __future__ import annotations

from typing import Tuple
from dataclasses import dataclass, astuple

from errors import Error, IllegalCharError
from position import Position
from tokens import Token

from token_types import *

@dataclass
class TokenizationResult:
    token: Token | None
    error: Error | None

    @staticmethod
    def success(token: Token) -> TokenizationResult:
        return TokenizationResult(token, None)

    @staticmethod
    def fail(error: Error) -> TokenizationResult:
        return TokenizationResult(None, error)

    def __iter__(self):
        return iter(astuple(self))


class Lexer:
    def __init__(self, text: str):
        self.text: str = text
        self.position: Position = Position(-1, 0, -1, text)
        self.current_char: str | None = None
        self.advance()

    def advance(self):
        self.position = self.position.next(self.current_char)
        self.current_char = self.text[self.position.index] if self.position.index < len(self.text) else None

    def generate_tokens(self) -> Tuple[list[Token], None] | Tuple[None, Error]:
        tokens = []

        while self.current_char is not None:
            c = self.current_char

            if c in WHITESPACE:
                self.advance()
            elif c in NUMBERS:
                token, error = self.number_literal() 
                if error: return None, error
                tokens.append(token)

            elif c in LETTERS + "_":
                token, error = self.identifier_token()
                if error: return None, error
                tokens.append(token)
                
            elif token := self.try_single_char_token():
                tokens.append(token)
            
            else:
                start_pos = self.position
                end_pos = start_pos.next()
                return None, IllegalCharError(start_pos, end_pos, f"'{c}' was not expected.")
        
        tokens.append(Token(TT_EOF, "eof", self.position, self.position.next()))

        return tokens, None

    def number_literal(self) -> TokenizationResult:
        num_str = ""
        has_colon = False
        start_pos = self.position

        while self.current_char is not None and self.current_char in NUMBERS + ".":
            if self.current_char == ".":
                if has_colon:
                    start_pos = self.position
                    end_pos = start_pos.next()
                    return TokenizationResult.fail(IllegalCharError(start_pos, end_pos, f"Too many '.' in number."))
                has_colon = True

            num_str += self.current_char
            self.advance()

        if self.current_char is not None and self.current_char in LETTERS:
            return TokenizationResult.fail(IllegalCharError(self.position, self.position.next(), "Number cannot contain any letters."))

        if has_colon:
            tok = Token(LIT_DECIMAL, num_str, start_pos, self.position)
        else:
            tok = Token(LIT_WHOLE, num_str, start_pos, self.position)
            
        return TokenizationResult.success(tok)

    def identifier_token(self) -> TokenizationResult:
        identifier = ""
        start_pos = self.position

        while self.current_char is not None and self.current_char in LETTERS + NUMBERS + "_":
            identifier += self.current_char
            self.advance()
        
        identifier_as_lower = identifier.lower()
        if identifier_as_lower in KEYWORDS:
            return TokenizationResult.success(Token(TT_KEYWORD, identifier_as_lower, start_pos, self.position))
        
        return TokenizationResult.success(Token(TT_IDENTIFIER, identifier, start_pos, self.position))

    def try_single_char_token(self) -> Token | None:
        """
        Attempts to consume a single char and return the corresponding token. 
        If the char does not correspond to a token, the char will not be consumed (self.advance won't be called), 
        and "None" shall be returned. If it does succeed, a Token shall be returned.
        """
        if self.current_char is None: 
            return None

        c = self.current_char
        pos = self.position
        if c in OPERATORS:
            self.advance()
            return Token(TT_OPERATOR, c, pos)

        if c in SEPERATORS:
            self.advance()
            return Token(TT_SEPERATOR, c, pos)

        self.advance()
