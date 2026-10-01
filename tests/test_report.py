from sparse_attention_lab.cli import load, write
from sparse_attention_lab.fixtures import generate, EXPECTED
from sparse_attention_lab.report import render
import json


def result(tmp_path):
    generate(tmp_path, write)
    return load(tmp_path)


def test_report_matches_ground_truth_exact(tmp_path):
    r = json.loads(render(result(tmp_path), 'json'))
    assert r['totals'] == EXPECTED['totals']
    assert len(r['sources']) == 200


def test_report_zero_false_positives(tmp_path):
    r = result(tmp_path)
    matches = [c for c in r['comparisons'] if c['exact_match']]
    assert len(matches) == 200
    assert all(c['pattern'] == ('diagonal', 'local', 'full', 'strided')[int(c['id'].split('-')[1]) % 4] for c in matches)
    assert all(c['false_positive'] == c['false_negative'] == 0 for c in matches)
    assert sum(not c['exact_match'] for c in r['comparisons']) == 600


def test_report_carries_provenance_banner(tmp_path):
    r = result(tmp_path)
    for fmt in ('md', 'json'):
        assert '200 synthetic fixture records; 0 real records' in render(r, fmt)


def test_hypothetical_figures_labelled(tmp_path):
    for fmt in ('md', 'json'):
        output = render(result(tmp_path), fmt)
        assert 'hypothetical' in output and 'unmeasured' in output


def test_no_em_dashes_in_outputs(tmp_path):
    r = result(tmp_path)
    r['sources'][0]['id'] = 'a' + chr(0x2014) + 'b'
    for fmt in ('md', 'json'):
        assert chr(0x2014) not in render(r, fmt)
