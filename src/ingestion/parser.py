from tree_sitter import Parser
from src.ingestion.loader import load_files_from_directory
from tree_sitter_languages import get_language  # ← Changed from get_parser
from src.ingestion.loader import EXTENSION_LANGUAGE_MAP
from src.utils.logger import get_logger

logger = get_logger(__name__)
def parser_code(file_paths):
    """Parse one or more files into ASTs."""
    results = load_files_from_directory(file_paths)

    for file in results:
        path = file["path"]
        ext = "." + path.split(".")[-1] 
        lang = EXTENSION_LANGUAGE_MAP.get(ext, "unknown")
        content = file.get("content", "")

        if lang == "unknown" or not content.strip():
            file["tree"] = None
            continue

        try:
            # get_language returns a Language object
            # Create Parser and set the language
            language = get_language(lang)
            tree_parser = Parser()
            tree_parser.set_language(language)
            file["tree"] = tree_parser.parse(content.encode("utf-8"))
            file["language"] = lang # Store language string for downstream use
        except Exception as e:
            logger.error(f"Could not parse {path} ({lang}): {e}")
            file["tree"] = None

    return results

def parse_content(code: str, language_name: str):
    """
    Parse code string into AST directly.
    
    Args:
        code: Source code string
        language_name: Language name (python, javascript, java, cpp, etc.)
        
    Returns:
        Tree-sitter AST or None
    """
    if not code.strip():
        return None
        
    try:
        # Normalize language name
        if language_name == "js": language_name = "javascript"
        
        language = get_language(language_name)
        tree_parser = Parser()
        tree_parser.set_language(language)
        return tree_parser.parse(code.encode("utf-8"))
    except Exception as e:
        logger.error(f"Could not parse content for {language_name}: {e}")
        return None

if __name__ == "__main__":
    test_files = ["sample.py", "sample.js", "sample.java", "sample.cpp"]
    parsed = parser_code(test_files)
    for file in parsed:
        print("File:", file["path"])
        print("Detected:", EXTENSION_LANGUAGE_MAP.get("." + file["path"].split(".")[-1], "unknown"))
        print("Tree:", file["tree"])
        print("Code:", file["content"][:60], "...\n")
