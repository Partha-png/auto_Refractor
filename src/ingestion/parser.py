from tree_sitter import Parser
from src.ingestion.loader import load_files_from_directory
from tree_sitter_languages import get_parser
from src.ingestion.loader import EXTENSION_LANGUAGE_MAP
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
            parser = get_parser(lang)
            file["tree"] = parser.parse(content.encode("utf-8"))
        except Exception as e:
            print(f"Could not parse {path} ({lang}): {e}")
            file["tree"] = None

    return results

if __name__ == "__main__":
    test_files = ["sample.py", "sample.js", "sample.java", "sample.cpp"]
    parsed = parser_code(test_files)
    for file in parsed:
        print("File:", file["path"])
        print("Detected:", EXTENSION_LANGUAGE_MAP.get("." + file["path"].split(".")[-1], "unknown"))
        print("Tree:", file["tree"])
        print("Code:", file["content"][:60], "...\n")
