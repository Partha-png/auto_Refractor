import click
import os
import sys
from src.refactor.engine import Engine
from src.gh_integration.pr_monitor import pr_monitor
from src.ingestion.parser import parser_code
from src.analysis.linter import Linter
from src.analysis.complexity import Complexity

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path())
@click.option('--groq/--ollama', default=True)
def refactor(file_path, output, groq):
    """Analyze and refactor a code file."""
    from pathlib import Path
    code = Path(file_path).read_text(encoding='utf-8')

    engine = Engine(use_groq=groq)
    result = engine.analyze_and_refactor(file_path, code)

    click.echo("\nIssues:")
    click.echo(result['issues'])
    click.echo("\nRefactored Code:")
    click.echo(result['refactored_code'])

    if output:
        Path(output).write_text(result['refactored_code'], encoding='utf-8')
        click.echo(f"\nSaved to: {output}")
if __name__ == "__main__":
    refactor()