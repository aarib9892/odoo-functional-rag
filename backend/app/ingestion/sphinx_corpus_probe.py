"""Final M2.1 Sphinx spike over the frozen, manifest-listed 30-page slice.

Checks manifest file sizes/hashes; this probe does not recheck Git cleanliness.
It writes experimental doctrees/diagnostics, not normalized production records.
"""

import hashlib
import json
import re
from collections import Counter
from importlib.metadata import version
from io import StringIO
from pathlib import Path, PurePosixPath
from shutil import copyfile
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.util.console import nocolor

from app.ingestion.docutils_adapter import (
    CardBlock,
    CardDirective,
    CardsBlock,
    CardsDirective,
)
from app.ingestion.rst_directives import ExampleBlock, ExampleDirective, icon_role

FINGERPRINT = "d359162bcd1c4785ae1f339d9b972d1bad90102e5351dc33abaebea046110d1d"
BASE = "content/applications/inventory_and_mrp/inventory/shipping_receiving/"
FLOWS = BASE + "daily_operations"
RESERVATIONS = BASE + "reservation_methods"
FLOW_ENTRIES = [
    "daily_operations/" + name
    for name in (
        "use_routes",
        "receipts_delivery_one_step",
        "receipts_delivery_two_steps",
        "receipts_three_steps",
        "delivery_three_steps",
        "putaway",
        "storage_category",
        "owned_stock",
        "dropshipping",
    )
]
CARD_TARGETS = [
    ("Putaway rules", "daily_operations/putaway"),
    ("Storage categories", "daily_operations/storage_category"),
    ("Consignment", "daily_operations/owned_stock"),
    ("Dropshipping", "daily_operations/dropshipping"),
    ("Picking methods", "picking_methods"),
    ("Removal strategies", "removal_strategies"),
    ("Routes", "daily_operations/use_routes"),
]


class PreservingTocTree(TocTree):
    """Keep source entries even when Sphinx filters unstaged destinations."""

    def run(self):
        result = super().run()
        for wrapper in result:
            for node in wrapper.findall(addnodes.toctree):
                node["original_entries"] = [
                    line.strip() for line in self.content if line.strip()
                ]
        return result


def clean(text):
    return " ".join(text.split())


def verify_files(repository, manifest):
    assert (
        manifest["inventory_fingerprint"] == FINGERPRINT
    ), "Use the frozen M1.2 manifest."
    canonical = json.dumps(manifest["inventory"], sort_keys=True, separators=(",", ":"))
    assert (
        hashlib.sha256(canonical.encode("utf-8")).hexdigest() == FINGERPRINT
    ), "Manifest payload changed."
    records = manifest["inventory"]["files"]
    assert len(records) == 30, "This probe expects the accepted 30-page slice."
    paths = []
    for record in records:
        relative = PurePosixPath(record["source_path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert relative.suffix == ".rst"
        path = repository / relative
        data = path.read_bytes()
        assert len(data) == record["size_bytes"], f"Size mismatch: {relative}"
        assert (
            hashlib.sha256(data).hexdigest() == record["sha256"]
        ), f"Hash mismatch: {relative}"
        paths.append(Path(relative))
    assert len(set(paths)) == len(paths), "Duplicate manifest paths."
    return sorted(paths)


def main():
    repository = Path("../sources/odoo-documentation").resolve()
    manifest = json.loads(
        Path("../data/manifests/odoo19-corpus.json").read_text(encoding="utf-8")
    )
    paths = verify_files(repository, manifest)
    output = Path("../data/experiments/m2/sphinx_corpus_probe").resolve()
    output.mkdir(parents=True, exist_ok=True)
    diagnostics = StringIO()
    nocolor()

    with TemporaryDirectory(prefix="m2-corpus-") as directory:
        work = Path(directory)
        source = work / "source"
        for path in paths:
            target = source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            copyfile(repository / path, target)
        app = Sphinx(
            srcdir=str(source),
            confdir=None,
            outdir=str(work / "build"),
            doctreedir=str(work / "doctrees"),
            buildername="dummy",
            confoverrides={
                "project": "M2 corpus probe",
                "root_doc": FLOWS,
                "extensions": ["sphinx_tabs.tabs"],
                "sphinx_tabs_valid_builders": ["dummy"],
                "nitpicky": True,
                "keep_warnings": True,
            },
            status=StringIO(),
            warning=diagnostics,
            freshenv=True,
        )
        for node in (ExampleBlock, CardBlock, CardsBlock):
            app.add_node(node)
        app.add_directive("example", ExampleDirective)
        app.add_directive("cards", CardsDirective)
        app.add_directive("card", CardDirective)
        app.add_directive("toctree", PreservingTocTree, override=True)
        app.add_role("icon", icon_role)
        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False
        try:
            app.build(force_all=True)
        finally:
            (output / "diagnostics.txt").write_text(
                diagnostics.getvalue(), encoding="utf-8"
            )
        trees = {
            path.with_suffix("").as_posix(): app.env.get_doctree(
                path.with_suffix("").as_posix()
            )
            for path in paths
        }
        for docname, tree in trees.items():
            destination = output / "doctrees" / (docname + ".txt")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(tree.pformat(), encoding="utf-8")

    errors = [
        node
        for tree in trees.values()
        for node in tree.findall(nodes.system_message)
        if node["level"] >= 3
    ]
    headers = [
        line
        for line in diagnostics.getvalue().splitlines()
        if ": WARNING:" in line or ": ERROR:" in line or ": CRITICAL:" in line
    ]
    warning_types = Counter()
    for line in headers:
        match = re.search(r"\[([^\]]+)\]$", line)
        warning_types[match.group(1) if match else "untyped"] += 1

    print(
        f"Versions: Docutils {version('docutils')}; Sphinx {version('sphinx')}; sphinx-tabs {version('sphinx-tabs')}"
    )
    print(f"Manifest file sizes/hashes verified: {len(paths)}")
    print(f"Stored doctrees: {len(trees)}")
    print(f"Parser errors across corpus: {len(errors)}")
    assert not errors and not any(
        ": ERROR:" in line or ": CRITICAL:" in line for line in headers
    )

    tree = trees[FLOWS]
    cards = list(tree.findall(CardBlock))
    assert len(list(tree.findall(CardsBlock))) == 3
    assert [(node["label"], node["target"]) for node in cards] == CARD_TARGETS
    assert all(node.children and node.source and node.line for node in cards)
    assert "piece, batch, cluster, or wave" in clean(cards[4].astext())
    source_lines = (
        (repository / (FLOWS + ".rst")).read_text(encoding="utf-8").splitlines()
    )
    for node in cards:
        assert source_lines[node.line - 1].strip() == ".. card:: " + node["label"]
    print("Cards: 7 labels, targets, parsed bodies and source lines preserved.")

    toc = list(tree.findall(addnodes.toctree))
    assert len(toc) == 1 and toc[0]["titlesonly"]
    assert toc[0]["original_entries"] == FLOW_ENTRIES
    available = [docname for title, docname in toc[0]["entries"]]
    expected = [
        BASE + "daily_operations/" + name
        for name in (
            "receipts_delivery_one_step",
            "receipts_delivery_two_steps",
            "delivery_three_steps",
        )
    ]
    assert available == expected
    assert toc[0].source and toc[0].line
    reservation_toc = list(trees[RESERVATIONS].findall(addnodes.toctree))
    assert len(reservation_toc) == 1
    assert len(reservation_toc[0]["original_entries"]) == 3
    assert [name for title, name in reservation_toc[0]["entries"]] == [
        RESERVATIONS + "/" + name
        for name in (
            "at_confirmation",
            "manually",
            "before_scheduled_date",
        )
    ]
    print(
        "Flows navigation: 9 original targets retained; 3 staged destinations; 6 unstaged."
    )
    print("Reservation navigation: all 3 staged destinations retained.")
    print("Unstaged targets remain metadata; no extra source pages were staged.")

    summary = {
        "source": manifest["inventory"]["source"],
        "inventory_fingerprint": manifest["inventory_fingerprint"],
        "files_verified": len(paths),
        "stored_doctrees": len(trees),
        "parser_errors": len(errors),
        "versions": {
            name: version(name) for name in ("docutils", "sphinx", "sphinx-tabs")
        },
        "cards": [
            {
                "label": node["label"],
                "target": node["target"],
                "body": clean(node.astext()),
                "source_path": FLOWS + ".rst",
                "source_line": node.line,
            }
            for node in cards
        ],
        "flow_navigation": {
            "original_entries": toc[0]["original_entries"],
            "staged_destinations": available,
        },
        "diagnostic_headers": len(headers),
        "diagnostic_types": dict(sorted(warning_types.items())),
        "limitations": [
            "No normalized records or chunks produced.",
            "Card targets retained as metadata; card link resolution not implemented.",
            "Images not staged; target/asset warnings remain visible.",
            "File bytes verified against manifest; Git cleanliness not rechecked.",
        ],
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Remaining diagnostic headers: {len(headers)}")
    print("Saved diagnostics, summary and readable doctrees:", output)
    print("Corpus parsing and navigation checks passed.")


if __name__ == "__main__":
    main()
