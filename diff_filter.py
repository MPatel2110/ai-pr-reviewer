from unidiff import PatchSet


# File extensions we know how to review. Day 3: Python only.
REVIEWABLE_EXTENSIONS = {".py"}

# Filename patterns to always skip (lockfiles, generated files).
SKIP_FILENAMES = {
    "poetry.lock",
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "Pipfile.lock",
    "uv.lock",
}

# Path segments that indicate generated or vendored code.
SKIP_PATH_SEGMENTS = {
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".next",
    "vendor",
}


def should_review_file(file_path: str) -> bool:
    """Return True if this file should be sent to the reviewer."""
    # Reject by filename
    filename = file_path.rsplit("/", 1)[-1]
    if filename in SKIP_FILENAMES:
        return False
    
    # Reject by path segment
    path_segments = set(file_path.split("/"))
    if path_segments & SKIP_PATH_SEGMENTS:
        return False
    
    # Reject minified files
    if filename.endswith((".min.js", ".min.css")):
        return False
    
    # Accept only if extension matches our reviewable list
    for ext in REVIEWABLE_EXTENSIONS:
        if filename.endswith(ext):
            return True
    
    return False


def parse_and_filter_diff(raw_diff: str) -> list[tuple[str, str]]:
    """
    Parse a unified diff and return only the files we should review.
    
    Args:
        raw_diff: Unified-diff-format string from GitHub.
    
    Returns:
        List of (file_path, file_diff_text) tuples for reviewable files.
        Empty list if nothing in the diff should be reviewed.
    """
    patch_set = PatchSet(raw_diff)
    results = []
    
    for patched_file in patch_set:
        # unidiff exposes the new file path via .path; for deletions
        # this would be the old path, which we don't need to review.
        if patched_file.is_removed_file:
            continue
        if patched_file.is_binary_file:
            continue
        
        file_path = patched_file.path
        if not should_review_file(file_path):
            continue
        
        # str(patched_file) reconstructs just this file's section of the diff
        results.append((file_path, str(patched_file)))
    
    return results