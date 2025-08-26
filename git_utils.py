# git_utils.py
import subprocess
from pathlib import Path

def _run(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout + res.stderr

def git_clone(repo_url: str, dest: str, branch: str = None):
    cmd = ["git", "clone"]
    if branch:
        cmd += ["-b", branch]
    cmd += [repo_url, dest]
    code, out = _run(cmd)
    if code != 0:
        raise RuntimeError(f"git clone failed: {out}")
    return out

def git_pull(repo_path: str):
    code, out = _run(["git", "pull"], cwd=repo_path)
    if code != 0:
        raise RuntimeError(f"git pull failed: {out}")
    return out

def git_checkout_branch(repo_path: str, branch: str):
    code, out = _run(["git", "checkout", "-B", branch], cwd=repo_path)
    if code != 0:
        raise RuntimeError(f"git checkout failed: {out}")
    return out

def git_commit_and_push(repo_path: str, branch: str, message: str = "Auto commit"):
    repo = Path(repo_path)
    # stage everything
    code, out = _run(["git", "add", "-A"], cwd=repo_path)
    if code != 0:
        raise RuntimeError(f"git add failed: {out}")
    # commit
    code, out = _run(["git", "commit", "-m", message], cwd=repo_path)
    if code != 0:
        # если нет изменений, git commit вернёт код 1 и сообщение "nothing to commit" — обработаем аккуратно
        if "nothing to commit" in out.lower():
            return "Нет изменений для коммита"
        raise RuntimeError(f"git commit failed: {out}")
    # push
    # убедимся, что ветка существует и checkout на нее
    git_checkout_branch(repo_path, branch)
    code, out = _run(["git", "push", "-u", "origin", branch], cwd=repo_path)
    if code != 0:
        raise RuntimeError(f"git push failed: {out}")
    return out
