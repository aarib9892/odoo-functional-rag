"""Controlled card/navigation adapters and source locations for pinned tabs."""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.directives.other import TocTree
from sphinx_tabs.tabs import TabDirective, TabsDirective


class CardsBlock(nodes.General, nodes.Element):
    pass


class CardBlock(nodes.General, nodes.Element):
    pass


class CardsDirective(Directive):
    has_content = True
    node_class = CardsBlock

    def run(self):
        node = self.node_class(self.block_text)
        node.source, node.line = self.state_machine.get_source_and_line(self.lineno)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class CardDirective(CardsDirective):
    node_class = CardBlock
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {"target": directives.unchanged_required}

    def run(self):
        if "target" not in self.options:
            raise self.error("A card target is required.")
        result = super().run()
        result[0]["label"] = self.arguments[0]
        result[0]["target"] = self.options["target"]
        return result


class PreservingTocTree(TocTree):
    def run(self):
        result = super().run()
        for wrapper in result:
            for node in wrapper.findall(addnodes.toctree):
                node["original_entries"] = [line.strip() for line in self.content if line.strip()]
        return result


class SourcedTabsDirective(TabsDirective):
    def run(self):
        result = super().run()
        for node in result:
            self.set_source_info(node)
        return result


class SourcedTabDirective(TabDirective):
    def run(self):
        key = f"tabs_{self.env.temp_data['tabs_stack'][-1]}"
        result = super().run()
        label = self.env.temp_data[key]["tab_titles"][-1][1]
        self.set_source_info(label)
        for panel in result:
            self.set_source_info(panel)
        return result
