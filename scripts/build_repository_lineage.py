#!/usr/bin/env python3
"""Deterministic, non-executing partial lineage extraction over a frozen scope."""
from __future__ import annotations

import argparse
import ast
import csv
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re

from frozen_audit_inputs import frozen_source_path

ROOT = Path(__file__).resolve().parents[1]
SCOPE = 'metadata/repository_audit_scope.json'
NODE_OUT = 'metadata/lineage_nodes.csv'
EDGE_OUT = 'metadata/lineage_edges.csv'
DOC_OUT = 'docs/repository_lineage.md'
TEXT_EXT = {'.py', '.R', '.md', '.json', '.jsonpatch', '.csv', '.yml', '.yaml'}
PATH_RE = re.compile(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:csv|json|jsonpatch|md|py|R|pdf|png|svg|docx|yml|txt|html)")
READERS = {'rows', 'js', 'read_json', 'read_csv', 'read_dataset', 'read_bytes', 'read_text', 'load_json'}
WRITERS = {'write_bytes', 'write_text'}


def csv_bytes(rows, fields):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def resolve_reference(actor, value, paths, document=False):
    """Resolve only unambiguous exact in-scope files, never glob or URI evidence."""
    if not isinstance(value, str) or not value or '://' in value or any(x in value for x in '*?{}'):
        return None
    value = value.split('#', 1)[0]
    if not value:
        return None
    if value.startswith('/'):
        return value.removeprefix(str(ROOT) + '/') if value.startswith(str(ROOT) + '/') and value.removeprefix(str(ROOT) + '/') in paths else None
    parent = str(PurePosixPath(actor).parent)
    # Markdown links have a defined document-relative base.
    if document:
        norm = str(Path(parent, value))
        import posixpath
        norm = posixpath.normpath(norm)
        return norm if norm in paths else None
    import posixpath
    candidates = {posixpath.normpath(value), posixpath.normpath(parent + '/' + value)} & paths
    return next(iter(candidates)) if len(candidates) == 1 else None


def value_of(node, env):
    """Evaluate a small path-expression grammar, without executing repository code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int)):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.BinOp):
        left, right = value_of(node.left, env), value_of(node.right, env)
        if isinstance(left, str) and isinstance(right, str):
            if isinstance(node.op, ast.Div):
                return str(PurePosixPath(left) / right)
            if isinstance(node.op, ast.Add):
                return left + right
    if isinstance(node, ast.Attribute):
        base = value_of(node.value, env)
        if isinstance(base, str) and node.attr == 'parent':
            return str(PurePosixPath(base).parent)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == 'parents':
        base, index = value_of(node.value.value, env), value_of(node.slice, env)
        if isinstance(base, str) and type(index) is int and index >= 0:
            parents = PurePosixPath(base).parents
            return str(parents[index]) if index < len(parents) else None
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in {'Path', 'str'} and len(node.args) == 1:
            return value_of(node.args[0], env)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'resolve' and not node.args:
            return value_of(node.func.value, env)
    return None


def python_edges(actor, source, paths):
    tree = ast.parse(source)
    env = {'__file__': str(ROOT / actor)}
    # Module assignments only: function/local variable names are not global facts.
    for node in tree.body:
        if isinstance(node, ast.Assign):
            value = value_of(node.value, env)
            if value is not None:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        env[target.id] = value
    edges, unresolved = [], []
    lines = source.splitlines()

    def add(node, value, kind, extractor):
        target = resolve_reference(actor, value, paths)
        if target:
            edges.append((actor, target, kind, node.lineno, extractor, lines[node.lineno - 1].strip()))
        else:
            unresolved.append((node.lineno, kind, str(value).replace(str(ROOT), '<repo>') if value is not None else '<dynamic expression>'))

    for node in ast.walk(tree):
        assertion = isinstance(node, ast.Assert) or (
            isinstance(node, ast.Call) and (
                isinstance(node.func, ast.Name) and node.func.id in {'ensure', 'require'} or
                isinstance(node.func, ast.Attribute) and node.func.attr in {'assertEqual', 'assertTrue', 'assertFalse', 'assertIn', 'assertNotIn'}
            )
        )
        if assertion:
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) and child.func.attr in {'read_text', 'read_bytes', 'exists', 'is_file'}:
                    target = resolve_reference(actor, value_of(child.func.value, env), paths)
                    if target:
                        edges.append((actor,target,'VALIDATES',node.lineno,'python_assertion_path',lines[node.lineno-1].strip()))
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in WRITERS | {'read_text', 'read_bytes', 'open'}:
                value = value_of(f.value, env)
                kind = 'WRITES' if f.attr in WRITERS else 'READS'
                if f.attr == 'open' and node.args:
                    mode = value_of(node.args[0], env)
                    if isinstance(mode, str) and any(x in mode for x in 'wax+'):
                        kind = 'WRITES'
                add(node, value, kind, 'python_path_method')
            elif isinstance(f, ast.Name) and f.id == 'open' and node.args:
                mode = value_of(node.args[1], env) if len(node.args) > 1 else 'r'
                kind = 'WRITES' if isinstance(mode, str) and any(x in mode for x in 'wax+') else 'READS'
                add(node, value_of(node.args[0], env), kind, 'python_open')
            elif node.args and ((isinstance(f, ast.Name) and f.id in READERS) or (isinstance(f, ast.Attribute) and f.attr in READERS)):
                # Known repository helpers are supported by their read-oriented names;
                # retained as lower-confidence static call evidence, not runtime proof.
                add(node, value_of(node.args[0], env), 'READS', 'python_read_helper_call')
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = str(PurePosixPath(actor).parent / (alias.name.replace('.', '/') + '.py'))
                if target in paths:
                    edges.append((actor, target, 'IMPORTS', node.lineno, 'python_local_import', lines[node.lineno-1].strip()))
        if isinstance(node, ast.Dict):
            for key, val in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and isinstance(key.value, str) and isinstance(val, ast.Constant) and isinstance(val.value, str) and re.fullmatch('[0-9a-f]{64}', val.value):
                    target = resolve_reference(actor, key.value, paths)
                    if target:
                        edges.append((actor,target,'PRESERVES',key.lineno,'python_hash_pin',lines[key.lineno-1].strip()))
    return edges, unresolved


def extract(actor, source, paths):
    edges, unresolved = [], []
    suffix = PurePosixPath(actor).suffix
    lines = source.splitlines()
    if suffix == '.py':
        try:
            edges, unresolved = python_edges(actor, source, paths)
        except SyntaxError as exc:
            unresolved.append((exc.lineno or 1, 'PARSE', 'Python syntax not parsed'))
    if suffix == '.md':
        for num, line in enumerate(lines,1):
            for raw in re.findall(r'\]\(([^)]+)\)',line):
                target = resolve_reference(actor,raw,paths,document=True)
                if target:
                    edges.append((actor,target,'DOCUMENTS',num,'markdown_link',raw))
    if suffix in {'.yml','.yaml'}:
        # Literal shell commands use repository root only when no cwd override exists.
        uncertain_cwd = 'working-directory:' in source or bool(re.search(r'^\s*cd\s+',source,re.M))
        for num,line in enumerate(lines,1):
            match = re.search(r'\b(?:python3?|Rscript)\s+([\w./-]+\.(?:py|R))\b',line)
            if match:
                target = resolve_reference(actor,match[1],paths)
                if target and not uncertain_cwd:
                    edges.append((actor,target,'INVOKES',num,'workflow_literal_command',line.strip()))
                else:
                    unresolved.append((num,'INVOKES',match[1]+' (cwd override or unresolved path)'))
    # Exact path mentions are references only, regardless of neighboring prose.
    for num,line in enumerate(lines,1):
        for match in PATH_RE.finditer(line):
            raw = match.group(0)
            target = resolve_reference(actor,raw,paths)
            if target and target != actor:
                edges.append((actor,target,'REFERENCES',num,'literal_path_reference',raw))
            elif any(x in raw for x in ('{','*')):
                unresolved.append((num,'REFERENCES',raw))
    if suffix == '.json':
        # Only key -> SHA256 pairs establish preservation, not all JSON path strings.
        def visit(item):
            if isinstance(item,dict):
                for key,value in item.items():
                    if isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value):
                        target = resolve_reference(actor,key,paths)
                        if target:
                            num=next((i for i,l in enumerate(lines,1) if json.dumps(key) in l),1)
                            edges.append((actor,target,'PRESERVES',num,'json_hash_manifest',key))
                    visit(value)
            elif isinstance(item,list):
                for value in item: visit(value)
        try: visit(json.loads(source))
        except json.JSONDecodeError: unresolved.append((1,'PARSE','JSON parse failed'))
    return edges, unresolved


def build(root=ROOT):
    scope = json.loads((root/SCOPE).read_text())
    paths = {f['path'] for f in scope['files']}
    edges, uncertain = set(), {}
    for file in scope['files']:
        path=file['path']; body=frozen_source_path(root,path).read_bytes()
        if hashlib.sha256(body).hexdigest()!=file['sha256']:
            raise ValueError('frozen input drift: '+path)
        if PurePosixPath(path).suffix in TEXT_EXT:
            try: source=body.decode('utf-8-sig')
            except UnicodeDecodeError: continue
            found, unresolved=extract(path,source,paths)
            edges.update(found)
            if unresolved: uncertain[path]=sorted(set(unresolved))
    ordered=sorted(edges)
    edge_rows=[dict(edge_id=f'LE{i:06}',source=a,target=b,relationship=k,evidence_file=a,evidence_line=n,extractor=e,evidence_detail=d,confidence='static_partial' if e in {'python_read_helper_call','python_assertion_path'} else 'static_exact') for i,(a,b,k,n,e,d) in enumerate(ordered,1)]
    produced={e['target'] for e in edge_rows if e['relationship']=='WRITES'}
    mentioned={e['target'] for e in edge_rows}
    nodes=[]
    for file in scope['files']:
        p=file['path']
        nodes.append(dict(node_id=p,path=p,sha256=file['sha256'],size_bytes=file['size_bytes'],tracked=str(file['tracked']).lower(),incoming_edges=sum(e['target']==p for e in edge_rows),outgoing_edges=sum(e['source']==p for e in edge_rows),exact_static_writer_found=str(p in produced).lower(),unresolved_operation_count=len(uncertain.get(p,[])),limitation='Static partial graph; absence of edges is not proof of no dependency.'))
    counts=Counter(e['relationship'] for e in edge_rows)
    orphans=[p for p in sorted(paths) if p not in mentioned]
    lines=['# A04 — Repository lineage graph','',f"Scope: `{scope['scope_id']}` at commit `{scope['baseline_commit']}`. The frozen population contains {len(paths)} files, including F01–F06 inputs. This wave’s generated outputs and ignored files are excluded to avoid a self-changing denominator.",'','## Outputs and interpretation','',f'- [Nodes](../{NODE_OUT}): every one of the {len(paths)} frozen files exactly once.',f'- [Edges](../{EDGE_OUT}): {len(edge_rows)} evidence-bearing static edges.', '- Direction is actor/document/manifest → referenced file. `WRITES` indicates a statically resolved output operation; it does not prove execution. `READS` indicates a resolved read or named read-helper call. `IMPORTS`, `INVOKES`, `PRESERVES`, `DOCUMENTS` and `REFERENCES` retain their distinct meanings.', '- A documentation mention, hash manifest, workflow artifact upload, or source path is never converted into a producer. `PRESERVES` means a SHA-256 pin is recorded; it does not prove a check ran.', '- Source captures and binaries are nodes even when no parser can establish their producers. Sources, tests and generated artifacts are connected only where exact static evidence exists.', '- No repository script was imported or executed and no network source was accessed by this extraction.', '', '## Extraction coverage','', '| Relationship | Edges |','| --- | ---: |']
    lines += [f'| {k} | {v} |' for k,v in sorted(counts.items())]
    lines += ['', '`VALIDATES` is emitted only when an explicit assertion/guard contains a statically resolved file read or existence check. The assertion condition is retained as evidence; this marks a check relationship, not a claim that it ran or that the checked content is substantively correct. Generic validation helpers and dynamically selected files remain unresolved.']
    lines += ['', '## Key paths inspected','', '- V13 adoption: `scripts/adopt_v13_reference.py` pins V12 inputs through hash dictionaries; local imports connect its patch helper. Static output methods involving dynamically assembled maps are unresolved rather than inferred from filenames.', '- White paper: `reports/white_paper_2026-10-15/analyze.py` reads named financial and research tables; resolved `OUT` write expressions connect metrics, chart data and manifests. The publication workflow explicitly invokes analysis, charting, document construction and validation. These links do not establish fresh legal or operational verification.', '', '## Limits and unresolved dependencies','', 'The Python extractor evaluates only constants, module-level assignments, path joins, `parent`/`parents`, and simple `Path`/`str`/`resolve` expressions. It does not execute helper functions, follow arbitrary loop variables, reconstruct dynamic output maps, resolve glob populations, or perform full data-flow analysis. Named read-helper calls are explicitly lower-confidence. R and embedded Python are scanned only for exact references; R call semantics are not resolved. Workflow invocation extraction uses repository-root semantics only when no `cd` or `working-directory` override is present; overrides are held unresolved. Relative Markdown links use the containing document directory.', '', f'{len(uncertain)} files have {sum(map(len,uncertain.values()))} unresolved read/write/invocation or parse expressions. These are extraction gaps, not repository defects. The following list is exhaustive for expressions recognized by this extractor; other dynamic operations may remain undetected.', '']
    for path,items in sorted(uncertain.items()):
        lines += [f'### `{path}`',''] + [f'- Line {n}: `{kind}` — `{detail.replace(chr(10)," ").replace("`", "")}`' for n,kind,detail in items] + ['']
    lines += ['## Files without incoming static references','',f'{len(orphans)} frozen files have no incoming reference. This is an orphan-screening list, not a deletion recommendation; entrypoints, raw sources, and manually produced artifacts may legitimately appear here.','']+[f'- `{p}`' for p in orphans]
    lines += ['', '## Reproduction and validation','', 'Run `python -B scripts/build_repository_lineage.py` to rebuild, or append `--check` to compare retained outputs without changing them. Run `python -B tests/check_repository_lineage.py` for synthetic extraction controls and scope/graph checks. The generator verifies every frozen input hash and refuses input drift. New files require an explicitly refreshed audit scope, not silent inclusion.','']
    return {NODE_OUT:csv_bytes(nodes,list(nodes[0])),EDGE_OUT:csv_bytes(edge_rows,list(edge_rows[0])),DOC_OUT:('\n'.join(lines)).encode()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=build()
    for path,body in outputs.items():
        target=ROOT/path
        if args.check:
            if not target.exists() or target.read_bytes()!=body: raise SystemExit('FAIL: output drift: '+path)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(body)
    print('PASS: frozen-scope lineage '+('matches retained outputs' if args.check else 'generated'))


if __name__=='__main__': main()
