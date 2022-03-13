from numpy import r_
from errors import Error, InvalidSyntaxError
from tokens import *
from nodes import *
from typing import Tuple, cast
from token_types import *

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self) -> Token:
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def seek(self, index: int):
        self.tok_idx = index
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        return self.statement()

    def statement(self) -> Tuple[Node, Error]:
        return self.expression()

    def expression(self) -> Tuple[Node, Error]:
        term, error = self.term()
        if error: 
            return None, error

        if tok := self.try_consume_token((TT_PLUS, TT_MINUS)):
            op_tok = tok
            right_term, error = self.expression()
            if error:
                return None, error

            return BinOpNode(op_tok, term, right_term), None

        return term, None

    def term(self) -> Tuple[Node, Error]:
        factor, error = self.factor()
        if error:
            return None, error

        if tok := self.try_consume_token((TT_MUL, TT_DIV)):
            op_tok = tok
            right_factor, error = self.term()
            if error:
                 return None, error

            return BinOpNode(op_tok, factor, right_factor), None

        return factor, None

    def factor(self) -> Tuple[Node, Error]:
        if tok := self.try_consume_token((TT_PLUS, TT_MINUS)):
            return UnOpNode(tok, self.factor()), None

        return self.atom()

    def atom(self) -> Tuple[Node, Error]:
        if tok := self.try_consume_token((TT_FLOAT, TT_INT)):
            node = NumberNode(cast(ValueToken, tok).value) # silly casting stuff
            return node, None
        
        l_paren = self.try_consume_token((TT_L_PAREN))
        if l_paren:
            expr, expr_error = self.expression()
            # I will handle the error slighly later, because I first want to check if there is a closing ')'.

            r_paren = self.try_consume_token((TT_R_PAREN))
            if not r_paren:
                tok = self.current_tok
                return None, InvalidSyntaxError(tok.start_pos, tok.end_pos, "Expected closing ')'.")

            if expr_error:
                return None, InvalidSyntaxError(l_paren.end_pos, r_paren.start_pos, "Expected an expression, variable or literal.")
                
            return expr, None


        tok = self.current_tok
        return None, InvalidSyntaxError(tok.start_pos, tok.end_pos, "Expected an expression, variable or literal.")

    def try_consume_token(self, token_types: list[str] = []):
        """
        Attempts to "consume" the current token if its type is among those given as argument. 
        Does call "self.advance" if the current token can't be matched.
        """
        tok = self.current_tok
        if len(token_types) == 0 or tok.token_type in token_types:
            self.advance()
            return tok