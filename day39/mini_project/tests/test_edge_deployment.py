# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Birim ve Entegrasyon Testleri: Model Sıkıştırma, ONNX Runtime ve Edge Dağıtımı
"""

import os
import pytest
import numpy as np
import onnx

from day39.mini_project.src.onnx_exporter import OnnxExporter, BiEncoderModule, CrossEncoderModule
from day39.mini_project.src.quantizer import ModelQuantizer
from day39.mini_project.src.edge_engine import EdgeInferenceEngine
from day39.mini_project.src.profiler import PerformanceProfiler
from day39.mini_project.src.edge_pipeline import EdgeRagPipeline
from day39.mini_project.src.models import ModelSizeReport, LatencyDistribution, AccuracyPreservation


@pytest.fixture(scope="module")
def exported_models(tmp_path_factory):
    """Testler için geçici dizinde FP32 ve INT8 modellerini hazırlar."""
    tmp_dir = tmp_path_factory.mktemp("edge_test_models")
    bi_fp32 = str(tmp_dir / "test_bi_fp32.onnx")
    bi_int8 = str(tmp_dir / "test_bi_int8.onnx")
    cross_fp32 = str(tmp_dir / "test_cross_fp32.onnx")
    cross_int8 = str(tmp_dir / "test_cross_int8.onnx")

    exporter = OnnxExporter(opset_version=17)
    exporter.export_bi_encoder(bi_fp32)
    exporter.export_cross_encoder(cross_fp32)

    quantizer = ModelQuantizer()
    bi_report = quantizer.quantize_to_int8(bi_fp32, bi_int8)
    cross_report = quantizer.quantize_to_int8(cross_fp32, cross_int8)

    return {
        "bi_fp32": bi_fp32,
        "bi_int8": bi_int8,
        "cross_fp32": cross_fp32,
        "cross_int8": cross_int8,
        "bi_report": bi_report,
        "cross_report": cross_report
    }


def test_onnx_export_bi_encoder(exported_models):
    """Bi-Encoder modelinin geçerli bir ONNX grafiği ürettiğini doğrular."""
    path = exported_models["bi_fp32"]
    assert os.path.exists(path)
    model = onnx.load(path)
    onnx.checker.check_model(model)
    assert len(model.graph.input) == 1
    assert model.graph.input[0].name == "input_features"
    assert len(model.graph.output) == 1
    assert model.graph.output[0].name == "embeddings"


def test_onnx_export_cross_encoder(exported_models):
    """Cross-Encoder modelinin geçerli bir ONNX grafiği ürettiğini doğrular."""
    path = exported_models["cross_fp32"]
    assert os.path.exists(path)
    model = onnx.load(path)
    onnx.checker.check_model(model)
    assert len(model.graph.input) == 1
    assert model.graph.input[0].name == "pair_features"
    assert len(model.graph.output) == 1
    assert model.graph.output[0].name == "relevance_score"


def test_dynamic_quantization_size_reduction(exported_models):
    """Dinamik INT8 kuantizasyonun en az %50 (hedef: ~%75) boyut küçülmesi sağladığını test eder."""
    bi_report: ModelSizeReport = exported_models["bi_report"]
    cross_report: ModelSizeReport = exported_models["cross_report"]

    assert bi_report.reduction_percentage >= 50.0
    assert bi_report.compression_ratio >= 2.0
    assert bi_report.quantized_bytes < bi_report.original_bytes

    assert cross_report.reduction_percentage >= 50.0
    assert cross_report.compression_ratio >= 2.0
    assert cross_report.quantized_bytes < cross_report.original_bytes


def test_edge_engine_inference(exported_models):
    """EdgeInferenceEngine sınıfının ONNX Runtime üzerinden C++ çıkarımı yaptığını doğrular."""
    engine = EdgeInferenceEngine(exported_models["bi_int8"], num_threads=2)
    engine.warmup(num_iterations=3)

    dummy_in = np.random.randn(2, 384).astype(np.float32)
    out = engine.encode(dummy_in)
    assert out.shape == (2, 384)

    # Vektörlerin L2 normu yaklaşık 1.0 olmalıdır
    norms = np.linalg.norm(out, axis=1)
    assert np.allclose(norms, [1.0, 1.0], atol=0.05)


def test_accuracy_preservation(exported_models):
    """FP32 referansı ile INT8 çıktısı arasındaki Kosinüs Benzerliğinin >= 0.985 olduğunu doğrular."""
    profiler = PerformanceProfiler(warmup_iters=2, benchmark_iters=10)

    fp32_engine = EdgeInferenceEngine(exported_models["bi_fp32"], num_threads=1)
    int8_engine = EdgeInferenceEngine(exported_models["bi_int8"], num_threads=1)

    dummy_in = np.random.randn(1, 384).astype(np.float32)
    out_fp32 = fp32_engine.encode(dummy_in)
    out_int8 = int8_engine.encode(dummy_in)

    acc: AccuracyPreservation = profiler.measure_accuracy_preservation(out_fp32, out_int8)
    assert acc.cosine_similarity >= 0.985
    assert acc.mean_absolute_error <= 0.025
    assert acc.is_tolerable is True


def test_latency_distribution_statistics():
    """Gecikme persentil (P50, P95, P99) ve istatistik hesaplama mantığını doğrular."""
    profiler = PerformanceProfiler()
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    dist: LatencyDistribution = profiler.compute_latency_distribution(latencies)

    assert dist.min_ms == 1.0
    assert dist.max_ms == 10.0
    assert dist.mean_ms == 5.5
    assert dist.p50_ms == 5.5
    assert dist.p95_ms > 9.0


def test_thread_scaling_configuration(exported_models):
    """Farklı CPU iş parçacığı ayarlarının (1 ve 2 thread) kilitlenmeden çalıştığını test eder."""
    profiler = PerformanceProfiler(warmup_iters=2, benchmark_iters=5)
    dummy_in = np.random.randn(1, 384).astype(np.float32)

    scaling = profiler.profile_thread_scaling(
        exported_models["bi_int8"],
        dummy_in,
        thread_counts=[1, 2]
    )

    assert len(scaling) == 2
    assert scaling[0].thread_count == 1
    assert scaling[1].thread_count == 2
    assert scaling[0].mean_latency_ms > 0
    assert scaling[1].mean_latency_ms > 0


def test_edge_pipeline_end_to_end(exported_models):
    """Tezgâh başı iki aşamalı (Bi-Encoder + Cross-Encoder) yerel arama akışını doğrular."""
    pipeline = EdgeRagPipeline(
        bi_encoder_model_path=exported_models["bi_int8"],
        cross_encoder_model_path=exported_models["cross_int8"],
        num_threads=2
    )

    query = "Van de Wiele jakarlı tezgâhta E-401 motor sıcaklığı arızasında ne yapılmalıdır?"
    result = pipeline.search_and_rerank(query, loom_id="TEZGAH-01", top_k=3, top_n=2)

    assert result.query == query
    assert result.loom_id == "TEZGAH-01"
    assert len(result.retrieved_doc_ids) == 2
    assert len(result.scores) == 2
    assert result.execution_time_ms > 0
    assert result.engine_used == "ONNX_INT8_EDGE"
    assert "DOC-VDW-001" in result.retrieved_doc_ids
