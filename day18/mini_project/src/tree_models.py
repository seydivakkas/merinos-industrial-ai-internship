from __future__ import annotations
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

class MerinosDecisionTreeClassifier:
    """Merinos halı kalite kontrolü için özelleştirilmiş Karar Ağacı sınıfı."""
    def __init__(self, **kwargs):
        self.model = DecisionTreeClassifier(
            random_state=kwargs.get("random_state", 42),
            ccp_alpha=kwargs.get("ccp_alpha", 0.0),
            max_depth=kwargs.get("max_depth", None),
            min_samples_split=kwargs.get("min_samples_split", 2),
            min_samples_leaf=kwargs.get("min_samples_leaf", 1),
            class_weight=kwargs.get("class_weight", "balanced"),
        )

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        return self.model.predict(X)

    def compute_pruning_path(self, X, y) -> Dict[str, Any]:
        """Minimal maliyet-karmaşıklık budama yolunu hesaplar."""
        path = self.model.cost_complexity_pruning_path(X, y)
        ccp_alphas = path.ccp_alphas
        impurities = path.impurities
        return {
            "ccp_alphas": ccp_alphas,
            "impurities": impurities,
            "n_alphas": len(ccp_alphas)
        }

class MerinosRandomForestClassifier:
    """Merinos halı kalite kontrolü için Random Forest sınıfı."""
    def __init__(self, **kwargs):
        self.model = RandomForestClassifier(
            n_estimators=kwargs.get("n_estimators", 100),
            random_state=kwargs.get("random_state", 42),
            n_jobs=kwargs.get("n_jobs", -1),
            class_weight=kwargs.get("class_weight", "balanced"),
            max_depth=kwargs.get("max_depth", None),
            min_samples_split=kwargs.get("min_samples_split", 2),
            min_samples_leaf=kwargs.get("min_samples_leaf", 1),
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> MerinosRandomForestClassifier:
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def get_oob_metrics(self) -> Tuple[float, float]:
        score = float(self.model.oob_score_)
        error = float(1.0 - score)
        return score, error

    def get_feature_importances(self, feature_names: List[str]) -> Dict[str, float]:
        raw_importances = self.model.feature_importances_
        return {
            name: round(float(imp), 4)
            for name, imp in zip(feature_names, raw_importances)
        }

    def compute_oob_convergence(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        min_trees: int = 5,
        max_trees: int = 100,
        step: int = 5
    ) -> Tuple[List[int], List[float]]:
        tree_counts = list(range(min_trees, max_trees + 1, step))
        oob_errors = []

        for n in tree_counts:
            rf = RandomForestClassifier(
                n_estimators=n,
                criterion=getattr(self, "criterion", "gini"),
                max_features=getattr(self, "max_features", "sqrt"),
                bootstrap=True,
                oob_score=True,
                n_jobs=getattr(self, "n_jobs", -1),
                random_state=getattr(self, "random_state", 42)
            )
            rf.fit(X_train, y_train)
            oob_errors.append(float(1.0 - rf.oob_score_))

        return tree_counts, oob_errors

    def benchmark_latency(self, X: np.ndarray, n_runs: int = 200) -> Tuple[float, float]:
        sample = X[:1]
        for _ in range(20):
            self.model.predict(sample)

        t0 = time.perf_counter()
        for _ in range(n_runs):
            self.model.predict(sample)
        t1 = time.perf_counter()

        latency_ms = ((t1 - t0) / n_runs) * 1000.0
        throughput_fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0
        return latency_ms, throughput_fps


# Ek yöntemler ve uyumluluk bağlayıcıları
import time
from typing import List, Optional
from sklearn.metrics import accuracy_score
from day18.mini_project.src.models import (
    TreeComplexityMetrics,
    PruningPathResult,
    RandomForestMetrics
)

def _dt_predict_proba(self, X: np.ndarray) -> np.ndarray:
    return self.model.predict_proba(X)

def _dt_get_complexity(self) -> TreeComplexityMetrics:
    return TreeComplexityMetrics(
        depth=int(self.model.get_depth()),
        node_count=int(self.model.tree_.node_count),
        leaf_count=int(self.model.get_n_leaves()),
        ccp_alpha=float(getattr(self, "ccp_alpha", 0.0))
    )

def _dt_benchmark_latency(self, X: np.ndarray, n_runs: int = 200) -> Tuple[float, float]:
    sample = X[:1]
    for _ in range(20):
        self.model.predict(sample)
    t0 = time.perf_counter()
    for _ in range(n_runs):
        self.model.predict(sample)
    t1 = time.perf_counter()
    latency_ms = ((t1 - t0) / n_runs) * 1000.0
    throughput_fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0
    return latency_ms, throughput_fps

def _dt_compute_pruning_evaluation(
    self,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    max_alpha_points: int = 25
) -> PruningPathResult:
    full_tree = DecisionTreeClassifier(
        criterion=getattr(self, "criterion", "gini"),
        random_state=getattr(self, "random_state", 42),
        min_samples_split=getattr(self, "min_samples_split", 2),
        min_samples_leaf=getattr(self, "min_samples_leaf", 1)
    )
    path = full_tree.cost_complexity_pruning_path(X_train, y_train)
    ccp_alphas, impurities = path.ccp_alphas, path.impurities

    valid_indices = np.where((ccp_alphas >= 0.0) & (ccp_alphas < np.max(ccp_alphas)))[0]
    if len(valid_indices) == 0:
        valid_indices = np.arange(len(ccp_alphas))

    selected_alphas = ccp_alphas[valid_indices]
    selected_impurities = impurities[valid_indices]

    if len(selected_alphas) > max_alpha_points:
        step = max(1, len(selected_alphas) // max_alpha_points)
        eval_indices = np.arange(0, len(selected_alphas), step)
        eval_alphas = selected_alphas[eval_indices]
        eval_impurities = selected_impurities[eval_indices]
    else:
        eval_alphas = selected_alphas
        eval_impurities = selected_impurities

    train_scores = []
    test_scores = []
    leaf_counts = []

    for alpha in eval_alphas:
        tree = DecisionTreeClassifier(
            criterion=getattr(self, "criterion", "gini"),
            random_state=getattr(self, "random_state", 42),
            min_samples_split=getattr(self, "min_samples_split", 2),
            min_samples_leaf=getattr(self, "min_samples_leaf", 1),
            ccp_alpha=alpha
        )
        tree.fit(X_train, y_train)
        train_scores.append(float(accuracy_score(y_train, tree.predict(X_train))))
        test_scores.append(float(accuracy_score(y_test, tree.predict(X_test))))
        leaf_counts.append(int(tree.get_n_leaves()))

    best_test_idx = int(np.argmax(test_scores))
    optimal_alpha = float(eval_alphas[best_test_idx])
    optimal_leaf_count = leaf_counts[best_test_idx]
    unpruned_leaf_count = leaf_counts[0] if len(leaf_counts) > 0 else 1

    reduction_pct = (
        ((unpruned_leaf_count - optimal_leaf_count) / unpruned_leaf_count) * 100.0
        if unpruned_leaf_count > 0 else 0.0
    )

    return PruningPathResult(
        ccp_alphas=[float(a) for a in eval_alphas],
        impurities=[float(imp) for imp in eval_impurities],
        train_scores=train_scores,
        test_scores=test_scores,
        optimal_ccp_alpha=optimal_alpha,
        optimal_leaf_count=optimal_leaf_count,
        unpruned_leaf_count=unpruned_leaf_count,
        leaf_reduction_pct=round(reduction_pct, 2)
    )

MerinosDecisionTreeClassifier.predict_proba = _dt_predict_proba
MerinosDecisionTreeClassifier.get_complexity = _dt_get_complexity
MerinosDecisionTreeClassifier.benchmark_latency = _dt_benchmark_latency
MerinosDecisionTreeClassifier._compute_pruning_evaluation = _dt_compute_pruning_evaluation

# Pruning path uyumluluğu
_orig_compute_pruning = MerinosDecisionTreeClassifier.compute_pruning_path
def _compat_compute_pruning(self, X_train, y_train, X_test=None, y_test=None, max_alpha_points=25, *args, **kwargs):
    if X_test is not None and y_test is not None:
        return self._compute_pruning_evaluation(X_train, y_train, X_test, y_test, max_alpha_points=max_alpha_points)
    return _orig_compute_pruning(self, X_train, y_train)
MerinosDecisionTreeClassifier.compute_pruning_path = _compat_compute_pruning

# Constructor uyumluluk sarmalayıcıları
_orig_dt_init = MerinosDecisionTreeClassifier.__init__
def _compat_dt_init(self, **kwargs):
    _orig_dt_init(self, **kwargs)
    self.is_fitted = False
    self.criterion = kwargs.get("criterion", "gini")
    self.ccp_alpha = kwargs.get("ccp_alpha", 0.0)
    self.max_depth = kwargs.get("max_depth", None)
    self.min_samples_split = kwargs.get("min_samples_split", 2)
    self.min_samples_leaf = kwargs.get("min_samples_leaf", 1)
    self.random_state = kwargs.get("random_state", 42)
    if "criterion" in kwargs:
        self.model.set_params(criterion=kwargs["criterion"])
    if "min_samples_split" in kwargs:
        self.model.set_params(min_samples_split=kwargs["min_samples_split"])
    if "min_samples_leaf" in kwargs:
        self.model.set_params(min_samples_leaf=kwargs["min_samples_leaf"])
MerinosDecisionTreeClassifier.__init__ = _compat_dt_init

_orig_rf_init = MerinosRandomForestClassifier.__init__
def _compat_rf_init(self, **kwargs):
    _orig_rf_init(self, **kwargs)
    self.is_fitted = False
    self.n_estimators = kwargs.get("n_estimators", 100)
    self.criterion = kwargs.get("criterion", "gini")
    self.max_features = kwargs.get("max_features", "sqrt")
    self.bootstrap = kwargs.get("bootstrap", True)
    self.oob_score = kwargs.get("oob_score", True)
    self.n_jobs = kwargs.get("n_jobs", -1)
    self.random_state = kwargs.get("random_state", 42)
    self.model.set_params(
        bootstrap=self.bootstrap,
        oob_score=self.oob_score,
        criterion=self.criterion,
        max_features=self.max_features,
    )
MerinosRandomForestClassifier.__init__ = _compat_rf_init
