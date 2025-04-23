from SyntaxAnalyzer import ParseTreeNode

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
    def __init__(self, name, symbol_type, attributes=None):
        self.name = name
        self.type = symbol_type  # e.g., "pinch", "skim", "pasta"
        self.attributes = attributes or {}  # For arrays: e.g., {'dimensions': 10, 'element_type': 'pinch'}
        self.is_used = False  # Track if the symbol is used
        self.value = None  # Store the actual value of the symbol
        print(f"Created symbol: {self.name} of type {self.type}")

    def __repr__(self):
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
        self._original_visit_return_statement(node)
    def __init__(self):
        self.global_scope = SymbolTable(debugName="global")
        self.current_scope = self.global_scope
        self.errors = []
        self.symbol_tables = [self.global_scope]
        self.current_function = None
        self.output_buffer = []  # Buffer to store output from serve statements
        # Define type compatibility rules
        self.type_compatibility = {
            "pinch": ["pinch"],           # Integers
            "skim": ["skim", "pinch"],    # Floats can accept integers
            "pasta": ["pasta"],           # Strings
            "recipe": ["recipe"],         # Arrays
            "bool": ["bool", "pinch"]     # Booleans can accept integers (0/1)
        }

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
            if node.value == "<looping_statement>":
                print(method_name + " ="*50)
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
                self.visit_make_statement(node, parent)
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
        
        # Debug - log if we couldn't determine the type
        print(f"Failed to determine type for expression: {expr_node.value if hasattr(expr_node, 'value') else 'unknown'}")
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
            
            self.generic_visit(node)
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
                                    value = int(literal_child.value)
                                    print(f"Extracted literal pinch value: {value}")
                                except ValueError:
                                    print(f"Invalid pinch literal: {literal_child.value}")
                            elif literal_child.node_type == "skimliterals":
                                try:
                                    value = float(literal_child.value)
                                    print(f"Extracted literal skim value: {value}")
                                except ValueError:
                                    print(f"Invalid skim literal: {literal_child.value}")
                            elif literal_child.node_type == "pastaliterals":
                                value = literal_child.value.strip('"')
                                print(f"Extracted literal pasta value: {value}")
                
                if value is not None:
                    symbol.set_value(value)
                    print(f"Initialized {var_name} with value: {value}")
                else:
                    # If direct extraction failed, try the evaluator
                    value = self._evaluate_expression(literals_node)
                    if value is not None:
                        symbol.set_value(value)
                        print(f"Initialized {var_name} with evaluated value: {value}")
        
        self.generic_visit(node)

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
            
            # Check initialization
            if len(node.children) > 6:
                elements_node = node.children[6]  # This is the <elements> node
                if hasattr(elements_node, 'children'):
                    for child in elements_node.children:
                        if hasattr(child, 'value') and child.value == '<literals>':
                            # Found the literals node, check its children
                            for value_node in child.children:
                                value_type = self.get_expression_type(value_node)
                                if value_type and value_type != var_type:
                                    # Convert base types to literal types for error message
                                    literal_type = value_type + "literals" if value_type in ["pinch", "skim", "pasta"] else value_type
                                    target_literal_type = var_type + "literals" if var_type in ["pinch", "skim", "pasta"] else var_type
                                    self.errors.append(SemanticError(
                                        code="TYPE_MISMATCH",
                                        message=f"Type mismatch in array initialization of '{var_name}': cannot assign '{literal_type}' to '{target_literal_type}'",
                                        line=line_num,
                                        identifier=var_name
                                    ))
            
            # Add to symbol table
            self.current_scope.add(var_name, Symbol(var_name, "recipe", attributes))
            
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
            
        self.generic_visit(node)
    
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
                    return int(node.value)
                except ValueError:
                    return None
            elif node.node_type == "skimliterals":
                try:
                    return float(node.value)
                except ValueError:
                    return None
            elif node.node_type == "pastaliterals":
                return node.value.strip('"')
        
        # Node with children
        if hasattr(node, 'value') and hasattr(node, 'children') and node.children:
            # Handle literals node
            if node.value == "<literals>" and len(node.children) > 0:
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
            else:
                # Hungry function (void return)
                return_type = "void"
                func_name = node.children[1].value
            
            print(f"Found function: {func_name} with return type {return_type}")
            
            # Register the function in the global scope
            try:
                self.global_scope.add(func_name, Symbol(func_name, "function", {"return_type": return_type}))
                print(f"Registered function {func_name} in global scope")
            except SemanticError as e:
                self.errors.append(e)
                return
            
            # Create a new scope for the function body
            old_scope = self.current_scope
            self.current_scope = SymbolTable(debugName=f"function_{func_name}", parent=old_scope)
            self.symbol_tables.append(self.current_scope)
            
            # Process function parameters first
            self._process_function_signature(node)
            
            # Then process the function body
            self.generic_visit(node)
            
            # Restore the previous scope
            self.current_scope = old_scope

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
                        # Unwrap the real operator string
                        raw_op = None
                        operator_node = second_child.children[0]
                        
                        # If it's an <assignment_operator> wrapper, grab its child token
                        if operator_node.value == "<assignment_operator>" and operator_node.children:
                            raw_op = operator_node.children[0].value
                            print(f"Found wrapped operator: {raw_op}")
                        # Otherwise maybe it was exposed directly
                        elif operator_node.value in ["=", "+=", "-=", "*=", "/=", "%="]:
                            raw_op = operator_node.value
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
                                print(f"Creating new symbol for {var_name}")
                                symbol = Symbol(var_name, "pinch")
                                self.current_scope.add(var_name, symbol)
                            
                            print(f"\nFound symbol: {symbol}")
                            print(f"Current symbol value: {symbol.get_value()}")
                            
                            # Evaluate the expression
                            print("\nEvaluating expression...")
                            print(f"Expression node structure before evaluation:")
                            self._print_node_structure(expr_node)
                            
                            value = self._evaluate_expression(expr_node)
                            print(f"Expression evaluation result: {value}")
                            
                            if value is not None:
                                # Handle different assignment operators
                                if raw_op == "=":
                                    symbol.set_value(value)
                                elif raw_op == "+=":
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
                                self._print_node_structure(expr_node)
                                print("\nCurrent scope symbols:")
                                self._print_scope_symbols()
        
        # Continue with generic visit to process other types of statements
        self.generic_visit(node)

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
            #are you fucking retarded????? why would you fucking include the ID checking here ???? it doesn't have childrennnnn????????????
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
                print(f"This is the fucking ID shi, they said to enhance this shi, it doesn't even work!")
                symbol = self.lookup_symbol(initial_node.value)
                if symbol:
                    print(f"Found symbol: {symbol}")
                    result = str(symbol.get_value() if hasattr(symbol, 'get_value') else "")
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
                        elif next_value.node_type == "id":
                            symbol = self.lookup_symbol(next_value.value)
                            if symbol:
                                print(f"Found symbol for concatenation: {symbol}")
                                result += str(symbol.get_value() if hasattr(symbol, 'get_value') else "")
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

        # children 2 'cause that shi is the second, second fucking dumbahh
        arg_node = statement_node.children[2]
        print(f"\nArgument node: {arg_node.value if hasattr(arg_node, 'value') else 'No value'}")
        print(f"Argument node type: {arg_node.node_type if hasattr(arg_node, 'node_type') else 'No type'}")

        if arg_node.node_type == 'id':
            #ask for input, for now in the fucking terminal, because I don't know how to pass a value from BE->FE->BE
            val = input("ask for input: ")

            symbol = self.lookup_symbol(arg_node.value)
            symbol.value = val
            print(symbol)
            self.output_buffer.append("input: " + str(val) + "")


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
        print(first_child.node_type + " temp"*50)

        if hasattr(first_child, 'node_type') and first_child.node_type == "for":
            self._handle_for_loop(node)
        
        # Continue with the generic visit to process child nodes
        self.generic_visit(node)

    def _handle_for_loop(self, node):
        # Expected structure: for ( <assignment> ; <expression> ; <assignment> ) <statement>
        if len(node.children) < 7:
            line_num = getattr(node, 'line_number', None)
            self.errors.append(SemanticError(
                code="INVALID_FOR_LOOP", 
                message="Invalid for loop structure",
                line=line_num
            ))
            return
        
        # Check that the condition expression evaluates to a boolean compatible type
        condition_expr = node.children[3]
        condition_type = self.get_expression_type(condition_expr)
        
        if condition_type and condition_type not in ["pinch", "skim", "bool"]:
            line_num = getattr(condition_expr, 'line_number', None)
            self.errors.append(SemanticError(
                code="INVALID_CONDITION", 
                message=f"Loop condition must evaluate to a boolean compatible type, got '{condition_type}'",
                line=line_num
            ))

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
        
        # Skip checking for undeclared identifiers
        return

    #-----------------------------------------------------------------
    # Unused variable warnings
    #-----------------------------------------------------------------
    def _check_unused_local_variables(self):
        # Skip global scope
        for table in self.symbol_tables[1:]:
            unused = table.get_unused()
            for name in unused:
                if not name.startswith('__'):
                    symbol = table.symbols.get(name)
                    if symbol:
                        self.errors.append(SemanticError(
                            code="UNUSED_VARIABLE",
                            message=f"Unused local variable '{name}'",
                            identifier=name,
                            is_warning=True
                        ))

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
        elif node.value == "<value>":
            print("Processing <value> node")
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
                        value = int(node.value)
                        print(f"Parsed literal integer: {value}")
                        return value
                    except (ValueError, TypeError):
                        pass
                elif node.node_type == "skimliterals":
                    try:
                        value = float(node.value)
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
                left_node = node.children[0]
                tail_node = node.children[1]
                
                left_value = self._evaluate_expression(left_node)
                print(f"Arithmetic left value: {left_value}")
                
                if tail_node.value == "<arithmetic_tail>" and hasattr(tail_node, 'children') and tail_node.children:
                    if tail_node.children[0].value != "λ":  # Make sure it's not empty
                        # Extract the actual operator, similar to above
                        operator_node = tail_node.children[0]
                        actual_operator = None
                        
                        if operator_node.value == "<arithmetic_operator>" and operator_node.children:
                            actual_operator = operator_node.children[0].value
                            print(f"Extracted arithmetic operator: {actual_operator}")
                        else:
                            actual_operator = operator_node.value
                            print(f"Direct arithmetic operator: {actual_operator}")
                        
                        right_node = tail_node.children[1]
                        right_value = self._evaluate_expression(right_node)
                        print(f"Arithmetic right value: {right_value}")
                        
                        if left_value is not None and right_value is not None and actual_operator:
                            result = self._apply_operator(actual_operator, left_value, right_value)
                            print(f"Arithmetic result: {result}")
                            
                            # Check for additional operations in the chain
                            if len(tail_node.children) > 2:
                                next_tail = tail_node.children[2]
                                if next_tail.value == "<arithmetic_tail>" and next_tail.children and next_tail.children[0].value != "λ":
                                    # Recursively process the next part using our current result as the left value
                                    return self._process_arithmetic_tail(next_tail, result)
                            
                            return result
                
                # If no operator or evaluation failed, return left value
                return left_value
        
        # Value nodes with IDs
        elif node.value in ["<value2>", "<value3>"]:
            print(f"Processing {node.value} node")
            if node.children:
                return self._evaluate_expression(node.children[0])
        
        # Catch-all for other node types: try first child
        elif node.children and len(node.children) > 0:
            print(f"Processing unrecognized node type: {node.value}, trying first child")
            return self._evaluate_expression(node.children[0])
        
        print(f"Unable to evaluate expression node: {node.value}")
        return None

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
        
        if operator == "+":
            result = left + right
            print(f"Addition result: {result}")
            return result
        elif operator == "-":
            result = left - right
            print(f"Subtraction result: {result}")
            return result
        elif operator == "*":
            result = left * right
            print(f"Multiplication result: {result}")
            return result
        elif operator == "/":
            if right == 0:
                print("Division by zero error")
                return None
            result = left / right
            print(f"Division result: {result}")
            return result
        elif operator == "%":
            if right == 0:
                print("Modulo by zero error")
                return None
            result = left % right
            print(f"Modulo result: {result}")
            return result
        elif operator == "==":
            result = left == right
            print(f"Equality result: {result}")
            return 1 if result else 0
        elif operator == "!=":
            result = left != right
            print(f"Inequality result: {result}")
            return 1 if result else 0
        elif operator == "<":
            result = left < right
            print(f"Less than result: {result}")
            return 1 if result else 0
        elif operator == ">":
            result = left > right
            print(f"Greater than result: {result}")
            return 1 if result else 0
        elif operator == "<=":
            result = left <= right
            print(f"Less than or equal result: {result}")
            return 1 if result else 0
        elif operator == ">=":
            result = left >= right
            print(f"Greater than or equal result: {result}")
            return 1 if result else 0
        
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