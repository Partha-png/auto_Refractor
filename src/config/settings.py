"""Application settings using Pydantic for validation."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, Dict, Any
import os


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # GitHub Configuration
    github_token: str = Field(..., env='GITHUB_TOKEN')
    github_webhook_secret: Optional[str] = Field(None, env='GITHUB_WEBHOOK_SECRET')
    github_repo_owner: Optional[str] = Field(None, env='GITHUB_REPO_OWNER')
    github_repo_name: Optional[str] = Field(None, env='GITHUB_REPO_NAME')
    
    # LLM Configuration
    groq_api_key: Optional[str] = Field(None, env='GROQ_API_KEY')
    llm_provider: str = "groq"  # "groq" or "ollama"
    llm_model: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    
    # Webhook Server Configuration
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8000
    webhook_workers: int = 4
    
    # Redis Configuration (for Celery)
    redis_url: str = "redis://localhost:6379/0"
    
    # Scoring Configuration
    enable_bleu: bool = True
    enable_perplexity: bool = False  # Disabled by default (resource intensive)
    enable_code_metrics: bool = True
    scoring_weights: Dict[str, float] = {
        "bleu": 0.3,
        "perplexity": 0.2,
        "complexity": 0.3,
        "maintainability": 0.2,
    }
    
    # Analysis Configuration
    max_function_length: int = 50
    max_function_args: int = 5
    max_nesting_depth: int = 4
    max_cyclomatic_complexity: int = 10
    
    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    
    # File Processing
    max_file_size_mb: int = 5
    supported_extensions: list[str] = [
        ".py", ".js", ".java", ".cpp", ".c", ".go", ".rb", ".rs"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @property
    def use_groq(self) -> bool:
        """Check if using Groq as LLM provider."""
        return self.llm_provider.lower() == "groq"
    
    @property
    def use_ollama(self) -> bool:
        """Check if using Ollama as LLM provider."""
        return self.llm_provider.lower() == "ollama"
    
    def get_scoring_weight(self, metric: str) -> float:
        """Get weight for a specific scoring metric."""
        return self.scoring_weights.get(metric, 0.0)


# Global settings instance
settings = Settings()