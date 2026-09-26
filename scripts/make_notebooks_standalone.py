"""Script to transform Day 01-15 notebooks into 100% self-contained standalone notebooks.
Ensures zero external file dependencies (no local mini_project imports, no external file reads).
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def update_day01():
    nb_path = REPO_ROOT / "day01" / "day01_firma_ve_calisma_ortami.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class DataModality(str, Enum):
    NUMERICAL = "numerical"
    VISUAL = "visual"
    TEXTUAL = "textual"

class DataAsset(BaseModel):
    asset_id: str = Field(..., description="Benzersiz varlik kimligi")
    name: str = Field(..., description="Varlik basligi")
    modality: DataModality = Field(..., description="Veri modalitesi")
    source_type: str = Field(..., description="Kaynak sistem")
    estimated_size_kb: float = Field(..., ge=0.0, description="Boyut KB")
    description: Optional[str] = None

class SystemResourceRequirements(BaseModel):
    min_cpu_cores: int = Field(default=2, ge=1)
    min_ram_gb: float = Field(default=4.0, ge=1.0)
    required_python_version: str = Field(default="3.10")

class WorkstationAuditResult(BaseModel):
    cpu_cores: int
    ram_gb: float
    python_version: str
    os_name: str
    is_compliant: bool
    notes: List[str]

class EnvironmentProfiler:
    def __init__(self, requirements: SystemResourceRequirements):
        self.requirements = requirements
        self.assets: List[DataAsset] = []

    def audit_workstation(self) -> WorkstationAuditResult:
        cores = os.cpu_count() or 1
        ram = psutil.virtual_memory().total / (1024**3)
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        compliant = (cores >= self.requirements.min_cpu_cores and ram >= self.requirements.min_ram_gb)
        return WorkstationAuditResult(
            cpu_cores=cores,
            ram_gb=round(ram, 2),
            python_version=py_ver,
            os_name=platform.system(),
            is_compliant=compliant,
            notes=["Is istasyonu donanim profili basariyla denetlendi."]
        )

    def register_asset(self, asset: DataAsset):
        self.assets.append(asset)

    def get_modality_distribution(self) -> Dict[str, int]:
        dist = {m.value: 0 for m in DataModality}
        for a in self.assets:
            dist[a.modality.value] += 1
        return dist

reqs = SystemResourceRequirements(
    min_cpu_cores=2,
    min_ram_gb=4.0,
    required_python_version="3.10"
)
profiler = EnvironmentProfiler(requirements=reqs)
audit = profiler.audit_workstation()
print("Workstation Audit:", audit.model_dump_json(indent=2))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 01 updated.")

def update_day02():
    nb_path = REPO_ROOT / "day02" / "day02_veri_turleri_ve_modelleme.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class ProductTabularRecord(BaseModel):
    product_id: str
    title: str
    collection: str
    width_cm: float
    length_cm: float
    primary_color: str

class VisualAssetMetadata(BaseModel):
    image_id: str
    file_name: str
    angle_or_view: str
    resolution: str

class ProductCompositeCatalog(BaseModel):
    product_id: str
    title: str
    collection: str
    dimensions: Dict[str, float]
    primary_color: str
    visual_assets: List[VisualAssetMetadata] = []

class SchemaTransformer:
    def __init__(self):
        self.products: Dict[str, ProductTabularRecord] = {}
        self.assets: Dict[str, VisualAssetMetadata] = {}
        self.links: Dict[str, List[str]] = {}

    def add_product(self, p: ProductTabularRecord):
        self.products[p.product_id] = p

    def add_asset(self, a: VisualAssetMetadata):
        self.assets[a.image_id] = a

    def link_product_to_images(self, pid: str, img_ids: List[str]):
        self.links[pid] = img_ids

    def validate_referential_integrity(self) -> Tuple[bool, List[str]]:
        errs = []
        for pid, img_ids in self.links.items():
            if pid not in self.products:
                errs.append(f"Product {pid} not found")
            for iid in img_ids:
                if iid not in self.assets:
                    errs.append(f"Asset {iid} referenced by product {pid} not found")
        return len(errs) == 0, errs

    def build_composite_catalog(self, pid: str) -> ProductCompositeCatalog:
        p = self.products[pid]
        linked_imgs = [self.assets[iid] for iid in self.links.get(pid, []) if iid in self.assets]
        return ProductCompositeCatalog(
            product_id=p.product_id,
            title=p.title,
            collection=p.collection,
            dimensions={"width_cm": p.width_cm, "length_cm": p.length_cm},
            primary_color=p.primary_color,
            visual_assets=linked_imgs
        )

print("Modeller basariyla tanimlandi.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 02 updated.")

def update_day03():
    nb_path = REPO_ROOT / "day03" / "day03_problem_tanimi_ve_baseline.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class ProblemSpecification(BaseModel):
    problem_id: str
    name: str
    input_contract: Dict[str, str]
    output_contract: Dict[str, str]
    target_metric: str
    baseline_threshold: float
    latency_sla_ms: float = 50.0

class EvaluationComparison(BaseModel):
    problem_id: str
    baseline_metric: float
    candidate_metric: float
    relative_improvement_pct: float
    baseline_latency_ms: float
    candidate_latency_ms: float
    is_candidate_superior: bool
    summary: str

class BaselineEvaluator:
    def __init__(self, spec: ProblemSpecification) -> None:
        self.spec = spec

    def evaluate(
        self,
        ground_truth: List[Any],
        baseline_preds: List[Any],
        candidate_preds: List[Any],
        baseline_lat_ms: float,
        candidate_lat_ms: float,
    ) -> EvaluationComparison:
        if not (len(ground_truth) == len(baseline_preds) == len(candidate_preds)):
            raise ValueError("Tum tahmin listeleri yer gercegi ile ayni uzunlukta olmalidir.")
        total = len(ground_truth)
        if total == 0:
            raise ValueError("Degerlendirme kumesi bos olamaz.")
        
        base_correct = sum(1 for gt, p in zip(ground_truth, baseline_preds) if gt == p)
        cand_correct = sum(1 for gt, p in zip(ground_truth, candidate_preds) if gt == p)
        base_acc = base_correct / total
        cand_acc = cand_correct / total
        
        rel_gain = ((cand_acc - base_acc) / base_acc * 100.0) if base_acc > 0 else 0.0
        superior = (cand_acc > base_acc) and (cand_acc >= self.spec.baseline_threshold)
        
        return EvaluationComparison(
            problem_id=self.spec.problem_id,
            baseline_metric=round(base_acc, 4),
            candidate_metric=round(cand_acc, 4),
            relative_improvement_pct=round(rel_gain, 2),
            baseline_latency_ms=baseline_lat_ms,
            candidate_latency_ms=candidate_lat_ms,
            is_candidate_superior=superior,
            summary=f"Aday Dogruluk: %{cand_acc*100:.1f} vs Baseline: %{base_acc*100:.1f} (+%{rel_gain:.1f} goreceli artis)"
        )

spec = ProblemSpecification(
    problem_id="PROB-SIM-01",
    name="Carpet Visual Similarity",
    input_contract={"query_image": "ndarray", "catalog": "List[Image]"},
    output_contract={"top_5_matches": "List[Tuple[str, float]]"},
    target_metric="Top-1 Accuracy",
    baseline_threshold=0.60,
    latency_sla_ms=25.0
)
print("Problem Sozlesmesi:", spec.model_dump_json(indent=2))'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 03 updated.")

def update_day04():
    nb_path = REPO_ROOT / "day04" / "day04_python_ortami_ve_veri_sozlesmesi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CarpetSpecificationContract(BaseModel):
    sku: str = Field(..., description="Stok kodu")
    collection: str
    width_cm: int = Field(..., ge=50, le=400)
    length_cm: int = Field(..., ge=50, le=600)
    knot_density_per_m2: int = Field(..., ge=100000, le=2000000)
    primary_color_hex: str

    @field_validator("primary_color_hex")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            raise ValueError(f"Gecersiz HEX renk formatı: {v}")
        return v.upper()

class LoomTelemetryContract(BaseModel):
    loom_id: str
    rpm: float = Field(..., ge=0.0, le=1200.0)
    warp_tension_cn: float = Field(..., ge=50.0, le=800.0)
    bearing_temp_c: float = Field(..., ge=10.0, le=110.0)
    vibration_mm_s: float = Field(..., ge=0.0, le=25.0)

loom_spec = CarpetSpecificationContract(
    sku="MER-VNT-160230-01",
    collection="Heritage",
    width_cm=160,
    length_cm=230,
    knot_density_per_m2=650000,
    primary_color_hex="#8B0000"
)
print("Gecerli Hali Sozlesmesi Dogrulandi:")
print(loom_spec.model_dump_json(indent=2))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 04 updated.")

def update_day05():
    nb_path = REPO_ROOT / "day05" / "day05_pandas_ve_veri_kalitesi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel

class DataQualityReport(BaseModel):
    total_rows: int
    missing_values: Dict[str, int]
    negative_tensions: int
    zero_speeds: int
    clean_ratio: float

class PandasDataPipeline:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def profile_quality(self) -> DataQualityReport:
        total = len(self.df)
        if total == 0:
            raise ValueError("DataFrame cannot be empty.")
        missing = self.df.isnull().sum().to_dict()
        neg_tens = int((self.df.get("tension", pd.Series(dtype=float)) < 0).sum())
        zero_spd = int((self.df.get("speed_rpm", pd.Series(dtype=float)) == 0).sum())
        clean_rows = int(self.df.dropna().shape[0])
        return DataQualityReport(
            total_rows=total,
            missing_values=missing,
            negative_tensions=neg_tens,
            zero_speeds=zero_spd,
            clean_ratio=round(clean_rows / total, 4)
        )

    def clean_telemetry(self) -> pd.DataFrame:
        cleaned = self.df.dropna().copy()
        if "tension" in cleaned.columns:
            cleaned = cleaned[cleaned["tension"] >= 0]
        if "speed_rpm" in cleaned.columns:
            cleaned = cleaned[cleaned["speed_rpm"] > 0]
        return cleaned

pipeline = PandasDataPipeline(telemetry_df)
report = pipeline.profile_quality()
print("Veri Kalitesi Raporu:")
print(report.model_dump_json(indent=2))'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 05 updated.")

def update_day06():
    nb_path = REPO_ROOT / "day06" / "day06_numpy_vektorel_hesaplama.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell5 = '''# 5. Minimal Implementation
import numpy as np

class MinMaxScaler:
    def __init__(self):
        self.min_ = None
        self.max_ = None

    def fit(self, X: np.ndarray):
        self.min_ = np.min(X, axis=0)
        self.max_ = np.max(X, axis=0)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        denom = np.where((self.max_ - self.min_) == 0, 1.0, (self.max_ - self.min_))
        return (X - self.min_) / denom

class StandardScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit(self, X: np.ndarray):
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        denom = np.where(self.std_ == 0, 1.0, self.std_)
        return (X - self.mean_) / denom

# Minimal olcekleyici ornegi
np.random.seed(42)
sample_data = np.random.uniform(10, 100, size=(100, 3))
minmax = MinMaxScaler().fit(sample_data)
norm_data = minmax.transform(sample_data)
print(f"Orijinal Aralık: [{sample_data.min():.2f}, {sample_data.max():.2f}]")
print(f"MinMax Normalize Aralık: [{norm_data.min():.2f}, {norm_data.max():.2f}]")'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 06 updated.")

def update_day07():
    nb_path = REPO_ROOT / "day07" / "day07_uzaklik_ve_benzerlik.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import numpy as np
from typing import List, Tuple

def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.sqrt(np.sum((v1 - v2) ** 2)))

def manhattan_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(np.sum(np.abs(v1 - v2)))

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def compute_pairwise_distances(X: np.ndarray, metric: str = "euclidean") -> np.ndarray:
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if metric == "euclidean":
                D[i, j] = euclidean_distance(X[i], X[j])
            elif metric == "cosine":
                D[i, j] = 1.0 - cosine_similarity(X[i], X[j])
            else:
                D[i, j] = manhattan_distance(X[i], X[j])
    return D

class KNNPatternMatcher:
    def __init__(self, k: int = 3, metric: str = "euclidean"):
        self.k = k
        self.metric = metric
        self.database = None
        self.labels = []

    def fit(self, X: np.ndarray, labels: List[str]):
        self.database = X
        self.labels = labels

    def query(self, v: np.ndarray) -> List[Tuple[str, float]]:
        scores = []
        for i, row in enumerate(self.database):
            if self.metric == "cosine":
                sim = cosine_similarity(v, row)
                scores.append((self.labels[i], sim))
            else:
                dist = euclidean_distance(v, row)
                scores.append((self.labels[i], dist))
        if self.metric == "cosine":
            scores.sort(key=lambda x: x[1], reverse=True)
        else:
            scores.sort(key=lambda x: x[1])
        return scores[:self.k]

print("Uzaklık ve Benzerlik Algoritmaları Hazırlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    
    # Check cell 6 import
    cell6_src = ''.join(nb['cells'][6]['source']).replace("from day07.mini_project.src.distance_similarity import compute_pairwise_distances", "# compute_pairwise_distances onceden tanimlandi")
    nb['cells'][6]['source'] = [line + '\n' for line in cell6_src.split('\n')]
    
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 07 updated.")

def update_day08():
    nb_path = REPO_ROOT / "day08" / "day08_kesifsel_veri_analizi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import pandas as pd
import numpy as np
from typing import Dict, Any
from pydantic import BaseModel

class ColumnSummary(BaseModel):
    mean: float
    std: float
    min: float
    median: float
    max: float
    skewness: float
    missing_count: int

class EDAReport(BaseModel):
    total_samples: int
    numeric_columns: Dict[str, ColumnSummary]
    correlation_pairs: Dict[str, float]

class EDAToolkit:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def generate_report(self) -> EDAReport:
        num_df = self.df.select_dtypes(include=[np.number])
        col_summaries = {}
        for col in num_df.columns:
            s = num_df[col].dropna()
            col_summaries[col] = ColumnSummary(
                mean=round(float(s.mean()), 3),
                std=round(float(s.std()), 3),
                min=round(float(s.min()), 3),
                median=round(float(s.median()), 3),
                max=round(float(s.max()), 3),
                skewness=round(float(s.skew()), 3),
                missing_count=int(self.df[col].isnull().sum())
            )
        corr_matrix = num_df.corr()
        pairs = {}
        cols = list(num_df.columns)
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                c1, c2 = cols[i], cols[j]
                pairs[f"{c1}_vs_{c2}"] = round(float(corr_matrix.loc[c1, c2]), 3)
        return EDAReport(
            total_samples=len(self.df),
            numeric_columns=col_summaries,
            correlation_pairs=pairs
        )

print("EDA Toolkit başarıyla tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 08 updated.")

def update_day09():
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
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def denoise_gaussian(self, img: np.ndarray, ksize=5, sigma=1.0) -> np.ndarray:
        return cv2.GaussianBlur(img, (ksize, ksize), sigma)

    def normalize_minmax(self, img: np.ndarray) -> np.ndarray:
        return img.astype(np.float32) / 255.0

    def process_pipeline(self, img: np.ndarray) -> dict:
        resized = self.resize(img)
        gray = self.to_grayscale(resized)
        denoised = self.denoise_gaussian(gray)
        norm = self.normalize_minmax(denoised)
        return {
            "resized_bgr": resized,
            "grayscale": gray,
            "denoised": denoised,
            "normalized": norm
        }

preprocessor = ImagePreprocessor(target_size=(200, 200))
results = preprocessor.process_pipeline(synthetic_carpet)
print("Pipeline Adımları Tamamlandı. Grayscale Boyut:", results["grayscale"].shape)'''
    nb['cells'][5]['source'] = [line + '\n' for line in cell5.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 09 updated.")

def update_day10():
    nb_path = REPO_ROOT / "day10" / "day10_renk_uzaylari_ve_farki.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np
from typing import Dict, Any

def bgr_to_cielab(bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)

def delta_e_cie76(lab1: np.ndarray, lab2: np.ndarray) -> float:
    return float(np.sqrt(np.sum((lab1.astype(np.float32) - lab2.astype(np.float32)) ** 2)))

def delta_e_ciede2000(lab1: np.ndarray, lab2: np.ndarray) -> float:
    # Minimal CIEDE2000 yaklasimi: agirlikli L*, a*, b* tolerans hesaplamasi
    dL = float(lab1[0]) - float(lab2[0])
    da = float(lab1[1]) - float(lab2[1])
    db = float(lab1[2]) - float(lab2[2])
    c1 = np.sqrt(float(lab1[1])**2 + float(lab1[2])**2)
    c2 = np.sqrt(float(lab2[1])**2 + float(lab2[2])**2)
    dC = c1 - c2
    dH2 = da**2 + db**2 - dC**2
    dH = np.sqrt(max(0.0, dH2))
    sl, sc, sh = 1.0 + 0.015 * (float(lab1[0]) - 50)**2 / np.sqrt(20 + (float(lab1[0]) - 50)**2), 1.0 + 0.045 * c1, 1.0 + 0.015 * c1
    return float(np.sqrt((dL / sl)**2 + (dC / sc)**2 + (dH / sh)**2))

class ColorDifferenceAnalyzer:
    def __init__(self, tolerance_de: float = 2.0):
        self.tolerance_de = tolerance_de

    def compare_colors(self, bgr_target: np.ndarray, bgr_sample: np.ndarray) -> Dict[str, Any]:
        lab_target = bgr_to_cielab(bgr_target.reshape(1, 1, 3)).reshape(3)
        lab_sample = bgr_to_cielab(bgr_sample.reshape(1, 1, 3)).reshape(3)
        de76 = delta_e_cie76(lab_target, lab_sample)
        de00 = delta_e_ciede2000(lab_target, lab_sample)
        passed = de00 <= self.tolerance_de
        return {
            "delta_e_cie76": round(de76, 2),
            "delta_e_ciede2000": round(de00, 2),
            "is_acceptable": passed,
            "target_lab": [float(x) for x in lab_target],
            "sample_lab": [float(x) for x in lab_sample]
        }

print("Renk Farkı Motoru Tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 10 updated.")

def update_day11():
    nb_path = REPO_ROOT / "day11" / "day11_kmeans_baskin_renk.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import List
from pydantic import BaseModel

class ColorCluster(BaseModel):
    bgr: List[int]
    rgb: List[int]
    percentage: float

class KMeansPaletteExtractor:
    def __init__(self, n_colors: int = 5, random_state: int = 42):
        self.n_colors = n_colors
        self.random_state = random_state

    def extract_palette(self, img_bgr: np.ndarray) -> List[ColorCluster]:
        pixels = img_bgr.reshape(-1, 3).astype(np.float32)
        kmeans = KMeans(n_clusters=self.n_colors, random_state=self.random_state, n_init=10)
        kmeans.fit(pixels)
        counts = np.bincount(kmeans.labels_)
        total = len(pixels)
        clusters = []
        for i, center in enumerate(kmeans.cluster_centers_):
            bgr = [int(round(c)) for c in center]
            rgb = [bgr[2], bgr[1], bgr[0]]
            pct = round(counts[i] / total, 4)
            clusters.append(ColorCluster(bgr=bgr, rgb=rgb, percentage=pct))
        clusters.sort(key=lambda c: c.percentage, reverse=True)
        return clusters

print("KMeansPaletteExtractor başarıyla tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 11 updated.")

def update_day12():
    nb_path = REPO_ROOT / "day12" / "day12_perspektif_ve_homografi.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np
from typing import Tuple

def order_four_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # Sol-ust
    rect[2] = pts[np.argmax(s)] # Sag-alt
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # Sag-ust
    rect[3] = pts[np.argmax(diff)] # Sol-alt
    return rect

class HomographyRectifier:
    def __init__(self, target_width: int = 300, target_height: int = 400):
        self.width = target_width
        self.height = target_height

    def rectify(self, img: np.ndarray, corners: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rect = order_four_points(corners)
        dst = np.array([
            [0, 0],
            [self.width - 1, 0],
            [self.width - 1, self.height - 1],
            [0, self.height - 1]
        ], dtype="float32")
        H = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, H, (self.width, self.height))
        return warped, H

print("Homografi Motoru Hazırlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 12 updated.")

def update_day13():
    nb_path = REPO_ROOT / "day13" / "day13_morfoloji_ve_kenar.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np

class MorphologyEdgeEngine:
    def __init__(self):
        pass

    def apply_canny(self, img: np.ndarray, thresh1=50, thresh2=150) -> np.ndarray:
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        return cv2.Canny(gray, thresh1, thresh2)

    def morphological_gradient(self, img: np.ndarray, ksize=3) -> np.ndarray:
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
        return cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

    def detect_defects(self, img: np.ndarray, thresh=200) -> np.ndarray:
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
        _, mask = cv2.threshold(tophat, thresh, 255, cv2.THRESH_BINARY)
        return mask

print("Morfoloji Motoru Tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 13 updated.")

def update_day14():
    nb_path = REPO_ROOT / "day14" / "day14_klasik_segmentasyon.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np
from typing import List
from pydantic import BaseModel

class SegmentedRegion(BaseModel):
    label_id: int
    area_pixels: int
    centroid: List[float]
    aspect_ratio: float

class CarpetSegmenter:
    def __init__(self, min_area: int = 50):
        self.min_area = min_area

    def segment_otsu(self, img: np.ndarray) -> np.ndarray:
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_regions(self, binary_mask: np.ndarray) -> List[SegmentedRegion]:
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask)
        regions = []
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= self.min_area:
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                ar = round(w / float(h), 2) if h > 0 else 0.0
                regions.append(SegmentedRegion(
                    label_id=i,
                    area_pixels=int(area),
                    centroid=[round(float(c), 1) for c in centroids[i]],
                    aspect_ratio=ar
                ))
        return regions

print("CarpetSegmenter Tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 14 updated.")

def update_day15():
    nb_path = REPO_ROOT / "day15" / "day15_gorsel_ozellik_entegrasyonu.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell4 = '''# 4. Library / API Investigation & Minimal Implementation
import cv2
import numpy as np
from typing import List, Dict
from pydantic import BaseModel

class IntegratedFeatureVector(BaseModel):
    color_moments: List[float]
    texture_roughness: float
    edge_density: float
    total_dimension: int

class VisualFeatureIntegrator:
    def __init__(self):
        pass

    def extract_features(self, img_bgr: np.ndarray) -> IntegratedFeatureVector:
        # 1. Renk Momentleri (Mean & Std per channel)
        means = [float(np.mean(img_bgr[:, :, c])) for c in range(3)]
        stds = [float(np.std(img_bgr[:, :, c])) for c in range(3)]
        color_feats = means + stds
        
        # 2. Doku Pürüzlülüğü (Laplacian varyansı)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # 3. Kenar Yoğunluğu (Canny kenar piksel oranı)
        edges = cv2.Canny(gray, 50, 150)
        density = float(np.sum(edges > 0) / edges.size)
        
        return IntegratedFeatureVector(
            color_moments=[round(x, 2) for x in color_feats],
            texture_roughness=round(lap_var, 2),
            edge_density=round(density, 4),
            total_dimension=len(color_feats) + 2
        )

print("VisualFeatureIntegrator Tanımlandı.")'''
    nb['cells'][4]['source'] = [line + '\n' for line in cell4.split('\n')]
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 15 updated.")

if __name__ == "__main__":
    update_day01()
    update_day02()
    update_day03()
    update_day04()
    update_day05()
    update_day06()
    update_day07()
    update_day08()
    update_day09()
    update_day10()
    update_day11()
    update_day12()
    update_day13()
    update_day14()
    update_day15()
    print("All Day 01-15 updated successfully.")
