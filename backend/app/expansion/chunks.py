"""Versioned full-app rendering and bounded fragments; old renderer stays frozen."""
from copy import deepcopy
from app.chunking.pipeline import build_document_chunks
from app.chunking.records import stable_hash
from app.chunking.tokens import count_tokens, ENCODING_NAME, TOKENIZER_VERSION
from app.chunking.walk import iter_blocks_with_sections

CONFIG = {'chunker_version': 'full-app-fragments-0.2', 'renderer_version': 'full-app-text-0.2',
          'max_tokens': 512, 'encoding_name': ENCODING_NAME, 'tokenizer_version': TOKENIZER_VERSION}


def table(block):
    group = next(c for c in block['children'] if c['kind'] == 'table_group')
    width = group['attributes']['cols']
    rows = [r for part in group['children'] if part['kind'] in {'table_head', 'table_body'} for r in part['children']]
    grid, pending = [], {}
    for row in rows:
        values = [''] * width
        for col, (remaining, text) in list(pending.items()):
            values[col] = text
            if remaining == 1: del pending[col]
            else: pending[col] = (remaining-1, text)
        cursor = 0
        for cell in row['children']:
            while cursor < width and values[cursor]: cursor += 1
            text = render(cell)
            attrs = cell['attributes']
            if cursor + attrs['colspan'] > width: raise ValueError('Invalid table span')
            for col in range(cursor, cursor + attrs['colspan']):
                values[col] = text or '[Empty cell]'
                if attrs['rowspan'] > 1: pending[col] = (attrs['rowspan']-1, text or '[Empty cell]')
            cursor += attrs['colspan']
        grid.append(values)
    if pending: raise ValueError('Table rowspan exceeds body')
    head = next((c for c in group['children'] if c['kind'] == 'table_head'), None)
    header_count = len(head['children']) if head else 0
    headers = [' / '.join(dict.fromkeys(row[col] for row in grid[:header_count])) or f'Column {col+1}'
               for col in range(width)]
    return '\n\n'.join('; '.join(f'{h}: {value}' for h, value in zip(headers, row)) for row in grid[header_count:])


def render(b):
    k = b['kind']; children = b.get('children', [])
    if k in {'anchor', 'comment', 'substitution_definition'}: return ''
    if k == 'table': return table(b)
    if k == 'image':
        return f"[Image reference: {b['attributes']['uri']}; interpretation unavailable]\n" + b['attributes'].get('alt', '')
    if k in {'literal', 'math'}: return f'[{k}]\n' + b['text']
    if k in {'paragraph', 'caption', 'title', 'rubric', 'field_name', 'term', 'line', 'classifier', 'label'}:
        return ' '.join(b['text'].split())
    if k in {'bullet_list', 'ordered_list'}:
        return '\n'.join((f"{i}. " if k == 'ordered_list' else '- ') + render(c)
                         for i, c in enumerate(children, b['attributes'].get('start', 1)))
    if k == 'navigation': return ''
    known = {'compound','container','list_item','field_list','field','field_body','table_cell',
             'tab','tabs','cards','card','figure','block_quote','admonition','line_block',
             'definition_list','definition_list_item','definition','footnote','attribution'}
    if k not in known: raise ValueError(f'Unsupported block: {k}')
    label = (b['attributes'].get('admonition_type', '').upper() if k == 'admonition'
             else 'Tab: ' + b['attributes']['label'] if k == 'tab'
             else ' '.join(c for c in b['attributes'].get('classes', []) if c in {'exercise','spoiler'}) if k == 'container' else '')
    text = '\n\n'.join(t for c in children if (t := render(c)))
    return (label + ':\n' if label else '') + text


def fragments(text, context, limit=512):
    offset = 0
    while offset < len(text):
        lo, hi = 1, len(text)-offset
        if count_tokens(context+'\n\n'+text[offset:offset+1]) > limit:
            raise ValueError('Heading exceeds fragment budget')
        while lo < hi:
            mid = (lo+hi+1)//2
            if count_tokens(context+'\n\n'+text[offset:offset+mid]) <= limit: lo = mid
            else: hi = mid-1
        end = offset + lo
        if end < len(text):
            boundary = text.rfind('\n\n', offset, end)
            if boundary <= offset: boundary = text.rfind(' ', offset, end)
            if boundary > offset: end = boundary+1
        yield offset, end, text[offset:end]
        offset = end


def record(content, fragment=None):
    body = {'schema_version': 'm31-chunk-0.1', 'chunking_config_id': stable_hash(CONFIG),
            'chunking_config': CONFIG, 'token_count': count_tokens(content['retrieval_text']), 'content': content}
    if fragment is not None: body['fragment'] = fragment
    if body['token_count'] > 512: raise ValueError('Chunk exceeds budget')
    return {'chunk_id': stable_hash(body), **body}


def chunks(document):
    try:
        old = build_document_chunks(document)
    except ValueError:
        old = None
    if old is not None:
        result = []
        for r in old:
            content = deepcopy(r['content']); content['renderer_version'] = CONFIG['renderer_version']
            result.append(record(content))
        return result
    result = []
    for section, block in iter_blocks_with_sections(document['items']):
        text = render(block)
        if not text.strip(): continue
        heading = ' > '.join(block['heading_path']) or document['title']
        # Repeat container qualifications across fragments so warnings/tabs stay visible.
        qualifier = block['attributes'].get('admonition_type', '')
        context = heading + (' / ' + qualifier.upper() if qualifier else '')
        for start, end, piece in fragments(text, context):
            content = {'source': document['source'], 'document_id': document['document_id'],
                'document_revision_id': document['revision_id'], 'section_id': section,
                'heading_path': block['heading_path'], 'source_block_ids': [block['block_id']],
                'renderer_version': CONFIG['renderer_version'], 'evidence_text': piece,
                'retrieval_text': context+'\n\n'+piece}
            result.append(record(content, {'block_id': block['block_id'], 'start': start, 'end': end,
                                             'rendered_length': len(text)}))
    return result
