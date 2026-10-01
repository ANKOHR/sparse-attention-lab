"""Deterministic report serialization and honest provenance."""
import json


def json_text(value):
    # Escape the prohibited punctuation even when supplied by a user.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).replace(chr(0x2014), '\\u2014') + '\n'


def render(result, format='md'):
    if format == 'json':
        return json_text(result)
    lines = ['# Sparse Attention Lab', '', result['provenance_banner'], '',
             result['measurement_boundary'], '', f"Records: {result['record_count']}",
             f"Comparisons: {result['comparison_count']}", '', '| Metric | Count |', '| --- | ---: |']
    lines += [f'| {k} | {v} |' for k, v in result['totals'].items()]
    lines += ['', 'Full per-record edge counts and source file/line provenance are available in the JSON report.', '',
              '| Pattern | TP | FP | FN | Exact matches |', '| --- | ---: | ---: | ---: | ---: |']
    lines += [f"| {p} | {t['true_positive']} | {t['false_positive']} | {t['false_negative']} | {t['exact_match']} |" for p, t in result['by_pattern'].items()]
    return '\n'.join(lines) + '\n'
