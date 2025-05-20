from flask import Flask, render_template, request, jsonify
from LexicalAnalyzer import LexicalAnalyzer
from SyntaxAnalyzer import SyntaxAnalyzer, LL1Parser, cfg, parse_table, follow_set
from SemanticAnalyzer import SemanticAnalyzer
import os
import sys
import time

app = Flask(__name__)

original_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

def normalize_newlines(text):
    """Normalize newline characters for cross-platform compatibility."""
    return text.replace("\r\n", "\n").replace("\r", "\n")

def process_output(raw_output):
    """Process output to properly handle escape sequences."""
    if not raw_output:
        return ""
        
    # First handle literal escape sequences in strings like "\\n" -> "\n"
    processed = raw_output
    
    # Then handle any actual escape sequences that should be printed as characters
    # This assumes raw_output could contain actual escape notation like "Hello\\nWorld"
    # that we want to convert to actual newlines and tabs in the output
    processed = processed.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")
    
    return processed

@app.route("/", methods=["GET", "POST"])
def index():
    program_code = ""
    lexeme_token_list = []
    lexical_errors = ""
    syntax_errors = ""
    semantic_errors = ""
    output_tab_result = ""
    active_tab = "errors"
    time_execution = 0
    
    if request.method == "POST":
        start_time = time.time()
        has_lexical_passed = False
        has_syntax_passed = False
        has_semantic_passed = False

        # FIX_OPTIONAL: Add empty string validation for code
        program_code = normalize_newlines(request.form.get("code")).strip()             # Normalize newlines and strip leading and trailing whitespaces
        try:
            # Tokenize user inputted code using Lexical Analyzer
            tokens, errors = LexicalAnalyzer().tokenize(program_code)
            lexeme_token_list = [(token[0], token[1]) for token in tokens]              # token[0] refers to lexeme, token[1] refers to token type
            if errors:
                lexical_errors = "\n\n".join(errors)                                      # Join all the error messages into a single string
            else:
                has_lexical_passed = True
        except Exception as e:
            lexical_errors = f"Lexical Error: {e}"

        # Parse tokens using Syntax Analyzer
        if has_lexical_passed:
            print("Lexical passed")
            try:
                # analyzer = SyntaxAnalyzer() # it should be like this
                syntax_analyzer = LL1Parser(cfg, parse_table, follow_set)

                # FIX: it should return the parse tree
                _, has_syntax_errors = syntax_analyzer.parse(tokens)
                
                # Get error
                syntax_errors = "\n".join(has_syntax_errors)

                if not has_syntax_errors:
                    has_syntax_passed = True
            except Exception as e:
                syntax_errors = f"An error occurred during syntax analysis: {e}"
        
        # Parse parse tree using Semantic Analyzer
        if has_syntax_passed:
            print("Syntax passed")
            try:
                semantic_analyzer = SemanticAnalyzer()
                # FIX: Should just use the returned parse tree
                # Should also return output_text
                semantic_errors_exceptions = semantic_analyzer.analyze(syntax_analyzer.parse_tree)        
                has_semantic_errors = [str(error) for error in semantic_errors_exceptions]
                semantic_errors = "\n".join(has_semantic_errors)

                if not has_semantic_errors:
                    has_semantic_passed = True
            except Exception as e:
                if semantic_analyzer.errors:
                    error_semantic_text = [str(error) for error in semantic_analyzer.errors]
                    semantic_errors = "\n".join(error_semantic_text)
                else:
                    semantic_errors = f"An error occurred during semantic analysis: {e}"

        if has_semantic_passed:
            print("Semantic passed")
            # FIX: Should just use the returned output
            output_tab_result = process_output(semantic_analyzer.get_output())
            active_tab = "output"

        if not has_lexical_passed or not has_syntax_passed or not has_semantic_passed:
            #output_tab_result = process_output(semantic_analyzer.get_output()) + "\nError while the program is running"
            output_tab_result = "Cannot run program with errors."

        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            time_execution = time.time() - start_time
            return jsonify({
                'result': lexeme_token_list,
                'error_tokens_text': lexical_errors,
                'error_syntax_text': syntax_errors,
                'error_semantic_text': semantic_errors,
                'output_text': output_tab_result,
                'active_tab': active_tab,
                'time_execution': time_execution,
            })

    # For standard GET requests or non-AJAX POST requests
    return render_template(
        "index.html",
        code=program_code,
        result=lexeme_token_list,
        error_tokens_text=lexical_errors,
        error_syntax_text=syntax_errors,
        error_semantic_text=semantic_errors,
        output_text=output_tab_result,
        active_tab=active_tab,
        time_execution=time_execution,
    )

if __name__ == "__main__":
    app.run(debug=True)