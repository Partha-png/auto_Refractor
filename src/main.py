import click
from pathlib import Path

from src.refactor.engine import Engine
from src.gh_integration.pr_monitor import pr_monitor
from src.ingestion.parser import parser_code
from src.analysis.linter import Linter
from src.analysis.complexity import Complexity
from src.utils.logger import setup_logging, get_logger
from src.config.settings import settings

# Setup logging
setup_logging(log_level=settings.log_level)
logger = get_logger(__name__)


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path for refactored code')
@click.option('--groq/--ollama', default=True, help='Use Groq (default) or Ollama LLM')
def refactor(file_path, output, groq):
    """Analyze and refactor a code file."""
    logger.info(f"Starting refactoring for: {file_path}")
    
    code = Path(file_path).read_text(encoding='utf-8')
    
    engine = Engine(use_groq=groq)
    result = engine.analyze_and_refactor(file_path, code)
    
    click.echo("\n" + "="*50)
    click.echo("Issues Found:")
    click.echo("="*50)
    click.echo(result['issues'])
    
    click.echo("\n" + "="*50)
    click.echo("Refactored Code:")
    click.echo("="*50)
    click.echo(result['refactored_code'])
    
    if output:
        Path(output).write_text(result['refactored_code'], encoding='utf-8')
        click.echo(f"\n✅ Saved to: {output}")
        logger.info(f"Refactored code saved to: {output}")
    
    logger.info("Refactoring complete")


if __name__ == "__main__":
    refactor()