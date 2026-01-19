from src.webhook.models import WebhookEvent
from src.refactor.engine import Engine
from src.gh_integration.client import Githubclient
from src.gh_integration.pr_creator import create_refactored_pr
from src.utils.logger import get_logger
from src.config.constants import EXTENSION_TO_LANGUAGE

logger = get_logger(__name__)


async def handle_pull_request_opened(event: WebhookEvent) -> dict:
    """
    Handle new PR creation event.
    
    Args:
        event: GitHub webhook event
        
    Returns:
        dict: Processing results
    """
    pr = event.pull_request
    repo = event.repository
    
    logger.info(f"Processing PR #{pr.number}: {pr.title}")
    
    # Skip draft PRs
    if pr.draft:
        logger.info(f"Skipping draft PR #{pr.number}")
        return {
            "status": "skipped",
            "reason": "draft PR",
            "pr_number": pr.number
        }
    
    # Skip PRs created by the bot (prevent infinite loop)
    if pr.title.startswith("Refactored:") or "Auto-Refractor" in pr.title or pr.title.startswith("🤖"):
        logger.info(f"Skipping bot-created PR #{pr.number}")
        return {
            "status": "skipped",
            "reason": "bot-created PR",
            "pr_number": pr.number
        }
    
    try:
        # Initialize GitHub client
        client = Githubclient(repo.full_name, repo.default_branch)
        
        # Get PR object from GitHub
        github_pr = client.repo.get_pull(pr.number)
        
        # Get changed files
        files = client.get_pr_files(github_pr)
        
        if not files:
            logger.warning(f"No files found in PR #{pr.number}")
            return {
                "status": "skipped",
                "reason": "no files",
                "pr_number": pr.number
            }
        
        # Initialize refactoring engine
        engine = Engine(use_groq=True)
        
        # Process each file
        results = []
        supported_extensions = list(EXTENSION_TO_LANGUAGE.keys())
        
        for file in files:
            filename = file.filename
            
            # Only process supported languages
            if not any(filename.endswith(ext) for ext in supported_extensions):
                logger.debug(f"Skipping unsupported file: {filename}")
                continue
            
            try:
                # Get file content
                content, sha = client.get_file_content(filename, pr.head.ref)
                
                # Analyze and refactor
                logger.info(f"Refactoring file: {filename}")
                result = engine.analyze_and_refactor(filename, content)
                
                results.append({
                    "filename": filename,
                    "content": result.get("refactored_code", ""),  # Add content for PR creator
                    "sha": sha,
                    "issues": result.get("issues", ""),
                    "refactored_code": result.get("refactored_code", ""),
                    "scores": result.get("scores"),  # Add scores
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                results.append({
                    "filename": filename,
                    "status": "error",
                    "error": str(e)
                })
        
        # Extract scores from first successful result
        original_scores = None
        refactored_scores = None
        for result in results:
            if result["status"] == "success" and result.get("scores"):
                original_scores = result["scores"].get("original")
                refactored_scores = result["scores"].get("refactored")
                break
        
        # Create refactored PR with scores
        try:
            if results and any(r["status"] == "success" for r in results):
                logger.info(f"Creating refactored PR for original PR #{pr.number}")
                
                refactored_pr = await create_refactored_pr(
                    client=client,
                    original_pr_number=pr.number,
                    original_pr_title=pr.title,
                    refactored_files=results,
                    original_scores=original_scores,
                    refactored_scores=refactored_scores
                )
                
                logger.info(f"Successfully created refactored PR #{refactored_pr.number}")
                
                # Comment on original PR with link to refactored PR
                comment = f"""**Auto-Refractor Analysis Complete**

Created refactored PR: #{refactored_pr.number}

**Files processed:** {len([r for r in results if r['status'] == 'success'])}/{len(results)}

View the refactored code and quality scores in PR #{refactored_pr.number}
"""
                client.comment_on_pr(github_pr, comment)
                
        except Exception as e:
            logger.error(f"Error creating refactored PR: {e}")
            # Still comment on original PR even if PR creation fails
            successful = len([r for r in results if r["status"] == "success"])
            comment = f"""**Auto-Refractor Analysis Complete**

Processed {successful}/{len(results)} files successfully

Note: Failed to create refactored PR. Error: {str(e)}
"""
            client.comment_on_pr(github_pr, comment)
        
        logger.info(f"Completed processing PR #{pr.number}: {len(results)} files processed")
        
        return {
            "status": "success",
            "pr_number": pr.number,
            "files_processed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error handling PR #{pr.number}: {e}")
        return {
            "status": "error",
            "pr_number": pr.number,
            "error": str(e)
        }


async def handle_pull_request_synchronized(event: WebhookEvent) -> dict:
    """
    Handle PR update event (new commits pushed).
    
    Args:
        event: GitHub webhook event
        
    Returns:
        dict: Processing results
    """
    pr = event.pull_request
    
    logger.info(f"PR #{pr.number} synchronized (updated)")
    
    # For now, treat synchronized events same as opened
    # In future, could check if we already processed this PR
    return await handle_pull_request_opened(event)


async def handle_pull_request_closed(event: WebhookEvent) -> dict:
    """
    Handle PR closed event.
    
    Args:
        event: GitHub webhook event
        
    Returns:
        dict: Processing results
    """
    pr = event.pull_request
    
    logger.info(f"PR #{pr.number} closed")
    
    # Could clean up any temporary data here
    return {
        "status": "acknowledged",
        "pr_number": pr.number,
        "action": "closed"
    }
