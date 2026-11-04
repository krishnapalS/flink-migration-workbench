"""Conservative adapter for one synthetic PowerCenter-shaped export pattern.

Not a general Informatica parser. Rejects every undeclared element/attribute,
transform, connector edge, parameter, or non-numeric filter expression.
"""
import re
from decimal import Decimal
from defusedxml import ElementTree as ET
from .compiler import Rejected, require, ident

ATTRS = {
    'POWERMART':set(), 'REPOSITORY':{'NAME'}, 'FOLDER':{'NAME'},
    'MAPPING':{'NAME'}, 'SOURCE':{'NAME'}, 'TARGET':{'NAME'},
    'SOURCEFIELD':{'NAME','DATATYPE','NULLABLE'},
    'TARGETFIELD':{'NAME','DATATYPE','NULLABLE'},
    'TRANSFORMATION':{'NAME','TYPE'},
    'TABLEATTRIBUTE':{'NAME','VALUE'},
    'CONNECTOR':{'FROMINSTANCE','FROMFIELD','TOINSTANCE','TOFIELD'}
}

def read_export(path):
    data = path.read_bytes()
    require(len(data) <= 1024*1024, 'export exceeds demo size limit')
    try:
        root = ET.fromstring(data, forbid_dtd=True)
    except Exception as exc:
        raise Rejected('unsafe or malformed XML') from exc
    for e in root.iter():
        require(e.tag in ATTRS and set(e.attrib) == ATTRS[e.tag], 'unsupported XML shape: ' + e.tag)
        require(not (e.text or '').strip(), 'unexpected XML text')
        require(not (e.tail or '').strip(), 'unexpected XML tail')
    require(root.tag == 'POWERMART' and len(root) == 1 and root[0].tag == 'REPOSITORY', 'expected one repository')
    repo = root[0]; require(len(repo) == 1 and repo[0].tag == 'FOLDER', 'expected one folder')
    folder = repo[0]; require(len(folder) == 1 and folder[0].tag == 'MAPPING', 'expected one mapping')
    m = folder[0]
    allowed = {'SOURCE','TARGET','TRANSFORMATION','CONNECTOR'}
    require(all(x.tag in allowed for x in m), 'unsupported mapping node')
    srcs=m.findall('SOURCE'); tgts=m.findall('TARGET'); trans=m.findall('TRANSFORMATION')
    require(len(srcs)==len(tgts)==len(trans)==1, 'requires one source, filter and target')
    src,tgt,tr=srcs[0],tgts[0],trans[0]
    require(tr.attrib['TYPE']=='Filter', 'only Filter is supported')
    require(len(tr)==1 and len(tr[0])==0 and tr[0].tag=='TABLEATTRIBUTE' and tr[0].attrib['NAME']=='Filter Condition', 'invalid filter')
    require(all(x.tag=='SOURCEFIELD' and len(x)==0 for x in src), 'unsupported source metadata')
    require(all(x.tag=='TARGETFIELD' and len(x)==0 for x in tgt), 'unsupported target metadata')
    for e in (src,tgt,tr): ident(e.attrib['NAME'])
    require(len({e.attrib['NAME'] for e in (src,tgt,tr)}) == 3, 'duplicate instance names')
    def fields(e):
        result=[]
        for f in e:
            a=f.attrib
            require(a['DATATYPE'] in ('bigint','string','decimal(18,2)') and a['NULLABLE'] in ('YES','NO'), 'unsupported field metadata')
            result.append({'name':a['NAME'],'type':a['DATATYPE'].upper(),'nullable':a['NULLABLE']=='YES'})
        return result
    fs=fields(src); require(fs == fields(tgt), 'only same-schema pass-through target supported')
    match=re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*)\s*(>=|>|<=|<|=)\s*(-?(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?)', tr[0].attrib['VALUE'])
    require(match is not None, 'unsupported filter syntax')
    name,op,value=match.groups(); typ=next((f['type'] for f in fs if f['name']==name), None)
    require(typ in ('BIGINT','DECIMAL(18,2)'), 'filter field must be numeric')
    require(typ!='BIGINT' or '.' not in value, 'integer comparison needs integer literal')
    expected=set()
    for f in fs:
        for a,b in [(src,tr),(tr,tgt)]: expected.add((a.attrib['NAME'], f['name'], b.attrib['NAME'], f['name']))
    require(all(len(c)==0 for c in m.findall('CONNECTOR')), 'unexpected connector child')
    actual=[tuple(c.attrib[k] for k in ['FROMINSTANCE','FROMFIELD','TOINSTANCE','TOFIELD']) for c in m.findall('CONNECTOR')]
    require(len(actual)==len(expected) and set(actual)==expected, 'missing, duplicate or unsupported connector')
    return {'version':1,'name':m.attrib['NAME'],'source':src.attrib['NAME'],'fields':fs,
            'select':[{'as':f['name'],'expr':{'field':f['name']}} for f in fs],
            'where':{'op':{'>=':'ge','>':'gt','<=':'le','<':'lt','=':'eq'}[op], 'left':{'field':name},
                     'right':{'literal':int(value) if typ=='BIGINT' else value,'type':typ}},
            'semantics':{'mode':'bounded','nulls':'sql','ordering':'unordered','duplicates':'preserve'}}
