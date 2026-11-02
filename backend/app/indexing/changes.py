from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceChanges:
    added: tuple[str, ...]
    changed: tuple[str, ...]
    unchanged: tuple[str, ...]
    removed: tuple[str, ...]


def plan_source_changes(
    previous: Mapping[str, str],
    current: Mapping[str, str],
) -> SourceChanges:
    """Compare complete source inventories: source path -> SHA-256."""
    old_paths = set(previous)
    new_paths = set(current)
    shared = old_paths & new_paths

    return SourceChanges(
        added=tuple(sorted(new_paths - old_paths)),
        changed=tuple(
            sorted(path for path in shared if previous[path] != current[path])
        ),
        unchanged=tuple(
            sorted(path for path in shared if previous[path] == current[path])
        ),
        removed=tuple(sorted(old_paths - new_paths)),
    )
