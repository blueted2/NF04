from __future__ import annotations
from optparse import Option

from errors import Error, InvalidSyntaxError
from tokens import *
from nodes import *
from typing import Any, cast
from token_types import *


@dataclass
class ParseResult:
    _node: Node | None
    _error: Error | None

    @staticmethod
    def success(node: Node) -> ParseResult:
        if node is None:
            raise Exception("node cannot be None")
        return ParseResult(node, None)

    @staticmethod
    def fail(error: Error) -> ParseResult:
        if error is None:
            raise Exception("error cannot be None")
        return ParseResult(None, error)

    @property
    def has_error(self) -> bool:
        return self._error is not None

    @property
    def node(self) -> Any:
        if self._node is None:
            raise Exception("Node property accessed even with error present.")
        return self._node

    @property
    def error(self) -> Error:
        if self._error is None:
            raise Exception("Error property accessed even with node present.")
        return self._error

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

    def parse(self) -> ParseResult:
        return self.program()

    def program(self) -> ParseResult:
        var_header_res = self.variables()
        if var_header_res.has_error:
            return var_header_res

        instructions_res = self.instructions()
        if instructions_res.has_error: 
            return instructions_res
        

        program_node = ProgramNode(var_header_res.node, instructions_res.node)
        return ParseResult.success(program_node)

    def variables(self) -> ParseResult:
        if not self.try_consume_keyword(["variables"]):
            tok = self.current_tok
            error = InvalidSyntaxError(tok.start_pos, tok.end_pos, f"Expected 'variables' keyword, not {tok}.")
            return ParseResult.fail(error)

        # Optional, don't need to check if said token was consumed
        self.try_consume_seperator(":")

        if not self.try_consume_seperator("\n"):
            tok = self.current_tok
            error = InvalidSyntaxError(tok.start_pos, tok.end_pos, f"Expected newline (\\n), not {tok}.")
            return ParseResult.fail(error)
        
        variables_def_lines: list[VariableDefLineNode] = []
        
        while self.current_tok.token_type == TT_IDENTIFIER:
            variable_type_def_res = self.variable_def_line()
            if variable_type_def_res.has_error:
                return variable_type_def_res
            
            variables_def_lines.append(variable_type_def_res.node)

        return ParseResult.success(VariablesNode(variables_def_lines))

    def variable_def_line(self) -> ParseResult:
        variables: list[IdentifierNode] = []

        while var_tok := self.try_consume_identifier():
            variables.append(IdentifierNode(var_tok.value))
            # Keep looking for identifiers until you find one without a "," after id.
            if not self.try_consume_seperator(","):
                break

        colon = self.token(TT_COLON)
        if colon.has_error: 
            return colon

        type_tok_res = self.type_node()
        if type_tok_res.has_error:
            return type_tok_res

        newline_res = self.try_consume_seperator("\n")
        if newline_res.has_error:
            return newline_res

        return ParseResult.success(VariableDefLineNode(type_tok_res.node, variables)) 

    def type_node(self) -> ParseResult:
        if self.try_consume_keyword(["pointeur"]):
            self.try_consume_keyword(["vers"])

            type_res = self.type_node()
            if type_res.has_error:
                return type_res

            return ParseResult.success(PointerTypeNode(type_res.node))

        if built_in := self.try_consume_keyword(["reel", "entier"]):
            return ParseResult.success(BuiltInTypeNode(built_in.value))

        if ident := self.try_consume_identifier():
            return ParseResult.success(IdentifierNode(ident.value))

        tok = self.current_tok
        return ParseResult.fail(InvalidSyntaxError(tok.start_pos, tok.end_pos, f"Expected type, not {tok}"))

    def identifier(self) -> ParseResult:
        ident_tok = self.try_consume_identifier()
        if ident_tok:
            return ParseResult.success(IdentifierNode(ident_tok.value))

        tok = self.current_tok
        return ParseResult.fail(InvalidSyntaxError(tok.start_pos, tok.end_pos, f"Expected identifier, not {tok}."))
    
    def instructions(self) -> ParseResult:
        return ParseResult.success(InstructionListNode([]))

    def statement(self) -> ParseResult:
        return self.expression()

    def expression(self) -> ParseResult:
        term_res = self.term()
        if term_res.has_error:
            return term_res

        if op_tok := self.try_consume_operator(["+", "-"]):
            expr_res = self.expression()
            if expr_res.has_error:
                return expr_res

            left_node = term_res.node
            right_node = expr_res.node
            expr_node = BinOpNode(op_tok, left_node, right_node)
            return ParseResult.success(expr_node)

        return term_res

    def term(self) -> ParseResult:
        factor_res = self.factor()
        if factor_res.has_error:
            return factor_res

        if op_tok := self.try_consume_operator(["*", "/"]):
            term_res = self.term()
            if term_res.has_error:
                 return term_res

            left_node = factor_res.node
            right_node = term_res.node
            term_node = BinOpNode(op_tok, left_node, right_node)
            return ParseResult.success(term_node)

        return factor_res

    def factor(self) -> ParseResult:
        un_op_token = self.try_consume_operator(["+", "-"])
        if un_op_token is None:
            return self.atom()

        factor_res = self.factor()
        if factor_res.has_error:
            return factor_res

        un_op_node = UnOpNode(un_op_token, factor_res.node)
        return ParseResult.success(un_op_node)

    def atom(self) -> ParseResult:
        num_tok = self.try_consume_token([LIT_WHOLE, LIT_DECIMAL])
        if num_tok is not None:
            num_node = NumberNode(num_tok.value, FLOAT_NODE if num_tok.token_type == LIT_DECIMAL else INT_NODE)
            return ParseResult.success(num_node)
        
        l_paren = self.try_consume_seperator("(")
        if l_paren:
            expr_res = self.expression()
            # I will handle the error slighly later, because I first want to check if there is a closing ')'.

            r_paren = self.try_consume_seperator(")")
            if r_paren is None:
                tok = self.current_tok
                error = InvalidSyntaxError(tok.start_pos, tok.end_pos, "Expected closing ')'.")
                return ParseResult.fail(error)

            if expr_res._error:
                error = InvalidSyntaxError(l_paren.end_pos, r_paren.start_pos, "Expected an expression, variable or literal.")
                return ParseResult.fail(error) 

            return expr_res

        tok = self.current_tok
        error = InvalidSyntaxError(tok.start_pos, tok.end_pos, "Expected an expression, variable or literal.")
        return ParseResult.fail(error)

    def try_consume_token(self, token_types: list[str] = [], token_values: list[str] = []) -> Optional[Token]:
        """
        Attempts to consume a given token if it matches the supplied requirements. Returns None if fail.
        """
        tok = self.current_tok
        if len(token_types) == 0:
            return tok

        if tok.token_type in token_types:
            if len(token_values) == 0 or tok.value in token_values:
                return tok

        return None

    def try_consume_keyword(self, keywords: list[str]) -> Optional[Token]:
        return self.try_consume_token([TT_KEYWORD], keywords)

    def try_consume_identifier(self) -> Optional[Token]:
        return self.try_consume_token([TT_IDENTIFIER])

    def try_consume_seperator(self, seperator: str):
        return self.try_consume_token([TT_SEPERATOR], [seperator])

    def try_consume_operator(self, operators: list[str]):
        return self.try_consume_token([TT_OPERATOR], operators)