"""Small, fixture-scoped Docutils adapter for the M2 parser comparison.

References and navigation targets are retained, not resolved. This module
supports the syntax exercised by the probe, not all Sphinx/Odoo syntax.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

from app.ingestion.rst_directives import ExampleDirective, icon_role


class SeeAlsoBlock(nodes.Admonition, nodes.Element):
    pass


class SeeAlsoDirective(BaseAdmonition):
    node_class = SeeAlsoBlock


class TabsBlock(nodes.General, nodes.Element):
    pass


class TabBlock(nodes.General, nodes.Element):
    pass


class CardsBlock(nodes.General, nodes.Element):
    pass


class CardBlock(nodes.General, nodes.Element):
    pass


class ToctreeBlock(nodes.General, nodes.Element):
    pass


class ParsedContainer(Directive):
    has_content = True
    node_class = TabsBlock

    def run(self):
        node = self.node_class(self.block_text)
        node.source, node.line = self.state_machine.get_source_and_line(self.lineno)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class TabDirective(ParsedContainer):
    node_class = TabBlock
    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        result = super().run()
        result[0]["label"] = self.arguments[0]
        return result


class CardsDirective(ParsedContainer):
    node_class = CardsBlock


class CardDirective(TabDirective):
    node_class = CardBlock
    option_spec = {"target": directives.unchanged_required}

    def run(self):
        if "target" not in self.options:
            raise self.error("The probe adapter requires a card :target:.")
        result = super().run()
        result[0]["target"] = self.options["target"]
        return result


class ToctreeDirective(Directive):
    has_content = True
    option_spec = {"titlesonly": directives.flag}

    def run(self):
        node = ToctreeBlock(self.block_text)
        node.source, node.line = self.state_machine.get_source_and_line(self.lineno)
        node["titlesonly"] = "titlesonly" in self.options
        # These fixtures contain plain relative docnames, without globs/titles.
        node["entries"] = [line.strip() for line in self.content if line.strip()]
        return [node]


def semantic_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    value = " ".join(text.split())
    attributes = {"rst_role": name, "role_text": value}
    display = value
    node_class = nodes.inline

    if name in {"ref", "doc"}:
        explicit = value.endswith(">") and "<" in value
        if explicit:
            display, target = value[:-1].rsplit("<", 1)
            display, target = display.strip(), target.strip()
        else:
            target = value
        attributes.update(target=target, explicit_title=explicit)
    elif name == "abbr":
        node_class = nodes.abbreviation
        if value.endswith(")") and " (" in value:
            display, explanation = value[:-1].rsplit(" (", 1)
            attributes["explanation"] = explanation

    node = node_class(rawtext, display, **attributes)
    node.source, node.line = inliner.reporter.get_source_and_line(lineno)
    return [node], []


def register_probe_adapter():
    """Register only in this probe process; do not use in a shared service."""
    for name in ("guilabel", "menuselection", "ref", "doc", "abbr"):
        roles.register_local_role(name, semantic_role)
    roles.register_local_role("icon", icon_role)
    for name, directive in {
        "example": ExampleDirective,
        "seealso": SeeAlsoDirective,
        "tabs": ParsedContainer,
        "tab": TabDirective,
        "cards": CardsDirective,
        "card": CardDirective,
        "toctree": ToctreeDirective,
    }.items():
        directives.register_directive(name, directive)
