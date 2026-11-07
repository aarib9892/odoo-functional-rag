import hashlib
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess

from docutils import statemachine
from docutils.parsers.rst import Directive

from app.ingestion.pinned_files import read_pinned_file

INCLUDE_POLICY_VERSION = "m3-pinned-relative-utf8-0.1"
MAX_INCLUDE_REQUESTS = 64


class IncludeSources:
    def __init__(self, repository, commit, source_root, files):
        self.repository = Path(repository).resolve()
        self.commit = commit
        self.root = Path(source_root).resolve()
        self.files = dict(files)
        self.dependencies = {path: {} for path in files}
        self.requests = {path: 0 for path in files}

        for path, data in self.files.items():
            if read_pinned_file(self.repository, commit, path) != data:
                raise ValueError("Selected source differs from its pinned Git bytes")

    def stage(self, owner, including_source, argument):
        if owner not in self.dependencies:
            raise ValueError("Include owner is outside the selected corpus")

        source = Path(including_source)
        if not source.is_absolute():
            source = self.root / source

        including = source.resolve().relative_to(self.root).as_posix()
        if including != owner and including not in self.dependencies[owner]:
            raise ValueError("Including file is not a recorded dependency of this page")

        if (
            not argument
            or PurePosixPath(argument).is_absolute()
            or "\\" in argument
            or "\0" in argument
            or argument.startswith("<")
            or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", argument)
        ):
            raise ValueError("Only relative repository include paths are supported")

        relative = posixpath.normpath(
            posixpath.join(
                PurePosixPath(including).parent.as_posix(),
                argument,
            )
        )
        if relative == ".." or relative.startswith("../") or relative == ".":
            raise ValueError("Include path escapes the repository")

        self.requests[owner] += 1
        if self.requests[owner] > MAX_INCLUDE_REQUESTS:
            raise ValueError("Include request limit exceeded")

        if relative not in self.files:
            self.files[relative] = read_pinned_file(
                self.repository, self.commit, relative
            )

        data = self.files[relative]
        target = (self.root / relative).resolve()

        if not target.is_relative_to(self.root):
            raise ValueError("Include target escapes the staging directory")

        if target.exists():
            if not target.is_file() or target.read_bytes() != data:
                raise ValueError("Staged include differs from pinned bytes")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        self.dependencies[owner][relative] = {
            "source_path": relative,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
        }
        return target, data

    def records(self, owner):
        return tuple(
            dict(record) for _, record in sorted(self.dependencies[owner].items())
        )


class PinnedInclude(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        store = getattr(env, "pinned_include_sources", None)

        if store is None:
            raise self.error("Pinned includes are not configured")

        source, _ = self.state_machine.get_source_and_line(self.lineno)

        try:
            target, data = store.stage(
                env.docname + ".rst",
                source,
                self.arguments[0],
            )
            text = data.decode("utf-8")
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            raise self.error(f"Pinned include failed: {error}") from error

        env.note_dependency(str(target))
        lines = statemachine.string2lines(
            text,
            tab_width=self.state.document.settings.tab_width,
            convert_whitespace=True,
        )
        self.state_machine.insert_input([*lines, ""], str(target))
        return []
