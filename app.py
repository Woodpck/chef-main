from SemanticAnalyzer import SemanticAnalyzer
from flask import Flask, render_template, request
from LexicalAnalyzer import LexicalAnalyzer
from SyntaxAnalyzer import SyntaxAnalyzer, LL1Parser, cfg, parse_table, follow_set

app = Flask(__name__)

def normalize_newlines(text):
    """Normalize newline characters for cross-platform compatibility."""
    return text.replace("\r\n", "\n").replace("\r", "\n")

# lex, parse, sem
def analyze(code):
    tokens = []
    syntax_errors = []
    semantic_errors: list[str] = []

    # Lexical Analysis
    if code.strip():
        analyzer = LexicalAnalyzer()
        try:
            tokens = analyzer.tokenize(code)
        except Exception as e:
            return [], [], [f"An error occurred during lexical analysis: {e}"]

    # Syntax Analysis
    if code.strip()     :
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
                    
    return tokens, syntax_errors, semantic_errors

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    error_tokens_text = ""
    error_syntax_text = ""
    error_symantic_text = ""
    code = ""
    tokens = []  # Store tokens for both lexical and syntax analysis

    if request.method == "POST":
        code = normalize_newlines(request.form.get("code", ""))
        action = request.form.get("action")

        # Lexical Analysis
        if code.strip():
            analyzer = LexicalAnalyzer()
            try:
                tokens = analyzer.tokenize(code)
                result = [(token[0], token[1]) for token in tokens]  # Match HTML table structure
                error_tokens_text = "\n".join(analyzer.errors)
            except Exception as e:
                error_tokens_text = f"An error occurred during lexical analysis: {e}"

        # Syntax Analysis
        if action == "Syntax" and code.strip():
            try:
                if not error_tokens_text:  # Only proceed if lexical analysis passed
                    parser = LL1Parser(cfg, parse_table, follow_set)
                    is_valid, syntax_errors = parser.parse(tokens)
                    
                    error_syntax_text = "\n".join(syntax_errors)
                # Note: We're not setting result here, keeping the tokens from lexical analysis
            except Exception as e:
                error_syntax_text = f"An error occurred during syntax analysis: {e}"

        if action == "Semantic" and code.strip():
            tokens, syntax_errors, semantic_errors = analyze(code)
            error_syntax_text = "\n".join(syntax_errors)
            error_symantic_text = "\n".join(semantic_errors)
    return render_template(
        "index.html",
        code=code,
        result=result,
        error_tokens_text=error_tokens_text,
        error_syntax_text=error_syntax_text,
        error_semantic_text=error_symantic_text
    )


if __name__ == "__main__":
    app.run(debug=True)