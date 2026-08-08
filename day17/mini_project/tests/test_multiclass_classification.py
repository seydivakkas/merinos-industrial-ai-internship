"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 17
Çok Sınıflı Kusur Sınıflandırma Test Paketi

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from day17.mini_project.src.data_generator import MulticlassQualityDataGenerator
from day17.mini_project.src.evaluator import MulticlassEvaluator
from day17.mini_project.src.models import DefectClass, MulticlassEvaluationReport
from day17.mini_project.src.multiclass_classifier import MerinosMulticlassClassifier
from day17.mini_project.src.preprocessor import MulticlassDataPreprocessor
from day17.mini_project.src.visualizer import MulticlassVisualizer


@pytest.fixture
def sample_dataset():
    """800 satırlık 4 sınıflı sentetik veri seti fikstürü."""
    gen = MulticlassQualityDataGenerator()
    return gen.generate_dataset(n_samples=800, random_state=42)


@pytest.fixture
def split_scaled_data(sample_dataset):
    """Standartlaştırılmış ve tabakalı ayrılmış veri fikstürü."""
    preprocessor = MulticlassDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.split_and_scale(
        sample_dataset, test_size=0.20, random_state=42
    )
    return preprocessor, X_train, X_test, y_train, y_test


def test_data_generator_multiclass_distribution(sample_dataset):
    """1. Sentetik jeneratörün 4 kusur sınıfını doğru oranda ve fiziksel sınırlarda üretmesi testi."""
    assert isinstance(sample_dataset, pd.DataFrame)
    assert len(sample_dataset) == 800
    assert "defect_class" in sample_dataset.columns

    unique_classes = sorted(sample_dataset["defect_class"].unique())
    assert unique_classes == [0, 1, 2, 3]

    counts = sample_dataset["defect_class"].value_counts().sort_index()
    # 4 sınıfın da örneklemleri yeterli sayıda olmalı (>100)
    for cnt in counts:
        assert cnt >= 100

    # Fiziksel pozitiflik kontrolleri
    assert (sample_dataset["yarn_tensile_strength"] > 0).all()
    assert (sample_dataset["yarn_linear_density_dtex"] > 1000).all()


def test_preprocessor_stratified_multiclass(sample_dataset):
    """2. Çok sınıflı tabakalı (stratified) bölme ve sızıntısız StandardScaler testi."""
    pre = MulticlassDataPreprocessor()
    X_train, X_test, y_train, y_test = pre.split_and_scale(sample_dataset, test_size=0.20, random_state=42)

    assert len(X_train) == 640
    assert len(X_test) == 160

    # Tabakalı dağılım kontrolü: Train ve Test sınıflarının oranları birbirine çok yakın olmalı
    train_dist = pd.Series(y_train).value_counts(normalize=True).sort_index()
    test_dist = pd.Series(y_test).value_counts(normalize=True).sort_index()
    for c in range(4):
        assert np.isclose(train_dist[c], test_dist[c], atol=0.02)

    # Train kümesi ortalaması ~0, standart sapması ~1
    assert np.allclose(np.mean(X_train, axis=0), 0.0, atol=1e-2)
    assert np.allclose(np.std(X_train, axis=0), 1.0, atol=1e-2)

    # Tekil ölçüm dönüşümü
    sample_row = sample_dataset.iloc[0].to_dict()
    arr = pre.transform_single(sample_row)
    assert arr.shape == (1, 10)


def test_softmax_multinomial_probabilities_sum_to_one(split_scaled_data):
    """3. Softmax Multinomial modelinin olasılık dağılımı (toplam 1.0) testi."""
    _, X_train, X_test, y_train, _ = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42)
    clf.fit(X_train, y_train)

    probs = clf.predict_proba(X_test)
    assert probs.shape == (len(X_test), 4)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_ovr_classifier_predictions(split_scaled_data):
    """4. One-vs-Rest (OvR) modelinin eğitimi, tahminleri ve olasılık üretimi testi."""
    _, X_train, X_test, y_train, _ = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="ovr", random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    assert len(preds) == len(X_test)
    assert set(np.unique(preds)).issubset({0, 1, 2, 3})

    probs = clf.predict_proba(X_test)
    assert probs.shape == (len(X_test), 4)
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_multiclass_confusion_matrix_dimensions(split_scaled_data):
    """5. 4x4 Karar matrisi (Confusion Matrix) hesaplama ve eleman toplamı testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    evaluator = MulticlassEvaluator()
    cm = evaluator.compute_confusion_matrix(y_test, y_pred)

    assert cm.shape == (4, 4)
    assert cm.sum() == len(y_test)
    # Köşegen üzerindeki doğru tahminler pozitif olmalı
    assert np.all(np.diag(cm) > 0)


def test_per_class_metrics_consistency(split_scaled_data):
    """6. Sınıf bazlı Precision, Recall ve F1 metriklerinin matematiksel tutarlılığı testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    evaluator = MulticlassEvaluator()
    per_class = evaluator.compute_per_class_metrics(y_test, y_pred)

    assert len(per_class) == 4
    for pc in per_class:
        assert 0.0 <= pc.precision <= 1.0
        assert 0.0 <= pc.recall <= 1.0
        assert 0.0 <= pc.f1_score <= 1.0
        assert pc.support > 0
        if pc.precision + pc.recall > 0:
            expected_f1 = 2 * pc.precision * pc.recall / (pc.precision + pc.recall)
            assert np.isclose(pc.f1_score, expected_f1, atol=1e-3)


def test_macro_micro_weighted_f1_hierarchy(split_scaled_data):
    """7. Makro, Mikro, Ağırlıklı F1 ve Cohen Kappa metriklerinin hesaplanması testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_probs = clf.predict_proba(X_test)

    evaluator = MulticlassEvaluator()
    metrics = evaluator.compute_global_metrics(y_test, y_pred, y_probs)

    assert metrics.accuracy >= 0.85
    assert metrics.macro_f1 >= 0.85
    assert metrics.micro_f1 >= 0.85
    assert metrics.weighted_f1 >= 0.85
    assert metrics.cohen_kappa >= 0.80
    assert metrics.log_loss >= 0.0


def test_multiclass_roc_auc_ovr_scores(split_scaled_data):
    """8. Her 4 sınıf için bağımsız One-vs-Rest ROC eğrileri ve AUC testi."""
    _, X_train, X_test, y_train, y_test = split_scaled_data
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    y_probs = clf.predict_proba(X_test)

    evaluator = MulticlassEvaluator()
    curves = evaluator.get_ovr_roc_curves(y_test, y_probs)

    assert len(curves) == 4
    for cname in [e.name for e in DefectClass]:
        assert cname in curves
        assert curves[cname]["auc"] >= 0.85
        assert len(curves[cname]["fpr"]) == len(curves[cname]["tpr"])


def test_visualizer_multiclass_panel(split_scaled_data, tmp_path):
    """9. 2x2 Çok sınıflı model teşhis panelinin üretimi ve dosya bütünlüğü testi."""
    pre, X_train, X_test, y_train, y_test = split_scaled_data
    clf_m = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    clf_o = MerinosMulticlassClassifier(strategy="ovr", random_state=42).fit(X_train, y_train)

    evaluator = MulticlassEvaluator()
    s_m = evaluator.evaluate_model(clf_m, X_test, y_test)
    s_o = evaluator.evaluate_model(clf_o, X_test, y_test)

    report = evaluator.generate_master_report(
        multinomial_summary=s_m,
        ovr_summary=s_o,
        y_test=y_test,
        feature_names=pre.feature_names,
        clf_multinomial=clf_m,
    )

    cm = evaluator.compute_confusion_matrix(y_test, clf_m.predict(X_test))
    curves = evaluator.get_ovr_roc_curves(y_test, clf_m.predict_proba(X_test))

    out_file = tmp_path / "test_multiclass_panel.png"
    viz = MulticlassVisualizer()
    saved_p = viz.plot_diagnostic_panel(report, cm, curves, str(out_file))

    assert Path(saved_p).exists()
    assert Path(saved_p).stat().st_size > 50_000


def test_cli_multiclass_lifecycle(tmp_path):
    """10. Çok sınıflı model yaşam döngüsü, JSON serileştirme ve tekil çıkarım testi."""
    csv_file = tmp_path / "multiclass_data.csv"
    report_file = tmp_path / "report.json"

    # 1. Veri üretimi
    gen = MulticlassQualityDataGenerator()
    df = gen.generate_dataset(n_samples=300, random_state=42)
    gen.save_dataset(df, str(csv_file))
    assert csv_file.exists()

    # 2. Ön işleme ve eğitim
    pre = MulticlassDataPreprocessor()
    X_train, X_test, y_train, y_test = pre.split_and_scale(df, test_size=0.20, random_state=42)
    clf = MerinosMulticlassClassifier(strategy="multinomial", random_state=42).fit(X_train, y_train)
    clf_ovr = MerinosMulticlassClassifier(strategy="ovr", random_state=42).fit(X_train, y_train)

    # 3. Rapor oluşturma
    evaluator = MulticlassEvaluator()
    s_m = evaluator.evaluate_model(clf, X_test, y_test)
    s_o = evaluator.evaluate_model(clf_ovr, X_test, y_test)

    report = evaluator.generate_master_report(
        multinomial_summary=s_m,
        ovr_summary=s_o,
        y_test=y_test,
        feature_names=pre.feature_names,
        clf_multinomial=clf,
    )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    assert report_file.exists()
    assert isinstance(report, MulticlassEvaluationReport)
    assert report.dataset_samples == 60  # 300 * 0.20
