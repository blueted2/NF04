from dataclasses import dataclass

@dataclass
class Position:
    index: int
    line: int
    column: int
    file_contents: str
    filename: str = "<unnamed>"

    def next(self, current_char=None):
        index = self.index + 1
        column = self.column + 1
        line = self.line

        if current_char == "\n":
            line += 1
            column = 0

        return Position(index, line, column, self.file_contents, self.filename)