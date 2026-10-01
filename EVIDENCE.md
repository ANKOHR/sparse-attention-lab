# Local build evidence

Measured on 2026-10-01 on this Windows host, Python 3.12.10, CPU only.

Installed-command demo: `sal.exe fixtures --out demo`, `sal.exe run --input demo`, `sal.exe report --format md`. PowerShell Stopwatch measured the complete sequence including process startup and Markdown console rendering: 1.2521435 seconds. This is a single local measurement, not an estimated speedup or a universal performance claim.

Computed fixture results: 200 records, 800 comparisons, 5400 predicted edges, 5400 reference edges, 4250 TP, 1150 FP, 1150 FN, 200 exact matches, 8000 full-causal baseline edges, and 2600 omitted edges. Tests separately check all 200 planted matching candidates and all 600 planted nonmatching candidates: zero false positive exact-match detections. Edge FP counts describe different masks and are not false match detections.

The hand-written five-record demo also ran through the installed executable without a traceback: 20 comparisons, 44 predicted edges, 28 reference edges, 26 TP, 18 FP, 2 FN, 8 exact matches. Different patterns coincide for short sequences, so a reference can have multiple exact matches.

No real-use trial, kernel runtime baseline, model-quality evaluation, or two-week adoption evidence has been measured. The improvement verdict remains pending.
