"""Validate a small typed IR, then emit SQL. No raw SQL expressions accepted."""
from __future__ import annotations
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

class Rejected(ValueError):
    """A mapping cannot be proven supported by this ruleset."""

TYPES = {'BIGINT', 'STRING', 'DECIMAL(18,2)'}
OPS = {'ge': '>=', 'gt': '>', 'le': '<=', 'lt': '<', 'eq': '='}
RULESET = 'bounded-relational-v1'

def require(value, message):
    if not value:
        raise Rejected(message)

def keys(obj, expected):
    require(isinstance(obj, dict) and set(obj) == set(expected), 'unexpected or missing fields: ' + str(expected))

def ident(name):
    require(isinstance(name, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}', name), 'unsafe identifier')
    return '`' + name + '`'

def literal(value, dtype):
    if dtype == 'STRING':
        require(isinstance(value, str) and len(value) <= 1024 and not any(ord(c) < 32 for c in value), 'invalid string literal')
        return "'" + value.replace("'", "''") + "'"
    if dtype == 'BIGINT':
        require(type(value) is int and -(2**63) <= value < 2**63, 'invalid BIGINT')
        return str(value)
    require(dtype == 'DECIMAL(18,2)' and isinstance(value, str), 'decimal must be a string')
    require(re.fullmatch(r'-?(0|[1-9][0-9]{0,15})(\.[0-9]{1,2})?', value), 'invalid fixed decimal')
    return "CAST('" + value + "' AS DECIMAL(18,2))"

def expr(node, fields, depth=0):
    require(depth < 16 and isinstance(node, dict), 'expression too deep or malformed')
    if set(node) == {'field'}:
        name = node['field']; ident(name)
        require(name in fields, 'unknown field: ' + name)
        return ident(name), fields[name]
    if set(node) == {'literal', 'type'}:
        require(node['type'] in TYPES, 'unsupported literal type')
        return literal(node['literal'], node['type']), node['type']
    if set(node) == {'upper'}:
        sql, typ = expr(node['upper'], fields, depth+1)
        require(typ == 'STRING', 'UPPER needs STRING')
        return 'UPPER(' + sql + ')', typ
    raise Rejected('unsupported expression; manual translation required')

def compile_mapping(ir):
    keys(ir, ['version', 'name', 'source', 'fields', 'select', 'where', 'semantics'])
    require(type(ir['version']) is int and ir['version'] == 1, 'unsupported IR version')
    ident(ir['name']); ident(ir['source'])
    require(ir['semantics'] == {'mode':'bounded', 'nulls':'sql', 'ordering':'unordered', 'duplicates':'preserve'}, 'unsupported semantics')
    require(isinstance(ir['fields'], list) and 0 < len(ir['fields']) <= 256, 'invalid fields')
    fields = {}
    for field in ir['fields']:
        keys(field, ['name', 'type', 'nullable']); ident(field['name'])
        require(field['name'] not in fields and field['type'] in TYPES and type(field['nullable']) is bool, 'invalid or duplicate field')
        fields[field['name']] = field['type']
    require(isinstance(ir['select'], list) and 0 < len(ir['select']) <= 256, 'invalid projection')
    out = []; aliases = set()
    for col in ir['select']:
        keys(col, ['as', 'expr']); ident(col['as'])
        require(col['as'] not in aliases, 'duplicate output alias')
        aliases.add(col['as']); sql, typ = expr(col['expr'], fields)
        out.append(sql + ' AS ' + ident(col['as']))
    where = ir['where']; keys(where, ['op', 'left', 'right'])
    require(where['op'] in OPS, 'unsupported predicate')
    left, lt = expr(where['left'], fields); right, rt = expr(where['right'], fields)
    require(lt == rt and lt != 'STRING', 'comparison requires matching numeric types')
    return 'SELECT ' + ', '.join(out) + '\nFROM ' + ident(ir['source']) + '\nWHERE ' + left + ' ' + OPS[where['op']] + ' ' + right + ';\n'

def write_artifacts(ir, out):
    sql = compile_mapping(ir)  # Nothing written before all validation passes.
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    canonical = json.dumps(ir, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    manifest = {'ruleset':RULESET, 'ir_sha256':hashlib.sha256(canonical).hexdigest(),
                'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(), 'status':'compiled_not_approved',
                'required_gates':['source_semantics_review', 'flink_runtime_test', 'reconciliation', 'human_approval'],
                'limitations':['bounded only', 'no connector deployment', 'no production export certification']}
    (out/'mapping.sql').write_text(sql)
    (out/'ir.json').write_text(json.dumps(ir, indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest
