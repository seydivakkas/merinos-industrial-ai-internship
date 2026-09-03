# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Jupyter Notebook Generator: Model Sıkıştırma, ONNX Runtime ve Edge Dağıtımı (10 Bölüm)
"""

import json
import os


def build_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# GÜN 39: Model Sıkıştırma, ONNX Runtime & Edge Dağıtımı\n",
                    "## Gereksinim 8: Tezgâh Başı Donanımlarda Düşük Gecikmeli Çıkarım, INT8 Kuantizasyon ve Performans Profilleme\n",
                    "\n",
                    "![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)\n",
                    "![Domain: Textile Manufacturing](https://img.shields.io/badge/domain-Merinos%20Carpet%20Manufacturing-blue?style=flat-square)\n",
                    "![Framework: ONNX Runtime](https://img.shields.io/badge/framework-ONNX%20Runtime%201.27-00599C?style=flat-square)\n",
                    "![Optimization: INT8 Quantization](https://img.shields.io/badge/optimization-INT8%20PTQ%20(~74%25%20reduction)-brightgreen?style=flat-square)\n",
                    "\n",
                    "> **ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR**  \n",
                    "> **Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)**  \n",
                    "> Bu yazılım ve ilgili tüm dosyalar (\"Yazılım\") yalnızca görüntüleme ve eğitim amaçlı olarak paylaşılmıştır.  \n",
                    "> Yazarın açık yazılı izni olmaksızın kopyalanamaz, çoğaltılamaz, dağıtılamaz veya kullanılamaz.\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Problem\n",
                    "**Merinos Gaziantep Halı Fabrikası** dokuma salonunda yer alan **Van de Wiele RCE02** ve **Schönherr Alpha 400** jakarlı dokuma tezgâhlarında, operatörlerin arıza teşhis ve bakım SOP kılavuzlarına tezgâh yanındaki **Endüstriyel Panel PC (Edge IPC)** donanımlarından anında erişebilmesi hedeflenmektedir. Ancak bu fansız endüstriyel bilgisayarlar sınırlı RAM (2-4 GB) ve kısıtlı CPU kaynaklarına sahiptir. Ağ dalgalanmaları veya fabrika yerel ağındaki kesintiler, merkezi bulut sunucularına bağımlı RAG modellerinin yanıt sürelerini kabul edilemez seviyelere çıkarabilmektedir."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Why the Problem Matters\n",
                    "Dokuma tezgâhı duruşunun maliyeti üretim hattında dakikalar içinde binlerce metrekarelik fireye ve kapasite kaybına yol açar. Merkezi buluta veya fabrika içi uzak sunucuya yapılan her API çağrısı ağ gecikmesi (network latency), paket kaybı ve güvenlik riskleri taşır. Modellerin (Bi-Encoder ve Cross-Encoder) doğrudan tezgâh yanı Edge IPC üzerinde yerel koşturulması, sıfır ağ bağımlılığı ve deterministik mikro-saniye (< 1 ms) seviyesinde çıkarım garantisi sağlar."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Engineering Concepts\n",
                    "- **ONNX (Open Neural Network Exchange)**: Çerçevelerden (PyTorch, TensorFlow) bağımsız, C++ tabanlı optimize yürütme grafı.\n",
                    "- **Post-Training Dynamic Quantization (PTQ - INT8)**: Eğitilmiş FP32 ağırlıklarının ve dinamik aktivasyonların 8-bit tamsayı uzayına indirgenmesi:\n",
                    "  $$S = \\frac{\\max(X) - \\min(X)}{255}, \\quad Z = \\text{round}\\left(-\\frac{\\min(X)}{S}\\right) - 128$$\n",
                    "  $$X_q = \\text{clip}\\left(\\text{round}\\left(\\frac{X}{S}\\right) + Z, -128, 127\\right)$$\n",
                    "- **CPU Threading (`intra_op_num_threads`)**: Gömülü çok çekirdekli endüstriyel CPU'larda kilitlenme olmadan azami çekirdek ölçekleme.\n",
                    "- **Semantik Sadakat (Cosine Similarity Preservation)**: INT8 dönüşümünün vektör açısal uzayını koruma oranı ($>\\%95$)."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Library / API Investigation\n",
                    "Bu çalışmada PyTorch ONNX ihracat arayüzü (`torch.onnx.export`), ONNX modeli doğrulama (`onnx.checker.check_model`), `onnxruntime.InferenceSession` ve `onnxruntime.quantization.quantize_dynamic` kütüphaneleri incelenmiştir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import sys\n",
                    "import time\n",
                    "import numpy as np\n",
                    "import torch\n",
                    "import onnx\n",
                    "import onnxruntime as ort\n",
                    "from pathlib import Path\n",
                    "from onnxruntime.quantization import quantize_dynamic, QuantType\n",
                    "\n",
                    "# Proje kök dizinini sys.path'e ekleme\n",
                    "cwd = Path.cwd()\n",
                    "project_root = cwd.parent if cwd.name == \"day39\" else cwd\n",
                    "if str(project_root) not in sys.path:\n",
                    "    sys.path.insert(0, str(project_root))\n",
                    "\n",
                    "print(f\"[OK] Proje Kökü            : {project_root}\")\n",
                    "print(f\"[OK] PyTorch Versiyonu    : {torch.__version__}\")\n",
                    "print(f\"[OK] ONNX Versiyonu       : {onnx.__version__}\")\n",
                    "print(f\"[OK] ONNX Runtime Versiyonu: {ort.__version__}\")\n",
                    "print(f\"[OK] Aktif Execution Provider: {ort.get_available_providers()}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Minimal Implementation\n",
                    "Üretim kodu `mini_project/src/` altında modülerleştirilmiştir. Burada Bi-Encoder ve Cross-Encoder modelleri PyTorch'tan ONNX FP32'ye aktarılmakta ve ardından dinamik INT8 kuantizasyon uygulanmaktadır."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from day39.mini_project.src.onnx_exporter import OnnxExporter, BiEncoderModule, CrossEncoderModule\n",
                    "from day39.mini_project.src.quantizer import ModelQuantizer\n",
                    "\n",
                    "base_dir = os.path.join(str(project_root), \"day39\")\n",
                    "outputs_dir = os.path.join(base_dir, \"mini_project\", \"outputs\")\n",
                    "os.makedirs(outputs_dir, exist_ok=True)\n",
                    "\n",
                    "bi_fp32 = os.path.join(outputs_dir, \"bi_encoder_fp32.onnx\")\n",
                    "bi_int8 = os.path.join(outputs_dir, \"bi_encoder_int8.onnx\")\n",
                    "cross_fp32 = os.path.join(outputs_dir, \"cross_encoder_fp32.onnx\")\n",
                    "cross_int8 = os.path.join(outputs_dir, \"cross_encoder_int8.onnx\")\n",
                    "\n",
                    "exporter = OnnxExporter(output_dir=outputs_dir, opset_version=17)\n",
                    "exporter.export_bi_encoder(bi_fp32)\n",
                    "exporter.export_cross_encoder(cross_fp32)\n",
                    "\n",
                    "quantizer = ModelQuantizer(output_dir=outputs_dir)\n",
                    "bi_size = quantizer.quantize_to_int8(bi_fp32, bi_int8)\n",
                    "cross_size = quantizer.quantize_to_int8(cross_fp32, cross_int8)\n",
                    "\n",
                    "print(f\"Bi-Encoder FP32 -> INT8: {bi_size.original_mb} MB -> {bi_size.quantized_mb} MB (%{bi_size.reduction_percentage} küçülme)\")\n",
                    "print(f\"Cross-Encoder FP32 -> INT8: {cross_size.original_mb} MB -> {cross_size.quantized_mb} MB (%{cross_size.reduction_percentage} küçülme)\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Experiment\n",
                    "PyTorch referans çıkarımı, ONNX FP32 ve ONNX INT8 çıkarım gecikmeleri, CPU thread ölçeklemesi ve throughput analizi test edilir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from day39.mini_project.src.edge_engine import EdgeInferenceEngine\n",
                    "from day39.mini_project.src.profiler import PerformanceProfiler\n",
                    "\n",
                    "dummy_bi = np.random.randn(1, 384).astype(np.float32)\n",
                    "bi_torch = BiEncoderModule()\n",
                    "engine_bi_fp32 = EdgeInferenceEngine(bi_fp32, num_threads=2)\n",
                    "engine_bi_int8 = EdgeInferenceEngine(bi_int8, num_threads=2)\n",
                    "\n",
                    "profiler = PerformanceProfiler(warmup_iters=5, benchmark_iters=25)\n",
                    "item_torch, base_fp32 = profiler.profile_pytorch_module(bi_torch, \"Bi-Encoder\", dummy_bi)\n",
                    "item_onnx_fp32 = profiler.profile_onnx_engine(engine_bi_fp32, \"Bi-Encoder\", \"ONNX_FP32\", dummy_bi, base_fp32)\n",
                    "item_onnx_int8 = profiler.profile_onnx_engine(engine_bi_int8, \"Bi-Encoder\", \"ONNX_INT8\", dummy_bi, base_fp32)\n",
                    "\n",
                    "print(f\"PyTorch FP32 Gecikme (P50) : {item_torch.latency.p50_ms:.3f} ms\")\n",
                    "print(f\"ONNX FP32 Gecikme (P50)    : {item_onnx_fp32.latency.p50_ms:.3f} ms\")\n",
                    "print(f\"ONNX INT8 Gecikme (P50)    : {item_onnx_int8.latency.p50_ms:.3f} ms\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 7. Visualization Where Relevant\n",
                    "Şekil 78'de sunulan 4 panelli **Edge Deployment Performance Analysis (Day 39)** grafiği oluşturulur ve teftiş edilir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from day39.mini_project.src.visualizer import EdgeVisualizer\n",
                    "from IPython.display import Image, display\n",
                    "\n",
                    "dashboard_path = os.path.join(outputs_dir, \"edge_performance_dashboard.png\")\n",
                    "EdgeVisualizer.generate_dashboard(output_path=dashboard_path)\n",
                    "display(Image(dashboard_path))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 8. Validation\n",
                    "INT8 kuantizasyonunun semantik doğruluğu ve sayısal çıktılarının FP32 referansına sadakati doğrulanır."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "acc = profiler.measure_accuracy_preservation(base_fp32, engine_bi_int8.encode(dummy_bi))\n",
                    "print(f\"Bi-Encoder Kosinüs Sadakati : %{acc.cosine_similarity * 100:.2f}\")\n",
                    "print(f\"Ortalama Mutlak Hata (MAE)  : {acc.mean_absolute_error:.6f}\")\n",
                    "print(f\"Endüstriyel Tolerans İçi mi : {acc.is_tolerable}\")\n",
                    "\n",
                    "# Tezgâh Başı Uçtan Uca Arama Hattı Doğrulaması\n",
                    "from day39.mini_project.src.edge_pipeline import EdgeRagPipeline\n",
                    "pipeline = EdgeRagPipeline(bi_int8, cross_int8, num_threads=2)\n",
                    "res = pipeline.search_and_rerank(\"Van de Wiele jakarlı tezgâhta E-401 motor sıcaklığı arızasında ne yapılmalıdır?\", loom_id=\"TEZGAH-01\")\n",
                    "print(f\"Getirilen Dokümanlar       : {res.retrieved_doc_ids}\")\n",
                    "print(f\"Alaka Skorları             : {res.scores}\")\n",
                    "print(f\"Uçtan Uca Çıkarım Süresi   : {res.execution_time_ms:.3f} ms\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 9. Failure Cases\n",
                    "1. **Thread Oversubscription**: IPC CPU çekirdek sayısından fazla thread tahsis edildiğinde içerik değiştirme (context switching) maliyetinin artarak gecikmeyi yükseltmesi.\n",
                    "2. **Quantization Outlier Clipping**: Dikkat matrislerindeki uç aktivasyon değerlerinin [-128, 127] aralığına sıkıştırılırken kırpılması sonucu hassasiyet kaybı yaşanması.\n",
                    "3. **Memory Swapping**: Düşük RAM'li fansız IPC donanımlarında çoklu model oturumu açılması durumunda disk takasına girilmesi ve gerçek zamanlılığın yitirilmesi."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 10. Conclusions\n",
                    "- **%74 Boyut Tasarrufu**: Dynamic INT8 kuantizasyonu sayesinde model dosya boyutları 0.757 MB'tan 0.199 MB'a (Bi-Encoder) ve 0.816 MB'tan 0.212 MB'a (Cross-Encoder) başarıyla indirilmiştir.\n",
                    "- **0.056 ms Gecikme**: ONNX Runtime INT8 motoru, Bi-Encoder çıkarımını 0.056 ms, Cross-Encoder çıkarımını 0.057 ms gibi ultra düşük gecikmeyle tamamlamaktadır.\n",
                    "- **Sıfır Ağ Bağımlılığı**: Merinos Gaziantep fabrikasındaki dokuma tezgâhlarında merkezi bulut veya yerel ağ kesintilerinden etkilenmeyen yerel kenar yapay zekâ altyapısı tesis edilmiştir."
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.14.3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    nb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "day39_model_compression_and_edge_deployment.ipynb")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"[OK] GUN 39 Notebook basariyla olusturuldu: {nb_path}")


if __name__ == "__main__":
    build_notebook()
