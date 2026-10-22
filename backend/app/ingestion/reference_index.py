"""Resolve selected-corpus targets while retaining explicit unresolved states."""

from pathlib import Path

from sphinx.util import docname_join


class ReferenceIndex:
    def __init__(self, app, trees, repository):
        self.app = app
        self.trees = trees
        self.repository = Path(repository)
        self.standard = app.env.get_domain("std")

    def document(self, from_doc, target):
        docname = docname_join(from_doc, target)
        if docname.endswith(".rst"):
            docname = docname[:-4]
        path = docname + ".rst"
        if docname in self.trees:
            return {"resolution": "resolved", "destination_path": path, "destination_anchor": None}
        candidate = (self.repository / path).resolve()
        try:
            candidate.relative_to(self.repository.resolve())
        except ValueError:
            return {"resolution": "invalid_target"}
        return {"resolution": "not_in_corpus", "destination_path": path,
                "destination_anchor": None, "target_existence": "not_checked"}

    def pending(self, from_doc, node):
        target, kind = node.get("reftarget", ""), node.get("reftype")
        if node.get("refdomain") != "std" or kind not in {"ref", "doc"}:
            return {"resolution": "unsupported_reference_kind"}
        if kind == "doc":
            result = self.document(node.get("refdoc", from_doc), target)
        else:
            label = (self.standard.anonlabels.get(target) if node.get("refexplicit")
                     else self.standard.labels.get(target))
            if not label:
                return {"resolution": "unresolved_label"}
            result = {"resolution": "resolved", "destination_path": label[0] + ".rst",
                      "destination_anchor": label[1]}
        if result["resolution"] == "resolved":
            # Verify the native resolver can actually construct the reference.
            resolved = self.standard.resolve_xref(self.app.env, from_doc, self.app.builder,
                                                 kind, target, node, node[0].deepcopy())
            if resolved is None:
                return {"resolution": "native_resolution_failed"}
            result["resolved_text"] = resolved.astext()
        return result
