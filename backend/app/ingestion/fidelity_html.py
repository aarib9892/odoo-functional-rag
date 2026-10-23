"""Independent HTML views of normalized records and the pinned RST source."""

from html import escape
from pathlib import Path


STYLE = """
body{font:15px/1.6 system-ui,sans-serif;color:#16293a;margin:0;padding:24px;background:#fff}
h1,h2,h3,h4{line-height:1.25;margin-top:1.5em}a,.reference{color:#15676b}p{margin:.7em 0}
table{border-collapse:collapse;width:100%;margin:18px 0}th,td{border:1px solid #a8b8bd;padding:9px;text-align:left}
th{background:#eaf2f1}aside,.card{border-left:4px solid #497f85;background:#f1f6f5;padding:12px 16px;margin:16px 0}
aside.warning{border-color:#a86a13;background:#fff6e6}.admonition-title{font-weight:750;margin-top:0}
.cards{display:grid;gap:10px}.tabs{border:1px solid #aec4c6;padding:12px}.tab{border-top:2px solid #5b9698;margin:12px 0}
.tab h4{margin:.5em 0}.meta{color:#667780;font:11px/1.4 system-ui;margin:3px 0}code,pre{font-family:ui-monospace,monospace}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;padding:12px}.formula{border:1px solid #afc4c5}
img{max-width:100%;height:auto}.missing{border:2px dashed #bf8a45;padding:14px;background:#fff9ee}
.source-line{display:block;white-space:pre-wrap;overflow-wrap:anywhere}.line-no{display:inline-block;width:4em;color:#75858d;user-select:none}
figure{margin:20px 0}figcaption{color:#54666f;font-size:13px}.reference{border-bottom:1px dotted #6a9fa1}
"""


def page(title, body):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>' + escape(title) + '</title><style>' + STYLE + '</style><body>' + body + '</body></html>'


def source_page(relative, data):
    lines = []
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        lines.append(f'<span class="source-line" id="L{number}"><span class="line-no">{number}</span>{escape(line)}</span>')
    return page(relative, '<h1>Pinned RST source</h1><p class="meta">' + escape(relative) + '</p><pre>' + ''.join(lines) + '</pre>')


def inline(item):
    kind, attributes = item["kind"], item.get("attributes", {})
    content = ''.join(inline(child) for child in item.get("children", [])) or escape(item["text"])
    if kind == "strong": return '<strong>' + content + '</strong>'
    if kind == "emphasis": return '<em>' + content + '</em>'
    if kind in {"literal", "math", "icon"}: return '<code>' + content + '</code>'
    if kind == "reference":
        tooltip = str(attributes.get("target", "")) + ' | ' + str(attributes.get("resolution", ""))
        return '<span class="reference" title="' + escape(tooltip, quote=True) + '">' + content + '</span>'
    if kind == "abbreviation": return '<abbr title="' + escape(str(attributes.get("explanation", "")), quote=True) + '">' + content + '</abbr>'
    if kind in {"gui_label", "menu_path"}: return '<strong>' + content + '</strong>'
    if kind == "unsupported": raise ValueError("Unsupported inline in review renderer")
    return content


def normalized_page(document, image_map):
    def render(item, header=False, stubs=0, column=0):
        if "items" in item:
            level = min(len(item["heading_path"]), 6)
            return f'<section><h{level}>' + escape(item["title"]) + f'</h{level}>' + ''.join(render(child) for child in item["items"]) + '</section>'
        kind, attributes = item["kind"], item.get("attributes", {})
        children = item.get("children", [])
        text = ''.join(inline(child) for child in item.get("inlines", [])) or escape(item.get("text", ""))
        if kind == "paragraph": return '<p>' + text + '</p>'
        if kind in {"caption", "title"}: return '<p class="admonition-title">' + text + '</p>'
        if kind in {"anchor", "comment", "substitution_definition"}: return ''
        if kind in {"literal", "math"}: return '<pre class="formula">' + escape(item["text"]) + '</pre>'
        if kind == "image":
            uri, alt = attributes["uri"], attributes.get("alt", "")
            if uri not in image_map:
                return '<div class="missing">Image unavailable in this review.<br><code>' + escape(uri) + '</code><p>Alt: ' + escape(alt) + '</p></div>'
            return '<img src="../source_html/_images/' + escape(image_map[uri], quote=True) + '" alt="' + escape(alt, quote=True) + '">'
        if kind == "figure": return '<figure>' + ''.join(render(child) for child in children) + '</figure>'
        if kind in {"bullet_list", "ordered_list"}:
            tag = 'ul' if kind == 'bullet_list' else 'ol'
            extra = ''
            if tag == 'ol':
                enum = {'arabic':'1','loweralpha':'a','upperalpha':'A','lowerroman':'i','upperroman':'I'}.get(attributes.get('enumtype'),'1')
                extra = f' start="{int(attributes.get("start",1))}" type="{enum}"'
            return '<' + tag + extra + '>' + ''.join(render(child) for child in children) + '</' + tag + '>'
        if kind == "list_item": return '<li>' + ''.join(render(child) for child in children) + '</li>'
        if kind == "admonition":
            typ = attributes["admonition_type"]
            label = {'seealso':'See also'}.get(typ, typ.title())
            title = '' if typ == 'admonition' and children and children[0]['kind']=='title' else '<p class="admonition-title">' + escape(label) + '</p>'
            return '<aside class="' + escape(typ, quote=True) + '">' + title + ''.join(render(child) for child in children) + '</aside>'
        if kind == "cards": return '<div class="cards">' + ''.join(render(child) for child in children) + '</div>'
        if kind == "card": return '<article class="card"><h4>' + escape(attributes['label']) + '</h4>' + ''.join(render(child) for child in children) + '<p class="meta">Target: ' + escape(attributes['target']) + '</p></article>'
        if kind == "tabs": return '<div class="tabs">' + ''.join(render(child) for child in children) + '</div>'
        if kind == "tab": return '<section class="tab"><h4>' + escape(attributes['label']) + '</h4>' + ''.join(render(child) for child in children) + '</section>'
        if kind == "navigation": return '<details><summary>Original navigation targets</summary><ul>' + ''.join('<li><code>' + escape(entry) + '</code></li>' for entry in attributes['original_entries']) + '</ul></details>'
        if kind == "table": return '<table>' + ''.join(render(child) for child in children) + '</table>'
        if kind == "table_group":
            count = sum(bool(child['attributes'].get('stub')) for child in children if child['kind']=='table_column')
            return ''.join(render(child, stubs=count) for child in children if child['kind']!='table_column')
        if kind in {"table_head", "table_body"}:
            tag = 'thead' if kind == 'table_head' else 'tbody'
            return '<' + tag + '>' + ''.join(render(child, kind=='table_head',stubs) for child in children) + '</' + tag + '>'
        if kind == "table_row":
            cells, index = [], 0
            for child in children:
                cells.append(render(child,header,stubs,index))
                index += child['attributes'].get('colspan',1)
            return '<tr>' + ''.join(cells) + '</tr>'
        if kind == "table_cell":
            tag = 'th' if header or column < stubs else 'td'
            return f'<{tag} rowspan="{attributes["rowspan"]}" colspan="{attributes["colspan"]}">' + ''.join(render(child) for child in children) + f'</{tag}>'
        if kind == "block_quote": return '<blockquote>' + ''.join(render(child) for child in children) + '</blockquote>'
        if kind in {"compound", "container", "field_list", "field", "field_body"}: return ''.join(render(child) for child in children)
        if kind == "field_name": return '<strong>' + text + '</strong>'
        raise ValueError(f"No normalized review rendering for {kind}")
    body = '<p class="meta">Independent rendering of normalized JSON. All tab panels are expanded. Formulas are shown as LaTeX.</p>'
    body += ''.join(render(item) for item in document['items'])
    return page(document['title'],body)


def build_source_html(files, repository, images, work):
    """Use the raw RST and native HTML writer, independently of normalized JSON."""
    from io import StringIO
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.util.console import nocolor
    from app.ingestion.rst_directives import ExampleBlock, ExampleDirective, icon_role
    from app.ingestion.rst_structures import (CardBlock, CardDirective, CardsBlock, CardsDirective,
                                             PreservingTocTree, SourcedTabDirective, SourcedTabsDirective)
    source, output = work / 'source', work / 'source_html'
    for relative, data in files.items():
        target = source / relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    for image in images:
        if image['source_file_present']:
            relative = image['uri']
            target = source / relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((repository / relative).read_bytes())
    def example_open(translator,node): translator.body.append('<aside class="admonition example"><p class="admonition-title">Example</p>')
    def aside_close(translator,node): translator.body.append('</aside>')
    def cards_open(translator,node): translator.body.append('<div class="cards">')
    def div_close(translator,node): translator.body.append('</div>')
    def card_open(translator,node): translator.body.append('<div class="card"><h4>'+escape(node['label'])+'</h4>')
    def math_inline(translator,node):
        translator.body.append('<code>'+escape(node.astext())+'</code>')
        raise nodes.SkipNode
    def math_block(translator,node):
        translator.body.append('<pre class="formula">'+escape(node.astext())+'</pre>')
        raise nodes.SkipNode
    diagnostics=StringIO()
    nocolor()
    app=Sphinx(srcdir=str(source),confdir=None,outdir=str(output),doctreedir=str(work/'doctrees'),
               buildername='html',confoverrides={'project':'Pinned source review','root_doc':sorted(files)[0][:-4],
                   'extensions':['sphinx_tabs.tabs'],'nitpicky':True,'smartquotes':False,
                   'html_theme':'basic','html_sidebars':{'**':[]},'html_copy_source':False,
                   'html_show_sourcelink':False,'html_show_sphinx':False},
               status=StringIO(),warning=diagnostics,freshenv=True)
    app.add_node(ExampleBlock,html=(example_open,aside_close))
    app.add_node(CardsBlock,html=(cards_open,div_close))
    app.add_node(CardBlock,html=(card_open,div_close))
    for name,directive in {'example':ExampleDirective,'cards':CardsDirective,'card':CardDirective,
                            'toctree':PreservingTocTree,'tabs':SourcedTabsDirective,'tab':SourcedTabDirective}.items():
        app.add_directive(name,directive,override=True)
    app.add_role('icon',icon_role)
    app.add_html_math_renderer('review_latex',inline_renderers=(math_inline,None),block_renderers=(math_block,None))
    app.config.html_math_renderer='review_latex'
    app.env.settings['file_insertion_enabled']=False
    app.env.settings['raw_enabled']=False
    app.build(force_all=True)
    logs=diagnostics.getvalue().replace(str(source)+'/', '')
    if ': ERROR:' in logs or ': CRITICAL:' in logs:
        raise ValueError('Source HTML rendering failed:\n'+logs)
    for path in output.rglob('*.html'):
        text=path.read_text(encoding='utf-8').replace('</head>', '<style>'+STYLE+'</style></head>')
        path.write_text(text,encoding='utf-8')
    return output,dict(app.builder.images),logs
