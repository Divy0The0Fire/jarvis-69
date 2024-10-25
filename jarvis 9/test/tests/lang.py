class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        """Advance the `pos` pointer and set `current_char`."""
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        """Skip over whitespace."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def lex_string(self):
        """Parse a string enclosed in double quotes."""
        result = ''
        self.advance()  # Skip opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # Skip closing quote
        return result

    def lex_number(self):
        """Parse a number."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def lex_identifier(self):
        """Parse an identifier, which can be a function name or an argument name."""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def lex_list(self):
        """Parse a list enclosed in square brackets."""
        elements = []
        self.advance()  # Skip the opening '['
        while self.current_char != ']':
            if self.current_char == '"':  # Parse strings inside the list
                elements.append(self.lex_string())
            elif self.current_char.isdigit():  # Parse numbers inside the list
                elements.append(self.lex_number())
            elif self.current_char == '[':  # Parse nested lists
                elements.append(self.lex_list())
            elif self.current_char == ',':
                self.advance()  # Skip commas
            else:
                self.advance()  # Skip other characters
        self.advance()  # Skip the closing ']'
        return elements

    def lex(self):
        """Lexical analyzer that converts the input into tokens."""
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
            elif self.current_char.isalnum() or self.current_char == '_':
                tokens.append(Token('ID', self.lex_identifier()))
            elif self.current_char == '"':
                tokens.append(Token('STRING', self.lex_string()))
            elif self.current_char == '=':
                tokens.append(Token('EQUALS', '='))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token('COMMA', ','))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token('LPAREN', '('))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token('RPAREN', ')'))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token('LIST', self.lex_list()))
            else:
                self.advance()
        return tokens


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = self.lexer.lex()
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def eat(self, token_type):
        """Consume a token of a particular type."""
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            raise Exception(f"Unexpected token {self.current_token.type}")

    def parse_function_call(self):
        """Parse a function call like `fn1(query="print(2+2)")`."""
        func_name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')

        args = {}
        while self.current_token.type != 'RPAREN':
            arg_name = self.current_token.value
            self.eat('ID')
            self.eat('EQUALS')

            if self.current_token.type == 'STRING':
                arg_value = self.current_token.value
                self.eat('STRING')
            elif self.current_token.type == 'LIST':
                arg_value = self.current_token.value
                self.eat('LIST')
            else:
                raise Exception(f"Unexpected token {self.current_token.type}")

            args[arg_name] = arg_value
            if self.current_token.type == 'COMMA':
                self.eat('COMMA')

        self.eat('RPAREN')
        return [func_name, args]

    def parse(self):
        """Parse the entire input to produce a list of function calls."""
        result = []
        while self.pos < len(self.tokens):
            result.append(self.parse_function_call())
            if self.pos < len(self.tokens) and self.current_token.type == 'COMMA':
                self.eat('COMMA')
        return result


# Testing the lexer, parser, and final output
def main():
    text = 'fn1(query="print(2+2)"), url(url=["https://www.dominos.com/", \'1\', [[1.00],2,3]])'
    lexer = Lexer(text)
    parser = Parser(lexer)
    result = parser.parse()
    print(result)  
    # Expected output: 
    # [['fn1', {'query': 'print(2+2)'}], ['url', {'url': ['https://www.dominos.com/', [1, 2, 3]]}]]

if __name__ == '__main__':
    main()
