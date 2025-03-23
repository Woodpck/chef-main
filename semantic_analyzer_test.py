from LexicalAnalyzer import LexicalAnalyzer
from SemanticAnalyzer import SemanticAnalyzer, SemanticError
from SyntaxAnalyzer import SyntaxAnalyzer, LL1Parser, cfg, parse_table, follow_set

# ANSI color codes for output formatting
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def analyze(code):
    tokens = []
    syntax_errors = []
    semantic_errors = []

    # Lexical Analysis
    if code.strip():
        analyzer = LexicalAnalyzer()
        try:
            tokens = analyzer.tokenize(code)
        except Exception as e:
            return [], [], [f"An error occurred during lexical analysis: {e}"]

    # Syntax Analysis
    if code.strip():
        try:
            parser = LL1Parser(cfg, parse_table, follow_set)
            is_valid, syntax_errors = parser.parse(tokens)
        except Exception as e:
            syntax_errors = [f"An error occurred during syntax analysis: {e}"]

    # Semantic Analysis
    if code.strip():
        try:
            if not syntax_errors:  # Only proceed if syntax analysis passed
                analyzer = SemanticAnalyzer()
                semantic_errors = analyzer.analyze(parser.parse_tree)
        except Exception as e:
            semantic_errors = [f"An error occurred during semantic analysis: {e}"]

    return tokens, syntax_errors, semantic_errors


def run_test(test):
    """
    Runs a single test case defined by a dictionary with keys:
      - name: str
      - code: str
      - expected_syntax_errors: list
      - expected_semantic_errors: list of tuples (error_code, identifier)
    Returns a dictionary with test results.
    """
    test_name = test.get("name", "Unnamed Test")
    code = test.get("code", "")
    expected_syntax_errors = test.get("expected_syntax_errors", [])
    expected_semantic_errors = test.get("expected_semantic_errors", [])
    expected_semantic_warnings = test.get("expected_semantic_warnings", [])

    print(f"{CYAN}===== Running Test: {test_name} ====={RESET}")
    tokens, syntax_errors, semantic_errors = analyze(code)

    # Process semantic errors: extract error code and identifier if available.
    actual_semantic_errors = []
    warnings = []
    for error in semantic_errors:
        if hasattr(error, 'code'):
            if error.is_warning:
                warnings.append((error.code, error.identifier))
            else:
                actual_semantic_errors.append((error.code, error.identifier))
        else:
            print(f"{RED}Error: {error}{RESET}")
            actual_semantic_errors.append((None, None))

    print(f"{YELLOW}Tokens:{RESET}\n  {tokens}")
    print(f"{YELLOW}Syntax Errors:{RESET}\n  {syntax_errors}")
    print(f"{YELLOW}Semantic Errors (codes and identifiers):{RESET}\n  {actual_semantic_errors}")
    print(f"{YELLOW}Warnings (codes and identifiers):{RESET}\n  {warnings}")

    syntax_pass = (syntax_errors == expected_syntax_errors)
    semantic_pass = (actual_semantic_errors == expected_semantic_errors)
    semantic_warnings_pass = (warnings == expected_semantic_warnings)

    syntax_result = f"{GREEN}PASS{RESET}" if syntax_pass else f"{RED}FAIL{RESET}"
    semantic_result = f"{GREEN}PASS{RESET}" if semantic_pass else f"{RED}FAIL{RESET}"
    semantic_warnings_result = f"{GREEN}PASS{RESET}" if semantic_warnings_pass else f"{RED}FAIL{RESET}"

    print(f"{CYAN}Results:{RESET}")
    print(f"  Syntax Test: {syntax_result}")
    print(f"  Semantic Test: {semantic_result}")
    print(f"  Semantic Warnings Test: {semantic_warnings_result}")
    print(f"{CYAN}{'=' * 40}{RESET}\n")

    # Return test results for summary purposes.
    return {
        "test_name": test_name,
        "syntax_pass": syntax_pass,
        "semantic_pass": semantic_pass,
        "syntax_errors": syntax_errors,
        "expected_syntax_errors": expected_syntax_errors,
        "semantic_errors": actual_semantic_errors,
        "expected_semantic_errors": expected_semantic_errors,
        "semantic_warnings": warnings,
        "expected_semantic_warnings": expected_semantic_warnings,
        "semantic_warnings_pass": semantic_warnings_pass,
    }


def run_all_tests():
    # Define tests as a list of dictionaries for easy addition.
    tests = [
        {
            "name": "Valid Code",
            "code": """
                dinein
                chef pinch dish() {
                    bool test;
                    test = 3;
                    spit 0;
                }
                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [],
        },
        {
            "name": "Undeclared Identifier",
            "code": """
                dinein
                chef pinch dish() {
                    bool test;
                    h = 3;      // 'h' is not declared
                    spit 0;
                }
                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [("UNDECLARED_IDENTIFIER", "h")],
        },
        {
            "name": "Duplicate Declaration",
            "code": """
                dinein
                chef pinch dish() {
                    bool test;
                    bool test;  // duplicate declaration
                    test = 5;
                    spit 0;
                }
                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [("DUPLICATE_DECLARATION", "test")],
        },
        {
            "name": "Undeclared Identifier in taste",
            "code": """
                dinein

                chef pinch dish() {
                    taste (i <= x <= 10) {
                        serve ("yow");
                    }
                    spit 0;
                }

                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [
                ("UNDECLARED_IDENTIFIER", "i"),
                ("UNDECLARED_IDENTIFIER", "x"),
            ],
        },
        {
            "name": "Declared Identifier in taste",
            "code": """
                dinein

                chef pinch dish() {
                    pinch i;
                    pinch x;
                    taste (i <= x <= 10) {
                        serve ("yow");
                    }
                    spit 0;
                }

                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [],
        },
        
        {
            "name": "Global Variable Shadowing",
            "code": """
                dinein

                chef pinch dish() {
                    pinch x = 5;
                    spit 0;
                }
                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [],
            
        },

        {
            "name": "duplicate function",
            "code": """
                dinein

                full pinch dish2() {
                    spit 0;
                }
                
                full pinch dish2() {
                    spit 0;
                }

                chef pinch dish() {
                    spit 0;
                }

                takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [("DUPLICATE_DECLARATION", "dish2")],
        },
        
        {
            "name": "bug 001",
            "code": """
            dinein

            chef pinch dish() {
                test=0;
                spit 0;
            }

            takeout
            """,
            "expected_syntax_errors": [],
            "expected_semantic_errors": [("UNDECLARED_IDENTIFIER", "test")],
        }
    ]

    results = []
    for test in tests:
        result = run_test(test)
        results.append(result)

    # Display a summary of all failed tests, if any.
    failed_tests = [res for res in results if not (res["syntax_pass"] and res["semantic_pass"])]
    if failed_tests:
        print(f"{RED}===== Failed Tests Summary ====={RESET}")
        for res in failed_tests:
            print(f"{RED}Test: {res['test_name']}{RESET}")
            if not res["syntax_pass"]:
                print("  Syntax Errors:")
                print(f"    Expected: {res['expected_syntax_errors']}")
                print(f"    Got:      {res['syntax_errors']}")
            if not res["semantic_pass"]:
                print("  Semantic Errors:")
                print(f"    Expected: {res['expected_semantic_errors']}")
                print(f"    Got:      {res['semantic_errors']}")
            print("-" * 40)
    else:
        print(f"{GREEN}All tests passed!{RESET}")


if __name__ == "__main__":
    run_all_tests()
