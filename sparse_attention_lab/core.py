"""Pure edge-set calculations. Edge counts do not estimate model quality."""
PATTERNS = ("diagonal", "local", "full", "strided")


class SchemaError(ValueError):
    """An input field violates the documented schema."""


def integer(value, field, low, high):
    if type(value) is not int or not low <= value <= high:
        raise SchemaError(f"field {field}: expected integer {low}..{high}")
    return value


def edges(length, pattern, window=2, stride=2):
    integer(length, "length", 1, 256)
    integer(window, "window", 1, 256)
    integer(stride, "stride", 1, 256)
    if pattern not in PATTERNS:
        raise SchemaError(f"field pattern: choose {', '.join(PATTERNS)}")
    return {(q, k) for q in range(length) for k in range(q + 1)
            if pattern == "full" or (pattern == "diagonal" and q == k)
            or (pattern == "local" and q - k < window)
            or (pattern == "strided" and (q - k) % stride == 0)}


def validate(record):
    if not isinstance(record, dict):
        raise SchemaError("field record: expected object")
    required = {"id", "synthetic", "length", "reference_edges"}
    allowed = required | {"window", "stride", "note"}
    if required - record.keys() or record.keys() - allowed:
        raise SchemaError(f"fields: missing {sorted(required - record.keys())}, unknown {sorted(record.keys() - allowed)}")
    if not isinstance(record['id'], str) or not 1 <= len(record['id']) <= 4096:
        raise SchemaError("field id: expected nonempty string, maximum 4096 characters")
    if type(record['synthetic']) is not bool:
        raise SchemaError("field synthetic: expected boolean")
    n = integer(record['length'], 'length', 1, 256)
    integer(record.get('window', 2), 'window', 1, 256)
    integer(record.get('stride', 2), 'stride', 1, 256)
    if 'note' in record and (not isinstance(record['note'], str) or len(record['note']) > 65536):
        raise SchemaError("field note: expected string, maximum 65536 characters")
    if not isinstance(record['reference_edges'], list):
        raise SchemaError("field reference_edges: expected array")
    seen = set()
    for edge in record['reference_edges']:
        if not isinstance(edge, list) or len(edge) != 2:
            raise SchemaError("field reference_edges: expected [query, key] pairs")
        q, k = edge
        integer(q, 'reference_edges.query', 0, n - 1)
        integer(k, 'reference_edges.key', 0, n - 1)
        if k > q:
            raise SchemaError("field reference_edges: future token edge is forbidden")
        if (q, k) in seen:
            raise SchemaError("field reference_edges: duplicate edge")
        seen.add((q, k))
    return record


def compare(record, pattern):
    validate(record)
    reference = {tuple(e) for e in record['reference_edges']}
    predicted = edges(record['length'], pattern, record.get('window', 2), record.get('stride', 2))
    return dict(id=record['id'], pattern=pattern, predicted_edges=len(predicted),
                reference_edges=len(reference), true_positive=len(predicted & reference),
                false_positive=len(predicted - reference), false_negative=len(reference - predicted),
                exact_match=predicted == reference,
                full_causal_edges=record['length'] * (record['length'] + 1) // 2,
                omitted_edges=record['length'] * (record['length'] + 1) // 2 - len(predicted))


def evaluate(records):
    seen = set()
    rows = []
    for record in records:
        validate(record)
        if record['id'] in seen:
            raise SchemaError(f"field id: duplicate id {record['id']!r}")
        seen.add(record['id'])
        rows.extend(compare(record, p) for p in PATTERNS)
    fields = ('predicted_edges', 'reference_edges', 'true_positive', 'false_positive', 'false_negative', 'exact_match', 'full_causal_edges', 'omitted_edges')
    return {'record_count': len(records), 'comparison_count': len(rows),
            'totals': {f: sum(row[f] for row in rows) for f in fields},
            'by_pattern': {p: {f: sum(row[f] for row in rows if row['pattern'] == p) for f in fields} for p in PATTERNS},
            'comparisons': rows}
