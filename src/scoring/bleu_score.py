"""BLEU score metric for code similarity."""

import re
from collections import Counter
from typing import List
from src.scoring.metrics import BaseMetric, MetricResult
from src.config.constants import MetricType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BLEUScoreMetric(BaseMetric):
    """
    BLEU (Bilingual Evaluation Understudy) score for code.
    
    Measures similarity between original and refactored code.
    Higher scores indicate more similarity (preservation of structure).
    """
    
    @property
    def metric_type(self) -> MetricType:
        return MetricType.BLEU
    
    @property
    def description(self) -> str:
        return "Measures code similarity (0-100, higher = more similar)"
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """
        Calculate BLEU score for code.
        
        Note: BLEU requires reference text, so this returns a placeholder.
        Use calculate_bleu() for actual comparison.
        """
        return MetricResult(
            metric_type=self.metric_type,
            score=0.0,
            description=self.description,
            details={"note": "Use calculate_bleu() for comparison"}
        )
    
    def calculate_bleu(
        self,
        reference_code: str,
        candidate_code: str,
        language: str,
        max_n: int = 4
    ) -> MetricResult:
        """
        Calculate BLEU score between reference and candidate code.
        
        Args:
            reference_code: Original/reference code
            candidate_code: Refactored/candidate code
            language: Programming language
            max_n: Maximum n-gram size (default: 4)
        
        Returns:
            MetricResult with BLEU score (0-100)
        """
        # Tokenize code into meaningful units
        ref_tokens = self._tokenize_code(reference_code)
        cand_tokens = self._tokenize_code(candidate_code)
        
        if not ref_tokens or not cand_tokens:
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": "Empty code"}
            )
        
        # Calculate n-gram precisions
        precisions = []
        for n in range(1, max_n + 1):
            precision = self._calculate_ngram_precision(
                ref_tokens, cand_tokens, n
            )
            precisions.append(precision)
        
        # Calculate geometric mean of precisions
        if all(p > 0 for p in precisions):
            import math
            bleu = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
        else:
            bleu = 0.0
        
        # Apply brevity penalty
        brevity_penalty = self._calculate_brevity_penalty(
            len(ref_tokens), len(cand_tokens)
        )
        bleu *= brevity_penalty
        
        # Convert to 0-100 scale
        score = bleu * 100
        
        return MetricResult(
            metric_type=self.metric_type,
            score=score,
            description=self.description,
            details={
                "precisions": precisions,
                "brevity_penalty": brevity_penalty,
                "ref_tokens": len(ref_tokens),
                "cand_tokens": len(cand_tokens),
            }
        )
    
    def _tokenize_code(self, code: str) -> List[str]:
        """
        Tokenize code into meaningful units.
        
        Splits on:
        - Whitespace
        - Operators
        - Punctuation
        - Preserves identifiers and keywords
        """
        # Remove comments (simple approach)
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)  # Python comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)  # C-style comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Block comments
        
        # Tokenize on word boundaries, operators, and punctuation
        tokens = re.findall(r'\w+|[^\s\w]', code)
        
        # Filter out empty tokens and normalize
        tokens = [t.lower() for t in tokens if t.strip()]
        
        return tokens
    
    def _calculate_ngram_precision(
        self,
        reference: List[str],
        candidate: List[str],
        n: int
    ) -> float:
        """Calculate n-gram precision."""
        if len(candidate) < n:
            return 0.0
        
        # Generate n-grams
        ref_ngrams = self._get_ngrams(reference, n)
        cand_ngrams = self._get_ngrams(candidate, n)
        
        if not cand_ngrams:
            return 0.0
        
        # Count matches (clipped)
        ref_counts = Counter(ref_ngrams)
        cand_counts = Counter(cand_ngrams)
        
        clipped_counts = {
            ngram: min(count, ref_counts[ngram])
            for ngram, count in cand_counts.items()
        }
        
        numerator = sum(clipped_counts.values())
        denominator = sum(cand_counts.values())
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _get_ngrams(self, tokens: List[str], n: int) -> List[tuple]:
        """Generate n-grams from tokens."""
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def _calculate_brevity_penalty(self, ref_len: int, cand_len: int) -> float:
        """Calculate brevity penalty."""
        if cand_len >= ref_len:
            return 1.0
        
        import math
        return math.exp(1 - ref_len / cand_len) if cand_len > 0 else 0.0
