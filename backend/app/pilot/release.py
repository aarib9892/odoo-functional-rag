"""Content-addressed operator release descriptors; preparation is not activation."""
import json
from pathlib import Path
import re

from app.chunking.records import stable_hash


def load_release(path: Path):
    record = json.loads(path.read_text())
    body = {k: v for k, v in record.items() if k != 'release_id'}
    if record.get('schema_version') != 'odoo-release-0.1' or stable_hash(body) != record.get('release_id'):
        raise ValueError('Invalid release descriptor identity')
    if record.get('state') not in {'indexed_candidate', 'approved'}:
        raise ValueError('Release has not been indexed; prepare embeddings after budget approval')
    if (record['source']['odoo_version'] != '19.0' or record['source']['language'] != 'en'
            or record['source']['repository_url'] != 'https://github.com/odoo/documentation.git'
            or not re.fullmatch('[a-f0-9]{40}', record['source']['commit'])
            or not re.fullmatch('[a-f0-9]{64}', record['snapshot_id'])):
        raise ValueError('Release must refer to pinned Odoo 19 English documentation')
    if record['retrieval_method'] not in {'dense', 'hybrid'}:
        raise ValueError('Invalid release retrieval method')
    if not record['corpus_name'].startswith('odoo19-full-'):
        raise ValueError('Expanded release needs its own corpus namespace')
    if record['coverage']['documents'] != 944:
        raise ValueError('Full release must account for all 944 pages')
    if (record['coverage'].get('searchable_documents',-1) < 1 or
            record['coverage'].get('reference_only_documents',-1) < 0 or
            record['coverage']['searchable_documents'] + record['coverage']['reference_only_documents'] != 944):
        raise ValueError('Release coverage categories must account for all pages')
    return record
