import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileRecord:
    source_path: str
    application: str
    size_bytes: int
    sha256: str


def build_file_records(
    repository_root: Path,
    selected: dict[str, str],
) -> list[FileRecord]:
    """Read selected files and describe their raw contents."""

    repository_root = repository_root.resolve(strict=True)
    records: list[FileRecord] = []

    for source_path, application in sorted(selected.items()):
        local_path = repository_root / source_path

        if local_path.is_symlink():
            raise ValueError(
                f"Selected source must not be a symbolic link: {source_path}"
            )

        resolved_path = local_path.resolve(strict=True)

        if not resolved_path.is_relative_to(repository_root):
            raise ValueError(
                f"Selected source is outside the repository: {source_path}"
            )

        content = resolved_path.read_bytes()

        record = FileRecord(
            source_path=source_path,
            application=application,
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )

        records.append(record)

    return records
