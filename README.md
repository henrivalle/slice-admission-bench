# Slice Admission Bench

[Português (Brasil)](README.pt-BR.md)

A small benchmark for teaching admission control with two constraints, bandwidth and compute. It compares how much reward three policies can accept under the same budgets and either synthetic or imported requests. Python 3.9 or newer runs it with the standard library.

```bash
python3 -m slice_admission --seed 42 --rounds 10 --requests 12 --bandwidth 16 --compute 16 > benchmark.csv
python3 -m slice_admission --rounds 2 --policy fifo
python3 -m unittest discover -s tests -v
```

Use `--policy` to run only `fifo`, `density`, or `optimal`. If it is omitted, the benchmark runs all three policies in that order, as before.

The CSV has one row per round and policy, with the number of offers, admissions, accepted reward, and resources used. Each round starts with a fresh budget. The seed fixes the synthetic sequence for a given Python version, and all policies see the same offers within a round.

| Policy | Inputs and behavior |
| --- | --- |
| `fifo` | Considers offers in arrival order and admits any offer that fits both remaining budgets. Decisions require no future offers. |
| `density` | Sorts a known batch by reward per normalized resource cost, then admits offers that fit. |
| `optimal` | Uses the complete batch and integer budgets to compute the maximum feasible reward with dynamic programming. It serves as an offline upper bound. |

The model uses independent batches with integer demand and fixed budgets. Keep budgets small when running the exact optimizer. The number of reachable states can grow with the product of the two budgets. The generated CSV reports trade-offs under these assumptions.

## Replay a workload trace

```bash
python3 -m slice_admission --trace examples/admission-trace.csv --bandwidth 3 --compute 2
```

Use a UTF-8 CSV with four positive integer columns named `round`, `bandwidth`, `compute`, and `reward`. Group rows in ascending round order and keep requests in arrival order within each round. Demand units must match the chosen budgets. Convert an anonymized resource trace into this tabular format to compare baselines on the same requests. The example is synthetic. Each round resets capacity, so the model represents independent decision windows.

## Research context

Henrique Valle de Lima's doctoral research at Universidade Federal de Goiás examined network slice admission with both communication and compute constraints. This repository supplies an independent teaching implementation of the simplified problem. The three policies and synthetic workloads shown here are for the benchmark. The thesis and papers describe their own algorithms and evaluations. [UFG thesis defense and bibliographic details](https://inf.ufg.br/e/34130-11-defesa-de-tese-de-doutorado-controle-de-admissao-para-network-slicing-considerando-recursos-de-comunicacao-e-computacao-henrique-valle-de-lima) · [Related SBrT paper](https://biblioteca.sbrt.org.br/articlefile/3641.pdf)

Issues and PRs are welcome in English or Portuguese. Start with [good first issues](https://github.com/henrivalle/slice-admission-bench/contribute) and see the [contribution guide](CONTRIBUTING.md) for a quick local test. The software is available under the [MIT license](LICENSE).
