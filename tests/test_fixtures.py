import json
from sparse_attention_lab.fixtures import EXPECTED, generate, records
from sparse_attention_lab.cli import write
from sparse_attention_lab.core import evaluate


def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path, write)
    assert (tmp_path/'records.jsonl').read_text().startswith('# Synthetic')
    assert all(r['synthetic'] is True for r in records())
    assert json.loads((tmp_path/'expectations.json').read_text())['synthetic'] is True
    assert 'Synthetic' in (tmp_path/'GROUND-TRUTH.md').read_text()


def test_fixture_ground_truth_matches_hand_computed():
    result = evaluate(records())
    for k in ('record_count', 'comparison_count', 'totals'):
        assert result[k] == EXPECTED[k]
