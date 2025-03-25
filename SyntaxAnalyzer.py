class SyntaxAnalyzer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.errors = []

cfg = {

    "<program>": [["dinein", "<global_dec>", "<function>", "chef", "pinch", "dish", "(", ")", "{", "<local_dec>", "<statement_block>", "spit", "pinchliterals", ";", "}", "takeout"]],
	
    "<global_dec>": [["<declarations>", "<global_dec>"],
					["λ"]],
    
	"<declarations>": [["<data_type>", "id", "<dec_or_init>", ";"],
			["recipe", "<data_type2>", "id", "[", "pinchliterals", "]", "<elements>", ";"]],
 
	"<data_type>": [["pinch"],
                 	["skim"],
                 	["pasta"],
                 	["bool"]],
 
 	"<data_type2>": [["pinch"],
                 	["skim"],
                 	["pasta"]],
  
	"<dec_or_init>": [["=", "<literals>", "<next_dec_or_init>"],
                   	["<next_dec_or_init>"]],
 
	"<next_dec_or_init>": [[",", "id", "<dec_or_init>"],
                        ["λ"]],
 
	"<literals>": [["pinchliterals"],
                	["skimliterals"],
                 	["pastaliterals"],
                 	["<yum_or_bleh>"]],
 
	"<literals2>": [["pinchliterals"],
                	["skimliterals"],
                 	["pastaliterals"]],
 
 	"<literals3>": [["pastaliterals"],
                 	["<yum_or_bleh>"]],
 
	"<yum_or_bleh>": [["yum"],
                   	["bleh"]],
 
	"<elements>": [["=", "{", "<literals>", "<elementtail>", "}"],
               	["λ"]],
 
    "<elementtail>": [[",", "<literals>", "<elementtail>"],
                ["λ"]],
    
	"<function>": [["full", "<data_type>", "id", "(", "<parameters>", ")", "{", "<local_dec>", "<statement_block>", "spit", "<expression>", ";", "}", "<function>"],
						["hungry", "id", "(", "<parameters>", ")", "{", "<local_dec>", "<statement_block>", "}", "<function>"],
                        ["λ"]],
 
	"<parameters>": [["<data_type>", "id", "<param_tail>"],
					["λ"]],
 
	"<param_tail>": [[",","<data_type>", "id", "<param_tail>"],
                  	["λ"]],
 
    "<local_dec>": [["<local_declarations>", "<local_dec>"],
                    ["λ"]],
    
	"<local_declarations>": [["<data_type>", "id", "<dec_or_init>", ";"],
			["recipe", "<data_type2>", "id", "[", "pinchliterals", "]", "<elements>", ";"]],
 
    "<statement_block>": [["<statement>", "<statement_block>"],
                    ["λ"]],
    
    "<statement>": [["id", "<statement_id_tail>"],
                    ["<unary_op>", "id", ";"],
                    ["<conditional_statement>"],
                    ["<looping_statement>"],
                    ["serve", "(", "<value3>", "<serve_tail>", ")", ";"],
                    ["make", "(", "id", ")", ";"]],
    
    "<statement_id_tail>": [["(", "<argument_list>", ")", ";"],
                            ["<assignment_operator>", "<expression>", ";"],
                            ["[", "pinchliterals", "]", "<assignment_operator>", "<arithmetic_exp>", ";"],
                            ["<unary_op>", ";"]],
    
    "<argument_list>": [["<arithmetic_exp>", "<argument_tail>"],
                        ["λ"]],
    
    "<argument_tail>": [[",", "<arithmetic_exp>" , "<argument_tail>"],
                        ["λ"]],
    
    "<expression>": [["<expression_operand>", "<expression_tail>"]],
    
    "<expression_tail>": [["<expression_operator>", "<expression_operand>", "<expression_tail>"],
                        ["λ"]],
    
    "<expression_operand>": [["<value>"],
                             ["(", "<expression>", ")"],
                             ["!", "(", "<expression>", ")"],
                             ["!!", "(", "<expression>", ")"]],
    
    "<expression_operator>": [["+"],
                            ["-"],
                            ["*"],
                            ["/"],
                            ["%"],
                            ["=="],
                            ["!="],
                            ["<"],
                            [">"],
                            ["<="],
                            [">="],
                            ["&&"],
				            ["??"]],
    
    "<arithmetic_exp>": [["<arithmetic_operand>", "<arithmetic_tail>"]],
    
    "<arithmetic_tail>": [["<arithmetic_operator>", "<arithmetic_operand>", "<arithmetic_tail>"],
                          ["λ"]],
    
    "<arithmetic_operand>": [["<value2>"],
                             ["(", "<arithmetic_exp>", ")"]],
    
    "<arithmetic_operator>": [["+"],
                            ["-"],
                            ["*"],
                            ["/"],
                            ["%"]],
    
    "<value>": [["<literals>"],
                ["id", "<value_id_tail>"]],
    
    "<value_id_tail>": [["(", "<argument_list>", ")"],
                ["[", "pinchliterals", "]"],
                ["λ"]],
    
    "<value2>": [["<literals2>"],
                ["id", "<value_id_tail>"]],
    
    "<value3>": [["<literals3>"],
                ["id", "<value_id_tail>"]],
    
	"<assignment_operator>": [["="],
				["+="],
				["-="],
				["*="],
				["/="],
				["%="]],
 
    "<unary_op>": [["++"],
                   ["--"]],
    
    "<conditional_statement>": [["taste", "(", "<condition>", ")", "{", "<statement_block>", "}", "<conditional_tail>"],
                                ["flip", "(", "id", ")", "{", "case", "<literals4>", ":", "<statement_block>", "chop", ";", "<case_tail>", "<default_block>", "}"]],
    
    "<conditional_tail>": [["elif", "(", "<condition>", ")", "{", "<statement_block>", "}", "<conditional_tail>"],
                            ["mix", "{", "<statement_block>", "}"],
                            ["λ"]],
    
    "<condition>": [["<condition_operand>", "<condition_tail>"]],
    
    "<condition_tail>": [["<condition_operator>", "<condition_operand>", "<condition_tail>"],
                        ["λ"]],
    
    "<condition_operand>": [["<value>"],
                            ["(", "<condition>", ")"],
                            ["!", "(", "<condition>", ")"],
                            ["!!", "(", "<condition>", ")"]],
    
    "<condition_operator>": [["=="],
                             ["!="],
                             ["<"],
                             [">"],
                             ["<="],
                             [">="],
                             ["&&"],
                             ["??"]],
    
    "<case_tail>": [["case", "<literals4>", ":", "<statement_block>", "chop", ";", "<case_tail>"],
                       ["λ"]],
    
    "<literals4>": [["pinchliterals"],
                    ["pastaliterals"]],
    
    "<default_block>": [["default", ":", "<statement_block>", "chop", ";"],
                       ["λ"]],
    
    "<looping_statement>": [["for", "(", "<pinch_opt>", "id", "=", "<for_init>", ";", "<condition>", ";", "<inc_dec>", ")", "{", "<statement_block>", "}"],
                            ["simmer" , "(", "<condition>", ")", "{", "<statement_block>", "}"],
                            ["keepmix", "{", "<statement_block>", "}", "simmer", "(", "<condition>", ")"]],        
                
    "<pinch_opt>": [["pinch"],
                    ["λ"]],
    
    "<for_init>": [["pinchliterals"],
                    ["id", "<value_id_tail>"]],
    
    "<inc_dec>": [["id", "<unary_op>"],
                  ["<unary_op>", "id"]],
    
    "<serve_tail>": [["+", "<value3>", "<serve_tail>"],
                     ["λ"]]
}

def compute_first_set(cfg):
    first_set = {non_terminal: set() for non_terminal in cfg.keys()}

    def first_of(symbol):
        if symbol not in cfg:
            return {symbol} 

        if symbol in first_set and first_set[symbol]:
            return first_set[symbol]

        result = set()
        
        for production in cfg[symbol]:
            for sub_symbol in production:
                if sub_symbol not in cfg:  # terminal
                    result.add(sub_symbol)
                    break  
                else:  # non-terminal
                    sub_first = first_of(sub_symbol)
                    result.update(sub_first - {"λ"})  
                    if "λ" not in sub_first:
                        break  
            
            else:  # all symbols in the production derive λ
                result.add("λ")

        first_set[symbol] = result
        return result

    for non_terminal in cfg:
        first_of(non_terminal)

    return first_set

def compute_follow_set(cfg, start_symbol, first_set):
    follow_set = {non_terminal: set() for non_terminal in cfg.keys()}
    follow_set[start_symbol].add("$")  

    changed = True  

    while changed:
        changed = False 
    
        for non_terminal, productions in cfg.items():
            for production in productions:
                for i, item in enumerate(production):
                    if item in cfg:  # nt only
                        follow_before = follow_set[item].copy()

                        if i + 1 < len(production):  # A -> <alpha>B<beta>
                            beta = production[i + 1]
                            if beta in cfg:  # if <beta> is a non-terminal
                                follow_set[item].update(first_set[beta] - {"λ"})
                                if "λ" in first_set[beta]:
                                    follow_set[item].update(follow_set[beta])
                            else:  # if <beta> is a terminal
                                follow_set[item].add(beta)
                        else:  # nothing follows B
                            follow_set[item].update(follow_set[non_terminal])

                        if follow_set[item] != follow_before:
                            changed = True  

    return follow_set

def compute_predict_set(cfg, first_set, follow_set):
    predict_set = {}  

    for non_terminal, productions in cfg.items():
        for production in productions:
            production_key = (non_terminal, tuple(production))  # A = (A,(prod))
            predict_set[production_key] = set()

            first_alpha = set()
            for symbol in production:
                if symbol in first_set:  # non-terminal
                    first_alpha.update(first_set[symbol] - {"λ"})
                    if "λ" not in first_set[symbol]:
                        break
                else:  # terminal
                    first_alpha.add(symbol)
                    break
            else:  
                first_alpha.add("λ")

            predict_set[production_key].update(first_alpha - {"λ"})

            # if λ in first_alpha, add follow set of lhs to predict set
            if "λ" in first_alpha:
                predict_set[production_key].update(follow_set[non_terminal])

    return predict_set

def gen_parse_table():
    parse_table = {}
    for (non_terminal, production), predict in predict_set.items():
        if non_terminal not in parse_table:
            parse_table[non_terminal] = {}
        for terminal in predict:
            if terminal in parse_table[non_terminal]:
                raise ValueError(f"Grammar is not LL(1): Conflict in parse table for {non_terminal} and {terminal}")
            parse_table[non_terminal][terminal] = production

    return parse_table  

first_set = compute_first_set(cfg)
follow_set = compute_follow_set(cfg, "<program>", first_set)
predict_set = compute_predict_set(cfg, first_set, follow_set)
parse_table = gen_parse_table()

class ParseTreeNode:
    def __init__(self, token_value, node_type=None, line_number=-1):
        if isinstance(token_value, str) and ':' in token_value:
            token_type, literal = token_value.split(':', 1)
            if token_type == "END":
                token_type = ""
            self.value = literal
            self.node_type = token_type if token_type else (node_type if node_type is not None else literal)
        else:
            self.value = token_value
            self.node_type = node_type if node_type is not None else token_value
        self.children = []
        self.line_number = line_number  # Line number attribute

    def add_child(self, child):
        self.children.append(child)

    def __str__(self, level=0):
        ret = "  " * level + f"{self.node_type} (Line {self.line_number})"
        ret += "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

class LL1Parser:
    def __init__(self, cfg, parse_table, follow_set):
        self.cfg = cfg
        self.parse_table = parse_table
        self.follow_set = follow_set
        self.stack = []
        self.input_tokens = []
        self.index = 0
        self.parse_tree = None
        self.errors = []
        self.node_stack = []
        self.production_markers = []
        
    def parse(self, tokens):
        # Filter out comment tokens before processing
        filtered_tokens = []
        in_block_comment = False
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Safety check for token structure
            if not isinstance(token, tuple) or len(token) < 2:
                filtered_tokens.append(token)
                i += 1
                continue
                
            token_lexeme = token[0]
            token_type = token[1]
            
            # Check if this is a block comment token (both open and close in one token)
            if isinstance(token_lexeme, str) and '/-' in token_lexeme and '-/' in token_lexeme:
                # This is a complete block comment, skip it
                i += 1
                continue
                
            # Check if this is the start of a block comment
            if not in_block_comment and isinstance(token_lexeme, str) and '/-' in token_lexeme:
                in_block_comment = True
                i += 1
                continue
                
            # Check if this is the end of a block comment
            if in_block_comment and isinstance(token_lexeme, str) and '-/' in token_lexeme:
                in_block_comment = False
                i += 1
                continue
                
            # Skip tokens if we're in a block comment
            if in_block_comment:
                i += 1
                continue
                
            # Handle line comments starting with //
            if isinstance(token_lexeme, str) and token_lexeme.startswith('//'):
                i += 1
                continue
            if isinstance(token_type, str) and token_type.startswith('//'):
                i += 1
                continue
                
            # If we get here, the token is not a comment and not in a comment block
            filtered_tokens.append(token)
            i += 1
        
        # Print warning if we ended in a block comment state
        if in_block_comment:
            print("WARNING: Unclosed block comment detected. Processing continued assuming end of file closes the comment.")
        
        # Continue with the original token processing logic
        def safe_process_token(token):
            try:
                if isinstance(token, tuple):
                    # Ensure we have at least lexeme, token_type, and line_number
                    if len(token) >= 3:
                        lexeme = token[0]
                        token_type = token[1]
                        line_number = token[2]
                    else:
                        lexeme = token[0] if len(token) > 0 else ""
                        token_type = token[1] if len(token) > 1 else str(lexeme)
                        line_number = -1
                    
                    # Only normalize the token type for identifiers, preserve the lexeme
                    if isinstance(token_type, str) and token_type.startswith("id"):
                        normalized_token = (lexeme, "id", line_number)
                    else:
                        normalized_token = (lexeme, token_type, line_number)
                    
                    return normalized_token
                else:
                    return (str(token), str(token), -1)
            except Exception as e:
                print(f"Error processing token {token}: {e}")
                return (str(token), str(token), -1)

        # Process the filtered tokens
        try:
            processed_tokens = [safe_process_token(token) for token in filtered_tokens]
            processed_tokens.append(('$', '$', -1))  # Add end marker
            
            # Debug: Print processed tokens after filtering comments
            # print("DEBUG: Received Tokens (after comment filtering):")
            # for i, token in enumerate(processed_tokens[:-1]):  # Skip the $ token in debug output
            #     print(f"Token {i}: Lexeme={token[0]}, Type={token[1]}, Line={token[2]}")
                
        except Exception as e:
            print(f"ERROR during token processing: {e}")
            return False, [f"Token processing error: {e}"]


        # Check if processed tokens are empty
        if not processed_tokens:
            print("ERROR: No tokens were processed!")
            return False, ["No tokens found for parsing"]
        
        self.input_tokens = processed_tokens
        self.index = 0
        self.stack = ['$', '<program>']
        self.parse_tree = ParseTreeNode('<program>')
        self.node_stack = [self.parse_tree]
        self.production_markers = []

        while self.stack[-1] != '$':
            top = self.stack[-1]
            current_token = self.input_tokens[self.index][1]
            current_line = self.input_tokens[self.index][2]

            # Handle production completion markers
            if isinstance(top, tuple) and top[0] == 'END':
                self._handle_production_end()
                continue

            if top not in self.cfg:  # Terminal
                if top == current_token:
                    self._process_terminal(current_line)
                else:
                    self.improved_syntax_error(current_line, current_token)
                    return False, self.errors
            else:  # Non-terminal
                if not self._process_non_terminal(current_token, current_line):
                    return False, self.errors

        self._prune_lambda_nodes(self.parse_tree)
        # Final validation and cleanup
        if self.index == len(self.input_tokens) - 1:
            print("Parsing successful!")
            print(self.parse_tree)
            return True, []
        else:
            return False, ["Incomplete parsing"]

    def _handle_production_end(self):
        """Handle end of production markers"""
        marker = self.stack.pop()
        if self.node_stack and self.production_markers:
            expected_marker = self.production_markers.pop()
            if marker[1] == expected_marker:
                self.node_stack.pop()
    def _prune_lambda_nodes(self, node):
        pass

    def _process_terminal(self, current_line):
        """Process terminal symbols"""
        expected_symbol = self.stack.pop()
        terminal_node = ParseTreeNode(f"{expected_symbol}:{self.input_tokens[self.index][0]}", line_number=current_line)
        self.node_stack[-1].add_child(terminal_node)
        self.index += 1

    def _process_non_terminal(self, current_token, current_line):
        """Process non-terminal symbols with proper nesting"""
        try:
            production = self.parse_table[self.stack[-1]].get(current_token)
            if production is None:
                self.improved_syntax_error(current_line, current_token)
                return False

            # Get current non-terminal and create node with line number
            current_nt = self.stack.pop()
            new_node = ParseTreeNode(current_nt, line_number=current_line)
            self.node_stack[-1].add_child(new_node)

            if production[0] != 'λ':
                # Push production markers and symbols
                self.production_markers.append(current_nt)
                self.stack.append(('END', current_nt))  # End marker
                for symbol in reversed(production):
                    self.stack.append(symbol)
                self.node_stack.append(new_node)
            else:
                # Add λ node with the same line number as the non-terminal
                lambda_node = ParseTreeNode('λ', line_number=current_line)
                new_node.add_child(lambda_node)

            return True
        except KeyError:
            self.improved_syntax_error(current_line, current_token)
            return False

    def improved_syntax_error(self, line_number, found):
        """Enhanced syntax error reporting with focused context awareness."""
        token_lexeme = self.input_tokens[self.index][0] if self.index < len(self.input_tokens) else found
        
        # Find the immediate context (closest non-terminal we're trying to parse)
        current_context = None
        for item in reversed(self.stack):
            if isinstance(item, str) and item.startswith('<'):
                current_context = item
                break
        
        # Find the immediate expected token(s)
        expected_tokens = set()
        if self.stack and self.stack[-1] not in self.cfg:  # If expecting a specific terminal
            expected_tokens.add(self.stack[-1])
        elif current_context in self.parse_table:
            # Only look at the immediate production options
            expected_tokens = set(self.parse_table[current_context].keys())
            expected_tokens.discard("λ")  # Remove lambda from expected tokens
        
        # Create a focused error message
        error_message = f"[SYNTAX_ERROR] at line {line_number}: "
        
        if expected_tokens:
            if len(expected_tokens) <= 3:
                expected_str = " or ".join(f"'{e}'" for e in sorted(expected_tokens))
                error_message += f"Expected {expected_str}, but found '{token_lexeme}' while parsing {current_context}"
            else:
                error_message += f"Unexpected '{token_lexeme}' while parsing {current_context}"
        else:
            error_message += f"Unexpected '{token_lexeme}' while parsing {current_context}"
        
        self.errors.append(error_message)
        
        # Attempt error recovery
        self._attempt_error_recovery(current_token=found, line_number=line_number)
    
    def _attempt_error_recovery(self, current_token, line_number):
        """Attempt to recover from syntax errors by skipping tokens until a valid state is found."""
        recovery_attempts = 0
        max_recovery_attempts = 5  # Limit recovery attempts to prevent infinite loops
        
        while recovery_attempts < max_recovery_attempts:
            # Try to find a synchronization point
            if self._find_sync_point(current_token):
                return True
            
            # If we can't find a sync point, skip the current token
            self.index += 1
            if self.index >= len(self.input_tokens):
                break
                
            current_token = self.input_tokens[self.index][1]
            recovery_attempts += 1
        
        # If we couldn't recover, add a fatal error
        self.errors.append(f"[FATAL_ERROR] at line {line_number}: Unable to recover from syntax error")
        return False
    
    def _find_sync_point(self, current_token):
        """Find a synchronization point by checking if the current token can follow any non-terminal on the stack."""
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] in self.cfg:
                if current_token in self.follow_set.get(self.stack[i], set()):
                    # Found a sync point, pop everything up to this non-terminal
                    while len(self.stack) > i + 1:
                        self.stack.pop()
                    return True
        return False

