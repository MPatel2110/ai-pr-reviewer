"""Parse Python imports and map them to local repository files."""

import ast
from pathlib import Path


def find_local_imports(file_content: str, repo_root: Path, current_file: Path) -> list[Path]:
    """
    Parse the imports in a Python file and return paths to local files they reference.
    
    Args:
        file_content: Source code of the file to analyze.
        repo_root: Path to the cloned repo root.
        current_file: Path of the file being analyzed (used for relative imports).
    
    Returns:
        List of Path objects for local files referenced by imports.
        Skips stdlib and third-party imports. Skips imports that don't resolve.
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        # If the file doesn't parse, we can't extract imports. Skip gracefully.
        return []
    
    resolved_paths: list[Path] = []
    current_dir = current_file.parent
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Handle: from X.Y import Z  or  from .X import Y
            module = node.module or ""
            level = node.level  # 0 = absolute, 1+ = relative ("." x level)
            
            base = current_dir if level > 0 else repo_root
            # For "from ..foo import bar", level=2, walk up (level-1) dirs
            for _ in range(max(0, level - 1)):
                base = base.parent
            
            # Try to resolve module to a .py file or package __init__.py
            if module:
                resolved = _resolve_module(base, module, repo_root)
                if resolved:
                    resolved_paths.append(resolved)
        
        elif isinstance(node, ast.Import):
            # Handle: import X  or  import X.Y
            for alias in node.names:
                resolved = _resolve_module(repo_root, alias.name, repo_root)
                if resolved:
                    resolved_paths.append(resolved)
    
    # Dedupe while preserving order
    seen = set()
    unique = []
    for p in resolved_paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _resolve_module(base: Path, module_name: str, repo_root: Path) -> Path | None:
    """
    Try to resolve a dotted module name to an actual file under base.
    
    Returns the Path if found and inside repo_root, else None.
    """
    parts = module_name.split(".")
    
    # Try as a .py file: foo.bar -> foo/bar.py
    candidate = base.joinpath(*parts).with_suffix(".py")
    if candidate.is_file() and _is_inside(candidate, repo_root):
        return candidate
    
    # Try as a package: foo.bar -> foo/bar/__init__.py
    candidate = base.joinpath(*parts) / "__init__.py"
    if candidate.is_file() and _is_inside(candidate, repo_root):
        return candidate
    
    return None


def _is_inside(path: Path, root: Path) -> bool:
    """Check that path is inside root (prevents accidental traversal outside the repo)."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def select_context_files(
    candidate_paths: list[Path],
    max_files: int = 3,
    max_total_lines: int = 2000,
) -> list[tuple[Path, str]]:
    """
    Choose which related files to include as context, respecting size caps.
    
    Strategy: smallest files first (more variety in context for the same budget).
    
    Args:
        candidate_paths: Local files identified as imports.
        max_files: Hard cap on number of files.
        max_total_lines: Hard cap on total lines across all included files.
    
    Returns:
        List of (path, content) tuples for files to include.
    """
    # Read all candidates with their line counts
    candidates_with_content = []
    for path in candidate_paths:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        line_count = content.count("\n") + 1
        candidates_with_content.append((path, content, line_count))
    
    # Sort smallest first
    candidates_with_content.sort(key=lambda x: x[2])
    
    selected = []
    total_lines = 0
    for path, content, line_count in candidates_with_content:
        if len(selected) >= max_files:
            break
        if total_lines + line_count > max_total_lines:
            continue  # Skip this one but keep looking for smaller files
        selected.append((path, content))
        total_lines += line_count
    
    return selected