from SyntaxAnalyzer import ParseTreeNode
from datetime import datetime
from tkinter import simpledialog

class SemanticError(Exception):
    def __init__(self, code, message, line=None, identifier=None, is_warning=False):
        self.code = code  # e.g., "DUPLICATE_DECLARATION"
        self.identifier = identifier  # e.g., the name of the identifier
        self.message = message
        self.is_warning = is_warning
        self.line = line
        super().__init__(f"[{code}] {message}")

    def __str__(self):
        line_info = f" on line {self.line}" if self.line is not None else ""
        return f"[{self.code}] {self.message}{line_info}"

#---------------------------------------------------------------------
# Symbol and SymbolTable classes for semantic analysis
#---------------------------------------------------------------------
class Symbol:
    def __init__(self, name, symbol_type, attributes=None, parameters=None):
        self.name = name
        self.type = symbol_type  # e.g., "pinch", "skim", "pasta"
        self.attributes = attributes or {}  # For arrays: e.g., {'dimensions': 10, 'element_type': 'pinch'}
        self.parameters = parameters
        self.is_used = False  # Track if the symbol is used
        self.value = None  # Store the actual value of the symbol
        print(f"Created symbol: {self.name} of type {self.type}")

    def __repr__(self):
        if self.type == 'function':
            if self.parameters.children:
                return f"Symbol(name={self.name}, type={self.type}, value=<array of {len(self.value)} elements>, attributes={self.attributes}, parameters={self.parameters.value})"
            else:
                return f"Symbol(name={self.name}, type={self.type}, value=<array of {len(self.value)} elements>, attributes={self.attributes}, parameters=None)"
        else:
            return f"Symbol(name={self.name}, type={self.type}, value={self.value}, attributes={self.attributes})"

    def set_value(self, value):
        print(f"Setting value for {self.name}: {value}")
        self.value = value
        self.is_used = True

    def get_value(self):
        print(f"Getting value for {self.name}: {self.value}")
        return self.value


class SymbolTable:
    def __init__(self, debugName="", parent=None):
        self.parent = parent
        self.debugName = debugName
        self.symbols = {}
        print(f"Created symbol table: {debugName}")

    def add(self, name, symbol):
        # Only check for duplicate function declarations
        if name in self.symbols and symbol.type == "function":
            raise SemanticError("DUPLICATE_DECLARATION", f"Duplicate declaration of function '{name}'", identifier=name)
        self.symbols[name] = symbol
        print(f"Added symbol {name} to table {self.debugName}")

    def lookup(self, name, mark_used=True):
        print(f"Looking up symbol: {name} in table {self.debugName}")
        if name in self.symbols:
            if mark_used:
                self.symbols[name].is_used = True
            print(f"Found symbol {name} in table {self.debugName}")
            return self.symbols[name]
        elif self.parent:
            print(f"Symbol {name} not found in {self.debugName}, checking parent")
            return self.parent.lookup(name, mark_used)
        else:
            print(f"Symbol {name} not found in any scope")
            return None

    def get_unused(self):
        return [name for name, symbol in self.symbols.items() if not symbol.is_used]

    def __repr__(self):
        return f"SymbolTable(name={self.debugName},symbols={self.symbols})"



#---------------------------------------------------------------------
# Updated SemanticAnalyzer class
#---------------------------------------------------------------------
class SemanticAnalyzer:
    """
    this   thing was never used, idk how you could   this up so badly

    def visit_return_statement(self, node):
        if not node.children or len(node.children) < 1:
            return

        # Check if this is the program termination
        if (hasattr(node, 'value') and node.value == "<return_statement>" and
                len(node.children) >= 2 and node.children[0].value == "spit"):

            expr_node = node.children[1]
            if expr_node.node_type == "pinchliterals" and expr_node.value != "0":
                line_num = getattr(node, 'line_number', None)
                self.errors.append(SemanticError(
                    code="INVALID_TERMINATION",
                    message="Program must terminate with 'spit 0;'",
                    line=line_num
                ))

        # Original return statement checks
        self._original_visit_return_statement(node)"""


    def __init__(self):
        self.global_scope = SymbolTable(debugName="global")
        self.current_scope = self.global_scope
        self.errors = []
        self.symbol_tables = [self.global_scope]
        self.current_function = None
        self.output_buffer = []  # Buffer to store output from serve statements
        self.termination_code = 0
        # Define type compatibility rules
        self.type_compatibility = {
            "pinch": ["pinch"],           # Integers
            "skim": ["skim"],    # Floats can accept integers
            "pasta": ["pasta"],           # Strings
            "recipe": ["recipe"],         # Arrays
            "bool": ["bool"]     # Booleans can accept integers (0/1)
        }
        self.MAX_LOOP_ITERATION = 50000 #change this value if you want to exceed that interation count

    def analyze(self, parse_tree, has_syntax_errors=False):
        if has_syntax_errors:
            print("Skipping semantic analysis due to syntax errors")
            return []

        print("Starting semantic analysis...")
        # Clear the output buffer at the start of analysis
        self.output_buffer = []
        
        # Store the parse tree for function evaluation
        self.parse_tree = parse_tree
        
        # Create a main program scope (should be a child of global scope)
        main_scope = SymbolTable(debugName="main_program", parent=self.global_scope)
        self.symbol_tables.append(main_scope)
        
        # Set current scope to main program
        old_scope = self.current_scope
        self.current_scope = main_scope
        
        # Visit the parse tree
        self.visit(parse_tree)
        
        # Restore the original scope
        self.current_scope = old_scope
        
        # Only check for unused variables in local scope
        self._check_unused_local_variables()
        print(f"Analysis complete. Found {len(self.errors)} issues.")

        return self.errors

    def visit(self, node, parent=None):
        # If the node has no value, return
        if not hasattr(node, 'value'):
            return
            
        # If the node label is a non-terminal (e.g., "<local_declarations>") then try to call its visitor.
        if isinstance(node.value, str) and node.value.startswith('<') and node.value.endswith('>'):
            method_name = "visit_" + node.value.strip('<>').replace('-', '_')
            if hasattr(self, method_name):
                getattr(self, method_name)(node)
            else:
                self.generic_visit(node)
        else:
            if node.node_type == "id":
                self.check_id_usage(node)
            elif node.value == "serve":
                self.visit_serve_statement(node, parent)
            elif node.value == "make":
                if not self.visit_make_statement(node, parent):
                    return None

            if node.value == "spit":
                # the spit on the main function a terminal, so why tf are you trying to access it through terminal checking,   bitch
                return_val = parent.children[12]
                """
                    idk what y'll   want, i'll just add those 3 types of return
                """
                if not int(return_val.value) in [0,1]:
                    self.errors.append(SemanticError(
                        code="INVALID_TERMINATION_CODE",
                        message="Program must be terminated using only these [1, 0]!",
                        line=getattr(node, 'line_number', None)
                    ))
                    return None
                self.termination_code = int(return_val.value)
            else:
                self.generic_visit(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child, node)

    #-----------------------------------------------------------------
    # Type checking utility methods
    #-----------------------------------------------------------------
    def get_expression_type(self, expr_node):
        """Determine the type of an expression."""
        # Base case for terminal nodes or nodes without children
        if not hasattr(expr_node, 'children') or not expr_node.children:
            if hasattr(expr_node, 'node_type'):
                if expr_node.node_type == "pinchliterals":
                    return "pinch"
                elif expr_node.node_type == "skimliterals":
                    return "skim"
                elif expr_node.node_type == "pastaliterals":
                    return "pasta"
                elif expr_node.node_type == "id":
                    symbol = self.current_scope.lookup(expr_node.value)
                    if symbol:
                        if 'element_type' in symbol.attributes:
                            return symbol.attributes['element_type']
                        return symbol.type
                elif expr_node.value == "<literals>":
                    pass
            # If we can't determine the type, log it for debugging
            print(f"Couldn't determine type for: {expr_node.value if hasattr(expr_node, 'value') else 'unknown'}")
            return None

        # For <expression> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<expression>":
            # The type of an expression is the type of its operand
            if expr_node.children:
                return self.get_expression_type(expr_node.children[0])
            return None
        
        # For <expression_operand> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<expression_operand>":
            if expr_node.children:
                # The type is the type of the value inside
                return self.get_expression_type(expr_node.children[0])
            return None
        
        # For <value> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<value>":
            if expr_node.children:
                return self.get_expression_type(expr_node.children[0])
            return None

        # For <value3> nodes - these are often used in function calls
        if hasattr(expr_node, 'value') and expr_node.value == "<value3>":
            if expr_node.children:
                return self.get_expression_type(expr_node.children[0])
            return None
        
        # Handle binary operations
        if len(expr_node.children) >= 3:
            left_expr = expr_node.children[0]
            operator_node = expr_node.children[1] 
            right_expr = expr_node.children[2]
            
            if hasattr(operator_node, 'value') and operator_node.value in ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "??"]:
                left_type = self.get_expression_type(left_expr)
                right_type = self.get_expression_type(right_expr)
                operator = operator_node.value
                
                print(f"Binary operation: {left_type} {operator} {right_type}")
                
                # Logical operators always return boolean
                if operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "??"]:
                    return "bool"
                
                # Type promotion rules for arithmetic
                if left_type == "skim" or right_type == "skim":
                    return "skim"
                elif left_type == "pinch" and right_type == "pinch":
                    return "pinch"
                elif left_type == "pasta" and right_type == "pasta" and operator == "+":
                    return "pasta"
                
        # For <literals> nodes
        if hasattr(expr_node, "value") and expr_node.value == "<literals>":
            return self.get_expression_type(expr_node.children[0])
        
        # Handle literals directly
        if hasattr(expr_node, 'value'):
            if hasattr(expr_node, 'node_type'):
                if expr_node.node_type == "pinchliterals":
                    return "pinch"
                elif expr_node.node_type == "skimliterals":
                    return "skim"
                elif expr_node.node_type == "pastaliterals":
                    return "pasta"
        
        # For parenthesized expressions
        if len(expr_node.children) >= 3 and hasattr(expr_node.children[0], 'value') and expr_node.children[0].value == "(":
            return self.get_expression_type(expr_node.children[1])

        if expr_node.value == "<yum_or_bleh>":
            return "bool"

        # Debug - log if we couldn't determine the type
        print(f"Failed to determine type for expression: {expr_node.value if hasattr(expr_node, 'value') else 'unknown'}")
        return None

    def get_condition_type(self, expr_node):
        """Determine the type of a condition."""
        # Base case for terminal nodes or nodes without children
        if not hasattr(expr_node, 'children') or not expr_node.children:
            if hasattr(expr_node, 'node_type'):
                if expr_node.node_type == "pinchliterals":
                    return "pinch"
                elif expr_node.node_type == "skimliterals":
                    return "skim"
                elif expr_node.node_type == "pastaliterals":
                    return "pasta"
                elif expr_node.node_type == "id":
                    symbol = self.current_scope.lookup(expr_node.value)
                    if symbol:
                        if 'element_type' in symbol.attributes:
                            return symbol.attributes['element_type']
                        return symbol.type
            # If we can't determine the type, log it for debugging
            print(f"Couldn't determine type for: {expr_node.value if hasattr(expr_node, 'value') else 'unknown'}")
            return None

        # For <condition> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<condition>":
            # The type of an expression is the type of its operand
            if expr_node.children:
                return self.get_condition_type(expr_node.children[0])
            return None

        # For <expression_operand> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<condition_operand>":
            if expr_node.children:
                # The type is the type of the value inside
                return self.get_condition_type(expr_node.children[0])
            return None

        # For <value> nodes
        if hasattr(expr_node, 'value') and expr_node.value == "<value>":
            if expr_node.children:
                return self.get_condition_type(expr_node.children[0])
            return None

        # For <value3> nodes - these are often used in function calls
        if hasattr(expr_node, 'value') and expr_node.value == "<value3>":
            if expr_node.children:
                return self.get_condition_type(expr_node.children[0])
            return None

        # Handle binary operations
        if len(expr_node.children) >= 3:
            left_expr = expr_node.children[0]
            operator_node = expr_node.children[1]
            right_expr = expr_node.children[2]

            if hasattr(operator_node, 'value') and operator_node.value in ["+", "-", "*", "/", "%", "==", "!=", "<",
                                                                           ">", "<=", ">=", "&&", "??"]:
                left_type = self.get_condition_type(left_expr)
                right_type = self.get_condition_type(right_expr)
                operator = operator_node.value

                print(f"Binary operation: {left_type} {operator} {right_type}")

                # Logical operators always return boolean
                if operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "??"]:
                    return "bool"

                # Type promotion rules for arithmetic
                if left_type == "skim" or right_type == "skim":
                    return "skim"
                elif left_type == "pinch" and right_type == "pinch":
                    return "pinch"
                elif left_type == "pasta" and right_type == "pasta" and operator == "+":
                    return "pasta"

        # For <literals> nodes
        if hasattr(expr_node, "value") and expr_node.value == "<literals>":
            return self.get_condition_type(expr_node.children[0])

        # Handle literals directly
        if hasattr(expr_node, 'value'):
            if hasattr(expr_node, 'node_type'):
                if expr_node.node_type == "pinchliterals":
                    return "pinch"
                elif expr_node.node_type == "skimliterals":
                    return "skim"
                elif expr_node.node_type == "pastaliterals":
                    return "pasta"

        # For parenthesized expressions
        if len(expr_node.children) >= 3 and hasattr(expr_node.children[0], 'value') and expr_node.children[
            0].value == "(":
            return self.get_condition_type(expr_node.children[1])

        # Debug - log if we couldn't determine the type
        print(
            f"Failed to determine type for condition: {expr_node.value if hasattr(expr_node, 'value') else 'unknown'}")
        return None

    def are_types_compatible(self, target_type, expr_type):
        """Check if expr_type is compatible with target_type."""
        if target_type is None or expr_type is None:
            return False  # Cannot determine compatibility
        
        print(f"Checking compatibility: target={target_type}, expr={expr_type}")
        
        # Handle array element type compatibility
        if isinstance(target_type, dict) and 'element_type' in target_type:
            target_elem_type = target_type['element_type']
            return expr_type in self.type_compatibility.get(target_elem_type, [])
        
        # Regular type compatibility
        return expr_type in self.type_compatibility.get(target_type, [])

    #-----------------------------------------------------------------
    # Declaration handling
    #-----------------------------------------------------------------
    def visit_global_dec(self, node):
        try:
            # Debug information
            print("\n=== Processing global declaration ===")
            print(f"Node value: {node.value if hasattr(node, 'value') else 'No value'}")
            print(f"Number of children: {len(node.children) if hasattr(node, 'children') else 0}")
            
            # Print structure of node for diagnosis
            if hasattr(node, 'children') and node.children:
                for i, child in enumerate(node.children):
                    print(f"Child {i} value: {child.value if hasattr(child, 'value') else 'No value'}")
                    if hasattr(child, 'children') and child.children:
                        print(f"  Grandchildren count: {len(child.children)}")
                        for j, grandchild in enumerate(child.children[:2]):  # Only print first 2 for brevity
                            print(f"  Grandchild {j} value: {grandchild.value if hasattr(grandchild, 'value') else 'No value'}")
            
            # Process each child of the global_dec node
            if hasattr(node, 'children'):
                for child in node.children:
                    if hasattr(child, 'children') and child.children:
                        # Check if this is an array declaration
                        if child.children[0].value == 'recipe':
                            print("Found array declaration in global scope")
                            self._handle_array_declaration(child)
                        else:
                            print("Found regular declaration in global scope")
                            self._handle_regular_declaration(child)
            
            #self.generic_visit(node)
        except IndexError as e:
            print(f"IndexError in visit_global_dec: {e}")
            # Add the stack trace for debugging
            import traceback
            traceback.print_exc()
            # Continue with generic visit to avoid breaking the analysis
            self.generic_visit(node)
        except Exception as e:
            print(f"Unexpected error in visit_global_dec: {e}")
            traceback.print_exc()
            self.generic_visit(node)

    def visit_declarations(self, node):
        print("\n" + "="*50)
        print("DEBUG: Processing declaration")
        print("="*50)
        
        if not node.children or len(node.children) < 2:
            return

        # Determine whether this is an array declaration or a regular variable declaration.
        if node.children and node.children[0].value == 'recipe':
            self._handle_array_declaration(node)
        else:
            # Get the variable type
            data_type_node = node.children[0].children[0]
            var_type = data_type_node.value
            print(f"Variable type: {var_type}")

            # Get the variable name
            id_node = node.children[1]
            var_name = id_node.value
            print(f"Variable name: {var_name}")

            # Create and add the symbol
            symbol = Symbol(var_name, var_type)
            self.current_scope.add(var_name, symbol)
            print(f"Added symbol: {symbol}")

            # Handle initialization if present
            if len(node.children) > 2 and node.children[2].value == "<dec_or_init>":
                init_node = node.children[2]
                if init_node.children and init_node.children[0].value == "=":
                    literals_node = init_node.children[1]
                    print(f"Literals node: {literals_node.value if hasattr(literals_node, 'value') else 'No value'}")

                    # Extract the literal value
                    value = None
                    if literals_node.value == "<literals>":
                        if literals_node.children and len(literals_node.children) > 0:
                            literal_child = literals_node.children[0]
                            if hasattr(literal_child, 'node_type'):
                                if literal_child.node_type == "pinchliterals":
                                    try:
                                        value = int(literal_child.value.replace("~", "-"))
                                        print(f"Extracted literal pinch value: {value}")
                                    except ValueError:
                                        print(f"Invalid pinch literal: {literal_child.value}")
                                elif literal_child.node_type == "skimliterals":
                                    try:
                                        value = float(literal_child.value.replace("~", "-"))
                                        print(f"Extracted literal skim value: {value}")
                                    except ValueError:
                                        print(f"Invalid skim literal: {literal_child.value}")
                                elif literal_child.node_type == "pastaliterals":
                                    value = literal_child.value.strip('"')
                                    print(f"Extracted literal pasta value: {value}")
                                elif literal_child.node_type == "<yum_or_bleh>":
                                    bool_val = literal_child.children[0].value
                                    value = bool_val
                    if value is not None:
                        symbol.set_value(value)
                        print(f"Initialized {var_name} with value: {value}")
                    else:
                        # If direct extraction failed, try the evaluator
                        value = self._evaluate_expression(literals_node)
                        if value is not None:
                            symbol.set_value(value)
                            print(f"Initialized {var_name} with evaluated value: {value}")

            #handle <next_dec_or_init>

        #self.generic_visit(node)

    def _handle_regular_declaration(self, node):
        if len(node.children) < 2:
            return

        # Get the variable type
        data_type_node = node.children[0].children[0]
        var_type = data_type_node.value
        print(f"Processing declaration with type: {var_type}")

        # Process first declaration
        id_node = node.children[1]
        var_name = id_node.value
        line_num = getattr(id_node, 'line_number', -1)
        print(f"Processing first variable: {var_name}")

        try:
            # Dictionary to hold all variables in this declaration
            variables_in_declaration = {}
            
            # Create symbol and add it to the current scope for the first variable
            symbol = Symbol(var_name, var_type)
            print(f"Adding symbol {var_name} to scope {self.current_scope.debugName}")
            self.current_scope.add(var_name, symbol)
            variables_in_declaration[var_name] = symbol
            
            # Process current declaration for initialization
            if len(node.children) > 2:
                dec_or_init = node.children[2]  # <dec_or_init>
                if dec_or_init.children and dec_or_init.children[0].value == "=":
                    # Handle initialization
                    literal_node = dec_or_init.children[1]
                    
                    # Try to extract literal value directly first
                    value = self._extract_literal_value(literal_node)

                    if value is not None:
                        symbol.set_value(value)
                        print(f"Set symbol {var_name} value directly: {value}")
                    else:
                        # If direct extraction failed, use the expression evaluator
                        value = self._evaluate_expression(literal_node)
                        if value is not None:
                            symbol.set_value(value)
                            print(f"Set symbol {var_name} value after evaluation: {value}")
                    
                    # Check type compatibility
                    self._check_initialization(var_name, var_type, literal_node, line_num)

                # Process additional declarations (variables after commas)
                print(f"\nProcessing additional variables for {var_type} declaration")
                
                # Helper function to find and process all variables in the declaration
                def find_additional_variables(current_node, depth=0):
                    indent = "  " * depth
                    print(f"{indent}Exploring node: {current_node.value if hasattr(current_node, 'value') else 'No value'}")
                    
                    # Skip if not a node with children or no children
                    if not hasattr(current_node, 'children') or not current_node.children:
                        return
                    
                    # Check if this is a comma, indicating another variable
                    if current_node.children[0].value == ",":
                        if len(current_node.children) > 1:
                            # The variable is the second child after the comma
                            var_id_node = current_node.children[1]
                            next_id = var_id_node.value
                            print(f"{indent}Found additional variable: {next_id}")
                            
                            # Create and register the variable
                            next_symbol = Symbol(next_id, var_type)
                            self.current_scope.add(next_id, next_symbol)
                            variables_in_declaration[next_id] = next_symbol
                            print(f"{indent}Registered {next_id} in symbol table")
                            
                            # Check for initialization
                            if len(current_node.children) > 2:
                                next_dec = current_node.children[2]
                                if next_dec.children and next_dec.children[0].value == "=":
                                    next_literal_node = next_dec.children[1]
                                    
                                    # Handle initialization
                                    print(f"{indent}Processing initialization for {next_id}")
                                    next_value = self._extract_literal_value(next_literal_node)
                                    if next_value is not None:
                                        next_symbol.set_value(next_value)
                                        print(f"{indent}Set {next_id} value directly: {next_value}")
                                    else:
                                        next_value = self._evaluate_expression(next_literal_node)
                                        if next_value is not None:
                                            next_symbol.set_value(next_value)
                                            print(f"{indent}Set {next_id} value after evaluation: {next_value}")
                                    
                                    # Check type compatibility
                                    self._check_initialization(next_id, var_type, next_literal_node, line_num)

                                # Check for more variables (recursive search)
                                find_additional_variables(next_dec, depth + 1)
                    
                    # Even if not a comma node, still check all children for commas
                    for child in current_node.children:
                        if hasattr(child, 'children') and child.children:
                            if child.children and child.children[0].value == ",":
                                find_additional_variables(child, depth + 1)
                
                # Start exploring from the first dec_or_init node
                find_additional_variables(dec_or_init)

                # Print final state for debug purposes
                print("\nFinal variable state after processing multi-variable declaration:")
                for name, sym in variables_in_declaration.items():
                    val = sym.get_value()
                    print(f"  {name}: {val} (type: {sym.type})")
                
        except SemanticError as e:
            self.errors.append(e)
            print(f"Error processing declaration: {e}")

    def _check_initialization(self, var_name, var_type, expr_node, line_num):
        """Helper method to check initialization type compatibility"""
        expr_type = self.get_expression_type(expr_node)

        if expr_type is not None and var_type is not None:
            compatible = self.are_types_compatible(var_type, expr_type)

            if not compatible:
                # Convert base types to literal types for error message
                literal_type = expr_type + "literals" if expr_type in ["pinch", "skim", "pasta"] else expr_type
                target_literal_type = var_type + "literals" if var_type in ["pinch", "skim", "pasta"] else var_type
                self.errors.append(SemanticError(
                    code="TYPE_MISMATCH",
                    message=f"Type mismatch in initialization of '{var_name}': cannot assign '{literal_type}' to '{target_literal_type}'",
                    line=line_num,
                    identifier=var_name
                ))

    def _handle_array_declaration(self, node):
        # Defensive checks
        if not hasattr(node, 'children'):
            return
        
        if len(node.children) < 5:
            return
        
        try:
            # Get array type
            if not hasattr(node.children[1], 'children') or not node.children[1].children:
                return
            
            data_type_node = node.children[1].children[0]
            var_type = data_type_node.value
            
            # Get array name
            id_node = node.children[2]
            var_name = id_node.value
            line_num = getattr(id_node, 'line_number', None)
            
            # Get array dimension
            dimension_node = node.children[4]

            #this part if   unnecessary, because the CFG already captures this shi,  ihhh biiihh
            try:
                dimension = int(dimension_node.value)
            except (ValueError, AttributeError) as e:
                dimension = None
                self.errors.append(SemanticError(
                    code="INVALID_ARRAY_SIZE",
                    message=f"Invalid array size for '{var_name}'", 
                    line=line_num, 
                    identifier=var_name
                ))
            
            attributes = {'dimensions': dimension, 'element_type': var_type}
            values = []
            element_ctr = 0;
            # Check initialization
            if len(node.children) > 6:
                elements_node = node.children[6]  # This is the <elements> node
                if hasattr(elements_node, 'children'):
                    first_literal_node = elements_node.children[2].children[0]

                    if not set(var_type).issubset(first_literal_node.node_type):
                        self.errors.append(SemanticError(
                            code="TYPE_MISMATCH",
                            message=f"Expected value '{var_type}' received value '{first_literal_node.node_type}'",
                            line=line_num,
                            identifier=var_name
                        ))

                    #append to the   value array ashjknddashjkdashjkasdhjkhjlkdas
                    values.append(first_literal_node.value)
                    element_ctr += 1

                    #check if there's more
                    element_tail = elements_node.children[3]
                    while element_tail.children:
                        literal_node = element_tail.children[1].children[0]

                        if not set(var_type).issubset(literal_node.node_type):
                            self.errors.append(SemanticError(
                                code="TYPE_MISMATCH",
                                message=f"Expected value '{var_type}' received value '{literal_node.node_type}'",
                                line=line_num,
                                identifier=var_name
                            ))
                            break

                        # append to the   value array ashjknddashjkdashjkasdhjkhjlkdas
                        values.append(literal_node.value)
                        element_ctr += 1
                        element_tail = element_tail.children[2]


                    # THIS   CODE IS RETARDATION, ISTG
                    # for child in elements_node.children:
                    #     if hasattr(child, 'value') and child.value == '<literals>':
                    #         # Found the literals node, check its children
                    #         for value_node in child.children:
                    #             value_type = self.get_expression_type(value_node)
                    #             if value_type and value_type != var_type:
                    #                 # Convert base types to literal types for error message
                    #                 literal_type = value_type + "literals" if value_type in ["pinch", "skim", "pasta"] else value_type
                    #                 target_literal_type = var_type + "literals" if var_type in ["pinch", "skim", "pasta"] else var_type
                    #                 self.errors.append(SemanticError(
                    #                     code="TYPE_MISMATCH",
                    #                     message=f"Type mismatch in array initialization of '{var_name}': cannot assign '{literal_type}' to '{target_literal_type}'",
                    #                     line=line_num,
                    #                     identifier=var_name
                    #                 ))
            
            # Add to symbol table
            symbol = Symbol(var_name, "recipe", attributes)
            if element_ctr < dimension and element_ctr != 0:
                self.errors.append(SemanticError(
                    code="MISSING_ELEMENTS",
                    message=f"Expected element count '{dimension}' received count '{element_ctr}'",
                    line=line_num,
                    identifier=var_name
                ))
            if element_ctr > dimension:
                self.errors.append(SemanticError(
                    code="TOO_MUCH_ELEMENTS",
                    message=f"Expected element count '{dimension}' received count '{element_ctr}'",
                    line=line_num,
                    identifier=var_name
                ))
            if values:
                symbol.set_value(values)
            self.current_scope.add(var_name, symbol)


            
        except Exception as e:
            if 'var_name' in locals() and 'line_num' in locals():
                self.errors.append(SemanticError(
                    code="INVALID_ARRAY_DECLARATION",
                    message=f"Invalid array declaration: {str(e)}",
                    line=line_num,
                    identifier=var_name
                ))

    def visit_local_declarations(self, node):
        print(f"\nProcessing local declaration in scope: {self.current_scope.debugName}")
        
        # Determine whether this is an array declaration or a regular variable declaration.
        if node.children and node.children[0].value == 'recipe':
            self._handle_array_declaration(node)
        else:
            self._handle_regular_declaration(node)
            
        #self.generic_visit(node)
    
    def visit_local_dec(self, node):
        print(f"\nProcessing local dec node in scope: {self.current_scope.debugName}")
        # Just genericVisit as the individual local_declarations will handle the work
        self.generic_visit(node)

    def _extract_literal_value(self, node):
        """Helper method to extract literal values from nodes"""

        if node is None:
            return None
            
        # Direct literal node
        if hasattr(node, 'node_type'):
            if node.node_type == "pinchliterals":
                try:
                    return int(node.value.replace("~", "-"))
                except ValueError:
                    return None
            elif node.node_type == "skimliterals":
                try:
                    return float(node.value.replace("~", "-"))
                except ValueError:
                    return None
            elif node.node_type == "pastaliterals":
                return node.value.strip('"')
            elif node.node_type == "bleh":
                return False
            elif node.node_type == "yum":
                return True

        # Node with children
        if hasattr(node, 'value') and hasattr(node, 'children') and node.children:
            # Handle literals node
            if node.value == "<literals>" and len(node.children) > 0:
                return self._extract_literal_value(node.children[0])
            elif node.value == "<yum_or_bleh>":
                return self._extract_literal_value(node.children[0])
        
        return None

    def lookup_symbol(self, name, mark_used=True):
        """Enhanced symbol lookup that tries harder to find symbols in all scopes"""
        print(f"Looking up symbol: {name} in current scope: {self.current_scope.debugName}")

        # First try the current scope
        if name in self.current_scope.symbols:
            symbol = self.current_scope.symbols[name]
            if mark_used:
                symbol.is_used = True
            print(f"Found symbol {name} in current scope {self.current_scope.debugName}")
            return symbol

        # If not found and there's a parent, try the parent scope
        if self.current_scope.parent:
            print(f"Symbol {name} not found in {self.current_scope.debugName}, checking parent")
            parent_result = self.current_scope.parent.lookup(name, mark_used)
            if parent_result:
                return parent_result

        # If still not found, search all symbol tables
        print(f"Symbol {name} not found in direct parent chain, searching all tables")
        for table in self.symbol_tables:
            if table != self.current_scope:  # Skip current scope as we already checked it
                if name in table.symbols:
                    symbol = table.symbols[name]
                    if mark_used:
                        symbol.is_used = True
                    print(f"Found symbol {name} in table {table.debugName}")
                    return symbol

        print(f"Symbol {name} not found in any scope")
        return None

    #-----------------------------------------------------------------
    # Function handling
    #-----------------------------------------------------------------
    def visit_function(self, node):
        """Handle function declarations"""
        print("\n=== Processing function declaration ===")
        
        # Get function name and return type
        if len(node.children) >= 3:
            if node.children[0].value == "full":
                # Full function with return type
                return_type = node.children[1].children[0].value
                func_name = node.children[2].value
                next_function = node.children[12]
            else:
                # Hungry function (void return)
                return_type = "void"
                func_name = node.children[1].value
                next_function = node.children[9]
            
            print(f"Found function: {func_name} with return type {return_type}")

            # Register the function in the global scope
            # try:
            #     self.global_scope.add(func_name, Symbol(func_name, "function", {"return_type": return_type}))
            #     print(f"Registered function {func_name} in global scope")
            # except SemanticError as e:
            #     self.errors.append(e)
            #     print("Error Registering function to global_scope")
            #     return
            if node.children[0].value == "hungry":
                important_nodes = [node.children[6], node.children[7]]
                parameter_node = node.children[3]
            else:
                important_nodes = [node.children[7], node.children[8], node.children[9]]
                parameter_node = node.children[4]
            symbol = Symbol(func_name, symbol_type="function", attributes={"return_type": return_type}, parameters=parameter_node)
            symbol.set_value(important_nodes)
            self.current_scope.add(func_name, symbol)

            """
                need to not make this run
                so i   turned commented it for now
                will just add a checking later
            """

            if next_function:   
                self.visit_function(next_function)

            # Create a new scope for the function body
            #old_scope = self.current_scope
            #self.current_scope = SymbolTable(debugName=f"function_{func_name}", parent=old_scope)
            #self.symbol_tables.append(self.current_scope)
            
            # Process function parameters first
            #self._process_function_signature(node)
            
            # Then process the function body
            #self.generic_visit(node)
            
            # Restore the previous scope
            #self.current_scope = old_scope

    def _process_function_signature(self, node):
        # Process the function signature to extract (and possibly record) the function name and its return type.
        if len(node.children) < 3:
            return
        if node.children[0].value in ["full", "hungry"]:
            # For "full" functions, the signature is: full <data_type> id ( <parameters> ) { ... }
            if node.children[0].value == "full":
                return_type_node = node.children[1].children[0]
                id_node = node.children[2]
                self.current_function = {"name": id_node.value, "return_type": return_type_node.value}
            else:  # "hungry" functions have no explicit return type in the signature.
                id_node = node.children[1]
                self.current_function = {"name": id_node.value, "return_type": "void"}

    #-----------------------------------------------------------------
    # Statement handling (including assignment checking)
    #-----------------------------------------------------------------
    def visit_statement(self, node):
        if not node.children:
            return
        
        print("\n" + "="*50)
        print("DEBUG: Starting statement processing")
        print("="*50)
        
        # Debug - print what kind of statement we're processing
        print(f"\n=== Processing statement ===")
        print(f"Statement node: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"Statement children: {[child.value if hasattr(child, 'value') else 'No value' for child in node.children]}")
        
        # Check if this is an assignment
        if len(node.children) >= 2:
            first_child = node.children[0]
            second_child = node.children[1]
            
            print(f"\nFirst child: {first_child.value if hasattr(first_child, 'value') else 'No value'}")
            print(f"First child type: {first_child.node_type if hasattr(first_child, 'node_type') else 'No type'}")
            print(f"Second child: {second_child.value if hasattr(second_child, 'value') else 'No value'}")
            print(f"Second child type: {second_child.node_type if hasattr(second_child, 'node_type') else 'No type'}")
            
            # Check if this is an assignment statement
            if hasattr(first_child, 'node_type') and first_child.node_type == "id":
                var_name = first_child.value
                print(f"\nFound identifier: {var_name}")
                
                # Check if this has an assignment operator
                if hasattr(second_child, 'value') and second_child.value == "<statement_id_tail>":
                    print("\nFound statement_id_tail")
                    print(f"Statement_id_tail children: {[child.value if hasattr(child, 'value') else 'No value' for child in second_child.children]}")
                    
                    if second_child.children and len(second_child.children) >= 2:

                        if second_child.children[0].value == "(":
                            return_val = self.get_function_return(first_child.value, second_child.children[1], True)
                            if not return_val:
                                return None


                        else:
                            # Unwrap the real operator string
                            raw_op = None
                            operator_node = second_child.children[0]
                            print(operator_node.node_type)

                            # If it's an <assignment_operator> wrapper, grab its child token
                            if operator_node.value == "<assignment_operator>" and operator_node.children:
                                raw_op = operator_node.children[0].value
                                print(f"Found wrapped operator: {raw_op}")
                            # Otherwise maybe it was exposed directly
                            elif operator_node.value in ["=", "+=", "-=", "*=", "/=", "%="]:
                                raw_op = operator_node.value
                                print(f"Found direct operator: {raw_op}")
                            elif operator_node.value == '<unary_op>':
                                raw_op = operator_node.children[0].value
                                print(f"Found direct operator: {raw_op}")
                            expr_node = second_child.children[1]

                            print(f"\nProcessing expression for {var_name}")
                            print(f"Operator: {raw_op}")
                            print(f"Expression node: {expr_node.value if hasattr(expr_node, 'value') else 'No value'}")
                            print(f"Expression node type: {expr_node.node_type if hasattr(expr_node, 'node_type') else 'No type'}")
                            print(f"Expression children: {[child.value if hasattr(child, 'value') else 'No value' for child in expr_node.children] if hasattr(expr_node, 'children') else 'No children'}")

                            if raw_op in ["=", "+=", "-=", "*=", "/=", "%="]:
                                print(f"\nFound assignment operator: {raw_op}")

                                # Look up the symbol
                                symbol = self.current_scope.lookup(var_name)
                                if not symbol:
                                    # If symbol doesn't exist, create it as a pinch type
                                    # print(f"Creating new symbol for {var_name}")
                                    # symbol = Symbol(var_name, "pinch")
                                    # self.current_scope.add(var_name, symbol)
                                    line_num = getattr(node, 'line_number', None)
                                    self.errors.append(SemanticError(
                                        code="UNDECLARED_IDENTIFIER",
                                        message=f"Identifier [{first_child.value}] does not exist!",
                                        line=line_num,
                                        identifier=first_child.value
                                    ))
                                    return None  # testing

                                print(f"\nFound symbol: {symbol}")
                                print(f"Current symbol value: {symbol.get_value()}")

                                # Evaluate the expression
                                print("\nEvaluating expression...")
                                print(f"Expression node structure before evaluation:")
                                self._print_node_structure(expr_node)

                                value = self._evaluate_condition(expr_node)
                                print(f"Expression evaluation result: {value}")


                                #checking match types
                                if ((symbol.type == 'pasta' and not isinstance(value, str)) or ((symbol.type == 'pinch' or symbol.type == 'skim') and isinstance(value, str))) or (symbol.type == 'bool' and value not in ['yum', 'bleh', 1, 0]):
                                    self.errors.append(SemanticError(
                                        code="TYPE_MISMATCH",
                                        message=f"Type mismatch in using operator[{raw_op}] to assign value to id[{symbol.type}] with value[{value}]",
                                        line=getattr(expr_node, 'line_number', None)
                                    ))
                                    return
                                #value validation
                                if symbol.type == 'pinch':
                                    value = int(value)
                                elif symbol.type == 'skim':
                                    value = float(value)

                                if value is not None:
                                    # Handle different assignment operators
                                    if raw_op == "=":
                                        symbol.set_value(value)
                                    elif raw_op == "+=":
                                        if symbol.type == 'pasta':
                                            symbol.set_value(str((symbol.get_value()) or "") + str(value))
                                        else:
                                            symbol.set_value((symbol.get_value() or 0) + value)
                                    elif raw_op == "-=":
                                        symbol.set_value((symbol.get_value() or 0) - value)
                                    elif raw_op == "*=":
                                        symbol.set_value((symbol.get_value() or 0) * value)
                                    elif raw_op == "/=":
                                        if value == 0:
                                            self.errors.append(SemanticError(
                                                code="DIVISION_BY_ZERO",
                                                message="Division by zero in assignment",
                                                line=getattr(expr_node, 'line_number', None)
                                            ))
                                        else:
                                            symbol.set_value((symbol.get_value() or 0) / value)
                                    elif raw_op == "%=":
                                        if value == 0:
                                            self.errors.append(SemanticError(
                                                code="DIVISION_BY_ZERO",
                                                message="Modulo by zero in assignment",
                                                line=getattr(expr_node, 'line_number', None)
                                            ))
                                        else:
                                            symbol.set_value((symbol.get_value() or 0) % value)
                                    print(f"Updated symbol value: {symbol.get_value()}")
                                else:
                                    print(f"\nWARNING: Expression evaluation returned None for {var_name}")
                                    print("Expression node structure:")
                                    #self._print_node_structure(expr_node)
                                    print("\nCurrent scope symbols:")
                                    #self._print_scope_symbols()
                            elif raw_op in ["++", "--"]:
                                print(f"\nFound inc_dec operator: {raw_op}")

                                # Look up the symbol
                                symbol = self.current_scope.lookup(var_name)
                                if not symbol:
                                    line_num = getattr(node, 'line_number', None)
                                    self.errors.append(SemanticError(
                                        code="UNDEFINED_VARIABLE",
                                        message=f"VARIABLE '{var_name}' is UNDEFINED!",
                                        line=line_num
                                    ))
                                    return
                                if raw_op == '++':
                                    symbol.set_value((symbol.get_value() or 0) + 1)
                                elif raw_op == '--':
                                    symbol.set_value((symbol.get_value() or 0) - 1)
            elif hasattr(first_child, 'node_type') and first_child.node_type == "<unary_op>":
                var_name = second_child.value
                var_op = first_child.children[0].value
                # Look up the symbol
                symbol = self.current_scope.lookup(var_name)
                if not symbol:
                    line_num = getattr(node, 'line_number', None)
                    self.errors.append(SemanticError(
                        code="UNDEFINED_VARIABLE",
                        message=f"VARIABLE '{var_name}' is UNDEFINED!",
                        line=line_num
                    ))
                    return
                print(var_op)
                if var_op == '++':
                    symbol.set_value((symbol.get_value() or 0) + 1)
                elif var_op == '--':
                    symbol.set_value((symbol.get_value() or 0) - 1)
        # Continue with generic visit to process other types of statements
        #if node.children[0].value in ["serve", "make", "for", "simmer", "keepmix", "taste", "flip", "elif", "mix"]:
        if node.value == '<statement>':
            self.generic_visit(node)

    def get_function_return(self, var_name, node, is_void=False):
        symbol = self.lookup_symbol(var_name)
        print(f"Found Function Call[symbol]={symbol}")
        if not is_void:
            if symbol.attributes.get("return_type", "none") == 'void':
                self.errors.append(SemanticError(
                    code="VOID_FUNCTION",
                    message="Void functions does not return a value!",
                    line=getattr(node, 'line_number', None)
                ))
                return None

        argument_node = node
        # Create a new scope for the function body
        old_scope = self.current_scope
        self.current_scope = SymbolTable(debugName=f"function_{var_name}", parent=old_scope)
        self.symbol_tables.append(self.current_scope)

        # needs to process parameters
        parameter_node = symbol.parameters
        while parameter_node.children and argument_node.children:
            # process the   parameter
            if parameter_node.children[0].value == ',':
                data_type = parameter_node.children[1].children[0].value
                data_name = parameter_node.children[2].value
                parameter_node = parameter_node.children[3]
            else:
                data_type = parameter_node.children[0].children[0].value
                data_name = parameter_node.children[1].value
                parameter_node = parameter_node.children[2]
            # assign the   argument to the   parameter

            if argument_node.children[0].value == ',':
                data_val = self._evaluate_expression(argument_node.children[1])
                argument_node = argument_node.children[2]
            else:
                data_val = self._evaluate_expression(argument_node.children[0])
                argument_node = argument_node.children[1]
            attributes = None
            if isinstance(data_val, list):
                dimension = len(data_val)
                attributes = {'dimensions': dimension, 'element_type': data_type}
                data_type = "recipe"
            new_symbol = Symbol(data_name, data_type, attributes)
            new_symbol.set_value(data_val)
            self.current_scope.add(data_name, new_symbol)

        # add error handling here for the parameter and arguments
        if parameter_node.children:
            self.errors.append(SemanticError(
                code="MISSING_ARGUMENTS",
                message="Doesn't meet the required number of arguments!",
                line=getattr(node, 'line_number', None)
            ))
            return None
        if argument_node.children:
            self.errors.append(SemanticError(
                code="TOO_MANY_ARGUMENTS",
                message="Too many arguments provided to function call!",
                line=getattr(node, 'line_number', None)
            ))
            return None

        # did it this way so that i don't need to add the spit on the visit_statement,   that
        self.generic_visit(symbol.value[0])
        self.generic_visit(symbol.value[1])

        return_val = ""
        if not is_void:
            return_node = symbol.value[2]
            return_val = self._evaluate_expression(return_node.children[1])

        self.current_scope = old_scope
        self.symbol_tables.pop()
        if not is_void:
            return return_val

    def replace_if_bool(self, s):
        if s == "True":
            return "yum"
        elif s == "False":
            return "bleh"
        else:
            return s

    def visit_serve_statement(self, node, parent=None):
        """Handle the 'serve' statement (function call)"""
        print("\n" + "="*50)
        print("DEBUG: Processing serve statement")
        print("="*50)
        print(f"Current scope: {self.current_scope.debugName}")
        
        # If we have a parent node, use it
        if parent and hasattr(parent, 'children') and len(parent.children) >= 3:
            statement_node = parent
            print("Using parent node for statement")
        else:
            # Otherwise, look for the statement node in the current node's children
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    if hasattr(child, 'value') and child.value == "<statement>":
                        statement_node = child
                        print("Found statement node in children")
                        break
                else:
                    print("No statement node found")
                    return
            else:
                print("No children in node")
                return
        
        # The argument should be in the third child (index 2)
        if len(statement_node.children) < 3:
            print("Statement node has insufficient children")
            return

        arg_node = statement_node.children[2]
        print(f"\nArgument node: {arg_node.value if hasattr(arg_node, 'value') else 'No value'}")
        print(f"Argument node type: {arg_node.node_type if hasattr(arg_node, 'node_type') else 'No type'}")
        
        # Handle string concatenation
        result = ""
        
        # Process the initial value3
        if hasattr(arg_node, 'children') and arg_node.children:
            initial_node = arg_node.children[0]
            #are you   retarded????? why would you   include the ID checking here ???? it doesn't have childrennnnn????????????
            if hasattr(initial_node, 'children') and initial_node.children:
                first_value = initial_node.children[0]
                print(f"\nProcessing initial value3")
                print(f"First value node: {first_value.value if hasattr(first_value, 'value') else 'No value'}")
                print(f"First value type: {first_value.node_type if hasattr(first_value, 'node_type') else 'No type'}")
                
                if hasattr(first_value, 'node_type'):
                    if first_value.node_type == "pastaliterals":
                        result = first_value.value.strip('"')
                        print(f"Found string literal: {result}")
            elif initial_node.node_type == 'id':
                #it   works now
                tail_node = arg_node.children[1]


                #check if the symbol exist, for   error checking alnhjsdljkasldhjkasas
                if not self.lookup_symbol(initial_node.value) and not initial_node.value == "len":
                    line_num = getattr(node, 'line_number', None)
                    self.errors.append(SemanticError(
                        code="UNDEFINED_IDENTIFIER",
                        message=f"Identifier [{initial_node.value}] does not exist!",
                        line=line_num,
                        identifier=initial_node.value
                    ))
                    return

                #NEED TO   CONFIRM IF ARRAYS AND FUNCTIONS CAN BE CALLED INSIDE THE DAMN SERVE
                if tail_node.children:
                    if tail_node.children[0].value == "[":
                        if initial_node.value == "len":
                            line_num = getattr(node, 'line_number', None)
                            self.errors.append(SemanticError(
                                code="NOT_A_RECIPE",
                                message=f"Identifier [{initial_node.value}] is a function!",
                                line=line_num,
                                identifier=initial_node.value
                            ))
                            return
                        #it's a   array <3   this shi
                        index_value = int(self._evaluate_expression(tail_node.children[1]))
                        symbol = self.lookup_symbol(initial_node.value)
                        listed_value = list(symbol.get_value())
                        if index_value >= len(listed_value):
                            line_num = getattr(node, 'line_number', None)
                            var_name = initial_node.value
                            self.errors.append(SemanticError(
                                code="ARRAY_OUT_OF_BOUNDS",
                                message=f"Accessed an index outside the allowed range. index[{index_value}]:range[{len(listed_value)-1}]",
                                line=line_num,
                                identifier=var_name
                            ))
                            return
                        result = self.replace_if_bool(str(listed_value[index_value]).replace('"', '').replace("-", "~"))
                    elif tail_node.children[0].value == "(":
                        if initial_node.value == "len":
                            # add error handling here for the parameter and arguments
                            if not tail_node.children[1].children:
                                self.errors.append(SemanticError(
                                    code="MISSING_ARGUMENTS",
                                    message=f"Doesn't meet the required number of arguments for [{initial_node.value}]!",
                                    line=getattr(node, 'line_number', None)
                                ))
                                return None
                            if "," in str(tail_node.children[1]):
                                self.errors.append(SemanticError(
                                    code="TOO_MANY_ARGUMENTS",
                                    message=f"Too many arguments provided to function call [{initial_node.value}]!",
                                    line=getattr(node, 'line_number', None)
                                ))
                                return None
                            return_val = len(self._evaluate_expression(tail_node.children[1]))
                        else:
                            return_val = self.get_function_return(initial_node.value, tail_node.children[1])
                        if return_val:
                            result = self.replace_if_bool(str(return_val).replace('"', '').replace("-", "~"))
                else:
                    symbol = self.lookup_symbol(initial_node.value)
                    print(f"Found symbol: {symbol}")
                    result = self.replace_if_bool(str(symbol.get_value() if hasattr(symbol, 'get_value') else "").replace("-", "~"))

            else:
                print("acts as a fallback to do some shit[serve]")
        # Process any serve_tail concatenations
        if len(statement_node.children) > 3:
            serve_tail = statement_node.children[3]
            print("\nProcessing serve_tail")
            while hasattr(serve_tail, 'children') and serve_tail.children:
                if serve_tail.children[0].value == "+":
                    print("Found concatenation operator")
                    # Get the next value3
                    next_value_node = serve_tail.children[1]
                    if hasattr(next_value_node, 'children') and next_value_node.children:
                        next_value = next_value_node.children[0]
                        print(f"\nNext value node: {next_value.value if hasattr(next_value, 'value') else 'No value'}")
                        print(f"Next value type: {next_value.node_type if hasattr(next_value, 'node_type') else 'No type'}")
                        
                        if hasattr(next_value, 'children') and next_value.children:
                            add_node = next_value.children[0]
                            if add_node.node_type == "pastaliterals":
                                result += add_node.value.strip('"')
                                print(f"Concatenated string literal: {result}")
                            else:
                                print("Hello World!")
                        elif next_value.node_type == 'id':
                            # it   works now
                            tail_node = next_value_node.children[1]

                            # check if the symbol exist, for   error checking alnhjsdljkasldhjkasas
                            if not self.lookup_symbol(next_value.value):
                                line_num = getattr(node, 'line_number', None)
                                self.errors.append(SemanticError(
                                    code="UNDEFINED_IDENTIFIER",
                                    message=f"Identifier [{next_value.value}] does not exist!",
                                    line=line_num,
                                    identifier=next_value.value
                                ))
                                return
                            # NEED TO   CONFIRM IF ARRAYS AND FUNCTIONS CAN BE CALLED INSIDE THE DAMN SERVE
                            if tail_node.children:
                                if tail_node.children[0].value == "[":
                                    # it's a   array <3   this shi
                                    index_value = int(self._evaluate_expression(tail_node.children[1]))
                                    symbol = self.lookup_symbol(next_value.value)
                                    listed_value = list(symbol.get_value())
                                    if index_value >= len(listed_value):
                                        line_num = getattr(node, 'line_number', None)
                                        var_name = next_value.value
                                        self.errors.append(SemanticError(
                                            code="ARRAY_OUT_OF_BOUNDS",
                                            message=f"Accessed an index outside the allowed range. index[{index_value}]:range[{len(listed_value) - 1}]",
                                            line=line_num,
                                            identifier=var_name
                                        ))
                                        return
                                    result += self.replace_if_bool(str(listed_value[index_value]).replace('"', '').replace("-", "~"))
                                elif tail_node.children[0].value == "(":
                                    return_val = self.get_function_return(next_value.value, tail_node.children[1])
                                    if return_val:
                                        result += self.replace_if_bool(str(return_val).replace('"', '').replace("-", "~"))
                            else:
                                symbol = self.lookup_symbol(next_value.value)
                                print(f"Found symbol: {symbol}")
                                result += self.replace_if_bool(str(symbol.get_value() if hasattr(symbol, 'get_value') else "").replace("-", "~"))

                            print(f"Concatenated result: {result}")
                    # Move to next serve_tail if exists
                    if len(serve_tail.children) > 2:
                        serve_tail = serve_tail.children[2]
                        print("Moving to next serve_tail")
                    else:
                        print("No more serve_tail to process")
                        break
                else:
                    print("hi")
                    break
        
        print(f"\nFinal concatenated result: {result}")
        if result:  # Only add non-empty results
            self.output_buffer.append(result)

    def visit_make_statement(self, node, parent=None):
        """Handle the 'serve' statement (function call)"""
        print("\n" + "=" * 50)
        print("DEBUG: Processing make statement")
        print("=" * 50)
        print(f"Current scope: {self.current_scope.debugName}")

        # If we have a parent node, use it
        if parent and hasattr(parent, 'children') and len(parent.children) >= 3:
            statement_node = parent
            print("Using parent node for statement")
        else:
            # Otherwise, look for the statement node in the current node's children
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    if hasattr(child, 'value') and child.value == "<statement>":
                        statement_node = child
                        print("Found statement node in children")
                        break
                else:
                    print("No statement node found")
                    return
            else:
                print("No children in node")
                return

        # The argument should be in the third child (index 2)
        if len(statement_node.children) < 3:
            print("Statement node has insufficient children")
            return

        # children 2 'cause that shi is the second, second   dumbahh
        arg_node = statement_node.children[2]
        print(f"\nArgument node: {arg_node.value if hasattr(arg_node, 'value') else 'No value'}")
        print(f"Argument node type: {arg_node.node_type if hasattr(arg_node, 'node_type') else 'No type'}")

        if arg_node.node_type == 'id':
            #val = input("ask for input: ")
            #raise Exception("Needs input for identifier")
            symbol = self.lookup_symbol(arg_node.value)
            if not symbol:
                line_num = getattr(node, 'line_number', None)
                self.errors.append(SemanticError(
                    "UNDECLARED_VARIABLE",
                    f"Identifier [{arg_node.value}] does not exist!",
                    line=line_num
                ))
                return None
            def validate_input(val):
                # Check if the value is None (cancelled)
                if val is None:
                    return None
                val = val.replace("~", "-")

                # Check if the value is a valid number (float or int)
                try:
                    # Try converting the input to a float (this will handle both int and float cases)
                    float_val = float(val)
                    # Check if the value can be safely cast to an int (if it's an integer value)
                    if float_val.is_integer():
                        return int(float_val)  # Return as integer
                    else:
                        return float_val  # Return as float
                except ValueError:
                    # If it's not a number, check if it's a string (non-empty)
                    if isinstance(val, str) and val.strip() != "":
                        return val  # Return as string
                    else:
                        return None  # Return None if it's an invalid input

            val = simpledialog.askstring("Input needed", f"Please enter value for [{symbol.name}]:")

            val = validate_input(val)

            if (symbol.type == 'pinch' and not isinstance(val, int) or
                    symbol.type == 'pasta' and not isinstance(val, str) or
                    symbol.type == 'skim' and not isinstance(val, float) or
                    val is None):
                line_num = getattr(node, 'line_number', None)
                self.errors.append(SemanticError(
                    "INVALID_VALUE",
                    f"{val} is not allowed to be passed to {symbol.type} type",
                    line=line_num
                ))
                return None
            if symbol.type == 'pinch':
                if val < -999999999 or val > 999999999:
                    line_num = getattr(node, 'line_number', None)
                    self.errors.append(SemanticError(
                        "INVALID_VALUE",
                        f"[pinch] can only hold values from [-999999999 to 999999999]",
                        line=line_num
                    ))
                    return None
            symbol.value = val
            self.output_buffer.append("input: " + str(val).replace("-","~") + "")

    def _evaluate_function_call(self, func_name):
        """Evaluate a function call and return its output"""
        print(f"\n=== Evaluating function call: {func_name} ===")
        
        # Look up the function in the symbol table
        func_symbol = self.global_scope.lookup(func_name)
        if not func_symbol or func_symbol.type != "function":
            print(f"Function {func_name} not found in symbol table")
            return None
        
        print(f"Found function symbol: {func_symbol}")
        
        # Find the function's body in the AST
        if not hasattr(self, 'parse_tree') or not self.parse_tree:
            print("No parse tree available")
            return None
            
        print("Searching for function definition in parse tree...")
        
        # First find the <function> node
        function_node = None
        for node in self.parse_tree.children:
            if hasattr(node, 'value') and node.value == "<function>":
                print(f"Found function node: {node.value}")
                # Check if this is the function we're looking for
                if len(node.children) >= 3:
                    if node.children[0].value == "full" and node.children[2].value == func_name:
                        function_node = node
                        print(f"Found full function definition for {func_name}")
                        break
                    elif node.children[0].value == "hungry" and node.children[1].value == func_name:
                        function_node = node
                        print(f"Found hungry function definition for {func_name}")
                        break
        
        if not function_node:
            print(f"Could not find function definition for {func_name}")
            return None
            
        print(f"Found function definition for {func_name}")
        
        # Create a new scope for the function
        old_scope = self.current_scope
        self.current_scope = SymbolTable(debugName=f"function_{func_name}", parent=old_scope)
        
        # Store the current output buffer and create a new one for the function
        old_output_buffer = self.output_buffer
        self.output_buffer = []
        
        try:
            # Execute the function body
            for child in function_node.children:
                if hasattr(child, 'value') and child.value == "<statement_block>":
                    print("Processing function body...")
                    for stmt in child.children:
                        if hasattr(stmt, 'value') and stmt.value == "<statement>":
                            self.visit(stmt)
            
            # Get the function's output
            function_output = self.output_buffer.copy()
            print(f"Function {func_name} output: {function_output}")
            
            return function_output
            
        finally:
            # Always restore the previous scope and output buffer
            self.current_scope = old_scope
            self.output_buffer = old_output_buffer

    def get_output(self):
        """Get the accumulated output from serve statements"""
        if not self.output_buffer:
            return "===Program executed successfully==="
        
        # Process each item in the output buffer
        processed_output = []
        for item in self.output_buffer:
            # Strip quotes from string literals if present
            if isinstance(item, str):
                item = item.strip('"')
            processed_output.append(str(item))
        
        # Join the processed output with newlines
        output = "\n".join(processed_output)
        
        # Only add success message if we have actual output
        if output:
            output += "\n\n===Program executed successfully==="
        
        return output
    
    def visit_looping_statement(self, node):
        if not node.children:
            return
        first_child = node.children[0]
        #add scope for the local-local
        old_scope = self.current_scope

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.current_scope = SymbolTable(debugName=f"loop_{timestamp}", parent=old_scope)
        self.symbol_tables.append(self.current_scope)

        if hasattr(first_child, 'node_type') and first_child.node_type == "for":
            self._handle_for_loop(node)
        elif hasattr(first_child, 'node_type') and first_child.node_type == "simmer":
            self._handle_simmer_loop(node)
        elif hasattr(first_child, 'node_type') and first_child.node_type == "keepmix":
            self._handle_keepmix_loop(node)

        self.symbol_tables.pop()
        self.current_scope = old_scope
        
        # Continue with the generic visit to process child nodes???????? ARE YOU   RETARDED? THIS IS A   LOOP
        #self.generic_visit(node)

    def visit_conditional_statement(self, node):
        if not node.children:
            return
        first_child = node.children[0]

        if hasattr(first_child, 'node_type') and first_child.node_type == "taste":
            self._handle_taste_condition(node)
        elif hasattr(first_child, 'node_type') and first_child.node_type == "flip":
            self._handle_flip_condition(node)

    def _handle_taste_condition(self, node):
        """
            1: check the   condition
            2: execute code block if the   condition is true
            3: check for the   conditional_tail
        """


        condition_node = node.children[2]
        eval_result = self._evaluate_condition(condition_node)
        print(f"Taste Condition Evaluation := " + str(eval_result))
        if eval_result:
            # add scope for the local-local
            old_scope = self.current_scope
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self.current_scope = SymbolTable(debugName=f"conditional_{timestamp}", parent=old_scope)
            self.symbol_tables.append(self.current_scope)

            statement_node = node.children[5]
            self.generic_visit(statement_node)

            self.symbol_tables.pop()
            self.current_scope = old_scope
        else:
            tail_node = node.children[7]
            self._handle_conditional_tail(tail_node)

    def _handle_flip_condition(self, node):
        """
            1: get the   base variable
            2: compare the   variable to each cases
            3: pretty much the   same with if-elif-else
        """

        variable = node.children[2]
        symbol = self.lookup_symbol(variable.value)
        case_val = node.children[6].children[0]

        if case_val.node_type == 'pinchliterals':
            case_val = int(case_val.value)
            eval_result = int(symbol.get_value()) == case_val
        else:
            case_val = str(case_val.value)
            eval_result = str(symbol.get_value()) == case_val
        if eval_result:
            statement_node = node.children[8]
            self.generic_visit(statement_node)
        else:
            case_tail = node.children[11]
            self._handle_case_tail(variable, case_tail)

    def _handle_case_tail(self, id_node, node):
        """
                    1: check the first   case and compare
                    2: if true execute yourself   you
                    3: if not, check the rest of the cases
                """

        if not node.children:
            return

        variable = id_node
        symbol = self.lookup_symbol(variable.value)

        first_child = node.children[0]
        if hasattr(first_child, 'node_type') and first_child.node_type == "case":
            case_val = node.children[1].children[0]
            if case_val.node_type == 'pinchliterals':
                case_val = int(case_val.value)
                eval_result = int(symbol.get_value()) == case_val
            else:
                case_val = str(case_val.value)
                eval_result = str(symbol.get_value()) == case_val
            if eval_result:
                statement_node = node.children[3]
                self.generic_visit(statement_node)
            else:
                case_tail = node.children[6]
                self._handle_case_tail(id_node, case_tail)
        elif hasattr(first_child, 'node_type') and first_child.node_type == "default":
            statement_node = node.children[2]
            print(statement_node)
            self.generic_visit(statement_node)



    def _handle_conditional_tail(self, node):
        """
            1: check for the   condition
            2: if there is still some   recall this
            3: if it becomes null, then nothing
        """
        if not node.children:
            return

        first_child = node.children[0]

        if hasattr(first_child, 'node_type') and first_child.node_type == "elif":
            condition_node = node.children[2]
            eval_result = self._evaluate_condition(condition_node)
            print(f"Taste Condition Evaluation := " + str(eval_result))
            if eval_result:

                # add scope for the local-local
                old_scope = self.current_scope
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                self.current_scope = SymbolTable(debugName=f"conditional_{timestamp}", parent=old_scope)
                self.symbol_tables.append(self.current_scope)

                statement_node = node.children[5]
                self.generic_visit(statement_node)

                self.symbol_tables.pop()
                self.current_scope = old_scope
            else:
                tail_node = node.children[7]
                self._handle_conditional_tail(tail_node)
        elif hasattr(first_child, 'node_type') and first_child.node_type == "mix":
                # add scope for the local-local
                old_scope = self.current_scope
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                self.current_scope = SymbolTable(debugName=f"conditional_{timestamp}", parent=old_scope)
                self.symbol_tables.append(self.current_scope)

                statement_node = node.children[2]
                self.generic_visit(statement_node)

                #remove scope
                self.symbol_tables.pop()
                self.current_scope = old_scope

    def _handle_keepmix_loop(self, node):
        """
            1: execute the mother  code
            2: check the   condition
            3: loop 1 if the   condition is true
        """
        """NEW, uses python while loop"""

        _current_iteration_count = 1
        statement_node = node.children[2]
        self.generic_visit(statement_node)

        condition_node = node.children[6]
        eval_result = self._evaluate_condition(condition_node)
        print(f"Do-While Condition Evaluation := " + str(eval_result))

        while eval_result and self.MAX_LOOP_ITERATION > _current_iteration_count:
            self.generic_visit(statement_node)
            eval_result = self._evaluate_condition(condition_node)
            _current_iteration_count += 1

        if self.MAX_LOOP_ITERATION <= _current_iteration_count:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INFINITE_LOOP_RISK",
                message=f"The loop exceeded the set limit of iteration counts[{self.MAX_LOOP_ITERATION}]",
                line=line_num
            ))
            return

        """OLD, uses recursion"""
        # statement_node = node.children[2]
        # self.generic_visit(statement_node)
        #
        # condition_node = node.children[6]
        # eval_result = self._evaluate_condition(condition_node)
        # print(f"Do-While Condition Evaluation := " + str(eval_result))
        # if eval_result:
        #     self._handle_keepmix_loop(node)

    def _handle_simmer_loop(self, node):
        """
            -----  loop-----
            1: check the   condition
            2: execute the   code
            -----  loop-----
        """
        """NEW, just python while loop"""
        condition_node = node.children[2]
        eval_result = self._evaluate_condition(condition_node)
        _current_iteration_count = 0
        print(f"While Condition Evaluation := " + str(eval_result))
        while eval_result and self.MAX_LOOP_ITERATION > _current_iteration_count:
            statement_node = node.children[5]
            self.generic_visit(statement_node)
            eval_result = self._evaluate_condition(condition_node)
            _current_iteration_count += 1

        if self.MAX_LOOP_ITERATION <= _current_iteration_count:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INFINITE_LOOP_RISK",
                message=f"The loop exceeded the set limit of iteration counts[{self.MAX_LOOP_ITERATION}]",
                line=line_num
            ))
            return
        """OLD, uses recursion"""
        # condition_node = node.children[2]
        # eval_result = self._evaluate_condition(condition_node)
        # print(f"While Condition Evaluation := " + str(eval_result))
        # if eval_result:
        #     statement_node = node.children[5]
        #     self.generic_visit(statement_node)
        #     self._handle_simmer_loop(node)

    def _handle_for_loop(self, node, loop=False):
        # Expected structure: for ( <assignment> ; <expression> ; <assignment> ) <statement>
        # general   process
        """
            1: assign the   variables
            -----  loop-----
            2: check the   condition
            3: execute the   code block
            4: increment/decrement
            -----  loop-----
        """

        """NEW, uses python while loop"""
        #need to do the assignment first!
        _dtype = node.children[2]
        _dname = node.children[3].value
        _dvalue = node.children[5].children[0]

        #for infinite loop checking
        _current_iteration_count = 0

        if _dtype.children:
            # Create symbol and add it to the current scope for the first variable
            symbol = Symbol(_dname, _dtype.children[0].value)
            print(f"Adding symbol {_dname} to scope {self.current_scope.debugName}")
            self.current_scope.add(_dname, symbol)
            if _dvalue.node_type == "id":
                _dvalue = self.lookup_symbol(_dvalue.value)
            else:
                _dvalue = self._extract_literal_value(_dvalue)

            if _dvalue is not None:
                symbol.set_value(_dvalue)
        else:
            symbol = self.lookup_symbol(_dname)
            if _dvalue.node_type == "id":
                _dvalue = self.lookup_symbol(_dvalue.value)
            else:
                _dvalue = self._extract_literal_value(_dvalue)
            print(f"Replacing value of {_dname} to {_dvalue} from scope {self.current_scope.debugName}")

            if _dvalue is not None:
                symbol.set_value(_dvalue)

        condition_expr = node.children[7]
        eval_result = self._evaluate_condition(condition_expr)
        print(f"For Condition Evaluation := " + str(eval_result))

        while eval_result and self.MAX_LOOP_ITERATION > _current_iteration_count:
            #execute code block
            statement_node = node.children[12]
            self.generic_visit(statement_node)
            #do the inc_dec
            var_name = node.children[9].children[0].value
            var_op = node.children[9].children[1].children[0].value

            # Look up the symbol
            symbol = self.current_scope.lookup(var_name)
            if not symbol:
                line_num = getattr(node, 'line_number', None)
                self.errors.append(SemanticError(
                    code="UNDEFINED_VARIABLE",
                    message=f"VARIABLE '{var_name}' is UNDEFINED!",
                    line=line_num
                ))
                return
            print(var_op)
            if var_op == '++':
                symbol.set_value((symbol.get_value() or 0) + 1)
            elif var_op == '--':
                symbol.set_value((symbol.get_value() or 0) - 1)

            eval_result = self._evaluate_condition(condition_expr)
            _current_iteration_count += 1 #for infinite loop checking

        if self.MAX_LOOP_ITERATION <= _current_iteration_count:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INFINITE_LOOP_RISK",
                message=f"The loop exceeded the set limit of iteration counts[{self.MAX_LOOP_ITERATION}]",
                line=line_num
            ))
            return

        """OLD, uses recursion"""
        # if not loop:
        #     if len(node.children) < 7:
        #         line_num = getattr(node, 'line_number', None)
        #         self.errors.append(SemanticError(
        #             code="INVALID_FOR_LOOP",
        #             message="Invalid for loop structure",
        #             line=line_num
        #         ))
        #         return
        #
        #     #need to do the assignment first!
        #     _dtype = node.children[2]
        #     _dname = node.children[3].value
        #     _dvalue = node.children[5].children[0]
        #     if _dtype.children:
        #         # Create symbol and add it to the current scope for the first variable
        #         symbol = Symbol(_dname, _dtype.children[0].value)
        #         print(f"Adding symbol {_dname} to scope {self.current_scope.debugName}")
        #         self.current_scope.add(_dname, symbol)
        #         if _dvalue.node_type == "id":
        #             _dvalue = self.lookup_symbol(_dvalue.value)
        #         else:
        #             _dvalue = self._extract_literal_value(_dvalue)
        #
        #         if _dvalue is not None:
        #             symbol.set_value(_dvalue)
        #     else:
        #         symbol = self.lookup_symbol(_dname)
        #         if _dvalue.node_type == "id":
        #             _dvalue = self.lookup_symbol(_dvalue.value)
        #         else:
        #             _dvalue = self._extract_literal_value(_dvalue)
        #         print(f"Replacing value of {_dname} to {_dvalue} from scope {self.current_scope.debugName}")
        #
        #         if _dvalue is not None:
        #             symbol.set_value(_dvalue)
        #
        # # Check that the condition expression evaluates to a boolean compatible type
        # # WHY ARE YOU   CHEKCING THE ID, INSTEAD OF A   CONDITION!??????? DO YOU EVEN KNOW THE SEQUENCE OF YOUR   SYMBOLSS!??? PARSE TREEE? AHJJJJJJJJASDJKHSAJKD
        #
        # condition_expr = node.children[7]
        # #condition_type = self.get_condition_type(condition_expr)
        # #print(condition_type + " " + "="*50)
        # eval_result = self._evaluate_condition(condition_expr)
        # print(f"For Condition Evaluation := " + str(eval_result))
        # # if not condition_type and condition_type not in ["pinch", "skim", "bool"]:
        # #     line_num = getattr(condition_expr, 'line_number', None)
        # #     self.errors.append(SemanticError(
        # #         code="INVALID_CONDITION",
        # #         message=f"Loop condition must evaluate to a boolean compatible type, got '{condition_type}'",
        # #         line=line_num
        # #     ))
        #
        # if eval_result:
        #     #execute code block
        #     statement_node = node.children[12]
        #     self.generic_visit(statement_node)
        #     #do the inc_dec
        #     var_name = node.children[9].children[0].value
        #     var_op = node.children[9].children[1].children[0].value
        #
        #     # Look up the symbol
        #     symbol = self.current_scope.lookup(var_name)
        #     if not symbol:
        #         line_num = getattr(node, 'line_number', None)
        #         self.errors.append(SemanticError(
        #             code="UNDEFINED_VARIABLE",
        #             message=f"VARIABLE '{var_name}' is UNDEFINED!",
        #             line=line_num
        #         ))
        #         return
        #     print(var_op)
        #     if var_op == '++':
        #         symbol.set_value((symbol.get_value() or 0) + 1)
        #     elif var_op == '--':
        #         symbol.set_value((symbol.get_value() or 0) - 1)
        #
        #     self._handle_for_loop(node, True)


    #-----------------------------------------------------------------
    # Return statement handling
    #-----------------------------------------------------------------
    def visit_return_statement(self, node):
        if not self.current_function:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INVALID_RETURN", 
                message="Return statement outside of function",
                line=line_num
            ))
            return
        
        # Check if return has an expression
        has_expr = len(node.children) > 1
        
        if self.current_function["return_type"] == "void" and has_expr:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INVALID_RETURN", 
                message=f"Function '{self.current_function['name']}' with void return type cannot return a value",
                line=line_num
            ))
        elif self.current_function["return_type"] != "void" and not has_expr:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INVALID_RETURN", 
                message=f"Function '{self.current_function['name']}' must return a value of type '{self.current_function['return_type']}'",
                line=line_num
            ))
        elif has_expr:
            expr_node = node.children[1]
            expr_type = self.get_expression_type(expr_node)
            if expr_type and not expr_type in self.type_compatibility.get(self.current_function["return_type"], []):
                line_num = getattr(node, 'line_number', None)
                # Convert base types to literal types for error message
                literal_type = expr_type + "literals" if expr_type in ["pinch", "skim", "pasta"] else expr_type
                target_literal_type = self.current_function["return_type"] + "literals" if self.current_function["return_type"] in ["pinch", "skim", "pasta"] else self.current_function["return_type"]
                self.errors.append(SemanticError(
                    code="TYPE_MISMATCH", 
                    message=f"Return type mismatch: cannot convert '{literal_type}' to '{target_literal_type}'",
                    line=line_num
                ))
        
        self.generic_visit(node)

    #-----------------------------------------------------------------
    # Identifier usage checking
    #-----------------------------------------------------------------
    def check_id_usage(self, node: ParseTreeNode):
        # For identifier usage in expressions, assume the leaf node value is the identifier name.
        var_name = node.value
        line_num = node.line_number
        # this shoul have a   error handling !!!
        # Skip checking for undeclared identifiers
        return

    #-----------------------------------------------------------------
    # Unused variable warnings
    #-----------------------------------------------------------------
    def _check_unused_local_variables(self):
        # Skip global scope
        #WHY DO YOU   NEED THIS?
        # for table in self.symbol_tables[1:]:
        #     unused = table.get_unused()
        #     for name in unused:
        #         if not name.startswith('__'):
        #             symbol = table.symbols.get(name)
        #             if symbol:
        #                 self.errors.append(SemanticError(
        #                     code="UNUSED_VARIABLE",
        #                     message=f"Unused local variable '{name}'",
        #                     identifier=name,
        #                     is_warning=True
        #                 ))

        pass

    def _process_arithmetic_exp_tail(self, tail_node, accumulated_value):
        if tail_node.value == "<arithmetic_exp_tail>" and hasattr(tail_node, 'children') and tail_node.children:
            if tail_node.children[0].value != "λ":
                operator_node = tail_node.children[0]  # <additive_operator>
                term_node = tail_node.children[1]  # <term>
                next_tail_node = tail_node.children[2]  # <arithmetic_exp_tail> (next chain)

                if operator_node.children:
                    actual_operator = operator_node.children[0].value
                    print(f"Additive operator: {actual_operator}")
                else:
                    actual_operator = operator_node.value
                    print(f"Direct additive operator: {actual_operator}")

                right_value = self._evaluate_expression(term_node)
                print(f"Next term value: {right_value}")

                result = self._apply_operator(actual_operator, accumulated_value, right_value)
                print(f"Result after applying additive operator: {result}")

                return self._process_arithmetic_exp_tail(next_tail_node, result)
        return accumulated_value

    def _process_term_tail(self, tail_node, accumulated_value):
        if tail_node.value == "<term_tail>" and hasattr(tail_node, 'children') and tail_node.children:
            if tail_node.children[0].value != "λ":
                operator_node = tail_node.children[0]  # <multiplicative_operator>
                factor_node = tail_node.children[1]  # <factor>
                next_tail_node = tail_node.children[2]  # <term_tail> (next chain)

                if operator_node.children:
                    actual_operator = operator_node.children[0].value
                    print(f"Multiplicative operator: {actual_operator}")
                else:
                    actual_operator = operator_node.value
                    print(f"Direct multiplicative operator: {actual_operator}")

                right_value = self._evaluate_expression(factor_node)
                print(f"Next factor value: {right_value}")

                result = self._apply_operator(actual_operator, accumulated_value, right_value)
                print(f"Result after applying multiplicative operator: {result}")

                return self._process_term_tail(next_tail_node, result)
        return accumulated_value

    def _evaluate_expression(self, node):
        if not node:
            return None
        print("\n" + "="*50)
        print("DEBUG: Starting expression evaluation")
        print("="*50)
        print(f"Evaluating node: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"Node type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
        if hasattr(node, 'children'):
            print(f"Children count: {len(node.children)}")
            for i, child in enumerate(node.children[:3]):  # Show first 3 children for brevity
                print(f"Child {i}: {child.value if hasattr(child, 'value') else 'No value'}")
        
        # Handle direct literals
        if not hasattr(node, 'children') or not node.children:
            if hasattr(node, 'node_type'):
                if node.node_type == "pinchliterals":
                    try:
                        value = int(node.value)
                        print(f"Direct pinch literal value: {value}")
                        return value
                    except ValueError:
                        print(f"Invalid pinch literal: {node.value}")
                        return None
                elif node.node_type == "skimliterals":
                    try:
                        value = float(node.value)
                        print(f"Direct skim literal value: {value}")
                        return value
                    except ValueError:
                        print(f"Invalid skim literal: {node.value}")
                        return None
                elif node.node_type == "pastaliterals":
                    value = node.value.strip('"')
                    print(f"Direct pasta literal value: {value}")
                    return value
                elif node.node_type == "id":
                    # Enhanced variable lookup that fixes scope issues
                    var_name = node.value
                    # Try all variable lookup strategies to ensure we find the variable
                    symbol = None
                    
                    # First, direct lookup in current scope
                    if hasattr(self, 'current_scope') and self.current_scope:
                        symbol = self.current_scope.lookup(var_name, True)
                    
                    # If not found, try global scope
                    if not symbol and hasattr(self, 'global_scope') and self.global_scope:
                        symbol = self.global_scope.lookup(var_name, True)
                    
                    # Finally, search all symbol tables
                    if not symbol and hasattr(self, 'symbol_tables'):
                        for table in self.symbol_tables:
                            if var_name in table.symbols:
                                symbol = table.symbols[var_name]
                                break
                    
                    if symbol:
                        value = symbol.get_value()
                        print(f"Found symbol {var_name} with value: {value}")
                        return value
                    else:
                        print(f"Symbol not found: {var_name}")
                        return None
            return None
        
        # Handle expression nodes
        if node.value == "<expression>":
            print("Processing <expression> node")
            if len(node.children) >= 2:
                operand_node = node.children[0]  # First child is <expression_operand>
                tail_node = node.children[1]     # Second child is <expression_tail>
                
                # Evaluate the first operand
                left_value = self._evaluate_expression(operand_node)
                print(f"Left operand value: {left_value}")
                
                # Process any operations in the expression tail
                if left_value is not None:
                    result = self._process_expression_tail(tail_node, left_value)
                    return result
                return left_value
        
        # Handle expression_operand nodes
        elif node.value == "<expression_operand>":
            print("Processing <expression_operand> node")
            if node.children:
                # Check if this is a parenthesized expression
                if len(node.children) >= 3 and node.children[0].value == "(":
                    print("Found parenthesized expression")
                    # The actual expression is the second child (index 1)
                    expr_node = node.children[1]
                    value = self._evaluate_expression(expr_node)
                    print(f"Parenthesized expression value: {value}")
                    return value
                else:
                    # Regular operand, evaluate normally
                    return self._evaluate_expression(node.children[0])
        
        # Handle value nodes
        elif node.value in ["<value>", "<value2>", "<value3>"]:
            print(f"Processing {node.value} node")
            if len(node.children) >= 1:
                # First child could be an ID or a literal
                first_child = node.children[0]
                
                # Special handling for parenthesized expressions
                if hasattr(first_child, 'value') and first_child.value == "(":
                    if len(node.children) >= 3:  # Should have "(", expr, ")"
                        expr_node = node.children[1]
                        value = self._evaluate_expression(expr_node)
                        print(f"Parenthesized value: {value}")
                        return value

                if hasattr(first_child, 'node_type') and first_child.node_type == "id":
                    # Look up the variable
                    if first_child.value != "len":
                        if not self.lookup_symbol(first_child.value):
                            line_num = getattr(node, 'line_number', None)
                            self.errors.append(SemanticError(
                                code="UNDEFINED_IDENTIFIER",
                                message=f"Identifier [{first_child.value}] does not exist!",
                                line=line_num,
                                identifier=first_child.value
                            ))
                            return None #testing
                        if self.lookup_symbol(first_child.value).value is None:
                            line_num = getattr(node, 'line_number', None)
                            self.errors.append(SemanticError(
                                code="NONE_VALUE",
                                message=f"Identifier [{first_child.value}] have a None value!",
                                line=line_num,
                                identifier=first_child.value
                            ))

                            return None  # testing

                    if node.children[1].children:
                        # function call

                        if node.children[1].children[0].value == '(':
                            if first_child.value == "len":
                                argument_node = node.children[1].children[1]

                                # add error handling here for the parameter and arguments
                                if not argument_node.children:
                                    self.errors.append(SemanticError(
                                        code="MISSING_ARGUMENTS",
                                        message=f"Doesn't meet the required number of arguments for [{first_child.value}]!",
                                        line=getattr(node, 'line_number', None)
                                    ))
                                    return None
                                if "," in str(argument_node):
                                    self.errors.append(SemanticError(
                                        code="TOO_MANY_ARGUMENTS",
                                        message=f"Too many arguments provided to function call [{first_child.value}]!",
                                        line=getattr(node, 'line_number', None)
                                    ))
                                    return None

                                return_val = len(self._evaluate_expression(argument_node))
                                return return_val
                            else:
                                symbol = self.lookup_symbol(first_child.value)
                                print(f"Found Function Call[symbol]={symbol}")
                                if symbol.attributes.get("return_type", "none") == 'void':
                                    self.errors.append(SemanticError(
                                        code="VOID_FUNCTION",
                                        message="Void functions does not return a value!",
                                        line=getattr(node, 'line_number', None)
                                    ))

                                argument_node = node.children[1].children[1]
                                # Create a new scope for the function body
                                old_scope = self.current_scope
                                self.current_scope = SymbolTable(debugName=f"function_{first_child.value}",
                                                                 parent=old_scope)
                                self.symbol_tables.append(self.current_scope)

                                # needs to process parameters
                                parameter_node = symbol.parameters
                                while parameter_node.children and argument_node.children:
                                    # process the   parameter
                                    if parameter_node.children[0].value == ',':
                                        data_type = parameter_node.children[1].children[0].value
                                        data_name = parameter_node.children[2].value
                                        parameter_node = parameter_node.children[3]
                                    else:
                                        data_type = parameter_node.children[0].children[0].value
                                        data_name = parameter_node.children[1].value
                                        parameter_node = parameter_node.children[2]
                                    # assign the   argument to the   parameter

                                    if argument_node.children[0].value == ',':
                                        data_val = self._evaluate_expression(argument_node.children[1])
                                        argument_node = argument_node.children[2]
                                    else:
                                        data_val = self._evaluate_expression(argument_node.children[0])
                                        argument_node = argument_node.children[1]
                                    new_symbol = Symbol(data_name, data_type)
                                    new_symbol.set_value(data_val)
                                    self.current_scope.add(data_name, new_symbol)

                                # add error handling here for the parameter and arguments
                                if parameter_node.children:
                                    self.errors.append(SemanticError(
                                        code="MISSING_ARGUMENTS",
                                        message="Doesn't meet the required number of arguments!",
                                        line=getattr(node, 'line_number', None)
                                    ))
                                if argument_node.children:
                                    self.errors.append(SemanticError(
                                        code="TOO_MANY_ARGUMENTS",
                                        message="Too many arguments provided to function call!",
                                        line=getattr(node, 'line_number', None)
                                    ))

                                return_node = symbol.value[2]
                                #did it this way so that i don't need to add the spit on the visit_statement,   that
                                self.generic_visit(symbol.value[0])
                                self.generic_visit(symbol.value[1])


                                return_val = self._evaluate_expression(return_node.children[1])

                                self.current_scope = old_scope
                                self.symbol_tables.pop()

                                return return_val
                        #this is the   array call
                        elif node.children[1].children[0].value == '[':
                            if first_child.value == "len":
                                line_num = getattr(node, 'line_number', None)
                                self.errors.append(SemanticError(
                                    code="NOT_A_RECIPE",
                                    message=f"Identifier [{first_child.value}] is a function!",
                                    line=line_num,
                                    identifier=first_child.value
                                ))
                                return
                            print("a"*100)
                            #it's a   array <3   this shi
                            index_value = int(self._evaluate_expression(node.children[1].children[1]))
                            symbol = self.lookup_symbol(first_child.value)
                            listed_value = list(symbol.get_value())
                            if index_value >= len(listed_value):
                                line_num = getattr(node, 'line_number', None)
                                var_name = first_child.value
                                self.errors.append(SemanticError(
                                    code="ARRAY_OUT_OF_BOUNDS",
                                    message=f"Accessed an index outside the allowed range. index[{index_value}]:range[{len(listed_value) - 1}]",
                                    line=line_num,
                                    identifier=var_name
                                ))
                                return None
                            final_val = listed_value[index_value]
                            if symbol.attributes.get("element_type", "None") == 'pinch':
                                final_val = int(final_val)
                            elif symbol.attributes.get("element_type", "None") == 'skim':
                                final_val = float(final_val)
                            elif symbol.attributes.get("element_type", "None") == 'pasta':
                                final_val = str(final_val).replace('"', "")
                            else:
                                if symbol.type == "pasta":
                                    final_val = str(final_val).replace('"', "")
                                else:
                                    line_num = getattr(node, 'line_number', None)
                                    var_name = first_child.value
                                    self.errors.append(SemanticError(
                                        code="UNKNOWN_RECIPE_TYPE",
                                        message=f"Undefined element_type[{symbol.attributes.get("element_type", "None")}] {symbol}",
                                        line=line_num,
                                        identifier=var_name
                                    ))
                                    return None
                            return final_val

                    else:
                        var_name = first_child.value
                        symbol = self.lookup_symbol(var_name)
                        if symbol:
                            print(f"Found variable {var_name} with value: {symbol.get_value()}")
                            return symbol.get_value()
                        else:
                            print(f"Variable not found: {var_name}")
                            return None

                else:
                    # For other types, evaluate the child
                    return self._evaluate_expression(first_child)
        
        # Handle value_id_tail nodes
        elif node.value == "<value_id_tail>":
            print("Processing <value_id_tail> node")
            # This node is usually empty for basic expressions, so just return None
            return None
        
        # Handle literals and literals nodes
        elif node.value == "<literals>" or (hasattr(node, 'node_type') and node.node_type in ["pinchliterals", "skimliterals", "pastaliterals"]):
            print(f"Processing literals node: {node.value}")
            if hasattr(node, 'node_type'):
                if node.node_type == "pinchliterals":
                    try:
                        value = int(node.value.replace("~", "-"))
                        print(f"Parsed literal integer: {value}")
                        return value
                    except (ValueError, TypeError):
                        pass
                elif node.node_type == "skimliterals":
                    try:
                        value = float(node.value.replace("~", "-"))
                        print(f"Parsed literal float: {value}")
                        return value
                    except (ValueError, TypeError):
                        pass
                elif node.node_type == "pastaliterals":
                    value = node.value.strip('"')
                    print(f"Parsed literal string: {value}")
                    return value
            
            # For <literals> nodes, evaluate the first child
            if node.value == "<literals>" and node.children:
                return self._evaluate_expression(node.children[0])
        
        # Handle <arithmetic_exp> nodes
        elif node.value == "<arithmetic_exp>":
            print("Processing <arithmetic_exp> node")
            if len(node.children) >= 2:
                term_node = node.children[0] # this should be the term
                exp_tail_node = node.children[1]

                left_value = self._evaluate_expression(term_node)
                print(f"Initial term value: {left_value}")

                return self._process_arithmetic_exp_tail(exp_tail_node, left_value)
            else:
                print("Unexpected structure in <arithmetic_exp>")
                return None
        elif node.value == "<term>":
            print("Processing <term> node")
            if len(node.children) >= 2:
                factor_node = node.children[0]  # <factor>
                term_tail_node = node.children[1]  # <term_tail>

                left_value = self._evaluate_expression(factor_node)
                print(f"Initial factor value: {left_value}")

                return self._process_term_tail(term_tail_node, left_value)
            else:
                print("Unexpected structure in <term>")
                return None
        elif node.value == "<factor>":
            print("Processing <factor> node")
            if not node.children:
                print("Empty <factor> node")
                return None

            first_child = node.children[0]

            if first_child.value == "(":
                # It's a parenthesis group
                expression_node = node.children[1]  # <arithmetic_exp> inside the ( )
                closing_parenthesis = node.children[2]  # Should be ')', but you usually don't need it

                print("Found parenthesis: evaluating inner expression")
                result = self._evaluate_expression(expression_node)
                print(f"Result of inner parenthesis expression: {result}")
                return result
            else:
                # It's just a simple <value2> (normal value)
                return self._evaluate_expression(first_child)

        elif node.children and len(node.children) > 0:
            print(f"Processing unrecognized node type: {node.value}, trying first child")
            return self._evaluate_expression(node.children[0])
        
        print(f"Unable to evaluate expression node: {node.value}")
        return None

    def _process_optional_equality(self, node, left_value):
        if not node.children or node.children[0].value == "λ":
            return left_value  # No comparison, just return left side

        operator = node.children[0].value  # '==' or '!='
        right_node = node.children[1]
        right_value = self._evaluate_condition(right_node)

        if operator == "==":
            return left_value == right_value
        elif operator == "!=":
            return left_value != right_value
        else:
            raise ValueError(f"Unknown operator in optional equality: {operator}")

    def _process_logical_or_tail(self, tail_node, left_value):
        if not tail_node or not tail_node.children or tail_node.children[0].value == "λ":
            return left_value

        if tail_node.children[0].value == "??":
            right_node = tail_node.children[1]
            right_value = self._evaluate_condition(right_node)
            combined = left_value or right_value
            return self._process_logical_or_tail(tail_node.children[2], combined)
        return left_value

    def _process_logical_and_tail(self, tail_node, left_value):
        if not tail_node or not tail_node.children or tail_node.children[0].value == "λ":
            return left_value

        if tail_node.children[0].value == "&&":
            right_node = tail_node.children[1]
            right_value = self._evaluate_condition(right_node)
            combined = left_value and right_value
            return self._process_logical_or_tail(tail_node.children[2], combined)
        return left_value

    def _process_equality_tail(self, node, left_value):
        if not node.children or node.children[0].value == "λ":
            return left_value
        operator = node.children[0].value  # '==' or '!='
        right = self._evaluate_condition(node.children[1])
        result = (left_value == right) if operator == "==" else (left_value != right)
        if len(node.children) > 2:
            return self._process_equality_tail(node.children[2], result)
        return result

    def _process_relational_tail(self, tail_node, left_value):
        if not tail_node or not tail_node.children or tail_node.children[0].value == "λ":
            return left_value

        right_node = tail_node.children[1]
        right_value = self._evaluate_condition(right_node)

        try:
            if tail_node.children[0].value == "<":
                combined = left_value < right_value
                return self._process_logical_or_tail(tail_node.children[2], combined)
            elif tail_node.children[0].value == "<=":
                combined = left_value <= right_value
                return self._process_logical_or_tail(tail_node.children[2], combined)
            if tail_node.children[0].value == ">":
                combined = left_value > right_value
                return self._process_logical_or_tail(tail_node.children[2], combined)
            elif tail_node.children[0].value == ">=":
                combined = left_value >= right_value
                return self._process_logical_or_tail(tail_node.children[2], combined)
            return left_value
        except TypeError:
            line_num = getattr(tail_node, 'line_number', None)
            type_names = {
                'int': 'pinch',
                'float': 'skin',
                'str': 'pasta'
            }
            self.errors.append(SemanticError(
                code="CONDITIONAL_MISMATCH",
                message=(
                    f"Cannot use operator[{tail_node.children[0].value}] to "
                    f"[{type_names.get(type(left_value).__name__, type(left_value).__name__)}] and "
                    f"[{type_names.get(type(right_value).__name__, type(right_value).__name__)}]"
                ),
                line=line_num,
            ))
            return None

    def _evaluate_condition(self, node):
        if not node:
            return None

        print("\n" + "=" * 50)
        print("DEBUG: Starting condition evaluation")
        print("=" * 50)
        print(f"Evaluating node: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"Node type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
        if hasattr(node, 'children'):
            print(f"Children count: {len(node.children)}")
            for i, child in enumerate(node.children[:3]):  # Show first 3 children for brevity
                print(f"Child {i}: {child.value if hasattr(child, 'value') else 'No value'}")

        # Handle <condition> node
        if node.value == "<condition>":
            print("Processing <condition> node")
            if not node.children:
                return None
            first_child = node.children[0]
            value = self._evaluate_condition(first_child)
            return value

        # Handle <condition_operand> node
        elif node.value == "<condition_operand>":
            print("Processing <condition_operand> node")
            if node.children:
                # Handle parenthesized, ! (negate)
                if len(node.children) >= 3 and node.children[0].value == "(":
                    expr_node = node.children[1]
                    return self._evaluate_condition(expr_node)
                elif len(node.children) >= 4 and node.children[0].value in ["!"]:
                    negate_type = node.children[0].value
                    expr_node = node.children[2]
                    result = self._evaluate_condition(expr_node)
                    if negate_type == "!":
                        return not result
                    
                else:
                    return self._evaluate_condition(node.children[0])

        # Handle <logical_or> node
        elif node.value == "<logical_or>":
            print("Processing <logical_or> node")
            if len(node.children) >= 2:
                left_node = node.children[0]
                tail_node = node.children[1]

                left_value = self._evaluate_condition(left_node)
                return self._process_logical_or_tail(tail_node, left_value)
            else:
                return self._evaluate_condition(node.children[0])

        # Handle <logical_and> node
        elif node.value == "<logical_and>":
            print("Processing <logical_and> node")
            if len(node.children) >= 2:
                left_node = node.children[0]
                tail_node = node.children[1]

                left_value = self._evaluate_condition(left_node)
                return self._process_logical_and_tail(tail_node, left_value)
            else:
                return self._evaluate_condition(node.children[0])

        # Handle <equality> node
        elif node.value == "<equality>":
            print("Processing <equality> node")
            left = self._evaluate_condition(node.children[0])  # <relational>
            optional = node.children[1]  # <optional_equality>
            return self._process_optional_equality(optional, left)

        # Handle <relational> node
        elif node.value == "<relational>":
            print("Processing <relational> node")
            if len(node.children) >= 2:
                left_node = node.children[0]
                tail_node = node.children[1]

                if left_node.value == "<primary>":
                    print("Processing <primary> node")
                    if not node.children:
                        return None

                    first_child = left_node.children[0]

                    if first_child.value == "!":
                        # Handle "!(<condition>)"
                        print("Found ! (negation) node")
                        inner_condition = left_node.children[2]  # because structure: ! ( <condition> )
                        value = not self._evaluate_condition(inner_condition)
                    elif first_child.value == "yum":
                        print(f"Found: {node.value} => processing")
                        value = True
                    elif first_child.value == "bleh":
                        print(f"Found: {node.value} => processing")
                        value = False
                    else:
                        # Normal <logical_or> (no negation)
                        value = self._evaluate_expression(first_child)

                else:
                    line_num = getattr(node, 'line_number', None)
                    self.errors.append(SemanticError("NO_PRIMARY_NODE", "Primary node missing!", line_num))
                    return None
                left_value = value
                return self._process_relational_tail(tail_node, left_value)
            else:
                return self._evaluate_expression(node.children[0])

        elif node.value == "<primary>":
            print("Processing <primary> node")
            if not node.children:
                return None

            first_child = node.children[0]

            if first_child.value == "!":
                # Handle "!(<condition>)"
                print("Found ! (negation) node")
                inner_condition = node.children[2]  # because structure: ! ( <condition> )
                return self._evaluate_condition(inner_condition)
            elif first_child.value == "yum":
                print(f"Found: {node.value} => processing")
                return True
            elif first_child.value == "bleh":
                print(f"Found: {node.value} => processing")
                return False
            else:
                # Normal <logical_or> (no negation)
                expression_val = self._evaluate_expression(first_child)
                # if not expression_val:
                #     self.errors.append(SemanticError("INVALID_OPERANDS",
                #                                      f"Cannot use '{operator}' to data_types({type(left)},{type(right)})"))
                #     print("Operands must be int, float, or string-string")
                #     return None
                return expression_val

        # Handle value nodes
        elif node.value == "<arithmetic_exp>":
            print("Processing <arithmetic_exp> node")
            eval_result = self._evaluate_expression(node)
            return eval_result

        # Handle value_id_tail nodes
        elif node.value == "<value_id_tail>":
            print("Processing <value_id_tail> node")
            # This node is usually empty for basic expressions, so just return None
            return None

        # Handle literals and literals nodes
        elif node.value == "<literals>" or (hasattr(node, 'node_type') and node.node_type in ["pinchliterals", "skimliterals","pastaliterals"]):
            print(f"Processing literals node: {node.value}")
            if hasattr(node, 'node_type'):
                if node.node_type == "pinchliterals":
                    try:
                        value = int(node.value.replace("~", "-"))
                        print(f"Parsed literal integer: {value}")
                        return value
                    except (ValueError, TypeError):
                        pass
                elif node.node_type == "skimliterals":
                    try:
                        value = float(node.value.replace("~", "-"))
                        print(f"Parsed literal float: {value}")
                        return value
                    except (ValueError, TypeError):
                        pass
                elif node.node_type == "pastaliterals":
                    value = node.value.strip('"')
                    print(f"Parsed literal string: {value}")
                    return value

            # For <literals> nodes, evaluate the first child
            if node.value == "<literals>" and node.children:
                return self._evaluate_condition(node.children[0])

        print(f"Unable to evaluate condition node: {node.value}")
        return None

    def _process_relational(self, tail_node, left_value):
        if not tail_node or not hasattr(tail_node, 'value') or tail_node.value != "<relational>":
            return left_value

        if not hasattr(tail_node, 'children') or not tail_node.children or tail_node.children[0].value == "λ":
            # Empty tail, no operation to perform
            return left_value

        # Get the operator - first child of expression_tail
        operator_node = tail_node.children[0].children[0]
        right_node = tail_node.children[1]
        if right_node.node_type == '<condition>':
            right_value = self._evaluate_condition(right_node)
            result = self._apply_condition_operator(operator_node.value, left_value, right_value)
            print(f"Condition relation result after operation {left_value} {operator_node.value} {right_value} = {result}")
            return result

    def _process_condition_tail(self, tail_node, left_value):
        """Process a condition tail with possible chained operations."""
        if not tail_node or not hasattr(tail_node, 'value') or tail_node.value != "<condition_tail>":
            return left_value

        if not hasattr(tail_node, 'children') or not tail_node.children or tail_node.children[0].value == "λ":
            # Empty tail, no operation to perform
            return left_value

        # Get the operator - first child of expression_tail
        operator_node = tail_node.children[0]

        # Extract the actual operator from <expression_operator> if needed
        actual_operator = None
        if operator_node.value == "<condition_operator>" and operator_node.children:
            # The real operator is the first child of <expression_operator>
            actual_operator = operator_node.children[0].value
            print(f"Extracted operator from <condition_operator>: {actual_operator}")
        else:
            actual_operator = operator_node.value
            print(f"Direct operator: {actual_operator}")

        # Get the right operand - second child of expression_tail
        if len(tail_node.children) < 2:
            return left_value  # No right operand

        right_operand_node = tail_node.children[1]
        print(f"Right operand node: {right_operand_node.value}")

        # Evaluate the right operand
        right_value = self._evaluate_condition(right_operand_node)
        print(f"Right operand value: {right_value}")

        # Apply the operator using the actual operator value
        if left_value is not None and right_value is not None and actual_operator:
            result = self._apply_condition_operator(actual_operator, left_value, right_value)
            print(f"Condition result after operation {left_value} {actual_operator} {right_value} = {result}")

            # Check if there are more operations in the tail
            if len(tail_node.children) > 2:
                next_tail = tail_node.children[2]
                if next_tail.value == "<relational>" and hasattr(next_tail, 'children') and next_tail.children and \
                        next_tail.children[0].value != "λ":
                    # Recursively process the next operation with our current result as the left value
                    print(f"Continuing to next operation in chain with result {result}")
                    return self._process_relational(next_tail, result)

            return result

        # If either value is None or the operator is invalid, return the left value
        print(f"Cannot evaluate expression, left: {left_value}, right: {right_value}, op: {actual_operator}")
        return left_value

    def _process_expression_tail(self, tail_node, left_value):
        """Process an expression tail with possible chained operations."""
        if not tail_node or not hasattr(tail_node, 'value') or tail_node.value != "<expression_tail>":
            return left_value
        
        if not hasattr(tail_node, 'children') or not tail_node.children or tail_node.children[0].value == "λ":
            # Empty tail, no operation to perform
            return left_value
        
        # Get the operator - first child of expression_tail
        operator_node = tail_node.children[0]
        
        # Extract the actual operator from <expression_operator> if needed
        actual_operator = None
        if operator_node.value == "<expression_operator>" and operator_node.children:
            # The real operator is the first child of <expression_operator>
            actual_operator = operator_node.children[0].value
            print(f"Extracted operator from <expression_operator>: {actual_operator}")
        else:
            actual_operator = operator_node.value
            print(f"Direct operator: {actual_operator}")
        
        # Get the right operand - second child of expression_tail
        if len(tail_node.children) < 2:
            return left_value  # No right operand
        
        right_operand_node = tail_node.children[1]
        print(f"Right operand node: {right_operand_node.value}")
        
        # Evaluate the right operand
        right_value = self._evaluate_expression(right_operand_node)
        print(f"Right operand value: {right_value}")
        
        # Apply the operator using the actual operator value
        if left_value is not None and right_value is not None and actual_operator:
            result = self._apply_operator(actual_operator, left_value, right_value)
            print(f"Expression result after operation {left_value} {actual_operator} {right_value} = {result}")
            
            # Check if there are more operations in the tail (e.g., for chained operations like a + b + c)
            if len(tail_node.children) > 2:
                next_tail = tail_node.children[2]
                if next_tail.value == "<expression_tail>" and hasattr(next_tail, 'children') and next_tail.children and next_tail.children[0].value != "λ":
                    # Recursively process the next operation with our current result as the left value
                    print(f"Continuing to next operation in chain with result {result}")
                    return self._process_expression_tail(next_tail, result)
            
            return result
        
        # If either value is None or the operator is invalid, return the left value
        print(f"Cannot evaluate expression, left: {left_value}, right: {right_value}, op: {actual_operator}")
        return left_value
    
    def _process_arithmetic_tail(self, tail_node, left_value):
        """Similar to _process_expression_tail but for arithmetic tails."""
        if not tail_node or not hasattr(tail_node, 'children') or not tail_node.children:
            return left_value
            
        # Extract the actual operator
        operator_node = tail_node.children[0]
        actual_operator = None
        
        if operator_node.value == "<arithmetic_operator>" and operator_node.children:
            actual_operator = operator_node.children[0].value
            print(f"Extracted arithmetic operator: {actual_operator}")
        else:
            actual_operator = operator_node.value
            print(f"Direct arithmetic operator: {actual_operator}")
        
        # Get the right operand
        if len(tail_node.children) < 2:
            return left_value
            
        right_node = tail_node.children[1]
        right_value = self._evaluate_expression(right_node)
        print(f"Arithmetic right value: {right_value}")
        
        # Apply the operator
        if left_value is not None and right_value is not None and actual_operator:
            result = self._apply_operator(actual_operator, left_value, right_value)
            print(f"Arithmetic result: {result}")
            
            # Check for more operations
            if len(tail_node.children) > 2:
                next_tail = tail_node.children[2]
                if next_tail.value == "<arithmetic_tail>" and next_tail.children and next_tail.children[0].value != "λ":
                    return self._process_arithmetic_tail(next_tail, result)
            
            return result
        
        return left_value

    def _evaluate_operand(self, node):
        if not node:
            return None
            
        print(f"\nEvaluating operand: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"Operand type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
        
        # Handle direct node types
        if hasattr(node, 'node_type'):
            if node.node_type == "id":
                # Use enhanced lookup
                symbol = self.lookup_symbol(node.value)
                if symbol:
                    print(f"Found symbol value: {symbol.get_value()}")
                    return symbol.get_value()
                else:
                    print(f"Symbol not found: {node.value}")
                    return None
            elif node.node_type == "pinchliterals":
                try:
                    value = int(node.value)
                    print(f"Pinch literal value: {value}")
                    return value
                except ValueError:
                    print(f"Invalid pinch literal: {node.value}")
                    return None
            elif node.node_type == "skimliterals":
                try:
                    value = float(node.value)
                    print(f"Skim literal value: {value}")
                    return value
                except ValueError:
                    print(f"Invalid skim literal: {node.value}")
                    return None
            elif node.node_type == "pastaliterals":
                value = node.value.strip('"')
                print(f"Pasta literal value: {value}")
                return value
        
        # Handle different node values
        return self._evaluate_expression(node)

    def _apply_operator(self, operator, left, right):
        """Apply binary operator to left and right operands"""
        print(f"Applying operator: {left} {operator} {right}")

        if (not isinstance(left, (int, float)) or not isinstance(right, (int, float))) and not operator == '+':
            self.errors.append(SemanticError("INVALID_OPERANDS", f"Cannot use '{operator}' to data_types({type(left)},{type(right)})"))
            print("Operands must be int, float, or string-string")
            return None

        result = None

        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        elif operator == "/":
            if right == 0:
                print("Division by zero error")
                return None
            if isinstance(left, int) and isinstance(right, int):
                result = left // right  # Integer division
            else:
                result = left / right  # Float division
        elif operator == "%":
            if right == 0:
                print("Modulo by zero error")
                return None
            result = left % right

        print(f"Operation result: {result}")
        return result

    def _apply_condition_operator(self, operator, left, right):
        print(f"Applying condition operator: {left} {operator} {right}")

        if operator == "==":
            result = left == right
            print(f"Equality result: {result}")
            return True if result else False

        elif operator == "!=":
            result = left != right
            print(f"Inequality result: {result}")
            return True if result else False

        elif operator == "<":
            result = left < right
            print(f"Less than result: {result}")
            return True if result else False
        elif operator == ">":
            result = left > right
            print(f"Greater than result: {result}")
            return True if result else False
        elif operator == "<=":
            result = left <= right
            print(f"Less than or equal result: {result}")
            return True if result else False
        elif operator == ">=":
            result = left >= right
            print(f"Greater than or equal result: {result}")
            return True if result else False

        elif operator == "&&":
            result = left and right
            print(f"And result: {result}")
            return True if result else False

        elif operator == "??":
            result = left or right
            print(f"Or result: {result}")
            return True if result else False

        print(f"Unknown operator: {operator}")
        return None

    def _print_scope_symbols(self):
        """Helper method to print all symbols in current scope"""
        print("\nCurrent scope symbols:")
        for name, symbol in self.current_scope.symbols.items():
            print(f"  {name}: {symbol.value} (type: {symbol.type})")
    
    def _print_node_structure(self, node, level=0):
        """Helper method to print the structure of a node"""
        indent = "  " * level
        print(f"{indent}Node: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"{indent}Type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
        if hasattr(node, 'children'):
            print(f"{indent}Children:")
            for child in node.children:
                self._print_node_structure(child, level + 1)