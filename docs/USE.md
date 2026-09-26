# How to use TissueLab today

You do **not** need an Amass API key, Ollama, Postgres, or `python -m tissuelab.train` to use the product. The labeled table is already in `data/tissuelab.sqlite`.

## 1. Start the app

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
tissuelab-app
```

The browser opens at [http://localhost:8501](http://localhost:8501). This is a **plain HTML** Predict page (no Streamlit websocket), so the Cursor Simple Browser and Chrome can both open it.

In Cursor: open the **Ports** panel, find **8501**, and click the globe / Open in Browser. Or paste `http://localhost:8501/` in Cursor’s Simple Browser.

Optional Streamlit radar demo (needs a websocket; often fails in Cursor’s preview):

```bash
streamlit run app/streamlit_app.py --server.port 8502
```

## 2. What to open

| Page | Use it for | Trust it? |
|---|---|---|
| **`/` Predict** | Evidence card for the gel you would run Friday | Literature lookup: yes. Not your next flask |
| **`/table`** | Every hand-extracted live/dead row (numeric + floors) | Yes — this is the product |
| **`/export.csv`** | Drop into Excel / GraphPad | Yes |
| **`/compare`** | Your gel vs GelMA + TGF-β3 | Same estimator, still literature |
| Streamlit Dataset / About | Queue + LOPO JSON | Yes |
| Inverse / next experiment | Simulator demo | No |

`?lang=pt` switches chrome to Portuguese. Scientific notes stay in English (that is the language of the papers).

## 3. Predict — the actual workflow

1. Leave the defaults the first time: **GelMA**, ~25 kPa, articular chondrocyte, 14 days.
2. Read the estimate and the **adaptive band** (never narrower than LOPO MAE; wider for thin or heterogeneous gels). GelMA’s number is one numeric paper (Daly ~80%, no kPa) — that is labeled **weak**.
3. Read **Also extracted for this gel**: Li 2016 / Levett 2014 / Paul 2023 with published kPa and qualitative live/dead. **Open this next** prefers the closest kPa paper even if it is a floor.
4. Switch hydrogel to **fibrin**, then **chitosan**. Papers, trust badge, and band must change.
5. Open **Table**. Filter chitosan (dropdown still lists every gel). Download CSV. Yellow pills are floors (“>90%”), not means.
6. Open **Compare**: fibrin vs GelMA + TGF-β3. The yellow strip is A minus B on the same estimator.
7. Ignore Streamlit radar / inverse / next-experiment unless you want the demo.

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
