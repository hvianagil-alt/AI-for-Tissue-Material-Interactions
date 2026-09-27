# How to use TissueLab today

You do **not** need an Amass API key, Ollama, Postgres, or `python -m tissuelab.train` to use the product. The labeled table is already in `data/tissuelab.sqlite`.

## 1. Start the app

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
tissuelab-app
```

The browser opens at [http://127.0.0.1:8501](http://127.0.0.1:8501). This is a **plain HTML** Protocol page (no Streamlit websocket), so the Cursor Simple Browser and Chrome can both open it. If Chrome says `ERR_CONNECTION_REFUSED` on `localhost`, use **127.0.0.1** — Chrome tries IPv6 (`::1`) first.

In Cursor: open the **Ports** panel, find **8501**, and click the globe / Open in Browser. Or paste `http://localhost:8501/` in Cursor’s Simple Browser.

Optional Streamlit radar demo (needs a websocket; often fails in Cursor’s preview):

```bash
streamlit run app/streamlit_app.py --server.port 8502
```

## 2. What to open

| Page | Use it for | Trust it? |
|---|---|---|
| **`/` Protocol** | Cells + job → what to run this week | Ranked extracted rows. Not a written methods section |
| **`/pack`** | One-page Friday card to print | Same labels as Protocol |
| **`/api/decision`** | Same pack as JSON | Same labels as the page |
| **`/library`** | Chemistry / architecture / application tags on every harvested paper | Paper counts, not live/dead |
| **`/lookup`** | You already picked a gel | Literature lookup: yes. Not your next flask |
| **`/table`** | Every hand-extracted live/dead row (numeric + floors) | Yes — this is the product |
| **`/export.csv`** | Drop into Excel / GraphPad | Yes |
| **`/compare`** | Your gel vs GelMA + TGF-β3 | Same estimator, still literature |
| Streamlit Dataset / About | Queue + LOPO JSON | Yes |
| Inverse / next experiment | Simulator demo | No |

`?lang=pt` switches the decision copy to Portuguese. Paper titles stay as published.

To see what “training a model” means on this table: [`docs/TRAIN.md`](TRAIN.md) → `python3 -m tissuelab.teach_model`. The clean training table is `data/train_gold.csv` (split by `split_group` = paper).

## 3. Protocol — the actual workflow

1. Open `/`. Leave the defaults: **articular chondrocyte**, keep them alive, encapsulate.
2. Read **This week, run** — today that is fibrin, not GelMA. GelMA is what labs run; this table has one articular live/dead paper for GelMA.
3. Read **Do not start here** — PEG. Open `/avoid` for coverage and the next extraction holes.
4. Open the three extracted papers. Then **Search Europe PMC** if you want live literature (tagged already-in-the-table or not).
5. If you already picked a gel, open **Lookup**. The big % is a table mean, not your flask. Charts and LOPO are behind “How this number is made”.
6. **Table** / CSV for the lab meeting. **Compare** for fibrin vs GelMA + TGF-β3. `GET /api/decision` for a script.
7. Ignore Streamlit radar / inverse unless you want the demo.

If the gel you typed has **no** live/dead rows, the app falls back to the global mean and says so. Use the papers, not that number.

## 4. How to read the numbers

- **80% on GelMA** is the mean of the GelMA rows in `v_model_viability` (today: one Daly 2016 condition). It is not a prediction of your next flask.
- The band is **at least leave-one-paper-out MAE (~16 points)** and wider when that gel has one row, no kPa, or a huge spread. It is not a biological confidence interval.
- Material-class mean **barely** beats a dummy mean (16.4 vs 16.5). Ridge is worse and is not served. The scientific MVP bar (15% better than dummy, R² > 0) is **not** met.
- Competitor to beat: a PI who already runs “GelMA ~25 kPa + TGF-β3”.

## 5. Dataset tab

- `literature_viability.csv` / the on-screen table: the only training labels.
- Extraction queue: the next papers to read by hand into `src/tissuelab/curated.py`.
- Do not treat auto-promoted `pmid*` rows or regex hits as labels.

## 6. Optional API

```bash
uvicorn app.api:app --reload --port 8000
```

`POST /predict` returns `literature_viability` even if the simulator joblib is missing. Inverse/recommend need that joblib (`artifacts/tissue_interaction_model.joblib`, gitignored). Train it only if you want the radar demo:

```bash
python -m tissuelab.train
```

## 7. Do not

- Harvest more Amass papers to “make the model work”.
- Paste the Amass key into git or chat.
- Treat mapped 0–100 radar scores as measurements.
- Promote abstract regex `%` or viability floors (`>90%`) into training labels.
