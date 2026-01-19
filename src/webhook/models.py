from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class User(BaseModel):
    """GitHub user model."""
    login: str
    id: int
    type: str

class Repository(BaseModel):
    """GitHub repository model."""
    id: int
    name: str
    full_name: str
    private: bool
    owner: User
    default_branch: str = "main"


class Branch(BaseModel):
    """Git branch reference."""
    ref: str
    sha: str
    repo: Repository


class PullRequest(BaseModel):
    """GitHub pull request model."""
    id: int
    number: int
    title: str
    state: str
    draft: bool
    user: User
    head: Branch
    base: Branch
    body: Optional[str] = None
    created_at: str
    updated_at: str


class WebhookEvent(BaseModel):
    """GitHub webhook event model."""
    action: str
    number: int
    pull_request: PullRequest
    repository: Repository
    sender: User
    
    class Config:
        """Pydantic config."""
        extra = "allow"  # Allow extra fields from GitHub
