"""Synthetic fixtures with manually enumerated reference sets; no randomness."""
from .report import json_text

REFERENCES = (
    [[0, 0], [1, 1], [2, 2], [3, 3]],
    [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2], [3, 2], [3, 3]],
    [[0, 0], [1, 0], [1, 1], [2, 0], [2, 1], [2, 2], [3, 0], [3, 1], [3, 2], [3, 3]],
    [[0, 0], [1, 1], [2, 0], [2, 2], [3, 1], [3, 3]],
)
EXPECTED = {'synthetic': True, 'record_count': 200, 'comparison_count': 800,
            'totals': {'predicted_edges': 5400, 'reference_edges': 5400,
                       'true_positive': 4250, 'false_positive': 1150,
                       'false_negative': 1150, 'exact_match': 200,
                       'full_causal_edges': 8000, 'omitted_edges': 2600}}


def records(count=200):
    return [dict(id=f'synthetic-{i:03}', synthetic=True, length=4,
                 reference_edges=REFERENCES[i % 4], note='Synthetic planted reference') for i in range(count)]


def generate(directory, write):
    directory.mkdir(parents=True, exist_ok=True)
    write(directory / 'records.jsonl', '# Synthetic fixture data\n' + ''.join(json_text(r).replace('\n', '') + '\n' for r in records()))
    write(directory / 'expectations.json', json_text(EXPECTED))
    write(directory / 'five-records.json.example', json_text({'synthetic': True, 'records': records(5)}))
    write(directory / 'GROUND-TRUTH.md', '# Synthetic hand-computed ground truth\n\n50 records per reference: diagonal (4 edges), local (7), full (10), strided (6).\nEach record predicts 4+7+10+6=27 edges. Total predicted=200*27=5400.\nIntersection sums per reference: 16,22,27,20. TP=50*(16+22+27+20)=4250.\nFP=5400-4250=1150; FN=5400-4250=1150. Exact matches=4*50=200.\nFull causal baseline=800*10=8000. Omitted edges=8000-5400=2600.\nThe three other candidates per record are planted nonmatches: 600 true negatives, zero false positive exact-match detections.\n')
