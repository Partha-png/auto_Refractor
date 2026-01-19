"""Input validation utilities."""

from pathlib import Path
from typing import Optional
from src.config.settings import settings
from src.config.constants import EXTENSION_TO_LANGUAGE, Language


def validate_file_size(file_path: str, max_size_mb: Optional[int] = None) -> bool:
    """
    Validate file size is within limits.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum size in MB (defaults to settings)
    
    Returns:
        True if valid, False otherwise
    """
    max_size = max_size_mb or settings.max_file_size_mb
    max_bytes = max_size * 1024 * 1024
    
    try:
        file_size = Path(file_path).stat().st_size
        return file_size <= max_bytes
    except (OSError, FileNotFoundError):
        return False


def validate_file_extension(file_path: str) -> bool:
    """
    Validate file has a supported extension.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if extension is supported, False otherwise
    """
    extension = Path(file_path).suffix.lower()
    return extension in settings.supported_extensions


def is_supported_language(file_path: str) -> bool:
    """
    Check if file language is supported.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if language is supported, False otherwise
    """
    extension = Path(file_path).suffix.lower()
    return extension in EXTENSION_TO_LANGUAGE


def validate_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validate GitHub webhook signature.
    
    Args:
        payload: Request payload bytes
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret
    
    Returns:
        True if signature is valid, False otherwise
    """
    import hmac
    import hashlib
    
    if not signature or not signature.startswith("sha256="):
        return False
    
    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (timing-safe)
    received_signature = signature.split("=")[1]
    return hmac.compare_digest(expected_signature, received_signature)


def validate_code_content(code: str, min_length: int = 10) -> bool:
    """
    Validate code content is not empty or too short.
    
    Args:
        code: Code content
        min_length: Minimum length in characters
    
    Returns:
        True if valid, False otherwise
    """
    if not code or not code.strip():
        return False
    return len(code.strip()) >= min_length


def validate_pr_number(pr_number: int) -> bool:
    """
    Validate PR number is positive integer.
    
    Args:
        pr_number: PR number
    
    Returns:
        True if valid, False otherwise
    """
    return isinstance(pr_number, int) and pr_number > 0


def validate_branch_name(branch_name: str) -> bool:
    """
    Validate Git branch name follows conventions.
    
    Args:
        branch_name: Branch name
    
    Returns:
        True if valid, False otherwise
    """
    if not branch_name or not branch_name.strip():
        return False
    
    # Check for invalid characters
    invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
    for char in invalid_chars:
        if char in branch_name:
            return False
    
    # Cannot start or end with slash or dot
    if branch_name.startswith(("/", ".")) or branch_name.endswith(("/", ".")):
        return False
    
    return True