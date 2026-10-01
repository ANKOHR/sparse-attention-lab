"""Local-only CLI with named errors and atomic output writes."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from .core import PATTERNS, SchemaError, edges, evaluate
from .fixtures import generate
from .report import json_text, render


class InputError(ValueError):
    pass


def write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f'WriteError: {path}: {exc}') from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f'MissingInput: {directory}: use sal fixtures --out <dir> or provide an input directory')
    records, sources, seen = [], [], set()
    for path in sorted(directory.iterdir()):
        if path.name == 'expectations.json' or path.suffix not in ('.json', '.jsonl', '.csv', '.yaml', '.yml'):
            continue
        if path.suffix != '.jsonl':
            raise InputError(f'SchemaError: {path}: line 1: field format: supported input is JSONL')
        for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise InputError(f'ParseError: {path}: line {line_number}, column {exc.colno}: {exc.msg}') from exc
            try:
                evaluate([record])
                if record['id'] in seen:
                    raise SchemaError('field id: duplicate id')
            except SchemaError as exc:
                raise InputError(f'SchemaError: {path}: line {line_number}: {exc}') from exc
            seen.add(record['id'])
            records.append(record)
            sources.append({'file': path.name, 'line': line_number, 'id': record['id'], 'synthetic': record['synthetic']})
    result = evaluate(records)
    synthetic = sum(r['synthetic'] for r in records)
    result.update(sources=sources, provenance_banner=f'Data provenance: {synthetic} synthetic fixture records; {len(records)-synthetic} real records declared by the input author (ownership not verified).',
                  measurement_boundary='Measured: exact edge-set counts against supplied references. Edge omissions are structural counts, not runtime or quality measurements. Time saved and money saved are unmeasured; any such claim would be hypothetical and is not reported.')
    return result


def parser():
    p = argparse.ArgumentParser(description='Compare causal attention edge sets on CPU. Examples: sal fixtures --out demo; sal run --input demo; sal report --format md')
    sub = p.add_subparsers(dest='command', required=True)
    f = sub.add_parser('fixtures', help='Generate 200 labelled synthetic records', epilog='Example: sal fixtures --out demo')
    f.add_argument('--out', required=True)
    r = sub.add_parser('run', help='Compute comparisons from JSONL input', epilog='Example: sal run --input demo')
    r.add_argument('--input', required=True)
    r.add_argument('--results', default='.sal/results.json')
    rep = sub.add_parser('report', help='Render computed results with provenance', epilog='Example: sal report --format json')
    rep.add_argument('--format', choices=['md', 'json'], default='md')
    rep.add_argument('--results', default='.sal/results.json')
    rep.add_argument('--out')
    pat = sub.add_parser('pattern', help='Enumerate causal attention edges', epilog='Example: sal pattern --length 4 --pattern local --window 2')
    pat.add_argument('--length', type=int, required=True)
    pat.add_argument('--pattern', choices=PATTERNS, required=True)
    pat.add_argument('--window', type=int, default=2)
    pat.add_argument('--stride', type=int, default=2)
    c = sub.add_parser('compare', help='Compare inputs without saving results', epilog='Example: sal compare --input demo --format json')
    c.add_argument('--input', required=True)
    c.add_argument('--format', choices=['md', 'json'], default='md')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'fixtures':
            generate(Path(args.out), write)
            print('Generated 200 synthetic records; no random seed is needed.')
        elif args.command == 'run':
            result = load(args.input)
            path = Path(args.results)
            path.parent.mkdir(parents=True, exist_ok=True)
            write(path, json_text(result))
            print(f"Computed {result['comparison_count']} comparisons. {result['provenance_banner']}")
        elif args.command == 'pattern':
            print(json_text({'measurement': 'Computed structural edges only; quality and speed are unmeasured.', 'edges': sorted(edges(args.length, args.pattern, args.window, args.stride))}), end='')
        else:
            if args.command == 'compare':
                result = load(args.input)
            else:
                try:
                    result = json.loads(Path(args.results).read_text(encoding='utf-8'))
                except FileNotFoundError as exc:
                    raise InputError(f'MissingInput: {args.results}: first use sal run --input <dir>') from exc
                except json.JSONDecodeError as exc:
                    raise InputError(f'ParseError: {args.results}: line {exc.lineno}: {exc.msg}') from exc
                if not isinstance(result, dict) or not all(k in result for k in ('provenance_banner', 'measurement_boundary', 'record_count', 'comparison_count', 'totals', 'by_pattern')):
                    raise InputError(f'SchemaError: {args.results}: field results: expected a saved sal run result')
            text = render(result, args.format)
            if getattr(args, 'out', None):
                write(Path(args.out), text)
            else:
                print(text, end='')
        return 0
    except (InputError, SchemaError, OSError, UnicodeError, KeyError, TypeError, AttributeError) as exc:
        print(f'{type(exc).__name__}: {exc}'.replace(chr(0x2014), '[dash]'), file=__import__('sys').stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
