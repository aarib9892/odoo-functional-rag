import subprocess
from pathlib import Path


def _run_git(repository_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            *arguments,
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    return result.stdout


def get_clean_commit(repository_root: Path) -> str:
    """Validate the repository root and cleanliness, then return HEAD."""

    repository_root = repository_root.resolve(strict=True)

    if not repository_root.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {repository_root}"
        )

    actual_root = Path(
        _run_git(repository_root, "rev-parse", "--show-toplevel").strip()
    ).resolve()

    if actual_root != repository_root:
        raise ValueError(
            f"Expected a repository root: {repository_root}. "
            f"Git reported: {actual_root}"
        )

    status = _run_git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    if status:
        raise ValueError(
            "The documentation checkout has local changes. "
            "Use a clean checkout before creating its inventory."
        )

    return _run_git(repository_root, "rev-parse", "HEAD").strip()
