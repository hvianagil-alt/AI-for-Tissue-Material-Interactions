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

| Tab | Use it for | Trust it? |
|---|---|---|
| **Predict** | The product: published live/dead % for the gel you typed, plus nearest extracted papers | Literature block: yes, as a lookup. Radar: no |
| **Dataset** | Browse the training table and the extraction queue | Yes — this is the evidence |
| **Inverse design** | Demo: sample gels toward a target profile | No — simulator |
| **Next experiment** | Demo: rank by expected improvement | No — simulator |
| **About** | Honest LOPO JSON | Yes — the scientific scoreboard |

## 3. Predict — the actual workflow

1. Leave the defaults the first time: **GelMA**, ~25 kPa, articular chondrocyte, 3D encapsulation.
2. Read **Literature viability** (material-class mean of published live/dead) and the **± LOPO MAE** band.
3. Read **Nearest extracted papers**. Open those DOIs. That list is how you choose the next gel.
4. Change only the hydrogel (try **fibrin**, **HA**, **alginate**, **chitosan**) and compare the papers that appear.
5. Ignore the four-outcome radar / protocol / simulated neighbors unless you explicitly want the demo.

If the gel you typed has **no** live/dead rows, the app falls back to the global mean and says so. Use the papers, not that number.

## 4. How to read the numbers

- **80% on GelMA** is the mean of the GelMA rows in `v_model_viability` (today: one Daly 2016 condition). It is not a prediction of your next flask.
- The band is **leave-one-paper-out MAE (~16 points)**, not a biological confidence interval. A published 80% is compatible with roughly 64–96 under that error.
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
