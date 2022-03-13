TT_FLOAT   = "float"
TT_INT     = "int"
TT_PLUS    = "plus"
TT_MINUS   = "minus"
TT_MUL     = "mul"
TT_DIV     = "div"
TT_L_PAREN = "l_paren"
TT_R_PAREN = "r_paren"
TT_LT      = "lt"
TT_GT      = "gt"
TT_EQUALS  = "equals"
TT_IDENT   = "ident"
TT_KEYWORD = "keyword"
TT_EOF     = "eof"

SINGLE_CHAR_TOKENS = {
    "+": TT_PLUS,
    "-": TT_MINUS,
    "*": TT_MUL,
    "/": TT_DIV,
    "(": TT_L_PAREN,
    ")": TT_R_PAREN,
    "<": TT_LT,
    ">": TT_GT,
    "=": TT_EQUALS
}

KEYWORDS = [
    "pour",
    "allant",
    "de",
    "par",
    "pas",
    "de",
    "faire"
]