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

    def analyze(self, parse_tree):
        self.visit(parse_tree)
        self._check_unused_variables()
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
            self.generic_visit(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

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
        # Expected structure: <data_type> id <dec_or_init> ;
        if len(node.children) < 2:
            return
        data_type_node = node.children[0].children[0]  # <data_type> -> terminal
        var_type = data_type_node.value
        id_node = node.children[1]
        var_name = id_node.value
        line_num = getattr(id_node, 'line_number', -1)
        
        print("handle regular declaration", var_name, var_type, self.current_scope)
        try:
            self.current_scope.add(var_name, Symbol(var_name, var_type))
        except Exception as e:
            self.errors.append(SemanticError(e.code, e.message, line=line_num, identifier=var_name))

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
            self.errors.append(SemanticError(code = "INVALID_ARRAY_SIZE", line=line_num, message=f"Invalid array size for '{var_name}'"), identifier=var_name)
        attributes = {'dimensions': dimension, 'element_type': var_type}
        try:
            self.current_scope.add(var_name, Symbol(var_name, var_type, attributes))
        except SemanticError as e:
            self.errors.append(SemanticError(e.code, e.message, line=line_num, identifier=var_name))


    #-----------------------------------------------------------------
    # Function handling
    #-----------------------------------------------------------------
    def visit_function(self, node):
        if len(node.children) >= 2:
            f_name = node.children[2].value
            try:
                self.global_scope.add(f_name, Symbol(f_name, "function"))
            except Exception as e:
                self.errors.append(e)
        # Create a new scope for the function body.
        old_scope = self.current_scope
        
        self.current_scope = SymbolTable(parent=old_scope)
        self.symbol_tables.append(self.current_scope)

        # add function name to the current scope
        
        
        self._process_function_signature(node)
        self.generic_visit(node)
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
            else:  # "hungry" functions have no explicit return type in the signature.
                id_node = node.children[1]
            self.current_function = id_node.value

    #-----------------------------------------------------------------
    # Statement handling (including assignment checking)
    #-----------------------------------------------------------------
    def visit_statement(self, node):
        if not node.children:
            return
        first_child = node.children[0]
        line_num = getattr(first_child, 'line_number', None)
        
        if first_child.node_type == "id":
            # Check for a simple assignment:
            if len(node.children) >= 2 and node.children[1].value in ["=", "+=", "-=", "*=", "/=", "%="]:
                var_name = first_child.value
                symbol = self.current_scope.lookup(var_name)
                if not symbol:
                    self.errors.append(SemanticError(code="UNDECLARED_IDENTIFIER", line=line_num, message=f"Assignment to undeclared identifier '{var_name}'", identifier=var_name))
            # Check for an array element assignment:
            elif len(node.children) >= 2 and node.children[1].value == "[":
                var_name = first_child.value
                symbol = self.current_scope.lookup(var_name)
                if not symbol:
                    self.errors.append(SemanticError(code="UNDECLARED_IDENTIFIER", line=line_num, message=f"Assignment to undeclared identifier '{var_name}'", identifier=var_name))
                else:
                    # Verify that the symbol is declared as an array.
                    if 'dimensions' not in symbol.attributes or symbol.attributes['dimensions'] is None:
                        self.errors.append(SemanticError(code="INVALID_ARRAY_USAGE", line=line_num, message=f"Identifier '{var_name}' is not declared as an array", identifier=var_name))
        self.generic_visit(node)
    
    def visit_looping_statement(self, node):
        if not node.children:
            return
        first_child = node.children[0]

        if first_child.node_type == "for":
            self._handle_for_loop(node)

    def _handle_for_loop(self, node):
        # Expected structure: for ( <assignment> ; <expression> ; <assignment> ) <statement>
        if len(node.children) < 7:
            raise SemanticError("INVALID_FOR_LOOP", "Invalid for loop structure", line=node.line_number)


    #-----------------------------------------------------------------
    # Identifier usage checking
    #-----------------------------------------------------------------
    def check_id_usage(self, node: ParseTreeNode):
        # For identifier usage in expressions, assume the leaf node value is the identifier name.
        var_name = node.value
        line_num = node.line_number
        symbol = self.current_scope.lookup(var_name)
        if not symbol:
            self.errors.append(SemanticError(code="UNDECLARED_IDENTIFIER", message=f"Use of undeclared identifier '{var_name}'", identifier=var_name, line=line_num))

    #-----------------------------------------------------------------
    # Unused variable warnings
    #-----------------------------------------------------------------
    def _check_unused_variables(self):
        for table in self.symbol_tables:
            unused = table.get_unused()
            for name in unused:
                if not name.startswith('__'):
                    self.errors.append(SemanticError(code="UNUSED_VARIABLE", message=f"Unused variable '{name}'", identifier=name, is_warning=True))