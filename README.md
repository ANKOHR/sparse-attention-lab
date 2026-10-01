# Sparse Attention Lab

A deterministic, CPU-only Python CLI for comparing causal attention patterns with explicit reference edges. It measures structure, not model accuracy. No dependencies, network calls, model calls, GPU workloads, or database servers are used.

Hypothesis: exact, tested comparisons against user-supplied references make a trustworthy structural comparison tool. Acceptance: 200 planted records, exact hand-computed totals, all 200 planted exact matches found, zero false positive exact-match detections, and a full demo under five seconds. Candidate edge false positives are a separate metric and are expected when a candidate differs from the reference.

## Quickstart

From this directory, with Python 3.10 or newer and setuptools already installed:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
$salScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$env:Path = "$salScripts;$env:Path"
sal.exe fixtures --out demo
sal.exe run --input demo
sal.exe report --format md
python -m pytest -q
```

PowerShell reserves `sal` as an alias for `Set-Alias`. Use `sal.exe` in PowerShell; other shells can use `sal`. The setup above adds the Python user scripts directory to the current session's PATH. Alternatively use `python -m sparse_attention_lab.cli` for every command.

The smallest input is one JSONL file. A tiny hand-written five-record synthetic input is provided in `examples/tiny/records.jsonl`:

```powershell
sal.exe run --input examples/tiny
sal.exe report --format md
```

## Input reference

Only UTF-8 JSONL is supported. Each nonblank, noncomment line is one object. Lines beginning with `#` are comments. Files are processed in filename order and records in line order. `expectations.json` is fixture metadata and is never consumed as input. Other `.json`, `.csv`, `.yaml`, or `.yml` files cause a named unsupported-format schema error; other extensions are ignored.

```json
{"id":"my-case","synthetic":false,"length":4,"window":2,"stride":2,"reference_edges":[[0,0],[1,1],[2,2],[3,3]],"note":"Henry's hand-entered reference"}
```

Required: `id` (unique string, 1..4096 characters), `synthetic` (boolean declaration), `length` (integer, 1..256), `reference_edges` (unique pairs of integer query/key indices with 0 <= key <= query < length). Optional: `window` and `stride` (integers, 1..256, default 2), `note` (string up to 65536 characters). Empty reference arrays are valid. Unknown fields, duplicate IDs/edges, future-token edges, negative values, booleans in integer fields, and oversized fields are rejected. Dates and money are outside this schema and are rejected as unknown fields. Real ownership is declared by the author, never inferred. Real trial inputs and results should stay local and should not be shipped.

Patterns: diagonal includes only query=key; local includes query-key < window; full includes every causal edge; strided includes (query-key) modulo stride=0. These are causal structural masks, not an implementation of an attention kernel. TP is intersection size, FP is predicted minus reference size, FN is reference minus predicted size. Exact match means set equality. Counts aggregate across comparisons, so each reference appears four times. `omitted_edges` counts omitted edges relative to a full causal mask, not time or memory saved.

## Commands

Every command provides `--help` and an example.

```powershell
sal.exe fixtures --out demo
sal.exe run --input demo --results .sal/results.json
sal.exe report --format json --results .sal/results.json --out report.json
sal.exe pattern --length 8 --pattern local --window 3
sal.exe compare --input examples/tiny --format md
```

`fixtures` generates the labelled 200-record fixture, an expectations file, hand arithmetic, and a five-record example. `run` saves computed results atomically, replacing the last result. `report` renders that saved snapshot without recomputing inputs. `pattern` enumerates one mask. `compare` computes and renders without saving. JSON reports include every comparison and source filename/line; Markdown gives totals and per-pattern counts. Parse errors name file and line; schema errors name offending fields. Missing paths produce nonzero exits with usage hints. Write failures leave no partial output file. Do not place a generated report inside an input directory.

## Architecture

```text
JSONL files -> cli.load (parse + validate + provenance)
           -> core.evaluate -> core.compare -> core.edges
           -> atomic results.json -> report.render -> Markdown / JSON
fixtures.generate -> labelled records + independent expectations
```

## Honesty boundary and fixture labels

Every figure is computed from explicit inputs. No model-quality, discovery, prediction, speedup, time-saved, or money-saved claims are made. Those quantities are unmeasured; any illustrative claim about them would be hypothetical. Omitted edges do not imply kernel speedups. The fixture is synthetic, not experimental model evidence. JSONL carries a synthetic header and every record has `synthetic: true`; JSON metadata and the example carry that field; fixture Markdown names itself synthetic. Reports give synthetic and declared-real record counts. No randomness is used, so there is no seed. Output is deterministic and timestamps are omitted. User-supplied prohibited punctuation is escaped in JSON outputs.

## Evidence and limitations

The independent arithmetic in fixture `GROUND-TRUTH.md` gives 5400 predicted and reference edges, 4250 TP, 1150 FP, 1150 FN, and 200 exact matches across 800 comparisons. Tests alter reference edges and verify changed figures, rather than trusting expectation metadata. The five-record example supports basic manual checking. Runtime evidence is recorded in `EVIDENCE.md`; it is one local wall-clock measurement, not a general speed guarantee.

Failure modes: incorrect hand-entered references produce incorrect interpretations despite correct arithmetic; author provenance declarations cannot verify ownership; dense Python sets use quadratic work and memory (length capped at 256); input size is otherwise unrestricted; multi-file fixture generation is not transactional although each file write is atomic. No actual tensors, learned attention scores, kernel latency, or downstream model quality are evaluated. An empty directory produces zeros. Unsupported formats are rejected rather than guessed.

## Two-week improvement hook and verdict

After Henry's first real use, record its date and a 14-day review date in `USAGE.md`. Hand-check a sample of comparisons and measure error rate = incorrect comparisons / checked comparisons. Record numerator, denominator, uses, and concrete failures. If error exceeds 10 percent, fix the top measured cause and repeat the hand check, or kill with the reason. If never used, kill. Real trial results stay local.

Verdict is pending the real-use evidence window; no two-week outcome is invented. At review: expand for daily use or revenue; integrate for heavy sibling overlap; commercialise for a buyer willing to pay as-is; maintain as portfolio evidence if otherwise useful; kill for no use or unmet acceptance criteria. Record the chosen verdict, evidence, and reason in `VERDICT.md`.
