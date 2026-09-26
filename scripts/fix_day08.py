import json
from pathlib import Path
import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

nb_path = REPO_ROOT / "day08" / "day08_kesifsel_veri_analizi.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from pydantic import BaseModel

class ColumnSummary(BaseModel):
    mean: float
    std: float
    min: float
    q25: float
    median: float
    q75: float
    max: float
    outlier_count_iqr: int

class EDAReport(BaseModel):
    row_count: int
    column_count: int
    columns: Dict[str, ColumnSummary]
    top_correlated_pairs: List[Tuple[str, str, float]]

class EDAToolkit:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> EDAReport:
        col_dict = {}
        for c in df.select_dtypes(include=[np.number]).columns:
            s = df[c]
            q25 = float(s.quantile(0.25))
            q75 = float(s.quantile(0.75))
            iqr = q75 - q25
            lower = q25 - 1.5 * iqr
            upper = q75 + 1.5 * iqr
            outliers = int(((s < lower) | (s > upper)).sum())
            col_dict[c] = ColumnSummary(
                mean=round(float(s.mean()), 2),
                std=round(float(s.std()), 2),
                min=round(float(s.min()), 2),
                q25=round(q25, 2),
                median=round(float(s.median()), 2),
                q75=round(q75, 2),
                max=round(float(s.max()), 2),
                outlier_count_iqr=outliers
            )
        
        num_cols = list(col_dict.keys())
        corr = df[num_cols].corr()
        pairs = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                c1, c2 = num_cols[i], num_cols[j]
                pairs.append((c1, c2, float(abs(corr.loc[c1, c2]))))
        pairs.sort(key=lambda x: x[2], reverse=True)
        return EDAReport(
            row_count=len(df),
            column_count=len(df.columns),
            columns=col_dict,
            top_correlated_pairs=pairs
        )

toolkit = EDAToolkit()
print("EDA Araç Seti Hazır.")'''

nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
print("Day 08 fixed.")
