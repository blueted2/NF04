import lexer
import parser

t = "1 + (  )"

lex = lexer.Lexer(t)
tokens, error = lex.generate_tokens()

if error:
    print(error.as_string())
    exit()
print(tokens)

par = parser.Parser(tokens)
res, error = par.parse()

if error:
    print(error.as_string())
