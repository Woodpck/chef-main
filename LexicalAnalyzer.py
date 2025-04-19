class LexicalAnalyzer:
    def __init__(self):
        self.whitespace = {' ', '\t', '\n'}
        self.alpha_big = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.alpha_small = set("abcdefghijklmnopqrstuvwxyz")
        self.all_num = set("0123456789")
        self.all_alpha = self.alpha_small | self.alpha_big
        self.alpha_num = self.all_alpha | self.all_num
        self.bool_delim = {';' , ' ' , ',',')'}
        self.dt_delim = {' ', '\t'}
        self.space_delim = {' '}
        self.semicolon_delim = {';'}
        self.colon_delim = {':'}
        self.newline_delim ={'\n'}
        self.oparan_delim = {'('}
        self.delim0 = {' ', '\t', '\n', '(', ')', ';', ',', '{', '}', '[', ']', '=', '+', '-', '*', '/', '%', '<', '>', '&', '|', '?', '!', '"', '~'}
        
        self.bool_delim = {';', ' ', ')', ',', '(', '<', '>', '&', '|'}
        self.operator_delim = {'>', '<', '=', '&', '|', '+', '-', '*', '/', '%'}
        
        self.delim1 = {' ', '"', '(', '~'} | self.alpha_num
        self.delim2 = {' ', '{'}
        self.delim3 = {' ', '(', '~'} | self.alpha_num
        self.delim4 = {';', ')'} | self.alpha_num
        self.delim5 = {' ', '!', '('} | self.alpha_num
        self.delim6 = {'"', '~', '\'', ' '} | self.alpha_num
        self.delim7 = {'('}
        self.delim8 = {' ', '~', '"', '\'', '('} | self.alpha_num
        self.num_delim = {' ', '?', '+', '>', '-', ';', ')', '<', '*', '/', '=', '%', ']', ',','{','}', ':'}

        self.delim12 = {')', '!', '\'', '"', ' ', '('} | self.alpha_num
        self.delim13 = {';', '{', ')', '<', '>', '=', '?', '&', '+', '-', '/', '*', '%', ' ', '!'}
        self.delim14 = {']', ' '} | self.alpha_num
        self.delim15 = {'=', ';', ' ', '\n', '[',"("}
        self.delim16 = {'\'', '"', '~', ' ', '\n', '{'} | self.alpha_num
        self.delim17 = {';', '}', ',', ' '  , '\n'} | self.alpha_small   

        self.com_delim = {'\n'}
        self.pasta_delim = {"\t",',', ';', ' ', ':', ')', '}', '+'}
        self.opdelim = {'+', '-', '*', '/', '%', '**'}
        self.id_delim = {' ', ';', ',', '.', '(', ')', '{', '[', ']', '='} | self.opdelim

        self.quotes = {'"', '“', '”'}
        self.ascii_delim = {chr(i) for i in range(32, 127)} | self.whitespace
        self.asciicmnt = {chr(i) for i in range(32, 127) if chr(i) not in {'/', '-'}} | {'\t', '\n'} 
        self.asciistr = ({chr(i) for i in range(32, 127) if chr(i) not in self.quotes } | {'\t', '\n', '\\', '“', '”'})
        
        self.errors = []
        self.code = ""
        self.index = 0
        self.line_number = 1
        self.identifier_count = 0

    def nextChar(self):
            if self.index < len(self.code):
                c = self.code[self.index]
                self.index += 1
                return c
            return None
        
    def stepBack(self):
            if self.index > 0:
                self.index -= 1

    def tokenize(self, code):
        self.code = code
        tokens = []
        self.index = 0
        state = 0
        lexeme = ""
        line = 1
        self.identifier_count = 0

        while True:
            c = self.nextChar()

            if c is None and state == 0:
                break
            
            
            # print(f"State: {state}, char: {repr(c)}, Lexeme: {repr(lexeme)}, Line: {line}")
            
            match state:
                case 0:
                    lexeme = ""
                    
                    if c == 'b':
                        state = 1
                        lexeme += 'b'
                    elif c == 'c':
                        state = 10
                        lexeme += 'c'
                    elif c == 'd':
                        state = 22
                        lexeme += 'd'
                    elif c == 'e':
                        state = 39
                        lexeme += 'e'
                    elif c == 'f':
                        state = 44
                        lexeme += 'f'
                    elif c == 'h':
                        state = 56
                        lexeme += 'h'
                    elif c == 'k':
                        state = 63
                        lexeme += 'k'
                    elif c == 'm':
                        state = 71
                        lexeme += 'm'
                    elif c == 'p':
                        state = 79
                        lexeme += 'p'
                    elif c == 'r':
                        state = 90
                        lexeme += 'r'
                    elif c == 's':
                        state = 97
                        lexeme += 's'
                    elif c == 't':
                        state = 117
                        lexeme += 't'
                    elif c == 'y':
                        state = 129
                        lexeme += 'y'
                    elif c == ' ':
                        continue  # Simply skip space
                    elif c == '\t':
                        continue  # Skip tab
                    elif c == '\n':
                        line += 1  # Increment line number
                    elif c == '-':
                        state = 139
                        lexeme += '-'
                    elif c == ',':
                        state = 145
                        lexeme += ','
                    elif c == '!':
                        state = 147
                        lexeme += '!'
                    elif c == '?':
                        state = 153
                        lexeme += '?'
                    elif c == '(':
                        state = 156
                        lexeme += '('
                    elif c == ')':
                        state = 158
                        lexeme += ')'
                    elif c == '[':
                        state = 160
                        lexeme += '['
                    elif c == ']':
                        state = 162
                        lexeme += ']'
                    elif c == '{':
                        state = 164
                        lexeme += '{'
                    elif c == '}':
                        state = 166
                        lexeme += '}'
                    elif c == '*':
                        state = 168
                        lexeme += '*'
                    elif c == '/':
                        state = 172
                        lexeme += '/'
                    elif c == '&':
                        state = 180
                        lexeme += '&'
                    elif c == '%':
                        state = 183
                        lexeme += '%'
                    elif c == '+':
                        state = 187
                        lexeme += '+'
                    elif c == '<':
                        state = 193
                        lexeme += '<'
                    elif c == '=':
                        state = 197
                        lexeme += '='
                    elif c == '>':
                        state = 201
                        lexeme += '>'
                    elif c == '"':
                        state = 205
                        lexeme += '"'
                    elif c == '~':
                        state = 208
                        lexeme += c  
                    elif c in self.all_num:
                        state = 209
                        lexeme += c   
                    elif c in self.alpha_small:
                        state = 230
                        lexeme += c
                    elif c == ';':
                        state = 234
                        lexeme += c
                    elif c == ':':
                        state = 236
                        lexeme += c    
                    else:
                        self.errors.append(f"Line {line}: Unexpected Character '{c}'.")
                    
                
                case 1:
                    if c == 'l':
                        state = 2
                        lexeme += c
                    elif c == 'o':
                        state = 6
                        lexeme += c
                    elif c in self.id_delim:  # If we see a valid delimiter, it's a single-char identifier
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 2:
                    if c == 'e':
                        state = 3
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 3:
                    if c == 'h':
                        state = 4
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 4:
                    if c in self.bool_delim:
                        state = 5
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 5:
                    tokens.append((lexeme, "bleh",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 6:
                    if c == 'o':
                        state = 7
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 7:
                    if c == 'l':
                        state = 8
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 8:
                    if c in self.dt_delim:
                        state = 9
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 9:
                    tokens.append((lexeme, "bool",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 10:
                    if c == 'a':
                        state = 11
                        lexeme += c
                    elif c == 'h':
                        state = 15
                        lexeme += c
                    elif c in self.id_delim: 
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 11:
                    if c == 's':
                        state = 12
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 12:
                    if c == 'e':
                        state = 13
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 13:
                    if c in self.space_delim:
                        state = 14
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 14:
                    tokens.append((lexeme, "case",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 15:
                    if c == 'e':
                        state = 16
                        lexeme += c
                    elif c == 'o':
                        state = 19
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0

                case 16:
                    if c == 'f':
                        state = 17
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 17:
                    if c in self.space_delim:
                        state = 18
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 18:
                    tokens.append((lexeme, "chef",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 19:
                    if c == 'p':
                        state = 20
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 20:
                    if c in self.semicolon_delim:
                        state = 21
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 21:
                    tokens.append((lexeme, "chop",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 22:
                    if c == 'e':
                        state = 23
                        lexeme += c
                    elif c == 'i':
                        state = 30
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 23:
                    if c == 'f':
                        state = 24
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 24:
                    if c == 'a':
                        state = 25
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 25:
                    if c == 'u':
                        state = 26
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 26:
                    if c == 'l':
                        state = 27
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 27:
                    if c == 't':
                        state = 28
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 28:
                    if c in self.colon_delim:
                        state = 29
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 29:
                    tokens.append((lexeme, "default",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 30:
                    if c == 'n':
                        state = 31
                        lexeme += c
                    elif c == 's':
                        state = 36
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 31:
                    if c == 'e':
                        state = 32
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 32:
                    if c == 'i':
                        state = 33
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 33:
                    if c == 'n':
                        state = 34
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 34:
                    if c in self.newline_delim or c.isspace():
                        state = 35
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                        
                case 35:
                    tokens.append((lexeme, "dinein",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 36:
                    if c == 'h':
                        state = 37
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 37:
                    if c in self.oparan_delim:
                        state = 38
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 38:
                    tokens.append((lexeme, "dish",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 39:
                    if c == 'l':
                        state = 40
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 40:
                    if c == 'i':
                        state = 41
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 41:
                    if c == 'f':
                        state = 42
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 42:
                    if c in self.delim0:
                        state = 43
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 43:
                    tokens.append((lexeme, "elif",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 44:
                    if c == 'l':
                        state = 45
                        lexeme += c
                    elif c == 'o':
                        state = 49
                        lexeme += c
                    elif c == 'u':
                        state = 52
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 45:
                    if c == 'i':
                        state = 46
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 46:
                    if c == 'p':
                        state = 47
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 47:
                    if c in self.delim0:
                        state = 48
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 48:
                    tokens.append((lexeme, "flip",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 49:
                    if c == 'r':
                        state = 50
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 50:
                    if c in self.delim0:
                        state = 51
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 51:
                    tokens.append((lexeme, "for",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 52:
                    if c == 'l':
                        state = 53
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 53:
                    if c == 'l':
                        state = 54
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 54:
                    if c in self.dt_delim:
                        state = 55
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 55:
                    tokens.append((lexeme, "full",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 56:
                    if c == 'u':
                        state = 57
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 57:
                    if c == 'n':
                        state = 58
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 58:
                    if c == 'g':
                        state = 59
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 59:
                    if c == 'r':
                        state = 60
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 60:
                    if c == 'y':
                        state = 61
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 61:
                    if c in self.space_delim:
                        state = 62
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 62:
                    tokens.append((lexeme, "hungry",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 63:
                    if c == 'e':
                        state = 64
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 64:
                    if c == 'e':
                        state = 65
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 65:
                    if c == 'p':
                        state = 66
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 66:
                    if c == 'm':
                        state = 67
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 67:
                    if c == 'i':
                        state = 68
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 68:
                    if c == 'x':
                        state = 69
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 69:
                    if c in self.delim2:
                        state = 70
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 70:
                    tokens.append((lexeme, "keepmix",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 71:
                    if c == 'a':
                        state = 72
                        lexeme += c
                    elif c == 'i':
                        state = 76
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 72:
                    if c == 'k':
                        state = 73
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 73:
                    if c == 'e':
                        state = 74
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 74:
                    if c in self.delim0:
                        state = 75
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 75:
                    tokens.append((lexeme, "make",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 76:
                    if c == 'x':
                        state = 77
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 77:
                    if c in self.delim2:
                        state = 78
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 78:
                    tokens.append((lexeme, "mix",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                        
                case 79:
                    if c == 'a':
                        state = 80
                        lexeme += c
                    elif c == 'i':
                        state = 85
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 80:
                    if c == 's':
                        state = 81
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 81:
                    if c == 't':
                        state = 82
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 82:
                    if c == 'a':
                        state = 83
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 83:
                    if c in self.dt_delim:
                        state = 84
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 84:
                    tokens.append((lexeme, "pasta",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 85:
                    if c == 'n':
                        state = 86
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 86:
                    if c == 'c':
                        state = 87
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 87:
                    if c == 'h':
                        state = 88
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 88:
                    if c in self.dt_delim:
                        state = 89
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 89:
                    tokens.append((lexeme, "pinch",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                        
                case 90:
                    if c == 'e':
                        state = 91
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 91:
                    if c == 'c':
                        state = 92
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 92:
                    if c == 'i':
                        state = 93
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 93:
                    if c == 'p':
                        state = 94
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 94:
                    if c == 'e':
                        state = 95
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 95:
                    if c in self.dt_delim:
                        state = 96
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 96:
                    tokens.append((lexeme, "recipe",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 97:
                    if c == 'e':
                        state = 98
                        lexeme += c
                    elif c == 'i':
                        state = 103
                        lexeme += c
                    elif c == 'k':
                        state = 109
                        lexeme += c
                    elif c == 'p':
                        state = 113
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 98:
                    if c == 'r':
                        state = 99
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 99:
                    if c == 'v':
                        state = 100
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 100:
                    if c == 'e':
                        state = 101
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 101:
                    if c in self.delim0:
                        state = 102
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 102:
                    tokens.append((lexeme, "serve",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 103:
                    if c == 'm':
                        state = 104
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 104:
                    if c == 'm':
                        state = 105
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 105:
                    if c == 'e':
                        state = 106
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 106:
                    if c == 'r':
                        state = 107
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 107:
                    if c in self.delim0:
                        state = 108
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 108:
                    tokens.append((lexeme, "simmer",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                        
                case 109:
                    if c == 'i':
                        state = 110
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 110:
                    if c == 'm':
                        state = 111
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 111:
                    if c in self.dt_delim:
                        state = 112
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 112:
                    tokens.append((lexeme, "skim",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 113:
                    if c == 'i':
                        state = 114
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 114:
                    if c == 't':
                        state = 115
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 115:
                    if c in self.space_delim:
                        state = 116
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 116:
                    tokens.append((lexeme, "spit",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 117:
                    if c == 'a':
                        state = 118
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 118:
                    if c == 'k':
                        state = 119
                        lexeme += c
                    elif c == 's':
                        state = 125
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 119:
                    if c == 'e':
                        state = 120
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 120:
                    if c == 'o':
                        state = 121
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 121:
                    if c == 'u':
                        state = 122
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 122:
                    if c == 't':
                        state = 123
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 123:
                    if c is None or c in self.whitespace:
                        state = 124
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 124:
                    tokens.append((lexeme, "takeout",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 125:
                    if c == 't':
                        state = 126
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 126:
                    if c == 'e':
                        state = 127
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 127:
                    if c in self.delim0:
                        state = 128
                        if c is not None:
                            self.stepBack() 
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 128:
                    tokens.append((lexeme, "taste",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 129:
                    if c == 'u':
                        state = 130
                        lexeme += c
                    elif c in self.id_delim:
                        tokens.append((lexeme,'identifier',line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 130:
                    if c == 'm':
                        state = 131
                        lexeme += c
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 131:
                    if c in self.bool_delim:
                        state = 132
                        if c is not None:
                            self.stepBack()
                    elif c and (c.isalpha() or c.isdigit() or c == '_'):
                        state = 232
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 132:
                    tokens.append((lexeme, "yum",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 133:
                    if c is None or c in self.ascii_delim:
                        state = 134
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: 'space' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 134:
                    tokens.append((" ", " ",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 135:
                    if c is None or c in self.ascii_delim:
                        state = 136
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: 'tab' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 136:
                    tokens.append(("\\t", "\\t",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 137:
                    if c is None or c in self.ascii_delim:
                        state = 138
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: 'newline' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 138:
                    tokens.append(("\\n", "\\n",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 139:
                    if c in self.delim3:
                        state = 140
                        if c is not None:
                            self.stepBack()
                    elif c == '-':
                        state = 141
                        lexeme += c
                    elif c == '=':
                        state = 143
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 140:
                    tokens.append((lexeme, "-",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 141:
                    if c in self.delim4:
                        state = 142
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 142:
                    tokens.append((lexeme, "--",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 143:
                    if c in self.delim5:
                        state = 144
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 144:
                    tokens.append((lexeme, "-=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 145:
                    if c in self.delim6:
                        state = 146
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 146:
                    tokens.append((lexeme, ",",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 147:
                    if c in self.delim7:
                        state = 148
                        if c is not None:
                            self.stepBack()
                    elif c == '!':
                        state = 149
                        lexeme += c
                    elif c == '=':
                        state = 151
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 148:
                    tokens.append((lexeme, "!",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 149:
                    if c in self.delim3:
                        state = 150
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 150:
                    tokens.append((lexeme, "!!",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 151:
                    if c in self.delim8:
                        state = 152
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 152:
                    tokens.append((lexeme, "!=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                        
                case 153:
                    if c == '?':
                        state = 154                        
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 154:
                    if c in self.delim3:
                        state = 155
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 155:
                    tokens.append((lexeme, "??",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 156:
                    if c in self.delim12:
                        state = 157
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 157:
                    tokens.append((lexeme, "(",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 158:
                    if c in self.delim13:
                        state = 159
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 159:
                    tokens.append((lexeme, ")",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 160:
                    if c in self.delim14:
                        state = 161
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 161:
                    tokens.append((lexeme, "[",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 162:
                    if c in self.delim15:
                        state = 163
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 163:
                    tokens.append((lexeme, "]",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 164:
                    if c in self.delim16:
                        state = 165
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 165:
                    tokens.append((lexeme, "{",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 166:
                    if c in self.delim17:
                        state = 167
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 167:
                    tokens.append((lexeme, "}",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                  
                case 168:
                    if c in self.delim3:
                        state = 169
                        if c is not None:
                            self.stepBack()
                    elif c == '=':
                        state = 170
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 169:
                    tokens.append((lexeme, "*",line))
                    if c is not None:
                        self.stepBack()
                    state = 0  
                    
                case 170:
                    if c in self.delim5:
                        state = 171
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 171:
                    tokens.append((lexeme, "*=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0 
                    
                case 172:
                    if c in self.delim3:
                        state = 173
                        if c is not None:
                            self.stepBack()
                    elif c == '/':
                        state = 174
                        lexeme += c
                    elif c == '-':
                        state = 176
                        lexeme += c
                    elif c == '=':  # Handle the '/=' operator
                        state = 238
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 173:
                    tokens.append((lexeme, "/",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 174:
                    if c == '\n' or c is None:
                        tokens.append((lexeme, "singlecomment",line))
                        state = 0
                    else:
                        state = 174 
                        lexeme += c
                        
                case 175:
                    if c in self.asciicmnt:
                        state = 175
                        lexeme += c
                    elif c in self.com_delim:
                        tokens.append((lexeme, "singlecomment",line))
                        if c is not None:
                            self.stepBack()
                        state = 0
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0 
                    
                case 176:
                    if c in self.asciicmnt:
                        state = 176
                        lexeme += c
                    elif c == '-':
                        state = 177
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 177:
                    if c == '/':
                        state = 178
                        lexeme += c
                        tokens.append((lexeme, "multicomment",line))
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0  

                        
                case 178:
                    if c is not None:
                        self.stepBack()
                    state = 0

                        
                case 179:
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 180:
                    if c == '&':
                        state = 181
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 181:
                    if c in self.delim3:
                        state = 182
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 182:
                    tokens.append((lexeme, "&&",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 183:
                    if c in self.delim3:
                        state = 184
                        if c is not None:
                            self.stepBack()
                    elif c == '=':
                        state = 185
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                    
                case 184:
                    tokens.append((lexeme, "%",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 185:
                    if c in self.delim5:
                        state = 186
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 186:
                    tokens.append((lexeme, "%=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 187:
                    if c in self.delim1:
                        state = 188
                        if c is not None:
                            self.stepBack()
                    elif c == '+':
                        state = 189
                        lexeme += c
                    elif c == '=':
                        state = 191
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 188:
                    tokens.append((lexeme, "+",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 189:
                    if c in self.delim4:
                        state = 190
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 190:
                    tokens.append((lexeme, "++",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 191:
                    if c in self.delim5:
                        state = 192
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 192:
                    tokens.append((lexeme, "+=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                
                case 193:
                    if c in self.delim3:
                        state = 194
                        if c is not None:
                            self.stepBack()
                    elif c == '=':
                        state = 195
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 194:
                    tokens.append((lexeme, "<",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 195:
                    if c in self.delim5:
                        state = 196
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 196:
                    tokens.append((lexeme, "<=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 197:
                    if c in self.delim8:
                        state = 198
                        if c is not None:
                            self.stepBack()
                    elif c == '=':
                        state = 199
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 198:
                    tokens.append((lexeme, "=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 199:
                    if c in self.delim8:
                        state = 200
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 200:
                    tokens.append((lexeme, "==",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 201:
                    if c in self.delim3:
                        state = 202
                        if c is not None:
                            self.stepBack()
                    elif c == '=':
                        state = 203
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 202:
                    tokens.append((lexeme, ">",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 203:
                    if c in self.delim3:
                        state = 204
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 204:
                    tokens.append((lexeme, ">=",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                    
                case 205:
                    if c in self.asciistr:
                        state = 205
                        lexeme += c
                    elif c == '"':
                        state = 206
                        lexeme += c
                    elif c == '“':
                        state = 206
                        lexeme += c
                    elif c == '”':
                        state = 206
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 206:
                    if c in self.pasta_delim:
                        state = 207
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 207:
                    tokens.append((lexeme, 'pastaliterals',line))
                    if c is not None:
                        self.stepBack()
                    state = 0


                #pinch and skim
                case 208:
                    if c in self.all_num:
                        state = 209
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 209:
                    if c in self.all_num:
                        state = 210
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 210:
                    if c in self.all_num:
                        state = 211
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 211:
                    if c in self.all_num:
                        state = 212
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 212:
                    if c in self.all_num:
                        state = 213
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0       
                case 213:
                    if c in self.all_num:
                        state = 214
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0    
                case 214:
                    if c in self.all_num:
                        state = 215
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0    
                case 215:
                    if c in self.all_num:
                        state = 216
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0    
                case 216:
                    if c in self.all_num:
                        state = 217
                        lexeme += c
                    elif c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 217:
                    if c == '.':
                        state = 219
                        lexeme += c
                    elif c in self.num_delim:
                        state = 218
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0  
                case 218:
                    tokens.append((lexeme, "pinchliterals",line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                case 219:
                    if c in self.all_num:
                        state = 220
                        lexeme += c
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0      
                case 220:
                    if c in self.all_num:
                        state = 221
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0 
                case 221:
                    if c in self.all_num:
                        state = 222
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 222:
                    if c in self.all_num:
                        state = 223
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0 
                case 223:
                    if c in self.all_num:
                        state = 224
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0   
                case 224:
                    if c in self.all_num:
                        state = 225
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 225:
                    if c in self.all_num:
                        state = 226
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 226:
                    if c in self.all_num:
                        state = 227
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 227:
                    if c in self.all_num:
                        state = 228
                        lexeme += c
                    elif c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 228:
                    if c in self.num_delim:
                        state = 229
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 229:
                    tokens.append((lexeme, "skimliterals",line))
                    if c is not None:
                        self.stepBack()
                    state = 0

                #Identifier
                case 230:
                    if c and (c.isalpha() or c.isdigit() or c == '_'):
                        lexeme += c
                        state = 232                        
                    elif c in self.id_delim:
                        state = 231
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: Identifier '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                        
                case 231:
                    self.identifier_count += 1  # Increment counter
                    token_name = f"identifier{self.identifier_count}"
                    tokens.append((lexeme, token_name,line))  # Use the numbered token
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
                case 232:
                    if c and (c.isalpha() or c.isdigit() or c == '_'):
                        lexeme += c
                        
                        if len(lexeme) > 32:
                            self.errors.append(f"Line {line}: id '{lexeme}' exceeds 32 characters.")
                            state = 0

                    elif c in self.id_delim:
                        state = 233
                        if c is not None:
                            self.stepBack()
                    
                    else:
                        self.errors.append(f"Line {line}: Id '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                
                case 233:
                    self.identifier_count += 1  # Increment counter
                    token_name = f"identifier{self.identifier_count}"
                    tokens.append((lexeme, token_name,line))  # Use the numbered token
                    if c is not None:
                        self.stepBack()
                    state = 0 
                    
                case 234:
                    if c is None or c in self.whitespace:
                        state = 235
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: Symbol '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 235:
                    tokens.append((lexeme, ";",line))
                    if c is not None:
                            self.stepBack()
                    state = 0
                case 236:
                    if c is None or c in self.whitespace:
                        state = 237
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: Symbol '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0
                case 237:
                    tokens.append((lexeme, ":",line))
                    if c is not None:
                            self.stepBack()
                    state = 0
                case 238:
                    if c in self.delim5:
                        state = 239
                        if c is not None:
                            self.stepBack()
                    else:
                        self.errors.append(f"Line {line}: '{lexeme}' Invalid Delimiter ' {repr(c)} '.")
                        state = 0

                case 239:
                    tokens.append((lexeme, "/=", line))
                    if c is not None:
                        self.stepBack()
                    state = 0
                    
        return tokens


    def display_tokens(self, tokens):
            print(f"{'Lexeme'.ljust(40)}{'Token'.ljust(20)}")
            print("-" * 60)
            for lexeme, token in tokens:
                print(f"{lexeme.ljust(40)}{token.ljust(20)}")
                print("-" * 60)


    def display_errors(self):
        if self.errors:
            print("\nLexical Errors:\n")
            for error in self.errors:
                    print(error)
    
def make_string_fixed(self):
    id_str = ""
    c = self.nextChar()
    start_line = self.line_number
    escape_character = False
    
    while c is not None: 
        if escape_character:
            # Properly handle escape sequences
            if c == 'n':
                id_str += '\n'  # Convert \n to actual newline character
            elif c == 't':
                id_str += '\t'  # Convert \t to actual tab character
            elif c in ['"', '\\']: 
                id_str += c
            else:
                id_str += '\\' + c  # Keep unrecognized escape sequences as is
            escape_character = False
        elif c == '\\':
            escape_character = True
        elif c == '"':
            c = self.nextChar()
            if c is not None and c not in self.ascii_delim:
                self.errors.append(f"Line {self.line_number}: Invalid delimiter '{c}' after string")
                return []
            else:
                self.identifier_count += 1
                token_name = f"string{self.identifier_count}"
                if c is not None:
                    self.stepBack()
                return [(id_str, token_name, start_line)]
        elif c == '\n':
            self.errors.append(f"Line {start_line}: String not properly closed with double quotes")
            return []
        else:
            id_str += c
        c = self.nextChar()
    
    self.errors.append(f"Line {start_line}: String not properly closed with double quotes")
    return []

# Add the fixed method to the class
LexicalAnalyzer.make_string = make_string_fixed


if __name__ == "__main__":
    try:
        with open("src/lexical/program", "r") as file:
            code = file.read()
            code = code.replace("    ", "\t")
    except FileNotFoundError:
        print("Error: The file 'program' was not found in the current directory.")
        exit(1)

    analyzer = LexicalAnalyzer()
    tokens = analyzer.tokenize(code)

    # Fixed to handle 3-tuple tokens
    analyzer.display_tokens(tokens)
    analyzer.display_errors()
    print("\nEnd of program analysis.\n")