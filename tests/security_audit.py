import os
import re
from pathlib import Path

def audit_codebase():
    patterns = [
        (r'AIza[0-9A-Za-z-_]{35}', "Google API Key"),
        (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API Key"),
        (r'(?i)api[_-]?key\s*[:=]\s*["\'](?!super_secret|your_|dev-|dev_)[a-zA-Z0-9_\-]{20,}["\']', "Hardcoded API Key"),
        (r'(?i)password\s*[:=]\s*["\'](?!your_|test|dev)[a-zA-Z0-9_\-]{8,}["\']', "Hardcoded Password")
    ]
    
    findings = []
    base_dir = Path(__file__).resolve().parent.parent

    for root, dirs, files in os.walk(base_dir):
        # Exclude git, venvs, cache
        dirs[:] = [d for d in dirs if d not in [".git", ".venv", "venv", "__pycache__", ".pytest_cache", "instance"]]
        for f in files:
            if f.endswith((".py", ".html", ".txt", ".json", ".md", ".example", ".css", ".js")):
                path = Path(root) / f
                rel_path = path.relative_to(base_dir)
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    for pat, desc in patterns:
                        if re.search(pat, content):
                            findings.append((str(rel_path), desc))
                except Exception as e:
                    print(f"Could not read {rel_path}: {e}")

    print("=== GITHUB SAFETY AUDIT REPORT ===")
    print(f"Scanned directory: {base_dir}")
    print(f"Total potential secret issues found: {len(findings)}")
    for file, issue in findings:
        print(f"  [ALERT] {file}: {issue}")

    # Check gitignore
    gitignore = base_dir / ".gitignore"
    if gitignore.exists():
        gi_content = gitignore.read_text(encoding="utf-8")
        required_ignores = [".env", "instance", "venv", ".venv", "__pycache__", "*.db", "*.sqlite"]
        missing_ignores = [req for req in required_ignores if req not in gi_content]
        if missing_ignores:
            print(f"  [WARNING] .gitignore is missing rules for: {missing_ignores}")
        else:
            print("  [PASS] .gitignore contains all required rules for secrets, DB, and virtualenvs.")
    else:
        print("  [FAIL] .gitignore not found!")

    assert len(findings) == 0, f"Secrets found in codebase: {findings}"
    print("=== AUDIT RESULT: PASS ===")

if __name__ == "__main__":
    audit_codebase()
