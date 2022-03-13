from position import Position
from dataclasses import dataclass
from strings_with_arrows import string_with_arrows


@dataclass
class Error:
    error_name: str
    start_pos: Position
    end_pos: Position
    details: str

    def as_string(self):
        file_contents = self.start_pos.file_contents
        filename = self.start_pos.filename

        result = f"{self.error_name}: {self.details}" + "\n"
        result += f'File {filename}, line {self.start_pos.line + 1}' + "\n\n"
        result += string_with_arrows(file_contents, self.start_pos, self.end_pos)
        return result

class IllegalCharError(Error):
	def __init__(self, start_pos, end_pos, details):
		super().__init__('Illegal Character', start_pos, end_pos, details)

class InvalidSyntaxError(Error):
    def __init__(self, start_pos, end_pos, details):
        super().__init__('Invalid Syntax Error', start_pos, end_pos, details)