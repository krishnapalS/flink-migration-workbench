"""Duplicate-aware, typed exact bag comparison. Not a source engine emulator."""
from collections import Counter
from decimal import Decimal
import json

def cell(x):
    if isinstance(x, Decimal): return ('decimal', str(x.normalize()))
    if x is None: return ('null', '')
    if type(x) in (int, str, bool): return (type(x).__name__, str(x))
    raise ValueError('unsupported comparison type')

def compare(expected, actual):
    def bag(rows): return Counter(tuple(cell(c) for c in row) for row in rows)
    a,b=bag(expected),bag(actual)
    return {'passed': a==b, 'expected_count':sum(a.values()), 'actual_count':sum(b.values()),
            'missing_rows':sum((a-b).values()), 'unexpected_rows':sum((b-a).values())}
