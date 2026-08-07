"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 16
İkili Sınıflandırma ve Lojistik Regresyon Test Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from day16.mini_project.src.data_generator import YarnQualityDataGenerator
from day16.mini_project.src.evaluator import ClassificationEvaluator
from day16.mini_project.src.logistic_classifier import MerinosBinaryLogisticClassifier
from day16.mini_project.src.models import BinaryClassificationReport, QualityClass
from day16.mini_project.src.preprocessor import QualityDataPreprocessor
from day16.mini_project.src.visualizer import ClassificationVisualizer


@pytest.fixture
def sample_dataset():
    """Testler için 500 satırlık kontrollü veri seti fikstürü."""
    gen = YarnQualityDataGenerator()
    return gen.generate_dataset(n_samples=500, defect_ratio=0.10, random_state=42)


@pytest.fixture
def split_scaled_data(sample_dataset):
    """Testler için standartlaştırılmış ve bölünmüş veri fikstürü."""
    preprocessor = QualityDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(
        sample_dataset, test_size=0.20, random_state=42
    )
    return preprocessor, X_train, X_test, y_train, y_test


def test_data_generator_imbalanced_distribution(sample_dataset):
    """1. Sentetik veri jeneratörünün boyut, sınıf dengesizliği ve sütun doğruluğu testi."""
    assert isinstance(sample_dataset, pd.DataFrame)
    assert len(sample_dataset) == 500
    assert "quality_label" in sample_dataset.columns

    defects = int(sample_dataset["quality_label"].sum())
    normals = len(sample_dataset) - defects

    assert defects == 50  # %10 kusurlu
    assert normals == 450
    assert len(sample_dataset.columns) == 11  # 10 öznitelik + 1 hedef

    # Fiziksel sınırların kontrolü
    assert (sample_dataset["yarn_tensile_strength"] > 0).all()
    assert (sample_dataset["twist_per_meter"] > 0).all()


def test_preprocessor_scaling_and_stratification(sample_dataset):
    """2. Veri ön işleyicisinin tabakalı ayrım, ölçekleme ve tekil dönüşüm testi."""
    pre = QualityDataPreprocessor()
    X_train, X_test, y_train, y_test = pre.split_and_scale(sample_dataset, test_size=0.20, random_state=42)

    assert len(X_train) == 400
    assert len(X_test) == 100

    # Tabakalı dağılım: her iki kümede de tam %10 kusur bulunmalı
    assert np.isclose(np.mean(y_train), 0.10, atol=0.01)
    assert np.isclose(np.mean(y_test), 0.10, atol=0.01)

    # Eğitim kümesi ortalaması ~0, standart sapması ~1 olmalı
    assert np.allclose(np.mean(X_train, axis=0), 0.0, atol=1e-2)
    assert np.allclose(np.std(X_train, axis=0), 1.0, atol=1e-2)

    # Tekil tahmin dönüşüm testi
    sample_row = sample_dataset.iloc[0].to_dict()
    X_single = pre.transform_single(sample_row)
    assert X_single.shape == (1, 10)


def test_logistic_regression_fit_and_probabilities(split_scaled_data):
    """3. Lojistik regresyon eğitimi ve olasılık kestirimi testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosBinaryLogisticClassifier(random_state=42)
    clf.fit(X_train, y_train)

    probs = clf.predict_proba(X_test)
    assert probs.shape == (len(X_test), 2)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    assert np.allclose(np.sum(probs, axis=1), 1.0)

    preds = clf.predict(X_test, threshold=0.50)
    assert len(preds) == len(X_test)
    assert set(np.unique(preds)).issubset({0, 1})


def test_model_coefficients_and_odds_ratios(split_scaled_data):
    """4. Katsayılar, odds oranları ve endüstriyel etki yönü analizi testi."""
    pre, X_train, _, y_train, _ = split_scaled_data
    clf = MerinosBinaryLogisticClassifier(random_state=42)
    clf.fit(X_train, y_train)

    weights = clf.get_feature_weights(pre.feature_names)
    assert len(weights) == 10

    # Odds oranı matematiksel eşitliği: OR = exp(beta)
    for fw in weights:
        assert np.isclose(fw.odds_ratio, np.exp(fw.weight), atol=1e-3)
        if fw.weight > 0:
            assert fw.impact_direction == "Kusur Riskini ARTIRICI"
            assert fw.odds_ratio > 1.0
        else:
            assert fw.impact_direction == "Kusur Riskini AZALTICI"
            assert fw.odds_ratio < 1.0

    # İplik mukavemeti (tensile strength) arttıkça kusur riski azalmalıdır (negatif beta)
    tensile_fw = next(w for w in weights if w.feature_name == "yarn_tensile_strength")
    assert tensile_fw.weight < 0.0


def test_confusion_matrix_metrics_calculation():
    """5. Karar matrisi bileşenleri ve F1/F2 türetilmiş metriklerin doğruluğu testi."""
    evaluator = ClassificationEvaluator(cost_fn=10.0, cost_fp=1.0)
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])  # 4 normal, 6 kusurlu
    y_pred = np.array([0, 0, 1, 0, 1, 1, 1, 1, 0, 0])  # 3 TN, 1 FP, 2 FN, 4 TP

    metrics, cost = evaluator.compute_confusion_metrics(y_true, y_pred)

    assert metrics.tp == 4
    assert metrics.fn == 2
    assert metrics.tn == 3
    assert metrics.fp == 1

    assert np.isclose(metrics.accuracy, 7 / 10)
    assert np.isclose(metrics.precision, 4 / 5)
    assert np.isclose(metrics.recall, 4 / 6, atol=1e-3)
    assert np.isclose(metrics.specificity, 3 / 4)

    # Cost = 10 * FN (2) + 1 * FP (1) = 21.0
    assert np.isclose(cost, 21.0)


def test_roc_auc_and_pr_auc_scores(split_scaled_data):
    """6. ROC-AUC ve PR-AUC eğri altı alan skorlarının endüstriyel yeterlilik testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosBinaryLogisticClassifier(random_state=42).fit(X_train, y_train)
    probs = clf.predict_proba(X_test)[:, 1]

    evaluator = ClassificationEvaluator()
    roc_metrics, _, _ = evaluator.evaluate_probabilities(y_test, probs)

    assert roc_metrics.roc_auc >= 0.85, f"ROC-AUC çok düşük: {roc_metrics.roc_auc}"
    assert roc_metrics.pr_auc >= 0.50, f"PR-AUC çok düşük: {roc_metrics.pr_auc}"
    assert roc_metrics.brier_score <= 0.15, f"Brier kalibrasyon hatası yüksek: {roc_metrics.brier_score}"


def test_balanced_class_weights_improves_recall(split_scaled_data):
    """7. class_weight='balanced' kullanımının azınlık sınıfı duyarlılığını (Recall) artırması testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data

    # Standart Lojistik Regresyon
    clf_base = MerinosBinaryLogisticClassifier(class_weight=None, random_state=42).fit(X_train, y_train)
    pred_base = clf_base.predict(X_test, threshold=0.50)

    # Dengeli Lojistik Regresyon
    clf_bal = MerinosBinaryLogisticClassifier(class_weight="balanced", random_state=42).fit(X_train, y_train)
    pred_bal = clf_bal.predict(X_test, threshold=0.50)

    evaluator = ClassificationEvaluator()
    m_base, _ = evaluator.compute_confusion_metrics(y_test, pred_base)
    m_bal, _ = evaluator.compute_confusion_metrics(y_test, pred_bal)

    # Dengeli model azınlık sınıfını yakalamaya odaklandığı için recall daha yüksek olmalıdır
    assert m_bal.recall >= m_base.recall
    assert m_bal.tp >= m_base.tp


def test_threshold_tuning_youden_and_cost(split_scaled_data):
    """8. Eşik tarama (Threshold Sweep), Youden's J ve maliyet minimizasyonu testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosBinaryLogisticClassifier(random_state=42).fit(X_train, y_train)
    probs = clf.predict_proba(X_test)[:, 1]

    evaluator = ClassificationEvaluator(cost_fn=10.0, cost_fp=1.0)
    evals, opt_youden, opt_f2, opt_cost = evaluator.sweep_thresholds(y_test, probs)

    assert len(evals) == 99
    # Dengesiz veride kusurları kaçırmamak için maliyet eşiği standart 0.50'den düşük olmalıdır
    assert opt_cost <= 0.50

    # Optimal maliyet eşiğindeki maliyet, tau=0.50 maliyetinden küçük veya eşit olmalıdır
    _, cost_50 = evaluator.compute_confusion_metrics(y_test, (probs >= 0.50).astype(int))
    _, cost_opt = evaluator.compute_confusion_metrics(y_test, (probs >= opt_cost).astype(int))
    assert cost_opt <= cost_50


def test_visualizer_generates_diagnostic_panel(split_scaled_data, tmp_path):
    """9. 2x2 Model teşhis panelinin görselleştirilmesi ve dosya bütünlüğü testi."""
    pre, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosBinaryLogisticClassifier(random_state=42).fit(X_train, y_train)
    bal_clf = MerinosBinaryLogisticClassifier(class_weight="balanced", random_state=42).fit(X_train, y_train)

    base_probs = clf.predict_proba(X_test)[:, 1]
    bal_probs = bal_clf.predict_proba(X_test)[:, 1]

    evaluator = ClassificationEvaluator(cost_fn=10.0, cost_fp=1.0)
    report = evaluator.generate_master_report(
        y_true=y_test,
        baseline_probs=base_probs,
        balanced_probs=bal_probs,
        feature_weights=clf.get_feature_weights(pre.feature_names),
    )
    _, evals, curve_data = evaluator.evaluate_probabilities(y_test, base_probs)

    out_file = tmp_path / "test_diagnostic_panel.png"
    viz = ClassificationVisualizer()
    saved_path = viz.plot_diagnostic_panel(report, curve_data, evals, str(out_file))

    assert Path(saved_path).exists()
    assert Path(saved_path).stat().st_size > 50_000  # En az 50 KB görsel boyutu


def test_cli_full_lifecycle_pipeline(tmp_path):
    """10. CLI uçtan uca yaşam döngüsü ve master rapor serileştirme testi."""
    csv_file = tmp_path / "yarn_data.csv"
    report_file = tmp_path / "report.json"
    plot_file = tmp_path / "plot.png"

    # 1. Veri üretimi
    gen = YarnQualityDataGenerator()
    df = gen.generate_dataset(n_samples=200, defect_ratio=0.10, random_state=42)
    gen.save_dataset(df, str(csv_file))
    assert csv_file.exists()

    # 2. Ön işleme ve eğitim
    pre = QualityDataPreprocessor()
    X_train, X_test, y_train, y_test = pre.split_and_scale(df, test_size=0.20, random_state=42)
    clf = MerinosBinaryLogisticClassifier(random_state=42).fit(X_train, y_train)
    bal_clf = MerinosBinaryLogisticClassifier(class_weight="balanced", random_state=42).fit(X_train, y_train)

    base_probs = clf.predict_proba(X_test)[:, 1]
    bal_probs = bal_clf.predict_proba(X_test)[:, 1]

    # 3. Rapor oluşturma
    evaluator = ClassificationEvaluator(cost_fn=10.0, cost_fp=1.0)
    report = evaluator.generate_master_report(
        y_true=y_test,
        baseline_probs=base_probs,
        balanced_probs=bal_probs,
        feature_weights=clf.get_feature_weights(pre.feature_names),
    )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    assert report_file.exists()
    assert isinstance(report, BinaryClassificationReport)
    assert report.defect_ratio == 0.10
