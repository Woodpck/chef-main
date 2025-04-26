from flask import Flask, render_template, request, jsonify
from LexicalAnalyzer import LexicalAnalyzer
from SyntaxAnalyzer import SyntaxAnalyzer, LL1Parser, cfg, parse_table, follow_set
from SemanticAnalyzer import SemanticAnalyzer
import time

app = Flask(__name__)

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

# lex, parse, sem
def analyze(code):
    tokens = []
    syntax_errors = []
    semantic_errors = []
    output = ""

    # Lexical Analysis
    if code.strip():
        analyzer = LexicalAnalyzer()
        try:
            tokens = analyzer.tokenize(code)
        except Exception as e:
            return [], [], [f"An error occurred during lexical analysis: {e}"], "Error occurred during analysis"

    # Syntax Analysis
    if code.strip():
        try:
            parser = LL1Parser(cfg, parse_table, follow_set)
            is_valid, syntax_errors = parser.parse(tokens)
        except Exception as e:
            syntax_errors = [f"An error occurred during syntax analysis: {e}"]

    # Semantic Analysis
    if code.strip():
        if not syntax_errors:  # Only proceed if syntax analysis passed
            analyzer = SemanticAnalyzer()
            semantic_errors_exceptions = analyzer.analyze(parser.parse_tree)
            
            for error in semantic_errors_exceptions:
                semantic_errors.append(str(error))
            
            # Get output from semantic analyzer if no errors
            if not semantic_errors:
                output = analyzer.get_output()
                if not output:
                    output = "Program executed successfully with no output."
    
    if syntax_errors or semantic_errors:
        output = "Cannot run program with errors."
    
    return tokens, syntax_errors, semantic_errors, output

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    error_tokens_text = ""
    error_syntax_text = ""
    error_semantic_text = ""
    code = ""
    tokens = []
    active_tab = "errors"
    output_text = ""  # For output tab
    time_execution = 0

    if request.method == "POST":
        start_time = time.time()
        code = normalize_newlines(request.form.get("code", ""))
        action = request.form.get("action")

        # Lexical Analysis
        if code.strip():
            analyzer = LexicalAnalyzer()
            try:
                tokens = analyzer.tokenize(code)
                result = [(token[0], token[1]) for token in tokens]
                error_tokens_text = "\n".join(analyzer.errors) if hasattr(analyzer, 'errors') else ""
            except Exception as e:
                error_tokens_text = f"An error occurred during lexical analysis: {e}"

        # Syntax Analysis
        if (action == "Syntax" or action == "Semantic" or action == "Run") and code.strip():
            try:
                if not error_tokens_text:
                    parser = LL1Parser(cfg, parse_table, follow_set)
                    is_valid, syntax_errors = parser.parse(tokens)
                    error_syntax_text = "\n".join(syntax_errors)
            except Exception as e:
                error_syntax_text = f"An error occurred during syntax analysis: {e}"

        # Semantic Analysis
        if (action == "Semantic" or action == "Run") and code.strip():
            if not error_tokens_text and not error_syntax_text:
                try:
                    analyzer = SemanticAnalyzer()
                    semantic_errors_exceptions = analyzer.analyze(parser.parse_tree)
                    semantic_errors = [str(error) for error in semantic_errors_exceptions]
                    error_semantic_text = "\n".join(semantic_errors)
                except Exception as e:
                    error_semantic_text = f"An error occurred during semantic analysis: {e}"

        # Run Program Action
        if action == "Run":
            if not code.strip():  # Check if code is empty or just whitespace
                # Keep the default "No output generated yet" message by not changing output_text
                pass  # Don't modify output_text when code is empty
            elif not error_tokens_text and not error_syntax_text and not error_semantic_text:
                # Use the existing analyzer instance that was created during semantic analysis
                if 'analyzer' in locals() and 'parser' in locals():
                    semantic_errors_exceptions = analyzer.analyze(parser.parse_tree)
                    if not semantic_errors_exceptions:  # Only proceed if no semantic errors
                        output_text = process_output(analyzer.get_output())
                    else:
                        output_text = "Cannot run program with errors."
                else:
                    output_text = "Error: Program analysis not completed properly."
            else:
                output_text = "Cannot run program with errors."
            
            active_tab = "output"

        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            time_execution = time.time() - start_time
            return jsonify({
                'result': result,
                'error_tokens_text': error_tokens_text,
                'error_syntax_text': error_syntax_text,
                'error_semantic_text': error_semantic_text,
                'output_text': output_text,
                'active_tab': active_tab,
                'time_execution': time_execution
            })

    # For standard GET requests or non-AJAX POST requests
    return render_template(
        "index.html",
        code=code,
        result=result,
        error_tokens_text=error_tokens_text,
        error_syntax_text=error_syntax_text,
        error_semantic_text=error_semantic_text,
        output_text=output_text,
        active_tab=active_tab,
        time_execution=time_execution
    )



if __name__ == "__main__":
    app.run(debug=True)