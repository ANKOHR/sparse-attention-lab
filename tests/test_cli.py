import json
import time
import pytest
from sparse_attention_lab.cli import main, load, write, InputError
from sparse_attention_lab.fixtures import generate


def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start = time.perf_counter()
    assert main(['fixtures', '--out', 'demo']) == 0
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--format', 'md']) == 0
    assert time.perf_counter() - start < 5
    assert 'Data provenance:' in capsys.readouterr().out


def test_empty_input_renders_without_traceback(tmp_path):
    r = load(tmp_path)
    assert r['record_count'] == 0
    assert all(v == 0 for v in r['totals'].values())


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path/'bad.jsonl').write_text('# Synthetic\n{broken}\n')
    assert main(['run', '--input', str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert 'ParseError' in err and 'bad.jsonl' in err and 'line 2' in err
    assert 'Traceback' not in err


def test_determinism_byte_identical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/'demo', write)
    main(['run', '--input', 'demo'])
    first = (tmp_path/'.sal/results.json').read_bytes()
    main(['run', '--input', 'demo'])
    assert first == (tmp_path/'.sal/results.json').read_bytes()


def test_cli_smoke_all_subcommands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for command in ('fixtures', 'run', 'report', 'pattern', 'compare'):
        with pytest.raises(SystemExit) as exc:
            main([command, '--help'])
        assert exc.value.code == 0
    assert main(['fixtures', '--out', 'demo']) == 0
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--format', 'json']) == 0
    assert main(['pattern', '--length', '4', '--pattern', 'strided']) == 0
    assert main(['compare', '--input', 'demo']) == 0


def test_write_failure_no_partial_files(tmp_path):
    with pytest.raises(InputError, match='WriteError'):
        write(tmp_path/'missing'/'report.md', 'content')
    assert list(tmp_path.iterdir()) == []


def test_missing_input_and_schema_errors(tmp_path, capsys):
    assert main(['run', '--input', str(tmp_path/'missing')]) == 2
    assert 'MissingInput' in capsys.readouterr().err
    (tmp_path/'bad.jsonl').write_text('{"id":"x"}\n')
    assert main(['run', '--input', str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert 'SchemaError' in err and 'fields' in err and 'line 1' in err


def test_real_provenance_and_windows_unicode(tmp_path):
    r = {'id': '研究 C:\\Users\\henry', 'synthetic': False, 'length': 1, 'reference_edges': [[0, 0]]}
    write(tmp_path/'real.jsonl', json.dumps(r, ensure_ascii=False)+'\n')
    assert '1 real records' in load(tmp_path)['provenance_banner']


def test_invalid_saved_report_named_error(tmp_path, capsys):
    path = tmp_path/'invalid.json'
    path.write_text('[]')
    assert main(['report', '--results', str(path)]) == 2
    assert 'SchemaError' in capsys.readouterr().err
    assert main(['report', '--results', str(tmp_path/'missing.json')]) == 2
    assert 'MissingInput' in capsys.readouterr().err


def test_report_write_failure_preserves_existing_output(tmp_path, capsys):
    generate(tmp_path/'demo', write)
    assert main(['run', '--input', str(tmp_path/'demo'), '--results', str(tmp_path/'results.json')]) == 0
    target = tmp_path/'existing-directory'
    target.mkdir()
    before = set(tmp_path.iterdir())
    assert main(['report', '--results', str(tmp_path/'results.json'), '--out', str(target)]) == 2
    assert 'WriteError' in capsys.readouterr().err
    assert set(tmp_path.iterdir()) == before
