from pathlib import PurePosixPath


def select_scope(
    paths: list[str],
    scope: dict[str, list[str]],
) -> dict[str, str]:
    """Return selected repository-relative paths mapped to applications."""

    if not scope:
        raise ValueError("Corpus scope must not be empty.")

    selected: dict[str, str] = {}

    for application, allowed_paths in scope.items():
        if not allowed_paths:
            raise ValueError(f"No allowed paths configured for {application!r}.")

        for allowed_path in allowed_paths:
            root = PurePosixPath(allowed_path)

            if ".." in root.parts or not root.is_relative_to(
                PurePosixPath("content/applications")
            ):
                raise ValueError(
                    f"Scope path must be inside content/applications: "
                    f"{allowed_path}"
                )

            matches = [
                path
                for path in paths
                if (PurePosixPath(path) == root or root in PurePosixPath(path).parents)
            ]

            if not matches:
                raise ValueError(
                    f"Scope path matched no tracked RST files: " f"{allowed_path}"
                )

            for path in matches:
                existing_application = selected.get(path)

                if (
                    existing_application is not None
                    and existing_application != application
                ):
                    raise ValueError(
                        f"File belongs to multiple configured applications: " f"{path}"
                    )

                selected[path] = application

    return dict(sorted(selected.items()))
