# Como se constrói e treina o modelo (aula prática)

Nunca treinaste um modelo. Não precisas de GPU, nem de ChatGPT, nem de `python -m tissuelab.train` (esse é o XGBoost do simulador).

Corre isto na raiz do repo:

```bash
pip install -e .
python3 -m tissuelab.teach_model
```

Imprime os números **da tua tabela** (`data/train_gold.csv` = `v_model_viability` com química/arquitectura/aplicação) e grava `artifacts/teach_model.json`. Não muda o que a app serve.

O plano científico está em [`ML_PLAN.md`](ML_PLAN.md). Esta página é o *como se faz em Python*.

## O que é um modelo, em três linhas

```python
model.fit(X_train, y_train)   # treinar: ajustar a função aos papers
pred = model.predict(X_test)  # usar: gel novo → viabilidade %
erro = abs(pred - y_test)     # avaliar: o paper de teste não entrou no fit
```

- **X** = o que o PI controla: família do gel, kPa, wt%, células, TGF, dias, e agora também modificação química / arquitectura / aplicação.
- **y** = `viability_pct` publicado (live/dead).
- **Treinar** = escolher os números internos da função (coeficientes do Ridge, ou os pesos do kernel no shrinkage) para X ficar perto de y **no treino**.
- **Não treinar no que queres prever.** Se o Bachmann está no teste, nenhuma linha `bachmann2020-*` pode estar no `fit`.

O modelo que a app usa hoje não chama `Ridge.fit`. Chama `shrinkage_estimate()` em `src/tissuelab/shrinkage.py`: média das condições parecidas, puxada para a média daquele gel (`N0 = 12`). Isso **já é** um modelo treinado. O `teach_model` mostra os dois.

A tabela limpa para o próximo `fit` está em `data/train_gold.csv`. Papers da harvest uniformizados: `data/papers_uniform.csv`. Não treines em `train_silver.csv`.

## Precisas de mais papers, variáveis, ou condições?

**Mais estudos (papers independentes).** Isso é o n. 15 labs ≠ 42 experiências.

| Queres treinar | Parâmetros à louca | Papers independentes para começar |
|---|---|---|
| Dummy (sempre a média) | 1 | já tens |
| Média por gel | ~1 por família | cada gel em ≥ 2 papers |
| Shrinkage servido | 11 hiperparâmetros fechados + 1 média por gel×célula | o que a app usa agora |
| Mixed model | intercepto por paper + ~5 slopes | **25** |
| Árvores (HGB, só relato) | muitas folhas | **40** (não é o começo do produto) |
| Ridge / começo de confiança | ~9 features × 10 papers/feature | **100** |
| Rede neural / GPT | milhares | não é este problema |

Ordem do que falta:

1. **Mais papers** com live/dead **numérico** (não “high viability”, não regex do abstract).
2. **Dentro** desses papers, condições que mexam em kPa, TGF, dias, encapsular vs print. Seis linhas do Bachmann não valem seis papers.
3. **Não** mais variáveis agora (passagem, densidade, porosidade). O Ridge já tem demasiados coeficientes para 15 labs e **perde** para a média.
4. Kit do ensaio (calceína vs MTT) só quando estiver preenchido — senão misturas o y.
5. **Não** mais abstracts Amass. ~12k papers colhidas sem live/dead extraído à mão não treinam nada. 2000 no modelo não é um botão — o n é papers com número na tabela ouro.

## O ciclo real neste repo

```text
paper extraído → curated.py → load_database → benchmark (LOPO) → a app serve o vencedor
```

```bash
# 1. acrescentar linhas em src/tissuelab/curated.py
python3 -m tissuelab.pipeline        # harvest → uniformizar química/estrutura/aplicação → ingest → LOPO
python3 -m tissuelab.teach_model     # a aula, split errado vs certo
```

Não há botão Train na UI. Não há GPU. `LeaveOneGroupOut(groups=study_id)` é o treino a sério — está em `src/tissuelab/benchmark.py`.

HGB é calculado no LOPO mas só entra no conjunto de deploy a ≥ 40 papers (`papers_needed_trees`). A 32 papers o mixed/shrinkage já é o estimador estável (e nesta tabela bate o dummy); a app continua a servir `shrinkage_estimate`. O começo de confiança do produto é **100 papers** (`papers_needed_beginning`), não 40, e 2000 gold não entra esta semana. Até lá, extrair papers no bairro dos géis que já tens é treinar.
