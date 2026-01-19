"""Application constants and enums."""

from enum import Enum
from typing import Dict, List


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUBY = "ruby"
    RUST = "rust"


class MetricType(str, Enum):
    """Types of scoring metrics."""
    BLEU = "bleu"
    PERPLEXITY = "perplexity"
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    MAINTAINABILITY_INDEX = "maintainability_index"
    LINES_OF_CODE = "lines_of_code"
    HALSTEAD_VOLUME = "halstead_volume"


class PRLabel(str, Enum):
    """GitHub PR labels."""
    REFACTORED = "refactored"
    AUTO_GENERATED = "auto-generated"
    NEEDS_REVIEW = "needs-review"
    QUALITY_IMPROVED = "quality-improved"


# Language to file extension mapping
LANGUAGE_EXTENSIONS: Dict[Language, List[str]] = {
    Language.PYTHON: [".py"],
    Language.JAVASCRIPT: [".js", ".jsx", ".ts", ".tsx"],
    Language.JAVA: [".java"],
    Language.CPP: [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    Language.C: [".c", ".h"],
    Language.GO: [".go"],
    Language.RUBY: [".rb"],
    Language.RUST: [".rs"],
}

# Extension to language mapping (reverse lookup)
EXTENSION_TO_LANGUAGE: Dict[str, Language] = {
    ext: lang
    for lang, exts in LANGUAGE_EXTENSIONS.items()
    for ext in exts
}

# Supported languages list
SUPPORTED_LANGUAGES = list(Language)

# Default scoring weights
SCORING_WEIGHTS = {
    MetricType.BLEU: 0.3,
    MetricType.PERPLEXITY: 0.2,
    MetricType.CYCLOMATIC_COMPLEXITY: 0.3,
    MetricType.MAINTAINABILITY_INDEX: 0.2,
}

# PR configuration
BRANCH_PREFIX = "refactor"
PR_LABELS = [PRLabel.REFACTORED, PRLabel.AUTO_GENERATED]

# Metric descriptions
METRIC_DESCRIPTIONS = {
    MetricType.BLEU: "Measures similarity between original and refactored code (0-100, higher is better)",
    MetricType.PERPLEXITY: "Measures code naturalness and readability (lower is better)",
    MetricType.CYCLOMATIC_COMPLEXITY: "Measures code complexity through control flow (lower is better)",
    MetricType.MAINTAINABILITY_INDEX: "Overall maintainability score (0-100, higher is better)",
    MetricType.LINES_OF_CODE: "Total lines of code (lower is better for same functionality)",
    MetricType.HALSTEAD_VOLUME: "Program vocabulary and length metric (lower is better)",
}

# Scoring thresholds
SCORE_THRESHOLDS = {
    "excellent": 85,
    "good": 70,
    "fair": 50,
    "poor": 0,
}

# GitHub webhook events to handle
HANDLED_WEBHOOK_EVENTS = [
    "pull_request.opened",
    "pull_request.synchronize",
    "pull_request.reopened",
]

# Ignored PR conditions
IGNORE_PR_CONDITIONS = {
    "draft": True,
    "labels_to_ignore": ["wip", "do-not-refactor"],
}