# Plano de modelo (a partir dos 3 vídeos), para este repo

Isto não é um curso. É o que os três tutoriais dizem **aplicado a** `v_model_viability` (hoje: 42 live/dead numéricos, 15 papers, shrinkage LOPO MAE ~15.8 vs dummy ~16.5, R² < 0, `mvp_pass` falso).

Vídeos digeridos:

1. [StatQuest — mixed models / HLM](https://www.youtube.com/watch?v=5tOifM51ZOk)
2. [StatQuest — cross-validation](https://www.youtube.com/watch?v=fSytzGwwBVw)
3. [Afflerbach / nanoHUB — ML workflow para propriedades de materiais](https://www.youtube.com/watch?v=qg3ju4nqqoQ)

O produto que o PI usa (`protocol_finder`, busca de papers) **não espera** por este plano. O número em `/lookup` só muda de estimador quando o LOPO mandar.

Se nunca treinaste um modelo: `docs/TRAIN.md` e `python3 -m tissuelab.teach_model` (Python, a tua tabela, split errado vs LOPO).

---

## 1. O que cada vídeo realmente ensina

### 1.1 Mixed models (StatQuest)

A lição não é “usa `lmer`”. É: **linhas do mesmo cluster não são experiências independentes**.

- Duplicar o dataset baixa o p-value à força. Tratar 6 condições do Bachmann 2020 como 6 papers é a mesma batota: mesma célula, mesmo kit, mesmo laboratório, mesmo enviesamento de figura.
- Clustering típico do vídeo: irmãos, o mesmo sujeito em t=1 e t=6 meses, alunos da mesma professora, doentes do mesmo hospital.
- **Duas consequências** se ignoras o cluster: (1) p-values / R² demasiado optimistas; (2) podes inverter o efeito real (o exemplo dos hospitais: a recta preta diz “sintomas graves → mais sobrevivência”; dentro de cada hospital a recta é negativa).
- Mixed model = rectas por cluster (efeitos aleatórios) + média entre clusters (efeito fixo). A recta do cluster é **puxada para a média** (shrinkage). Ele diz isso no caveat técnico.
- Quase sempre: **intercepto aleatório**. Slope aleatório só se tens dados e uma razão teórica. Slope fixo = o efeito (TGF, kPa) é o mesmo em todos os labs; intercepto aleatório = cada paper tem o seu baseline de viabilidade.

**No TissueLab, hoje:**

| Vídeo | O teu caso |
|---|---|
| Cluster | `study_id` (o paper / o lab) |
| Observação dentro do cluster | uma linha de `literature_viability.csv` (gel × kPa × dia) |
| “Irmão” | Aitchison d1 / d7 / d14 — três linhas, um protocolo |
| Hospital de In-N-Out vs University Medical | Ortega 2024 ~99% vs Hu 2012 5–85% no mesmo “chitosan*”: o lab, o crosslinking e o ensaio dominam o gel |
| Recta preta enganadora | Ridge LOPO MAE 22.6, pior que a média: aprende ruído de paper |
| Shrinkage das rectas para a média | exactamente `shrinkage.py`: média local do kernel + prior da família do gel, com `N0 = 12` |
| Intercepto aleatório | o baseline do paper (ainda não está explícito num `MixedLM`; o shrinkage faz um primo empírico) |
| Slope fixo | efeito de TGF / kPa / dias, **se** um dia houver papers suficientes para o estimar sem o confundir com o lab |
| Slope aleatório | **proibido agora**. 15 clusters. O vídeo diz: às vezes nem tens escolha, não há dados para libertar o slope |

O Daly 2016 é o exemplo perfeito de “duplicar”: quatro géis (agarose, alginate, GelMA, PEGMA) todos a 80%. Um random split 80/20 pode pôr três no treino e GelMA no teste e o modelo “acerta” GelMA=80 sem ter visto nada de GelMA noutro lab.

### 1.2 Cross-validation (StatQuest)

A lição: precisas dos dados **duas vezes** — treinar (estimar parâmetros) e testar (ver se generaliza). Reusar o mesmo conjunto para as duas coisas é a pior ideia. Um único corte 75/25 é arbitrário, por isso rodas os blocos.

- 4-fold / 10-fold: cada bloco é teste uma vez.
- Leave-one-out extremo: **um bloco = uma amostra**.
- Tuning (λ do Ridge, número de árvores): também por CV, não “à olho no conjunto que vais servir”.

**O que o vídeo *não* diz, e que é o teu caso:** o bloco não é a linha, é o paper.

| StatQuest | Errado aqui | Certo aqui |
|---|---|---|
| Bloco = paciente | Bloco = linha de viabilidade | Bloco = `study_id` |
| 10-fold aleatório | `train_test_split` 90/10 como o Afflerbach | `LeaveOneGroupOut` / o loop que já está em `benchmark.py` |
| LOOCV | deixar de fora `bachmann2020-fibrin-1kpa` e treinar nas outras 5 do Bachmann | deixar de fora **o Bachmann inteiro** |
| Comparar métodos no teste | comparar Ridge no treino | comparar dummy vs material-mean vs shrinkage vs (mais tarde) misto / HGB **no LOPO** |
| Tunar λ | retunar `N0` / `TAU_KPA` na query do PI | hiperparâmetros **fechados**; se um dia reabrires, nested LOPO (loop de fora = paper, loop de dentro = λ) |

Já tens isto: `leave_one_paper_out()` em `src/tissuelab/benchmark.py` e `lopo_shrinkage_predictions()` em `src/tissuelab/shrinkage.py`. O Afflerbach, no notebook, faz split **aleatório 10%**. Essa parte **não se copia**. Ele próprio mostra que com n=467 o teste já não espelha o treino; tu tens n=42 e clusters.

### 1.3 Workflow de materiais (Afflerbach)

Ele prevê **band gap a partir da composição**. Sete passos. ML = encontrar padrões; supervisionado; regressão (número contínuo) vs classificação (isolante/condutor); árvores → random forest. Nunca confies no CSV que te deram.

Tradução directa:

| Passo Afflerbach | Band gap | TissueLab |
|---|---|---|
| 1. Limpar | duplicados do mesmo composto; ficar com `reliability=1`; média se empatar; histogramas; n=467 já é “pouquinho” e desequilibrado nos band gaps baixos | uma condição publicada = uma linha; **não** médias o Bachmann 1 kPa com o 30 kPa (são géis diferentes); **não** metas regex de abstracts (`pmid*`); histograma da viabilidade está empilhado em 80–99% com mortes raras (Hu 5%, PEG_dextran 5%) |
| 2. Gerar features | 87 Magpie: média composicional de número atómico, raio, T de fusão… | **não uses Magpie em “GelMA”**. Features = o que o PI controla: `material_class`, `stiffness_kpa`, `polymer_concentration_wt_pct`, `cell_type`, `growth_factor`, `culture_time_days`, `culture_model` (2D / encapsular / print). Analogia da pergunta do chat (“e a estrutura cristalina?”): 2D vs 3D e o crosslinking são a tua “estrutura”. Sem isso o modelo acha que chitosan do Hu = chitosan_gelatin_PVA do Ortega |
| 3. Feature engineering | tirar constantes; tirar colunas correlacionadas; normalizar | `stiffness_kpa` e `wt%` no Bachmann são quase a mesma variável (1.5%→1 kPa, 5%→30 kPa). Ridge já faz scale. Árvores não precisam. O kernel do shrinkage usa `TAU_KPA=20` e `TAU_DAYS=21` em vez de z-score |
| 4. Avaliação | split aleatório 10% | **LOPO**. Ponto. |
| 5. Modelo default | 1 árvore: treino RMSE≈0, teste RMSE≈1.2 → overfit | Ridge já é esse gráfico: memoriza o paper, rebenta no paper seguinte |
| 6. Optimizar | mais árvores; o treino piora um pouco, o teste melhora — é isso que queres | só depois de haver dados; e o “número de árvores” só se escolhe **dentro** do LOPO, nunca olhando para o LOPO final |
| 7. Prever / voltar ao lab | “serve para célula solar?” define o target | o PI pergunta: *as minhas células, esta semana, vivo / print / matriz* — isso já é `find_protocol()`. A regressão de live/dead é o analogo do band gap; o ranking de protocolos é o produto |

Outras frases dele que importam:

- **Não confies nos dados.** A view `v_model_viability` é a única tabela de treino. `paper_extractions` e `v_auto_viability` são ruído com cara de número.
- **Desequilíbrio.** Ele não subsample com n pequeno. Tu também não: não apagues as mortes (são os únicos sinais), não clones as linhas a 90%.
- **Não podes prever o que não está no y.** Direct vs indirect band gap: sem coluna, impossível. sGAG, COL2, “vai imprimir bem”: modelos **separados** ou, até haver n, o ranking do `protocol_finder` (contagens, não regressão).
- **Active learning ≠ supervised.** Supervised = tens y. Active learning = escolhes a próxima experiência para reduzir incerteza. O loop do lab no `ROADMAP.md` (série GelMA/fibrin, `study_id = labpilot_YYYY`) é isso. Não é “meter o modelo a aprender sozinho com abstracts”.

Ele fala em n=467 como regime de dados pequenos. Tu estás uma ordem de grandeza abaixo. Random forest, no vídeo, só ganha ao overfit da árvore única porque tem *centenas* de compostos e *dezenas* de features contínuas baratas. Aqui o n efectivo é o número de papers (15), não 42.

---

## 2. O que já está feito (não recomeçar)

Isto já *é* o modelo correcto para o n actual:

- Target: `viability_pct` em `data/literature_viability.csv` / `v_model_viability`.
- Estimador servido: empirical Bayes em `src/tissuelab/shrinkage.py` (kernel + prior da família, `N0=12`).
- Competidores no LOPO: dummy, média por `material_class`, Ridge. Shrinkage ganha por ~0.7 MAE. Ridge perde. `mvp_pass` continua falso (precisa MAE ≤ 85% do dummy **e** R² > 0).
- Produto do PI: `src/tissuelab/protocol_finder.py` + `lit_search.py`. Não é um LLM.

Não treines XGBoost / rede / fine-tune em cima disto até o gate da Fase C.

---

## 3. Plano, por fases, com gates

Cada fase tem uma saída mensurável. Se o gate falha, **não** passes à seguinte. O PI continua a usar o finder.

### Fase A — limpar e ver (esta semana, 0 treino novo)

Objectivo Afflerbach passo 1–3 + mixed-model “não duplicates”.

1. Histograma de `viability_pct` e tabela `study_id × n_rows × mean ± sd`. Esperado: massa em 80–99%, 15 barras, Daly todo em 80, Bachmann com o PEG a 5%.
2. Missingness: quantas linhas têm `stiffness_kpa`, `wt%`, `culture_time_days`, `growth_factor`, `culture_model`. O kernel já penaliza kPa/dias em falta; o Ridge imputa mediana — isso **inventa** 25 kPa. Não sirvas Ridge enquanto a fracção sem kPa for alta.
3. Correlação `stiffness_kpa` vs `polymer_concentration_wt_pct` **dentro do mesmo paper**. Se for ~1, no modelo tabular usa **um** dos dois, não os dois.
4. Regra de ouro da linha: mesma fórmula + mesmo kPa + mesmo dia + mesmo paper → **uma** linha (média se o paper reporta réplicas). kPa diferentes → linhas diferentes. Papers diferentes do mesmo gel → linhas diferentes com `study_id` diferente.
5. **Não** extraías os 40 primeiros da `extraction_queue.csv` às cegas. A queue está cheia de menisco, lenhina, PVA tribologia, in vivo. Filtro de extração:

   - células: articular / auricular / MSC em contexto de cartilagem
   - 3D encapsular ou print (2D só se o PI o pedir; não treina o modelo de encapsulação)
   - gel da lista `LAB_GELS` em `protocol_finder.py` (fibrin, GelMA, HA, alginate, chitosan, agarose, PEG, composites desses)
   - **número** de live/dead (ou calceína) no texto/tabela, não “high viability”
   - um `study_id` por paper; cada condição = `experiments` row; o % vai para `measurements` com `assay=viability_pct`

   Preferir papers com fulltext aberto (Europe PMC) e já ligados na harvest. Recusar: só in vivo, só fármaco sem gel, só abstract com regex.

**Gate A:** um CSV/relatório de cobertura (n por gel × célula × 2D/3D) e a queue filtrada. Sem modelo novo.

### Fase B — mais labels, mesmo estimador (2–3 semanas)

Objectivo: o n que o Afflerbach diria “ainda pequeno, mas já se vê um padrão”, e que o ROADMAP já pedia.

- Meta: **≥ 25 papers, ≥ 80 live/dead numéricos, ≥ 40 com kPa**.
- Só `src/tissuelab/curated.py` (ou o sítio onde as linhas hand-curated entram). Depois:

```bash
python3 -m tissuelab.load_database
python3 -m tissuelab.benchmark
```

- Não retunes `N0`, `TAU_KPA`, `TAU_DAYS` para “passar o mvp”. Isso é o pecadilho do StatQuest (usar o teste para escolher o λ).
- Opcional: campo `live_dead_kit` (calceína vs MTT vs trypan). MTT e live/dead **não** são o mesmo y. Se o kit for misturado, o dummy fica mais difícil de bater por razões erradas.

**Gate B:** `n_studies ≥ 25` e `n_rows ≥ 80`. Re-corre LOPO. Se o shrinkage **piorar** vs dummy, o lote novo está sujo (kits misturados, 2D+3D, figura mal lida) — corrige dados, não o modelo.

### Fase C — o mixed model a sério (só depois do gate B)

Objectivo StatQuest: intercepto aleatório por paper, slopes fixos.

Candidato novo em `benchmark.py`, **ao lado** do shrinkage, nunca no sítio do shrinkage até ganhar:

```text
viability_pct ~ material_class + cell_type + growth_factor
                + stiffness_kpa + culture_time_days
                + (1 | study_id)
```

- Primeiro `statsmodels.regression.mixed_linear_model.MixedLM` (ou `lme4` num script R). Sem `(stiffness | study_id)`.
- LOPO: para cada paper deixado de fora, fita o misto **só nos outros papers**, prevê o held-out. Papers não são um nível que o modelo “conhece” no teste — no teste usas só o **efeito fixo** (a recta preta). Isso é o analogo honesto de “lab novo”.
- Compara MAE/R² com dummy, material-mean, shrinkage.
- Se o misto ganhar, passa a ser o `deployed_estimator`. Se perder, fica no JSON e a UI continua com shrinkage.

Isto **é** o “treinar AI” correcto neste n: um modelo hierárquico, não uma rede.

**Gate C (MVP científico, já escrito no ROADMAP):**

- n_studies ≥ 25 (idealmente rumo a 40)
- LOPO MAE do estimador servido ≤ 85% do dummy (~14.0 se o dummy continuar ~16.5)
- LOPO R² > 0

Se falhar, volta à extração. Não abras o forest.

### Fase D — tabular ML, Afflerbach-style, com o CV do StatQuest à séria

Só se C passou. Senão estás a reproduzir o gráfico dele: treino perfeito, teste lixo — e o Ridge já te mostrou isso.

1. Features fechadas (poucas): as de `FEATURES_NUM` + `FEATURES_CAT` **mais** `growth_factor` e `culture_model`. Nada de 87 colunas Magpie.
2. Pipeline sklearn (já tens o esqueleto em `_pipe()`): impute+scale no numérico, one-hot no categórico, **dentro** do pipeline, para não haver leakage de mediana do teste.
3. Modelo default: `HistGradientBoostingRegressor` **ou** `RandomForestRegressor` com `max_depth=2`, `min_samples_leaf` alto (tipo 8–12). Equivale à “uma árvore rasa”, não à árvore profunda que no vídeo tem RMSE de treino 0.
4. Avaliação: `LeaveOneGroupOut(groups=study_id)`. Parity plot **só** desses pontos held-out (o da direita no vídeo). Ignora o parity do treino.
5. Nested, se tocares em n_estimators / learning_rate:

   - loop de fora: cada paper é teste
   - loop de dentro: nos papers de treino, GroupKFold para escolher hiperparâmetros
   - o papel de fora **não** entra no tuning

6. Deploy rule, igual à de agora: só substitui shrinkage se o MAE LOPO for menor **e** R²>0. Caso contrário o forest fica no `honest_benchmark.json` como o Ridge (relatado, não servido).

Não uses XGBoost no simulador (`src/tissuelab/train.py`) como prova. Esse R² ~0.92 é biologia fingida.

### Fase E — o loop do Afflerbach passo 7 (o produto)

O modelo existe para mudar a experiência da semana.

1. O finder já escolhe gel + TGF + encapsular/print. Mantém-no como UI principal.
2. O número de `/lookup` usa o vencedor LOPO, com a banda ≥ MAE LOPO (já em `adaptive_band`).
3. Série de laboratório **nunca** no treino: `study_id = labpilot_YYYY`, 4 rigidezes, mesmas células, live/dead d1 e d7. Treina sem ela, testa nela. Se perder para “GelMA 10–25 kPa + TGF-β3”, não há empresa — está no ROADMAP.
4. Active learning simples, sem biblioteca nova: a próxima extração / o próximo gel do lab é onde o shrinkage tem `n_eff_same` baixo **ou** a banda está larga. Não é incerteza de GP; é o `n_eff_same` que já calculas.

---

## 4. Semana a semana (concreto)

| Semana | Fazes | Não fazes |
|---|---|---|
| 0 | Ler este doc com os 3 vídeos abertos. Correr `python3 -m tissuelab.benchmark` e abrir `artifacts/honest_benchmark.json`. Histograma + missingness. | Fine-tune, sklearn extra, Magpie, Ollama |
| 1–2 | Extrair 8–12 papers que passem o filtro (GelMA/fibrin/HA/alginate/agarose/chitosan × condrócito/MSC, live/dead numérico). Recarregar DB + LOPO. | Promover `pmid*` para treino |
| 3 | Deve estar ~25 papers / ~80 rows. Relatório: dummy vs shrinkage vs material-mean. | Retunar `N0` |
| 4 | MixedLM + LOPO no `benchmark.py`. Se ganhar, ligar na literature card. | Random forest |
| 5+ | Só se gate C: HGB raso + nested LOPO. Série de lab como teste externo. | Rede, LLM-as-label, novo tecido |

Tempo de extração honesto: 1.5–3 h/paper se fores só a tabelas/texto. 12 papers ≈ uma semana focada, não “o modelo aprende sozinho”.

---

## 5. Mapeamento ficheiro a ficheiro

| Trabalho | Ficheiro |
|---|---|
| Labels | `src/tissuelab/curated.py` → `data/literature_viability.csv` |
| Queue (candidatos, não labels) | `data/extraction_queue.csv` |
| Estimador actual | `src/tissuelab/shrinkage.py` |
| LOPO / dummy / Ridge | `src/tissuelab/benchmark.py` |
| Cartão do número | `src/tissuelab/literature_model.py` |
| O que o PI faz esta semana | `src/tissuelab/protocol_finder.py` |
| Métrica gravada | `artifacts/honest_benchmark.json` |
| Testes que tens de continuar verdes | `tests/test_shrinkage.py`, `tests/test_literature_model.py`, `tests/test_mvp_pipeline.py` |

Quando adicionares o MixedLM, a regra é a mesma do Ridge: entra em `leave_one_paper_out()`, ganha sítio no `candidates`, os testes passam a afirmar “misto reportado”; só mudas `deployed_estimator` se o MAE o mandar.

---

## 6. Frases para não esquecer

- 42 linhas ≠ 42 experiências. São 15 labs. O n do modelo é 15.
- Shrinkage **já é** o mixed model pobre: prior do gel + puxão local. O vídeo de HLM explica porque é que isso é mais honesto que uma floresta.
- O split aleatório do notebook de band gap, neste repo, é um bug.
- Treinar uma rede ou um GPT nos 8.5k abstracts prevê texto, não live/dead do próximo gel.
- O produto vendável, enquanto R² < 0, é o protocolo ranqueado + papers. O regressor é um lookup com incerteza. Os dois coexistem; só o segundo é que este plano mexe, e só depois dos gates.
