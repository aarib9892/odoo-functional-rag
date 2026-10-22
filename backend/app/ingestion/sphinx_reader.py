"""Read verified RST bytes in a controlled temporary Sphinx project."""

from contextlib import contextmanager
from io import StringIO
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from sphinx.application import Sphinx
from sphinx.util.console import nocolor

from app.ingestion.normalized_models import Diagnostic, SourceLocation
from app.ingestion.rst_directives import ExampleBlock, ExampleDirective, icon_role
from app.ingestion.rst_structures import (
    CardBlock, CardDirective, CardsBlock, CardsDirective, PreservingTocTree,
    SourcedTabDirective, SourcedTabsDirective,
)


def parse_diagnostics(text):
    """Keep unrecognized log groups as global diagnostics, never discard them."""
    groups = []
    for line in text.splitlines():
        if re.search(r"(?:WARNING|ERROR|CRITICAL):", line):
            groups.append([line])
        elif groups:
            groups[-1].append(line)
        elif line.strip():
            groups.append([line])
    result = []
    pattern = re.compile(r"^(?:(.*?\.rst)(?::(\d+))?: )?(WARNING|ERROR|CRITICAL): (.*)$")
    for group in groups:
        match = pattern.match(group[0])
        if match:
            path, line, severity, message = match.groups()
            code = re.search(r" \[([^\]]+)\]$", message)
            result.append((Diagnostic("warning" if severity == "WARNING" else "error",
                                      code.group(1) if code else "parser_untyped", "\n".join(group),
                                      SourceLocation(path or "", int(line) if line else None,
                                                     "node" if line else "unknown")), "\n".join(group)))
        else:
            severity = "error" if re.search(r"(?:ERROR|CRITICAL):", group[0]) else "warning"
            result.append((Diagnostic(severity, "parser_unclassified", "\n".join(group),
                                      SourceLocation("", None, "unknown")), "\n".join(group)))
    return result


@contextmanager
def read_corpus(files):
    """Yield app, stored trees, source root and a stable diagnostics string."""
    diagnostics = StringIO()
    nocolor()
    with TemporaryDirectory(prefix="m22-corpus-") as directory:
        work = Path(directory)
        source = work / "source"
        for relative, data in sorted(files.items()):
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        root = sorted(files)[0][:-4]
        app = Sphinx(srcdir=str(source), confdir=None, outdir=str(work / "build"),
                     doctreedir=str(work / "doctrees"), buildername="dummy",
                     confoverrides={"project": "Odoo normalized corpus", "root_doc": root,
                                    "extensions": ["sphinx_tabs.tabs"],
                                    "sphinx_tabs_valid_builders": ["dummy"],
                                    "nitpicky": True, "keep_warnings": True, "smartquotes": False},
                     status=StringIO(), warning=diagnostics, freshenv=True)
        for node in (ExampleBlock, CardBlock, CardsBlock):
            app.add_node(node)
        for name, directive in {"example": ExampleDirective, "cards": CardsDirective,
                                "card": CardDirective, "toctree": PreservingTocTree,
                                "tabs": SourcedTabsDirective, "tab": SourcedTabDirective}.items():
            app.add_directive(name, directive, override=True)
        app.add_role("icon", icon_role)
        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False
        app.build(force_all=True)
        trees = {relative[:-4]: app.env.get_doctree(relative[:-4]) for relative in sorted(files)}
        logs = diagnostics.getvalue().replace(str(source) + "/", "")
        yield app, trees, source, logs
