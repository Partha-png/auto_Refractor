"""
Report generator for formatting code quality scores and comparisons.
"""
from typing import Dict, Optional, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


def format_score_report(
    original_scores: Dict[str, float],
    refactored_scores: Dict[str, float],
    filename: str
) -> str:
    """
    Format score comparison as markdown report.
    
    Args:
        original_scores: Scores before refactoring
        refactored_scores: Scores after refactoring
        filename: Name of the file
        
    Returns:
        str: Markdown formatted report
    """
    # Calculate overall improvement
    orig_overall = original_scores.get("overall_score", 0)
    refact_overall = refactored_scores.get("overall_score", 0)
    improvement = refact_overall - orig_overall
    
    report = f"""## 📊 Quality Report: `{filename}`

### Overall Score
- **Before:** {orig_overall:.1f}/100
- **After:** {refact_overall:.1f}/100
- **Improvement:** {improvement:+.1f} points

### Detailed Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
"""
    
    # Add each metric
    metrics = [
        ("BLEU Score", "bleu_score"),
        ("Code Complexity", "complexity_score"),
        ("Maintainability", "maintainability_score")
    ]
    
    for metric_name, metric_key in metrics:
        orig = original_scores.get(metric_key, 0)
        refact = refactored_scores.get(metric_key, 0)
        diff = refact - orig
        
        if diff > 0:
            change = f"+{diff:.1f} ✅"
        elif diff < 0:
            change = f"{diff:.1f} ⚠️"
        else:
            change = "0.0 ➖"
        
        report += f"| {metric_name} | {orig:.1f} | {refact:.1f} | {change} |\n"
    
    return report


def generate_comparison_table(
    original_scores: Dict[str, float],
    refactored_scores: Dict[str, float]
) -> str:
    """
    Generate simple comparison table.
    
    Args:
        original_scores: Scores before refactoring
        refactored_scores: Scores after refactoring
        
    Returns:
        str: Markdown table
    """
    table = "| Metric | Before | After | Change |\n"
    table += "|--------|--------|-------|--------|\n"
    
    metrics = {
        "Overall": "overall_score",
        "BLEU": "bleu_score",
        "Complexity": "complexity_score",
        "Maintainability": "maintainability_score"
    }
    
    for name, key in metrics.items():
        orig = original_scores.get(key, 0)
        refact = refactored_scores.get(key, 0)
        diff = refact - orig
        
        change = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
        table += f"| {name} | {orig:.1f} | {refact:.1f} | {change} |\n"
    
    return table


def format_summary(results: list) -> str:
    """
    Format summary of multiple file results.
    
    Args:
        results: List of file results with scores
        
    Returns:
        str: Markdown formatted summary
    """
    if not results:
        return "No files processed."
    
    total_improvement = 0
    files_improved = 0
    
    summary = "## 📊 Refactoring Summary\n\n"
    
    for result in results:
        if "scores" in result and result["scores"]:
            scores = result["scores"]
            orig = scores.get("original", {}).get("overall_score", 0)
            refact = scores.get("refactored", {}).get("overall_score", 0)
            improvement = refact - orig
            
            if improvement > 0:
                files_improved += 1
                total_improvement += improvement
    
    avg_improvement = total_improvement / len(results) if results else 0
    
    summary += f"- **Files Processed:** {len(results)}\n"
    summary += f"- **Files Improved:** {files_improved}\n"
    summary += f"- **Average Improvement:** {avg_improvement:+.1f} points\n\n"
    
    summary += "### Files\n\n"
    for result in results:
        filename = result.get("filename", "unknown")
        status = result.get("status", "unknown")
        
        if status == "success" and "scores" in result:
            scores = result["scores"]
            orig = scores.get("original", {}).get("overall_score", 0)
            refact = scores.get("refactored", {}).get("overall_score", 0)
            improvement = refact - orig
            
            emoji = "✅" if improvement > 0 else "➖"
            summary += f"- {emoji} `{filename}` ({improvement:+.1f})\n"
        else:
            summary += f"- ❌ `{filename}` (failed)\n"
    
    return summary
