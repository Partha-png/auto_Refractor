from src.github.client import Githubclient
from src.refactor.engine import Engine
class pr_monitor:
    def __init__(self,repo,base_branch):
        self.client=Githubclient(repo,base_branch)
        self.engine=Engine(use_groq=True)
    def analyze_open_prs(self):
        """get all the open prs and analyze them"""
        prs=self.client.get_open_pull_requests()
        if not prs:
            print("no open prs found")
            return 
        for pr in prs:
            changed_files=self.client.get_pr_files(pr)
            if not changed_files:
                print(f"no changes in pr{pr.number}")
                continue
            results=[]
            review=[]
            for f in changed_files:
                filename=f.filename
                if not any(filename.endswith(ext) for ext in [".py", ".js", ".cpp", ".java", ".c", ".rb", ".go", ".rs"]):
                     continue         
                try:
                    content,sha=self.client.get_file_content(filename,pr.head.ref)
                    analysis=self.engine.analyze_and_refactor(file_path=filename,code=content)
                    review_result=self.engine.review_code(file_path=filename,code=content)
                    review.append((filename,review_result))
                    results.append((filename,analysis))
                except Exception as e:
                    print(f"error processing file {filename} in pr {pr.number}: {e}")
                    continue 
            final_results={}
            final_results={
                "pr_number":pr.number,
                "reviews":review,
                "analyses":results
            }
            if results and review:
                    comment="code suggestion "
                    self.client.comment_on_pr(pr,comment)
            else:
                 print(f"no suggestions for pr {pr.number}")
            return final_results
if __name__=="__main__":
    repo="microsoft/Web-Dev-For-Beginners"
    base_branch="main"
    monitor=pr_monitor(repo,base_branch)
    monitor.analyze_open_prs()