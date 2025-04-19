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

    def __repr__(self):
        return f"Symbol(name={self.name}, type={self.type}, attributes={self.attributes})"


class SymbolTable:
    def __init__(self, debugName="", parent=None):
        self.parent = parent
        self.debugName = debugName
        self.symbols = {}

    def add(self, name, symbol):
        # Only check for duplicate function declarations
        if name in self.symbols and symbol.type == "function":
            raise SemanticError("DUPLICATE_DECLARATION", f"Duplicate declaration of function '{name}'", identifier=name)
        self.symbols[name] = symbol

    def lookup(self, name, mark_used=True):
        if name in self.symbols:
            if mark_used:
                self.symbols[name].is_used = True
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name, mark_used)
        else:
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
        self._handle_regular_declaration(node)
    
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
        f_name = "unknown"  # Default value
        return_type = "void"  # Default return type
        
        if len(node.children) >= 2:
            f_name = node.children[2].value if node.children[0].value == "full" else node.children[1].value
            return_type = node.children[1].children[0].value if node.children[0].value == "full" else "void"
            try:
                self.global_scope.add(f_name, Symbol(f_name, "function", {"return_type": return_type}))
            except Exception as e:
                self.errors.append(e)
        
        # Create a new scope for the function body
        old_scope = self.current_scope
        self.current_scope = SymbolTable(debugName=f"function_{f_name}", parent=old_scope)
        self.symbol_tables.append(self.current_scope)
        
        # Process function parameters first
        self._process_function_signature(node)
        
        # Then process the function body
        self.generic_visit(node)
        
        # Check if a function with a return type has a return statement
        if return_type != "void":
            # TODO: Add check for return statement existence
            pass
            
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
        
        # Debug - print what kind of statement we're processing
        print(f"Processing statement: {node.value if hasattr(node, 'value') else 'unknown'}")
        for i, child in enumerate(node.children):
            print(f"  Child {i}: {child.value if hasattr(child, 'value') else 'unknown'}")
        
        # Check if this is an assignment
        if len(node.children) >= 3:
            first_child = node.children[0]
            second_child = node.children[1]
            
            if hasattr(first_child, 'node_type') and first_child.node_type == "id" and \
            hasattr(second_child, 'value') and second_child.value in ["=", "+=", "-=", "*=", "/=", "%="]:
                var_name = first_child.value
                line_num = getattr(first_child, 'line_number', None)
                
                # Look up the symbol
                symbol = self.current_scope.lookup(var_name)
                if not symbol:
                    self.errors.append(SemanticError(
                        code="UNDECLARED_IDENTIFIER", 
                        message=f"Assignment to undeclared identifier '{var_name}'",
                        line=line_num,
                        identifier=var_name
                    ))
                else:
                    # Get the type of the expression being assigned
                    expr_node = node.children[2]
                    expr_type = self.get_expression_type(expr_node)
                    target_type = symbol.type
                    
                    print(f"Assignment check: {var_name} (type={target_type}) = expression (type={expr_type})")
                    
                    # Check if the types are compatible
                    if expr_type is not None and target_type is not None:
                        compatible = expr_type in self.type_compatibility.get(target_type, [])
                        
                        if not compatible:
                            # Convert base types to literal types for error message
                            literal_type = expr_type + "literals" if expr_type in ["pinch", "skim", "pasta"] else expr_type
                            target_literal_type = target_type + "literals" if target_type in ["pinch", "skim", "pasta"] else target_type
                            self.errors.append(SemanticError(
                                code="TYPE_MISMATCH", 
                                message=f"Type mismatch in assignment to '{var_name}': cannot assign '{literal_type}' to '{target_literal_type}'",
                                line=line_num,
                                identifier=var_name
                            ))
                            print(f"ERROR: Type mismatch detected! {literal_type} is not compatible with {target_literal_type}")
        
        # Continue with generic visit to process other types of statements
        self.generic_visit(node)
    
    def visit_serve_statement(self, node, parent=None):
        """Handle the 'serve' statement (function call)"""
        print("\n=== Debug: Processing serve statement ===")
        print(f"Node value: {node.value if hasattr(node, 'value') else 'No value'}")
        
        # If we have a parent node, use it
        if parent and hasattr(parent, 'children') and len(parent.children) >= 6:
            statement_node = parent
        else:
            # Otherwise, look for the statement node in the current node's children
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    if hasattr(child, 'value') and child.value == "<statement>":
                        statement_node = child
                        break
                else:
                    print("Could not find statement node")
                    return
            else:
                print("No children in serve node")
                return
        
        print(f"Statement node value: {statement_node.value}")
        print(f"Statement children count: {len(statement_node.children)}")
        
        # The argument should be in the third child (index 2)
        arg_node = statement_node.children[2]
        print(f"Argument node value: {arg_node.value}")
        
        # Check if this is a function call
        if hasattr(arg_node, 'children') and arg_node.children:
            if arg_node.children[0].node_type == "id":
                # This is a function call
                func_name = arg_node.children[0].value
                print(f"Found function call: {func_name}")
                
                # Look up the function in the symbol table
                func_symbol = self.global_scope.lookup(func_name)
                if func_symbol and func_symbol.type == "function":
                    # Get the return value from the function
                    return_value = self._evaluate_function_call(func_name)
                    if return_value is not None:
                        # Only add to output buffer if it's not already there
                        if not self.output_buffer or self.output_buffer[-1] != str(return_value):
                            self.output_buffer.append(str(return_value))
                else:
                    print(f"Function {func_name} not found or not a function")
            else:
                # Handle literals3 node for string literals
                literals3_node = arg_node.children[0]
                print(f"Literals3 node value: {literals3_node.value}")
                
                if hasattr(literals3_node, 'children') and literals3_node.children:
                    # The string literal should be the first child of literals3
                    string_node = literals3_node.children[0]
                    print(f"String node type: {string_node.node_type if hasattr(string_node, 'node_type') else 'No node type'}")
                    print(f"String node value: {string_node.value if hasattr(string_node, 'value') else 'No value'}")
                    
                    if hasattr(string_node, 'node_type') and string_node.node_type == "pastaliterals":
                        # Handle string literals directly
                        print(f"Found string literal: {string_node.value}")
                        # Only add to output buffer if it's not already there
                        if not self.output_buffer or self.output_buffer[-1] != string_node.value.strip('"'):
                            self.output_buffer.append(string_node.value.strip('"'))
                    elif hasattr(string_node, 'value'):
                        # Only add to output buffer if it's not already there
                        if not self.output_buffer or self.output_buffer[-1] != str(string_node.value).strip('"'):
                            self.output_buffer.append(str(string_node.value).strip('"'))
        
        print("=== End of serve statement processing ===\n")

    def _evaluate_function_call(self, func_name):
        """Evaluate a function call and return its value"""
        print(f"\n=== Debug: Evaluating function call {func_name} ===")
        
        # Look up the function in the symbol table
        func_symbol = self.global_scope.lookup(func_name)
        if not func_symbol or func_symbol.type != "function":
            print(f"Function {func_name} not found or not a function")
            return None
            
        # Get the function's return type
        return_type = func_symbol.attributes.get('return_type', 'void')
        print(f"Function return type: {return_type}")
        
        # For now, we'll just return a dummy value based on the return type
        # In a real implementation, you would need to:
        # 1. Find the function's body in the AST
        # 2. Execute the function's statements
        # 3. Return the actual value from the function
        if return_type == "pinch":
            return 42  # Example integer return value
        elif return_type == "skim":
            return 3.14  # Example float return value
        elif return_type == "pasta":
            return "asdasd"  # Example string return value
        elif return_type == "bool":
            return True  # Example boolean return value
            
        return None

    def get_output(self):
        """Get the accumulated output from serve statements"""
        if not self.output_buffer:
            return "===Program executed successfully==="
        return "\n".join(self.output_buffer) + "\n\n===Program executed successfully==="

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