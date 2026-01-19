import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.config.constants import EXTENSION_TO_LANGUAGE, Language


def get_file_extension(file_path: str) -> str:

    return Path(file_path).suffix.lower()


def detect_language(file_path: str) -> Optional[Language]:
    extension = get_file_extension(file_path)
    return EXTENSION_TO_LANGUAGE.get(extension)


def sanitize_branch_name(name: str) -> str:
    """
    Sanitize string for use as Git branch name.
    
    Args:
        name: Raw branch name
    
    Returns:
        Sanitized branch name
    """
    # Replace invalid characters with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_\-/]', '-', name)
    # Remove consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Lowercase for consistency
    return sanitized.lower()


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y%m%d-%H%M%S") -> str:
    """
    Format datetime as string.
    
    Args:
        dt: Datetime object (defaults to now)
        fmt: Format string
    
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Original value
        new_value: New value
    
    Returns:
        Percentage change (positive = increase, negative = decrease)
    """
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    return ((new_value - old_value) / old_value) * 100


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def extract_code_from_markdown(text: str) -> str:
    """
    Extract code from markdown code blocks.
    
    Args:
        text: Markdown text potentially containing code blocks
    
    Returns:
        Extracted code or original text if no code block found
    """
    # Match code blocks with optional language specifier
    pattern = r'```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        # Return the first code block found
        return matches[0].strip()
    
    return text.strip()


def clean_code_output(code: str) -> str:
    """
    Clean LLM-generated code output.
    
    Args:
        code: Raw code output from LLM
    
    Returns:
        Cleaned code
    """
    # Extract from markdown if present
    code = extract_code_from_markdown(code)
    
    # Remove common LLM prefixes/explanations
    prefixes_to_remove = [
        "Here's the refactored code:",
        "Refactored code:",
        "Here is the refactored code:",
        "The refactored code is:",
        "Here's the improved version:",
        "Improved code:",
        "Here's the code:",
        "```python",
        "```",
    ]
    
    for prefix in prefixes_to_remove:
        code = code.replace(prefix, "")
    
    # Remove lines that are just explanations (common LLM patterns)
    lines = code.split('\n')
    cleaned_lines = []
    skip_next = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines at the start
        if not cleaned_lines and not stripped:
            continue
            
        # Skip lines that look like explanations
        if any(stripped.lower().startswith(phrase) for phrase in [
            "this code", "the code", "i've refactored", "i refactored",
            "the refactored", "here's", "here is", "note:", "explanation:"
        ]):
            continue
            
        cleaned_lines.append(line)
    
    # Join and strip
    code = '\n'.join(cleaned_lines).strip()
    
    return code