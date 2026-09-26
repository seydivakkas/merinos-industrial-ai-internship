"""Fix Day 06, 07, 08, 11, 13, 14 to match the exact properties and methods expected by their notebook cells.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def fix_day06():
    nb_path = REPO_ROOT / "day06" / "day06_numpy_vektorel_hesaplama.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
import numpy as np

class MinMaxScaler:
    def __init__(self):
        self.min_ = None
        self.max_ = None

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.min_ = X.min(axis=0)
        self.max_ = X.max(axis=0)
        denom = np.where((self.max_ - self.min_) == 0, 1.0, (self.max_ - self.min_))
        return (X - self.min_) / denom

class StandardScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)
        denom = np.where(self.std_ == 0, 1.0, self.std_)
        return (X - self.mean_) / denom

X = np.array([
    [70.0, 14.0, 800.0],
    [85.0, 15.2, 830.0],
    [65.0, 13.8, 790.0],
    [90.0, 16.0, 860.0]
], dtype=np.float64)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Orijinal Veri Matrisi:\\n", X)
print("\\nZ-Score Standartlaştırılmış Matris:\\n", np.round(X_scaled, 4))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 06 fixed.")

def fix_day07():
    nb_path = REPO_ROOT / "day07" / "day07_uzaklik_ve_benzerlik.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import numpy as np
from typing import List, Tuple

def euclidean_distance(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.linalg.norm(u - v))

def manhattan_distance(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.sum(np.abs(u - v)))

def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return 0.0
    return float(np.dot(u, v) / (nu * nv))

def compute_pairwise_distances(features: np.ndarray, metric: str = "euclidean") -> np.ndarray:
    n = features.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if metric == "euclidean":
                D[i, j] = euclidean_distance(features[i], features[j])
            else:
                D[i, j] = 1.0 - cosine_similarity(features[i], features[j])
    return D

class KNNPatternMatcher:
    def __init__(self, metric: str = "euclidean"):
        self.metric = metric
        self.catalog_ids = []
        self.features = None

    def fit(self, catalog_ids: List[str], features: np.ndarray):
        self.catalog_ids = catalog_ids
        self.features = features

    def query(self, q: np.ndarray, k: int = 3) -> List[Tuple[str, float]]:
        if self.features is None or len(self.features) == 0:
            raise ValueError("Katalog veritabanı boş veya eğitilmedi.")
        scores = []
        for i, f in enumerate(self.features):
            if self.metric == "euclidean":
                dist = euclidean_distance(q, f)
            else:
                dist = 1.0 - cosine_similarity(q, f)
            scores.append((self.catalog_ids[i], dist))
        scores.sort(key=lambda x: x[1])
        return scores[:k]

u = np.array([2.0, 3.0, 5.0])
v = np.array([5.0, 7.0, 5.0])
print(f"Öklid: {euclidean_distance(u, v):.4f}")
print(f"Manhattan: {manhattan_distance(u, v):.4f}")
print(f"Kosinüs Benzerliği: {cosine_similarity(u, v):.4f}")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 07 fixed.")

def fix_day08():
    nb_path = REPO_ROOT / "day08" / "day08_kesifsel_veri_analizi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from pydantic import BaseModel

class ColumnStats(BaseModel):
    mean: float
    std: float
    min: float
    max: float

class EDAReport(BaseModel):
    row_count: int
    column_count: int
    columns: Dict[str, ColumnStats]
    top_correlated_pairs: List[Tuple[str, str, float]]

class EDAToolkit:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> EDAReport:
        col_dict = {}
        for c in df.select_dtypes(include=[np.number]).columns:
            s = df[c]
            col_dict[c] = ColumnStats(
                mean=round(float(s.mean()), 2),
                std=round(float(s.std()), 2),
                min=round(float(s.min()), 2),
                max=round(float(s.max()), 2)
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

def fix_day11():
    nb_path = REPO_ROOT / "day11" / "day11_kmeans_baskin_renk.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
from sklearn.cluster import KMeans
import numpy as np
import cv2
from typing import List
from pydantic import BaseModel

class ColorCluster(BaseModel):
    bgr: List[int]
    rgb: List[int]
    proportion_pct: float
    hex_code: str

class PaletteResult(BaseModel):
    k_clusters: int
    clusters: List[ColorCluster]

class KMeansPaletteExtractor:
    def __init__(self, n_colors: int = 4, random_state: int = 42):
        self.n_colors = n_colors
        self.random_state = random_state

    def extract_palette(self, img: np.ndarray) -> PaletteResult:
        pixels = img.reshape(-1, 3).astype(np.float32)
        km = KMeans(n_clusters=self.n_colors, random_state=self.random_state, n_init=10)
        km.fit(pixels)
        counts = np.bincount(km.labels_, minlength=self.n_colors)
        total = len(pixels)
        clusters = []
        for i, center in enumerate(km.cluster_centers_):
            b, g, r = [int(round(c)) for c in center]
            pct = round(float(counts[i] / total * 100.0), 2)
            hex_c = f"#{r:02X}{g:02X}{b:02X}"
            clusters.append(ColorCluster(
                bgr=[b, g, r],
                rgb=[r, g, b],
                proportion_pct=pct,
                hex_code=hex_c
            ))
        clusters.sort(key=lambda x: x.proportion_pct, reverse=True)
        return PaletteResult(k_clusters=len(clusters), clusters=clusters)

extractor = KMeansPaletteExtractor(n_colors=4, random_state=42)
print("K-Means Palet Motoru Başlatıldı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 11 fixed.")

def fix_day13():
    nb_path = REPO_ROOT / "day13" / "day13_morfoloji_ve_kenar.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import cv2
import numpy as np

class MorphologyEdgeEngine:
    @staticmethod
    def apply_morphology(img: np.ndarray, op: str, kernel_size: int = 3) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        if op == "opening":
            return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        elif op == "closing":
            return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        elif op == "gradient":
            return cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
        else:
            raise ValueError(f"Bilinmeyen morfolojik operasyon: {op}")

    @staticmethod
    def detect_canny_edges(img: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> np.ndarray:
        return cv2.Canny(img, low_thresh, high_thresh)

    @staticmethod
    def detect_lines_hough(edges: np.ndarray, threshold: int = 30, min_line_length: int = 40, max_line_gap: int = 5) -> np.ndarray:
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
        if lines is None:
            return np.empty((0, 4), dtype=int)
        return lines.reshape(-1, 4)

print("Morfoloji ve Çizgi Tespit Motoru Yüklendi.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 13 fixed.")

def fix_day14():
    nb_path = REPO_ROOT / "day14" / "day14_klasik_segmentasyon.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import cv2
import numpy as np
from typing import List, Tuple
from pydantic import BaseModel

class RegionProperties(BaseModel):
    region_id: int
    area_px: int
    perimeter_px: float
    circularity: float

class CarpetSegmenter:
    @staticmethod
    def segment_otsu(img: np.ndarray) -> Tuple[np.ndarray, float]:
        thresh, mask = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return mask, float(thresh)

    @staticmethod
    def extract_regions(mask: np.ndarray) -> List[RegionProperties]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        regions = []
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area < 20:
                continue
            perimeter = cv2.arcLength(cnt, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0.0
            regions.append(RegionProperties(
                region_id=i + 1,
                area_px=int(area),
                perimeter_px=round(float(perimeter), 1),
                circularity=round(float(circularity), 3)
            ))
        return regions

print("Segmentasyon Motoru Yüklendi.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 14 fixed.")

if __name__ == "__main__":
    fix_day06()
    fix_day07()
    fix_day08()
    fix_day11()
    fix_day13()
    fix_day14()
    print("All fixes applied.")
