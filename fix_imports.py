import os
import re

replacements = {
    # Absolute imports from root modules
    r'\bimport database\b': 'from rdt.shared import database',
    r'\bimport utils\b': 'from rdt.shared import utils',
    r'\bimport credentials\b': 'from rdt.shared import credentials',
    r'\bimport retry_utils\b': 'from rdt.shared import retry_utils',
    r'\bimport analysis\b': 'from rdt.shared import analysis',
    r'\bimport db_init\b': 'from rdt.shared import db_init',
    r'\bimport obsidian_prep\b': 'from rdt.shared import obsidian',
    
    r'\bfrom config_models import\b': 'from rdt.shared.config_models import',
    r'\bfrom rich_utils import\b': 'from rdt.shared.rich_utils import',
    r'\bfrom http_client import\b': 'from rdt.shared.http_client import',
    r'\bfrom scheduler_utils import\b': 'from rdt.shared.scheduler_utils import',
    r'\bfrom credentials import\b': 'from rdt.shared.credentials import',
    r'\bfrom retry_utils import\b': 'from rdt.shared.retry_utils import',
    r'\bfrom analysis import\b': 'from rdt.shared.analysis import',
    r'\bfrom db_init import\b': 'from rdt.shared.db_init import',
    r'\bfrom obsidian_prep import\b': 'from rdt.shared.obsidian import',

    # Stale package name
    r'\bresearch_digest_tui\b': 'rdt.tui',
    
    # Internal TUI imports that were pointed to rdt.tui but should be rdt.shared
    r'\brdt\.tui\.config_models\b': 'rdt.shared.config_models',
    r'\brdt\.tui\.rich_utils\b': 'rdt.shared.rich_utils',
    r'\brdt\.tui\.scheduler_utils\b': 'rdt.shared.scheduler_utils',
    r'\brdt\.adapters\.obsidian\b': 'rdt.shared.obsidian',

    # Relative imports in rdt/tui/services/ pointing to moved files
    r'from \.\.config_models import': 'from rdt.shared.config_models import',
    r'from \.\.rich_utils import': 'from rdt.shared.rich_utils import',
    r'from \.\.scheduler_utils import': 'from rdt.shared.scheduler_utils import',

    # Subprocess path in runner_service.py
    r'repo_root / "rdt" / "digest.py"': 'repo_root / "rdt" / "digest.py"',
}

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, repl in replacements.items():
        new_content = re.sub(pattern, repl, new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

for root, dirs, files in os.walk('.'):
    if '.venv' in dirs: dirs.remove('.venv')
    if '.git' in dirs: dirs.remove('.git')
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            if update_file(filepath):
                print(f"Updated: {filepath}")
