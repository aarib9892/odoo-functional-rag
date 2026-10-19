import subprocess
from pathlib import Path


def discover_rst_files(repository_root: Path) -> list[str]:
    """Return sorted, repository-relative tracked RST paths."""

    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "ls-files",
            "-z",
            "--",
            "content/applications/",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    paths = result.stdout.split("\0")

    rst_paths = [path for path in paths if path and path.endswith(".rst")]

    return sorted(rst_paths)
