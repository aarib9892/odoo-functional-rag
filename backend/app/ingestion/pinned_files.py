from pathlib import Path, PurePosixPath
import re
import subprocess


def read_pinned_file(
    repository: Path,
    commit: str,
    source_path: str,
) -> bytes:
    """Read a regular file from a full SHA-1 commit, using its Git blob."""
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("Expected a full lowercase SHA-1 commit ID")

    if not isinstance(source_path, str):
        raise ValueError("Expected a repository-relative path string")

    path = PurePosixPath(source_path)
    if (
        not path.parts
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != source_path
        or "\\" in source_path
        or "\0" in source_path
    ):
        raise ValueError("Expected a canonical repository-relative POSIX path")

    command = [
        "git",
        "--no-replace-objects",
        "--literal-pathspecs",
        "-C",
        str(repository.resolve()),
    ]

    def git(*arguments):
        return subprocess.run(
            [*command, *arguments],
            check=True,
            capture_output=True,
            timeout=10,
        ).stdout

    if git("cat-file", "-t", commit).strip() != b"commit":
        raise ValueError("Expected a commit object")

    entries = [
        entry
        for entry in git(
            "ls-tree",
            "--full-tree",
            "-z",
            commit,
            "--",
            source_path,
        ).split(b"\0")
        if entry
    ]
    if not entries:
        raise FileNotFoundError(source_path)
    if len(entries) != 1:
        raise ValueError("Expected exactly one source file")

    description, returned_path = entries[0].split(b"\t", 1)
    mode, kind, object_id = description.split()

    if returned_path != source_path.encode("utf-8"):
        raise ValueError("Git returned a different source path")

    if kind != b"blob" or mode not in {b"100644", b"100755"}:
        raise ValueError(
            "Expected a regular file; links and directories are unsupported"
        )

    return git("cat-file", "blob", object_id.decode("ascii"))
