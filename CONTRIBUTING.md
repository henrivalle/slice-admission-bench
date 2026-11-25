# Contributing / Como contribuir

Start with [good first issues](https://github.com/henrivalle/slice-admission-bench/contribute). A short comment with your intended approach helps others see what is in progress. Issues and pull requests are welcome in English or Portuguese.

Comece pelas [tarefas para iniciantes](https://github.com/henrivalle/slice-admission-bench/contribute). Comente brevemente como pretende trabalhar para que outras pessoas saibam o que está em andamento. Issues e pull requests são bem-vindos em inglês e português.

## First test / Primeiro teste

From a checkout of your fork, run / No clone do seu fork, execute:

```bash
python3 -m unittest discover -s tests -v
python3 -m slice_admission --seed 42 --rounds 1 --requests 4
```

The last command prints CSV with one row for each policy. Python 3.9 or newer is enough to run the current code and tests. When changing the CLI, include a reproducible command and the expected output. When changing a policy, include a small case that demonstrates its effect and respects both capacities.

O último comando mostra um CSV com uma linha por política. Python 3.9 ou superior é suficiente para executar o código e os testes. Para mudanças na linha de comando, inclua um comando reproduzível e a saída esperada. Para mudanças de política, inclua um caso pequeno que demonstre o efeito e respeite as duas capacidades.

Link to the issue from your PR and include the tests you ran. Use synthetic examples in the repository. / Vincule a issue ao PR e liste os testes executados. Use exemplos sintéticos no repositório.
