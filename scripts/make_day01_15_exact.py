"""Embed exact standalone implementations into Day 01-15 notebooks.
Reads the exact logic from mini_project/src and embeds it directly into the notebooks.
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def process_day04():
    nb_path = REPO_ROOT / "day04" / "day04_python_ortami_ve_veri_sozlesmesi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
from pydantic import BaseModel, Field, field_validator
from typing import List

class CarpetSpecificationContract(BaseModel):
    product_id: str = Field(..., description="Stok ve urun kimligi")
    title: str = Field(..., min_length=2, max_length=100)
    collection: str
    width_cm: float = Field(..., gt=20.0, le=600.0)
    length_cm: float = Field(..., gt=20.0, le=1000.0)
    pile_height_mm: float = Field(..., ge=2.0, le=45.0)
    palette_hex: List[str] = Field(..., min_length=1)

class LoomTelemetryContract(BaseModel):
    loom_id: str
    motor_temperature_c: float = Field(..., ge=15.0, le=120.0)
    pneumatic_pressure_bar: float = Field(..., ge=1.0, le=30.0)
    warp_tension_cn: float = Field(..., ge=50.0, le=800.0)
    rpm: int = Field(..., ge=100, le=1500)

spec = CarpetSpecificationContract(
    product_id="CRP-101",
    title="Merinos Royal Gold",
    collection="Imperial",
    width_cm=200.0,
    length_cm=290.0,
    pile_height_mm=14.0,
    palette_hex=["#D4AF37", "#000000"]
)
print("Doğrulanan Veri Sözleşmesi:")
print(spec.model_dump_json(indent=2))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 04 updated.")

def process_day05():
    nb_path = REPO_ROOT / "day05" / "day05_pandas_ve_veri_kalitesi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
from typing import Dict, List, Tuple, Any
from pydantic import BaseModel
import pandas as pd
import numpy as np

class DataQualityReport(BaseModel):
    total_rows: int
    clean_rows: int
    quarantine_rows: int
    completeness_score_pct: float
    validity_score_pct: float

class PandasDataPipeline:
    def __init__(self):
        pass

    def clean_and_profile(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        range_rules: Dict[str, Tuple[float, float]]
    ) -> Tuple[pd.DataFrame, pd.DataFrame, DataQualityReport]:
        if df.empty:
            raise ValueError("Girdi veri çerçevesi boş olamaz.")
        
        # Eksik deger kontrolu
        valid_mask = df[required_columns].notnull().all(axis=1)
        
        # Sinir kurallari kontrolu
        for col, (min_v, max_v) in range_rules.items():
            if col in df.columns:
                valid_mask = valid_mask & (df[col] >= min_v) & (df[col] <= max_v)
        
        clean_df = df[valid_mask].copy()
        quarantine_df = df[~valid_mask].copy()
        
        total = len(df)
        clean_count = len(clean_df)
        comp = float(df[required_columns].notnull().mean().mean() * 100.0)
        valid = float((clean_count / total) * 100.0) if total > 0 else 0.0
        
        report = DataQualityReport(
            total_rows=total,
            clean_rows=clean_count,
            quarantine_rows=len(quarantine_df),
            completeness_score_pct=round(comp, 2),
            validity_score_pct=round(valid, 2)
        )
        return clean_df, quarantine_df, report

df = pd.DataFrame({
    "loom_id": ["L1", "L2", "L3", "L4", "L5"],
    "rpm": [820.0, np.nan, 840.0, 790.0, 810.0],
    "tension_cn": [410.0, 420.0, -10.0, 430.0, 405.0]
})

pipeline = PandasDataPipeline()
clean_df, quarantine_df, report = pipeline.clean_and_profile(
    df=df,
    required_columns=["loom_id", "rpm", "tension_cn"],
    range_rules={"rpm": (600, 1000), "tension_cn": (0, 800)}
)
print("Temiz Veri Adedi:", len(clean_df))
print("Karantina Veri Adedi:", len(quarantine_df))
print("Veri Kalite Skoru: %", report.validity_score_pct)'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 05 updated.")

def process_day06():
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
print("Orijinal Veri Matrisi:\n", X)
print("\nZ-Score Standartlaştırılmış Matris:\n", np.round(X_scaled, 4))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 06 updated.")

def process_day07():
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
    
    # Remove any external import in cell 6
    cell6_src = "".join(nb['cells'][6]['source']).replace("from day07.mini_project.src.distance_similarity import compute_pairwise_distances", "# compute_pairwise_distances standalone tanimlandi")
    nb['cells'][6]['source'] = [line + '\n' for line in cell6_src.split('\n')]
    
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 07 updated.")

def process_day08():
    nb_path = REPO_ROOT / "day08" / "day08_kesifsel_veri_analizi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from pydantic import BaseModel

class EDAReport(BaseModel):
    mean_temp: float
    outlier_count_temp: int
    top_correlated_pairs: List[Tuple[str, str, float]]

class EDAToolkit:
    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> EDAReport:
        s = df["motor_temp_c"]
        mean_t = float(s.mean())
        std_t = float(s.std())
        outliers = int(((s - mean_t).abs() > 2 * std_t).sum())
        
        num_cols = df.select_dtypes(include=[np.number]).columns
        corr = df[num_cols].corr()
        pairs = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                c1, c2 = num_cols[i], num_cols[j]
                pairs.append((c1, c2, float(abs(corr.loc[c1, c2]))))
        pairs.sort(key=lambda x: x[2], reverse=True)
        return EDAReport(
            mean_temp=round(mean_t, 2),
            outlier_count_temp=outliers,
            top_correlated_pairs=pairs
        )

toolkit = EDAToolkit()
print("EDA Araç Seti Hazır.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 08 updated.")

def process_day09():
    nb_path = REPO_ROOT / "day09" / "day09_opencv_temelleri.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
import cv2
import numpy as np

class ImagePreprocessor:
    def __init__(self, target_size=(256, 256)):
        self.target_size = target_size

    def resize(self, img: np.ndarray) -> np.ndarray:
        return cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        if len(img.shape) == 2:
            return img
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def enhance_contrast_clahe(self, gray_img: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray_img)

# Sentetik dokuma deseni üretimi
synthetic_carpet = np.zeros((300, 300, 3), dtype=np.uint8)
synthetic_carpet[:, :] = (120, 80, 50)
synthetic_carpet[50:250, 50:250] = (200, 150, 100)

preprocessor = ImagePreprocessor(target_size=(256, 256))
resized = preprocessor.resize(synthetic_carpet)
gray = preprocessor.to_grayscale(resized)
enhanced = preprocessor.enhance_contrast_clahe(gray)

print(f"Orijinal Boyut: {synthetic_carpet.shape} -> Yeniden Boyutlandırılmış: {resized.shape}")
print(f"Gri Tonlama Boyut: {gray.shape} | CLAHE Kontrast Güçlendirildi.")'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 09 updated.")

def process_day10():
    nb_path = REPO_ROOT / "day10" / "day10_renk_uzaylari_ve_farki.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import cv2
import numpy as np
from typing import Tuple

def bgr_to_cielab(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr.reshape(1, 1, 3), cv2.COLOR_BGR2LAB).reshape(3)

def delta_e_cie76(lab1: np.ndarray, lab2: np.ndarray) -> float:
    return float(np.sqrt(np.sum((lab1.astype(np.float32) - lab2.astype(np.float32)) ** 2)))

class ColorDifferenceAnalyzer:
    def __init__(self, threshold_warning: float = 2.0, threshold_reject: float = 5.0):
        self.threshold_warning = threshold_warning
        self.threshold_reject = threshold_reject

    def grade_color_match(self, ref_bgr: np.ndarray, sample_bgr: np.ndarray) -> Tuple[float, str, str]:
        lab_ref = bgr_to_cielab(ref_bgr)
        lab_sample = bgr_to_cielab(sample_bgr)
        de = delta_e_cie76(lab_ref, lab_sample)
        if de <= self.threshold_warning:
            return round(de, 2), "PASS", "Tolerans dahilinde"
        elif de <= self.threshold_reject:
            return round(de, 2), "WARNING", "Sınırda ton sapması"
        else:
            return round(de, 2), "REJECT", "Kabul edilemez ton sapması"

ref_bgr = np.array([30, 80, 180], dtype=np.uint8)  # Sıcak kiremit tonu
sample_bgr = np.array([32, 82, 177], dtype=np.uint8)
analyzer = ColorDifferenceAnalyzer(threshold_warning=2.0, threshold_reject=5.0)

de, status, desc = analyzer.grade_color_match(ref_bgr, sample_bgr)
print(f"Numune Ton Farkı Delta E: {de:.2f} -> Durum: [{status}] ({desc})")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 10 updated.")

def process_day11():
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
    proportion_pct: float
    hex_code: str

class PaletteResult(BaseModel):
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
            clusters.append(ColorCluster(bgr=[b, g, r], proportion_pct=pct, hex_code=hex_c))
        clusters.sort(key=lambda x: x.proportion_pct, reverse=True)
        return PaletteResult(clusters=clusters)

extractor = KMeansPaletteExtractor(n_colors=4, random_state=42)
print("K-Means Palet Motoru Başlatıldı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 11 updated.")

def process_day12():
    nb_path = REPO_ROOT / "day12" / "day12_perspektif_ve_homografi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import cv2
import numpy as np
from typing import Tuple

def order_four_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

class HomographyRectifier:
    def __init__(self, output_width: int = 300, output_height: int = 400):
        self.output_width = output_width
        self.output_height = output_height

    def rectify(self, img: np.ndarray, corners: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rect = order_four_points(corners.astype(np.float32))
        dst = np.array([
            [0, 0],
            [self.output_width - 1, 0],
            [self.output_width - 1, self.output_height - 1],
            [0, self.output_height - 1]
        ], dtype="float32")
        H = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, H, (self.output_width, self.output_height))
        return warped, H

rectifier = HomographyRectifier(output_width=300, output_height=400)
print("Homografi Düzeltici Hazır.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 12 updated.")

def process_day13():
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
    def detect_edges_canny(img: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> np.ndarray:
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
    print("Day 13 updated.")

def process_day14():
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
                circularity=round(float(circularity), 3)
            ))
        return regions

print("Segmentasyon Motoru Yüklendi.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 14 updated.")

def process_day15():
    nb_path = REPO_ROOT / "day15" / "day15_gorsel_ozellik_entegrasyonu.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Standalone Definitions
import cv2
import numpy as np
from typing import List
from pydantic import BaseModel

class IntegratedFeatures(BaseModel):
    texture_features: List[float]
    color_moments: List[float]
    hu_moments: List[float]
    total_dimension: int

class VisualFeatureIntegrator:
    def __init__(self):
        pass

    def fuse_features(self, img_bgr: np.ndarray) -> IntegratedFeatures:
        if len(img_bgr.shape) != 3 or img_bgr.shape[2] != 3:
            raise ValueError("Girdi 3 kanallı BGR görsel olmalıdır.")
        
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 1. Doku özellikleri (Laplacian varyansı, Sobel enerji)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_energy = float(np.mean(sobelx**2 + sobely**2))
        std_val = float(np.std(gray))
        mean_val = float(np.mean(gray))
        texture = [round(lap_var, 2), round(sobel_energy, 2), round(std_val, 2), round(mean_val, 2)]
        
        # 2. Renk Momentleri (Mean & Std for 3 channels = 6)
        color = []
        for c in range(3):
            color.append(round(float(np.mean(img_bgr[:, :, c])), 2))
            color.append(round(float(np.std(img_bgr[:, :, c])), 2))
            
        # 3. Hu Momentleri (7 adet rotasyon ve olcek invaryant moment)
        moments = cv2.moments(gray)
        hu = cv2.HuMoments(moments).flatten()
        hu_log = [round(float(-np.sign(h) * np.log10(abs(h) + 1e-10)), 3) for h in hu]
        
        total_dim = len(texture) + len(color) + len(hu_log)
        return IntegratedFeatures(
            texture_features=texture,
            color_moments=color,
            hu_moments=hu_log,
            total_dimension=total_dim
        )

integrator = VisualFeatureIntegrator()
print("Görsel Öznitelik Entegratörü Başlatıldı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 15 updated.")

if __name__ == "__main__":
    process_day04()
    process_day05()
    process_day06()
    process_day07()
    process_day08()
    process_day09()
    process_day10()
    process_day11()
    process_day12()
    process_day13()
    process_day14()
    process_day15()
    print("Day 04-15 processed.")
