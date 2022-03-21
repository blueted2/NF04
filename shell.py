from typing import cast
import lexer
import parser
from tokens import Token

with open("program.NF04", 'r') as fp:
    text = fp.read()

lex = lexer.Lexer(text)
tokens, error = lex.generate_tokens()

if error is not None:
    print(error.as_string())
    exit()

tokens = cast(list[Token], tokens)
print(tokens)

par = parser.Parser(tokens)
parse_res = par.parse()

if parse_res.has_error:
    print(parse_res.error.as_string())
else:
    print(parse_res.node)
