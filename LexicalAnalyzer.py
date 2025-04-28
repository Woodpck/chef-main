# CONSTANTS
EOF = '←'

ALPHA_BIG = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}
ALPHA_SMALL = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}
ALL_ALPHA = ALPHA_BIG | ALPHA_SMALL
ALL_NUM = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
ALPHA_NUM = ALL_ALPHA | ALL_NUM
UNDER_ALPHA_NUM = ALPHA_NUM | {'_'}

WHITE_SPACE = {' ', '\t', '\n'}
BOOL_DELIM = {';', ' ', ')', ',', '(', '<', '>', '&', '|'}
DT_DELIM = {' ', '\t'}
SPACE_DELIM = {' '}
SEMICOLON_DELIM = {';'}
COLON_DELIM = {':'}
NEWLINE_DELIM = {'\n'}
OPARAN_DELIM = {'('}
PASTA_DELIM = {"\t",',', ';', ' ', ':', ')', '}', '+'}
NUM_DELIM = {' ', '?', '+', '>', '-', ';', ')', '<', '*', '/', '=', '%', ']', ',','{','}', ':'}
OP_DELIM = {'+', '-', '*', '/', '%', '**'}
ID_DELIM = {' ', ';', ',', '.', '(', ')', '{', '[', ']', '='} | OP_DELIM

DELIM_1 = {' ', '"', '(', '~'} | ALPHA_NUM
DELIM_3 = {' ', '(', '~'} | ALPHA_NUM
DELIM_4 = {';', ')'} | ALPHA_NUM
DELIM_5 = {' ', '!', '('} | ALPHA_NUM
DELIM_6 = {'"', '~', '\'', ' '} | ALPHA_NUM
DELIM_8 = {' ', '~', '"', '\'', '('} | ALPHA_NUM
DELIM_12 = {')', '!', '\'', '"', ' ', '('} | ALPHA_NUM
DELIM_13 = {';', '{', ')', '<', '>', '=', '?', '&', '+', '-', '/', '*', '%', ' ', '!'}
DELIM_14 = {']', ' '} | ALPHA_NUM
DELIM_15 = {'=', ';', ' ', '\n', '[',"("}
DELIM_16 = {'\'', '"', '~', ' ', '\n', '{'} | ALPHA_NUM
DELIM_17 = {';', '}', ',', ' '  , '\n'} | ALPHA_SMALL

# TOKENS
TT_BLEH = 'bleh'
TT_BOOL = 'bool'
TT_CASE = 'case'
TT_CHEF = 'chef'
TT_CHOP = 'chop'
TT_DEFAULT = 'default'
TT_DINEIN = 'dinein'
TT_DISH = 'dish'
TT_ELIF = 'elif'
TT_FLIP = 'flip'
TT_FOR = 'for'
TT_FULL = 'full'
TT_HUNGRY = 'hungry'
TT_KEEPMIX = 'keepmix'
TT_MAKE = 'make'
TT_MIX = 'mix'
TT_PASTA = 'pasta'
TT_PINCH = 'pinch'
TT_RECIPE = 'recipe'
TT_SERVE = 'serve'
TT_SIMMER = 'simmer'
TT_SKIM = 'skim'
TT_SPIT = 'spit'
TT_TAKEOUT = 'takeout'
TT_TASTE = 'taste'
TT_YUM = 'yum'

TT_MINUS = '-'
TT_MINUS_EQUAL = '-='
TT_DECREMENT = '--'
TT_COMMA = ','
TT_NEGATE_OP = '!'
TT_LOGICAL_NOT = '!!'
TT_NOT_EQUAL = '!='
TT_LOGICAL_OR = '??'
TT_OPARAN = '('
TT_CPARAN = ')'
TT_OBRACE = '['
TT_CBRACE = ']'
TT_OBRACK = '{'
TT_CBRACK = '}'
TT_MULTIPLY = '*'
TT_MULTIPLY_EQUAL = '*='
TT_DIVIDE = '/'
TT_DIVIDE_EQUAL = '/='
TT_LOGICAL_AND = '&&'
TT_MODULO = '%'
TT_MODULO_EQUAL = '%='
TT_PLUS = '+'
TT_INCREMENT = '++'
TT_PLUS_EQUAL = '+='
TT_LESS_THAN = '<'
TT_LESS_THAN_EQUAL = '<='
TT_ASSIGN = '='
TT_EQUAL_TO = '=='
TT_GREATER_THAN = '>'
TT_GREATER_THAN_EQUAL = '>='

TT_PASTA_LITERAL = 'pastaliterals'
TT_PINCH_LITERAL = 'pinchliterals'
TT_SKIM_LITERAL = 'skimliterals'
TT_IDENTIFIER = 'identifier'

TT_SEMI_COLON = ';'
TT_COLON = ':'

# ERRORS
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        '''This formats the error message like: `Lexical Error: Invalid character '@' at line X, column Y`'''
        result = f'{self.error_name}: {self.details} at line {self.pos_start.ln + 1}, column {self.pos_start.col + 1}\n'
        result += f'    {self.get_error_line()}\n'
        result += f'    {"~" * (self.pos_start.col)}^'          # Error pointer
        
        # # Add the error line where the invalid character was found
        # error_line = self.get_error_line()
        # if error_line:  # If there's an error line, append it
        #     result += f'    {error_line}\n'
        #     result += f'    {"~" * (self.pos_start.col)}^'  # Error pointer
        # else:
        #     result += "    Error line not found.\n"
        
        return result

    def get_error_line(self):
        '''This method returns the line of code that caused the error'''
        lines = self.pos_start.ftxt.split('\n')
        return lines[self.pos_start.ln] if self.pos_start.ln < len(lines) else ""
    
        # print(f'[Get_error-line]: lines variable contains: {lines}')
        # if self.pos_start.ln < len(lines):
        #     return lines[self.pos_start.ln]
        # else:
        #     print(f"Error: Line index {self.pos_start.ln} out of range for file.")
        #     print(f"File content: {self.pos_start.ftxt}")  # Debugging
        #     return ""  # In case of invalid line index

# NEW INVALID CLASS
class LexicalError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "LexicalError", details)

# POSITION
class Position:
    def __init__(self, idx, ln, col, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.ftxt = ftxt

    def track_next_character(self, current_character):
        self.idx += 1
        self.col += 1

        if current_character == '\n':
            self.ln += 1                # Move to the next line
            self.col = 0                # Reset column to 0
        
        # Debugging line
        # print(f"Tracking character: {current_character} at line {self.ln}, column {self.col}")  
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.ftxt)

# LEXER
class LexicalAnalyzer:
    def __init__(self):
        self.code = None
        self.pos = None
        self.current_character = None
        self.identifier_count = 0
        self.line_number = 1                        # Start tracking line number from 1
        
    def initialize_lexer(self, code):
        self.code = code + EOF                      # Append EOF to signal end of file
        self.pos = Position(-1, 0, -1, code)        # Position starts at index 0
        self.read_next_character()                  # Set the first character

    def read_next_character(self):
        self.pos.track_next_character(self.current_character)
        self.current_character = self.code[self.pos.idx] if self.pos.idx < len(self.code) else None

    def match_char_and_advance(self, expected_char):
        if self.current_character == expected_char:
            self.read_next_character()
            return True
        return False
    
    def reserve_and_transition(self, string_buffer, next_state):
        string_buffer += self.current_character     # Collect the current character
        return string_buffer, next_state

    def fallback_to_identifier(self, position, next_state):
        self.pos = position.copy()
        self.current_character = self.code[self.pos.idx] if self.pos.idx < len(self.code) else None
        fall_back = self.current_character
        self.read_next_character()
        return fall_back, next_state

    def check_delimiter(self, delimiter_set):
        # !IMPORTANT: Revisit EOF logic
        return self.current_character in delimiter_set or self.current_character == EOF

    def emit_token(self, tokens, token_type, value):
        tokens.append((value, token_type, self.pos.ln))
    
    def process_string_literal(self, string_literal, next_state):
        ESCAPE_MAP = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t'}

        if self.match_char_and_advance('\\'):               # If backslash found, handle escape sequences
            escape_char = self.current_character
            if escape_char in ESCAPE_MAP:
                string_literal += ESCAPE_MAP[escape_char]
            else:
                string_literal += escape_char               # If unknown escape, include as-is
        else:
            string_literal += self.current_character        # Regular character in literal

        self.read_next_character()                          # Ensure you're reading the next character here

        return string_literal, next_state

    def append_digit_and_advance(self, literal: str) -> tuple[bool, str]:
        if self.current_character.isdigit():
            literal += self.current_character
            self.read_next_character()
            return True, literal
        return False, literal

    def display_lexical_error(self, start_pos, end_pos, error_ref, error_message):
        self.read_next_character()
        error_ref.append(LexicalError(start_pos, end_pos, error_message))

    def tokenize(self, code):
        tokens = []
        errors = []
        state = 0

        self.initialize_lexer(code)
        print(self.code)

        while self.current_character is not None:
            start_position = self.pos.copy()
            # Debugging state and current character
            print(f"Index: {self.pos.idx}, Current Character: '{self.current_character}', State: {state}")

            if state == 0:
                str_buffer = ""
                str_start_ = self.pos.copy()
                pasta_literal = ""

                # reserved words
                if self.match_char_and_advance('b'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 1)
                elif self.match_char_and_advance('c'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 10)
                elif self.match_char_and_advance('d'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 22)
                elif self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 39)
                elif self.match_char_and_advance('f'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 44)
                elif self.match_char_and_advance('h'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 56)
                elif self.match_char_and_advance('k'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 63)
                elif self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 71)
                elif self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 79)
                elif self.match_char_and_advance('r'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 90)
                elif self.match_char_and_advance('s'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 97)
                elif self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 117)
                elif self.match_char_and_advance('y'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 129)
                # in original lexer, they skipped 133
                # in original lexer, they skipped 135
                # in original lexer, they skipped 137
                # reserved symbols
                elif    self.match_char_and_advance('-'):       state = 139
                elif    self.match_char_and_advance(','):       state = 145
                elif    self.match_char_and_advance('!'):       state = 147
                elif    self.match_char_and_advance('?'):       state = 153
                elif    self.match_char_and_advance('('):       state = 156
                elif    self.match_char_and_advance(')'):       state = 158
                elif    self.match_char_and_advance('['):       state = 160
                elif    self.match_char_and_advance(']'):       state = 162
                elif    self.match_char_and_advance('{'):       state = 164
                elif    self.match_char_and_advance('}'):       state = 166
                elif    self.match_char_and_advance('*'):       state = 168
                elif    self.match_char_and_advance('/'):       state = 172
                elif    self.match_char_and_advance('&'):       state = 181
                elif    self.match_char_and_advance('%'):       state = 184
                elif    self.match_char_and_advance('+'):       state = 188
                elif    self.match_char_and_advance('<'):       state = 194
                elif    self.match_char_and_advance('='):       state = 198
                elif    self.match_char_and_advance('>'):       state = 202
                elif    self.match_char_and_advance('"'):       state = 206
                
                # pinch and skim literals 
                elif self.current_character == '~':
                    is_negative = True
                    negative_sign_pos = self.pos.copy()
                    self.read_next_character()
                    state = 209
                elif self.current_character.isdigit():       
                    is_negative = False
                    state = 209
                
                # identifiers
                elif self.current_character.islower():
                    identifier = self.current_character
                    self.read_next_character()
                    state = 231

                elif    self.match_char_and_advance(';'):       state = 235
                elif    self.match_char_and_advance(':'):       state = 237
                elif    self.check_delimiter(WHITE_SPACE):      self.read_next_character()          # Captures space, newline, and tab                    
                else:
                    '''Captures characters not present above like: @'''
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0

            elif state == 1:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 2)
                elif self.match_char_and_advance('o'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 6)
                else:
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 2:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 3)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 3:
                if self.match_char_and_advance('h'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 4)
                else:                                               
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 4:
                if self.check_delimiter(BOOL_DELIM):       
                    state = 5
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 5:
                self.emit_token(tokens, TT_BLEH, 'bleh')
                state = 0
            elif state == 6:
                if self.match_char_and_advance('o'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 7)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 7:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 8)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 8:
                if self.check_delimiter(DT_DELIM):         
                    state = 9
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 9:
                self.emit_token(tokens, TT_BOOL, 'bool')
                state = 0
            elif state == 10:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 11)
                elif self.match_char_and_advance('h'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 15)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 11:
                if self.match_char_and_advance('s'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 12)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 12:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 13)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 13:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 14
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 14:
                self.emit_token(tokens, TT_CASE, 'case')
                state = 0
            elif state == 15:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 16)
                elif self.match_char_and_advance('o'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 19)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 16:
                if self.match_char_and_advance('f'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 17)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 17:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 18
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 18:
                self.emit_token(tokens, TT_CHEF, 'chef')
                state = 0
            elif state == 19:
                if self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 20)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 20:
                if self.check_delimiter(SEMICOLON_DELIM):  
                    state = 21
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 21:
                self.emit_token(tokens, TT_CHOP, 'chop')
                state = 0
            elif state == 22:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 23)
                elif self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 30)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 23:
                if self.match_char_and_advance('f'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 24)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 24:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 25)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 25:
                if self.match_char_and_advance('u'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 26)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 26:                                               
                if self.match_char_and_advance('l'):
                    str_buffer, state = self.reserve_and_transition(str_buffer, 27)
                else:
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 27:
                if self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 28)
                else:
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 28:
                if self.check_delimiter(COLON_DELIM):      
                    state = 29
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 29:
                self.emit_token(tokens, TT_DEFAULT, 'default')
                state = 0
            elif state == 30:
                if self.match_char_and_advance('n'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 31)
                elif self.match_char_and_advance('s'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 36)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 31:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 32)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 32:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 33)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 33:
                if self.match_char_and_advance('n'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 34)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 34:
                if self.check_delimiter(NEWLINE_DELIM):    
                    state = 35
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 35:
                self.emit_token(tokens, TT_DINEIN, 'dinein')
                state = 0
            elif state == 36:
                if self.match_char_and_advance('h'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 37)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 37:
                if self.check_delimiter(OPARAN_DELIM):     
                    state = 38
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 38:
                self.emit_token(tokens, TT_DISH, 'dish')
                state = 0
            elif state == 39:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 40)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 40:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 41)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 41:
                if self.match_char_and_advance('f'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 42)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 42:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 43          # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 43:
                self.emit_token(tokens, TT_ELIF, 'elif')
                state = 0
            elif state == 44:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 45)
                elif self.match_char_and_advance('o'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 49)
                elif self.match_char_and_advance('u'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 52)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 45:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 46)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 46:
                if self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 47)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 47:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 48          # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 48:
                self.emit_token(tokens, TT_FLIP, 'flip')
                state = 0
            elif state == 49:
                if self.match_char_and_advance('r'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 50)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 50:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 51          # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 51:
                self.emit_token(tokens, TT_FOR, 'for')
                state = 0
            elif state == 52:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 53)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 53:
                if self.match_char_and_advance('l'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 54)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 54:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 55          # In docs, this is dt_delim
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 55:
                self.emit_token(tokens, TT_FULL, 'full')
                state = 0
            elif state == 56:
                if self.match_char_and_advance('u'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 57)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 57:
                if self.match_char_and_advance('n'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 58)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 58:
                if self.match_char_and_advance('g'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 59)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 59:
                if self.match_char_and_advance('r'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 60)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 60:
                if self.match_char_and_advance('y'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 61)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 61:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 62
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 62:
                self.emit_token(tokens, TT_HUNGRY, 'hungry')
                state = 0
            elif state == 63:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 64)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 64:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 65)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 65:
                if self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 66)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 66:
                if self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 67)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 67:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 68)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 68:
                if self.match_char_and_advance('x'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 69)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 69:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 70          # In docs, this is delim2
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 70:
                self.emit_token(tokens, TT_KEEPMIX, 'keepmix')
                state = 0
            elif state == 71:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 72)
                elif self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 76)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 72:
                if self.match_char_and_advance('k'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 73)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 73:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 74)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 74:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 75          # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 75:
                self.emit_token(tokens, TT_MAKE, 'make')
                state = 0
            elif state == 76:
                if self.match_char_and_advance('x'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 77)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 77:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 78          # In docs, this is delim2
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 78:
                self.emit_token(tokens, TT_MIX, 'mix')
                state = 0
            elif state == 79:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 80)
                elif self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 85)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 80:
                if self.match_char_and_advance('s'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 81)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 81:
                if self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 82)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 82:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 83)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 83:
                if self.check_delimiter(DT_DELIM):         
                    state = 84
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 84:
                self.emit_token(tokens, TT_PASTA, 'pasta')
                state = 0
            elif state == 85:
                if self.match_char_and_advance('n'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 86)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 86:
                if self.match_char_and_advance('c'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 87)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 87:
                if self.match_char_and_advance('h'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 88)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 88:
                if self.check_delimiter(DT_DELIM):         
                    state = 89
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 89:
                self.emit_token(tokens, TT_PINCH, 'pinch')
                state = 0
            elif state == 90:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 91)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 91:
                if self.match_char_and_advance('c'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 92)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 92:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 93)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 93:
                if self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 94)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 94:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 95)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 95:
                if self.check_delimiter(DT_DELIM):         
                    state = 96
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 96:
                self.emit_token(tokens, TT_RECIPE, 'recipe')
                state = 0
            elif state == 97:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 98)
                elif self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 103)
                elif self.match_char_and_advance('k'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 109)
                elif self.match_char_and_advance('p'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 113)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 98:
                if self.match_char_and_advance('r'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 99)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 99:
                if self.match_char_and_advance('v'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 100)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 100:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 101)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 101:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 102         # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 102:
                self.emit_token(tokens, TT_SERVE, 'serve')
                state = 0
            elif state == 103:
                if self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 104)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 104:
                if self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 105)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 105:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 106)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 106:
                if self.match_char_and_advance('r'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 107)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 107:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 108         # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 108:
                self.emit_token(tokens, TT_SIMMER, 'simmer')
                state = 0
            elif state == 109:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 110)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 110:
                if self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 111)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 111:
                if self.check_delimiter(DT_DELIM):         
                    state = 112
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 112:
                self.emit_token(tokens, TT_SKIM, 'skim')
                state = 0
            elif state == 113:
                if self.match_char_and_advance('i'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 114)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 114:
                if self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 115)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 115:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 116
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 116:
                self.emit_token(tokens, TT_SPIT, 'spit')
                state = 0
            elif state == 117:
                if self.match_char_and_advance('a'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 118)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 118:
                if self.match_char_and_advance('k'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 119)
                elif self.match_char_and_advance('s'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 125)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 119:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 120)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 120:
                if self.match_char_and_advance('o'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 121)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 121:
                if self.match_char_and_advance('u'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 122)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 122:
                if self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 123)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 123:
                if self.check_delimiter(WHITE_SPACE):      
                    state = 124
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 124:
                self.emit_token(tokens, TT_TAKEOUT, 'takeout')
                state = 0
            elif state == 125:
                if self.match_char_and_advance('t'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 126)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 126:
                if self.match_char_and_advance('e'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 127)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 127:
                if self.check_delimiter(SPACE_DELIM):      
                    state = 128         # In docs, this is delim0
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 128:
                self.emit_token(tokens, TT_TASTE, 'taste')
                state = 0
            elif state == 129:
                if self.match_char_and_advance('u'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 130)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 130:
                if self.match_char_and_advance('m'):       
                    str_buffer, state = self.reserve_and_transition(str_buffer, 131)
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 131:
                if self.check_delimiter(BOOL_DELIM):       
                    state = 132
                else:                                           
                    identifier, state = self.fallback_to_identifier(str_start_, 231)
            elif state == 132:
                self.emit_token(tokens, TT_YUM, 'yum')
                state = 0
            # in original lexer, they skipped 133
            # in original lexer, they skipped 135
            # in original lexer, they skipped 137
            elif state == 139:
                if      self.check_delimiter(DELIM_3):          state = 140         # Check DELIM_3 delimiters
                elif    self.match_char_and_advance('-'):       state = 141
                elif    self.match_char_and_advance('='):       state = 143
                else:
                    '''Captures example: a -: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 140:
                self.emit_token(tokens, TT_MINUS, '-')
                state = 0
            elif state == 141:
                if      self.check_delimiter(DELIM_4):          state = 142
                else:
                    '''Captures example: a--! or --!a'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 142:
                self.emit_token(tokens, TT_DECREMENT, '--')
                state = 0
            elif state == 143:
                if      self.check_delimiter(DELIM_5):          state = 144         # Check DELIM_5 delimiters
                else:
                    '''Captures example: a -=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 144:
                self.emit_token(tokens, TT_MINUS_EQUAL, '-=')
                state = 0
            elif state == 145:
                if      self.check_delimiter(DELIM_6):          state = 146
                else:
                    '''Captures example: a,: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 146:
                self.emit_token(tokens, TT_COMMA, ',')
                state = 0
            elif state == 147:
                if      self.check_delimiter(OPARAN_DELIM):     state = 148         # In docs, this is delim7
                elif    self.match_char_and_advance('!'):       state = 149
                elif    self.match_char_and_advance('='):       state = 151
                else:
                    '''Captures example: !:(a)'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}', expected '!' or '('")
                    state = 0
            elif state == 148:
                self.emit_token(tokens, TT_NEGATE_OP, '!')
                state = 0
            elif state == 149:
                if      self.check_delimiter(DELIM_3):          state = 150
                else:
                    '''Captures example: !!:(a)'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 150:
                self.emit_token(tokens, TT_LOGICAL_NOT, '!!')
                state = 0
            elif state == 151:
                if      self.check_delimiter(DELIM_8):          state = 152
                else:
                    '''Captures example: a !=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 152:
                self.emit_token(tokens, TT_NOT_EQUAL, '!=')
                state = 0
            elif state == 153:
                if      self.match_char_and_advance('?'):       state = 154
                else:
                    '''Captures example: a ?: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}', expected '?'")
                    state = 0
            elif state == 154:
                if      self.check_delimiter(DELIM_3):          state = 155
                else:
                    '''Captures example: a ??: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 155:
                self.emit_token(tokens, TT_LOGICAL_OR, '??')
                state = 0
            elif state == 156:
                if      self.check_delimiter(DELIM_12):         state = 157
                else:
                    '''Captures example: (:a < b)'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 157:
                self.emit_token(tokens, TT_OPARAN, '(')
                state = 0
            elif state == 158:
                if      self.check_delimiter(DELIM_13):         state = 159
                else:
                    '''Captures example: (a < b)'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 159:
                self.emit_token(tokens, TT_CPARAN, ')')
                state = 0
            elif state == 160:
                if      self.check_delimiter(DELIM_14):         state = 161
                else:
                    '''Captures example: a[:4]'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 161:
                self.emit_token(tokens, TT_OBRACE, '[')
                state = 0
            elif state == 162:
                if      self.check_delimiter(DELIM_15):         state = 163
                else:
                    '''Captures example: a[4]:'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 163:
                self.emit_token(tokens, TT_CBRACE, ']')
                state = 0
            elif state == 164:
                if      self.check_delimiter(DELIM_16):         state = 165
                else:
                    '''Captures example: {:'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 165:
                self.emit_token(tokens, TT_OBRACK, '{')
                state = 0
            elif state == 166:
                if      self.check_delimiter(DELIM_17):         state = 167
                else:
                    '''Captures example: }:'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 167:
                self.emit_token(tokens, TT_CBRACK, '}')
                state = 0
            elif state == 168:
                if      self.check_delimiter(DELIM_3):          state = 169         # Set to similar delim as -
                elif    self.match_char_and_advance('='):       state = 170         # This is *=, there is no mention in docs transition diagram
                else:
                    '''Captures example: a *: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 169:
                self.emit_token(tokens, TT_MULTIPLY, '*')
                state = 0
            elif state == 170:
                if      self.check_delimiter(DELIM_5):          state = 171         # Set to similar delim as -=
                else:
                    '''Captures example: a *=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 171:
                self.emit_token(tokens, TT_MULTIPLY_EQUAL, '*=')
                state = 0
            elif state == 172:
                if      self.check_delimiter(DELIM_3):          state = 173         # In docs, delimiter is single comment but it should be division so changed it to DELIM_3, will test
                elif    self.match_char_and_advance('='):       state = 174         # In docs, there is no /= in transition diagram but they have the operation in practice
                elif    self.match_char_and_advance('/'):       state = 176         # This is for singleline comment
                elif    self.match_char_and_advance('-'):       state = 178         # This is for multiline comment
                else:
                    '''Captures example: a /: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 173:
                self.emit_token(tokens, TT_DIVIDE, '/')
                state = 0
            elif state == 174:
                if      self.check_delimiter(DELIM_5):          state = 175
                else:
                    '''Captures example: a /=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 175:
                self.emit_token(tokens, TT_DIVIDE_EQUAL, '/=')
                state = 0
            elif state == 176:
                if     (self.current_character != '\n' and 
                        self.current_character != EOF):         self.read_next_character()
                else:                                           state = 177
            elif state == 177:
                self.read_next_character()
                state = 0
            # !REVISIT: Handle unterminated multi-line comment lexical error
            elif state == 178:
                if      self.match_char_and_advance('-'):       state = 179       
                else:                                           self.read_next_character()
            elif state == 179:
                if      self.match_char_and_advance('/'):       state = 180
                else:                                           self.read_next_character()
            elif state == 180:
                state = 0
            elif state == 181:
                if      self.match_char_and_advance('&'):       state = 182
                else:                                           
                    '''Captures example: a &: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}', expected '&'")
                    state = 0
            elif state == 182:
                if      self.check_delimiter(DELIM_3):          state = 183
                else:
                    '''Captures example: a &&: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 183:
                self.emit_token(tokens, TT_LOGICAL_AND, '&&')
                state = 0
            elif state == 184:
                if      self.check_delimiter(DELIM_3):          state = 185
                elif    self.match_char_and_advance('='):       state = 186
                else:
                    '''Captures example: a %: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 185:
                self.emit_token(tokens, TT_MODULO, '%')
                state = 0
            elif state == 186:
                if      self.check_delimiter(DELIM_5):          state = 187
                else:
                    '''Captures example: a %=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 187:
                self.emit_token(tokens, TT_MODULO_EQUAL, '%=')
                state = 0
            elif state == 188:
                if      self.check_delimiter(DELIM_1):          state = 189
                elif    self.match_char_and_advance('+'):       state = 190
                elif    self.match_char_and_advance('='):       state = 192
                else:
                    '''Captures example: a +: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 189:
                self.emit_token(tokens, TT_PLUS, '+')
                state = 0
            elif state == 190:
                if      self.check_delimiter(DELIM_4):          state = 191
                else:
                    '''Captures example: a++! or ++!a'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 191:
                self.emit_token(tokens, TT_INCREMENT, '++')
                state = 0
            elif state == 192:
                if      self.check_delimiter(DELIM_5):          state = 193
                else:
                    '''Captures example: a +=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 193:
                self.emit_token(tokens, TT_PLUS_EQUAL, '+=')
                state = 0
            elif state == 194:
                if      self.check_delimiter(DELIM_3):          state = 195
                elif    self.match_char_and_advance('='):       state = 196
                else:
                    '''Captures example: a <: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 195:
                self.emit_token(tokens, TT_LESS_THAN, '<')
                state = 0
            elif state == 196:
                if      self.check_delimiter(DELIM_5):          state = 197
                else:                                           
                    '''Captures example: a <=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 197:
                self.emit_token(tokens, TT_LESS_THAN_EQUAL, '<=')
                state = 0
            elif state == 198:
                if      self.check_delimiter(DELIM_8):          state = 199
                elif    self.match_char_and_advance('='):       state = 200
                else:
                    '''Captures example: a =! b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 199:
                self.emit_token(tokens, TT_ASSIGN, '=')
                state = 0
            elif state == 200:
                if      self.check_delimiter(DELIM_8):          state = 201
                else:
                    '''Captures example: a ==> b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 201:
                self.emit_token(tokens, TT_EQUAL_TO, '==')
                state = 0
            elif state == 202:
                if      self.check_delimiter(DELIM_3):          state = 203
                elif    self.match_char_and_advance('='):       state = 204
                else:                                           
                    '''Captures example: a >: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 203:
                self.emit_token(tokens, TT_GREATER_THAN, '>')
                state = 0
            elif state == 204:
                if      self.check_delimiter(DELIM_5):          state = 205         # In docs, this is delim3
                else:
                    '''Captures example: a >=: b'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
            elif state == 205:
                self.emit_token(tokens, TT_GREATER_THAN_EQUAL, '>=')
                state = 0
            elif state == 206:
                MAX_PASTA_LITERAL_LENGTH = 256
                if (self.current_character not in {EOF, '\n', '"'} and 
                    len(pasta_literal) < MAX_PASTA_LITERAL_LENGTH):
                    pasta_literal, state = self.process_string_literal(pasta_literal, 206)
                elif self.match_char_and_advance('"'):
                    state = 207
                elif self.current_character in {EOF, '\n'}:
                    '''Captures example: "Hello World;'''
                    self.display_lexical_error(str_start_.copy(), self.pos.copy(), errors, f"Unterminated pastaliteral")
                    state = 0
                else:
                    '''Captures pasta literal that exceeds 256 characters'''
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Pastaliteral exceeds {MAX_IDENTIFIER_LENGTH} characters")
                    state = 0
            elif state == 207:
                if      self.check_delimiter(PASTA_DELIM):      state = 208
                else:
                    '''Captures example: "Hello World"-'''
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid delimiter '{invalid_character}', expected ',' or ';'")
                    state = 0
            elif state == 208:
                self.emit_token(tokens, TT_PASTA_LITERAL, f'"{pasta_literal}"')
                state = 0
            elif state == 209:
                number_literal = "-" if is_negative else ""
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 210
                else:                                           
                    '''Captures example: ~ without number after'''
                    self.display_lexical_error(negative_sign_pos, self.pos, errors, f"Expected digit after '~'")
                    state = 0
            elif state == 210:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 211
                else:                                           state = 218
            elif state == 211:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 212
                else:                                           state = 218
            elif state == 212:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 213
                else:                                           state = 218
            elif state == 213:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 214
                else:                                           state = 218
            elif state == 214:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 215
                else:                                           state = 218
            elif state == 215:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 216
                else:                                           state = 218
            elif state == 216:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 217
                else:                                           state = 218
            elif state == 217:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 218
                else:                                           state = 218
            elif state == 218:
                if      self.check_delimiter(NUM_DELIM):        state = 219
                elif    self.current_character == '.':
                    decimal_pos = self.pos.copy()
                    self.read_next_character()      
                    state = 220
                elif not self.current_character.isdigit():
                    '''Captures example: 123a'''
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid suffix '{invalid_character}' on pinchliteral")
                    state = 0
                else:
                    '''Captures example: 1234567891'''              
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Pinchliteral exceeds 9 digits")
                    state = 0
            elif state == 219:
                self.emit_token(tokens, TT_PINCH_LITERAL, number_literal)
                state = 0
            elif state == 220:
                number_literal += '.'
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 221
                else:                                           state = 229
            elif state == 221:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 222
                else:                                           state = 229
            elif state == 222:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 223
                else:                                           state = 229
            elif state == 223:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 224
                else:                                           state = 229
            elif state == 224:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 225
                else:                                           state = 229
            elif state == 225:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 226
                else:                                           state = 229
            elif state == 226:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 227
                else:                                           state = 229
            elif state == 227:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 228
                else:                                           state = 229
            elif state == 228:
                is_digit, number_literal = self.append_digit_and_advance(number_literal)
                if      is_digit:                               state = 229
                else:                                           state = 229
            elif state == 229:
                if number_literal.endswith('.'):
                    '''Captures example: 123. without number after'''
                    self.display_lexical_error(decimal_pos, self.pos, errors, f"Expected digit after '.'")
                    state = 0
                elif self.check_delimiter(NUM_DELIM):        
                    state = 230
                elif self.current_character == '.':
                    '''Captures example: 123..1 or 123.1.1'''
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Expected single '.' in skimliteral")
                    state = 0
                elif not self.current_character.isdigit():
                    '''Captures example: 123.a'''
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid suffix '{invalid_character}' on skimliteral")
                    state = 0
                else:
                    '''Captures example: 0.1234567891'''
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Skimliteral exceeds 9 digits")
                    state = 0
            elif state == 230:
                self.emit_token(tokens, TT_SKIM_LITERAL, number_literal)
                state = 0
            elif state == 231:
                MAX_IDENTIFIER_LENGTH = 32
                if (self.current_character in UNDER_ALPHA_NUM and 
                    len(identifier) < MAX_IDENTIFIER_LENGTH):
                    identifier += self.current_character
                    self.read_next_character()
                    state = 231                                                         # Stay in the same state to collect more characters
                elif self.check_delimiter(ID_DELIM):
                    state = 232
                elif self.current_character not in UNDER_ALPHA_NUM:
                    '''Captures example: my_var!'''     
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid character '{invalid_character}'")
                    state = 0
                else:
                    '''Captures example: variableNameThatExceeds32Characters'''
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Identifier exceeds {MAX_IDENTIFIER_LENGTH} characters")
                    state = 0
            elif state == 232:
                self.identifier_count += 1
                token_name = f"{TT_IDENTIFIER}{self.identifier_count}"
                self.emit_token(tokens, token_name, identifier)
                state = 0
            elif state == 235:
                if      self.check_delimiter(WHITE_SPACE):      state = 236
                else:                                           
                    '''Captures example: skim a = 3.5;g'''
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid delimiter '{invalid_character}', expected ' ', '\\t', or '\\n'")
                    state = 0
            elif state == 236:
                self.emit_token(tokens, TT_SEMI_COLON, ';')
                state = 0
            elif state == 237:
                if      self.check_delimiter(WHITE_SPACE):      state = 238
                else:
                    '''Captures example: case 3:g'''                                           
                    invalid_character = self.current_character
                    self.display_lexical_error(self.pos.copy(), self.pos, errors, f"Invalid delimiter '{invalid_character}', expected ' ', '\\t', or '\\n'")
                    state = 0
            elif state == 238:
                self.emit_token(tokens, TT_COLON, ':')
                state = 0

            # Convert errors to string format here
            error_strings = [error.as_string() for error in errors]

        # Debugging the token
        print(f"Tokens produced: {tokens}")

        return tokens, error_strings
