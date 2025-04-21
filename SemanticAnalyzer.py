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
        
        # Visit the parse tree
        self.visit(parse_tree)
        
        # Only check for unused variables in local scope
        self._check_unused_local_variables()
        print(f"Analysis complete. Found {len(self.errors)} issues.")
        return self.errors

    def visit(self, node, parent=None):
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
                expr_node = init_node.children[1]
                value = self._evaluate_expression(expr_node)
                if value is not None:
                    symbol.set_value(value)
                    print(f"Initialized {var_name} with value: {value}")
        
        self.generic_visit(node)
    
    def visit_local_declarations(self, node):
        # Determine whether this is an array declaration or a regular variable declaration.
        if node.children and node.children[0].value == 'recipe':
            self._handle_array_declaration(node)
        else:
            self._handle_regular_declaration(node)
        self.generic_visit(node)

    def _handle_regular_declaration(self, node):
        if len(node.children) < 2:
            return

        # Get the variable type
        data_type_node = node.children[0].children[0]
        var_type = data_type_node.value

        # Process first declaration
        id_node = node.children[1]
        var_name = id_node.value
        line_num = getattr(id_node, 'line_number', -1)

        try:
            self.current_scope.add(var_name, Symbol(var_name, var_type))

            # Process additional declarations
            current_node = node.children[2]  # <dec_or_init>
            while current_node.children:
                if current_node.children[0].value == ",":
                    next_id = current_node.children[1].value
                    self.current_scope.add(next_id, Symbol(next_id, var_type))
                    current_node = current_node.children[2]
                elif current_node.children[0].value == "=":
                    # Handle initialization
                    self._check_initialization(var_name, var_type,
                                               current_node.children[1],
                                               line_num)
                    break
                else:
                    break
        except SemanticError as e:
            self.errors.append(e)

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
                        operator_node = second_child.children[0]
                        expr_node = second_child.children[1]
                        
                        print(f"\nProcessing expression for {var_name}")
                        print(f"Operator node: {operator_node.value if hasattr(operator_node, 'value') else 'No value'}")
                        print(f"Expression node: {expr_node.value if hasattr(expr_node, 'value') else 'No value'}")
                        print(f"Expression node type: {expr_node.node_type if hasattr(expr_node, 'node_type') else 'No type'}")
                        print(f"Expression children: {[child.value if hasattr(child, 'value') else 'No value' for child in expr_node.children] if hasattr(expr_node, 'children') else 'No children'}")
                        
                        if hasattr(operator_node, 'value') and operator_node.value in ["=", "+=", "-=", "*=", "/=", "%="]:
                            print(f"\nFound assignment operator: {operator_node.value}")
                            
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
                            value = self._evaluate_expression(expr_node)
                            print(f"Expression evaluation result: {value}")
                            
                            if value is not None:
                                # Handle different assignment operators
                                if operator_node.value == "=":
                                    symbol.set_value(value)
                                elif operator_node.value == "+=":
                                    symbol.set_value((symbol.get_value() or 0) + value)
                                elif operator_node.value == "-=":
                                    symbol.set_value((symbol.get_value() or 0) - value)
                                elif operator_node.value == "*=":
                                    symbol.set_value((symbol.get_value() or 0) * value)
                                elif operator_node.value == "/=":
                                    if value == 0:
                                        self.errors.append(SemanticError(
                                            code="DIVISION_BY_ZERO",
                                            message="Division by zero in assignment",
                                            line=getattr(expr_node, 'line_number', None)
                                        ))
                                    else:
                                        symbol.set_value((symbol.get_value() or 0) / value)
                                elif operator_node.value == "%=":
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
            if hasattr(initial_node, 'children') and initial_node.children:
                first_value = initial_node.children[0]
                print(f"\nProcessing initial value3")
                print(f"First value node: {first_value.value if hasattr(first_value, 'value') else 'No value'}")
                print(f"First value type: {first_value.node_type if hasattr(first_value, 'node_type') else 'No type'}")
                
                if hasattr(first_value, 'node_type'):
                    if first_value.node_type == "pastaliterals":
                        result = first_value.value.strip('"')
                        print(f"Found string literal: {result}")
                    elif first_value.node_type == "id":
                        symbol = self.current_scope.lookup(first_value.value)
                        if symbol:
                            print(f"Found symbol: {symbol}")
                            result = str(symbol.get_value() if hasattr(symbol, 'get_value') else "")
                            print(f"Symbol value: {result}")
        
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
                        
                        if hasattr(next_value, 'node_type'):
                            if next_value.node_type == "pastaliterals":
                                result += next_value.value.strip('"')
                                print(f"Concatenated string literal: {result}")
                            elif next_value.node_type == "id":
                                symbol = self.current_scope.lookup(next_value.value)
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
                    break
        
        print(f"\nFinal concatenated result: {result}")
        if result:  # Only add non-empty results
            self.output_buffer.append(result)

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
                elif node.node_type == "id":
                    symbol = self.current_scope.lookup(node.value)
                    if symbol:
                        print(f"Found symbol value: {symbol.get_value()}")
                        return symbol.get_value()
                    else:
                        print(f"Symbol not found: {node.value}")
                        return None
            return None
        
        # Handle expression nodes
        if node.value == "<expression>":
            if len(node.children) >= 2:
                operand = node.children[0]  # First child is operand
                tail = node.children[1]     # Second child is expression_tail
                
                # Evaluate the first operand
                left_value = self._evaluate_operand(operand)
                print(f"Left operand value: {left_value}")
                
                # If there's an operator and second operand in the tail
                if tail.value == "<expression_tail>" and tail.children:
                    operator = tail.children[0]
                    right_operand = tail.children[1]
                    
                    # Evaluate the second operand
                    right_value = self._evaluate_operand(right_operand)
                    print(f"Right operand value: {right_value}")
                    
                    if left_value is not None and right_value is not None:
                        if operator.value == "+":
                            result = left_value + right_value
                            print(f"Addition result: {result}")
                            return result
                        elif operator.value == "-":
                            result = left_value - right_value
                            print(f"Subtraction result: {result}")
                            return result
                        elif operator.value == "*":
                            result = left_value * right_value
                            print(f"Multiplication result: {result}")
                            return result
                        elif operator.value == "/":
                            if right_value == 0:
                                print("Division by zero error")
                                return None
                            result = left_value / right_value
                            print(f"Division result: {result}")
                            return result
                        elif operator.value == "%":
                            if right_value == 0:
                                print("Modulo by zero error")
                                return None
                            result = left_value % right_value
                            print(f"Modulo result: {result}")
                            return result
                else:
                    # If no operator, just return the left value
                    return left_value
        
        # Handle single operand
        elif len(node.children) == 1:
            operand = node.children[0]
            return self._evaluate_operand(operand)
            
        return None

    def _evaluate_operand(self, node):
        if not node:
            return None
            
        print(f"\nEvaluating operand: {node.value if hasattr(node, 'value') else 'No value'}")
        print(f"Operand type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
        
        # Handle direct node types
        if hasattr(node, 'node_type'):
            if node.node_type == "id":
                # Look up the symbol
                symbol = self.current_scope.lookup(node.value)
                if symbol:
                    print(f"Found symbol value: {symbol.value}")
                    return symbol.value
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
        
        # Handle different node values
        if hasattr(node, 'value'):
            if node.value == "<value>":
                if hasattr(node, 'children') and node.children:
                    first_child = node.children[0]
                    if hasattr(first_child, 'node_type'):
                        if first_child.node_type == "id":
                            symbol = self.current_scope.lookup(first_child.value)
                            if symbol:
                                print(f"Found symbol value through value node: {symbol.value}")
                                return symbol.value
                            else:
                                print(f"Symbol not found through value node: {first_child.value}")
                                return None
                        elif first_child.node_type in ["pinchliterals", "skimliterals"]:
                            return self._evaluate_operand(first_child)
            elif node.value == "<expression_operand>":
                if hasattr(node, 'children') and node.children:
                    return self._evaluate_operand(node.children[0])
        
        print(f"Unknown operand type: {node.node_type if hasattr(node, 'node_type') else 'No type'}")
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