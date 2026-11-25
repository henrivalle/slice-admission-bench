# Slice Admission Bench

[English](README.md)

Benchmark para ensinar controle de admissão com duas restrições, largura de banda e computação. Ele compara a recompensa aceita por três políticas usando os mesmos orçamentos e cargas sintéticas. A execução usa a biblioteca padrão do Python 3.9 ou posterior.

```bash
python3 -m slice_admission --seed 42 --rounds 10 --requests 12 --bandwidth 16 --compute 16 > benchmark.csv
python3 -m unittest discover -s tests -v
```

O CSV tem uma linha por rodada e política, com o número de ofertas, admissões, recompensa aceita e recursos usados. Cada rodada começa com o orçamento completo. A semente fixa a sequência sintética para uma mesma versão do Python, e todas as políticas recebem as mesmas ofertas na rodada.

| Política | Entrada e comportamento |
| --- | --- |
| `fifo` | Considera as ofertas na ordem de chegada e admite as que cabem nos dois orçamentos restantes. A decisão não depende de ofertas futuras. |
| `density` | Ordena um lote conhecido por recompensa por custo normalizado de recursos e admite as ofertas que cabem. |
| `optimal` | Usa o lote completo e orçamentos inteiros para calcular a recompensa viável máxima por programação dinâmica. Serve como limite superior offline. |

O modelo usa lotes independentes com demandas inteiras e orçamentos fixos. Use orçamentos pequenos com o otimizador exato. O número de estados alcançáveis pode crescer com o produto dos dois orçamentos. O CSV ilustra as escolhas desse modelo e usa dados sintéticos em toda a execução.

## Contexto acadêmico

A pesquisa de doutorado de Henrique Valle de Lima na Universidade Federal de Goiás investigou a admissão de fatias de rede sob restrições de comunicação e processamento. Este repositório oferece uma implementação didática independente de uma versão simplificada do problema. As três políticas e as cargas sintéticas pertencem ao benchmark. A tese e os artigos descrevem os respectivos algoritmos e avaliações. [Defesa e dados bibliográficos na UFG](https://inf.ufg.br/e/34130-11-defesa-de-tese-de-doutorado-controle-de-admissao-para-network-slicing-considerando-recursos-de-comunicacao-e-computacao-henrique-valle-de-lima) · [Artigo relacionado no SBrT](https://biblioteca.sbrt.org.br/articlefile/3641.pdf)

Issues e PRs são bem-vindos em português ou inglês. Comece pelas [tarefas para iniciantes](https://github.com/henrivalle/slice-admission-bench/contribute) e veja o [guia de contribuição](CONTRIBUTING.md) para rodar o primeiro teste. O software é distribuído sob a [licença MIT](LICENSE).
