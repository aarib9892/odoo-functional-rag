"""Explicit shared provider budget; reservations survive retries and unknown usage."""
import argparse
import json
from pathlib import Path
import sqlite3
import time
from uuid import uuid4

from app.chunking.tokens import count_tokens


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_file(): raise BudgetExceeded('Choose an approved budget before provider calls')

    @staticmethod
    def approve(path, limit_usd):
        if not 0 < limit_usd <= 1000: raise ValueError('Budget must be in (0,1000] USD')
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        # Never reset existing spend or increase a cap implicitly.
        with path.open('xb'):
            pass
        path.chmod(0o600)
        with sqlite3.connect(path) as db:
            db.executescript('CREATE TABLE approval (limit_usd REAL); CREATE TABLE spend (id TEXT PRIMARY KEY, stage TEXT, reserved REAL, actual REAL, created REAL);')
            db.execute('INSERT INTO approval VALUES (?)', (limit_usd,))

    def reserve(self, stage, usd):
        if usd < 0: raise ValueError('Invalid cost reservation')
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            limit = db.execute('SELECT limit_usd FROM approval').fetchone()[0]
            spent = db.execute('SELECT coalesce(sum(coalesce(actual,reserved)),0) FROM spend').fetchone()[0]
            if spent + usd > limit: raise BudgetExceeded('Provider budget exhausted; no request sent')
            key = str(uuid4())
            db.execute('INSERT INTO spend VALUES (?,?,?,NULL,?)', (key,stage,usd,time.time()))
        return key

    def finish(self, key, actual):
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE spend SET actual=? WHERE id=?', (actual,key))


class MeteredClient:
    def __init__(self, client, budget, prices):
        self.client, self.budget, self.prices = client, budget, prices
        self.embeddings = self.Embeddings(self)
        self.responses = self.Responses(self)

    def __getattr__(self, name): return getattr(self.client, name)

    class Embeddings:
        def __init__(self, owner): self.o = owner
        async def create(self, **kwargs):
            o=self.o; rate=o.prices['embedding_per_million']/1e6
            if kwargs['model'] != o.prices['embedding_model']: raise ValueError('Unpriced embedding model')
            texts=kwargs['input']; texts=[texts] if isinstance(texts,str) else texts
            key=o.budget.reserve('embedding', sum(count_tokens(t)+16 for t in texts)*rate)
            response=await o.client.embeddings.create(**kwargs)
            o.budget.finish(key,response.usage.total_tokens*rate)
            return response

    class Responses:
        def __init__(self, owner): self.o=owner
        async def parse(self, **kwargs):
            o=self.o; p=o.prices
            if kwargs['model'] != p['generation_model']: raise ValueError('Unpriced generation model')
            schema=json.dumps(kwargs['text_format'].model_json_schema())
            tokens=count_tokens(kwargs['input']+kwargs['instructions']+schema)+2048
            cost=(tokens*p['input_per_million']+kwargs['max_output_tokens']*p['output_per_million'])/1e6
            key=o.budget.reserve('generation',cost)
            response=await o.client.responses.parse(**kwargs)
            if response.usage:
                o.budget.finish(key,(response.usage.input_tokens*p['input_per_million']+response.usage.output_tokens*p['output_per_million'])/1e6)
            return response


def main():
    p=argparse.ArgumentParser(description='Record a user-chosen budget. Does not call a provider.')
    p.add_argument('--path',type=Path,required=True);p.add_argument('--limit-usd',type=float,required=True)
    a=p.parse_args();Budget.approve(a.path,a.limit_usd);print('Recorded budget; no provider calls made.')


if __name__=='__main__':main()
