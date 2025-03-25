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
        if name in self.symbols:
            raise SemanticError("DUPLICATE_DECLARATION", f"Duplicate declaration of '{name}'", identifier=name)
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
    def __init__(self):
        self.global_scope = SymbolTable(debugName="global")
        self.current_scope = self.global_scope
        self.errors = []
        self.symbol_tables = [self.global_scope]
        self.current_function = None
        # Define type compatibility rules
        self.type_compatibility = {
            "pinch": ["pinch"],           # Integers
            "skim": ["skim", "pinch"],    # Floats can accept integers
            "pasta": ["pasta"],           # Strings
            "recipe": ["recipe"],         # Arrays
            "bool": ["bool", "pinch"]     # Booleans can accept integers (0/1)
        }

    def analyze(self, parse_tree):
        print("Starting semantic analysis...")
        self.visit(parse_tree)
        self._check_unused_variables()
        print(f"Analysis complete. Found {len(self.errors)} issues.")
        for error in self.errors:
            print(f"  {error}")
        return self.errors

    def visit(self, node):
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
                self.visit_serve_statement(node)
            self.generic_visit(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    #-----------------------------------------------------------------
    # Type checking utility methods
    #-----------------------------------------------------------------
    def get_expression_type(self, expr_node):
        """Determine the type of an expression."""
        # Base case for terminal nodes or nodes without children
        if not hasattr(expr_node, 'children') or not expr_node.children:
            if hasattr(expr_node, 'node_type'):
                if expr_node.node_type == "pinchliteral":
                    return "pinch"
                elif expr_node.node_type == "skimliteral":
                    return "skim"
                elif expr_node.node_type == "pastaliteral":
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
        print("scope", self.current_scope)
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
        # Debug - print the declaration we're processing
        print(f"Processing declaration: {node.value if hasattr(node, 'value') else 'unknown'}")
        for i, child in enumerate(node.children):
            print(f"  Child {i}: {child.value if hasattr(child, 'value') else 'unknown'}")
        
        if len(node.children) < 2:
            return
        
        # Get the variable type and name
        data_type_node = node.children[0].children[0]  # <data_type> -> terminal    //missing lit
        print(f"{node.children[3].value=}")      
        var_type = data_type_node.value
        id_node = node.children[1]
        var_name = id_node.value
        line_num = getattr(id_node, 'line_number', -1)
        
        print(f"Declaration: {var_name} of type {var_type}")
        
        try:
            # Add the symbol to the current scope
            self.current_scope.add(var_name, Symbol(var_name, var_type))
            # Check for initialization
                        # Check for initialization
            if (
                len(node.children) > 2
                and hasattr(node.children[2], "children")
                and len(node.children[2].children) > 1
                and hasattr(node.children[2].children[0], "value")
                and node.children[2].children[0].value == "="
                and hasattr(node.children[2].children[1], "children")
                and len(node.children[2].children[1].children) > 0
            ):
                # Get the type of the initializer
                expr_node = node.children[2].children[1].children[0]
                expr_type = self.get_expression_type(expr_node)
                
                print(f"Initialization check: {var_name} (type={var_type}) = expression (type={expr_type})")
                
                # Check compatibility
                if expr_type is not None and var_type is not None:
                    compatible = expr_type in self.type_compatibility.get(var_type, [])
                    
                    if not compatible:
                        self.errors.append(SemanticError(
                            code="TYPE_MISMATCH", 
                            message=f"Type mismatch in initialization of '{var_name}': cannot assign '{expr_type}' to '{var_type}'",
                            line=line_num,
                            identifier=var_name
                        ))
                        print(f"ERROR: Type mismatch detected in initialization! {expr_type} is not compatible with {var_type}")
        except Exception as e:
            if isinstance(e, SemanticError):
                self.errors.append(e)
            else:
                print(f"Exception during declaration: {str(e)}")
                self.errors.append(SemanticError(
                    code="UNKNOWN_ERROR",
                    message=f"Error during declaration of '{var_name}': {str(e)}",
                    line=line_num,
                    identifier=var_name
                ))

    def _handle_array_declaration(self, node):
        # Expected structure: 'recipe', <data_type2>, id, "[", pinchliterals, "]", <elements>, ";"
        if len(node.children) < 5:
            return
        data_type_node = node.children[1].children[0]  # <data_type2> -> terminal
        var_type = data_type_node.value
        id_node = node.children[2]
        var_name = id_node.value
        # Get array dimension from the pinchliterals node (assumed to be an integer literal)
        dimension_node = node.children[4]
        line_num = getattr(id_node, 'line', None)
        
        try:
            dimension = int(dimension_node.value)
        except ValueError:
            dimension = None
            self.errors.append(SemanticError(
                code="INVALID_ARRAY_SIZE",
                message=f"Invalid array size for '{var_name}'", 
                line=line_num, 
                identifier=var_name
            ))
        attributes = {'dimensions': dimension, 'element_type': var_type}
        try:
            self.current_scope.add(var_name, Symbol(var_name, "recipe", attributes))
            
            # Check if there's an initialization and verify type compatibility of elements
            if len(node.children) > 7 and node.children[7].value == "=":
                # TODO: Add array initialization type checking
                pass
        except SemanticError as e:
            self.errors.append(SemanticError(e.code, e.message, line=line_num, identifier=var_name))


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
        self._process_function_signature(node)
        self.generic_visit(node)
        
        # Check if a function with a return type has a return statement
        if return_type != "void":
            # TODO: Add check for return statement existence
            pass
            
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
                            self.errors.append(SemanticError(
                                code="TYPE_MISMATCH", 
                                message=f"Type mismatch in assignment to '{var_name}': cannot assign '{expr_type}' to '{target_type}'",
                                line=line_num,
                                identifier=var_name
                            ))
                            print(f"ERROR: Type mismatch detected! {expr_type} is not compatible with {target_type}")
        
        # Continue with generic visit to process other types of statements
        self.generic_visit(node)
    
    def visit_serve_statement(self, node):
        """Handle the 'serve' statement (function call)"""
        if not hasattr(node, 'children') or len(node.children) < 3:
            return
        
        # Check for arguments
        if len(node.children) >= 3 and hasattr(node.children[2], 'value') and node.children[2].value == "<value3>":
            arg_node = node.children[2]
            arg_type = self.get_expression_type(arg_node)
            
            print(f"Serve statement with argument of type: {arg_type}")
            
            # Serve typically expects a pasta type (string) for output
            if arg_type and arg_type != "pasta":
                line_num = getattr(node, 'line_number', None) or getattr(arg_node, 'line_number', None)
                self.errors.append(SemanticError(
                    code="TYPE_MISMATCH", 
                    message=f"Type mismatch in 'serve' statement: expected 'pasta', got '{arg_type}'",
                    line=line_num
                ))
                print(f"ERROR: Serve statement expects 'pasta' type, but got {arg_type}")
    
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
                self.errors.append(SemanticError(
                    code="TYPE_MISMATCH", 
                    message=f"Return type mismatch: cannot convert '{expr_type}' to '{self.current_function['return_type']}'",
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
        symbol = self.current_scope.lookup(var_name)
        if not symbol:
            self.errors.append(SemanticError(
                code="UNDECLARED_IDENTIFIER", 
                message=f"Use of undeclared identifier '{var_name}'",
                identifier=var_name, 
                line=line_num
            ))

    #-----------------------------------------------------------------
    # Unused variable warnings
    #-----------------------------------------------------------------
    def _check_unused_variables(self):
        for table in self.symbol_tables:
            unused = table.get_unused()
            for name in unused:
                if not name.startswith('__'):
                    self.errors.append(SemanticError(
                        code="UNUSED_VARIABLE", 
                        message=f"Unused variable '{name}'",
                        identifier=name, 
                        is_warning=True
                    ))