from github import Github
import os
from dotenv import load_dotenv
class Githubclient:
    def __init__(self,repo:str,base_branch:str="main"):
        """Github client wrapper for pull req ,file,commit"""
        load_dotenv()
        token=os.getenv('github_token')
        if not token:
            raise ValueError("GitHub token not found in environment variables.")
        self.repo_name=repo
        self.base_branch=base_branch
        self.client=Github(token)
        self.repo=self.client.get_repo(repo)
    def get_open_pull_requests(self):

        """fetch all open pull requests"""
        return [pr for pr in self.repo.get_pulls(state="open")]
    def get_pr_files(self,pr):
            """get changed files in a pr"""
            return [f for f in  pr.get_files()] 
    def get_file_content(self,path:str,ref:str):
            """get file content of the pull request"""
            file_content=self.repo.get_contents(path,ref=ref)
            return file_content.decoded_content.decode("utf-8"),file_content.sha
    def comment_on_pr(self,pr,comment:str):
            """comment on a pull request"""
            pr.create_issue_comment(comment)
            return f"Commented on PR #{pr.number}"
    def change_branch(self,base_branch:str,new_branch:str):
         """create a new branch"""
         source=self.repo.get_branch(base_branch)
         self.repo.create_git_ref(
              ref=f"refs/heads/{new_branch}",
              sha=source.commit.sha
         )
         return f"created branch {new_branch}from{base_branch}"
    def commit_and_push(self,branch:str,path:str,content:str,commit_message:str,sha:str):
            """commit and push changes to a branch"""
            try:
                existing=self.repo.get_contents(path,ref=branch)
                self.repo.update_file(path,commit_message,content,existing.sha,branch=branch)
                return f"Committed and pushed changes to {branch}"
            except Exception as e:
                self.repo.create_file(path, commit_message, content, branch=branch)
                return f"Created {path} in {branch}"
    def create_pull_request(self,branch:str,title:str,body:str):
         """open a pr"""
         pr=self.repo.create_pull(
              title=title,
              body=body,
              head=branch,
              base=self.base_branch
         )
         return pr