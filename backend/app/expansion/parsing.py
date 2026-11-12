"""Additional pinned Odoo structures, opt-in; never execute embedded HTML."""
from dataclasses import replace
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import raw_role
from app.ingestion.normalization import Normalizer
from app.ingestion.normalized_models import Block, Inline
from app.ingestion.rst_structures import CardDirective


class FullCard(CardDirective):
    option_spec = {**CardDirective.option_spec, 'large': directives.flag,
                   'image': directives.unchanged, 'alt': directives.unchanged,
                   'tag': directives.unchanged}

    def run(self):
        result = super().run()
        result[0]['tag'] = self.options.get('tag', '')
        if self.options.get('image'):
            image = nodes.image(uri=self.options['image'], alt=self.options.get('alt', ''))
            image.source, image.line = result[0].source, result[0].line
            result[0] += image
        return result


class PreservedContainer(Directive):
    has_content = True
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {'class': directives.class_option, 'name': directives.unchanged}

    def run(self):
        node = nodes.container(self.block_text, classes=[self.name, *self.options.get('class', [])])
        node.source, node.line = self.state_machine.get_source_and_line(self.lineno)
        if self.name == 'h:div' and self.arguments:
            node['classes'].extend(self.arguments[0].split())
        elif self.arguments:
            node += nodes.rubric(text=self.arguments[0])
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def reference_only_html(name, rawtext, text, lineno, inliner, options=None, content=None):
    # Inline raw markup is data only, never passed to a browser or executed.
    return [nodes.inline(rawtext, '[Inline graphic; interpretation unavailable]', classes=['image-reference'])], []


reference_only_html.options = raw_role.options


class FullNormalizer(Normalizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normalizer_version = 'full-app-structures-0.2'

    def inline(self, node):
        if isinstance(node, (nodes.superscript, nodes.subscript, nodes.footnote_reference)):
            return Inline(node.tagname, node.astext(), self.location(node), {},
                          tuple(self.inline(c) for c in node.children))
        return super().inline(node)

    def block(self, node, headings):
        if isinstance(node, (nodes.line, nodes.term, nodes.classifier, nodes.label)):
            inlines = tuple(self.inline(c) for c in node.children)
            return Block(self.next_id('b'), node.tagname, self.location(node), headings,
                         ''.join(i.text for i in inlines), {}, inlines, ())
        if isinstance(node, (nodes.line_block, nodes.line, nodes.definition_list,
                             nodes.definition_list_item, nodes.term, nodes.definition,
                             nodes.classifier, nodes.footnote, nodes.label, nodes.attribution)):
            return Block(self.next_id('b'), node.tagname, self.location(node), headings,
                         node.astext() if isinstance(node, (nodes.line, nodes.term, nodes.classifier, nodes.label)) else '',
                         {}, (), tuple(self.block(c, headings) for c in node.children if not isinstance(c, nodes.Text)))
        return super().block(node, headings)
