from docutils import nodes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition


class ExampleBlock(nodes.Admonition, nodes.Element):
    """An Odoo example containing parsed child nodes."""


class ExampleDirective(BaseAdmonition):
    node_class = ExampleBlock


def icon_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Preserve an icon's identifier as inline text and metadata."""
    classes = ["odoo-icon", *(options or {}).get("classes", [])]
    node = nodes.inline(rawtext, text, classes=classes)
    node["icon_name"] = text
    node.source, node.line = inliner.reporter.get_source_and_line(lineno)
    return [node], []
