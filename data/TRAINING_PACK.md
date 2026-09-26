# Training pack

Generated 2026-09-26T18:34:45Z.

| File | Rows | Use |
|---|---|---|
| `train_gold.csv` | 52 conditions / 17 papers | **Train** viability. Split by `split_group`. |
| `train_silver.csv` | 71 auto rows | Review queue only. **Do not train.** |
| `papers_uniform.csv` | 9659 papers (2094 training_relevant) | Chemistry / architecture / application tags. |
| `feature_codebook.json` | vocab | Same labels the analyzer used. |

Gold chemistry filled on 52/52 rows.

```python
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut

gold = pd.read_csv("data/train_gold.csv")
y = gold["viability_pct"]
groups = gold["split_group"]
# LeaveOneGroupOut().split(gold, y, groups)
```

Amass abstracts without a typed live/dead number never enter `train_gold.csv`.
