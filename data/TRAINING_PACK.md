# Training pack

Generated 2026-09-26T22:25:34Z.

| File | Rows | Use |
|---|---|---|
| `train_gold.csv` | 159 conditions / 55 papers | **Train** viability. Split by `split_group`. |
| `train_silver.csv` | 69 auto rows | Review queue only. **Do not train.** |
| `papers_uniform.csv` | 12024 papers (2317 training_relevant) | Chemistry / architecture / application tags. |
| `feature_codebook.json` | vocab | Same labels the analyzer used. |

Gold chemistry filled on 159/159 rows.

```python
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut

gold = pd.read_csv("data/train_gold.csv")
y = gold["viability_pct"]
groups = gold["split_group"]
# LeaveOneGroupOut().split(gold, y, groups)
```

Amass abstracts without a typed live/dead number never enter `train_gold.csv`.
