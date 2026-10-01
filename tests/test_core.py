import pytest
from sparse_attention_lab.core import SchemaError, edges, evaluate
from sparse_attention_lab.fixtures import records


@pytest.mark.parametrize('field,value', [('length', -1), ('length', True), ('length', 257), ('window', 0), ('stride', -2), ('id', ''), ('id', 'x'*4097), ('synthetic', 'yes'), ('reference_edges', [[0, 1]]), ('reference_edges', [[0, 0], [0, 0]]), ('amount', -5), ('date', '2099-01-01')])
def test_rejects_adversarial_values(field, value):
    r = records(1)[0]
    r[field] = value
    with pytest.raises(SchemaError):
        evaluate([r])


def test_duplicate_ids_rejected():
    with pytest.raises(SchemaError, match='duplicate id'):
        evaluate(records(1)*2)


def test_known_pattern_edges():
    assert edges(3, 'local') == {(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)}
    assert edges(3, 'strided') == {(0, 0), (1, 1), (2, 0), (2, 2)}


def test_corrupted_ground_truth_changes_results():
    r = records(1)
    before = evaluate(r)
    r[0]['reference_edges'] = []
    after = evaluate(r)
    assert before['totals'] != after['totals']
    assert after['totals']['true_positive'] == 0


def test_handles_unicode_and_long_inputs():
    r = records(1)
    r[0]['id'] = '研究 C:\\data\\input'
    r[0]['note'] = 'λ'*65536
    assert evaluate(r)['record_count'] == 1
